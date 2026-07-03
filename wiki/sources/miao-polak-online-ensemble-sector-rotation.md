---
type: source
title: "Online Ensemble Learning for Sector Rotation: A Gradient-Free Framework"
domain: quantitative-finance
status: complete
created: 2026-07-02
updated: 2026-07-02
tags:
  - source
  - paper
  - quantitative-finance
  - machine-learning
  - ensemble-learning
  - sector-rotation
  - online-learning
related:
  - "[[quantitative-finance]]"
  - "[[Sector-Rotation]]"
  - "[[Online-Ensemble-Learning]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
  - "[[das2026-chronos-multivariate-forecasting]]"
source_type: paper
author: "Jiaju Miao, Paweł Polak (Stony Brook University, Dept. of Applied Mathematics and Statistics)"
date_published: 2025-11-12
url: "https://arxiv.org/abs/2304.09947"
confidence: high
key_claims:
  - "A gradient-free online ensemble (Multiplicative Weights Update Method) combining 16 models by rolling out-of-sample R^2 beats individual models, equal-weight ensembles, and offline-optimized ensembles."
  - "Sector-level returns are more predictable and stable than firm-level returns because sector aggregation cancels idiosyncratic noise while retaining systematic factor exposure."
  - "The average per-period ensemble gain converges almost surely to realized out-of-sample R^2, giving an interpretable, non-asymptotic (Chebyshev-based) high-probability regret bound decaying at rate tau^-2."
  - "The resulting Top-5 sector rotation strategy delivers Sortino ratios of 1.14 (equal-weighted) / 1.21 (cap-weighted) over 1987-2021, rising to 2.4 / 2.1 during the 2020-2021 COVID period, and survives 5-15bps transaction costs."
---

# Online Ensemble Learning for Sector Rotation: A Gradient-Free Framework

Navigation: [[quantitative-finance]]

---

## Bibliographic Record

| Field | Detail |
|-------|--------|
| Authors | Jiaju Miao, Paweł Polak (Dept. of Applied Mathematics and Statistics, Stony Brook University) |
| Submitted | v2, November 12, 2025 (originally arXiv April 2023) |
| arXiv | [2304.09947](https://arxiv.org/abs/2304.09947) [q-fin.ST] |
| PDF | https://arxiv.org/pdf/2304.09947 |
| Keywords | Ensemble of Models; Machine Learning; Multiplicative Weights Update Method; Online Learning; Regret Minimization, Sector Rotation |
| Source | PDF directly read (all 17 pages, main text, proofs, tables, references) |

---

## Abstract (verbatim)

"We propose a gradient-free online ensemble learning algorithm that dynamically combines forecasts from a heterogeneous set of machine learning models based on their recent predictive performance, measured by out-of-sample R². The ensemble is model-agnostic, requires no gradient access, and is designed for sequential forecasting under nonstationarity. It adaptively reweights 16 constituent models: three linear benchmarks — Ordinary Least Squares (OLS), Principal Component Regression (PCR), and LASSO — and thirteen nonlinear machine learning models, including Random Forests, Gradient-Boosted Regression Trees, and a hierarchy of feedforward neural networks (NN1–NN12). We apply this framework to the sector rotation problem, using sector-level features derived by aggregating firm-specific characteristics. Empirically, we find that sector-level returns are more predictable and stable than individual asset returns, making them well-suited for cross-sectional forecasting. To exploit this structure, our algorithm constructs sector-specific ensembles that assign adaptive weights to constituent models in a rolling-window fashion, guided by their forecast accuracy. Our key theoretical contribution is to bound the online forecast regret directly in terms of realized out-of-sample R², a standard empirical performance metric that here serves as the loss function in the ensemble procedure. This provides a novel and interpretable guarantee: the ensemble performs nearly as well as the best model in hindsight. Empirical results show that the ensemble consistently outperforms individual models, equal-weighted combinations, and traditional offline ensemble methods in both predictive accuracy and economic value. When used to construct sector rotation portfolios, it delivers substantial improvements in risk-adjusted returns, maintains robustness across macroeconomic regimes, and demonstrates resilience during periods of financial stress, including the COVID-19 crisis."

---

## Section Structure

1. Introduction
2. Modeling Sector Returns
3. Performance Driven Ensemble of Models (theory: gain function, Lemma 1-3, regret bounds)
4. Empirical Study
5. Conclusion
References [1]-[33]

---

## Sector Universe and Data

**Sector definition**: First two digits of Standard Industrial Classification (SIC) codes. Chosen over GICS/ICB because SIC gives consistent historical coverage across the full sample, aligns with regulatory datasets (SEC filings), and avoids classification drift / backfill bias from periodic GICS revisions over long horizons. Results in **50 sectors**.

**Return construction** (Eq. 1): for each sector, two return measures computed —
- Equally weighted: simple average of constituent stock returns.
- Capitalization weighted: market-cap-weighted average of constituent stock returns.

**Raw data**: Monthly CRSP stock returns, **March 1957 to December 2021**.

**Firm-level features**: 94 firm-level predictive characteristics (following Gu, Kelly & Xiu 2020 [12]) spanning past returns, profitability, valuation, and trading frictions, for roughly 9,000 firms across 60 raw sectors. Of the 94, 61 update annually, 13 quarterly, 20 monthly. Standard publication lags applied to avoid look-ahead bias: 1 month (monthly vars), 4 months (quarterly), 6 months (annual) — i.e., returns t→t+1 are forecast using characteristics disclosed at t-1, t-4, t-6 respectively.

**Dimensionality reduction — Probabilistic PCA (PPCA)**: Including all raw firm-level variables would yield ~14,100 predictors per sector (untenable given sample size/overfitting risk). PPCA is applied separately to each characteristic × sector rolling window; only the **first principal component per characteristic** is retained as the sector-level predictor (empirically, using more than PC1 degraded predictive performance — likely overfitting/noise amplification). This produces the sector-level feature vector z_{i,t} ∈ R^K, one component per original characteristic.

**Train/test split**: 30-year training window (1957-1986); 35-year out-of-sample test period (**1987-2021**). Models refitted annually (not monthly) — training set expands by one year, forecasts generated for the following 12 months, ~360-observation rolling training window, 5-fold CV for hyperparameter tuning within each window.

**Model pruning**: OLS and shallow neural nets (fewer than six layers) are excluded from the final ensemble reporting because they systematically underperform (often negative out-of-sample R²), dominated by regularized methods (LASSO) and deeper architectures.

---

## The 16-Model Ensemble Composition

| Family | Models | Count |
|--------|--------|-------|
| Linear benchmarks | OLS, Principal Component Regression (PCR), LASSO | 3 |
| Tree-based | Random Forests (RF), Gradient-Boosted Regression Trees (GBRT) | 2 |
| Feedforward neural networks | NN1 through NN12 (NNk = k hidden layers, ReLU activation) | 11 |

Total: 3 + 2 + 11 = 16 constituent models forecasting sector-level excess returns r_{i,t+1} from sector-level features z_{i,t}.

- OLS: g(z) = z^T θ, minimize residual sum of squares.
- PCR: project z onto lower-dimensional space via PCA before fitting linear model.
- LASSO: OLS objective + ℓ1 penalty λΣ|θ_j|, induces sparsity, improves high-dimensional robustness.
- RF: average over decorrelated bootstrap-trained decision trees.
- GBRT: additive trees fit sequentially to minimize squared loss with shrinkage parameter λ.
- NN1-NN12: increasing depth feedforward nets, ReLU activation, final layer g(z;w) = x^{(L-1)T} w^{(L-1)}.

---

## Theoretical Core: Gradient-Free Online Ensemble (MWUM)

**Baseline 1 — Simple Average ensemble**: uniform weights across all 16 models.

**Baseline 2 — Offline Ensemble** (Lemma 1): closed-form optimal *static* weights p* solving a constrained quadratic program that maximizes out-of-sample R² over the full history:

p̂* = arg max_{p ∈ R^L_+, 1^T p = 1} { 1 - [ (1/τ)Σ(r_t - r̂_t^T p)² ] / [ (1/τ)Σ r_t² ] }

Closed form: p̂* = p̂_OLS - (R̂^T R̂)^{-1} 1_L · (1_L^T p̂_OLS - 1) / (1_L^T (R̂^T R̂)^{-1} 1_L), analogous to Breiman's stacked regression. Critical limitation: static weights assume model relevance is constant — violated under regime shifts; also ignores exploration (may overweight historically dominant models, underuse complementary/diverse ones).

**Baseline 3 — Exploitation Ensemble**: online, dynamic weights, but uses only the exploitation term of the gain function (below), not the full gain.

**Proposed — Online Ensemble via Multiplicative Weights Update Method (MWUM)**:

Weight update: w^{(t+1)} = w^{(t)} (1 + η m^{(t)}), where η is the learning rate and m^{(t)} the gain vector, followed by normalization p^{(t)} = w^{(t)}/Σw^{(t)}_l. No retraining, no gradients, no future data — purely sequential using only past forecast errors.

**Gain function** (Eq. 6), decomposed into exploitation and exploration terms:

m^{(t)}(p^{(t)}) = [1_L − (r_t 1_L − r̂_t)² / σ̂_t²]  −  [R̃_t 1_L / σ̂_t²]

- **Exploitation term**: rewards a model when its squared forecast error is smaller than the estimated return-variance benchmark σ̂_t² (a bootstrap-based rolling estimator); penalizes errors larger than that benchmark.
- **Exploration term**: compares each model's prediction against the current weighted ensemble forecast r̃_t = r̂_t^T p^(t). If a low-weight model's prediction moves in the *same* direction as an already-dominant model, it is penalized as redundant; if it moves in the *opposite* direction (complementary information) while the exploitation term shows small error, its weight is increased. This implements a bias-variance-diversity trade-off (citing Wood et al. 2023 on ensemble diversity theory).

**Adaptive learning rate**: in the 35-year backtest, η is chosen each rebalancing period from a predefined grid, selecting the value that achieved the best out-of-sample performance over the prior 12 months — implementable without look-ahead bias.

### Regret / Convergence Results

**Lemma 2 (asymptotic equivalence)**: |R²_oos(τ) − (1/τ)Σ_t m^{(t)}(p^{(t)})^T p^{(t)}| → 0 almost surely as τ → ∞, under mild regularity conditions (Assumption 1: finite second moment/ergodicity, consistent variance estimator, bounded gain). I.e., the average realized gain converges to the realized out-of-sample R² — this validates using the gain function itself as a tractable, gradient-free surrogate objective for the online weight update.

**Lemma 3 (non-asymptotic high-probability bound)**: assuming r_t ~ iid N(0, σ_r²), for any weight sequence and any ε > 0:

P(|R²_oos(τ) − (1/τ)Σ m^{(t)T}p^{(t)}| > ε) ≤ 2(1+L) / [ε σ_r τ² √(8/τ² − 6/τ + 1)]

Derived via Chebyshev + Young's inequality; the bound is **non-asymptotic (finite τ)** and shows the deviation probability decays at rate **τ^-2**, confirming that the ensemble's realized average gain concentrates tightly around out-of-sample R² even in finite samples — this is the paper's "novel and interpretable guarantee: performs nearly as well as the best model in hindsight."

---

## Key Empirical Results

### Table 1: Average out-of-sample R² across sectors (selected models + all ensembles)

| | PCR | LASSO | GBRT | NN6 | NN7 | NN8 | NN9 | NN10 | NN11 | NN12 | Simple Avg | Offline Ens. | Exploitation Ens. | **Online Ens.** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Equal-weighted sector return | -0.62 | 0.95 | 0.56 | -0.06 | 0.83 | 0.53 | 0.24 | 0.77 | 0.62 | 0.75 | 0.90 | 0.93 | 0.99 | **1.19** |
| Cap-weighted sector return | 0.38 | 1.11 | 0.89 | 0.35 | 0.36 | 1.06 | 0.89 | 0.95 | 0.62 | 0.75 | 1.07 | 1.08 | 1.09 | **1.12** |

LASSO has the highest individual-model average R²_oos, followed by deeper NN architectures. The full **Online Ensemble beats every individual model and every other ensemble benchmark** on both weighting schemes. Improvement over the Exploitation Ensemble (which drops the exploration term) isolates the value of the diversity-promoting term: 1.19 vs. 0.99 (equal-weighted).

### Table 2: Sector rotation portfolio performance, quintile sort on predicted returns (Bottom 5 / 41-55 / 21-40 / 6-20 / Top 5), vs. S&P 500 and 1/N benchmark

**Panel I (full sample, 1987-2021), equally-weighted sector returns:**

| Statistic | S&P 500 | 1/N | Bottom 5 | Top 5 | Top-Bottom |
|---|---|---|---|---|---|
| Annual Return | 8.89% | 10.48% | 6.61% | 14.15% | — |
| Annual Volatility | 15.04% | 19.71% | 23.04% | 15.68% | — |
| Annual Sharpe | 0.5912 | 0.5317 | 0.2869 | 0.6570 | — |
| Max Drawdown | 52.56% | 62.19% | 66.39% | 52.33% | — |
| Annual Sortino | 0.9487 | 0.9114 | 0.5903 | 1.1465 | — |

Net-of-cost Top 5 Sharpe at 5/10/15 bps: 0.6357 / 0.6143 / 0.5931 (equal-weighted). Monotonic relationship: annualized returns rise from 6.61% (Bottom 5) to 14.15% (Top 5) across the full sample.

**Panel II (COVID period, 2020-2021), equally-weighted:**

| Statistic | S&P 500 | Bottom 5 | Top 5 |
|---|---|---|---|
| Annual Return | 21.62% | 19.15% | 50.40% |
| Annual Sharpe | 1.1067 | 0.5287 | 1.5163 |
| Annual Sortino | 1.8400 | 1.0014 | 2.4006 |

During COVID, annualized return rises from 19.15% (Bottom 5) to 50.40% (Top 5); Sortino ratio for Top 5 climbs to 2.40 (equal-weighted) / 2.10 (cap-weighted) — both above the full-sample values, i.e. the strategy performs *better*, not worse, during acute regime stress. Net-of-cost Sortino at 5/10/15bps in COVID period: 2.36/2.33/2.29 (still far above benchmarks).

Capital-weighted results (Panel I.B / II.B) show the same monotonic pattern and confirm the strategy is not reliant on small-cap/illiquid names — cap-weighted Top 5 Sortino is 1.15 (full sample) and 2.10 (COVID).

### Table 3: Risk-adjusted alpha of quintile portfolios (monthly, 1987-2021), CAPM / Fama-French 3-factor / Carhart 4-factor

Equally-weighted, Newey-West t-stats in parentheses:

| Portfolio | Excess return | CAPM alpha | 3F alpha | 4F alpha |
|---|---|---|---|---|
| Top 5 | 0.0130*** (3.96) | 0.0303*** (3.03) | 0.0297*** (2.97) | 0.0305*** (3.05) |
| Top−Bottom | 0.0079** (2.47) | 0.0081*** (4.13) | 0.0088*** (4.59) | 0.0068** (4.05) |

Alphas are positive and statistically significant for "6-20" and "Top 5" portfolios, often at the 1% level, and remain significant (though shrinking) as more risk factors are added — indicating the ensemble captures incremental predictability beyond size/value/momentum. The market-neutral Top-5-minus-Bottom-5 long-short strategy delivers alphas comparable to the long-only Top 5 strategy (cap-weighted Top-Bottom 4F alpha: 0.0039**, t=2.10).

---

## Regime Robustness (COVID-19)

- The S&P 500 fell 34% during the Feb-Mar 2020 crash; technology, healthcare, and consumer staples sectors rebounded quickly while energy, industrials, and financials lagged.
- The online ensemble captured this rotation: the "Top 5" portfolio's cumulative outperformance versus the market grows steadily and especially accelerates during the COVID period (Figure 2), rather than being arbitraged away — evidence the edge persisted rather than decaying with market adaptation.
- Drawdown behavior: Top 5 exhibits smaller peak-to-trough declines and faster recovery than the market during major historical downturns (dot-com 2002, GFC 2008), suggesting downside protection alongside outperformance.

---

## Citations of Note

- Gu, Kelly, Xiu (2020) [12]: "Empirical Asset Pricing via Machine Learning" — source of the 94 firm-level characteristics and PPCA/feature-engineering approach; this paper's ensemble R²_oos values exceed [12]'s individual-stock-level values, attributed to sector-level aggregation improving signal-to-noise.
- Karatas & Hirsa (2021) [13]: "Two-Stage Sector Rotation Methodology Using Machine Learning and Deep Learning Techniques" — cited as the traditional macro-indicator-driven sector rotation approach this paper's firm-characteristic-aggregation approach deliberately departs from. See [[karatas2021-two-stage-sector-rotation]].
- Wood, Mu, Webb, Reeve, Lujan, Brown (2023) [33]: "A Unified Theory of Diversity in Ensemble Learning" — theoretical basis for the exploration/diversity term in the gain function.
- Breiman (1996) [6]: Stacked Regressions — analog for the offline ensemble baseline.
- Arora, Hazan, Kale (2005) [3]; Alabdulmohsin (2018) [1]; Bailey & Piliouras (2018) [5]: Multiplicative Weights Update Method foundations (MWUM traces to AdaBoost / online learning / game theory).
- Tipping & Bishop (1999) [28]: Probabilistic PCA.
- Sharpe (1964) [27]; Fama-French (1993) [11]; Carhart (1997) [8]: factor models used for alpha decomposition.
- Hansen, Lunde, Nason: not present in this paper (contrast with [[zhang2026-benchmarking-deep-ts-equity]], which uses Model Confidence Set methodology from this reference).

---

## Provenance Note

All 17 pages of the PDF directly read in full (introduction, sector-return modeling, ensemble theory with all three lemma proofs, empirical study, conclusion, references). No appendices in this version of the paper beyond the reference list.

---

## See Also

- [[quantitative-finance]] — domain page
- [[Sector-Rotation]] — concept page: sector rotation as a strategy class
- [[Online-Ensemble-Learning]] — concept page: gradient-free online model combination theory
- [[zhang2026-benchmarking-deep-ts-equity]] — contrasting benchmark: firm-level (not sector-level) deep time-series architectures on CRSP daily data, using SMAA/regret rather than MWUM
- [[das2026-chronos-multivariate-forecasting]] — foundation-model forecasting approach, different paradigm from this paper's supervised-ensemble approach
