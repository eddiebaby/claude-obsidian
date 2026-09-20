---
type: entity
title: "vectorbt"
created: 2026-07-13
updated: 2026-07-13
domain: quantitative-finance
address: c-000142
tags:
  - entity
  - software
  - backtesting
  - python
status: developing
related:
  - "[[Event-Driven-Backtesting]]"
  - "[[compass2026-backtesting-engine-blueprint]]"
  - "[[HftBacktest]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
---

# vectorbt

NumPy+Numba "vectorized" backtesting library (PRO version adds Rust kernels). The compass blueprint assigns it exactly one job: **fast signal triage across huge parameter grids** — thousands of combinations in seconds — before porting survivors to an event-driven engine for decision-grade results.

## Two honest caveats from the report

- Even vectorbt "doesn't actually do any vectorized backtesting — it follows a sequential approach" internally row-by-row.
- "No proper order management — once you issue an order command, it gets executed/rejected immediately." No partial fills, queue position, or path-dependent order chains.

## Design lesson

Flat structured NumPy arrays instead of per-event Python objects — the allocation/GC discipline that makes Numba effective; the same lesson applies to any custom engine's hot loop.
