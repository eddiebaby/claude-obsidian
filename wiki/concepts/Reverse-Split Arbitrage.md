---
type: concept
title: "Reverse-Split Arbitrage"
domain: quantitative-finance
complexity: basic
created: 2026-11-03
updated: 2026-11-03
tags:
  - strategy
  - quantitative-finance
  - equity
  - event-driven
status: seed
aliases:
  - "RSA"
  - "Reverse Split Round-Up"
related:
  - "[[Index Rebalance and Event-Driven Strategy]]"
  - "[[Execution-Realism]]"
  - "[[Retail Alpha Strategy Roadmap]]"
sources: []
---

# Reverse-Split Arbitrage

Live scanner: `trading/equity-research/run_rsa.py`. Parser: `eqr/rsa.py`. Tests: `tests/test_rsa.py`. Research only. Scott places every order.

## Thesis

When a company does a reverse split and rounds fractional shares **up per holder**, 1 pre-split share becomes 1 post-split share worth about ratio × price.
- Example: one $0.40 share at 1:25 becomes a share worth about $10.
- The edge is mechanical, not predictive. It scales with the number of accounts, not with capital.

## Setup Conditions

- **Entry trigger:** an 8-K or 6-K announcing a reverse split with a fixed ratio, a first split-adjusted trading day, and per-holder round-up wording.
- **Kill wording:**
  - "cash in lieu": you get cash for the fraction instead of a share.
  - "rounded down".
  - "rounding … at the DTC-participant level": the round-up happens at the broker, so no extra share reaches your account.
  - Record-holder aggregation.
  - Any clause that excludes holders who bought after the announcement.
- **Robinhood can't buy most OTC names.** Check the exchange.

## Execution

| Parameter | Value |
|-----------|-------|
| Asset class | US-listed equities (Nasdaq / NYSE / NYSE American) |
| Timeframe | Event: buy before the split, sell after the round-up posts (about 3-4 weeks at Robinhood) |
| Position size | 1 whole share per account. Never fractional. Buying more adds price risk with no extra round-up. |
| Entry | By the close of **Buy by**, the last session before the first split-adjusted trading day. A day earlier is safer under T+1. |
| Exit | Sell the rounded-up share once it posts, or sell right away if the round-up never comes. |
| Downside | About 1 pre-split share price per account if the issuer pays cash instead. |
| Upside | price × (ratio − 1) per account, minus the post-split fade |

## Evidence

- Mechanics come from issuer filings. The 2026-10-15 to 11-03 sample had many round-ups: NXXT, ATYR, AXNX, HCAI, AIIO, GCTK, XXII.
- Other filings paid cash: WHLR, ONCO, OMEX, RUBI, TOPS, CAPS.
- ENHA rounded up, but at the DTC-participant level.
- Robinhood pays round-ups "when received from the issuer, typically 3-4 weeks". Its default for leftover fractions is cash.
- No realized P&L yet. Log fills in the tracker before claiming an edge.
- **Lessons from the first scan (2026-11-03):**
  - **AIIO.** The Oct 16 release promised "a full ordinary share" per holder. The Oct 27 meeting-results release switched to "disregarded … aggregated and sold". **The newest filing is the one to trust.**
  - **NCI.** The headline range was 1-for-2 to 1-for-400, with a "cap of 500-to-1". The actual ratio was "every eight (8) … into one (1)". The range and the cap are not the ratio.
  - **Cayman/BVI small caps.** Many file the meeting notice as a 6-K with a fixed effective date, before the vote. Treat these as pending until a results 6-K posts.
  - **Typical sizes.** Most live candidates pay $1-5 per account. Only the occasional 1-for-50+ on a $0.50+ stock pays $25-60 per account.

## Risks & Failure Modes

- **Issuer wording.** Issuers increasingly add participant-level or anti-arbitrage wording. Always read the quoted clause in the scan report.
- **Post-split fade.** These names often fall 20-50% while the round-up is pending, and the round-up share can't be sold until it posts.
- **Broker delay or denial.** Robinhood may pay cash despite round-up wording. Track every pending share per account.
- **Parser misses.** The parser is regex over filing text. MIXED or UNKNOWN results need a manual read.

## Status

Seed, 2026-11-03. Scanner built: `python run_rsa.py` writes `reports/rsa-YYYY-MM-DD.md`. 23 parser tests.

The first report had 3 BUY names:
- XXII 1:58, buy by 11/4
- ALPS 1:5, buy by 11/6
- NCI 1:8, buy by 11/9

It also had 5 pending a shareholder vote, led by LICN (1:100, vote 11/9).

Next: a per-account tracker for pending round-ups.
