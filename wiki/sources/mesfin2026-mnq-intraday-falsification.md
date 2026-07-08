---
type: source
source_type: paper
title: "Structural Limits of OHLCV-Based Intraday Signals in MNQ Futures: A Systematic Falsification Study"
author: "Mathias Mesfin"
date_published: 2026-05-05
url: "https://arxiv.org/abs/2605.04004"
domain: quantitative-finance
created: 2026-07-07
updated: 2026-07-07
confidence: high
tags:
  - source
  - quantitative-finance
  - futures
  - intraday
key_claims:
  - "14 OHLCV signal families tested on 947 days of 5-min MNQ data (2021-2025): none pass walk-forward validation with realistic costs"
  - "Gross edge at next-bar-open execution is 0.07-1.50 points per trade — below the ~2-point round-trip cost"
  - "Opening range breakout fails in all variants (immediate, pullback, delayed entry)"
status: developing
related:
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[kurth2026-trend-following-demise]]"
  - "[[byrd-balch-2019-intraday-ml-market-efficiency]]"
  - "[[Tick-Size-Microstructure]]"
  - "[[Backtest-Overfitting]]"
---

# Mesfin 2026 — MNQ Intraday Signal Falsification

The most directly relevant paper to the [[LucidFlex Automated Scalping PRD]] in existence: a systematic falsification study of retail-style intraday signals on **exactly the instrument** (MNQ) and **exactly the bar granularity** (5-min OHLCV) a prop-firm bot would trade.

## Setup

- 947 trading days of 5-minute MNQ futures, 2021–2025.
- 14 signal families: opening range breakouts, gap strategies, volume signals, cross-session momentum, liquidity grabs, volatility-conditioned classifiers, news-driven approaches.
- Out-of-sample walk-forward; pass criteria: t ≥ 2.0, N ≥ 30 trades, positive net of a fixed 2-point round-trip cost, multi-year stability.
- Two positive-control signals (known genuine edges from separate research) confirm the harness can detect real edge — the nulls are not a broken test.

## Result

**No signal family meets all criteria.** Gross edge available to next-bar-open execution is 0.07–1.50 points/trade — structurally below transaction cost. ORB fails in every entry variant. One gap-continuation signal reached t = 3.23 (+14.52 points) but with N = 22, below minimum sample size — the classic seductive small-N trap ([[Backtest-Overfitting]]).

## What it means for the PRD

- Downgrades ORB (menu family #1) and all C-grade OHLCV families: gaps, volume, level/liquidity signals — falsified on MNQ 2021–25, not merely unevidenced.
- Contradicts Zarattini-Aziz-Barbon's net-positive SPY intraday results — instrument, cost model, and strategy definitions differ; the PRD's Phase 1 harness adjudicates on MES/MNQ directly.
- Fourth independent confirmation of the post-2009 fast-edge death: [[kurth2026-trend-following-demise]] (tick-size mechanism), [[byrd-balch-2019-intraday-ml-market-efficiency]] (ML prediction), and this paper all converge.

## Caveats

- Author's own scope note: a null result for THIS instrument, bar type, and execution style — not a universal claim. Signals using information not in 5-min OHLCV bars (order flow, cross-asset, announcement timing, overnight decomposition) are outside the falsification.
- Single-author arXiv preprint, not peer-reviewed; methodology is transparent and reproducible, which partially compensates.
