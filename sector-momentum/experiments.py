"""Principled improvement experiments — NOT a config sweep.

Each variant is a distinct economic idea, tested on BOTH the last-15y window
(2011-2026, no 2008) and the full sample (2000-2026). A variant only counts as
an improvement if it beats SPY on BOTH windows. Anything that only beats SPY on
one window is fit to that window, not signal.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import backtest as bt
import metrics as m
from data import BENCHMARK, TBILL, load

WINDOWS = {"Last 15y (2011-)": "2011-01-01", "Full (2000-)": "2000-01-01"}


def stats(daily: pd.Series, rf: pd.Series) -> tuple[float, float, float]:
    rfw = rf.reindex(daily.index).fillna(0)
    return m.cagr(daily), m.sharpe(daily, rfw), m.max_drawdown(daily)


def main():
    px = load()
    irx = px[TBILL]
    spy_px = px[BENCHMARK]
    prices = px.drop(columns=[TBILL])
    rf = bt._cash_daily(irx)

    # Each variant: name -> lambda(start) -> daily returns
    variants = {
        "Baseline: top-3 + overlay + band(5)":
            lambda s: bt.run(prices, irx, top_n=3, band_n=5, use_overlay=True, start=s),
        "Idea 1: faster momentum (6-1 lookback)":
            lambda s: bt.run(prices, irx, top_n=3, band_n=5, use_overlay=True, lookback=126, start=s),
        "Idea 2: multi-horizon blend (3/6/9/12)":
            lambda s: bt.run(prices, irx, top_n=3, band_n=5, use_overlay=True, blend=True, start=s),
        "Idea 3: market-regime gate (SPY dual-mom)":
            lambda s: bt.run(prices, irx, top_n=3, band_n=5, use_overlay=False,
                             market_series=spy_px, start=s),
        "Idea 4: concentrated top-2, no overlay drag":
            lambda s: bt.run(prices, irx, top_n=2, band_n=3, use_overlay=False, start=s),
        "Idea 5: gate + blend (2+3 combined)":
            lambda s: bt.run(prices, irx, top_n=3, band_n=5, use_overlay=False,
                             blend=True, market_series=spy_px, start=s),
    }

    results = {}
    for wname, start in WINDOWS.items():
        rows = []
        spy = bt.benchmark_buyhold(prices, BENCHMARK, start=start)
        spy_c, spy_s, spy_d = stats(spy, rf)
        for name, fn in variants.items():
            c, sh, dd = stats(fn(start), rf)
            rows.append((name, c, sh, dd, sh - spy_s))
        results[wname] = (rows, (spy_c, spy_s, spy_d))

    for wname, (rows, (spy_c, spy_s, spy_d)) in results.items():
        print(f"\n=== {wname} ===   SPY: CAGR {spy_c*100:.1f}%  Sharpe {spy_s:.2f}  MaxDD {spy_d*100:.1f}%")
        hdr = f"{'Variant':<44}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>9}{'vs SPY':>9}"
        print(hdr); print("-" * len(hdr))
        for name, c, sh, dd, edge in rows:
            beat = "  BEATS" if sh > spy_s else ""
            print(f"{name:<44}{c*100:>7.1f}%{sh:>8.2f}{dd*100:>8.1f}%{edge:>+9.2f}{beat}")

    # robustness verdict: beat SPY Sharpe on BOTH windows?
    print("\n=== Robustness: beats SPY Sharpe on BOTH windows? ===")
    names = list(variants)
    for nm in names:
        beats = []
        for wname, (rows, (_, spy_s, _)) in results.items():
            sh = next(r[2] for r in rows if r[0] == nm)
            beats.append(sh > spy_s)
        verdict = "ROBUST (both)" if all(beats) else \
                  "bull-only fit" if beats[0] and not beats[1] else \
                  "crash-only" if beats[1] and not beats[0] else "beats neither"
        print(f"  {nm:<46} {verdict}")


if __name__ == "__main__":
    main()
