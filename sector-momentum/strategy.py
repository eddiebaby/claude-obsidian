"""Signal construction: 12-1 momentum, cross-sectional rank, absolute-momentum overlay.

All signals are computed on the daily adjusted-close panel using integer positional
lookbacks so there is no lookahead: at a rebalance date d, everything uses prices
through d's close, and the resulting weights are held from d forward.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

LOOKBACK = 252   # 12 months of trading days
SKIP = 21        # skip the most recent month (avoids short-term reversal)


def momentum(prices: pd.DataFrame, pos: int, lookback: int = LOOKBACK, skip: int = SKIP) -> pd.Series:
    """Momentum at row `pos`: P[pos-skip] / P[pos-lookback] - 1, per column."""
    if pos < lookback:
        return pd.Series(dtype=float)
    mom = prices.iloc[pos - skip] / prices.iloc[pos - lookback] - 1
    return mom.dropna()


def momentum_blend(prices: pd.DataFrame, pos: int, lookbacks=(63, 126, 189, 252), skip: int = SKIP) -> pd.Series:
    """Average of rank-normalized momentum across several lookbacks (multi-horizon)."""
    parts = []
    for lb in lookbacks:
        s = momentum(prices, pos, lb, skip)
        if not s.empty:
            parts.append(s.rank(pct=True))
    if not parts:
        return pd.Series(dtype=float)
    return pd.concat(parts, axis=1).mean(axis=1).dropna()


def momentum_12_1(prices: pd.DataFrame, pos: int) -> pd.Series:
    return momentum(prices, pos, LOOKBACK, SKIP)


def total_return_12(prices: pd.DataFrame, pos: int) -> pd.Series:
    """Full 12-month return at row `pos`: P[pos] / P[pos-LOOKBACK] - 1 (abs-mom filter)."""
    if pos < LOOKBACK:
        return pd.Series(dtype=float)
    return (prices.iloc[pos] / prices.iloc[pos - LOOKBACK] - 1).dropna()


def select(
    mom: pd.Series,
    ret12: pd.Series,
    hurdle: float,
    prev_holdings: list[str],
    top_n: int = 3,
    band_n: int | None = None,
    use_overlay: bool = True,
) -> dict[str, float]:
    """Return target weights {ticker: weight} for the sector slots.

    - top_n slots, equal weight (1/top_n each).
    - band_n: keep a current holding if it is still within the top `band_n` by
      momentum, even if it fell out of the top_n (turnover control). None = no band.
    - use_overlay: a slot whose ETF's 12-month total return is below `hurdle`
      (the T-bill return) is moved to cash. Cash weight is the complement.
    Weights sum to <= 1; the remainder is cash.
    """
    ranked = mom.sort_values(ascending=False)
    if ranked.empty:
        return {"CASH": 1.0}

    top = list(ranked.index[:top_n])

    if band_n is not None and prev_holdings:
        band = set(ranked.index[:band_n])
        kept = [h for h in prev_holdings if h in band and h in ranked.index]
        selected = list(kept)
        for t in top:
            if len(selected) >= top_n:
                break
            if t not in selected:
                selected.append(t)
        # backfill if band-keeps left us short
        for t in ranked.index:
            if len(selected) >= top_n:
                break
            if t not in selected:
                selected.append(t)
        selected = selected[:top_n]
    else:
        selected = top

    slot = 1.0 / top_n
    weights: dict[str, float] = {}
    cash = 0.0
    for t in selected:
        if use_overlay and float(ret12.get(t, -np.inf)) < hurdle:
            cash += slot
        else:
            weights[t] = weights.get(t, 0.0) + slot
    # unfilled slots (universe smaller than top_n early on) -> cash
    filled = len(selected)
    if filled < top_n:
        cash += (top_n - filled) * slot
    if cash > 1e-9:
        weights["CASH"] = cash
    return weights
