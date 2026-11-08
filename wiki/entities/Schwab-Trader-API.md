---
type: entity
title: "Schwab Trader API"
created: 2026-09-19
updated: 2026-11-08
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
  - "[[Pattern-Day-Trader-Rule]]"
  - "[[schwab-systematic-trading-prd-2026-11]]"
sources:
  - "[[compass2026-unified-backtester-prd-brief]]"
  - "[[schwab-systematic-trading-prd-2026-11]]"
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

## Order entry and operations (from [[schwab-systematic-trading-prd-2026-11]])

- **Orders: stocks, ETFs, listed options only.** Futures orders return HTTP 400 "Unsupported instrument". Futures, futures options and forex trade only in thinkorswim. thinkorswim conditional orders run server-side on thinkScript, but can't take external signals, don't re-arm after a fill, and don't support recursive studies. Treat any futures sleeve at Schwab as manual.
- Order types via API: market, limit, stop, stop-limit, trailing, MOC, LOC; multi-leg options via complex-order types (verify each structure at 1 lot).
- **Order-write limit: 0–120/min per account**, set at app registration. Register at 120, budget ≤ 30. Data calls run at ~120/min.
- **No sandbox.** paperMoney isn't reachable from the API, so paper trading means an in-house shadow simulator fed by live Schwab quotes.
- Client order IDs are not assumed. The OMS persists every intent before sending and re-queries open orders before a retry.
- The streamer carries equity, option **and futures** quotes. An ES quote can drive a signal that executes in SPY or XSP.
- Token service: refresh the access token every 25 min. Write any rotated refresh token to the secrets manager before using it. Alert on day 5 of 7, and block new positions if the token would expire mid-session. Phone re-login runbook target: under 3 min, Sunday afternoon HST.
- [[Pattern-Day-Trader-Rule]]: Schwab stopped counting day trades 2026-06-08. Real-time intraday buying power arrived 2026-07-13, so check buying power before every intraday order.
- Account plumbing: a developer account plus an approved "Trader API – Individual" app (approval can take several days). Options spreads need spread approval; portfolio margin needs $125k (not required).

> [!contradiction] Futures price history, again
> The PRD (NFR-API-4, FR-DATA-S2) repeats that Schwab price history covers equities only. The vault's own ~7-month /MES 5m pull contradicts it (see above and [[compass2026-unified-backtester-prd-brief]]).

## Role in the stack

Use it for deep **daily** equity history plus a **forward-archived** intraday feed. Don't use it for multi-year intraday backtests.
