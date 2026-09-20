---
type: concept
title: "Combinatorial Purged Cross-Validation (CPCV)"
status: developing
domain: quantitative-finance
address: c-000147
created: 2026-07-13
updated: 2026-07-13
tags:
  - concept
  - validation
  - anti-overfitting
  - machine-learning
aliases: [CPCV, purged cross-validation]
related:
  - "[[Walk-Forward-Analysis]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[Backtest-Overfitting]]"
  - "[[Marcos Lopez de Prado]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
---

# Combinatorial Purged Cross-Validation (CPCV)

López de Prado's (2018) validation scheme for financial ML: generate **many backtest paths** from combinations of train/test group splits, with two leakage killers:

- **Purging** — drop training samples whose label windows overlap the test period's information.
- **Embargo** — drop samples immediately after the test set, killing serial-correlation leakage.

A representative configuration: 10 train / 8 test groups → 36 backtest paths, with ~21-day (1 month) purge and embargo.

## Why it beats walk-forward and k-fold

Peer-reviewed comparison (Arian et al., synthetic controlled environment) finds CPCV superior on both **Probability of Backtest Overfitting (PBO)** and deflated Sharpe. One walk-forward path is one draw; 36 combinatorial paths give a distribution — the difference between "it worked once" and "it works."

## Caveat

The superiority evidence is from synthetic environments — robust, but not live-trading proof. Financial labels overlap in time (a 60-min triple-barrier label spans 12 bars), which is precisely why naive k-fold catastrophically leaks and why purge width must match label horizon. The scalppulse ML rig (2026-07-12) implemented the poor-man's version: monthly walk-forward + one-day embargo; CPCV is the upgrade at compass Milestone 5.
