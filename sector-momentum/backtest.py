"""Monthly-rebalance backtest engine with drift, costs, and a T-bill cash leg.

Signal and execution both happen at the rebalance day's close (market-on-close,
per the spec). Weights drift with returns between rebalances; turnover cost is
charged on the sum of absolute weight changes at each rebalance.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import strategy as strat
from data import SECTOR_ETFS, TBILL

TRADING_DAYS = 252


def _cash_daily(irx: pd.Series) -> pd.Series:
    """Daily total return of the cash leg from the annualized T-bill yield (%)."""
    y = irx.reindex(irx.index).ffill() / 100.0
    return (1 + y) ** (1 / TRADING_DAYS) - 1


def _trailing_cash_return(cash_daily: pd.Series, dates: pd.DatetimeIndex, pos: int,
                          lookback: int = strat.LOOKBACK) -> float:
    """Compound cash return over the trailing `lookback` days ending at `pos`."""
    if pos < lookback:
        return 0.0
    window = cash_daily.reindex(dates).iloc[pos - lookback:pos].fillna(0)
    return float((1 + window).prod() - 1)


def run(
    prices: pd.DataFrame,
    irx: pd.Series,
    top_n: int = 3,
    band_n: int | None = None,
    use_overlay: bool = True,
    cost_bps: float = 5.0,
    start: str | None = "2000-01-01",
    lookback: int = strat.LOOKBACK,
    blend: bool = False,
    market_series: pd.Series | None = None,
) -> pd.Series:
    """Run one strategy config and return its daily return series.

    lookback: momentum formation window (days), skipping the last month.
    blend: use the multi-horizon rank-blended momentum instead of a single lookback.
    market_series: if given (e.g. SPY), a market-regime gate forces the whole book
        to cash whenever that series' own 12-month return is below the T-bill hurdle.
    """
    sectors = [c for c in SECTOR_ETFS if c in prices.columns]
    px = prices[sectors].copy()
    dates = px.index
    daily_ret = px.pct_change()

    cash_daily = _cash_daily(irx).reindex(dates).fillna(0)
    mkt = market_series.reindex(dates) if market_series is not None else None

    # Rebalance on the last trading day of each month.
    month_end = pd.Series(dates, index=dates).groupby([dates.year, dates.month]).last()
    rebal_dates = pd.DatetimeIndex(month_end.values)
    if start is not None:
        rebal_dates = rebal_dates[rebal_dates >= pd.Timestamp(start)]

    pos_of = {d: i for i, d in enumerate(dates)}
    cost = cost_bps / 10000.0

    weights = {}          # current target weights {ticker: w} incl "CASH"
    port_ret = pd.Series(0.0, index=dates)
    holdings: list[str] = []
    rebal_set = set(rebal_dates)

    # find first rebalance with enough history
    active = False
    for i, d in enumerate(dates):
        # accrue today's return using yesterday's weights (weights drift with prices)
        if weights:
            r = 0.0
            for t, w in weights.items():
                if t == "CASH":
                    r += w * cash_daily.iloc[i]
                else:
                    r += w * (daily_ret[t].iloc[i] if not np.isnan(daily_ret[t].iloc[i]) else 0.0)
            port_ret.iloc[i] = r
            # drift the weights by realized returns
            new_w = {}
            for t, w in weights.items():
                g = 1 + (cash_daily.iloc[i] if t == "CASH" else
                         (daily_ret[t].iloc[i] if not np.isnan(daily_ret[t].iloc[i]) else 0.0))
                new_w[t] = w * g
            tot = sum(new_w.values())
            if tot > 0:
                weights = {t: w / tot for t, w in new_w.items()}

        if d in rebal_set:
            pos = pos_of[d]
            mom = strat.momentum_blend(px, pos) if blend else strat.momentum(px, pos, lookback)
            if mom.empty:
                continue
            ret12 = strat.total_return_12(px, pos)
            hurdle = _trailing_cash_return(cash_daily, dates, pos)
            # market-regime gate: risk-off -> whole book to cash
            if mkt is not None and pos >= strat.LOOKBACK:
                mkt_mom = mkt.iloc[pos] / mkt.iloc[pos - strat.LOOKBACK] - 1
                if pd.notna(mkt_mom) and mkt_mom < hurdle:
                    target = {"CASH": 1.0}
                    turnover = sum(abs(target.get(k, 0.0) - weights.get(k, 0.0))
                                   for k in set(target) | set(weights))
                    port_ret.iloc[i] -= cost * turnover
                    weights = target
                    holdings = []
                    active = True
                    continue
            target = strat.select(mom, ret12, hurdle, holdings,
                                  top_n=top_n, band_n=band_n, use_overlay=use_overlay)
            # turnover cost on sum of absolute weight changes
            all_keys = set(target) | set(weights)
            turnover = sum(abs(target.get(k, 0.0) - weights.get(k, 0.0)) for k in all_keys)
            port_ret.iloc[i] -= cost * turnover
            weights = target
            holdings = [t for t in target if t != "CASH"]
            active = True

    return port_ret[port_ret.index >= (pd.Timestamp(start) if start else dates[0])] if active else port_ret


def benchmark_buyhold(prices: pd.DataFrame, ticker: str, start: str | None = "2000-01-01") -> pd.Series:
    r = prices[ticker].pct_change()
    if start:
        r = r[r.index >= pd.Timestamp(start)]
    return r.fillna(0)


def benchmark_equal_weight(prices: pd.DataFrame, start: str | None = "2000-01-01") -> pd.Series:
    """Monthly-rebalanced equal weight across all available sector ETFs."""
    sectors = [c for c in SECTOR_ETFS if c in prices.columns]
    px = prices[sectors]
    daily = px.pct_change()
    dates = px.index
    month_end = pd.Series(dates, index=dates).groupby([dates.year, dates.month]).last()
    rebal = set(pd.DatetimeIndex(month_end.values))
    out = pd.Series(0.0, index=dates)
    w = None
    for i, d in enumerate(dates):
        if w is not None:
            row = daily.iloc[i].reindex(w.index)
            out.iloc[i] = float((w * row.fillna(0)).sum())
            grown = w * (1 + row.fillna(0))
            w = grown / grown.sum()
        if d in rebal:
            avail = px.iloc[i].dropna().index
            if len(avail):
                w = pd.Series(1.0 / len(avail), index=avail)
    if start:
        out = out[out.index >= pd.Timestamp(start)]
    return out
