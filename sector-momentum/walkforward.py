"""Walk-forward validation (spec step 4): choose the config on the in-sample window
(2000-2015), then report its performance out-of-sample (2016-present) UNTOUCHED.

This is the test that separates a real edge from an overfit one. A config that
looks best in-sample and then collapses out-of-sample was luck, not signal.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import backtest as bt
import metrics as m
from data import BENCHMARK, TBILL, load

SPLIT = "2016-01-01"
START = "2000-01-01"

CONFIGS = {
    "Plain top-3 (no overlay)":  dict(top_n=3, band_n=None, use_overlay=False),
    "Top-3 + overlay":           dict(top_n=3, band_n=None, use_overlay=True),
    "Top-3 + overlay + band(4)": dict(top_n=3, band_n=4,    use_overlay=True),
    "Top-3 + overlay + band(5)": dict(top_n=3, band_n=5,    use_overlay=True),
    "Top-2 + overlay":           dict(top_n=2, band_n=None, use_overlay=True),
    "Top-4 + overlay":           dict(top_n=4, band_n=None, use_overlay=True),
}


def _sharpe_window(daily: pd.Series, rf: pd.Series, lo: str, hi: str | None) -> tuple:
    w = daily[(daily.index >= lo) & (daily.index < hi)] if hi else daily[daily.index >= lo]
    rfw = rf.reindex(w.index).fillna(0)
    return m.sharpe(w, rfw), m.cagr(w), m.max_drawdown(w)


def main():
    px = load()
    irx = px[TBILL]
    prices = px.drop(columns=[TBILL])
    rf = bt._cash_daily(irx)

    series = {name: bt.run(prices, irx, start=START, **cfg) for name, cfg in CONFIGS.items()}
    spy = bt.benchmark_buyhold(prices, BENCHMARK, start=START)

    print(f"Walk-forward split at {SPLIT}\n")
    hdr = f"{'Config':<28}{'IS Shrp':>9}{'IS CAGR':>9}{'OOS Shrp':>10}{'OOS CAGR':>10}{'OOS MaxDD':>11}"
    print(hdr); print("-" * len(hdr))

    is_ranking = []
    for name, s in series.items():
        is_sh, is_cg, _ = _sharpe_window(s, rf, START, SPLIT)
        oos_sh, oos_cg, oos_dd = _sharpe_window(s, rf, SPLIT, None)
        is_ranking.append((name, is_sh, oos_sh, oos_cg, oos_dd))
        print(f"{name:<28}{is_sh:>9.2f}{is_cg*100:>8.1f}%{oos_sh:>10.2f}{oos_cg*100:>9.1f}%{oos_dd*100:>10.1f}%")

    spy_is = _sharpe_window(spy, rf, START, SPLIT)
    spy_oos = _sharpe_window(spy, rf, SPLIT, None)
    print(f"{'SPY buy & hold':<28}{spy_is[0]:>9.2f}{spy_is[1]*100:>8.1f}%{spy_oos[0]:>10.2f}{spy_oos[1]*100:>9.1f}%{spy_oos[2]*100:>10.1f}%")

    # The honest pick: best by IN-SAMPLE Sharpe, then read its OUT-OF-SAMPLE result.
    picked = max(is_ranking, key=lambda r: r[1])
    print(f"\nConfig chosen on in-sample (2000-2015) Sharpe: {picked[0]}")
    print(f"  In-sample Sharpe:   {picked[1]:.2f}")
    print(f"  Out-of-sample Sharpe:{picked[2]:>6.2f}   CAGR {picked[3]*100:.1f}%   MaxDD {picked[4]*100:.1f}%")
    print(f"  SPY out-of-sample:   {spy_oos[0]:.2f}   CAGR {spy_oos[1]*100:.1f}%   MaxDD {spy_oos[2]*100:.1f}%")

    degrade = picked[1] - picked[2]
    print(f"\n  Sharpe degradation IS->OOS: {degrade:+.2f}")
    if picked[2] < spy_oos[0]:
        print("  VERDICT: the chosen config FAILS to beat SPY out-of-sample. Do not trade it as-is.")
    elif degrade > 0.4:
        print("  VERDICT: beats SPY OOS but degrades hard from IS. Weak edge; size tiny or shelve.")
    else:
        print("  VERDICT: holds up out-of-sample and beats SPY. Candidate for paper trading.")


if __name__ == "__main__":
    main()
