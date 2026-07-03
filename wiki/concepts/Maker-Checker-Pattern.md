---
type: concept
title: "Maker-Checker Pattern"
status: mature
created: 2026-06-27
updated: 2026-06-27
domain: quantitative-finance
tags:
  - concept
  - maker-checker
  - verification
  - agentic-systems
  - quantitative-finance
  - risk-management
related:
  - "[[Loop-Engineering]]"
  - "[[loop-engineering-hedge-funds-2026]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
---

# Maker-Checker Pattern

The principle that the entity which produced an output cannot be trusted to grade it. The remedy is structural separation: a *maker* generates the output; a *checker* (with different instructions, ideally a different model, and zero exposure to the maker's reasoning) applies deterministic verification gates.

The agent that wrote the code is the worst possible judge of whether the code is correct. The agent that generated the signal is the worst possible judge of whether the signal represents real alpha or pure noise.

---

## Institutional Origin

Every serious prop shop is structurally organized as a maker-checker stack:
- **Jane Street**: the trader who proposes a trade does not approve the trade
- **Citadel**: the researcher who builds a model does not validate the model
- **Renaissance Technologies**: the Medallion Fund's extraordinary performance is in part attributed to strict internal validation separation

The agentic loop merely automates an institutional pattern that has existed since open-outcry trading pits. Loop engineering applies it to solo operators.

---

## Structure of the Split

```
Maker Agent (Sonnet-class)          Checker Agent (Opus-class)
────────────────────────            ──────────────────────────
Reads SKILL.md                      Receives only: the signal
Reads latest data                   (no maker reasoning trace)
Produces candidate signal           Applies deterministic gates
Writes to STATE.md                  Returns: pass/reject + report
↓                                   ↓
pending_signal.json  ──────────→   verification result
```

Critical constraint: the checker **never sees how the maker reasoned.** That separation is the entire edge. A checker that reads the maker's justification will tend to confirm it rather than adversarially test it.

---

## The Verification Gates (Trading)

Five deterministic thresholds computable from backtest output:

| Gate | Threshold | Rationale |
|------|-----------|-----------|
| Annualized Sharpe | > 1.5 | Minimum risk-adjusted return criterion |
| Maximum drawdown | < 10% | Capital preservation floor |
| Newey-West t-statistic | > 2.0 | Inference robust to autocorrelated returns |
| Out-of-sample period | >= 24 months | Prevents in-sample overfit |
| Sector exposure | < 30% | Concentration risk limit |

The checker does not need to understand the strategy. It needs to compute five numbers and apply five inequalities.

**Newey-West t-stat**: adjusts standard error of the alpha estimate for heteroskedasticity and autocorrelation in residuals. Required because strategy returns are almost always serially correlated. Ordinary t-stats overstate significance.

---

## Healthy Rejection Rate

In production deployments, a healthy maker-checker split rejects 40-60% of candidate signals before execution.

- **Below 40%**: warning sign. Usually indicates verifier looseness, not maker excellence.
- **Above 60%**: may indicate overly tight gates or poor maker quality.
- **Equities**: often above 55% (harder to find genuine edge)
- **Liquid futures**: lower rejection rate
- **Crypto**: lowest (signal quality dominated by latency, not statistical edge)

---

## Failure Mode: Verification Debt

*Verification debt* = the gap between the verification gate the loop currently enforces and the gate the strategy actually requires to remain in regime.

Causes:
- Verifier tuned once and never recalibrated
- Market regime changed; old thresholds no longer appropriate
- Gates still trigger *occasional* rejections, so the system *feels* rigorous
- In practice, almost every candidate passes

The system appears to be compounding while it is accruing latent risk.

Cure: schedule a recalibration loop that runs against the rolling outcomes log in STATE.md and tightens/loosens gates based on observed precision and recall. Ideally, a *third* agent — an auditor of the verifier itself.

---

## Why Different Model Matters

Using Opus-class for the checker and Sonnet-class for the maker is not about capability hierarchy — it is about independence. Different model architectures have different failure modes and different tendencies toward confirmation bias. When maker and checker share a model, their blind spots overlap.

Current production latency with this split: 4-12 seconds end-to-end. Adequate for intraday momentum, mean-reversion, and event-driven strategies on minute or hour scale. Insufficient for genuine HFT.

---

## Worktree Discipline

The most common architectural error: running the risk monitor inside the same worktree as the maker. When the maker drifts into a degenerate regime (overconfident, style-drifted, ignoring risk signals), the risk monitor drifts with it. The kill switch never fires.

Fix: risk monitor runs in a strictly isolated worktree with no shared context with either maker or checker. It observes the loop from outside, not from within it.

---

## See Also

- [[Loop-Engineering]] — the broader framework; maker-checker is one of the six structural primitives
- [[loop-engineering-hedge-funds-2026]] — the source with the full pseudocode and production observations
- [[zhang2026-benchmarking-deep-ts-equity]] — relevant for choosing which model architectures to use as maker vs. checker
