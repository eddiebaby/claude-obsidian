---
type: source
title: "Building a Professional-Grade Backtesting Engine for Stocks and Futures in Python: An Architectural Blueprint"
created: 2026-07-13
updated: 2026-07-13
domain: quantitative-finance
address: c-000137
tags:
  - source
  - quantitative-finance
  - backtesting
  - futures
  - architecture
  - research-report
status: ingested
source_type: research-report
author: "Claude deep-research (compass artifact)"
date_published: 2026
confidence: medium-high
key_claims:
  - "Build ONE event-driven core (Python, Numba hot paths, Rust later only if profiling demands) plus a thin vectorized fast-path for research triage — never two permanent engines. Reference architecture: NautilusTrader; minimal skeleton: QuantStart's six-component event loop"
  - "Futures mechanics must be first-class from day one: Instrument object carrying tick size, point value, margin, session calendar, roll rules; keep unadjusted per-contract series for P&L and back-adjusted continuous series for signals — never one series for both"
  - "Source tick/MBO data from Databento (GLBX.MDP3, ~$26/GB trades, $179/mo Standard), store in Parquet + DuckDB, validate every strategy with walk-forward + CPCV + Deflated Sharpe Ratio"
  - "Realistic fills, per-contract costs (~$2.50-3.50 exchange+NFA per round turn plus commission), and honest slippage/queue modeling matter more than any indicator"
related:
  - "[[Event-Driven-Backtesting]]"
  - "[[Continuous-Contract-Construction]]"
  - "[[Futures-Contract-Mechanics]]"
  - "[[Execution-Realism]]"
  - "[[Walk-Forward-Analysis]]"
  - "[[Combinatorial-Purged-Cross-Validation]]"
  - "[[Information-Driven-Bars]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[NautilusTrader]]"
  - "[[Databento]]"
  - "[[QuantStart]]"
  - "[[LEAN-QuantConnect]]"
  - "[[vectorbt]]"
  - "[[HftBacktest]]"
  - "[[Marcos Lopez de Prado]]"
  - "[[Micro-Futures Trend Strategy]]"
  - "[[LucidFlex Automated Scalping PRD]]"
---

# Compass 2026 — Backtesting Engine Architectural Blueprint

Deep-research report on how to build a professional-grade Python backtesting engine for stocks and CME futures. The direct blueprint for graduating the scalppulse research rig (`trading/scalppulse/`, built 2026-07-12) into a real engine.

## Core architectural decisions

1. **One event-driven core, not two engines.** [[Event-Driven-Backtesting|Six-component event loop]] (DataHandler → Strategy → Portfolio → ExecutionHandler over an Event queue). The same engine runs backtest and live — "research-to-live parity" ([[NautilusTrader]]'s founding principle). The reimplementation gap between research code and production code is where silent divergence lives.
2. **Vectorized path only for triage.** [[vectorbt]]-style parameter sweeps answer "any edge at all?" in seconds; only event-driven results are decision-grade. Share the indicator library between modes; never share execution semantics.
3. **Futures as first-class citizens.** [[Futures-Contract-Mechanics|Instrument objects]] carry tick size/value, point multiplier, margins (loaded from dated config, never hardcoded), session calendar (RTH vs ETH, 5:00 PM CT reopen, maintenance break), and roll rules.
4. **Dual-series discipline** — the highest-ROI futures-specific correctness rule: unadjusted per-contract prices for fills/margin/P&L, [[Continuous-Contract-Construction|back-adjusted continuous series]] for signals only. Nearly impossible to retrofit.
5. **Anti-overfitting framework from day one, not bolted on:** [[Walk-Forward-Analysis]], [[Combinatorial-Purged-Cross-Validation]] (purge + embargo), [[Deflated-Sharpe-Ratio]] + PBO tracking the number of trials, Monte Carlo trade resampling. Only cost-adjusted per-contract P&L is reported.

## Data layer

- **[[Databento]]** (GLBX.MDP3) for CME tick/MBO: licensed distributor, nanosecond timestamps, identical historical/live APIs. Pay-as-you-go ~$26/GB trades, ~$1/GB MBO, $125 free credits; Standard $179/mo (rising to $199 for new subscribers after 2026-06-22).
- **Storage:** Parquet + DuckDB (single-node research default); ArcticDB for versioning; ClickHouse only at multi-TB/multi-user; kdb+ out of scope (~$100k/yr).
- **[[Information-Driven-Bars]]** (tick/volume/dollar/imbalance) built from trade-level data; dollar bars target ~50 bars/day via ADV/50 threshold heuristic.

## Execution realism

[[Execution-Realism]] hierarchy: next-bar-open (honest minimum, what scalppulse uses) → intrabar OHLC worst-case → tick-level replay (the only honest level for intraday futures scalping) → queue-position modeling ([[HftBacktest]] reference). Slippage must be per-instrument and per-session — "a single global slippage constant is a common, dangerous oversimplification."

## Optimization ladder

Profile first → NumPy/Polars vectorization → Numba `@njit` on event loop and fills (~300x reported) → multiprocessing for sweeps → Rust (PyO3) only for profiler-proven matching-engine bottlenecks. Polars over pandas at scale (5x load, 8x less memory).

## Build order (milestones)

M0 instrument+data foundations → M1 vectorized daily MVP → M2 event-driven core (Numba, deterministic replay) → M3 execution realism (order types, slippage models) → M4 tick/queue modeling → M5 validation framework (parallel, ongoing) → M6 Rust hot paths (only if needed). Benchmark escape hatches: never going live → drop parity rigor; daily/swing only → defer M4 indefinitely and lean on the vectorized path.

> [!key-insight] Convergence with the vault's empirical results
> The report's thesis — costs and honest fills matter more than any indicator — is exactly what [[mesfin2026-mnq-intraday-falsification]] found academically and what the scalppulse sessions (2026-07-12: 3 concepts + ML meta-filter + stocks-in-play ORB, all killed net of costs) found empirically. The blueprint's CPCV/DSR framework is the formalization of the train/test + cross-symbol gauntlet used there.

## Caveats (from the report itself)

Margins/fees are time-sensitive (Nov 2025 snapshots); Databento per-GB rates partly derived, not rate-card; CPCV/DSR superiority rests on synthetic-environment studies; all backtest Sharpes are upper bounds.
