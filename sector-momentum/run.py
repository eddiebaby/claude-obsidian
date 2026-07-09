"""Orchestrator: fetch data, run every strategy variant + benchmarks, print the
comparison table, deflate the Sharpe by the honest trial count, save equity curves.

Usage:
    python run.py            # uses cached data if present
    python run.py --refresh  # re-download the universe
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

import backtest as bt
import metrics as m
from data import BENCHMARK, TBILL, load

OUT = Path(__file__).parent / "results"


def main(refresh: bool = False, start: str = "2000-01-01"):
    START = start
    print("Loading universe...")
    px = load(refresh=refresh)
    irx = px[TBILL]
    prices = px.drop(columns=[TBILL])
    rf_daily = bt._cash_daily(irx)

    # --- the honest trial list: every config we actually evaluate ---
    configs = {
        "Plain top-3 (no overlay)":        dict(top_n=3, band_n=None, use_overlay=False),
        "Top-3 + abs-mom overlay":         dict(top_n=3, band_n=None, use_overlay=True),
        "Top-3 + overlay + band(4)":       dict(top_n=3, band_n=4,    use_overlay=True),
        "Top-2 + overlay":                 dict(top_n=2, band_n=None, use_overlay=True),
        "Top-4 + overlay":                 dict(top_n=4, band_n=None, use_overlay=True),
        "Top-3 + overlay + band(5)":       dict(top_n=3, band_n=5,    use_overlay=True),
    }

    series = {}
    for name, cfg in configs.items():
        series[name] = bt.run(prices, irx, start=START, **cfg)

    # benchmarks (not counted as strategy trials for deflation)
    series["SPY buy & hold"] = bt.benchmark_buyhold(prices, BENCHMARK, start=START)
    series["Equal-weight sectors"] = bt.benchmark_equal_weight(prices, start=START)

    # align all on a common index
    idx = None
    for s in series.values():
        idx = s.index if idx is None else idx.union(s.index)
    series = {k: v.reindex(idx).fillna(0) for k, v in series.items()}
    rf_daily = rf_daily.reindex(idx).fillna(0)

    # --- summary table ---
    rows = []
    strat_sharpes_monthly = []
    for name in configs:
        summ = m.summary(series[name], rf_daily, name)
        rows.append(summ)
        mo = summ["_monthly"]
        strat_sharpes_monthly.append(mo.mean() / mo.std(ddof=1))
    for name in ["SPY buy & hold", "Equal-weight sectors"]:
        rows.append(m.summary(series[name], rf_daily, name))

    # deflated Sharpe on the best strategy, honest trial count
    n_trials = len(configs)
    sharpe_var = float(np.var(strat_sharpes_monthly, ddof=1))
    best = max(rows[:len(configs)], key=lambda r: (r["Sharpe"] if not np.isnan(r["Sharpe"]) else -9))
    dsr, sr_m, sr0 = m.deflated_sharpe(best["_monthly"], n_trials, sharpe_var)

    # --- print ---
    print(f"\nSample: {idx[0].date()} -> {idx[-1].date()}   ({len(idx)} trading days)\n")
    hdr = f"{'Strategy':<30}{'CAGR':>8}{'Vol':>8}{'Sharpe':>8}{'MaxDD':>9}{'Calmar':>8}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        star = "  <-- best" if r["name"] == best["name"] else ""
        print(f"{r['name']:<30}{r['CAGR']*100:>7.1f}%{r['Vol']*100:>7.1f}%"
              f"{r['Sharpe']:>8.2f}{r['MaxDD']*100:>8.1f}%{r['Calmar']:>8.2f}{star}")

    print(f"\nDeflated Sharpe analysis (Bailey & Lopez de Prado 2014):")
    print(f"  Best config:           {best['name']}")
    print(f"  Trials evaluated (N):  {n_trials}")
    print(f"  Variance of trial SR:  {sharpe_var:.5f}")
    print(f"  Observed monthly SR:   {sr_m:.4f}")
    print(f"  Null expected max SR:  {sr0:.4f}   (what zero-skill would produce over {n_trials} trials)")
    print(f"  P(skill is real), DSR: {dsr:.3f}")
    verdict = "PASSES — Sharpe survives the trial-count haircut" if dsr > 0.95 else \
              "MARGINAL — treat with suspicion" if dsr > 0.90 else \
              "FAILS — likely overfit / not distinguishable from luck"
    print(f"  Verdict:               {verdict}")

    # --- kill-criteria check vs SPY (net) ---
    spy = next(r for r in rows if r["name"] == "SPY buy & hold")
    print(f"\nKill-criteria check (spec): beat SPY buy & hold net of costs?")
    print(f"  Best CAGR {best['CAGR']*100:.1f}% vs SPY {spy['CAGR']*100:.1f}%  "
          f"| Best Sharpe {best['Sharpe']:.2f} vs SPY {spy['Sharpe']:.2f}")

    # --- save equity curves ---
    OUT.mkdir(exist_ok=True)
    eq = pd.DataFrame({k: (1 + v).cumprod() for k, v in series.items()})
    eq.to_csv(OUT / "equity_curves.csv")
    tbl = pd.DataFrame([{k: r[k] for k in ["name", "CAGR", "Vol", "Sharpe", "MaxDD", "Calmar", "months"]}
                        for r in rows]).set_index("name")
    tbl.to_csv(OUT / "summary.csv")
    print(f"\nSaved: {OUT/'equity_curves.csv'}  and  {OUT/'summary.csv'}")


if __name__ == "__main__":
    start = "2000-01-01"
    for a in sys.argv:
        if a.startswith("--start="):
            start = a.split("=", 1)[1]
    main(refresh="--refresh" in sys.argv, start=start)
