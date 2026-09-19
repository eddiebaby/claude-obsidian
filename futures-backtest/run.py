#!/usr/bin/env python3
"""CLI: run a futures backtest and print the things that decide whether it is real.

    python3 run.py                          # synthetic demo book, 12-month trend
    python3 run.py --equity 250000          # see what capital fixes
    python3 run.py --strategy ma --fast 50 --slow 200
    python3 run.py --compare                # strategies + roll-method sensitivity
    python3 run.py --data ./data --start 2005-01-01   # real contract bars
    python3 run.py --csv                    # write results/ for further analysis

Headline metrics come last on purpose. The first thing printed is capacity:
whether the account can hold the positions the risk target implies. A Sharpe
computed on positions you cannot actually carry is fiction.
"""
from __future__ import annotations

import argparse
import csv as csvmod
import sys
from datetime import date
from pathlib import Path

import contracts as cx
import data as datamod
import engine
import metrics as mt
import roll as rollmod
import sizing as sz
import strategies as st
import synthetic as syn

RESULTS = Path(__file__).parent / "results"


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_argument_group("data")
    src.add_argument("--data", help="directory of per-contract CSVs (data/MES/MESH26.csv)")
    src.add_argument("--rates", help="CSV of the collateral rate (e.g. ^IRX), percent")
    src.add_argument("--rate", type=float, default=None,
                     help="flat annual collateral rate if no --rates file")
    src.add_argument("--markets", default=",".join(cx.MICRO_UNIVERSE),
                     help="comma-separated symbols")
    src.add_argument("--start", default=None)
    src.add_argument("--end", default=None)
    src.add_argument("--seed", type=int, default=20260919, help="synthetic data seed")

    risk = p.add_argument_group("risk")
    risk.add_argument("--equity", type=float, default=100_000.0)
    risk.add_argument("--vol-target", type=float, default=0.10)
    risk.add_argument("--vol-span", type=int, default=60)
    risk.add_argument("--idm", type=float, default=None)
    risk.add_argument("--margin-cap", type=float, default=0.25)
    risk.add_argument("--buffer", type=float, default=0.10)
    risk.add_argument("--fixed", type=int, default=None,
                      help="hold N contracts per market instead of risk sizing "
                           "(benchmark / diagnostic mode)")

    trade = p.add_argument_group("trading")
    trade.add_argument("--strategy", default="tsm", choices=sorted(st.REGISTRY))
    trade.add_argument("--lookback", type=int, default=252)
    trade.add_argument("--fast", type=int, default=50)
    trade.add_argument("--slow", type=int, default=200)
    trade.add_argument("--long-only", action="store_true")
    trade.add_argument("--rebalance", default=engine.WEEKLY, choices=engine.REBALANCES)
    trade.add_argument("--lag", type=int, default=1, help="bars from signal to fill")
    trade.add_argument("--roll-method", default=rollmod.CALENDAR, choices=rollmod.ROLL_METHODS)
    trade.add_argument("--adjust", default=rollmod.PANAMA, choices=rollmod.ADJUSTMENTS)
    trade.add_argument("--slippage-ticks", type=float, default=None)

    out = p.add_argument_group("output")
    out.add_argument("--compare", action="store_true",
                     help="strategy table + roll/adjustment sensitivity")
    out.add_argument("--csv", action="store_true", help="write results/ CSVs")
    out.add_argument("--trials", type=int, default=6,
                     help="honest number of configs tried, for the deflated Sharpe")
    return p.parse_args(argv)


def build_strategy(args):
    kind = args.strategy
    if kind == "tsm":
        return st.TimeSeriesMomentum(lookback=args.lookback, allow_short=not args.long_only)
    if kind == "ma":
        return st.MovingAverageCross(fast=args.fast, slow=args.slow,
                                     allow_short=not args.long_only)
    if kind == "multi":
        return st.MultiSpeedMomentum(allow_short=not args.long_only)
    if kind == "volmom":
        return st.VolAdjustedMomentum(lookback=args.lookback)
    if kind == "breakout":
        return st.Breakout(lookback=args.lookback, allow_short=not args.long_only)
    return st.Constant(1.0)


def load_markets(args):
    syms = [s.strip().upper() for s in args.markets.split(",") if s.strip()]
    start = datamod.parse_date(args.start) if args.start else None
    end = datamod.parse_date(args.end) if args.end else None
    if args.data:
        book = datamod.load_book(args.data, syms)
        rates = (datamod.load_rates(args.rates) if args.rates
                 else datamod.constant_rate(args.rate if args.rate is not None else 0.04))
        return book, rates, start, end, False
    s = start or date(2010, 1, 4)
    e = end or date(2026, 6, 30)
    book = syn.synthetic_book(syms, start=s, end=e, seed=args.seed)
    rates = (datamod.load_rates(args.rates) if args.rates else
             (datamod.constant_rate(args.rate) if args.rate is not None
              else syn.synthetic_rates(s, e)))
    return book, rates, s, e, True


def make_config(args, rates, start, end, markets=None) -> engine.BacktestConfig:
    fixed = ({m: args.fixed for m in markets} if args.fixed and markets else None)
    cfg = engine.BacktestConfig(
        start=start, end=end, initial_equity=args.equity,
        vol_target=args.vol_target, vol_span=args.vol_span, idm=args.idm,
        max_margin_to_equity=args.margin_cap, rebalance=args.rebalance,
        execution_lag=args.lag, buffer_frac=args.buffer,
        roll_method=args.roll_method, adjust=args.adjust,
        slippage_ticks=args.slippage_ticks, rates=rates,
        fixed_contracts=fixed)
    return cfg


# --- reporting --------------------------------------------------------------

def pct(x: float, nd: int = 2) -> str:
    return "n/a" if x != x else f"{100 * x:.{nd}f}%"


def print_capacity(book, cfg, args):
    """Can this account actually hold the positions the risk target implies?"""
    syms = sorted(book)
    idm = cfg.idm if cfg.idm is not None else sz.idm_for(len(syms), cfg.avg_corr)
    weight = 1.0 / len(syms)
    print(f"\nCAPACITY at ${cfg.initial_equity:,.0f} "
          f"({len(syms)} markets, {pct(cfg.vol_target)} vol target, IDM {idm:.2f})")
    print(f"  {'mkt':5s} {'price':>12s} {'ann vol':>8s} {'$risk/ct':>10s} "
          f"{'full size':>10s} {'min equity':>12s}")
    shortfall = []
    for s in syms:
        m = book[s]
        segs = rollmod.roll_schedule(m, offset_days=cfg.roll_offset_days,
                                     method=cfg.roll_method, start=cfg.start, end=cfg.end)
        adj = rollmod.continuous(segs, method=cfg.adjust)
        held = rollmod.held_contract(segs)
        ds = sorted(adj)
        vals = [adj[d] for d in ds]
        raws = [held[d].close(d) or adj[d] for d in ds]
        vol = sz.blended_vol(vals[-cfg.vol_lookback_cap:], span=cfg.vol_span,
                             basis=m.spec.vol_basis, base=raws[-cfg.vol_lookback_cap:])
        px = raws[-1]
        if vol is None:
            continue
        rpc = sz.risk_per_contract(m.spec, px, vol)
        full = sz.position_scale(cfg.initial_equity, m.spec, px, vol, weight,
                                 cfg.vol_target, idm)
        need = sz.min_equity_for_one(m.spec, px, vol, weight, cfg.vol_target, idm)
        flag = "" if full >= 0.5 else "  <- rounds to zero"
        if full < 0.5:
            shortfall.append((s, need))
        print(f"  {s:5s} {px:12,.4f} {pct(vol, 1):>8s} {rpc:10,.0f} "
              f"{full:10.2f} {need:12,.0f}{flag}")
    if shortfall:
        worst = max(n for _, n in shortfall)
        print(f"  {len(shortfall)} market(s) cannot hold one contract at this equity: "
              f"{', '.join(s for s, _ in shortfall)}")
        print(f"  -> the book trades {len(syms) - len(shortfall)}/{len(syms)} markets. "
              f"${worst:,.0f} equity (or fewer, larger-weight markets) fixes it.")


def print_rolls(res, book):
    print("\nROLLS (the assumption every long futures backtest hides)")
    for s in sorted(book):
        rows = [r for r in res.roll_report[s] if r["gap"] is not None]
        if not rows:
            continue
        gaps = [r["gap"] for r in rows]
        px = abs(rows[-1]["old_close"] or 1.0) or 1.0
        total = sum(gaps)
        print(f"  {s:5s} {len(rows):4d} rolls  mean gap {sum(gaps)/len(gaps):+10.4f}  "
              f"cumulative {total:+12.4f}  ({pct(total / px, 1)} of last price)")
    roll_cost = res.costs_by_reason.get("roll", 0.0)
    print(f"  roll cost {roll_cost:,.0f} of {res.total_costs():,.0f} total "
          f"({pct(roll_cost / res.total_costs() if res.total_costs() else 0, 0)})")


def print_summary(s, res, label=""):
    print(f"\nRESULT  {label or s['name']}   {s['start']} -> {s['end']}  "
          f"({s['years']:.1f} years)")
    rows = [
        ("CAGR", pct(s["CAGR"])), ("Vol (realised)", pct(s["Vol"])),
        ("vol vs target", f"{s['vol_realised_ratio']:.2f}x"),
        ("Sharpe (excess)", f"{s['Sharpe']:.2f}"), ("Sortino", f"{s['Sortino']:.2f}"),
        ("Max drawdown", pct(s["MaxDD"])),
        ("Drawdown length", f"{s['DD_days']} days"
                            f"{'' if s['DD_recovered'] else ' (unrecovered)'}"),
        ("Calmar", f"{s['Calmar']:.2f}"), ("Skew", f"{s['Skew']:+.2f}"),
        ("Final equity", f"${s['final_equity']:,.0f}"),
        ("Interest earned", f"${s['interest_earned']:,.0f}"),
        ("Costs", f"${s['costs']:,.0f}  (roll ${s['roll_costs']:,.0f} / "
                  f"signal ${s['signal_costs']:,.0f})"),
        ("Cost drag", f"{pct(s['cost_drag'])} of avg equity per year"),
        ("Turnover", f"{s['turnover_x_equity']:.1f}x equity/yr, "
                     f"{s['contracts_per_year']:.0f} contracts/yr"),
        ("Margin/equity", f"avg {pct(s['avg_margin_to_equity'], 1)}, "
                          f"peak {pct(s['peak_margin_to_equity'], 1)}"),
        ("Effective markets", f"{s['effective_markets']:.1f} of {s['markets']}"),
        ("Margin calls", f"{s['margin_calls']} ({s['derisk_days']} de-risk days)"),
    ]
    for k, v in rows:
        print(f"  {k:20s} {v}")
    if s["_annual"]:
        print("\n  year   return")
        for y in sorted(s["_annual"]):
            print(f"  {y}  {pct(s['_annual'][y], 1):>8s}")
    print("\n  P&L by market")
    for sym, v in sorted(res.pnl_by_market.items(), key=lambda kv: -kv[1]):
        print(f"  {sym:6s} ${v:>14,.0f}")


def print_deflated(s, trials: int):
    monthly = list(s["_monthly"].values())
    if len(monthly) < 12:
        return
    var = 0.02      # spread of monthly Sharpes across a small, similar search
    d = mt.deflated_sharpe(monthly, n_trials=max(2, trials), sharpe_variance=var)
    if d["dsr"] != d["dsr"]:
        return
    print(f"\nDEFLATED SHARPE  (Bailey & Lopez de Prado, {trials} trials declared)")
    print(f"  monthly Sharpe {d['sharpe']:.3f} vs threshold {d['threshold']:.3f} "
          f"-> P(true Sharpe > 0) = {pct(d['dsr'], 1)}")
    print("  Declare every config you tried, including the abandoned ones. "
          "Six is almost always a lie.")


def compare(book, cfg, args, rates):
    print("\nCOMPARISON  (same data, same costs — only the stated axis changes)")
    fmt = "  {:22s} {:>8s} {:>8s} {:>8s} {:>9s} {:>8s} {:>7s}"
    print(fmt.format("config", "CAGR", "vol", "Sharpe", "maxDD", "cost", "eff mkt"))
    rows = []
    variants = [
        ("tsm252", st.TimeSeriesMomentum(252)),
        ("tsm252 long-only", st.TimeSeriesMomentum(252, allow_short=False)),
        ("ma50/200", st.MovingAverageCross(50, 200)),
        ("multi 63/126/252", st.MultiSpeedMomentum()),
        ("volmom252", st.VolAdjustedMomentum(252)),
        ("breakout252", st.Breakout(252)),
        ("always long", st.Constant(1.0)),
    ]
    for label, strat in variants:
        res = engine.run(book, cfg, strat)
        s = mt.summary(res, name=label)
        rows.append((label, s))
        print(fmt.format(label, pct(s["CAGR"], 1), pct(s["Vol"], 1),
                         f"{s['Sharpe']:.2f}", pct(s["MaxDD"], 1),
                         pct(s["cost_drag"], 2), f"{s['effective_markets']:.1f}"))

    print("\n  roll / adjustment sensitivity (12-month trend held constant)")
    base = st.TimeSeriesMomentum(252)
    for rm in rollmod.ROLL_METHODS:
        for adj in (rollmod.PANAMA, rollmod.RATIO):
            c = engine.BacktestConfig(**{**cfg.__dict__, "roll_method": rm, "adjust": adj})
            s = mt.summary(engine.run(book, c, base))
            print(fmt.format(f"{rm}/{adj}", pct(s["CAGR"], 1), pct(s["Vol"], 1),
                             f"{s['Sharpe']:.2f}", pct(s["MaxDD"], 1),
                             pct(s["cost_drag"], 2), f"{s['effective_markets']:.1f}"))
    print("  A strategy whose Sharpe moves materially across these four rows is "
          "measuring the roll convention, not the market.")
    return rows


def write_csv(res, s, tag: str):
    RESULTS.mkdir(exist_ok=True)
    eq = RESULTS / f"equity_{tag}.csv"
    with eq.open("w", newline="") as fh:
        w = csvmod.writer(fh)
        w.writerow(["date", "equity", "ret", "gross_pnl", "interest", "costs",
                    "margin", "margin_to_equity", "gross_notional",
                    "markets_held", "effective_markets"])
        for r in res.records:
            w.writerow([r.date, f"{r.equity:.2f}", f"{r.ret:.8f}",
                        f"{r.gross_pnl:.2f}", f"{r.interest:.2f}", f"{r.costs:.2f}",
                        f"{r.margin:.2f}", f"{r.margin_to_equity:.4f}",
                        f"{r.gross_notional:.2f}", r.markets_held,
                        f"{r.effective_markets:.3f}"])
    tr = RESULTS / f"trades_{tag}.csv"
    with tr.open("w", newline="") as fh:
        w = csvmod.writer(fh)
        w.writerow(["date", "symbol", "contract", "contracts", "price", "cost", "reason"])
        for t in res.trades:
            w.writerow([t.date, t.symbol, t.code, t.contracts, f"{t.price:.6f}",
                        f"{t.cost:.2f}", t.reason])
    sm = RESULTS / f"summary_{tag}.csv"
    with sm.open("w", newline="") as fh:
        w = csvmod.writer(fh)
        keys = [k for k in s if not k.startswith("_")]
        w.writerow(keys)
        w.writerow([s[k] for k in keys])
    print(f"\nwrote {eq.name}, {tr.name}, {sm.name} to {RESULTS}/")


def main(argv=None) -> int:
    args = parse_args(argv)
    book, rates, start, end, is_synth = load_markets(args)
    cfg = make_config(args, rates, start, end, markets=sorted(book))
    strategy = build_strategy(args)

    print("=" * 78)
    print("FUTURES BACKTEST")
    print("=" * 78)
    print(f"  data        {'SYNTHETIC (seeded)' if is_synth else args.data}")
    print(f"  markets     {', '.join(sorted(book))}")
    print(f"  strategy    {getattr(strategy, 'label', args.strategy)}  "
          f"rebalance={cfg.rebalance} lag={cfg.execution_lag}bar")
    print(f"  mechanics   roll={cfg.roll_method} adjust={cfg.adjust} "
          f"buffer={pct(cfg.buffer_frac, 0)} margin cap={pct(cfg.max_margin_to_equity, 0)}")
    if is_synth:
        print("\n  !! SYNTHETIC DATA: trending by construction. These numbers test the")
        print("     engine, not the edge. Point --data at real contract bars before")
        print("     believing any Sharpe printed below.")

    if cfg.fixed_contracts:
        print(f"\n  FIXED SIZE MODE: {args.fixed} contract(s) per market, "
              "risk sizing bypassed.")
    else:
        print_capacity(book, cfg, args)

    res = engine.run(book, cfg, strategy)
    s = mt.summary(res, name=getattr(strategy, "label", args.strategy))
    print_rolls(res, book)
    print_summary(s, res)
    print_deflated(s, args.trials)

    if res.warnings:
        print("\nWARNINGS")
        for w in res.warnings:
            print(f"  - {w}")

    if args.compare:
        compare(book, cfg, args, rates)
    if args.csv:
        write_csv(res, s, tag=getattr(strategy, "label", args.strategy))
    return 0


if __name__ == "__main__":
    sys.exit(main())
