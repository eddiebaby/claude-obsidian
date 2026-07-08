---
type: concept
title: "Micro-Futures Trend Strategy"
domain: quantitative-finance
complexity: intermediate
created: 2026-07-05
updated: 2026-07-05
tags:
  - strategy
  - quantitative-finance
  - futures
  - position
status: seed
aliases:
  - "Micro Futures Trend Following"
  - "Diversified Trend Build"
related:
  - "[[Retail Alpha Strategy Roadmap]]"
  - "[[Trend-Following]]"
  - "[[Tick-Size-Microstructure]]"
  - "[[Turnover-Regularization]]"
  - "[[Volatility Risk Premium Strategy]]"
sources:
  - "[[kurth2026-trend-following-demise]]"
  - "[[pollok2026-end-to-end-portfolio-policies]]"
---

# Micro-Futures Trend Strategy

Build guide. Slow, diversified time-series momentum on CME micro contracts. The crisis-alpha sleeve.

## Thesis

Trend following on futures is the best-documented systematic strategy in existence (100+ years of evidence across asset classes), driven by behavioral underreaction and hedging flows. It pays little in calm equity bull markets and pays big in sustained dislocations (2008, 2020, 2022), which is exactly when the equity sleeves bleed. Micro contracts (1/10th standard size) made proper multi-asset diversification possible under $100K, which was impossible at retail scale a decade ago.

**Critical design constraint from [[kurth2026-trend-following-demise]]**: fast trend (days-weeks) is dead post-2009 on small-tick, dense-order-book contracts; slow trend (months) and large volatility-normalized-tick contracts survive. Build slow only. This also keeps turnover, therefore costs, low ([[Turnover-Regularization]]).

## Universe

Start with 8-10 micros across asset classes, expand later:

| Contract | Asset | Class |
|---|---|---|
| MES | S&P 500 | Equity |
| MNQ | Nasdaq 100 | Equity |
| M2K | Russell 2000 | Equity |
| MGC | Gold | Metal |
| SIL | Silver (micro) | Metal |
| MCL | WTI Crude | Energy |
| M6E | EUR/USD | FX |
| M6B | GBP/USD | FX |
| MBT | Bitcoin | Crypto |
| 10Y Micro Yield | 10Y Treasury yield | Rates |

Diversification across classes IS the strategy; equity-only trend is just slow beta timing.

## Signal Construction

**Baseline (slow, boring, robust):**
1. Signal: sign of the 12-month return (or 50/200-day MA cross; they are near-equivalent, pick one and do not optimize between them).
2. Direction: long if positive, short if negative, every market, always in (or flat-instead-of-short variant for a long-bias version; test both, expect similar).
3. Update weekly. Slow signals + weekly updates keep annual turnover per market in low single digits.

**Sizing (where all the engineering lives):**
1. Vol-target each position: position notional = (target vol per market) / (realized 60-day vol of that market). Equal risk per market, e.g. each market sized to contribute ~2% annualized portfolio vol.
2. Portfolio target: 10-12% annualized vol to start.
3. Micro contract sizes are the constraint: at small equity, round-down to whole contracts will leave some markets at zero. Minimum viable account for 8 markets at 10% vol is roughly $25-50K; below that, trade fewer markets, not bigger sizes.

## Data Required

| Data | Source | Cost |
|---|---|---|
| Daily continuous futures (back-adjusted), 20+ yrs | Norgate Data (Futures) | ~$40/mo |
| Alternative historical | Databento (pay-per-use) | cheap at daily granularity |
| Live daily closes | Broker (IBKR) | free |

Backtest on back-adjusted continuous contracts with the roll method documented; roll assumptions change slow-trend results less than fast, but document them anyway.

## Backtest Plan

1. Sample: 2000-present minimum; longer if data allows (the strategy's value is in the rare years).
2. Costs: 1-2 ticks per side per roll and per signal flip; micros have proportionally wider spreads than minis, which slow signals mostly neutralize.
3. Benchmarks: SG Trend Index correlation (should be > 0.5 if the implementation is faithful), and the 60/40 portfolio with and without a 20% trend allocation (the honest use case).
4. Expect standalone net Sharpe 0.4-0.7 with multi-year flat stretches. If the backtest shows more, look for the bug before celebrating.

## Execution

- Weekly order batch, market orders near the close are fine at micro size on these contracts.
- Rolls: calendar-based (5 days before first notice / expiry), automated. Roll discipline is the main operational task.
- IBKR margin for a vol-targeted micro book is modest; monitor margin-to-equity < 25%.

## Risks & Failure Modes

- **Multi-year drawdowns in choppy regimes** (2011-2019 was brutal for trend). This sleeve is held for the crisis years; abandoning it in year 3 of chop right before the payoff year is the classic retail failure, and the reason the sizing must be comfortable enough to hold.
- **Whipsaw at signal boundaries**: slow signals minimize but do not eliminate it; the weekly (not daily) update cadence helps.
- **Crypto/rates regime dependence**: MBT trend history is short; size it half-weight.
- **Position rounding at small equity**: silently concentrates risk in fewer markets; monitor effective diversification, not intended.

## Kill Criteria

- Implementation correlation to SG Trend Index < 0.3 over 12 months: the build is wrong, fix before judging the strategy.
- This sleeve is NOT killed on standalone drawdown (drawdowns are its cost of carry); it is killed only if 5-year net Sharpe < 0 while the SG Trend Index is positive (implementation failure, not strategy failure).

## Expansion Hooks

- Add markets as equity grows (grains via micro ags when liquid, more FX, VX).
- Multi-speed ensemble (blend 3, 6, 12-month lookbacks) once single-speed is live.
- Carry signal as a second sleeve on the same infrastructure (futures carry is the natural companion to trend).
- [[pollok2026-end-to-end-portfolio-policies]] end-to-end weights as a research comparison, not a replacement: the paper's own result is that simple rules tie it.

## Status

- [ ] Hypothesis formed (documented here)
- [ ] Backtested
- [ ] Paper traded
- [ ] Live (small size)
- [ ] Scaled
