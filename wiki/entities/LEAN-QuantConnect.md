---
type: entity
title: "LEAN (QuantConnect)"
created: 2026-07-13
updated: 2026-07-13
domain: quantitative-finance
address: c-000141
tags:
  - entity
  - software
  - backtesting
status: developing
aliases: [LEAN, QuantConnect]
related:
  - "[[Event-Driven-Backtesting]]"
  - "[[Execution-Realism]]"
  - "[[compass2026-backtesting-engine-blueprint]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
---

# LEAN (QuantConnect)

QuantConnect's open-source engine. In the compass blueprint's borrow-table its value is the **reality-modeling abstractions**: pluggable fill / slippage / fee / margin / buying-power models per security.

## Details worth stealing

- Slippage model family: `NullSlippageModel`, `ConstantSlippageModel`, `VolumeShareSlippageModel` (slippage scales with order size vs bar volume — the right template for market impact).
- Fill-model nuance: its futures stop-market fills at close+slippage while equities use `max(open, stop)+slippage` — modeling choices like this must be conscious, not inherited defaults.

## Caveats

Large C#-centric codebase; ecosystem lock-in.
