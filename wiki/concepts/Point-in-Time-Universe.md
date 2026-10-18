---
type: concept
title: "Point-in-Time Universe"
created: 2026-09-19
updated: 2026-09-19
domain: quantitative-finance
address: c-000157
tags:
  - concept
  - backtesting
  - survivorship-bias
  - data-engineering
status: developing
aliases: [survivorship bias, point-in-time constituents, survivorship-free universe]
related:
  - "[[Backtest-Overfitting]]"
  - "[[Norgate-Data]]"
  - "[[EODHD]]"
  - "[[Schwab-Trader-API]]"
  - "[[Instrument-Master]]"
  - "[[Post-Earnings Announcement Drift Strategy]]"
  - "[[Index Rebalance and Event-Driven Strategy]]"
sources:
  - "[[compass2026-unified-backtester-prd-brief]]"
---

# Point-in-Time Universe

An equity backtest has to trade the universe **as it existed on each historical date**: the S&P 500 members *then*, including names that later got delisted, acquired, or went bankrupt. Using today's constituent list silently removes the losers and inflates returns. That's survivorship bias. Look-ahead bias is its twin, e.g. applying a later symbol change or a dividend adjustment computed from the future.

## What the data layer needs

| Need | Free source? | Paid fix |
|---|---|---|
| Historical index membership | Wikipedia revision scraping, ETF holdings (teddykoker, riazarbi repos), `n100tickers` (NDX from Jan 2020). Incomplete. | [[Norgate-Data]] Platinum; [[EODHD]] (S&P 500 from 2012) |
| Delisted price history | Largely absent (Schwab, Yahoo) | Norgate; Databento US Equities |
| Splits/dividends/symbol changes | Schwab is split-adjusted only | Norgate bundled; Databento Corporate Actions ($299/mo) |

## Rules

- Keep **raw** prices for fills and **adjusted** prices for signals. This is the same dual-series idea as [[Continuous-Contract-Construction]] in futures.
- The universe for date *t* is a query against membership intervals, not a static list. Store listing, delisting, and symbol-change dates in the [[Instrument-Master]].
- **Doesn't apply to:** a fixed ETF or futures universe ([[Sector-ETF Momentum Strategy]]; the ES/NQ work). It becomes mandatory as soon as a strategy selects single stocks cross-sectionally.
