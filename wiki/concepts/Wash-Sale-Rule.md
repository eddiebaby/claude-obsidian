---
type: concept
title: "Wash-Sale Rule"
domain: quantitative-finance
complexity: intermediate
address: c-000166
created: 2026-11-08
updated: 2026-11-08
status: developing
aliases:
  - "Wash sale"
  - "Ticker partition"
  - "Section 475(f) election"
  - "Trader tax status"
tags:
  - concept
  - quantitative-finance
  - tax
  - risk-management
related:
  - "[[schwab-systematic-trading-prd-2026-11]]"
  - "[[Section-1256-Contracts]]"
  - "[[Short-Term Mean Reversion Strategy]]"
  - "[[Trend-Following]]"
sources:
  - "[[schwab-systematic-trading-prd-2026-11]]"
---

# Wash-Sale Rule

**A taxable loss is disallowed if a substantially identical security is bought within 30 days.** If the repurchase happens in an IRA, the loss is gone permanently, because the IRA's basis never carries it. A systematic program that trades the same index in two accounts will trip this constantly unless the design prevents it.

## The PRD's fix: partition by index

From [[schwab-systematic-trading-prd-2026-11]] §10.2:

- **FR-TAX-1, ticker partition.** Each index belongs to one account. SPY and QQQ belong to the taxable intraday sleeve (E8). The IRA sleeves use VTI, IWM, DIA, the sector SPDRs and non-equity ETFs. Whether two ETFs on the same index are "substantially identical" is unsettled, so the partition is by **index**, not by ticker.
- **FR-TAX-2, wash-sale ledger.** The OMS tags every taxable loss and blocks a same-index buy in any account for 30 days.
- KPI: wash-sale events per month. Any cross-account event means the partition has a hole.

Instruments it does not touch: [[Section-1256-Contracts]] (XSP, futures) and anything bought and sold inside the IRA.

## The escape hatch: Section 475(f)

- If Scott qualifies for trader tax status (facts-and-circumstances) and elects 475(f), securities are marked to market. Gains become ordinary income, the wash-sale rule stops applying, and the $3,000 capital-loss cap goes away.
- It is hard to revoke and must be elected before 15 April of the year it takes effect (IRS Topic 429).
- 1256 contracts keep 60/40 treatment and should not be swept into the election.
- **Decision owner: the CPA**, in Phase 4, after a year of after-tax reports per sleeve.

## Why it matters for strategy choice

High-turnover taxable sleeves (E8 intraday, E9 overnight SPY) generate short-term gains and frequent same-ticker round trips. That is part of why the PRD benches overnight SPY (E9) and puts the daily ETF sleeves in the IRA.
