---
type: concept
title: "Pattern Day Trader Rule"
domain: quantitative-finance
complexity: basic
address: c-000164
created: 2026-11-08
updated: 2026-11-08
status: developing
aliases:
  - "PDT rule"
  - "PDT"
  - "Intraday Margin Buying Power"
tags:
  - concept
  - quantitative-finance
  - regulation
  - broker
  - intraday
related:
  - "[[schwab-systematic-trading-prd-2026-11]]"
  - "[[Schwab-Trader-API]]"
  - "[[Gamma Closing Reversal Strategy]]"
  - "[[LucidFlex Automated Scalping PRD]]"
sources:
  - "[[schwab-systematic-trading-prd-2026-11]]"
---

# Pattern Day Trader Rule

**At Schwab the pattern-day-trader limit is gone as of 2026-06-08.** The constraint that replaces it is real-time intraday buying power.

## The old rule

FINRA margin rule: four or more day trades in five business days flags a margin account as a pattern day trader, which then needs $25,000 minimum equity. This is general knowledge, not from the source. Below that line, small accounts could not day-trade stocks or ETFs freely. That pushed intraday index ideas toward futures (no PDT rule) and prop-firm evals.

## What changed in 2026

| Date | Change | Scope |
|---|---|---|
| 2026-06-08 | Schwab stops counting day trades | Schwab margin accounts |
| 2026-07-13 | Real-time Intraday Margin Buying Power; a trade that would create an intraday margin deficit can be blocked | Schwab margin accounts with ≥ $2,000 |
| to 2027-10-20 | FINRA phase-in for other brokers (Regulatory Notice 26-10) | Industry |

Source: [[schwab-systematic-trading-prd-2026-11]] §10.1, citing Schwab and FINRA RN 26-10. The PRD's §3 E8 text says "June 4". Use June 8.

## Why it matters for the book

- **Intraday index exposure is cheaper as ETFs now.** A one-cent SPY spread is ≈ 0.15 bp per round trip. An MES round trip at Schwab costs ≈ $5.24 (≈ 1.05 index points). Size also steps in single shares, not $30k+ contracts.
- The QQQ result in [[Gamma Closing Reversal Strategy]] (+1.8 bps net, t 1.65) can trade in the ETF itself at a Schwab margin account. It no longer has to go through MNQ.
- It weakens one argument for the prop-firm route ([[LucidFlex Automated Scalping PRD]]) at small size, though not the eval-fee/payout asymmetry argument.

## The new failure mode

Buying-power blocks. The OMS must check intraday buying power before every intraday order. The PRD's KPI is "buying-power rejections per week (any → review sizing)".
