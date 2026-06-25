---
type: domain
title: "Quantitative Finance"
status: developing
created: 2026-06-24
updated: 2026-06-24
tags:
  - domain
  - quantitative-finance
  - machine-learning
  - portfolio-optimization
related:
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
  - "[[depth-psychology]]"
---

# Quantitative Finance

The application of mathematical and statistical methods to financial markets: asset pricing, portfolio optimization, algorithmic trading, risk management, and the evaluation of forecasting models.

Navigation: [[index]] | [[domains/_index]]

---

## Scope in This Vault

Two papers ingested. [[zhang2026-benchmarking-deep-ts-equity]] covers architecture benchmarking and portfolio deployment for equities. [[das2026-chronos-multivariate-forecasting]] covers multivariate vs. univariate forecasting accuracy using a foundation model on equities and Treasury rates.

---

## Sub-areas

| Sub-area | Description | Sources in vault |
|----------|-------------|-----------------|
| Time-series forecasting for equities | Predicting asset returns using ML/statistical models | [[zhang2026-benchmarking-deep-ts-equity]], [[das2026-chronos-multivariate-forecasting]] |
| Fixed-income / yield curve forecasting | Forecasting Treasury rates across maturities | [[das2026-chronos-multivariate-forecasting]] |
| Multivariate vs. univariate forecasting | Whether MV inputs improve raw forecast accuracy | [[das2026-chronos-multivariate-forecasting]] |
| Foundation models for time series | Zero-shot pretrained models (Chronos-2) applied to financial series | [[das2026-chronos-multivariate-forecasting]] |
| Portfolio optimization | Constrained QP, risk controls, turnover limits | [[zhang2026-benchmarking-deep-ts-equity]] |
| Multi-criteria model selection | SMAA, acceptability analysis, regret diagnostics | [[zhang2026-benchmarking-deep-ts-equity]] |

---

## Key Frameworks and Methods (in vault)

**SMAA (Stochastic Multi-Criteria Acceptability Analysis)**: Evaluates model or strategy rankings without imposing explicit preference weights; integrates over all possible orderings to compute rank-acceptability distributions.

**Constrained quadratic portfolio (QP)**: Translates forecasting signals into portfolio weights under real-world constraints: capacity, beta, industry exposure, risk limits, leverage, and turnover.

**Deployment-adjusted acceptability index**: Modifies SMAA by penalizing models whose criteria wins produce high portfolio regret; Gibbs form = entropic update from the SMAA prior.

**Decile portfolios**: Cross-sectional strategy ranking stocks by predicted return; long top decile, short bottom. Standard in academic equity benchmarking.

---

## Key Empirical Finding (from vault)

From [[zhang2026-benchmarking-deep-ts-equity]] (Zhang, Cheng, Leung 2026): no deep or statistical architecture dominates across all preference orderings on CRSP daily data 2018-2024. Best model (TransEnc-8) achieves rank-1 acceptability of only 0.352. After a 20bps transaction cost assumption, net Sharpe is negative for every model tested. Rankings vary substantially with market state, feature universe, and transaction costs.

---

## Sources

- [[zhang2026-benchmarking-deep-ts-equity]] — arXiv 2606.09420 | Zhang, Cheng, Leung 2026 | CRSP benchmark, 15 architectures, SMAA, constrained QP
- [[das2026-chronos-multivariate-forecasting]] — arXiv 2605.21504 | Das, Goyal, Yadav 2026 | Chronos-2 foundation model, MV vs. UV forecasting, Mag-7 equities + Treasury rates 2000-2025

---

## Add new sources and concept pages as the domain grows.
