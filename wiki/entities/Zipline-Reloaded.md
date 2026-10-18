---
type: entity
title: "Zipline-Reloaded"
created: 2026-09-19
updated: 2026-09-19
domain: quantitative-finance
address: c-000156
tags:
  - entity
  - backtester
  - open-source
status: developing
related:
  - "[[Event-Driven-Backtesting]]"
  - "[[NautilusTrader]]"
  - "[[LEAN-QuantConnect]]"
  - "[[compass2026-unified-backtester-prd-brief]]"
sources:
  - "[[compass2026-unified-backtester-prd-brief]]"
---

# Zipline-Reloaded

Community-maintained fork of Quantopian's Zipline. The brief uses it as a **reference, not a dependency**, for three things:

- **Pipeline API**: declarative cross-sectional factor computation over a point-in-time universe. It's the model for US-equity factor research ([[Point-in-Time-Universe]]).
- **Portfolio accounting**: cash, positions, and P&L bookkeeping.
- **Trading calendars**: the origin of `exchange_calendars`.

Compare [[NautilusTrader]] (architecture and live parity), [[vectorbt]] (sweeps), and [[LEAN-QuantConnect]] (multi-asset accounting). General warning: every framework comes with silent optimistic defaults for fills, slippage, and corporate actions. Reconcile any library against a hand-checked case.
