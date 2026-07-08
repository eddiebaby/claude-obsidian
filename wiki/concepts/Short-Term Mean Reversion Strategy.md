---
type: concept
title: "Short-Term Mean Reversion Strategy"
domain: quantitative-finance
complexity: intermediate
created: 2026-07-05
updated: 2026-07-05
tags:
  - strategy
  - quantitative-finance
  - equity
  - swing
status: seed
aliases:
  - "Mean Reversion Build"
  - "RSI-2 Strategy"
related:
  - "[[Retail Alpha Strategy Roadmap]]"
  - "[[Sector-ETF Momentum Strategy]]"
  - "[[Turnover-Regularization]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[Tick-Size-Microstructure]]"
sources: []
---

# Short-Term Mean Reversion Strategy

Build guide. Liquidity provision in liquid US equities over 1-5 day horizons.

## Thesis

Sharp short-term selloffs in fundamentally healthy, liquid stocks overshoot because sellers demand immediacy (margin calls, stop runs, index flows) and buyers are slow. Supplying that liquidity earns a spread. This is genuine alpha, and it dies above roughly $1-5M deployed because fills at size move the price you are fading. That capacity ceiling is why it is a retail edge.

## Universe

Current S&P 500 members, or Russell 1000 filtered to price > $10 and 20-day average dollar volume > $20M. Survivorship-bias-free membership history is mandatory for the backtest (delisted losers are exactly what this strategy buys).

## Signal Construction

**Baseline (Connors-style, long-only):**
1. Regime filter: stock above its 200-day SMA (only fade dips in uptrends; fading downtrends is how mean reversion accounts die).
2. Entry trigger: RSI(2) < 10, or close at a 5-day low with a 3%+ two-day decline.
3. Rank all triggers by severity (lowest RSI / deepest z-score of 5-day return); take the top 5-10 names, equal risk weight.
4. Exit: close above yesterday's high, RSI(2) > 65, or time stop at 5 trading days, whichever first.
5. Portfolio cap: max 20% of equity per name, max 100% gross. No leverage in v1.

**Optional short side** (only after the long side is proven live): mirror logic below the 200-day SMA, half size. Shorts add borrow costs, squeeze risk, and crash-up exposure; the long side carries most of the documented edge.

## Data Required

| Data | Source | Cost |
|---|---|---|
| Daily OHLCV + adjusted, with delistings | Norgate Data (Platinum) or Sharadar SEP | ~$30-40/mo |
| Index membership history | Norgate / Sharadar tickers table | Included |

Do not build this on free Yahoo-style data: no delistings means the backtest is fiction.

## Backtest Plan

1. Sample: 2005-present. Must include Oct 2008, Aug 2011, Aug 2015, Feb 2018, Mar 2020 (the strategy's character shows only in crash months).
2. Costs: this is a high-turnover strategy, so cost modeling decides everything ([[Turnover-Regularization]] logic applies with full force). Model 5 bps slippage + half-spread per side; stress at 2x.
3. Execution assumption honesty: signals computed at close, fills at next open (not same-day close, which is lookahead).
4. Benchmarks: SPY buy-and-hold; time-in-market-adjusted return (the strategy is often flat, so compare on return-per-exposure too).
5. Walk-forward parameter selection; report [[Deflated-Sharpe-Ratio]].

## Execution

- Limit orders into weakness at or below prior close beat market-on-open fills materially for this strategy; model both, trade the one you backtested.
- IBKR API or Alpaca for automation. Daily bar granularity is sufficient; no intraday infrastructure needed in v1.

## Risks & Failure Modes

- **Knife-catching**: the entry is literally buying decline. The 200-day filter and per-name cap are the defenses; the time stop prevents bag-holding.
- **Crash clustering**: all signals fire at once in a market break, exactly when correlation goes to 1. Gross exposure cap is the control.
- **Edge decay**: this family is well-known; expect thinner spreads than the 2000s literature. If the backtest edge post-2018 is materially weaker than pre-2010, size expectations to the recent period.
- **Earnings gaps**: exclude names reporting within the holding window; an earnings gap is not the overreaction being harvested.

## Kill Criteria

- Rolling 2-year net Sharpe < 0: stop trading, keep researching.
- Live slippage > 2x modeled for 20 consecutive trades: halt, fix execution before resuming.

## Expansion Hooks

- Cross-sectional z-score ranking instead of fixed RSI thresholds (turns it into a rankable signal, consistent with the rank-don't-forecast rule).
- Intraday entry timing (last-hour entries) once daily version is live.
- Pair with [[Post-Earnings Announcement Drift Strategy]]: same data layer, opposite holding-period profile.

## Status

- [ ] Hypothesis formed (documented here)
- [ ] Backtested
- [ ] Paper traded
- [ ] Live (small size)
- [ ] Scaled
