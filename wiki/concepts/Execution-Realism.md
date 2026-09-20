---
type: concept
title: "Execution Realism"
status: developing
domain: quantitative-finance
address: c-000149
created: 2026-07-13
updated: 2026-07-13
tags:
  - concept
  - backtesting
  - execution
  - microstructure
aliases: [fill modeling, slippage modeling]
related:
  - "[[Event-Driven-Backtesting]]"
  - "[[HftBacktest]]"
  - "[[LEAN-QuantConnect]]"
  - "[[Tick-Size-Microstructure]]"
  - "[[mesfin2026-mnq-intraday-falsification]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
---

# Execution Realism

"This is where backtests most often lie." The hierarchy of fill models, least → most honest:

1. **Next-bar-open** — signal on close, fill at next open. The honest minimum for daily/swing; kills the same-bar-close lookahead cheat.
2. **Intrabar OHLC worst-case** — for stops/limits, assume adverse ordering inside the bar (scalppulse: stop checked before target when both are in range).
3. **Tick-level replay** — marketable orders fill against the opposing book. The only honest level for intraday futures scalping.
4. **Queue-position modeling** — for passive limit orders: fill only when volume trades through your price beyond the queue ahead ([[HftBacktest]] reference).

## Slippage

Per-instrument AND per-session, never one global constant: ES/NQ RTH ≈ one tick on modest size; micros and overnight sessions run wider. For size, scale impact with order size vs bar volume ([[LEAN-QuantConnect]]'s `VolumeShareSlippageModel` template) or vs depth/ADV.

## Latency

Model feed latency and order latency separately; inject measured distributions. Retail/cloud to CME is milliseconds. "A strategy whose edge disappears under realistic latency is not real."

## The vault's empirical verdict

Every 2026-07-12 scalppulse result and [[mesfin2026-mnq-intraday-falsification]] agree: at intraday horizons, cost/fill modeling *is* the result — gross edges of fractions of an R evaporate under one honest tick of slippage. Order types to support before believing any intraday backtest: market, limit, stop, stop-limit, OCO brackets, trailing stops, each with explicit intrabar trigger logic.
