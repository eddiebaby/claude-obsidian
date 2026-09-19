#!/usr/bin/env python3
"""Write a sample data directory in the layout `run.py --data` expects.

Two uses: it documents the real-data file format by producing it, and it
exercises the CSV loader end to end (the synthetic-object path and the
load-from-disk path are different code).

    python3 make_sample_data.py --out ./data-demo
    python3 run.py --data ./data-demo --rates ./data-demo/irx.csv --markets MES,MGC

The bars are seeded synthetic ones, so they trend by construction. Replace the
files with real vendor exports in the same layout and nothing else changes.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

import contracts as cx
import data as datamod
import synthetic as syn


def write_market(md: datamod.MarketData, root: Path) -> int:
    out = root / md.symbol
    out.mkdir(parents=True, exist_ok=True)
    for c in md.contracts:
        with (out / f"{c.code}.csv").open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["date", "open", "high", "low", "close", "volume", "open_interest"])
            for d in c.dates:
                b = c.bars[d]
                w.writerow([d, b.open, b.high, b.low, b.close,
                            int(b.volume), int(b.open_interest)])
    return len(md.contracts)


def write_rates(rates: datamod.RateSeries, path: Path, every: int = 21) -> int:
    """Percent-quoted short rate, monthly-ish samples (the engine carries forward)."""
    days = sorted(rates.rates)[::every]
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "close"])
        for d in days:
            w.writerow([d, round(rates.rates[d] * 100, 3)])
    return len(days)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default="./data-demo")
    p.add_argument("--markets", default=",".join(cx.MICRO_UNIVERSE))
    p.add_argument("--start", default="2010-01-04")
    p.add_argument("--end", default="2026-06-30")
    p.add_argument("--seed", type=int, default=20260919)
    args = p.parse_args(argv)

    start, end = datamod.parse_date(args.start), datamod.parse_date(args.end)
    syms = tuple(s.strip().upper() for s in args.markets.split(",") if s.strip())
    root = Path(args.out)

    book = syn.synthetic_book(syms, start=start, end=end, seed=args.seed)
    files = sum(write_market(md, root) for md in book.values())
    n = write_rates(syn.synthetic_rates(start, end, seed=args.seed), root / "irx.csv")

    print(f"wrote {files} contract files across {len(book)} markets to {root}/")
    print(f"wrote {n} collateral-rate rows to {root / 'irx.csv'}")
    print(f"\nnow: python3 run.py --data {root} --rates {root / 'irx.csv'} "
          f"--markets {','.join(syms)}")
    print("SYNTHETIC BARS — trending by construction. Swap in real exports before "
          "believing a Sharpe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
