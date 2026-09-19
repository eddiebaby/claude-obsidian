---
type: concept
title: "Futures Backtesting Engine"
domain: quantitative-finance
complexity: advanced
created: 2026-09-19
updated: 2026-09-19
tags:
  - infrastructure
  - quantitative-finance
  - futures
  - backtesting
status: built
aliases:
  - "futures-backtest"
  - "Futures Backtester"
related:
  - "[[Micro-Futures Trend Strategy]]"
  - "[[Trend-Following]]"
  - "[[Backtest-Overfitting]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[Tick-Size-Microstructure]]"
  - "[[Sector-ETF Momentum Strategy]]"
---

# Futures Backtesting Engine

Code: `futures-backtest/` in this repo. Built 2026-09-19. Pure stdlib Python,
no vendor data required to run it, ~100 assertions in
`tests/test_futures_engine.py` (`make test-futures`, ~5 seconds).

This is the execution half of [[Micro-Futures Trend Strategy]]. That page says
what to trade; this one is the machinery that decides whether the answer is
real.

## Why an equity backtester cannot be reused

The `sector-momentum/` engine treats a position as a weight and a return as a
percentage. Every one of those assumptions breaks on futures:

| Equity assumption | Futures reality |
|---|---|
| `weight x pct_return` | `contracts x multiplier x (settle_t − settle_t−1)` |
| fractional sizes | whole contracts only |
| one price series | a chain of delivery months with rolls between them |
| cash buys the position | margin is *posted*; the balance earns interest |
| leverage capped by cash | capped by margin-to-equity, an order of magnitude higher |
| no expiry | every contract dies; the roll is a real trade with a real cost |

## The central invariant

> Holding one contract and rolling it must earn exactly
> `multiplier × (back-adjusted price change)`, minus the cost of each fill.

This is the reason back-adjustment exists, and the first thing sloppy roll
handling breaks. The engine asserts it to the cent in the test suite. Three
corollaries fall out of it:

1. **Signals come from the adjusted series; P&L comes from the contract held.**
   Mixing those is the classic futures backtest error.
2. **A back-adjusted level is fictional.** Only its differences are real. With
   persistent backwardation, panama adjustment can drive a crude series
   *negative* over twenty years — so percent returns must be computed as
   `(adjusted difference) / (unadjusted price you could actually trade)`. This
   is a real bug caught during the build, not a hypothetical: the naive version
   printed 29.0 annualised vol for MCL.
3. **The roll is a trade.** Two legs, both priced on their own contract, both
   paying commission and slippage. On a slow trend book the roll is ~75% of all
   trading cost.

## What the engine models

- **Contract specs** — multiplier, tick size and value, commission, initial and
  maintenance margin, roll months, per-market risk weight. CME micros plus
  full-size contracts. Spec numbers are plausible 2026 retail estimates and are
  meant to be replaced with broker quotes.
- **Rolls** — calendar (N days before expiry) or liquidity-based (back month
  out-trades front, capped by the calendar rule so an illiquid tape cannot push
  a roll past expiry). Panama / ratio / unadjusted splicing, with every roll gap
  reported per market.
- **Sizing** — volatility targeting in integer contracts: EWMA vol blended with
  long-run vol (short-window vol collapses in quiet tape and hands back a
  position several times too big into the next shock), instrument
  diversification multiplier, a no-trade buffer band, a margin-to-equity ceiling.
- **Accounting** — daily mark-to-market on the held contract, collateral
  interest on the balance, per-fill costs, forced de-risking at the margin
  ceiling, liquidation and a hard stop at zero equity.
- **Validation** — realised vs target vol, effective market count, cost drag
  against *average* equity, margin utilisation, Deflated Sharpe
  ([[Deflated-Sharpe-Ratio]]) for the multiple-testing haircut
  ([[Backtest-Overfitting]]).

## What it found immediately

Running the default 8-market micro book at $100,000:

- **MES and MNQ round to zero contracts.** At a 10% vol target across 8 markets,
  full size in MES is 0.12 contracts — the market is in the book on paper and
  flat in reality. The book trades 6 of 8 markets and realises ~6% vol against a
  10% target.
- This is the constraint [[Micro-Futures Trend Strategy]] flagged from theory,
  now with a number attached: the CLI prints the minimum equity at which each
  market can hold one contract. Fix it with fewer markets at larger weights, not
  by ignoring it.
- **Roll convention moves the answer.** Panama vs ratio adjustment shifted
  Sharpe 0.76 → 0.83 on identical data and costs. Any result reported without
  its roll assumption is incomplete; `run.py --compare` prints the sensitivity
  table on purpose.

## Honest limits

Settlement prices only (no intraday fills or gap modelling inside the day);
flat-rate margin rather than SPAN (conservative); constant FX per currency;
fixed-tick slippage. And the bundled synthetic data **trends by construction** —
it validates the plumbing, never the edge. Every performance number is
provisional until real contract bars are loaded.

## Next

- [ ] Load real bars (Norgate / Databento) for the 8-market micro book
- [ ] Re-run `--compare`, keep the roll-sensitivity table with the result
- [ ] Walk-forward split, mirroring `sector-momentum/walkforward.py`
- [ ] Correlation-aware IDM (the current one assumes equicorrelation)
- [ ] Carry as a second signal on the same infrastructure
