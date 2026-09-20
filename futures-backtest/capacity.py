#!/usr/bin/env python3
"""Can this account run this strategy? Arithmetic, before you buy any data.

    python3 capacity.py                    # the ladder, $25K to $1M
    python3 capacity.py --equity 100000    # one account, market by market
    python3 capacity.py --equity 100000 --vol-target 0.15

Reads `contracts.REFERENCE_MARKET` (plausible 2026 prices and vols), never a
data file. The answer is driven by contract size, not by any strategy: a market
whose full-conviction position is under half a contract is permanently flat no
matter how good the signal is, and a book "holding 8 markets" that is really
holding 5 has neither the risk nor the diversification it claims.

Refresh the reference prices in contracts.py from a quote screen before trusting
a marginal call; nothing else in the engine reads them.
"""
from __future__ import annotations

import argparse

import contracts as cx
import sizing as sz

LADDER = (25_000, 50_000, 100_000, 150_000, 250_000, 500_000, 1_000_000)


def tier_name(syms: tuple) -> str:
    for name, tier in (("micro-8", cx.MICRO_UNIVERSE), ("retail-6", cx.RETAIL_UNIVERSE),
                       ("core-5", cx.CORE_UNIVERSE), ("starter-4", cx.STARTER_UNIVERSE)):
        if tuple(tier) == tuple(syms):
            return name
    return f"{len(syms)} markets"


def detail(equity: float, syms: tuple, vol_target: float, avg_corr: float) -> None:
    idm = sz.idm_for(len(syms), avg_corr)
    weight = 1.0 / len(syms)
    print(f"\n  {'mkt':5s} {'price':>11s} {'vol':>6s} {'$risk/ct':>10s} "
          f"{'full size':>10s} {'rounds to':>10s} {'min equity':>12s}")
    risk_sum = 0.0
    for sym in syms:
        px, vol = cx.REFERENCE_MARKET[sym]
        spec = cx.get(sym)
        rpc = sz.risk_per_contract(spec, px, vol)
        full = sz.position_scale(equity, spec, px, vol, weight, vol_target, idm)
        need = sz.min_equity_for_one(spec, px, vol, weight, vol_target, idm)
        held = round(full)
        risk_sum += (held * rpc) ** 2
        flag = "" if full >= 0.5 else "  <- flat"
        print(f"  {sym:5s} {px:11,.4f} {100*vol:5.1f}% {rpc:10,.0f} {full:10.2f} "
              f"{held:10d} {need:12,.0f}{flag}")
    # Rough portfolio vol under equicorrelation, positions rounded to integers.
    n = max(1, sum(1 for s in syms
                   if round(sz.position_scale(equity, cx.get(s), *cx.REFERENCE_MARKET[s],
                                              weight, vol_target, idm))))
    approx = (risk_sum * (1 + avg_corr * (n - 1))) ** 0.5 / equity
    print(f"\n  IDM {idm:.2f}, risk weight {weight:.3f} each")
    print(f"  approx realised vol after integer rounding: {100*approx:.1f}% "
          f"vs {100*vol_target:.1f}% target ({approx/vol_target:.2f}x)")
    if approx < vol_target * 0.85:
        print("  -> under-risked: the rounding is eating the target. Fewer markets, "
              "larger weights.")
    elif approx > vol_target * 1.15:
        print("  -> over-risked: rounding up is levering you past the target.")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--equity", type=float, default=None)
    p.add_argument("--vol-target", type=float, default=0.10)
    p.add_argument("--avg-corr", type=float, default=0.15)
    p.add_argument("--markets", default=None, help="force a specific book")
    args = p.parse_args(argv)

    print("=" * 74)
    print(f"CAPACITY  (vol target {100*args.vol_target:.0f}%, "
          f"assumed average correlation {args.avg_corr:.2f})")
    print("=" * 74)

    if args.equity is None:
        print(f"\n  {'equity':>10s}  {'book':10s} markets")
        for eq in LADDER:
            syms, _ = sz.universe_for(eq, args.vol_target, args.avg_corr)
            print(f"  {eq:>10,}  {tier_name(syms):10s} {', '.join(syms)}")
        print("\n  Run with --equity to see the per-market arithmetic and what the "
              "next tier costs.")
        return 0

    if args.markets:
        syms = tuple(s.strip().upper() for s in args.markets.split(",") if s.strip())
        notes = []
    else:
        syms, notes = sz.universe_for(args.equity, args.vol_target, args.avg_corr)
    print(f"\n  ${args.equity:,.0f} -> {tier_name(syms)}: {', '.join(syms)}")
    for n in notes:
        print(f"    rejected {n}")
    detail(args.equity, syms, args.vol_target, args.avg_corr)

    # What does the next tier up cost?
    order = list(cx.CAPACITY_TIERS)
    if tuple(syms) in [tuple(t) for t in order]:
        idx = [tuple(t) for t in order].index(tuple(syms))
        if idx > 0:
            nxt = order[idx - 1]
            idm = sz.idm_for(len(nxt), args.avg_corr)
            w = 1.0 / len(nxt)
            need = max(sz.min_equity_for_one(cx.get(s), *cx.REFERENCE_MARKET[s], w,
                                             args.vol_target, idm) for s in nxt)
            print(f"\n  next tier up ({tier_name(nxt)}: {', '.join(nxt)}) needs "
                  f"${need * 0.5:,.0f} to round in, ${need:,.0f} to hold cleanly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
