#!/usr/bin/env python3
"""Walk-forward validation: pick the config in-sample, then read the out-of-sample
result untouched.

    python3 walkforward.py                       # synthetic, split 2018-01-01
    python3 walkforward.py --split 2020-01-01
    python3 walkforward.py --data ./data --rates ./data/irx.csv --equity 250000

Mirrors sector-momentum/walkforward.py, which is the point: the same discipline,
applied to the futures book, so the two sleeves are judged the same way.

The test that separates an edge from a fitted curve is not "which config had the
best Sharpe" — it is "the config I would have chosen, how did it do on data I had
not seen". A config that wins in-sample and collapses out-of-sample was luck.
Trend books add a second failure mode the equity sleeve does not have: the config
can be right and the *account* still too small to express it, so the realised vol
and the effective market count are reported in both windows.
"""
from __future__ import annotations

import argparse
from datetime import date

import contracts as cx
import data as datamod
import engine
import metrics as mt
import sizing as sz
import strategies as st
import synthetic as syn

SPLIT = date(2018, 1, 1)

CONFIGS = {
    "12m momentum":        st.TimeSeriesMomentum(252),
    "12m long-only":       st.TimeSeriesMomentum(252, allow_short=False),
    "6m momentum":         st.TimeSeriesMomentum(126),
    "50/200 MA cross":     st.MovingAverageCross(50, 200),
    "multi-speed blend":   st.MultiSpeedMomentum(),
    "vol-scaled momentum": st.VolAdjustedMomentum(252),
}
BENCHMARK = ("always long", st.Constant(1.0))


def window(res, lo: date | None, hi: date | None) -> dict:
    """Metrics over one date window of an already-completed run."""
    rows = [r for r in res.records
            if (lo is None or r.date >= lo) and (hi is None or r.date < hi)]
    if len(rows) < 30:
        return {}
    rets = [r.ret for r in rows]
    eq = [r.equity for r in rows]
    rf_ann = mt.mean([res.config.rates.annual(r.date) for r in rows])
    rf_daily = (1 + rf_ann) ** (1 / mt.TRADING_DAYS) - 1
    costs = sum(r.costs for r in rows)
    base = mt.mean(eq)
    years = len(rows) / mt.TRADING_DAYS
    return {
        "n": len(rows),
        "sharpe": mt.sharpe(rets, rf_daily),
        "cagr": mt.cagr(rets),
        "vol": mt.ann_vol(rets),
        "maxdd": mt.max_drawdown(eq),
        "cost_drag": costs / years / base if years and base else 0.0,
        "eff_mkts": mt.mean([r.effective_markets for r in rows]),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data")
    p.add_argument("--rates")
    p.add_argument("--markets", default=None)
    p.add_argument("--equity", type=float, default=100_000.0)
    p.add_argument("--vol-target", type=float, default=0.10)
    p.add_argument("--split", default=str(SPLIT))
    p.add_argument("--start", default="2010-01-04")
    p.add_argument("--end", default="2026-06-30")
    p.add_argument("--seed", type=int, default=20260919)
    args = p.parse_args(argv)

    split = datamod.parse_date(args.split)
    start, end = datamod.parse_date(args.start), datamod.parse_date(args.end)
    if args.markets:
        syms = tuple(s.strip().upper() for s in args.markets.split(",") if s.strip())
    else:
        syms, _ = sz.universe_for(args.equity, args.vol_target)

    if args.data:
        book = datamod.load_book(args.data, syms)
        rates = (datamod.load_rates(args.rates) if args.rates
                 else datamod.constant_rate(0.04))
        synthetic = False
    else:
        book = syn.synthetic_book(syms, start=start, end=end, seed=args.seed)
        rates = (datamod.load_rates(args.rates) if args.rates
                 else syn.synthetic_rates(start, end))
        synthetic = True

    cfg = engine.BacktestConfig(start=start, end=end, initial_equity=args.equity,
                                vol_target=args.vol_target, rates=rates)

    print("=" * 84)
    print(f"WALK-FORWARD  split {split}   ${args.equity:,.0f}  "
          f"{100*args.vol_target:.0f}% vol target")
    print(f"  book: {', '.join(syms)}"
          f"{'' if args.markets else '  (chosen by capacity at this equity)'}")
    print("=" * 84)
    if synthetic:
        print("  !! SYNTHETIC DATA: trends by construction, so IS and OOS are drawn")
        print("     from the same generator and degradation is understated. This run")
        print("     checks the discipline; only real bars check the edge.")

    runs = {name: engine.run(book, cfg, strat) for name, strat in CONFIGS.items()}
    bench_name, bench_strat = BENCHMARK
    runs[bench_name] = engine.run(book, cfg, bench_strat)

    hdr = (f"\n  {'config':<20}{'IS Shrp':>9}{'IS CAGR':>9}{'OOS Shrp':>10}"
           f"{'OOS CAGR':>10}{'OOS vol':>9}{'OOS MaxDD':>11}{'OOS cost':>10}{'eff mkt':>9}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 3))

    rows = {}
    for name, res in runs.items():
        i, o = window(res, None, split), window(res, split, None)
        if not i or not o:
            print(f"  {name:<20} insufficient data either side of the split")
            continue
        rows[name] = (i, o)
        print(f"  {name:<20}{i['sharpe']:>9.2f}{100*i['cagr']:>8.1f}%"
              f"{o['sharpe']:>10.2f}{100*o['cagr']:>9.1f}%{100*o['vol']:>8.1f}%"
              f"{100*o['maxdd']:>10.1f}%{100*o['cost_drag']:>9.2f}%"
              f"{o['eff_mkts']:>9.1f}")

    if bench_name not in rows or len(rows) < 2:
        print("\n  not enough history either side of the split to conclude anything")
        return 1

    candidates = {k: v for k, v in rows.items() if k != bench_name}
    picked = max(candidates, key=lambda k: candidates[k][0]["sharpe"])
    pi, po = candidates[picked]
    bi, bo = rows[bench_name]

    print(f"\n  Chosen on IN-SAMPLE Sharpe alone: {picked}")
    print(f"    in-sample      Sharpe {pi['sharpe']:>5.2f}  CAGR {100*pi['cagr']:>5.1f}%")
    print(f"    out-of-sample  Sharpe {po['sharpe']:>5.2f}  CAGR {100*po['cagr']:>5.1f}%  "
          f"MaxDD {100*po['maxdd']:.1f}%")
    print(f"    benchmark OOS  Sharpe {bo['sharpe']:>5.2f}  CAGR {100*bo['cagr']:>5.1f}%  "
          f"MaxDD {100*bo['maxdd']:.1f}%   ({bench_name})")

    degrade = pi["sharpe"] - po["sharpe"]
    print(f"\n    Sharpe degradation IS->OOS: {degrade:+.2f}")
    best_oos = max(candidates, key=lambda k: candidates[k][1]["sharpe"])
    if best_oos != picked:
        print(f"    (the best OOS config was {best_oos} — you could not have known that,"
              " which is the whole point)")

    verdicts = []
    if po["sharpe"] < bo["sharpe"]:
        verdicts.append("FAILS to beat always-long out-of-sample. Do not trade it.")
    elif degrade > 0.4:
        verdicts.append("beats the benchmark OOS but degrades hard from IS. "
                        "Weak edge; size tiny or shelve.")
    else:
        verdicts.append("holds up out-of-sample and beats always-long. "
                        "Candidate for paper trading.")
    ratio = po["vol"] / args.vol_target if args.vol_target else 0
    if ratio < 0.8:
        scaled = "scaled" in picked or "vol-scaled" in picked or "multi" in picked
        because = ("partly by design for a scaled-forecast config, but check it against "
                   "capacity.py" if scaled else
                   "the account cannot express this book. Run capacity.py before funding")
        verdicts.append(f"SIZING: realised OOS vol is {ratio:.2f}x target — {because}.")
    if po["cost_drag"] > 0.01:
        verdicts.append(f"COSTS: {100*po['cost_drag']:.2f}%/yr of equity is high for a "
                        "slow book; check the roll schedule and the rebalance cadence.")
    if po["eff_mkts"] < 0.7 * len(syms):
        verdicts.append(f"CONCENTRATION: {po['eff_mkts']:.1f} effective markets of "
                        f"{len(syms)} held — rounding is collapsing the diversification.")
    print("\n  VERDICT")
    for v in verdicts:
        print(f"    - {v}")
    print("\n  Declare all "
          f"{len(CONFIGS)} configs to the deflated Sharpe, not just the winner.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
