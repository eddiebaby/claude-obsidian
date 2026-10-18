---
type: entity
title: "Databento"
created: 2026-07-13
updated: 2026-09-19
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
  - "[[compass2026-unified-backtester-prd-brief]]"
---

# Databento

Market-data vendor; the compass blueprint's pick for CME futures tick/MBO data in a Python-first build. Licensed CME distributor sourcing from the Aurora colo (median feed latency ~6.1 µs), dataset **GLBX.MDP3**: MBO (L3), MBP-10 (L2), BBO (L1), tick trades, and OHLCV — nanosecond timestamps, identical historical/live APIs.

## Pricing (as of report, 2026)

- Pay-as-you-go historical: ~**$26/GB** for CME trades, ~**$1/GB** for MBO (derived from documented examples, not rate card); ~5 days of ES trades ≈ $2.17. **$125 free credits** for new accounts.
- **Standard $179/mo** (rising to $199/mo for new subscribers after 2026-06-22): 15 years of futures history, live data, 1 year L1, 1 month L2/L3.
- CME license fees pass through: $32.65/mo non-pro.

## Continuous symbology (from [[compass2026-unified-backtester-prd-brief]])

- Roll rules: calendar `c`, open-interest `n`, volume `v`; depth rank `.0`, `.1`, … (e.g. `ES.c.0`, `NQ.v.0`).
- **Raw prices only: no back- or ratio-adjustment, by design.** Databento's reasons: adjustments are opaque, they distort features, you can't actually hold a position through a roll, and no single rule fits everyone. Its rolls also don't match CME's published equity-index roll dates. Adjustment is the engine's job; see [[Continuous-Contract-Construction]].
- GLBX.MDP3 history starts **2010-06-06**. Pre-2017-05-21 data comes from the legacy FIX/FAST feed (MBP-10 max), which is fine for OHLCV.

## Equities & reference data

- **US Equities Standard $199/mo**: full OHLCV-1s/-1m history (~7 yrs usable), L1 ~12 mo, L2/L3 ~1 mo. Same symbology and client as futures, so it gives a genuinely unified pipeline. Mini and Basic plans only start in 2023.
- **Corporate Actions** from $299/mo (6 yrs PIT, 60+ event types). **Adjustment Factors** from $225/mo. **Security Master** 18 yrs PIT. For a solo researcher, [[Norgate-Data]] is far cheaper for the survivorship/adjustment layer.

## Relevance to Scott's stack

The upgrade path beyond the Schwab API (equities/futures 5m bars, ~7-8.5 months depth) when tick-level fills or MBO queue modeling become necessary — i.e., at compass Milestone 4, not before. Budget: tens of dollars for targeted trade-data pulls.

**Update 2026-09-18:** `trading/propfirm/pull_databento.py` now exists. It pulls `ES/NQ.v.0` ohlcv-1m, resamples to 5m in the Schwab CSV format, has a `--quote` cost check, and refuses above `--max-usd` (default $60). It's waiting on an API key to run the pre-2023 NQ validation for [[Gamma Closing Reversal Strategy]].
