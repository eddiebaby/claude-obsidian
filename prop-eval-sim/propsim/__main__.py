"""CLI: python -m propsim --preset lucidflex50k --bars oos_paths.csv --sizes 1,2,3,4"""
from __future__ import annotations

import argparse
import sys
from dataclasses import replace

from .engine import Controls
from .montecarlo import sweep, to_markdown
from .paths import eod_only, load_bar_csv, load_daily_csv, synthetic_days
from .rules import DRAWDOWN_MODES, PRESETS


def _num(s: str) -> float:
    return float(s.replace("$", "").replace(",", ""))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="propsim", description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--bars", help="bar-level CSV: date,pnl (cumulative per-unit MTM P&L, net of costs)")
    src.add_argument("--daily", help="daily CSV: date,pnl[,mae,mfe,mfe_first]")
    src.add_argument(
        "--synthetic",
        metavar="MEAN:SD[:BARS[:TRADE_FRAC]]",
        help="Gaussian days, $ per trade per unit, e.g. 9.5:250:30:0.44",
    )
    ap.add_argument("--preset", default="lucidflex50k", choices=sorted(PRESETS))
    ap.add_argument("--drawdown-mode", choices=DRAWDOWN_MODES, help="override the preset's drawdown mode")
    ap.add_argument("--fee", type=_num, help="override the evaluation fee")
    ap.add_argument("--fee-period", type=int, help="charge the fee every N trading days (monthly ~21)")
    ap.add_argument("--sizes", default="1,2,3,4", help="comma-separated position sizes (units)")
    ap.add_argument("--sims", type=int, default=2000)
    ap.add_argument("--horizon", type=int, default=252, help="trading days per campaign")
    ap.add_argument("--attempts", type=int, default=5, help="max evaluations bought per campaign")
    ap.add_argument("--block", type=float, default=10.0, help="mean bootstrap block length (days)")
    ap.add_argument("--daily-stop", type=_num, help="trader daily stop, dollars")
    ap.add_argument("--profit-cap", type=_num, help="trader daily profit cap in the evaluation, dollars")
    ap.add_argument("--funded-profit-cap", type=_num, help="daily profit cap in the funded account")
    ap.add_argument("--stop-slippage", type=_num, default=0.0, help="$ per unit lost beyond a stop")
    ap.add_argument("--eod-only", action="store_true", help="discard intraday path (shows the optimistic bias)")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)

    if a.bars:
        bank = load_bar_csv(a.bars)
    elif a.daily:
        bank = load_daily_csv(a.daily)
    else:
        try:
            parts = [float(x) for x in a.synthetic.split(":")]
        except ValueError:
            ap.error("--synthetic expects numbers: MEAN:SD[:BARS[:TRADE_FRAC]]")
        if not 2 <= len(parts) <= 4:
            ap.error("--synthetic expects MEAN:SD[:BARS[:TRADE_FRAC]] (negative MEAN: --synthetic=-3:125)")
        mean, sd = parts[0], parts[1]
        bars = int(parts[2]) if len(parts) > 2 else 30
        frac = parts[3] if len(parts) > 3 else 1.0
        bank = synthetic_days(2520, mean, sd, bars=bars, trade_frac=frac, seed=a.seed)
    if a.eod_only:
        bank = eod_only(bank)
    if not bank:
        print("no days loaded", file=sys.stderr)
        return 1

    firm = PRESETS[a.preset]
    if a.drawdown_mode:
        firm = firm.with_drawdown_mode(a.drawdown_mode)
    if a.fee is not None or a.fee_period is not None:
        ev = firm.eval
        ev = replace(
            ev,
            fee=ev.fee if a.fee is None else a.fee,
            fee_period_days=ev.fee_period_days if a.fee_period is None else a.fee_period,
        )
        firm = replace(firm, eval=ev)
    sizes = [float(s) for s in a.sizes.split(",")]
    if firm.max_contracts is not None and max(sizes) > firm.max_contracts:
        ap.error(f"size {max(sizes):g} exceeds {firm.name} contract cap of {firm.max_contracts}")
    common = dict(stop_slippage=a.stop_slippage, daily_stop=a.daily_stop)
    rows = sweep(
        bank,
        firm,
        sizes,
        sims=a.sims,
        seed=a.seed,
        horizon_days=a.horizon,
        max_attempts=a.attempts,
        block=a.block,
        eval_ctl=Controls(daily_profit_cap=a.profit_cap, **common),
        funded_ctl=Controls(daily_profit_cap=a.funded_profit_cap, **common),
    )
    traded = sum(d.traded for d in bank)
    print(f"{firm.name} | {len(bank)} days in bank ({traded} traded) | {a.sims} sims x {a.horizon} days | "
          f"max {a.attempts} attempts\n")
    print(to_markdown(rows))
    if firm.notes:
        print(f"\nRules: {firm.notes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
