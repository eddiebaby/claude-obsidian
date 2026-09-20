---
type: entity
title: "HftBacktest"
created: 2026-07-13
updated: 2026-07-13
domain: quantitative-finance
address: c-000143
tags:
  - entity
  - software
  - backtesting
  - microstructure
status: developing
related:
  - "[[Execution-Realism]]"
  - "[[compass2026-backtesting-engine-blueprint]]"
  - "[[Tick-Size-Microstructure]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
---

# HftBacktest

Python/Numba + Rust backtester and the **reference implementation for queue-position fill modeling** — the gold standard for passive/limit-order strategies. Models both feed and order latency, reconstructs the full order book from L2/L3 feeds, offers configurable queue models (e.g., power-law probability) and partial fills.

## The core realism rule it encodes

A resting limit order fills only when volume traded through the price exceeds the queue ahead of you. Injecting measured latency distributions is first-class: "a strategy whose edge disappears under realistic latency is not real."

## Caveats

HFT-focused, crypto-centric examples, requires L2/L3 data. Its own docs warn against both overly optimistic and overly pessimistic simulation — treat all backtest Sharpes as upper bounds.
