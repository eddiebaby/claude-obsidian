---
type: entity
title: "Databento"
created: 2026-07-13
updated: 2026-07-13
domain: quantitative-finance
address: c-000139
tags:
  - entity
  - data-vendor
  - market-data
  - futures
status: developing
related:
  - "[[compass2026-backtesting-engine-blueprint]]"
  - "[[Futures-Contract-Mechanics]]"
  - "[[Information-Driven-Bars]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
---

# Databento

Market-data vendor; the compass blueprint's pick for CME futures tick/MBO data in a Python-first build. Licensed CME distributor sourcing from the Aurora colo (median feed latency ~6.1 µs), dataset **GLBX.MDP3**: MBO (L3), MBP-10 (L2), BBO (L1), tick trades, and OHLCV — nanosecond timestamps, identical historical/live APIs.

## Pricing (as of report, 2026)

- Pay-as-you-go historical: ~**$26/GB** for CME trades, ~**$1/GB** for MBO (derived from documented examples, not rate card); ~5 days of ES trades ≈ $2.17. **$125 free credits** for new accounts.
- **Standard $179/mo** (rising to $199/mo for new subscribers after 2026-06-22): 15 years of futures history, live data, 1 year L1, 1 month L2/L3.
- CME license fees pass through: $32.65/mo non-pro.

## Relevance to Scott's stack

The upgrade path beyond the Schwab API (equities/futures 5m bars, ~7-8.5 months depth) when tick-level fills or MBO queue modeling become necessary — i.e., at compass Milestone 4, not before. Budget: tens of dollars for targeted trade-data pulls.
