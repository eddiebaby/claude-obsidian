"""Account mechanics: one day, one evaluation attempt, one funded account.

Fill assumptions (state them, don't hide them):
- A trader daily stop or a firm daily-loss-limit flatten fills exactly at the
  level minus `stop_slippage` dollars per unit of size.
- A trader daily profit cap fills exactly at the cap (no favorable overshoot).
- A drawdown breach liquidates the account; the evaluation is failed.
- Profit target and payouts are judged on end-of-day balances.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional

from .paths import Day
from .rules import EvalRules, FirmRules, FundedRules, PhaseRules


@dataclass(frozen=True)
class Controls:
    """The trader's own limits, layered inside the firm's."""

    daily_stop: Optional[float] = None
    """Flatten for the day when day P&L reaches -daily_stop (dollars, total)."""
    daily_profit_cap: Optional[float] = None
    """Flatten for the day when day P&L reaches +cap (manages consistency rules)."""
    stop_slippage: float = 0.0
    """Dollars per unit of size lost beyond a stop level."""

    def __post_init__(self) -> None:
        if self.daily_stop is not None and self.daily_stop <= 0:
            raise ValueError("daily_stop must be a positive dollar amount")
        if self.daily_profit_cap is not None and self.daily_profit_cap <= 0:
            raise ValueError("daily_profit_cap must be a positive dollar amount")
        if self.stop_slippage < 0:
            raise ValueError("stop_slippage must be >= 0")


@dataclass
class Account:
    start: float
    balance: float
    peak: float
    floor: float


def open_account(start: float, phase: PhaseRules) -> Account:
    return Account(start=start, balance=start, peak=start, floor=start - phase.max_loss)


def _raise_floor(acct: Account, phase: PhaseRules) -> None:
    if phase.drawdown_mode == "static":
        return
    lock = math.inf if phase.lock_floor_offset is None else acct.start + phase.lock_floor_offset
    cand = min(acct.peak - phase.max_loss, lock)
    if cand > acct.floor:
        acct.floor = cand


# status values returned by play_day
OK, STOP, CAP, BREACH, DLL_FAIL = "ok", "stop", "cap", "breach", "dll_fail"
_PRIORITY = {BREACH: 3, DLL_FAIL: 2, STOP: 1}


def play_day(acct: Account, day: Day, size: float, phase: PhaseRules, ctl: Controls) -> tuple[float, str]:
    """Advance the account by one day. Mutates `acct`. Returns (day_pnl, status)."""
    b0 = acct.balance
    intraday_trail = phase.drawdown_mode == "intraday_trailing"
    touch = phase.breach_on_intraday_touch or intraday_trail

    lo = -math.inf
    if ctl.daily_stop is not None:
        lo = -ctl.daily_stop
    dll_fail = -math.inf
    if phase.daily_loss_limit is not None:
        if phase.dll_action == "flatten":
            lo = max(lo, -phase.daily_loss_limit)
        else:
            dll_fail = -phase.daily_loss_limit
    hi = math.inf if ctl.daily_profit_cap is None else ctl.daily_profit_cap

    pnl: Optional[float] = None
    status = OK
    for rec, seg_min in day.segments:
        r = rec * size
        m = seg_min * size
        if r >= hi:  # the first bar at/above the cap is always a record bar
            pnl, status = hi, CAP
            if intraday_trail and b0 + hi > acct.peak:
                acct.peak = b0 + hi
                _raise_floor(acct, phase)
            break
        if intraday_trail and b0 + r > acct.peak:
            acct.peak = b0 + r
            _raise_floor(acct, phase)
        # Within a segment the floor is constant. The first level the path
        # crosses on the way down is the highest one it reaches.
        event, level = None, -math.inf
        candidates = [(lo, STOP), (dll_fail, DLL_FAIL)]
        if touch:
            candidates.append((acct.floor - b0, BREACH))
        for lvl, ev in candidates:
            if m <= lvl and (lvl > level or (lvl == level and _PRIORITY[ev] > _PRIORITY.get(event, 0))):
                event, level = ev, lvl
        if event == BREACH or event == DLL_FAIL:
            return level, event
        if event == STOP:
            pnl, status = lo - ctl.stop_slippage * size, STOP
            break
    if pnl is None:
        pnl = day.close * size

    bal = b0 + pnl
    if bal <= acct.floor:
        return pnl, BREACH
    acct.balance = bal
    if bal > acct.peak:
        acct.peak = bal
        _raise_floor(acct, phase)
    return pnl, status


# --------------------------------------------------------------------------
# Evaluation attempt
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class EvalResult:
    outcome: str  # "passed" | "breach" | "dll_fail" | "timeout" | "horizon"
    days: int
    fees: float
    profit: float


def run_eval(days: Iterable[Day], firm: FirmRules, size: float, ctl: Controls) -> EvalResult:
    ev: EvalRules = firm.eval
    acct = open_account(firm.start_balance, ev.phase)
    fees = ev.fee
    n = traded = 0
    best = 0.0
    for day in days:
        n += 1
        if ev.fee_period_days and n > 1 and (n - 1) % ev.fee_period_days == 0:
            fees += ev.fee
        pnl, status = play_day(acct, day, size, ev.phase, ctl)
        if status in (BREACH, DLL_FAIL):
            return EvalResult(status, n, fees, acct.balance - acct.start)
        if day.traded:
            traded += 1
        best = max(best, pnl)
        profit = acct.balance - acct.start
        if (
            profit >= ev.profit_target
            and traded >= ev.min_days
            and (ev.consistency_max_day_frac is None or best <= ev.consistency_max_day_frac * profit)
        ):
            return EvalResult("passed", n, fees + ev.activation_fee, profit)
        if ev.max_days is not None and n >= ev.max_days:
            return EvalResult("timeout", n, fees, profit)
    return EvalResult("horizon", n, fees, acct.balance - acct.start)


# --------------------------------------------------------------------------
# Funded account
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class FundedResult:
    outcome: str  # "breach" | "dll_fail" | "graduated" | "horizon"
    days: int
    payouts: int
    withdrawn: float
    trader_take: float


def run_funded(days: Iterable[Day], firm: FirmRules, size: float, ctl: Controls) -> FundedResult:
    fu: Optional[FundedRules] = firm.funded
    if fu is None:
        raise ValueError(f"{firm.name} has no funded rules")
    acct = open_account(firm.start_balance, fu.phase)
    n = n_pay = qual = 0
    withdrawn = take = 0.0
    cyc_pnl = cyc_best = 0.0
    for day in days:
        n += 1
        pnl, status = play_day(acct, day, size, fu.phase, ctl)
        if status in (BREACH, DLL_FAIL):
            return FundedResult(status, n, n_pay, withdrawn, take)
        if pnl >= fu.payout_day_min_profit and pnl > 0:
            qual += 1
        cyc_pnl += pnl
        cyc_best = max(cyc_best, pnl)
        if qual < fu.payout_min_days:
            continue
        amount = fu.payout_frac_of_profit * (acct.balance - acct.start)
        if fu.payout_max is not None:
            amount = min(amount, fu.payout_max)
        # never withdraw the account into its own floor
        amount = min(amount, acct.balance - acct.floor - 0.01)
        consistent = fu.consistency_max_day_frac is None or (
            cyc_pnl > 0 and cyc_best <= fu.consistency_max_day_frac * cyc_pnl
        )
        if amount >= max(fu.payout_min, 1e-9) and consistent:
            acct.balance -= amount  # floor and peak are left where they are
            withdrawn += amount
            take += amount * fu.profit_split
            n_pay += 1
            qual = 0
            cyc_pnl = cyc_best = 0.0
            if fu.max_payouts is not None and n_pay >= fu.max_payouts:
                return FundedResult("graduated", n, n_pay, withdrawn, take)
    return FundedResult("horizon", n, n_pay, withdrawn, take)
