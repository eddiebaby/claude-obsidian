---
type: concept
title: "Instrument Master"
created: 2026-09-19
updated: 2026-09-19
domain: quantitative-finance
address: c-000158
tags:
  - concept
  - backtesting
  - data-engineering
  - architecture
status: developing
aliases: [security master, unified instrument table]
related:
  - "[[Futures-Contract-Mechanics]]"
  - "[[Continuous-Contract-Construction]]"
  - "[[Point-in-Time-Universe]]"
  - "[[Event-Driven-Backtesting]]"
  - "[[DuckDB]]"
sources:
  - "[[compass2026-unified-backtester-prd-brief]]"
---

# Instrument Master

The single table that lets one engine trade futures and equities. Every bar, order, and position refers to an internal instrument ID, and asset-class differences live here as data rather than as special cases in the code.

## Fields

| Field | Equity | Futures |
|---|---|---|
| asset class, venue, currency | stock, NYSE/Nasdaq, USD | future, CME Globex, USD |
| multiplier | 1 | ES 50 · MES 5 · NQ 20 · MNQ 2 |
| tick size | 0.01 | 0.25 |
| session-calendar ID | NYSE (9:30–16:00 ET, optional pre/post) | CME Globex (Sun 18:00 → Fri 17:00 ET, daily 17:00–18:00 break; RTH/ETH tags) |
| roll rule | — | calendar / OI / volume ([[Continuous-Contract-Construction]]) |
| point-in-time listing, delisting, symbol changes | yes ([[Point-in-Time-Universe]]) | contract expiries |
| buying power | cash (+ short borrow/locate cost, dividend accrual) | margin (initial/maintenance from dated config) |

## Companion conventions

- **Bars:** one OHLCV schema with UTC timestamps plus explicit session tags, stored in both raw and adjusted versions.
- **Calendars:** `exchange_calendars` / `pandas-market-calendars`. Align carefully whenever a strategy trades futures against cash-equity hours, e.g. an equity-hours signal driving an ES trade.
- **Blotter:** one accounting model covering cash, per-instrument positions, margin used, realized/unrealized P&L, and mark-to-market across both asset classes.

## Vault state

`trading/propfirm/futures_costs.py::FuturesSpec` is a minimal futures-only version (point value, tick, commission, slippage). Extending it into a small table with calendar ID and roll rule is the cheapest start.
