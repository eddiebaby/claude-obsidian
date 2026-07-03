---
type: concept
title: "Online Ensemble Learning"
domain: quantitative-finance
complexity: advanced
status: developing
created: 2026-07-02
updated: 2026-07-02
aliases:
  - "Multiplicative Weights Update Method"
  - "MWUM"
  - "gradient-free ensemble learning"
tags:
  - concept
  - quantitative-finance
  - machine-learning
  - ensemble-learning
  - online-learning
related:
  - "[[quantitative-finance]]"
  - "[[miao-polak-online-ensemble-sector-rotation]]"
  - "[[Sector-Rotation]]"
sources:
  - "[[miao-polak-online-ensemble-sector-rotation]]"
---

# Online Ensemble Learning

Navigation: [[quantitative-finance]]

---

## Definition

Online ensemble learning combines forecasts from multiple constituent models by adaptively reweighting them **sequentially**, using only past forecast performance — no retraining, no gradient access to constituent models, and no forward-looking data. This makes it distinct from both (a) offline/static ensembles that fix weights once using the full historical sample, and (b) gradient-based online learning methods that require access to each model's internals.

The canonical instance in this vault is the **Multiplicative Weights Update Method (MWUM)** used in [[miao-polak-online-ensemble-sector-rotation]], which traces to algorithmic game theory and boosting (AdaBoost) roots (Arora, Hazan & Kale 2005; Alabdulmohsin 2018).

---

## Why Gradient-Free Matters

Because MWUM only needs each constituent model's *forecast output*, not its internal parameters or gradients, it can combine arbitrarily heterogeneous models — linear regressions, tree ensembles, and deep neural networks of varying depth — without needing a common differentiable framework. This also makes it practical for aggregating forecasts from **independent managers, teams, or organizational units** while preserving confidentiality, and suits decentralized or privacy-preserving infrastructures (e.g., microprediction networks).

---

## Mechanism

**Setup**: L constituent models each produce a forecast r̂_t^{(l)} at each time t. Weights w^{(t)} are maintained per model and normalized to a probability vector p^{(t)} = w^{(t)} / Σw^{(t)}_l. The ensemble forecast is r̃_t = r̂_t^T p^{(t)}.

**Update rule**: w^{(t+1)} = w^{(t)} (1 + η m^{(t)}), where η > 0 is a learning rate and m^{(t)} is a **gain function** observed after the period's realized return is known.

**Gain function decomposition** (the paper's central design choice):

m^{(t)}(p^{(t)}) = *exploitation term* − *exploration term*

- **Exploitation**: rewards models whose squared forecast error is smaller than a rolling estimate of return variance σ̂_t² (a volatility benchmark); penalizes models with larger error. This is the term that drives weight toward historically accurate models.
- **Exploration**: compares each model's prediction direction against the *current consensus* (the already-weighted ensemble forecast). A low-weight model predicting in the same direction as a dominant model is penalized as redundant (adds no new information); a low-weight model predicting in the *opposite* direction of the dominant model — provided its own error is small — is rewarded, because it contributes genuinely complementary (non-redundant) information.

This implements an explicit **bias-variance-diversity trade-off**: the ensemble doesn't just chase recent winners, it actively preserves model diversity, which is the mechanism separately formalized in ensemble-diversity theory (Wood et al. 2023).

**Adaptive learning rate**: rather than fixing η, [[miao-polak-online-ensemble-sector-rotation]] selects η* each rebalancing period from a grid of candidates, choosing whichever value achieved the best out-of-sample performance over the *prior* 12 months only — this keeps the procedure fully implementable without look-ahead bias, important given the paper's 35-year backtest spans multiple structural regimes.

---

## Regret Guarantees

The paper's central theoretical contribution is bounding online forecast regret **directly in terms of realized out-of-sample R²** rather than an abstract loss — R²_oos is standard, interpretable, and already used as the empirical performance metric practitioners care about.

- **Lemma 2 (asymptotic equivalence)**: the time-averaged gain (1/τ)Σ_t m^{(t)T}p^{(t)} converges almost surely to the realized R²_oos(τ) as the horizon τ → ∞, under mild regularity conditions (finite second moments, ergodicity, consistent variance estimation, bounded gain). This justifies using the gain function itself as a valid online proxy objective for R²_oos.
- **Lemma 3 (non-asymptotic high-probability bound)**: under i.i.d. Gaussian returns, a Chebyshev-plus-Young's-inequality argument gives P(|R²_oos(τ) − average gain| > ε) ≤ 2(1+L) / [ε σ_r τ² √(8/τ² − 6/τ + 1)] — the deviation probability decays at rate **τ^-2**, a concrete finite-sample concentration guarantee (not just an asymptotic limit).

Net effect: "the ensemble performs nearly as well as the best model in hindsight" — a regret bound in the classical online-learning sense (bounded gap to the best-in-hindsight comparator), but expressed in R² units that a portfolio manager can interpret directly, rather than an abstract cumulative-loss bound.

---

## Handling Nonstationarity

Financial return-generating processes are nonstationary — the relative accuracy ranking among models shifts across regimes. Static/offline ensembles (fixed weights solved once via a constrained quadratic program, per Breiman's stacked regression) cannot adapt to this. MWUM's per-period reweighting using only *recent* forecast errors gives it a structural advantage in nonstationary settings: it naturally down-weights a model whose edge has decayed and up-weights one whose relative accuracy has recently improved, without needing to detect a regime break explicitly.

Empirically in [[miao-polak-online-ensemble-sector-rotation]], the full online ensemble (with the exploration term) outperforms the "Exploitation Ensemble" (same online reweighting, but exploitation term only) — 1.19 vs. 0.99 average out-of-sample R² (equal-weighted sectors) — isolating the specific value of the diversity/exploration mechanism beyond mere adaptive accuracy-chasing.

---

## Performance-Weighted Averaging — Comparison Table

| Method | Weights | Adapts over time? | Uses model diversity? | Result in [[miao-polak-online-ensemble-sector-rotation]] (avg R²_oos, equal-weighted) |
|--------|---------|--------------------|-----------------------|----|
| Simple Average | Uniform | No | No | 0.90 |
| Offline Ensemble | Static, R²-optimal (closed-form QP) | No | No | 0.93 |
| Exploitation Ensemble | Online, accuracy-only | Yes | No | 0.99 |
| **Online Ensemble (MWUM, full gain)** | Online, accuracy + diversity | Yes | Yes | **1.19** |

---

## Related Vault Context

Contrast with [[zhang2026-benchmarking-deep-ts-equity]]'s **SMAA (Stochastic Multi-Criteria Acceptability Analysis)** framework — SMAA evaluates model rankings across preference-weight uncertainty for *model selection/diagnosis*, whereas MWUM here is a *live combination mechanism* that continuously blends all constituent models' outputs rather than selecting one. They are complementary rather than competing approaches: SMAA answers "which single model should I deploy under uncertain preferences," MWUM answers "how do I combine all of them adaptively without ever having to choose."

---

## See Also

- [[quantitative-finance]] — domain page
- [[Sector-Rotation]] — the strategy application this mechanism is used for in the vault
- [[miao-polak-online-ensemble-sector-rotation]] — source page, full theoretical treatment
- [[zhang2026-benchmarking-deep-ts-equity]] — contrasting multi-criteria model-selection framework (SMAA)
