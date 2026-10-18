---
type: entity
title: "EODHD"
created: 2026-09-19
updated: 2026-09-19
domain: quantitative-finance
address: c-000154
tags:
  - entity
  - data-vendor
  - equities
status: developing
aliases: [EOD Historical Data]
related:
  - "[[Norgate-Data]]"
  - "[[Point-in-Time-Universe]]"
  - "[[compass2026-unified-backtester-prd-brief]]"
sources:
  - "[[compass2026-unified-backtester-prd-brief]]"
---

# EODHD

EOD/fundamentals data vendor. It's the cheaper alternative to [[Norgate-Data]] for point-in-time constituents.

- Historical constituents via the Fundamentals Data API (**$59.99/mo**, ~$599.90/yr) or an Indices Historical Constituents add-on (**$29.99/mo**). Dividend-adjusted EOD is also available.
- **Limits:** point-in-time reconstruction is reliable only from **April 2012**, and deep snapshots are documented for the **S&P 500 only**, so Nasdaq-100 coverage is weak. That's why the brief makes Norgate the primary pick.
