---
type: concept
title: "Walk-Forward Analysis"
status: developing
domain: quantitative-finance
address: c-000146
created: 2026-07-13
updated: 2026-07-13
tags:
  - concept
  - validation
  - backtesting
  - anti-overfitting
related:
  - "[[Combinatorial-Purged-Cross-Validation]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[Backtest-Overfitting]]"
  - "[[Regime-Trust-Gating]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
  - "[[bailey-lopez-de-prado-2014-deflated-sharpe]]"
---

# Walk-Forward Analysis

Pardo's industry-standard realistic simulation: **re-optimize on a rolling training window, test on the adjacent out-of-sample window, roll forward, repeat** — so a strategy must repeatedly prove itself on data its parameters never saw. The out-of-sample segments concatenate into one honest equity curve.

## Why it is the floor, not the ceiling

Walk-forward produces a single test path and can still be gamed by trying many configurations and keeping the survivor — which is why the compass blueprint pairs it with [[Combinatorial-Purged-Cross-Validation]] (many paths) and [[Deflated-Sharpe-Ratio]] (deflate for the number of trials). Report all three by default; never judge a strategy on a single in-sample Sharpe.

## Vault practice

The scalppulse ML meta-filter (2026-07-12) used month-by-month walk-forward with a one-day boundary embargo: each month predicted by a model trained only on prior months. Result — OOS AUC decayed 0.56 → 0.45 over seven months — is exactly the non-stationarity signal walk-forward exists to expose (a single random split would have hidden it).
