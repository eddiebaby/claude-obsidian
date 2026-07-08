---
type: source
source_type: paper
title: "Hedging Demand and Market Intraday Momentum"
author: "Guido Baltussen, Zhi Da, Sten Lammers, Martin Martens"
date_published: 2021-01-01
url: "https://ideas.repec.org/a/eee/jfinec/v142y2021i1p377-403.html"
domain: quantitative-finance
created: 2026-07-07
updated: 2026-07-07
confidence: high
tags:
  - source
  - quantitative-finance
  - intraday
  - futures
key_claims:
  - "Across 60+ futures (equities, bonds, commodities, FX) 1974-2020, the last 30 minutes are positively predicted by the rest-of-day return"
  - "Mechanism: gamma hedging by option market makers and leveraged-ETF rebalancing, which trade WITH the day's move near the close"
  - "The effect reverts over subsequent days — it is flow pressure, not information"
status: developing
related:
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[mesfin2026-mnq-intraday-falsification]]"
  - "[[Research - Intraday Futures Strategies Under Prop-Firm Constraints]]"
---

# Baltussen, Da, Lammers & Martens 2021 (JFE) — Hedging Demand and Market Intraday Momentum

The strongest upgrade to menu family #10 in [[LucidFlex Automated Scalping PRD]]: peer-reviewed (JFE), 60+ futures contracts, 46 years of data, and — unlike Gao et al.'s statistical pattern — a **mechanism**: option dealers hedging short gamma and leveraged-ETF managers rebalancing must buy into rising closes and sell into falling ones. Flow, not information; hence the multi-day reversion.

## Why the mechanism matters for the bot

1. **Conditioning:** flow pressure scales with dealer gamma exposure and leveraged-ETF AUM — on days when dealers are long gamma the effect should weaken or invert. A gamma-exposure proxy (e.g., SpotGamma-style estimates or OI-based approximations) becomes a testable filter — information that is NOT in 5-min OHLCV bars, hence outside [[mesfin2026-mnq-intraday-falsification]]'s falsification scope.
2. **Cross-asset breadth:** documented on bonds/commodities/FX futures too — the same sleeve may diversify across micro contracts later.
3. **Formulation:** rest-of-day → last 30 min (vs Gao's first-30-min variant): both should be in the Phase 1 pre-registered grid.

> [!gap] Abstract does not address net-of-cost tradability at retail size; the flow mechanism guarantees the pattern, not the profit. Phase 1 measures net expectancy directly.
