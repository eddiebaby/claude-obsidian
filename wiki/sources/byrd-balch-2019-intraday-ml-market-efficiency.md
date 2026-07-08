---
type: source
source_type: paper
title: "Intra-day Equity Price Prediction using Deep Learning as a Measure of Market Efficiency"
author: "David Byrd, Tucker Hybinette Balch"
date_published: 2019-08-22
url: "https://arxiv.org/abs/1908.08168"
domain: quantitative-finance
created: 2026-07-07
updated: 2026-07-07
confidence: medium
tags:
  - source
  - quantitative-finance
  - intraday
  - machine-learning
key_claims:
  - "Two ML-based intraday prediction strategies on U.S. equities (2003-2017) were profitable until 2009 and unprofitable after"
  - "Authors attribute the inflection to rising HFT volume / market efficiency, acknowledged as needing further investigation"
status: developing
related:
  - "[[mesfin2026-mnq-intraday-falsification]]"
  - "[[kurth2026-trend-following-demise]]"
  - "[[LucidFlex Automated Scalping PRD]]"
---

# Byrd & Balch 2019 — Intraday ML Prediction as a Market-Efficiency Measure

U.S. equities 2003–2017: deep-learning intraday price prediction worked until 2009, then died. The authors treat declining profitability as evidence of increasing market efficiency, tentatively linked to HFT volume growth.

## Relevance

Third leg of the post-2009 convergence: [[kurth2026-trend-following-demise]] (fast trend, tick-size mechanism), [[mesfin2026-mnq-intraday-falsification]] (OHLCV signals on MNQ), and this paper (intraday ML on equities) independently date the death of fast retail-accessible edges to the same regime shift. Any Phase 1 backtest in the [[LucidFlex Automated Scalping PRD]] that "works" pre-2010 but not after is measuring this regime change, not edge.

> [!gap] Cost treatment (gross vs net) and exact holding periods not specified in the abstract; full text unread.
