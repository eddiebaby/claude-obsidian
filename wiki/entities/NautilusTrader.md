---
type: entity
title: "NautilusTrader"
created: 2026-07-13
updated: 2026-07-13
domain: quantitative-finance
address: c-000138
tags:
  - entity
  - software
  - backtesting
  - trading-infrastructure
status: developing
related:
  - "[[Event-Driven-Backtesting]]"
  - "[[compass2026-backtesting-engine-blueprint]]"
  - "[[vectorbt]]"
  - "[[LEAN-QuantConnect]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
---

# NautilusTrader

Open-source algorithmic trading platform and the **reference architecture** for a modern event-driven engine: Rust core with a Python control plane, nanosecond deterministic clock, message-bus + Actor model, event replay for reproducibility, Parquet data catalog.

## Why it matters

Its explicit design goal is **backtest/live parity** — eliminating the traditional split where "research is conducted in Python using vectorized approaches, while production trading systems are implemented separately... in compiled languages." Strategy code is unchanged between backtest and live.

## What to borrow / avoid

- **Borrow:** the Rust-core/Python-control split, parity discipline, deterministic replay, Parquet catalog.
- **Avoid:** steep learning curve, heavy Rust+Cython build; overkill if never going live. The compass blueprint's advice: emulate selectively, or adopt outright only at institutional scale.
