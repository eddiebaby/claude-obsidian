---
type: source
title: "PRD Research Brief: Unified Python Backtesting Engine for CME Equity-Index Futures + US Equities"
created: 2026-09-19
updated: 2026-09-19
domain: quantitative-finance
address: c-000151
tags:
  - source
  - quantitative-finance
  - backtesting
  - data-vendors
  - futures
  - equities
  - research-report
status: ingested
source_type: research-report
source_file: ".raw/articles/compass2026-unified-backtester-prd-brief-2026-09-19.md"
author: "Claude deep-research (compass artifact)"
date_published: 2026-09
confidence: medium
key_claims:
  - "One event-driven, session-aware, bar-based core for both futures and equities; data from multiple vendors plus a dedicated point-in-time index-membership source"
  - "Schwab Trader API is a free equities price source but has hard gaps: ~48 days of 1m history, no delisted names, no point-in-time constituents, no corporate-action feed, split- but not dividend-adjusted"
  - "Cheapest turnkey survivorship fix: Norgate Platinum US Stocks (USD 630/yr) for point-in-time S&P 500 / Nasdaq-100 membership + delisted history"
  - "Databento serves raw continuous-contract prices and deliberately does NOT back-adjust; roll adjustment is the engine's responsibility"
  - "Validation (WFA, DSR, PBO, CPCV) is a first-class requirement; correctness before speed"
related:
  - "[[compass2026-backtesting-engine-blueprint]]"
  - "[[Instrument-Master]]"
  - "[[Point-in-Time-Universe]]"
  - "[[Continuous-Contract-Construction]]"
  - "[[Futures-Contract-Mechanics]]"
  - "[[Event-Driven-Backtesting]]"
  - "[[Execution-Realism]]"
  - "[[Walk-Forward-Analysis]]"
  - "[[Combinatorial-Purged-Cross-Validation]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[Backtest-Overfitting]]"
  - "[[Schwab-Trader-API]]"
  - "[[Databento]]"
  - "[[Norgate-Data]]"
  - "[[EODHD]]"
  - "[[DuckDB]]"
  - "[[Zipline-Reloaded]]"
  - "[[NautilusTrader]]"
  - "[[vectorbt]]"
  - "[[LEAN-QuantConnect]]"
---

# Compass 2026 — Unified Backtester PRD Brief (Futures + Equities)

Second compass deep-research artifact on backtesting, written as a PRD input. It follows [[compass2026-backtesting-engine-blueprint]] (2026-07-13). The architecture mostly matches that blueprint. What's new here is **data sourcing**: what Schwab can and can't supply, which vendor fills each gap, and how to run equities and futures through one engine.

## What's new vs the July blueprint

| Topic | New content |
|---|---|
| Schwab as a data source | Endpoint limits, 7-day refresh-token wall, split-only adjustment, no constituents or corporate actions → [[Schwab-Trader-API]] |
| Survivorship bias | Point-in-time S&P 500 / NDX membership and delisted names as a *separate required data layer* → [[Point-in-Time-Universe]] |
| Vendor map | [[Norgate-Data]] (USD 630/yr Platinum), [[EODHD]] (constituents from 2012, S&P 500 only), Databento US Equities ($199/mo) and Corporate Actions ($299/mo) → [[Databento]] |
| Unifying asset classes | One instrument table, dual session calendars, margin and cash accounting in one blotter → [[Instrument-Master]] |
| Databento continuous symbology | `c`/`n`/`v` roll rules, `.0/.1` depth ranks, **raw prices only, no back-adjustment** → [[Continuous-Contract-Construction]] |
| Execution costs | Schwab equities $0; Schwab futures **$2.25/contract/side** + exchange/reg fees |
| Engine references | Adds [[Zipline-Reloaded]] (Pipeline API, calendars) and Backtrader (lifecycle hooks `next()`/`notify_order()`/`notify_trade()`; maintenance slowing, so copy its patterns rather than depend on it) |

## Phased plan (from the brief)

0. Data foundation: unified bar + instrument schema, instrument master, session calendars, Parquet + [[DuckDB]] store.
1. Futures correctness: configurable roll + back/ratio adjustment, ES/MES/NQ/MNQ specs, RTH/ETH, margin; hand-checked trades.
2. Equities: deep Schwab daily + forward intraday archive; Norgate/EODHD point-in-time universe, delisted names, splits/dividends.
3. Unified event-driven core: multi-asset accounting, order/fill/slippage/commission, look-ahead guards.
4. Validation harness: [[Walk-Forward-Analysis]], [[Combinatorial-Purged-Cross-Validation]], [[Deflated-Sharpe-Ratio]], PBO ([[Backtest-Overfitting]]), reproducibility (snapshots, seeds, run logs).
5. (Out of scope) broker-adapter seam for paper/live, [[NautilusTrader]]-style parity.

**Plan-changing thresholds:** if intraday equities become the primary strategy type, switch to Databento US Equities. If the universe grows past SPX/NDX, reassess constituents (Norgate already covers Russell and S&P 400/600). If you go live, the broker seam becomes its own phase.

## Contradictions with the vault's empirical record

> [!contradiction] Schwab futures price history, contradicted by [[Schwab-Trader-API]] usage in `trading/scalppulse/`
> The brief (citing the schwab-py docstring) says Schwab "does not provide price history for options, futures, or any other instruments." **The vault's own code did pull it.** `scalppulse/schwab_data.py::fetch_futures` returned `/MES` 5-minute bars from 2025-12-16 to 2026-07-10 (`MES_5m_365d_schwab.csv`, ~7 months), and `propfirm/data/` holds `MES/MNQ_5m_schwab_deep.csv`. The docstring is stale, or the claim covers only some symbols. What's still true: the history is *shallow*, so Databento is still needed for multi-year futures work.

> [!contradiction] Futures commission in `trading/propfirm/futures_costs.py`
> The brief gives Schwab futures at **$2.25/contract/side** plus exchange and regulatory fees. `futures_costs.py` models /MES and /MNQ at **$0.66/side**, labelled "Schwab/TOS retail rate (conservative)". If execution happens at Schwab, that label is wrong and the model understates costs about 3.4x on micros. It doesn't matter for prop-firm (Tradovate/Rithmic) rates. Check the actual fee schedule of whichever broker executes.

> [!contradiction] Margins and RTH, contradicted by [[Futures-Contract-Mechanics]]
> The brief: ES margin ≈ $13,200 / $12,000 and RTH ≈ 9:30–4:00 ET. The existing page: $12,320 / $11,200 (Nov-2025 snapshot) and CME RTH 8:30 AM–3:15 PM CT (= 9:30–4:15 ET). The margin gap is normal drift over time. For RTH, keep the CME definition, which includes the 4:00–4:15 ET futures-only window.

## Caveats (from the brief)

Schwab history depths are community-observed, not documented. Vendor pricing changes often. EODHD point-in-time data is only reliable from April 2012 and is weak for NDX. All figures are as of September 2026.
