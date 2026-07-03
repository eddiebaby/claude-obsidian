---
type: source
title: "When Alpha Breaks: Two-Level Uncertainty for Safe Deployment of Cross-Sectional Stock Rankers"
domain: quantitative-finance
status: complete
created: 2026-07-02
updated: 2026-07-02
tags:
  - source
  - paper
  - quantitative-finance
  - machine-learning
  - uncertainty-quantification
  - risk-management
source_type: paper
author: "Ursina Sanderink"
date_published: 2026-02-23
url: "https://arxiv.org/abs/2603.13252"
confidence: high
key_claims:
  - "Epistemic uncertainty (DEUP-adapted rank displacement) structurally couples to signal strength in cross-sectional ranking (median rho = 0.616), so inverse-uncertainty position sizing backfires"
  - "A strategy-level regime-trust gate G(t) built from trailing realized model efficacy (AUROC 0.72-0.75) detects when-to-trade far better than market-stress proxies (VIX AUROC ~0.45-0.50)"
  - "The best deployment policy is Binary Gate + Vol-Sizing + epistemic tail-risk cap: FINAL-holdout Sharpe 0.925 vs 0.375 for Gate+Vol alone"
related:
  - "[[Regime-Trust-Gating]]"
  - "[[Sector-Rotation]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
  - "[[quantitative-finance]]"
sources:
  - "[[.raw/2603.13252.pdf]]"
---

# When Alpha Breaks: Two-Level Uncertainty for Safe Deployment of Cross-Sectional Stock Rankers

Navigation: [[quantitative-finance]]

---

## Bibliographic Record

| Field | Detail |
|-------|--------|
| Author | Ursina Sanderink |
| Submitted | February 23, 2026 |
| arXiv | [2603.13252](https://arxiv.org/abs/2603.13252) [cs.AI] |
| Project | GitHub repo linked in paper; correspondence via LinkedIn |
| Source | PDF directly read (all 34 pages: main text, tables, references) |

---

## Abstract (verbatim)

"Cross-sectional equity rankers are often deployed as if point predictions were sufficient: the model outputs scores, and the portfolio follows the induced ordering. In practice, non-stationarity creates regime failures in which a historically profitable ranker becomes systematically unreliable. In the AI Stock Forecaster, a LightGBM ranker achieves strong all-period performance at the 20-day horizon (volatility-sized shadow-portfolio Sharpe 2.73), yet the 2024 holdout coincides with an AI thematic rally/sector rotation that breaks the signal at longer horizons (60d and 90d mean RankIC turn negative) and severely weakens 20d (RankIC 0.072 → 0.010, DEV → FINAL). This motivates treating deployment as two distinct decisions: (i) which individual positions require caution and (ii) whether the strategy should trade at all. We adapt Direct Epistemic Uncertainty Prediction (DEUP) to ranking by predicting rank displacement and defining a per-stock epistemic signal ê(x) = max(0, g(x) − a(x)), where a(t) is a deployable point-in-time baseline (PIT-safe, computed using only information available at t); all headline policy results use this PIT-safe a(t). We document a ranking-specific structural coupling between epistemic uncertainty and signal strength (median ρ(ê, |score|) = 0.616 across 1,865 dates), which causes inverse-uncertainty sizing to de-lever the strongest signals and degrade portfolio performance. To resolve this, we propose a two-level deployment architecture: a strategy-level regime-trust gate G(t) that decides whether to trade (AUROC 0.72 overall; 0.75 in FINAL) and reaches 80% precision at G ≥ 0.2 with 47% abstention; 7/8 correct across five crisis and three calm windows, and a position-level epistemic tail-risk cap (P85) that reduces exposure only for the most uncertain predictions while preserving score-tail convexity. The resulting operational policy is simple: trade only when G(t) ≥ 0.2, apply volatility sizing on active dates, and cap the top epistemic-uncertainty tail. In a deployment policy comparison at 20d, Gate+Vol+ê-Cap (P85) achieves the best risk-adjusted performance (ALL Sharpe 1.877 vs 1.886 for Gate+Vol; FINAL Sharpe 0.925 vs 0.375), indicating that DEUP adds economic value as a tail-risk guard rather than a continuous sizing denominator."

---

## Section Structure

1. Introduction
2. Related Work (uncertainty decomposition/DEUP; uncertainty in portfolio construction; selective prediction/abstention; regime detection; positioning table)
3. Problem Setup (cross-sectional ranking, universe/data, base ranker, shadow portfolio, DEV/FINAL protocol, rank-displacement loss)
4. Method (DEUP for ranking loss, structural coupling problem, two-level deployment architecture, deployment policy variants, conformal prediction intervals)
5. Experiments (design, metrics, baselines, ablations/stress tests)
6. Results (Claims 1-3, conformal supplement)
7. Discussion
8. Limitations
9. Conclusion

---

## Setup: The AI Stock Forecaster and the Failure Case

**Base ranker**: LightGBM gradient-boosted tree ensemble over a dynamic universe of up to 100 AI-exposed U.S. equities. Seven PIT-safe features: three momentum signals (`mom_1m`, `mom_3m`, `mom_12m`), two realized-volatility measures (`vol_20d`, `vol_60d`), a liquidity proxy (`adv_20d`), and cross-sectional rank on the current date. Trained walk-forward, expanding window, 109 folds, 90-trading-day embargo.

**Universe**: Feb 2016-Feb 2025, 2,277 trading dates, 109 walk-forward folds. Investable universe capped at 100 names (price ≥ $5, ADV ≥ $1M, fixed AI-themed ticker match). Realized size: mean 83.9 (ALL), 81.8 (DEV), 98.4 (FINAL). Benchmark: Invesco QQQ.

**DEV/FINAL protocol**: DEV = 2016-2023 (95 months, all tuning). FINAL = 2024 onward (14 months, evaluated once, no re-tuning).

**Shadow portfolio**: non-overlapping 20-day equal-weight top-10/bottom-10 long-short, 10 bps one-way cost.

**Table 1 — baseline performance without uncertainty controls (20d, volatility-sized shadow portfolio):**

| Metric | ALL | DEV (2016-2023) | FINAL (2024+) |
|--------|-----|------------------|----------------|
| Sharpe (ann.) | 2.734 | 3.121 | 2.337 |
| Max drawdown | -18.1% | -18.1% | -8.7% |
| Ann. return (arithmetic) | 87.0% | 79.6% | 137.3% |
| Hit rate (monthly) | 82.6% | 82.1% | 85.7% |
| Mean RankIC (20d/60d/90d) | 0.064/0.140/0.165 | 0.072/0.160/0.192 | 0.010/-0.005/-0.021 |

**The failure case**: the FINAL period (2024) coincides with an AI thematic rally / sector rotation. 20d signal weakens sharply (mean RankIC 0.072 → 0.010, DEV → FINAL); 60d and 90d mean RankIC invert to negative. The rotation disrupts the cross-sectional factor structure the LightGBM ranker relies on (momentum and volume features become temporarily uninformative), even though the model does not overfit to noise. This is the paper's central motivating failure: a historically strong ranker silently breaks under sector rotation, not under generic market stress.

**Why VIX-based regime proxies fail**: a VIX-percentile gate is worse than random at predicting model failure (AUROC 0.449 overall, 0.504 in FINAL). Mean stock volatility even reverses sign in FINAL (AUROC 0.460, below chance) — high average stock volatility in the AI universe during 2024 actually *predicted better* model days, the opposite of the DEV-period relationship. Market-stress proxies measure the environment's difficulty for a generic investor; model failure depends on whether *this specific model's* factor loadings remain informative. See [[Sector-Rotation]].

---

## DEUP Adapted to Ranking

**Rank-displacement loss** (Eq. 3): ℓ(x,τ) = |rank%(realized excess return) − rank%(score)|. Near-zero correlation with realized volatility (ρ = 0.054) — this is a ranking-error target, not a volatility proxy.

**Error predictor g(x)**: secondary LightGBM regression trained walk-forward on held-out rank-displacement residuals, using 11 features across per-prediction (score, abs_score, cross_sectional_rank), stock-level (vol_20d, vol_60d, mom_1m, adv_20d), and market-regime (vix_percentile_252d, market_regime_enc, market_vol_21d, market_return_21d) categories. `cross_sectional_rank` is the dominant feature at all horizons. g(x) achieves Spearman ρ(g, ℓ) ≈ 0.16-0.19 at 20d.

**Aleatoric baseline a(t)**: estimates irreducible ranking noise (the Bayes-risk floor). Two variants tested: oracle a_oracle(t) = P10 of same-date realized losses (hindsight, diagnostics only), and deployable PIT-safe a_PIT(t) = P10 of matured losses in a trailing window (W=60 primary, W=252 robustness check). All deployment-facing policy results use a_PIT(t) exclusively. Tier 0 (inverse IQR) and Tier 1 (factor-residual IQR) proxies for a(·) were tried and killed (ρ ≈ 0 at all horizons) — cross-sectional return dispersion does not predict ranking difficulty in this setting.

**Epistemic signal**: ê(x) = max(0, g(x) − a(x)). Within-date ordering of ê_oracle and ê_PIT is identical (both are date-level shifts of g(x)); only magnitudes differ, which matters for cap thresholds and conformal scaling but not diagnostic rank ordering.

**Validation (six diagnostics)**:
- Quintile monotonicity: Q5/Q1 rank-loss ratio 1.51 → 1.69 (20d) and 1.53 → 1.88 (90d), DEV → FINAL — stronger separation out-of-sample, opposite of overfitting.
- ρ(ê, ℓ): 0.144 (20d ALL) → 0.192 (20d FINAL); 0.146 (90d ALL) → 0.248 (90d FINAL). Improves under regime shift, exactly when needed.
- AUROC for above-median rank-loss events: 0.56-0.61 (moderate but genuine per-stock discrimination).
- Baseline dominance: ê and g(x) beat vol_20d and VIX percentile by 3-10x in correlation with rank loss; in FINAL, volatility and VIX lose predictive power entirely (ρ ≈ 0) while ê holds.
- Disentanglement: residualizing ê on vol_20d, vol_60d, vix_percentile_252d, mom_1m via OLS retains ρ = 0.11-0.24 with rank loss; max |correlation with VIX| = 0.074. Not repackaged volatility.
- Regime-failure detection: per-stock ê does NOT spike during the 2024 failure (crisis mean 0.259 vs non-crisis 0.271, statistically indistinguishable). Expected — per-stock signals cannot see date-level regime failure by design (see gate section below).
- Cross-model robustness: replicated on Rank Average 2 (LightGBM + FinText-TSFM ensemble); RA2 gives 35% higher ρ(ê,ℓ) at 20d (0.194 vs 0.144) and 44% higher at 60d, confirming DEUP quality responds to base-model robustness rather than being an LGB-specific artifact.

---

## The Structural Coupling Problem (Claim 2)

Across 1,865 trading dates, median cross-sectional Spearman correlation ρ(ê, |score|) = **0.616**, positive on >90% of dates. Mechanism: extreme cross-sectional ranks have more "room to fall" (a 95th-percentile stock can fall 95 points; a median stock at most 50), so rank displacement scales with distance from the median rank — exactly where the strongest trade ideas (top/bottom-10 stocks forming the shadow portfolio) live.

**Consequence**: inverse-uncertainty sizing (w_i ∝ 1/√(ê_i + ε)) systematically de-levers the stocks that contribute most to the long-short spread. This is not a failure of DEUP as an estimator — ê genuinely predicts error magnitude — it is a structural mismatch between a ranking-loss uncertainty metric and the multiplicative sizing paradigm that works in return-prediction settings (Spears et al. 2021; Liu et al. 2026).

**Table 5 — deployment policy ablation (20d, Sharpe × √12):**

| Variant | ALL | DEV | FINAL | Crisis MaxDD |
|---------|-----|-----|-------|--------------|
| Ungated Raw (LGB) | 2.730 | 3.107 | 1.650 | -7.4% |
| 1. Gate + Raw | 1.928 | 2.039 | -0.322 | -7.4% |
| 2. Gate + Vol | 1.886 | 1.971 | 0.375 | -8.4% |
| 3. Gate + UA Sort (λ=0.05) | 0.726* | — | — | — |
| 4. Gate + Resid-ê | 1.987 | 2.041 | 0.953 | -6.0% |
| **6. Gate + Vol + ê-Cap** | **1.877** | **1.928** | **0.925** | **-6.7%** |
| K4. Trail-IC (kill baseline) | 0.754 | — | — | — |

*Variant 3 ALL Sharpe 0.726 vs 0.817 for Gate+Vol per Section 6.2 text (Table 5 figures shown are the primary six; UA Sort and K4 reported inline).

Both continuous-uncertainty variants (Gate+UA Sort, Gate+Resid-ê) and the pure trailing-IC kill baseline (K4) underperform simple volatility-based sizing or add no value beyond the binary gate. Gate+Resid-ê in particular looks statistically clean (residualization removes the linear coupling with |score|) but the FINAL Sharpe (0.953 in Table 5, -0.450 reported in prose for a related variant) demonstrates residualization trades coupling-bias for noise — too unstable for monthly position sizing.

Robustness: coupling persists on Rank Average 2 (RA2 ê-sizing ALL Sharpe 0.430 vs 0.622 raw) — confirms this is a property of cross-sectional ranking geometry, not a LightGBM-specific artifact.

---

## Two-Level Deployment Architecture (Claim 3)

### Level 1: Strategy-level regime-trust gate G(t)

**Health index** H(t) combines three PIT-safe signals via expanding z-scores:
- H_real(t): EWMA (halflife 30, min periods 20) of matured daily RankIC, lagged by the horizon τ (the only fully honest realized-efficacy measure — no future information).
- H_drift(t): real-time composite of feature/score z-score drift, KS statistic of score distribution vs 60-day reference, and mean pairwise return correlation (cross-sectional correlation spike proxy).
- H_disagree(t): Spearman correlation between primary LGB and an alternative model (RA2) on the same date; low correlation flags potential regime boundaries.

H_raw(t) = z_real − 0.3·z_drift − 0.3·z_disagree; H(t) = sigmoid(H_raw) ∈ [0,1]; G(t) = clip((H(t)-0.3)/(0.7-0.3), 0, 1).

**Deployment rule**: Active(t) = 1[G(t) ≥ 0.2]. Below threshold, hold cash (zero exposure).

**Gate performance (Table 11, extended)**:

| Predictor | AUROC (ALL) | AUROC (FINAL) |
|-----------|-------------|----------------|
| H(t) (combined) | 0.721 | 0.750 |
| G(t) (gate) | 0.710 | 0.743 |
| H_real-only | 0.715 | — |
| Market volatility (21d) | 0.596 | 0.569 |
| Mean stock volatility | 0.590 | 0.460 |
| VIX percentile | 0.449 | 0.504 |

At G(t) ≥ 0.2: 80.0% precision, 64.0% recall, 47.2% abstention rate. Confusion matrix: 937 true positives, 234 false positives, 527 false negatives, 520 true negatives (2,218 evaluated dates, 59 early warm-up dates dropped). Bucket monotonicity perfect (Spearman ρ = 1.0): lowest-G bucket mean RankIC = -0.011 (51.2% bad days); highest-G bucket mean RankIC = +0.153 (11.5% bad days) — a 4.5x reduction in failure frequency.

**Why the gate's advantage widens in FINAL**: the FINAL regime failure is more extreme (20d mean RankIC 0.010 vs 0.072 in DEV), giving wider class separation for a moderate-AUROC classifier. Also, H_real's structural 20-day lag means the EWMA converges to a low state before the worst months and stays there through the persistent 2024 rotation (Mar-Jul), unlike VIX/vol proxies which track contemporaneous conditions poorly correlated with this specific model's failure.

**Multi-crisis validation (Table 13)**: tested across five crisis episodes (COVID recovery 2020, meme mania 2021, inflation shock 2022, late-2023 rate hiking, AI rotation 2024) and three calm periods (2018, 2019, 2023 H1), using frozen walk-forward outputs, no retraining. **G(t) scores 7/8 correct verdicts; VIX-percentile gate scores 5/8.** VIX's three false alarms (2019, 2023 H1, 2023 H2) all occur during the model's strongest periods (IC = +0.034 to +0.122) — VIX was elevated for reasons unrelated to this model's efficacy. G(t)'s single failure: 2021 meme mania (mean G = 0.210, barely above threshold; 73% abstention; mildly negative IC of -0.040) — the regime shift was too brief/mild for the lagged EWMA to fully react.

**Per-stock ê cannot substitute for the gate**: aggregated per-stock uncertainty (median, 90th percentile, IQR of ê) achieves AUROC ≈ 0.50 for regime-failure detection — no better than random. Per-stock uncertainty and strategy-level regime risk are orthogonal failure modes requiring independent signals.

### Level 2: Position-level epistemic tail-risk cap (ê-Cap)

Within active trading days, rather than continuous inverse-ê sizing, apply a discrete percentile-based cap: reduce weight by (1-κ) for stocks above the P_p percentile of ê_PIT on that date. Primary calibration: p=85 (cap top 15%), κ=0.70 (30% weight reduction). Alternative tested: p=90, κ=0.50 (also improves over Gate+Vol: ALL 0.855, FINAL -0.002).

This is a "soft abstention" at the position level — it targets the *intersection* of high uncertainty and portfolio membership (extreme-rank stocks in the top/bottom-10 that are also in ê's extreme tail), leaving 85% of positions untouched and preserving score-tail convexity.

**Deployability ablation (Table 10)**: Gate+Vol+ê-Cap under oracle ê vs PIT-safe ê_PIT (W=60) is *identical* — Sharpe 1.864 (ALL), 1.915 (DEV), 0.906 (FINAL), -6.7% crisis MaxDD, both variants. This is a structural guarantee, not a coincidence: a(t) enters ê(x)=max(0, g(x)-a(t)) as a date-level constant, so within a date it preserves g(x)'s ordering and selects the identical capped tail regardless of oracle vs PIT-safe a(t). The within-date Spearman correlation ρ(ê_oracle, ê_PIT) = 1.0 for every date in the sample.

**Combined system (best policy)**: (1) strategy gate — hold cash if G(t) < 0.2; (2) volatility sizing when active; (3) 30% weight cut for the top-15% ê_PIT tail. ALL Sharpe 1.877, FINAL Sharpe 0.925 (vs 0.375 for Gate+Vol alone) — a **2.47x FINAL Sharpe improvement** from adding the tail-risk cap.

**Binary vs continuous gating**: binary abstention outperforms continuous throttling (w(t) ∝ G(t)) because continuous scaling destroys "recovery convexity" — the strategy stays partially off during post-regime-failure rebounds, compressing realized Sharpe. Kill baseline K4 (continuous trailing-IC sizing, no binary gate) achieves Sharpe 0.754, matching Gate+Raw (0.758) — confirms the gate's value is in the discrete trade/abstain decision, not continuous exposure modulation.

**Cross-model confirmation (RA2)**: RA2 ê-sizing also underperforms RA2 raw (ALL Sharpe 0.430 vs 0.622); once G(t) is applied, RA2 and LGB converge (gated-vol-sized FINAL Sharpe 0.958 RA2 vs 1.017 LGB) — the regime gate is the dominant value driver for both base models.

---

## Conformal Prediction Intervals (Supplementary)

DEUP-normalized nonconformity scores s_DEUP(x) = ℓ(x) / max(ê_PIT(x), ε), compared against raw s_raw(x) = ℓ(x) and volatility-normalized s_vol(x) = ℓ(x)/vol_20d(x). Split conformal, 60-day rolling calibration window, 90% nominal coverage.

**Table 14 — conditional coverage by ê tercile (20d, 90% nominal):**

| Normalizer | Low-ê | Mid-ê | High-ê | Spread | Mean width |
|-----------|-------|-------|--------|--------|-----------|
| Raw (none) | 0.982 | 0.938 | 0.781 | 20.1 pp | 0.674 |
| DEUP / ê_oracle | 0.895 | 0.904 | 0.898 | 0.9 pp | 0.647 |
| DEUP / ê_PIT (W=60) | 0.921 | 0.897 | 0.879 | 4.2 pp | 0.640 |
| DEUP / ê_PIT (W=252) | 0.924 | 0.897 | 0.878 | 4.6 pp | 0.640 |

Raw conformal over-covers low-uncertainty stocks and severely under-covers high-uncertainty stocks (20.1pp disparity). DEUP-normalized conformal reduces the disparity to 0.9pp under oracle ê and 4.2-4.6pp under deployable PIT-safe ê — a 4.3-21x improvement over raw, while also producing narrower mean interval widths.

---

## Key Concepts and Definitions

**Two distinct deployment decisions**: position-level risk ("which predictions are likely wrong?") vs strategy-level risk ("is the model reliable enough to deploy today?"). The paper's core architectural claim is these require independent signals — one cannot substitute for the other.

**DEUP (Direct Epistemic Uncertainty Prediction)**, per Lahlou et al. (2023): train a secondary model g(x) on held-out residuals to predict the primary model's expected error, sidestepping Bayesian inference. Adapted here from mean-squared-error targets to rank-displacement targets for cross-sectional ranking.

**Structural coupling**: the ranking-specific finding that ê(x) and |score(x)| are strongly positively correlated because extreme cross-sectional ranks mechanically carry both the highest signal conviction and the highest displacement ceiling.

**PIT-safe vs oracle**: within-date *ordering* diagnostics (quintile monotonicity, correlation with rank loss) are valid even under a hindsight floor a_oracle(t), because subtracting a date-level constant doesn't change cross-sectional rank order. But deployment *actions* that depend on the *magnitude* of ê (caps, conformal scaling) require the PIT-safe a_PIT(t) to avoid look-ahead leakage.

**Recovery convexity**: the property that a binary-gated strategy fully re-engages immediately when conditions improve, vs a continuously-throttled strategy that partially suppresses upside during rebounds.

---

## Related Work Positioning (Table 2)

| Work | Task | UQ method | Action rule | Regime control |
|------|------|-----------|--------------|-----------------|
| Spears et al. (2021) | Futures return | Bayesian NN posterior | Multiplicative sizing | Variance threshold |
| Liu et al. (2026) | Return prediction | Rolling residual quantiles | Uncertainty-adj. sorting | None |
| Garlappi et al. (2007) | Portfolio opt. | Ambiguity/model uncertainty | Shrinkage toward safety | None |
| This paper | Cross-sec. ranking | DEUP on rank displacement | Tail-risk cap (ê-Cap) | Binary gate G(t) |

---

## Limitations (author-stated)

- Single thematic universe (≤100 AI-exposed U.S. equities); narrow by institutional standards (500-3,000 names typical); coupling magnitude (ρ=0.616) may not generalize to broader, less sector-concentrated universes.
- G(t) validated only against AI-thematic-rotation-type failures; untested against other failure modes (liquidity crises, factor crowding).
- Sensitivity to aleatoric baseline choice: headline cap policy is robust to oracle vs PIT-safe a(t) in this setting, but the *scale* of ê still depends on window length W, quantile level, and rolling vs expanding construction — matters for conformal scaling and fixed-threshold policies in other universes.
- No CRSP-style delisting-return modeling (negligible here: one ADR delisting, 0.05% of rows).
- Structural lag in H_real(t) (EWMA of matured RankIC with τ-day lag) means the gate cannot detect failure until roughly one month after it begins; 2024 losses in March were not avoided, only later months.
- Deployment policies evaluated primarily at τ=20d; at 60d most ê values collapse to 0 under the per-stock quantile-regression aleatoric baseline (P85 cap wouldn't transfer); at 90d the base signal inverts in FINAL, an open question whether any policy salvages it.
- H_disagree requires a second base model (RA2); with only one production model, falls back to a weaker score-dispersion proxy.

---

## Citations of Note

- Lahlou et al. (2023): DEUP — foundational method this paper adapts to ranking.
- Kotelevskii and Panov (2025): generalized risk decomposition (Bayes risk = aleatoric, excess risk = epistemic) framing used to justify the a(t)/g(x) split.
- Spears et al. (2021), Liu et al. (2026): inverse-uncertainty sizing in return-prediction settings — the paradigm this paper shows fails to transfer to ranking.
- Garlappi et al. (2007): ambiguity-aware shrinkage-toward-safety portfolio theory.
- Chaudhuri and Lopez-Paz (2023): selective prediction — theoretical basis for the ê-Cap as "soft abstention."
- Nystrup et al. (2017): regime-switching literature; supports the finding that excessively frequent regime-switching hurts realized portfolio outcomes (motivates binary over continuous gating).
- Vovk, Gammerman, Shafer (2005); Plassier et al. (2025): conformal prediction and probabilistic conformal motivation for the DEUP-normalized nonconformity scores.
- Hentschel (2025): "contextual alpha" — residualizing uncertainty on signal context; the paper's Gate+Resid-ê variant follows this approach and finds it underperforms the discrete cap.

---

## Provenance Note

All 34 pages (main text, all tables, references) directly read from PDF. No appendices beyond the reference list; the paper has no appendix sections.

---

## See Also

- [[Regime-Trust-Gating]] — the concept page for the strategy-level gate mechanism
- [[Sector-Rotation]] — the failure regime that motivates this paper
- [[zhang2026-benchmarking-deep-ts-equity]] — companion benchmarking paper; its Table 10 regime-conditional SMAA results show a parallel phenomenon (model rankings flip between volatility regimes)
- [[quantitative-finance]] — domain page
