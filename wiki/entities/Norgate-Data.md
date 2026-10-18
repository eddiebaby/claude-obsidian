---
type: entity
title: "Norgate Data"
created: 2026-09-19
updated: 2026-09-19
domain: quantitative-finance
address: c-000153
tags:
  - entity
  - data-vendor
  - equities
  - survivorship-bias
status: developing
related:
  - "[[Point-in-Time-Universe]]"
  - "[[EODHD]]"
  - "[[compass2026-unified-backtester-prd-brief]]"
  - "[[Post-Earnings Announcement Drift Strategy]]"
sources:
  - "[[compass2026-unified-backtester-prd-brief]]"
---

# Norgate Data

EOD equity-data vendor. The brief ranks it the **best turnkey fix for survivorship bias** for a solo researcher.

- **Platinum US Stocks: USD 630/yr** (USD 346.50 for 6 months). This is the *minimum* tier with point-in-time index constituents and delisted securities; Gold and Silver don't include them.
- Constituents: S&P 500, Nasdaq-100, Russell 1000/2000/3000, S&P 100/400/600, point-in-time.
- Delisted history back to 1990 (the Diamond tier goes to 1950). Split and dividend adjustments are bundled.
- **EOD only**, with no intraday data.

**When to buy:** only when a cross-sectional equity strategy is actually being built ([[Post-Earnings Announcement Drift Strategy]], [[Index Rebalance and Event-Driven Strategy]], small-cap mean reversion). The [[Retail Alpha Strategy Roadmap]] already named Norgate/Sharadar as the shared small-cap data layer. Buying it earlier is paying for data that sits unused.
