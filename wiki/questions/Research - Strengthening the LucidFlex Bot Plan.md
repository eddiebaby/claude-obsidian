---
type: synthesis
title: "Research: Strengthening the LucidFlex Bot Plan"
domain: quantitative-finance
created: 2026-07-07
updated: 2026-07-07
tags:
  - research
  - quantitative-finance
  - futures
  - intraday
  - prop-firm
status: developing
question: "What can strengthen the LucidFlex bot plan beyond the falsified OHLCV signals — signals outside Mesfin's scope, sizing under trailing drawdown, and eval-pass tactics?"
answer_quality: solid
related:
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[Research - Intraday Futures Strategies Under Prop-Firm Constraints]]"
  - "[[Prop-Firm-Eval-Sizing]]"
  - "[[Overnight-Drift]]"
  - "[[baltussen2021-hedging-demand-intraday-momentum]]"
  - "[[busseti-ryu-boyd-2016-risk-constrained-kelly]]"
  - "[[cont2021-cross-impact-ofi]]"
sources:
  - "[[baltussen2021-hedging-demand-intraday-momentum]]"
  - "[[busseti-ryu-boyd-2016-risk-constrained-kelly]]"
  - "[[cont2021-cross-impact-ofi]]"
---

# Research: Strengthening the LucidFlex Bot Plan

## Overview

Follow-up sweep to [[Research - Intraday Futures Strategies Under Prop-Firm Constraints]]. That round established what does NOT work (bar-level OHLCV signals, falsified on MNQ). This round targets what makes the *surviving* plan stronger: signals that live outside 5-min OHLCV bars, and the two disciplines that matter more than signal choice for a prop account — **sizing under a fixed drawdown** and **eval-pass mechanics**.

## Key Findings

1. **Intraday momentum has a peer-reviewed MECHANISM, and it's exploitable precisely because it's outside OHLCV bars.** Baltussen et al. 2021 (JFE), 60+ futures, 1974–2020: the last 30 minutes are predicted by the rest-of-day return, driven by **option-dealer gamma hedging + leveraged-ETF rebalancing** trading with the close (Source: [[baltussen2021-hedging-demand-intraday-momentum]], confidence high). This is flow, not information — hence it reverts over days. The conditioning variable (dealer gamma exposure) is *not in OHLCV data*, so [[mesfin2026-mnq-intraday-falsification]] never tested the conditioned version. This upgrades menu family #10 from "fragile" to "mechanism-backed, with a testable gamma filter."

2. **Sizing is the highest-leverage improvement, and there's a convex-optimal answer.** Busseti-Ryu-Boyd 2016: maximize log-growth subject to P(drawdown > α) < β; dominates fractional Kelly at equal drawdown risk (Source: [[busseti-ryu-boyd-2016-risk-constrained-kelly]], confidence high). Maps exactly onto the eval (α = $2,000 MLL, β = tolerated bust probability). Replaces the PRD's ad-hoc "5% of MLL per trade." Filed as [[Prop-Firm-Eval-Sizing]].

3. **Order flow is an execution tool, not a signal, at this timeframe.** OFI predictability decays within seconds-to-minutes (Cont et al. 2021), below the non-HFT floor — useless as a 1–30 min directional signal, but usable to shave entry/exit slippage against the cost model (Source: [[cont2021-cross-impact-ofi]], confidence high).

4. **The dominant eval failure mode is mechanical, not strategic, and LucidFlex's structure dodges it.** 60–70% of trailing-drawdown liquidations happen right after the trader's best day (intraday-trailing ratchet chasing the high). LucidFlex uses EOD trailing + lock at breakeven+$100 — structurally the safer variant (Source: aggregator guides, confidence medium). Sweet spot 0.5–1% risk/trade for pass rate; 1.5–2% for ROI-per-eval-dollar. See [[Prop-Firm-Eval-Sizing]].

## Concrete upgrades to [[LucidFlex Automated Scalping PRD]]

- **Add a gamma-conditioned intraday-momentum sleeve** (Baltussen formulation: rest-of-day → last 30 min), with dealer-gamma proxy as a filter. Explicitly outside Mesfin's falsification.
- **Replace ad-hoc sizing** with risk-constrained Kelly (α = MLL, β = target bust prob); Monte Carlo the full eval (target + MLL + consistency cap + daily stop) to get expected eval spend before funding.
- **Add an OFI execution layer** (Rithmic depth) to recover slippage — conditional on Phase 0 platform confirming L2 data.
- **Reframe the whole eval as a sizing problem**: with a genuine small edge, expected eval cost = fee / pass-probability; if that exceeds ~2 payouts, don't run it even if the edge is real.

## Contradictions

- Baltussen (intraday momentum robust across 60+ futures, 46 yrs) vs [[mesfin2026-mnq-intraday-falsification]] (cross-session momentum fails on MNQ 2021–25). Reconciliation: Mesfin tested *unconditioned* OHLCV momentum; Baltussen's edge is in the *flow mechanism and its conditioning*, and includes the close-auction window Mesfin's next-bar-open execution may not capture. Not a true contradiction — different signals sharing a name. Phase 1 tests both explicitly.

## Open Questions

- Cheapest reliable dealer-gamma proxy for a retail bot (SpotGamma subscription vs OI-derived approximation)? Cost-benefit unresolved.
- Does the Baltussen close-driven effect survive LucidFlex's 4:15pm hard-flat (30 min before the 4:45 cutoff, and before the cash close)? The last-30-min window is exactly where flat-by-close bites — may require trading the 3:15–3:45 window instead of 3:30–4:00.
- Risk-constrained Kelly needs a trustworthy per-trade return distribution — circular until Phase 1 produces one; bootstrap from backtest, widen for parameter uncertainty.

## Sources

- [[baltussen2021-hedging-demand-intraday-momentum]] — Baltussen, Da, Lammers, Martens, JFE 2021
- [[busseti-ryu-boyd-2016-risk-constrained-kelly]] — Busseti, Ryu, Boyd, 2016
- [[cont2021-cross-impact-ofi]] — Cont, Cucuringu, Zhang, 2021
