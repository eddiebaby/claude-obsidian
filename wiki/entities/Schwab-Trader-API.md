---
type: entity
title: "Schwab Trader API"
created: 2026-09-19
updated: 2026-09-19
domain: quantitative-finance
address: c-000152
tags:
  - entity
  - broker
  - market-data
  - api
status: developing
aliases: [schwab-py, Schwab API]
related:
  - "[[compass2026-unified-backtester-prd-brief]]"
  - "[[Databento]]"
  - "[[Point-in-Time-Universe]]"
  - "[[Norgate-Data]]"
sources:
  - "[[compass2026-unified-backtester-prd-brief]]"
---

# Schwab Trader API

Scott's broker API and the free price source behind `trading/scalppulse/` and `trading/propfirm/`. It replaced the retired TD Ameritrade API. The standard Python client is **schwab-py** (alexgolec), successor to `tda-api`. Alternatives: `schwabdev`, `pyschwab`, and others.

## Market data: `priceHistory`

- Bars: 1/5/10/15/30-minute, daily, weekly, monthly. One symbol per call; quotes can be batched. ~120 req/min; HTTP 429 → honor `Retry-After`, bounded backoff.
- **Depth (community-observed, not documented):** 1m ≈ 48 days (other wrappers report 30–35), 30m ≈ 9 months, daily ≈ 20 years (AAPL back to 1985). The vault got **~9 months of 5m** for equities and **~7 months of /MES 5m** in practice.
- **Adjustment:** split-adjusted, **not dividend-adjusted**. No corporate-action feed, no index constituents, no delisted names. See [[Point-in-Time-Universe]].
- Futures: the brief says Schwab gives none, but the vault's own pulls contradict that (see [[compass2026-unified-backtester-prd-brief]]). Futures history is shallow in any case, so use [[Databento]] for depth.
- Gotcha: schwab-py's per-frequency wrappers have sent `period`/`periodType` together with explicit dates, which the API says not to combine. Pin a known-good version and check the returned date span.

## Auth

Access token: 30 min, auto-refreshed. **Refresh token: hard 7-day expiry**, after which requests fail with `invalid_client`. This requires a manual browser re-auth every week (already handled in `schwab_data.py`), so fully unattended collection isn't possible. Plan a Sunday re-auth.

## Costs

Equities $0 online (SEC/regulatory fees on sells). Futures **$2.25/contract/side** + exchange/regulatory fees. Options $0.65/contract.

## Role in the stack

Use it for deep **daily** equity history plus a **forward-archived** intraday feed. Don't use it for multi-year intraday backtests.
