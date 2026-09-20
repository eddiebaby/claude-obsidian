---
type: entity
title: "QuantStart"
created: 2026-07-13
updated: 2026-07-13
domain: quantitative-finance
address: c-000140
tags:
  - entity
  - education
  - backtesting
status: developing
related:
  - "[[Event-Driven-Backtesting]]"
  - "[[compass2026-backtesting-engine-blueprint]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
---

# QuantStart

Quant-education site whose **event-driven backtester series** defines the canonical minimal class hierarchy: Event / Event Queue / DataHandler / Strategy / Portfolio / ExecutionHandler. The compass blueprint calls it "the cleanest minimal skeleton to start from" — the starting point that NautilusTrader and LEAN elaborate.

## Key contributions cited

- The six-component decomposition with swappable ABC DataHandler/ExecutionHandler (the seam that gives backtest/live parity).
- The structural anti-lookahead argument: drip-feeding bars as events makes lookahead bias hard to introduce by accident, unlike vectorized engines.
- The dual-series warning for futures: adjusted prices for strategy backtesting are not the right series for other purposes.

## Caveats

Naive instant fills, no futures mechanics, single-threaded — a skeleton, not a finished engine.
