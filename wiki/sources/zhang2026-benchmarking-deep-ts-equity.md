---
type: source
title: "Benchmarking Deep Time Series Models for Equity Portfolios"
domain: quantitative-finance
status: complete
created: 2026-06-24
updated: 2026-06-24
tags:
  - source
  - paper
  - quantitative-finance
  - machine-learning
  - time-series
  - portfolio-optimization
related:
  - "[[quantitative-finance]]"
---

# Benchmarking Deep Time Series Models for Equity Portfolios

Navigation: [[quantitative-finance]]

---

## Bibliographic Record

| Field | Detail |
|-------|--------|
| Authors | Aoxin Zhang (Beijing Normal U.), Yuhan Cheng (Shandong U., corresponding), Kwanting Leung (Peking U. NSD) |
| Submitted | June 8, 2026 |
| arXiv | [2606.09420](https://arxiv.org/abs/2606.09420) [math.OC, q-fin.PM] |
| PDF | https://arxiv.org/pdf/2606.09420 |
| Keywords | deep time-series benchmarking; equity portfolios; multi-criteria decision analysis; preference uncertainty; stochastic acceptability analysis; portfolio implementation |
| Source | PDF directly read (pp. 1-20, all tables and figures) |

---

## Abstract (verbatim)

"Benchmarking forecasting architectures for daily equity portfolios is not just a prediction exercise. It also asks which model remains usable after preferences, costs, and portfolio constraints are imposed. We build a CRSP daily-stock benchmark for 15 deep and statistical time-series architectures over 2018-2024. The protocol combines common-window decile portfolios, stochastic multi-criteria acceptability analysis, a deployment-adjusted acceptability index, and a constrained quadratic portfolio layer with capacity, beta, industry, risk, leverage, and turnover controls. The index starts from the SMAA rank-acceptability distribution and downweights models whose criteria-level wins produce high portfolio regret; its Gibbs form is characterized as an entropic update from the SMAA prior. Empirically, no architecture dominates the raw benchmark: TransEnc-8 has the largest rank-1 acceptability, 0.352, and no model exceeds about 0.36. Rankings vary with preferences, market state, feature universe, and transaction costs. In the promoted five-model constrained-portfolio comparison, TransEnc-8 is selected throughout, while return-oriented raw rankings can favor TS-RIDGE. Broad-universe decile signals can survive costs, but the baseline constrained-QP net Sharpe at 20 bps is negative for every promoted model. The benchmark supports model selection and diagnosis rather than a standalone trading-strategy claim."

---

## Section Structure (7 sections)

1. Introduction
2. Related Literature
3. Methodology: Acceptability, Regret, and Allocation
4. Data and Benchmark Design
5. Common-Window Results and Inference
6. Robust Multi-Criteria Model Selection
7. Constrained Portfolio Construction
- Appendices A-E (proofs, feature definitions, supplementary analysis, Kendall association, registry keys)

---

## Architecture Universe (15 models, Table 2)

| Family | Models | Count | Role |
|--------|--------|-------|------|
| Linear / statistical | TS-RIDGE, TS-OLS, AR1-GARCH11 | 3 | Shrinkage anchor, no-shrinkage comparator, classical baseline |
| Recurrent networks | LSTM, GRU, RNN | 3 | LSTM, GRU, tanh-RNN vs. linear benchmark |
| Transformer / patch / residual-stack | TransEnc-8, TransEnc-10, PatchTST-8, PatchTST-16, NBEATS | 5 | Plain transformer encoders, PatchTST variants, N-BEATS residual stack |
| Mixer / graph / ensemble | TSMixer-8, TSMixer-10, MoE-MLP, GraphRNN | 4 | Residual mixer, mixture-of-experts, graph-recurrent |

Note: source registry keys (script labels) differ from manuscript labels; see Appendix E. Models are canonical implementations, not named frontier systems (no Informer, Autoformer, FEDformer).

**Five promoted models** (fixed follow-through set for constrained-portfolio analysis): TS-RIDGE, LSTM, TransEnc-8, TransEnc-10, TS-OLS. Selected because all have full 1,197-date coverage, positive common-window gross Sharpe, and positive decile net Sharpe at 20 bps (except TS-OLS, added as no-shrinkage comparator).

---

## Data and Benchmark Design (Section 4)

**Raw panel**: CRSP daily common-stock, 2018-2024. After filters: 4,862,011 stock-date rows, 5,451 assets, 1,761 dates.

**Feature set**: 24 usable predictors in price-path, activity, size, beta, and market-relative blocks. Feature engineering produces 4,551,500 rolling samples.

**Shared evaluation window**: 1,197 prediction dates, 2020-03-30 to 2024-12-30.

**Confirmatory window**: 2021-01-04 to 2024-12-30 (1,004 trading days, 4,410 assets, 2,777,135 stock-date observations).

**Portfolio rule** (Table 1, Panel B): Equal-weight long-short decile portfolio formed daily from model forecasts. Same shared intersection for all models. Inference: moving-block bootstrap, 20-trading-day blocks, 10,000 resamples. Multiple testing: BH-FDR and Bonferroni adjustments; SPA screen in common-window discussion. Trading costs: drift-adjusted one-way turnover reconstructed from holdings; net Sharpe uses 10, 20, and 50 bps single-side costs. Risk adjustment: Fama-French five-factor regressions, Newey-West 20-day lag.

Three nested signal universes: F1 (price-path and quote-geometry), F2 (adds turnover, log dollar volume, log number of trades), F3 (adds market cap, rolling beta, market-relative excess-return transforms).

---

## Formal Definitions (Section 3)

**Criteria vector** (Definition 1): Each model m is represented by

V_m = (SR_gross, SR_net20, SR_vw, |t_FF5|, -TO, -MDD, 1 - p_m)

where SR = Sharpe ratio, TO = turnover, MDD = maximum drawdown, p_m = bootstrap loss proxy. Seven criteria, all oriented so larger is better.

**Rank acceptability** (Definition 2): Criteria uncertainty via moving-block resamples b; preference uncertainty via weight vectors q on the seven-criterion simplex. For each (b, q): U_m = sum_k q_k V_mk; R_m = rank(U_m); RA_m(r) = Pr{R_m = r}. The rank-1 acceptability index is the share of sampling and preference states where model m is first.

**Deployment regret** (Definition 3): R_m^d = max_{l in M_d} J_l^d - J_m^d, where J_m^d is the realized net Sharpe under downstream design d. Positive regret means the criteria-selected model loses realized net Sharpe relative to the best model after the portfolio rule is applied.

**Deployment-adjusted acceptability** (Definition 4): DA_m^(1,d) = [RA_m(1) exp{-gamma_d R_m^d}] / [sum_{l} RA_l(1) exp{-gamma_d R_l^d}]. Temperature tau_d = max(sd_0(R_m^d), 1); baseline design gives tau_d ~= 1.170. As gamma_d -> 0, DA_m converges to normalized SMAA rank-1 acceptability.

**Proposition 1 (entropic characterization)**: DA^(1,d) is the unique solution to min_{p in Delta(S_d)} [sum_m p_m R_m^d + tau_d KL(p || q)], where q_m = RA_m(1) / sum RA_l(1) is the normalized SMAA prior. The temperature trades off minimizing expected deployment regret against staying close to the preference-robust SMAA prior.

**Problem 2 (daily constrained portfolio)**: max_w w^T s_t^(m) - lambda_tc ||w - w_{t-1}||_1 - lambda_risk w^T D_t w, subject to dollar neutrality, leverage ||w||_1 <= 2, single-name capacity |w_i| <= 0.01 DV_i/AUM, beta neutrality |w^T beta| <= 0.05, industry net exposure <= 0.02. Scores centered and scaled cross-sectionally before entering optimizer. AUM = 100M; net return r_t^net = r_t^gross - 0.002 TO_t (20 bps); 50 bps stress uses 0.005 TO_t.

**Proposition 4 (turnover-weight alignment)**: On a one-dimensional turnover slice, ranking by SMAA preference utility U_m(u) is equivalent to ranking by portfolio turnover penalty Pi_m(lambda(u)) under the monotone map lambda(u) = kappa * u / (1 - u). The crossover between any pair i, j with a_i > a_j and tau_i > tau_j occurs at u*_ij = (a_i - a_j) / [(a_i - a_j) + kappa(tau_i - tau_j)].

---

## Key Results Tables

### Table 3: Master common-window benchmark (sorted by gross Sharpe, 1,197 dates)

| Model | Family | Ann.ret | Sharpe | Net20 SR | Turn. | VW SR | FF5 alpha t |
|-------|--------|---------|--------|----------|-------|-------|-------------|
| TS-RIDGE | Linear shrinkage | 42.9% | 3.88 | 0.60 | 7.95 | 42.4% | 7.79 |
| TS-OLS | Linear baseline | 30.7% | 2.48 | -2.32 | 1.18 | 30.4% | 6.33 |
| LSTM | Recurrent | 21.7% | 0.98 | 0.17 | 1.21 | 21.3% | 2.25 |
| TransEnc-8 | Transformer | 15.5% | 0.71 | 0.48 | 0.66 | 15.0% | 1.62 |
| TransEnc-10 | Transformer | 19.4% | 0.61 | 0.35 | 0.19 | 14.8% | 1.40 |
| PatchTST-8 | PatchTST | 8.4% | 0.49 | -0.09 | 0.88 | 8.4% | 1.45 |
| GRU | Recurrent | 5.2% | 0.28 | -0.55 | 0.76 | 4.2% | 0.47 |
| TSMixer-10 | Mixer | 4.6% | 0.19 | -0.65 | 0.15 | 4.1% | 0.41 |
| NBEATS | MLP/NBEATS | 1.1% | 0.06 | -1.95 | 0.85 | 0.9% | 0.10 |
| TSMixer-8 | Mixer | -2.9% | -0.12 | -0.92 | 0.25 | -2.9% | -0.26 |
| MoE-MLP | MoE-MLP | -9.8% | -0.45 | -1.61 | 0.50 | -9.9% | -1.11 |
| RNN | Recurrent | -9.2% | -0.49 | -2.53 | 0.75 | -9.1% | -1.23 |
| PatchTST-16 | PatchTST | -25.3% | -1.48 | -1.84 | 0.18 | -24.8% | -2.91 |
| AR1-GARCH11 | Statistical | -21.5% | -1.48 | -5.82 | 1.25 | -21.6% | -3.45 |
| GraphRNN | Graph/recurrent | -39.3% | -1.56 | -2.00 | 0.22 | -39.1% | -3.58 |

p+ values: TS-RIDGE < 0.001, TS-OLS < 0.001; all others 0.013 to 0.999.

### Table 5: Model Confidence Set (MCS)

| Return definition | Confidence | Models retained |
|-------------------|-----------|----------------|
| Gross Sharpe | 90% | TS-RIDGE; LSTM; TransEnc-8; TransEnc-10; GRU; TSMixer-10; TSMixer-8 |
| Gross Sharpe | 95% | same seven |
| Net Sharpe, 20 bps | 90% | LSTM; TransEnc-8; TransEnc-10 |
| Net Sharpe, 20 bps | 95% | LSTM; TransEnc-8; TransEnc-10; PatchTST-8; TSMixer-8 |

TS-RIDGE exits net MCS because high daily turnover (7.95) erodes cost-adjusted performance.

### Table 6: SMAA rank acceptability summary (10,000 resamples, 10,000 Dirichlet draws)

| Model | Rank-1 prob. | Top-3 prob. | Most likely rank |
|-------|-------------|-------------|-----------------|
| TransEnc-8 | 0.352 | 0.692 | 1 |
| LSTM | 0.168 | 0.692 | 2 |
| TransEnc-10 | 0.022 | 0.554 | 3 |
| PatchTST-16 | 0.172 | 0.307 | 1 |
| TS-RIDGE | 0.199 | 0.293 | 1 |
| PatchTST-8 | 0.069 | 0.194 | 5 |
| GraphRNN | 0.007 | 0.170 | 6 |
| AR1-GARCH11 | 0.011 | 0.077 | 14 |
| MoE-MLP | 0.000 | 0.008 | 11 |
| RNN | 0.000 | 0.007 | 12 |

Note: PatchTST-16 receives 0.172 rank-1 share despite negative gross Sharpe (-1.33) because low turnover and lighter friction scores dominate when preferences move toward implementation criteria. This is expected SMAA behavior, not a return claim.

### Table 7: SMAA rank-1 acceptability bands and modal ranks

| Model | Rank-1 RA | Band lo | Band hi | Modal rank | Modal RA |
|-------|-----------|---------|---------|------------|----------|
| TransEnc-8 | 0.352 | 0.343 | 0.362 | 1 | 0.352 |
| TS-RIDGE | 0.199 | 0.191 | 0.207 | 1 | 0.199 |
| PatchTST-16 | 0.172 | 0.165 | 0.179 | 1 | 0.172 |
| LSTM | 0.168 | 0.161 | 0.175 | 2 | 0.368 |
| PatchTST-8 | 0.069 | 0.064 | 0.074 | 5 | 0.256 |
| TransEnc-10 | 0.022 | 0.019 | 0.024 | 3 | 0.416 |
| AR1-GARCH11 | 0.011 | 0.009 | 0.013 | 14 | 0.370 |
| GraphRNN | 0.007 | 0.005 | 0.009 | 6 | 0.197 |

Finite-sample precision check uses 50,000 preference draws as convergence diagnostic.

### Table 9: Annualized Sharpe ratios at transaction cost levels

| Model | 0 bps | 10 bps | 20 bps | 30 bps | 50 bps |
|-------|-------|--------|--------|--------|--------|
| TS-RIDGE | 3.88 | 2.23 | 0.60 | -1.04 | -4.30 |
| LSTM | 0.98 | 0.79 | 0.60 | 0.41 | 0.03 |
| TransEnc-8 | 0.71 | 0.60 | 0.48 | 0.36 | 0.13 |
| TransEnc-10 | 0.61 | 0.48 | 0.35 | 0.22 | -0.04 |
| TS-OLS | 2.48 | 0.08 | -2.32 | -4.72 | -9.49 |

Crossover: TS-RIDGE leads at 0-10 bps; LSTM and TS-RIDGE tied at 20 bps; LSTM leads at 30 bps; TransEnc-8 leads at 50 bps.

### Table 10: Regime-conditional SMAA rank-1 acceptability

| Model | Rank-1 high-vol | Rank-1 low-vol | Difference | Top-3 high-vol | Top-3 low-vol |
|-------|----------------|----------------|------------|----------------|---------------|
| LSTM | 0.470 | 0.009 | 0.461 | 0.758 | 0.488 |
| TS-RIDGE | 0.198 | 0.144 | 0.054 | 0.332 | 0.255 |
| TransEnc-8 | 0.089 | 0.337 | -0.248 | 0.672 | 0.724 |
| TransEnc-10 | 0.006 | 0.230 | -0.224 | 0.428 | 0.811 |
| PatchTST-16 | 0.080 | 0.250 | -0.170 | 0.225 | 0.373 |

LSTM dominates in high-volatility; TransEnc-8 and TransEnc-10 dominate in low-volatility.

### Table 12: Constrained portfolio (net Sharpe, 20 bps, baseline design)

All five promoted models have negative net Sharpe under constrained-QP:

| Model | Net SR | Ann.return | Avg.turnover | Max DD |
|-------|--------|-----------|--------------|--------|
| TransEnc-8 | -0.76 | -0.37% | 0.93 | -0.93 |
| TransEnc-10 | -1.18 | -0.47% | 0.95 | -0.95 |
| LSTM | -1.25 | -0.53% | 0.99 | -0.95 |
| TS-RIDGE | -2.37 | -1.11% | 2.04 | -1.00 |
| TS-OLS | -3.99 | -1.72% | 2.76 | -1.00 |

High-turnover-penalty design: same ranking, marginally better. 50 bps stress: TransEnc-8 -2.23, LSTM -2.97, TS-RIDGE -5.57, TS-OLS -8.75.

### Table 15: Deployment regret under constrained-portfolio designs

| Design | Model | Net SR | Regret | Turnover |
|--------|-------|--------|--------|----------|
| Baseline | TransEnc-8 | -0.76 | 0.00 | 0.93 |
| Baseline | TransEnc-10 | -1.18 | 0.41 | 0.95 |
| Baseline | LSTM | -1.25 | 0.49 | 0.99 |
| Baseline | TS-RIDGE | -2.37 | 1.61 | 2.04 |
| Baseline | TS-OLS | -3.99 | 3.23 | 2.76 |

TransEnc-8 regret = 0 across all three designs (baseline, high turnover penalty, 50 bps stress). SMAA and constrained-QP both select TransEnc-8; cross-framework regret is zero under baseline design.

Rank association between raw SMAA expected ranks and constrained-QP ranks: Kendall tau = 0.80, Spearman rho = 0.90, stable across 0-50 bps cost range (Figure 11).

---

## Key Concepts Formally Defined

**Seven criteria**: gross Sharpe, net-20 Sharpe, value-weighted Sharpe, |FF5 alpha t-stat|, minus turnover, minus max drawdown, 1 minus bootstrap loss probability.

**Turnover-weight alignment**: On a one-dimensional turnover slice, SMAA preference weight u and portfolio turnover penalty lambda(u) = kappa * u / (1-u) induce the same ranking (Proposition 4). Explains why SMAA penalizes TS-RIDGE when low-turnover criterion receives weight, and the constrained portfolio confirms that penalty.

**Structured preference priors** (Table 8): Return-oriented prior keeps TS-RIDGE as rank-1 leader (prob. 0.996). Net-performance-oriented prior keeps TS-RIDGE as leader (0.810) but raises TransEnc-8 (0.103) and LSTM (0.075). Statistical-rigor prior keeps TS-RIDGE (0.985).

---

## Citations in Paper

- Lahdelahti et al. [1-3]: original SMAA development
- Xidonas et al. [4]: equity-portfolio decision-support with SMAA
- Elmachtoub/Grigas [5]: smart predict-then-optimize
- Cesa-Bianchi/Lugosi [6]: prediction with expert advice (exponential weights / Gibbs form)
- Bonnans and Shapiro [13]: parametric optimization sensitivity (Proposition 3)
- Topkis [15]: increasing differences / comparative statics (Proposition 4)
- Lo [39], Ledoit/Wolf [40]: Sharpe-ratio inference
- Newey-West [41]: HAC standard errors
- Hansen/Lunde/Nason [45]: Model Confidence Set

---

## Provenance Note

Pages 1-20 directly read from PDF (all main text, tables, and figures). Appendices A-E not extracted (proofs, feature definitions, full registry key table, Kendall association detail, robustness checks). All tables above sourced from direct reading.

---

## See Also

- [[quantitative-finance]] - domain page
