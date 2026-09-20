---
type: concept
title: "Futures Contract Mechanics (ES/MES/NQ/MNQ)"
status: developing
domain: quantitative-finance
address: c-000150
created: 2026-07-13
updated: 2026-07-13
tags:
  - concept
  - futures
  - reference
  - contract-specs
aliases: [ES specs, MES specs, futures specs]
related:
  - "[[Continuous-Contract-Construction]]"
  - "[[Micro-Futures Trend Strategy]]"
  - "[[Prop-Firm-Eval-Sizing]]"
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[Overnight-Drift]]"
sources:
  - "[[compass2026-backtesting-engine-blueprint]]"
---

# Futures Contract Mechanics (ES/MES/NQ/MNQ)

Reference page for the CME equity-index contract family. Verify against CME product pages before sizing — specs and margins drift.

## Contract specs

| Contract | Tick | Tick value | Point value |
|---|---|---|---|
| ES | 0.25 | $12.50 | $50 |
| MES | 0.25 | $1.25 | $5 |
| NQ | 0.25 | $5.00 | $20 |
| MNQ | 0.25 | $0.50 | $2 |

Micros are exactly 1/10th of the E-minis and carried ~45% of equity-index ADV (Nov 2025). Design consequence: strategies should size in **notional/index units** and let the Instrument translate to contracts, so the same logic scales MES → ES.

## Margins (CME, snapshot 11/2025 — load from dated config, never hardcode)

ES $12,320/$11,200 (init/maint) · MES $1,232/$1,120 · NQ $18,480/$16,800 · MNQ $1,848/$1,680. Intraday broker margins far lower (MES ~$50). Initial ≈ 110% of maintenance.

## Sessions & settlement

Globex: Sunday 5 PM CT → Friday 4 PM CT, maintenance break 4–5 PM CT. **RTH 8:30 AM–3:15 PM CT carries ~70% of volume**; the trading-day boundary is the 5 PM reopen, not midnight. Daily settlement is a window around the cash close, and mark-to-market drives margin — the engine's session calendar must distinguish RTH/ETH and handle DST (store UTC internally, convert to America/Chicago for session logic only).

## Rollover

Quarterly (Mar/Jun/Sep/Dec, H/M/U/Z), third Friday expiry; volume migrates on rollover Thursday ~8 trading days prior (expiring volume −80% in one session, spreads widen). See [[Continuous-Contract-Construction]] for how the data layer must handle this.

## Costs

~$2.50–3.50 exchange+NFA fees per round turn plus commission (NFA $0.02/side). At MES's $5/point this is proportionally ~10x the drag of ES per notional — measured directly in the 2026-07-12 scalppulse /MES runs (~1.5 points round-trip all-in ≈ 20% of an average winner).
