---
type: source
source_type: paper
title: "The Overnight Drift"
author: "Nina Boyarchenko, Lars Christian Larsen, Paul Whelan"
date_published: 2020-03-01
url: "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3560269"
domain: quantitative-finance
created: 2026-07-07
updated: 2026-07-07
confidence: medium
tags:
  - source
  - quantitative-finance
  - overnight-drift
  - futures
key_claims:
  - "Overnight drift in S&P 500 E-mini futures is compensation to intermediaries for absorbing order imbalances at the NYSE close"
  - "Much of the overnight return accrues around the European market open, when dealers can offload inventory risk"
status: developing
related:
  - "[[Overnight-Drift]]"
  - "[[glasserman2025-overnight-news]]"
  - "[[LucidFlex Automated Scalping PRD]]"
---

# Boyarchenko, Larsen & Whelan — The Overnight Drift

NY Fed Staff Report (No. 917) / SSRN. The mechanism paper for the overnight drift on **ES futures specifically** — the exact vehicle class of the [[LucidFlex Automated Scalping PRD]].

## Mechanism

Dealers absorb order imbalances at the NYSE close and are compensated through higher overnight returns; in E-mini futures much of the overnight return is earned **around the European open** (~2–4am ET), when dealers can offload risk. This makes the drift *conditionally timed*, not a uniform hold-all-night effect — a partial-night hold (e.g., late evening → post-Euro-open) may capture most of the return at a fraction of the exposure.

## Cost honesty

For intermediaries, the paper's framing is that net of balance-sheet, risk, and funding charges the anomaly is compensation, not free money. A retail prop trader does not bear those institutional charges — the retail cost is commissions + spread (~1–2 ticks on MES) — but does bear overnight gap risk against a $2,000 trailing MLL.

> [!gap] Primary source not fetched (SSRN and newyorkfed.org both returned 403). Claims here are from corroborating secondary summaries; confidence capped at medium until the staff report PDF is read directly. Also unverified: post-2020 magnitude.
