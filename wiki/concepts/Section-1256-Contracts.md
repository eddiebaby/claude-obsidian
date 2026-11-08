---
type: concept
title: "Section 1256 Contracts"
domain: quantitative-finance
complexity: intermediate
address: c-000165
created: 2026-11-08
updated: 2026-11-08
status: developing
aliases:
  - "Section 1256"
  - "60/40 tax treatment"
  - "1256 contracts"
tags:
  - concept
  - quantitative-finance
  - tax
  - options
  - futures
related:
  - "[[schwab-systematic-trading-prd-2026-11]]"
  - "[[Wash-Sale-Rule]]"
  - "[[Volatility Risk Premium Strategy]]"
  - "[[Micro-Futures Trend Strategy]]"
  - "[[Futures-Contract-Mechanics]]"
sources:
  - "[[schwab-systematic-trading-prd-2026-11]]"
---

# Section 1256 Contracts

**Gains on Section 1256 contracts are taxed 60% long-term and 40% short-term, whatever the holding period.** They are marked to market at year end and reported on Form 6781, and the wash-sale rule does not apply. For a short-holding taxable sleeve that is the cheapest treatment available.

## What qualifies

| Instrument | 1256? | Note |
|---|---|---|
| Broad-based index options: SPX, XSP, NDX, RUT | Yes | Cash-settled, European; XSP is 1/10 SPX |
| Regulated futures (ES/MES, NQ/MNQ, …) | Yes | General knowledge; applies to the futures work in [[Futures-Contract-Mechanics]] |
| ETF options: SPY, QQQ, IWM | **No** | Ordinary equity options: short-term, wash-sale applies |
| Stocks and ETFs | No | Short-term if held ≤ 1 year |

Source: [[schwab-systematic-trading-prd-2026-11]] §10.2, citing Cboe on XSP.

## Design consequences

- **Put-write goes in XSP, not SPY.** The O1 sleeve ([[Volatility Risk Premium Strategy]]) uses XSP spreads for 60/40 treatment and no wash sales. European exercise also removes early-assignment and pin risk. That is also why the PRD folds covered calls into O1 (O2): SPY-based versions lose 1256 status.
- **475(f) does not override it.** A mark-to-market trader election converts securities gains to ordinary income, but 1256 contracts keep 60/40. See [[Wash-Sale-Rule]].
- **Hawaii.** The state taxes capital gains its own way. Have the CPA confirm how the 60/40 split flows through the state return (PRD §10.2, open question).

## Cost note

Schwab charges $0.65 per contract per leg, so a vertical costs $2.60 per round trip. Proprietary index products such as SPX and VIX add an exchange fee that Schwab does not publish on its pricing page.
