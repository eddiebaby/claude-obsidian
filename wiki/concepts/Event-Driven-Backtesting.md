---
type: concept
title: "Event-Driven Backtesting"
status: developing
domain: quantitative-finance
address: c-000144
created: 2026-07-13
updated: 2026-07-13
tags:
  - concept
  - backtesting
  - architecture
  - trading-infrastructure
related:
  - "[[Execution-Realism]]"
  - "[[Walk-Forward-Analysis]]"
  - "[[NautilusTrader]]"
  - "[[QuantStart]]"
  - "[[vectorbt]]"
  - "[[Backtest-Overfitting]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
---

# Event-Driven Backtesting

Architecture in which market data is drip-fed bar-by-bar (or tick-by-tick) as **events** that must be acted on in sequence, rather than computed over whole arrays at once. The dominant design for any engine that must be honest about execution — and the one that should serve both backtest and live trading with unchanged strategy code (**backtest/live parity**).

## The six-component loop (QuantStart canon)

Event (MARKET/SIGNAL/ORDER/FILL) → Event Queue → **DataHandler** (emits MarketEvents; historic or live subclasses swap freely) → **Strategy** (consumes data, emits SignalEvents) → **Portfolio** (signals → orders with sizing/risk; tracks positions, processes fills; for futures: margin, mark-to-market, roll events) → **ExecutionHandler** (orders → fills; simulated broker or real adapter behind one interface). RiskManager and PerformanceAnalytics sit alongside.

## Why it beats vectorized for decisions

- **Structural anti-lookahead**: data arrives as events, so future information is hard to touch by accident; a vectorized engine has "no built-in mechanism that would prevent you from cheating."
- Path-dependent order chains (stops, OCO brackets, partial fills, queue position) can be modeled honestly; vectorized engines execute/reject instantly by construction.

## Division of labor

Keep a vectorized fast-path ([[vectorbt]]-style) strictly for parameter-sweep triage, sharing the indicator library but never the execution semantics. Only event-driven results are decision-grade. Do not build two permanent engines.

## Vault context

The scalppulse rig (2026-07-12) implements the minimal honest version: signal-on-close → next-bar-open fills, intrabar stop-first brackets, costs per side. The compass blueprint is the path from that to a full engine (Numba hot loop, deterministic replay, swappable live handlers).
