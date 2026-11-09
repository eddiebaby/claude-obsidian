"""Firm rule sets.

Every number here is a parameter, not a fact. Prop firms change rules without
notice. The presets carry the date and source they came from; re-verify against
the firm's own help center before spending money on an evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

DRAWDOWN_MODES = ("eod_trailing", "intraday_trailing", "static")
DLL_ACTIONS = ("flatten", "fail")


@dataclass(frozen=True)
class PhaseRules:
    """Loss rules for one account phase (evaluation or funded).

    max_loss
        Distance in dollars from the high-water mark (trailing modes) or from
        the starting balance (static) at which the account is liquidated.
    drawdown_mode
        "eod_trailing": the floor ratchets up only from end-of-day balances.
        "intraday_trailing": the floor ratchets up from the highest unrealized
        balance seen during the day, tick by tick.
        "static": the floor never moves.
    lock_floor_offset
        The trailing floor stops rising at start_balance + this offset.
        0 means it locks at the starting balance; None means it never locks.
    breach_on_intraday_touch
        True: the account fails the moment unrealized equity touches the floor.
        False: only the closing balance is checked. Forced True for
        intraday_trailing.
    daily_loss_limit / dll_action
        Firm daily loss limit in dollars. "flatten" ends the day at the limit
        and the account keeps going; "fail" fails the account.
    """

    max_loss: float
    drawdown_mode: str = "eod_trailing"
    lock_floor_offset: Optional[float] = 0.0
    breach_on_intraday_touch: bool = True
    daily_loss_limit: Optional[float] = None
    dll_action: str = "flatten"

    def __post_init__(self) -> None:
        if self.drawdown_mode not in DRAWDOWN_MODES:
            raise ValueError(f"drawdown_mode must be one of {DRAWDOWN_MODES}")
        if self.dll_action not in DLL_ACTIONS:
            raise ValueError(f"dll_action must be one of {DLL_ACTIONS}")
        if self.max_loss <= 0:
            raise ValueError("max_loss must be positive")


@dataclass(frozen=True)
class EvalRules:
    profit_target: float
    phase: PhaseRules
    min_days: int = 1
    consistency_max_day_frac: Optional[float] = None
    """Pass requires best day <= frac * total profit (e.g. 0.5)."""
    fee: float = 0.0
    fee_period_days: Optional[int] = None
    """Recurring subscription: charge `fee` again every N trading days.
    None = one fee per attempt."""
    activation_fee: float = 0.0
    max_days: Optional[int] = None


@dataclass(frozen=True)
class FundedRules:
    phase: PhaseRules
    profit_split: float = 0.9
    payout_min_days: int = 5
    """Qualifying days needed per payout cycle."""
    payout_day_min_profit: float = 0.0
    """A day qualifies when its P&L is at least this."""
    payout_min: float = 0.0
    payout_max: Optional[float] = None
    payout_frac_of_profit: float = 1.0
    """Withdrawable share of profit above the starting balance."""
    max_payouts: Optional[int] = None
    """After this many payouts the account graduates (sim stops, counted as success)."""
    consistency_max_day_frac: Optional[float] = None
    """Payout requires best day in the cycle <= frac * cycle profit."""


@dataclass(frozen=True)
class FirmRules:
    name: str
    start_balance: float
    eval: EvalRules
    funded: Optional[FundedRules] = None
    max_contracts: Optional[int] = None
    """Cap in the same units as `size` (e.g. micros)."""
    notes: str = ""

    def with_drawdown_mode(self, mode: str) -> "FirmRules":
        ev = replace(self.eval, phase=replace(self.eval.phase, drawdown_mode=mode))
        fu = None
        if self.funded is not None:
            fu = replace(self.funded, phase=replace(self.funded.phase, drawdown_mode=mode))
        return replace(self, eval=ev, funded=fu, name=f"{self.name} [{mode}]")


# --------------------------------------------------------------------------
# Presets
# --------------------------------------------------------------------------

LUCIDFLEX_50K = FirmRules(
    name="LucidFlex 50K",
    start_balance=50_000.0,
    max_contracts=40,  # micros; 4 minis. Scales with EOD balance (not modeled).
    eval=EvalRules(
        profit_target=3_000.0,
        phase=PhaseRules(max_loss=2_000.0, drawdown_mode="eod_trailing", lock_floor_offset=100.0),
        consistency_max_day_frac=0.5,
        fee=130.0,
        fee_period_days=None,  # vault sources disagree: one-off vs monthly. Verify.
    ),
    funded=FundedRules(
        phase=PhaseRules(max_loss=2_000.0, drawdown_mode="eod_trailing", lock_floor_offset=100.0),
        profit_split=0.9,
        payout_min_days=5,
        payout_day_min_profit=150.0,
        payout_min=500.0,
        payout_frac_of_profit=0.5,
        max_payouts=5,  # sources say 5-6 before moving to a live account
    ),
    notes=(
        "From wiki [[LucidFlex Automated Scalping PRD]], third-party guides read "
        "2026-07-06. MLL lock read as start+$100 per [[Prop-Firm-Eval-Sizing]]. "
        "Re-verify every number at support.lucidtrading.com."
    ),
)

GENERIC_INTRADAY_TRAILING_50K = FirmRules(
    name="Generic 50K (intraday trailing)",
    start_balance=50_000.0,
    max_contracts=50,
    eval=EvalRules(
        profit_target=3_000.0,
        phase=PhaseRules(max_loss=2_500.0, drawdown_mode="intraday_trailing", lock_floor_offset=100.0),
        fee=150.0,
        fee_period_days=21,
    ),
    funded=FundedRules(
        phase=PhaseRules(max_loss=2_500.0, drawdown_mode="intraday_trailing", lock_floor_offset=100.0),
        profit_split=0.9,
        payout_min_days=8,
        payout_day_min_profit=50.0,
        payout_min=500.0,
        payout_max=2_000.0,
        payout_frac_of_profit=0.5,
        consistency_max_day_frac=0.3,
    ),
    notes="Illustrative structure, not any specific firm's rules.",
)

GENERIC_EOD_TRAILING_DLL_50K = FirmRules(
    name="Generic 50K (EOD trailing + daily loss limit)",
    start_balance=50_000.0,
    max_contracts=50,
    eval=EvalRules(
        profit_target=3_000.0,
        phase=PhaseRules(
            max_loss=2_000.0,
            drawdown_mode="eod_trailing",
            lock_floor_offset=0.0,
            daily_loss_limit=1_000.0,
            dll_action="flatten",
        ),
        consistency_max_day_frac=0.5,
        fee=50.0,
        fee_period_days=21,
    ),
    funded=FundedRules(
        phase=PhaseRules(
            max_loss=2_000.0,
            drawdown_mode="eod_trailing",
            lock_floor_offset=0.0,
            daily_loss_limit=1_000.0,
            dll_action="flatten",
        ),
        profit_split=0.9,
        payout_min_days=5,
        payout_day_min_profit=150.0,
        payout_min=100.0,
        payout_frac_of_profit=0.5,
        payout_max=5_000.0,
    ),
    notes="Illustrative structure, not any specific firm's rules.",
)

PRESETS = {
    "lucidflex50k": LUCIDFLEX_50K,
    "generic-intraday50k": GENERIC_INTRADAY_TRAILING_50K,
    "generic-eod-dll50k": GENERIC_EOD_TRAILING_DLL_50K,
}
