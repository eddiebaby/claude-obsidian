---
type: source
source_type: paper
title: "Cross-Impact of Order Flow Imbalance in Equity Markets"
author: "Rama Cont, Mihai Cucuringu, Chao Zhang"
date_published: 2021-12-24
url: "https://arxiv.org/abs/2112.13213"
domain: quantitative-finance
created: 2026-07-07
updated: 2026-07-07
confidence: high
tags:
  - source
  - quantitative-finance
  - microstructure
  - order-flow
key_claims:
  - "Multi-level (integrated) OFI predicts short-horizon returns better than best-level OFI"
  - "Predictability decays rapidly; concentrated at horizons far below 1 minute"
  - "Cross-asset OFI adds little once multi-level single-asset OFI is used"
status: developing
related:
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[Tick-Size-Microstructure]]"
---

# Cont, Cucuringu & Zhang — Cross-Impact of Order Flow Imbalance

Answers the "can order flow rescue the intraday bot?" question with a clean negative for signals and a useful positive for execution: OFI's predictive power **decays within seconds-to-minutes** — below the LucidFlex non-HFT floor — so it cannot be the directional signal for 1–30+ minute holds. Cross-asset OFI adds little beyond multi-level single-asset OFI.

## What survives for the PRD

**OFI as execution layer, not signal:** time entries/exits within an already-triggered trade to shave slippage. The PRD's cost model budgets 1–2 ticks slippage per round turn against a required ≥ 4–5 tick gross edge; recovering even half a tick per side materially moves net expectancy. Requires order book data from the execution feed (Rithmic depth), which is a Phase 0 platform question.
