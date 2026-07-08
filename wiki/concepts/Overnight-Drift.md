---
type: concept
title: "Overnight-Drift"
domain: quantitative-finance
complexity: intermediate
created: 2026-07-07
updated: 2026-07-07
tags:
  - quantitative-finance
  - anomaly
  - futures
  - overnight-drift
status: developing
aliases:
  - "Overnight Effect"
  - "Night Effect"
  - "Overnight Premium"
related:
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[Micro-Futures Trend Strategy]]"
  - "[[Tick-Size-Microstructure]]"
sources:
  - "[[glasserman2025-overnight-news]]"
  - "[[boyarchenko-larsen-whelan-overnight-drift]]"
  - "[[knuteson2020-overnight-intraday-returns]]"
---

# Overnight Drift

The tendency of equity indices to earn essentially all of their return while the cash market is closed, with intraday (open-to-close) returns flat to negative. Documented since Cooper, Cliff & Gulen 2008; called "the grandmother of all market anomalies" (Haghani/Elm Wealth). Decades of data, replicated worldwide, robust across competing explanations.

## The decomposition

Close-to-close index return = overnight (close → next open) + intraday (open → close). Over 30 years, the overnight component captures nearly all cumulative gains (Source: [[glasserman2025-overnight-news]]); intraday is flat-to-negative (Source: [[knuteson2020-overnight-intraday-returns]]).

## Proposed mechanisms

| Mechanism | Source | Status |
|---|---|---|
| Dealer inventory compensation — intermediaries absorb close imbalances, earn the overnight return, unload around the European open (~2–4am ET) | [[boyarchenko-larsen-whelan-overnight-drift]] (ES futures) | Mainstream, mechanism-specific timing |
| Overnight news arrival + differential response | [[glasserman2025-overnight-news]] | Mainstream, partial explanation |
| Retail order timing (buy at open) + institutional close selling | Haghani et al. "Night Moves" | Plausible complement |
| Large-player manipulation | Knuteson | Heterodox; use his data, not his theory |

## Tradability — honest ledger

- **For institutions:** net of balance-sheet, funding, and risk charges the anomaly is compensation for a service, not free money.
- **Cross-sectional long-short versions** (long top overnight performers): ~38% gross annualized 1995+ but killed by impact and borrow costs, and **decaying since the 2008–2015 publication wave** (Elm Wealth).
- **Simple long-index-futures overnight hold:** retail costs are only commissions + ~1-tick spread on MES (~2–3 ticks round trip vs a mean overnight move measured in tens of ticks). The binding constraints are (1) gap risk against a small account/MLL and (2) rule legality — on LucidFlex, holding through the night is conditional on Lucid's definition of "overnight" (Phase 0 item in [[LucidFlex Automated Scalping PRD]]).
- **Timing refinement:** the Boyarchenko result implies a partial-night hold (late evening → after European open) may capture most of the drift with less exposure.

> [!gap] Post-2020 magnitude on ES specifically is unverified — the primary staff report was not fetchable (403). Phase 1 must measure the drift on 2015–2026 MES/ES data directly before trusting it.
