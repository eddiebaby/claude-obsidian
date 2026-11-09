"""Campaign Monte Carlo: buy evaluations until one passes, then run the funded account.

A campaign is one trader-year (by default): resample a day sequence from the
bank, attempt evaluations back to back (each attempt costs its fee), and once
one passes, trade the funded account on the remaining days. Sizes are compared
with common random numbers: simulation i uses the same day sequence at every size.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

from .engine import Controls, run_eval, run_funded
from .paths import Day, DayStream, stationary_bootstrap_indices
from .rules import FirmRules


@dataclass(frozen=True)
class CampaignResult:
    passes: int
    fails: int
    attempts: int
    days_to_pass: Optional[int]
    fees: float
    funded_outcome: Optional[str]
    payouts: int
    trader_take: float
    open_at_horizon: bool = False
    """An evaluation attempt was still running when the horizon ended (its fee is in `fees`)."""

    @property
    def net(self) -> float:
        return self.trader_take - self.fees


def run_campaign(
    bank: Sequence[Day],
    firm: FirmRules,
    size: float,
    rng: np.random.Generator,
    horizon_days: int = 252,
    max_attempts: int = 5,
    block: float = 10.0,
    eval_ctl: Controls = Controls(),
    funded_ctl: Controls = Controls(),
) -> CampaignResult:
    idx = stationary_bootstrap_indices(len(bank), horizon_days, block, rng)
    stream = DayStream(bank, idx)
    passes = fails = attempts = 0
    fees = 0.0
    while attempts < max_attempts:
        attempts += 1
        res = run_eval(stream, firm, size, eval_ctl)
        if res.outcome == "horizon" and res.days == 0:
            attempts -= 1  # nothing left to trade; no fee paid
            break
        fees += res.fees
        if res.outcome == "passed":
            passes += 1
            days_to_pass = stream.used
            if firm.funded is None:
                return CampaignResult(1, fails, attempts, days_to_pass, fees, None, 0, 0.0)
            fr = run_funded(stream, firm, size, funded_ctl)
            return CampaignResult(1, fails, attempts, days_to_pass, fees, fr.outcome, fr.payouts, fr.trader_take)
        if res.outcome == "horizon":
            # attempt still open when the horizon ended: neither pass nor fail
            return CampaignResult(passes, fails, attempts, None, fees, None, 0, 0.0, open_at_horizon=True)
        fails += 1
    return CampaignResult(passes, fails, attempts, None, fees, None, 0, 0.0)


@dataclass(frozen=True)
class Summary:
    size: float
    sims: int
    pass_rate: float
    """Passes / completed attempts (attempts still open at the horizon excluded)."""
    p_funded: float
    median_days_to_pass: Optional[float]
    mean_fees: float
    mean_payouts: float
    mean_take: float
    ev: float
    p_net_positive: float
    funded_breach_rate: Optional[float]
    p5_net: float
    p95_net: float
    p_open_at_horizon: float = 0.0
    """Share of campaigns that ended mid-attempt; such attempts are excluded from pass_rate."""


def simulate(
    bank: Sequence[Day],
    firm: FirmRules,
    size: float,
    sims: int = 2000,
    seed: int = 0,
    **kw,
) -> Summary:
    if firm.max_contracts is not None and size > firm.max_contracts:
        raise ValueError(f"size {size} exceeds {firm.name} cap of {firm.max_contracts}")
    results = [run_campaign(bank, firm, size, np.random.default_rng([seed, i]), **kw) for i in range(sims)]
    passes = sum(r.passes for r in results)
    completed = sum(r.passes + r.fails for r in results)
    d2p = [r.days_to_pass for r in results if r.days_to_pass is not None]
    funded = [r for r in results if r.funded_outcome is not None]
    nets = np.array([r.net for r in results])
    return Summary(
        size=size,
        sims=sims,
        pass_rate=passes / completed if completed else float("nan"),
        p_funded=sum(1 for r in results if r.passes) / sims,
        median_days_to_pass=float(np.median(d2p)) if d2p else None,
        mean_fees=float(np.mean([r.fees for r in results])),
        mean_payouts=float(np.mean([r.payouts for r in results])),
        mean_take=float(np.mean([r.trader_take for r in results])),
        ev=float(nets.mean()),
        p_net_positive=float((nets > 0).mean()),
        funded_breach_rate=(
            sum(1 for r in funded if r.funded_outcome in ("breach", "dll_fail")) / len(funded) if funded else None
        ),
        p5_net=float(np.percentile(nets, 5)),
        p95_net=float(np.percentile(nets, 95)),
        p_open_at_horizon=sum(r.open_at_horizon for r in results) / sims,
    )


def sweep(bank: Sequence[Day], firm: FirmRules, sizes: Sequence[float], **kw) -> list[Summary]:
    return [simulate(bank, firm, s, **kw) for s in sizes]


def to_markdown(rows: Sequence[Summary], title: str = "") -> str:
    def f(x, fmt):
        return "—" if x is None else format(x, fmt)

    out = []
    if title:
        out.append(f"**{title}**\n")
    out.append(
        "| Size | Pass/attempt | P(funded) | Days to funded (median) | Fees | Payouts | Take | EV | P(net>0) | Funded breach | Open at horizon | Net p5 / p95 |"
    )
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        out.append(
            f"| {r.size:g} | {r.pass_rate:.0%} | {r.p_funded:.0%} | {f(r.median_days_to_pass, '.0f')} "
            f"| ${r.mean_fees:,.0f} | {r.mean_payouts:.2f} | ${r.mean_take:,.0f} | **${r.ev:,.0f}** "
            f"| {r.p_net_positive:.0%} | {f(r.funded_breach_rate, '.0%')} | {r.p_open_at_horizon:.0%} "
            f"| ${r.p5_net:,.0f} / ${r.p95_net:,.0f} |"
        )
    return "\n".join(out)
