---
type: entity
title: "DuckDB"
created: 2026-09-19
updated: 2026-09-19
domain: quantitative-finance
address: c-000155
tags:
  - entity
  - database
  - data-engineering
status: developing
related:
  - "[[Instrument-Master]]"
  - "[[compass2026-backtesting-engine-blueprint]]"
  - "[[compass2026-unified-backtester-prd-brief]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
  - "[[compass2026-unified-backtester-prd-brief]]"
---

# DuckDB

In-process columnar SQL engine. Both compass backtesting reports treat it as the consensus solo-researcher store: **Hive-partitioned Parquet (by symbol/date) queried through DuckDB**, with Arrow for in-memory interchange.

- Zero setup: no server, reads Parquet in place.
- **ASOF JOIN** aligns time series whose timestamps don't match exactly, e.g. futures bars against equity bars, or bars against event timestamps, without look-ahead.
- For repeated join-heavy work, load the Parquet into a `.duckdb` file. Partition and row-group sizing affects memory more than the choice of engine does.

Current state: the vault's rigs store CSVs per symbol in `trading/*/data/`. Moving to Parquet + DuckDB is Phase 0 of both reports.
