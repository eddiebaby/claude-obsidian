---
type: domain
title: "Quantitative Finance"
status: developing
created: 2026-06-24
updated: 2026-07-03
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

Ten papers ingested (2026-07-03 sweep added eight). Coverage now spans the full strategy stack: signal mechanisms ([[kurth2026-trend-following-demise]]), forecasting ([[das2026-chronos-multivariate-forecasting]], [[zhang2026-benchmarking-deep-ts-equity]]), sector rotation blueprints ([[miao-polak-online-ensemble-sector-rotation]], [[karatas2021-two-stage-sector-rotation]]), model/objective design ([[tan2023-spatio-temporal-momentum]], [[poh2020-learning-to-rank-cross-sectional]], [[pollok2026-end-to-end-portfolio-policies]]), deployment risk ([[sanderink2026-when-alpha-breaks]]), and evaluation discipline ([[bailey-lopez-de-prado-2014-deflated-sharpe]]).

> [!key-insight] Cross-paper thesis: turnover determines net survival
> Four independent studies converge: gross forecast accuracy does not decide whether a strategy makes money — turnover does. Zhang's TS-RIDGE (gross Sharpe 3.88, turnover 7.95/day) dies at 20bps; Pollok's transformer (turnover ~0.02/day) beats an LSTM with identical gross performance; Tan's explicit [[Turnover-Regularization]] is what keeps the single-layer model alive at 10bps; Miao-Polak's monthly sector rotation survives costs precisely because sector-level signals rebalance slowly. Design for low turnover first, accuracy second.

---

## Sub-areas

| Sub-area | Description | Sources in vault |
|----------|-------------|-----------------|
| **Loop engineering / agentic trading** | Autonomous recursive trading systems; maker-checker separation; self-improving skill files | [[loop-engineering-hedge-funds-2026]] |
| Time-series forecasting for equities | Predicting asset returns using ML/statistical models | [[zhang2026-benchmarking-deep-ts-equity]], [[das2026-chronos-multivariate-forecasting]] |
| **Sector rotation** | Ranking and rotating across sector portfolios/ETFs | [[miao-polak-online-ensemble-sector-rotation]], [[karatas2021-two-stage-sector-rotation]] |
| Trend-following / CTA microstructure | Why and where momentum signals still have a live mechanism | [[kurth2026-trend-following-demise]] |
| Momentum learning (TSM + CSM) | Joint/learned momentum strategies, learning-to-rank | [[tan2023-spatio-temporal-momentum]], [[poh2020-learning-to-rank-cross-sectional]] |
| End-to-end portfolio policies | Features → weights via differentiable performance loss | [[pollok2026-end-to-end-portfolio-policies]] |
| Deployment risk / regime gating | When to trust a live model; trade/abstain decisions | [[sanderink2026-when-alpha-breaks]] |
| Backtest validation | Selection-bias-corrected performance statistics | [[bailey-lopez-de-prado-2014-deflated-sharpe]] |
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

## Key Concepts

**Strategy classes**: [[Trend-Following]], [[Cross-Sectional-Momentum]], [[Sector-Rotation]]
**Model design**: [[End-to-End-Portfolio-Optimization]], [[Learning-to-Rank]], [[Online-Ensemble-Learning]], [[Echo-State-Networks]], [[Turnover-Regularization]]
**Deployment & validation**: [[Regime-Trust-Gating]], [[Deflated-Sharpe-Ratio]], [[Backtest-Overfitting]], [[Tick-Size-Microstructure]]
**Agentic systems**: [[Loop-Engineering]] — the structural move from prompting agents to building systems that prompt agents; [[Maker-Checker-Pattern]] — the institutional verification pattern now automatable via agents

---

## Sources

- [[loop-engineering-hedge-funds-2026]] — v260615 practitioner essay | Anonymous 2026 | Five-stage autonomous trading loop, six primitives, maker-checker, SKILL.md, verification debt
- [[zhang2026-benchmarking-deep-ts-equity]] — arXiv 2606.09420 | Zhang, Cheng, Leung 2026 | CRSP benchmark, 15 architectures, SMAA, constrained QP
- [[das2026-chronos-multivariate-forecasting]] — arXiv 2605.21504 | Das, Goyal, Yadav 2026 | Chronos-2 foundation model, MV vs. UV forecasting, Mag-7 equities + Treasury rates 2000-2025
- [[kurth2026-trend-following-demise]] — arXiv 2607.01550 | Kurth, Eisler, Rej, Bouchaud (CFM) 2026 | 100 futures 1995-2025; fast trend dead on small-tick contracts; tick-size mechanism
- [[pollok2026-end-to-end-portfolio-policies]] — arXiv 2607.00475 | Pollok & Robik 2026 | 16 CME futures; differentiable Sharpe; transformer's low turnover wins net
- [[miao-polak-online-ensemble-sector-rotation]] — arXiv 2304.09947 | Miao & Polak | 50 SIC sectors; MWUM online ensemble; top-5 Sharpe 0.657 net-survivable
- [[karatas2021-two-stage-sector-rotation]] — arXiv 2108.02838 | Karatas & Hirsa 2021 | 8 iShares sector ETFs; macro + RNN two-stage; ESN wins
- [[tan2023-spatio-temporal-momentum]] — arXiv 2302.10175 | Tan, Roberts, Zohren 2023 | joint TSM+CSM; single-layer net; turnover regularization
- [[poh2020-learning-to-rank-cross-sectional]] — arXiv 2012.07149 | Poh, Lim, Zohren, Roberts 2020 | LambdaMART ranking 3x Sharpe vs classical sorts (gross)
- [[sanderink2026-when-alpha-breaks]] — arXiv 2603.13252 | Sanderink 2026 | regime-trust gate + epistemic tail cap; deployment safety for rankers
- [[bailey-lopez-de-prado-2014-deflated-sharpe]] — JPM 2014 | Bailey & López de Prado | DSR; expected max Sharpe under null; multiple-testing correction

---

## Adjacent ML Optimization (relevant to building trading models)

- [[PACE Optimizer]] — lightweight AdamW wrapper that improves EMA-returned LLM checkpoints via optimal control pullback; directly applicable when fine-tuning LLMs on financial data (arXiv 2606.25086)
- [[Iterate Averaging in LLM Training]] — why production LM pipelines return EMA of weights rather than final iterate; taxonomy of averaging schemes; the training–inference model gap

---

## Add new sources and concept pages as the domain grows.
