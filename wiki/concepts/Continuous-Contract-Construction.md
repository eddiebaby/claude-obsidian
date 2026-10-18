---
type: concept
title: "Continuous Contract Construction"
status: developing
domain: quantitative-finance
address: c-000145
created: 2026-07-13
updated: 2026-09-19
tags:
  - concept
  - futures
  - data-engineering
  - backtesting
aliases: [back-adjustment, Panama method, dual-series discipline]
related:
  - "[[Futures-Contract-Mechanics]]"
  - "[[Event-Driven-Backtesting]]"
  - "[[Micro-Futures Trend Strategy]]"
  - "[[Trend-Following]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
  - "[[compass2026-unified-backtester-prd-brief]]"
---

# Continuous Contract Construction

How to stitch individual futures contracts (ESH6, ESM6, …) into one analyzable series across quarterly rolls — called "the single most consequential data-engineering decision" for a futures engine.

## The three methods

| Method | Mechanics | Use / failure mode |
|---|---|---|
| **Unadjusted splice** | Raw concatenation | Wrong for almost everything: artificial gaps at each roll (a spliced VIX series showed a 14.8% jump when the real move was 0.3%) |
| **Back-adjusted (Panama)** | Subtract each roll gap as constant offset from all prior prices | Correct for per-period P&L and trend signals; levels drift, can go negative over long histories, percentage returns distorted |
| **Proportional (ratio)** | Multiply history by old-settle/new-open ratio | Preserves percentage returns; absolute-level signals (fixed stops) must be re-scaled |

## The dual-series discipline (the rule that matters)

**Unadjusted per-contract series for fills, margin, and P&L. Back-adjusted (or proportional) continuous series for indicators and signals only. Never compute P&L off the adjusted series.** The two series coexist, keyed to the same timeline: Portfolio marks to unadjusted front-month settlement; Strategy reads the adjusted series from the DataHandler. This is what separates a professional futures engine from a retail one, and it is nearly impossible to retrofit — adopt from day one.

## Vendor reality: Databento doesn't adjust

[[Databento]]'s continuous symbols (`ES.v.0` and similar) splice **raw** contract prices with no back- or ratio-adjustment. The adjusted signal series has to be built on our side: **difference (back-adjusted)** for absolute-P&L/level work, **ratio** for return-based work. Keep the raw per-contract prices for fills and slippage across the roll ([[compass2026-unified-backtester-prd-brief]]).

## Roll rules

Support both **date-based** (fixed days before expiry; volume migrates on "rollover Thursday," ~8 trading days out) and **volume/open-interest-based** (roll when back-month volume/OI exceeds front). Expiring-contract volume drops ~80% in a single session and spreads widen several-fold — the engine must roll before the "volume desert" even though ES/NQ are cash-settled.
