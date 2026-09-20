---
type: concept
title: "Information-Driven Bars"
status: developing
domain: quantitative-finance
address: c-000148
created: 2026-07-13
updated: 2026-07-13
tags:
  - concept
  - data-engineering
  - machine-learning
  - microstructure
aliases: [dollar bars, volume bars, tick bars, imbalance bars]
related:
  - "[[Marcos Lopez de Prado]]"
  - "[[Tick-Size-Microstructure]]"
  - "[[Databento]]"
  - "[[Combinatorial-Purged-Cross-Validation]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
---

# Information-Driven Bars

López de Prado's alternative sampling schemes (*Advances in Financial ML*, ch. 2): instead of sampling by clock time, sample when a fixed amount of **activity** has occurred.

- **Tick bars** — every N trades
- **Volume bars** — every N contracts/shares
- **Dollar bars** — every $X traded; most robust to price-level and float changes
- **Imbalance / runs bars** — when signed order-flow imbalance exceeds expectation

## Why bother

Time bars oversample quiet periods and undersample bursts. Dollar bars produce return distributions closer to normal with lower serial correlation — a real advantage for any ML feature pipeline (the scalppulse meta-filter used 5-minute time bars; this is one of its known weaknesses).

## Practical heuristic

Set the dollar/volume threshold to trailing 30-day average daily value ÷ ~50, targeting ~50 bars/day. Requires trade-level (tick) data to construct accurately — one of the concrete reasons the compass blueprint budgets for [[Databento]] trades data rather than bar feeds.
