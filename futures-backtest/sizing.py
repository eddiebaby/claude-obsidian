"""Position sizing: risk targeting in integer contracts, with margin as a hard wall.

This is where a futures book is won or lost. The signal says *which way*; this
module decides *how much*, and at retail equity the answer is frequently "zero
contracts", which silently concentrates the book into whichever markets happen
to be cheap. `diversification` reports that instead of letting it hide.

Sizing follows the standard volatility-target form (Carver):

    contracts = (equity * tau * weight * IDM * signal) / (ann_vol_$ per contract)

with `ann_vol_$ per contract` = annualised vol x price x multiplier x fx for a
percent-vol market, or annualised vol of price *differences* x multiplier x fx
for a yield-quoted one, where percent vol is meaningless.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import contracts as cx

TRADING_DAYS = 252


# --- volatility estimation ---------------------------------------------------

def _risk_series(values: list[float], basis: str = "pct",
                 base: list[float] | None = None) -> list[float]:
    """Turn a price history into the series whose vol we want.

    basis 'abs' -> first differences (yield contracts, anything that can cross
    zero). basis 'pct' -> differences divided by the *actual* contract price.

    That denominator is the subtle part. A panama-adjusted series' level is
    fictional: with persistent backwardation it drifts down, and on crude over
    twenty years it can go negative outright, at which point `adj_t/adj_t-1 - 1`
    is garbage. Only its differences are real. So percent returns are computed
    as (adjusted difference) / (unadjusted price you could actually trade),
    which is both well-defined and the number that scales dollar risk.
    """
    xs: list[float] = []
    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]
        if basis == "abs":
            xs.append(diff)
            continue
        denom = base[i - 1] if base is not None and i - 1 < len(base) else values[i - 1]
        if not denom:
            continue
        xs.append(diff / abs(denom))
    return xs


def ewma_vol(values: list[float], span: int = 60, basis: str = "pct",
             min_obs: int = 25, base: list[float] | None = None) -> float | None:
    """Annualised EWMA volatility of an adjusted price series.

    `base` is the parallel series of *unadjusted* prices used as the denominator
    for percent returns; omit it and the adjusted levels are their own base
    (fine for a short window, wrong over decades — see `_risk_series`).

    Returns None when there is not enough history: the engine must then hold no
    position rather than guess a size.
    """
    xs = _risk_series(values, basis=basis, base=base)
    if len(xs) < min_obs:
        return None
    lam = 2.0 / (span + 1.0)
    var = None
    for x in xs:
        var = x * x if var is None else (1 - lam) * var + lam * x * x
    if var is None or var <= 0:
        return None
    return math.sqrt(var * TRADING_DAYS)


def blended_vol(values: list[float], span: int = 60, basis: str = "pct",
                weight_recent: float = 0.7, min_obs: int = 25,
                base: list[float] | None = None) -> float | None:
    """EWMA vol blended with the long-run sample vol.

    Pure short-window vol collapses in quiet tape and hands back a position
    several times too large going into the next shock. The blend is the cheapest
    known fix and costs nothing in complexity.
    """
    fast = ewma_vol(values, span=span, basis=basis, min_obs=min_obs, base=base)
    if fast is None:
        return None
    xs = _risk_series(values, basis=basis, base=base)
    if len(xs) < min_obs:
        return fast
    m = sum(xs) / len(xs)
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    slow = math.sqrt(max(var, 0.0) * TRADING_DAYS)
    if slow <= 0:
        return fast
    w = min(max(weight_recent, 0.0), 1.0)
    return w * fast + (1 - w) * slow


# --- sizing -----------------------------------------------------------------

def risk_per_contract(spec: cx.ContractSpec, price: float, ann_vol: float,
                      fx: float = 1.0) -> float:
    """Annualised account-currency risk of holding ONE contract."""
    if spec.vol_basis == "abs":
        return abs(ann_vol) * spec.multiplier * fx
    return abs(ann_vol) * abs(price) * spec.multiplier * fx


def notional(spec: cx.ContractSpec, price: float, contracts: float,
             fx: float = 1.0) -> float:
    """Signed notional exposure. Futures require no cash for this — which is
    exactly why it has to be measured."""
    return contracts * price * spec.multiplier * fx


def idm_for(n_markets: int, avg_corr: float = 0.15, cap: float = 2.5) -> float:
    """Instrument diversification multiplier for an equal-weight book.

    IDM = sqrt(n / (1 + (n-1) * rho)) under an equicorrelation assumption: the
    factor by which you can scale up because the markets do not move together.
    Capped, because the correlation assumption fails precisely when it matters.
    """
    n = max(1, int(n_markets))
    rho = min(max(avg_corr, 0.0), 0.99)
    return min(cap, math.sqrt(n / (1.0 + (n - 1) * rho)))


def position_scale(equity: float, spec: cx.ContractSpec, price: float,
                   ann_vol: float, weight: float, vol_target: float,
                   idm: float = 1.0, fx: float = 1.0) -> float:
    """Contracts held at full conviction (|signal| = 1). Not yet rounded."""
    rpc = risk_per_contract(spec, price, ann_vol, fx)
    if rpc <= 0 or equity <= 0:
        return 0.0
    return (equity * vol_target * weight * idm * spec.risk_weight) / rpc


def buffered_target(current: int, raw_target: float, scale: float,
                    buffer_frac: float = 0.10) -> int:
    """Trade only to the edge of a no-trade band around the raw target.

    Without this, a vol-targeted book churns every rebalance on rounding noise
    alone; with a 10% band, turnover drops by roughly half for a few basis
    points of tracking error against the unbuffered position.
    """
    if buffer_frac <= 0:
        return int(round(raw_target))
    width = buffer_frac * abs(scale)
    lower, upper = raw_target - width, raw_target + width
    if current < math.floor(lower + 0.5):
        return int(round(lower))
    if current > math.ceil(upper - 0.5):
        return int(round(upper))
    return current


# --- margin -----------------------------------------------------------------

def margin_required(positions: dict[str, int], prices: dict[str, float],
                    specs: dict[str, cx.ContractSpec],
                    maintenance: bool = False) -> float:
    """Total margin for a book. Flat-rate per contract, no cross-margin credit —
    conservative, which is the right direction to be wrong in."""
    total = 0.0
    for sym, q in positions.items():
        if not q:
            continue
        spec = specs[sym]
        m = spec.maintenance_margin if maintenance else spec.initial_margin
        total += abs(q) * m
    return total


def scale_to_margin_cap(positions: dict[str, int], prices: dict[str, float],
                        specs: dict[str, cx.ContractSpec], equity: float,
                        cap: float = 0.25) -> tuple[dict[str, int], bool]:
    """Shrink the whole book proportionally until margin/equity <= cap.

    Returns (positions, was_scaled). Scaling is proportional so the book keeps
    its shape; markets round to zero from the bottom up, which is reported by
    `diversification` rather than silently accepted.
    """
    if equity <= 0:
        return {s: 0 for s in positions}, bool(any(positions.values()))
    limit = cap * equity
    used = margin_required(positions, prices, specs)
    if used <= limit or used <= 0:
        return dict(positions), False
    k = limit / used
    out = {}
    for sym, q in positions.items():
        shrunk = int(math.floor(abs(q) * k)) * (1 if q >= 0 else -1)
        out[sym] = shrunk
    # Rounding down can still leave the biggest single contract over the cap.
    while margin_required(out, prices, specs) > limit and any(out.values()):
        worst = max((s for s in out if out[s]),
                    key=lambda s: abs(out[s]) * specs[s].initial_margin)
        out[worst] -= 1 if out[worst] > 0 else -1
    return out, True


# --- diagnostics -------------------------------------------------------------

@dataclass
class Diversification:
    """How many markets the book is *actually* risking, versus how many it holds."""

    held: int
    intended: int
    effective: float          # exp(entropy) of risk shares — 1.0 = all in one
    zeroed: tuple[str, ...]   # markets whose target rounded to zero contracts

    @property
    def rounding_loss(self) -> int:
        return len(self.zeroed)


def diversification(positions: dict[str, int], risk_each: dict[str, float],
                    intended: int | None = None) -> Diversification:
    """Effective market count from the entropy of the risk distribution.

    A book "holding 8 markets" where MES carries 70% of the risk is a 2-market
    book. This is the number to watch as equity shrinks and contracts round off.
    """
    risks = {s: abs(positions.get(s, 0)) * risk_each.get(s, 0.0) for s in risk_each}
    total = sum(risks.values())
    held = sum(1 for s, q in positions.items() if q)
    zeroed = tuple(sorted(s for s in risk_each if not positions.get(s, 0)))
    if total <= 0:
        return Diversification(held, intended or len(risk_each), 0.0, zeroed)
    ent = 0.0
    for r in risks.values():
        p = r / total
        if p > 0:
            ent -= p * math.log(p)
    return Diversification(held, intended or len(risk_each), math.exp(ent), zeroed)


def min_equity_for_one(spec: cx.ContractSpec, price: float, ann_vol: float,
                       weight: float, vol_target: float, idm: float = 1.0,
                       fx: float = 1.0) -> float:
    """Equity at which this market's full-conviction position reaches ONE contract.

    Below this number the market is in the book on paper and flat in reality.
    Checking it before trading is the difference between "I run an 8-market
    trend book" and "I run a 4-market trend book and a spreadsheet that says 8".
    """
    rpc = risk_per_contract(spec, price, ann_vol, fx)
    denom = vol_target * weight * idm * spec.risk_weight
    if denom <= 0:
        return float("inf")
    return rpc / denom
