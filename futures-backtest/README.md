# futures-backtest

A backtesting engine for futures contracts. Pure stdlib Python — no pandas, no
numpy, no paid data required to run it. Built 2026-09-19 as the execution
counterpart to [[Micro-Futures Trend Strategy]] in the wiki.

The sibling project `sector-momentum/` backtests ETFs, where a position is a
weight and a return is a percentage. None of that works for futures, which is
why this is a separate engine rather than a flag on that one.

## Why futures need their own engine

| Equity backtest assumes | Futures reality |
|---|---|
| `weight x pct_return` | `contracts x multiplier x (settle_t - settle_t-1)` |
| fractional position sizes | whole contracts — at $100k, MES rounds to zero |
| one continuous price series | a chain of delivery months you must roll between |
| cash is spent on the position | margin is *posted*; the balance earns interest |
| leverage capped by cash | capped by margin-to-equity, ~10x higher |
| no expiry | every contract dies; rolling is a real trade with a real cost |

Get any one of these wrong and the equity curve is fiction. The roll is the
usual culprit: a back-adjusted continuous series has a fictional price level,
and a backtest that computes percentage returns off it is quietly measuring the
adjustment, not the market.

## Quick start

```bash
cd futures-backtest

python3 capacity.py --equity 100000              # start here: can the account hold it?
python3 run.py                                   # synthetic demo, 12-month trend
python3 walkforward.py                           # pick in-sample, read out-of-sample
python3 run.py --equity 300000 --compare         # strategy + roll sensitivity table
python3 run.py --markets MES,MGC --fixed 1       # long 1 contract benchmark
python3 run.py --data ./data --rates ./data/irx.csv --start 2005-01-01
python3 run.py --csv                             # writes results/
```

`--markets` defaults to the largest capacity tier the given equity can actually
hold, so a $100K run does not silently carry three permanently flat markets.
`capacity.py` prints that arithmetic on its own, from contract specs, with no
data at all — run it before buying any.

With no `--data` the run uses **seeded synthetic bars**. Those paths trend by
construction, so they prove the plumbing and nothing else. Every performance
number below the banner is meaningless until you point `--data` at real bars.

## What it does

- **Contract specs** (`contracts.py`) — multiplier, tick size, tick value,
  commission, initial/maintenance margin, roll months, per-market risk weight,
  for the CME micro universe plus the full-size contracts you graduate to.
- **Rolls** (`roll.py`) — calendar (N days before expiry) or liquidity
  (back month out-trades the front, capped by the calendar rule). Panama
  (additive), ratio (multiplicative) or unadjusted splicing, with a per-market
  report of every roll gap so the assumption is visible rather than buried.
- **Sizing** (`sizing.py`) — volatility targeting in whole contracts, EWMA vol
  blended with long-run vol, instrument diversification multiplier, a no-trade
  buffer to kill rounding churn, a margin-to-equity ceiling, and diagnostics for
  how many markets the book is *actually* risking.
- **Engine** (`engine.py`) — daily mark-to-market against the contract actually
  held, rolls as priced trades, collateral interest, commission and slippage per
  fill, a hard margin ceiling with forced de-risking, and liquidation if equity
  reaches zero.
- **Signals** (`strategies.py`) — 12-month time-series momentum, 50/200 MA
  crossover, multi-speed blend, vol-scaled momentum, breakout, plus `Constant`
  for benchmarks. All slow, on purpose.
- **Metrics** (`metrics.py`) — CAGR, vol, Sharpe (excess of the cash leg the
  book earns), Sortino, drawdown with duration, Calmar, skew, annual table, and
  the Deflated Sharpe Ratio for the multiple-testing haircut.

## Order of operations in one day

1. mark existing positions to today's settle of the contract held,
2. accrue collateral interest on yesterday's closing equity,
3. rebalance, if scheduled, from signals as of `t - execution_lag`,
4. roll any holding period that ends today, at today's settles,
5. enforce the margin ceiling; de-risk if breached,
6. record.

Signals never see the bar they trade on (`execution_lag=1` by default). The
test suite asserts this rather than trusting it.

## The invariant that matters

> Holding one contract and rolling it must earn exactly
> `multiplier x (back-adjusted price change)`, minus the cost of each fill.

That is the whole reason back-adjustment exists, and it is the first thing that
breaks when roll handling is sloppy. `tests/test_futures_engine.py` checks it to
the cent — on a hand-built single-roll fixture *and* across full 59-roll chains
(monthly crude, the yield contract, quarterly equity, FX) — along with: roll
legs priced on both contracts, both legs of a gap roll charged, interest
compounding on a flat book, integer-only positions, the margin cap holding on
every single day, forced liquidation on ruin, a day-by-day ledger
reconciliation (`equity_t == equity_t-1 + gross + interest - costs`, ruin day
included), determinism, and percent-vol computed against the tradable price
rather than the fictional adjusted level.

**The trap that survived the first pass**, and the reason the multi-roll tests
exist: `_calendar_target` originally rolled off each contract's *last quote*
rather than its expiry. Every contract still alive when a vendor download ends
is truncated at the download date, so all of them report a fake expiry there and
the chain cascades through every deferred month in the final days — ten one-day
segments, ten phantom round turns, 7% of all roll fills in the last fortnight,
and a live position whose mark was silently dropped. It only shows up on a
multi-roll chain with a truncated tail, which is to say on every real dataset.
`roll_schedule` now rolls off `expiry_date()` and refuses to roll out of a
contract that is still quoting at the data end.

```bash
make test-futures        # from the repo root, ~5 seconds, no dependencies
```

## Real data

**Full checklist: [DATA.md](DATA.md).** Two things from it that change what you
buy:

- **Capacity first.** MES needs $203K of equity to justify one contract at 1/8
  weight, MNQ $340K. Below ~$250K the 8-market book is a fiction; `capacity.py`
  gives the book that fits.
- **The micros launched in 2019**, so they cannot support a trend backtest whose
  value lives in rare years. Backtest the full-size parent, trade the micro:
  drop `ESH19.csv` into `data/MES/` and the loader uses it while keeping the
  micro's multiplier, tick and margin (`ContractSpec.history_proxy`). The one
  exception is Micro 10-Year Yield, quoted in yield where ZN is quoted in
  dollars — different instruments, never substituted.

Per-contract bars, one CSV per delivery month:

```
data/MES/MESH26.csv
data/MES/MESM26.csv

date,open,high,low,close,volume,open_interest
2026-01-02,5901.25,5930.00,5895.50,5925.75,182340,1204553
```

`volume` and `open_interest` are optional; supply them to enable liquidity-based
rolls. Norgate, Databento and CME exports all reshape into this in a few lines.
Collateral rate: any CSV with `date` and a percent-quoted yield (`^IRX` works).

`make_sample_data.py` writes that layout for you, which is the fastest way to
see the format and to check the loader against your own exports:

```bash
python3 make_sample_data.py --out ./data-demo --markets MES,MGC
python3 run.py --data ./data-demo --rates ./data-demo/irx.csv --markets MES,MGC
```

Already have a back-adjusted continuous file instead? `data.load_continuous`
wraps it, but it charges only a modelled roll cost and cannot see calendar-spread
slippage or term structure. It is for reconnaissance, not for sizing money.

## Known limitations

- **Settlement prices only.** Intraday fills, stops and gap risk inside the day
  are not modelled; a market order at the close is assumed to fill at the close
  plus the configured slippage.
- **Margin is a flat rate per contract**, not SPAN. No cross-margin credit, no
  volatility-scaled margin. Conservative, but it means margin-to-equity here
  runs higher than a real SPAN account would show.
- **FX is a constant per currency** (default 1.0). Fine for a USD-only micro
  book; wrong the moment you add a non-USD contract with a moving cross.
- **No slippage model beyond fixed ticks.** Micros have proportionally wider
  spreads than minis, and a fixed-tick assumption flatters large orders.
- **Specs are estimates.** Margins and commissions in `contracts.py` are
  plausible 2026 retail numbers, not quotes. Check them against the CME contract
  page and your broker before sizing real money.
- **Synthetic data trends by construction.** Say it twice, because the first
  Sharpe you see will come from it.

## Next

- Real bars (see [DATA.md](DATA.md)); re-run `walkforward.py` and `--compare`,
  and keep the roll-sensitivity table with the result.
- Correlation-aware IDM (the current one assumes equicorrelation).
- Carry as a second signal on the same infrastructure — futures carry is the
  natural companion to trend, and the engine already holds the term structure.
- Order generation for a paper account, once a walk-forward passes.

## Files

- `contracts.py` — contract registry and cost arithmetic
- `data.py` — per-contract bar loading, continuous-file wrapper, rate series
- `synthetic.py` — seeded synthetic bars so the engine runs with no vendor feed
- `roll.py` — roll schedules, back-adjustment, roll-gap diagnostics
- `sizing.py` — vol targeting, integer rounding, margin, diversification
- `strategies.py` — signals
- `engine.py` — the daily loop
- `metrics.py` — performance and multiple-testing statistics
- `run.py` — CLI
- `capacity.py` — can this account hold this book? (no data required)
- `walkforward.py` — in-sample pick, out-of-sample read, with a verdict
- `make_sample_data.py` — writes a sample `--data` directory in the expected layout
- `DATA.md` — the buy-reshape-run-check checklist for real bars
- `../tests/test_futures_engine.py` — the invariants, hermetic
