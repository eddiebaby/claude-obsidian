---
type: source
source_type: paper
title: "Does Overnight News Explain Overnight Returns?"
author: "Paul Glasserman, Kriste Krstovski, Paul Laliberte, Harry Mamaysky"
date_published: 2025-07-06
url: "https://arxiv.org/abs/2507.04481"
domain: quantitative-finance
created: 2026-07-07
updated: 2026-07-07
confidence: high
tags:
  - source
  - quantitative-finance
  - overnight-drift
key_claims:
  - "Nearly all U.S. stock market gains are earned overnight; average intraday returns are negative or flat, over a 30-year window"
  - "News topic prevalence and differential market response explain a substantial share of the overnight premium"
status: developing
related:
  - "[[Overnight-Drift]]"
  - "[[knuteson2020-overnight-intraday-returns]]"
  - "[[boyarchenko-larsen-whelan-overnight-drift]]"
  - "[[LucidFlex Automated Scalping PRD]]"
---

# Glasserman et al. 2025 — Does Overnight News Explain Overnight Returns?

2.4 million news articles paired with 30 years of returns, supervised topic analysis. Confirms the overnight/intraday split ([[Overnight-Drift]]) with a news-based partial explanation, and forecasts out-of-sample which stocks outperform overnight and underperform intraday.

## Relevance to the PRD

Independent, recent, high-credibility confirmation that the overnight premium is real and persistent — the structural basis for menu family #13 (Globex overnight-session drift) in [[LucidFlex Automated Scalping PRD]]. The paper is cross-sectional equities, not index futures execution; magnitude and timing for ES/MES come from [[boyarchenko-larsen-whelan-overnight-drift]].

> [!gap] The paper does not state whether the premium persists in the most recent (2024+) data — post-publication decay unverified.
