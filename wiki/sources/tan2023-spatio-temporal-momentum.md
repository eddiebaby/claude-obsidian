---
type: source
title: "Spatio-Temporal Momentum: Jointly Learning Time-Series and Cross-Sectional Strategies"
domain: quantitative-finance
source_type: paper
author: "Wee Ling Tan, Stephen Roberts, Stefan Zohren (Oxford-Man Institute of Quantitative Finance, University of Oxford)"
date_published: 2023-02-20
url: "https://arxiv.org/abs/2302.10175"
confidence: high
status: complete
created: 2026-07-03
updated: 2026-07-03
tags:
  - source
  - paper
  - quantitative-finance
  - machine-learning
  - momentum
  - portfolio-optimization
key_claims:
  - "A single fully-connected layer (SLP) jointly predicting trading signals for all assets from both time-series and cross-sectional momentum features outperforms deeper architectures (MLP, CNN, LSTM) and the single-asset Deep Momentum Network (DMN) benchmark."
  - "The spatio-temporal momentum (STMOM) strategy retains its performance edge over benchmarks at transaction costs of up to 5-10 basis points."
  - "Turnover regularization via a localized minibatch penalty consistently improves the SLP's net-of-cost performance across all cost scenarios tested (0-10 bps)."
related:
  - "[[Turnover-Regularization]]"
  - "[[Trend-Following]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
  - "[[pollok2026-end-to-end-portfolio-policies]]"
  - "[[quantitative-finance]]"
sources:
  - "[[.raw/2302.10175.pdf]]"
---

# Spatio-Temporal Momentum: Jointly Learning Time-Series and Cross-Sectional Strategies

Navigation: [[quantitative-finance]]

---

## Bibliographic Record

| Field | Detail |
|-------|--------|
| Authors | Wee Ling Tan, Stephen Roberts, Stefan Zohren — Dept. of Engineering Science, Oxford-Man Institute of Quantitative Finance, University of Oxford |
| Submitted | February 20, 2023 |
| arXiv | [2302.10175](https://arxiv.org/abs/2302.10175) [q-fin.PM] |
| Published | *The Journal of Financial Data Science*, 2023 |
| Source | PDF directly read (all 17 main-text pages + Appendices A-B, all tables and figures) |

---

## Abstract (verbatim)

"We introduce Spatio-Temporal Momentum strategies, a class of models that unify both time-series and cross-sectional momentum strategies by trading assets based on their cross-sectional momentum features over time. While both time-series and cross-sectional momentum strategies are designed to systematically capture momentum risk premia, these strategies are regarded as distinct implementations and do not consider the concurrent relationship and predictability between temporal and cross-sectional momentum features of different assets. We model spatio-temporal momentum with neural networks of varying complexities and demonstrate that a simple neural network with only a single fully-connected layer learns to simultaneously generate trading signals for all assets in a portfolio by incorporating both their time-series and cross-sectional momentum features. Backtesting on portfolios of 46 actively-traded US equities and 12 equity index futures contracts, we demonstrate that the model is able to retain its performance over benchmarks in the presence of high transaction costs of up to 5-10 basis points. In particular, we find that the model when coupled with least absolute shrinkage and turnover regularization results in the best performance over various transaction cost scenarios."

---

## Core Idea: Unifying TSM and CSM

Time-series momentum (TSMOM) constructs a signal for each asset from only that asset's own historical returns, ignoring interactions with other assets in the portfolio. Cross-sectional momentum (CSMOM) scores and ranks all assets by return, then takes a maximum long position for the top decile and maximum short for the bottom decile — but this binary long/short allocation ignores the actual signal strength for the majority of assets, which fall in intermediate deciles and get no position at all.

The paper's central move: treat prediction of the trading signal for each asset as one task in a **multitask learning** problem, where all tasks (assets) share the same input — a spatio-temporal tensor of momentum features drawn from the *entire universe*, not just the asset's own history. The model directly outputs a signal vector **X**_t in [-1,1]^N for all N assets simultaneously, bypassing the need to manually rank assets (as CSMOM does) while still letting the network learn cross-asset interactions (which pure TSMOM cannot).

Formally: **X**_t = f(**u**_t; θ), where **u**_t ∈ ℝ^(N×τ×d) is the spatio-temporal tensor (N assets, τ steps of temporal history, d features per asset-timestep). For N=1 this collapses to a pure time-series momentum strategy — STMOM is a strict generalization.

---

## Architecture Comparison — Why the Single Layer Won

Five architectures were tested end-to-end, all trained directly against annualized Sharpe ratio (not a two-stage forecast-then-optimize pipeline):

| Model | Structure |
|-------|-----------|
| **SLP** (Single Layer Perceptron) | **X**_t = tanh(**W**ᵀ**u**_t + **b**) — one linear map + activation, no hidden layers |
| MLP | Two hidden layers, tanh activations |
| CNN | 1-D causal (autoregressive) convolutions, optional dilation, average pooling into an MLP head |
| LSTM | Single-layer LSTM, fully connected output layer mapping hidden state to signal vector |
| DMN (reference/benchmark) | Lim, Zohren & Roberts (2019) single-output Sharpe-optimized LSTM — trained per-asset, not multitask |

**Result: the SLP — the simplest possible model — beat every deeper STMOM architecture (MLP, CNN, LSTM) on both datasets.** On US Equities (vol-target rescaled, Table 2): SLP Sharpe 2.609 vs. MLP 1.040, CNN 0.192, LSTM 1.015. On Equity Index Futures (Table 4): SLP Sharpe 2.066, more than 6x the reference DMN's 0.340 in risk-adjusted terms cited in the text (SLP and MLP outperformed DMN "by more than four times" on raw signals, Table 3).

**Why the paper says simplicity wins**: STMOM models train on only *t* samples (one aggregate Sharpe loss per time step across the whole universe), while a per-asset DMN effectively sees *t × N* samples (each asset trained somewhat independently). This is a low signal-to-noise, data-constrained regime — added model complexity (MLP's extra hidden layers, CNN's convolutional filters, LSTM's gating) increases overfitting risk faster than it captures genuine structure. The paper explicitly notes CNN's poor performance "echoes a similar conclusion" from the original DMN paper (Lim et al. 2019) about architecture complexity struggling in this data regime.

The SLP's linear weight matrix **W** is also directly interpretable — the paper runs a SHAP analysis (Section 5.7) on the trained SLP for a single asset (BAC) and across the full universe, finding the top 20 most important features are dominated by **volatility-normalized MACD features from *other* assets in the cross-section**, not the asset's own return features — direct evidence the model is learning genuine cross-sectional interaction, not just re-deriving single-asset TSMOM.

---

## Turnover Regularization

Turnover is defined per-asset as TO_t^(i) = σ_tgt |X_t^(i)/σ_t^(i) − X_{t-1}^(i)/σ_{t-1}^(i)| (Eq. 12) — the volatility-scaled absolute change in position size between consecutive days.

For sequential models (LSTM, DMN) turnover regularization is straightforward: optimize directly for the ex-cost Sharpe ratio using consecutive time steps. For **non-recurrent, non-sequential models like the SLP**, which are trained on shuffled minibatches with no guaranteed temporal ordering between samples, the paper introduces a **localized minibatch turnover penalty** (Eq. 14):

TÕ_t^(i) = σ_tgt |X_t^(i)/σ_t^(i) − X_t*^(i)/σ_t*^(i)|, where t ≠ t* are two distinct consecutive-in-time samples that happen to co-occur within the same shuffled training minibatch.

**Result: turnover regularization consistently improved the SLP across every transaction cost level tested (Table 6)**, while the same regularization applied to the DMN only helped at the single highest cost tested (10 bps) and *hurt* performance at every other level. See [[Turnover-Regularization]] for the full comparison and why this asymmetry matters.

---

## Full Results: Net Sharpe vs. Transaction Costs (Table 6, US Equities, rescaled to target vol)

| Model | 0.0 bps | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 | 5.0 | 10.0 |
|-------|---------|-----|-----|-----|-----|-----|-----|------|
| Long Only | 0.841 | 0.839 | 0.838 | 0.835 | 0.832 | 0.829 | 0.826 | 0.812 |
| TSMOM | 0.358 | 0.347 | 0.336 | 0.315 | 0.293 | 0.271 | 0.249 | 0.140 |
| MACD | 0.245 | 0.238 | 0.232 | 0.219 | 0.207 | 0.194 | 0.182 | 0.119 |
| CSMOM | -0.655 | -0.683 | -0.710 | -0.765 | -0.820 | -0.875 | -0.930 | -1.204 |
| **DMN** | **2.920** | 2.844 | 2.768 | 2.615 | 2.462 | 2.308 | 2.153 | 1.375 |
| DMN+Reg | 2.073 | 2.044 | 2.015 | 1.957 | 1.899 | 1.840 | 1.782 | **1.486** |
| **SLP** | 2.609 | 2.518 | 2.427 | 2.243 | 2.060 | 1.876 | 1.691 | 0.762 |
| **SLP+Reg** | **2.672** | **2.603** | **2.534** | **2.395** | **2.256** | **2.116** | **1.976** | **1.271** |

The paper's headline claim: both the (non-regularized) DMN and SLP retain their performance edge over the classical benchmarks (Long Only, TSMOM, MACD, CSMOM) at transaction costs of up to **5-10 basis points**, which the authors characterize as realistic for equity markets. SLP+Reg dominates plain SLP at every cost level and remains competitive with DMN despite DMN's much larger per-asset training data advantage.

Average turnover distributions (Figure 4) confirm the mechanism: SLP has materially lower average turnover than DMN, and turnover-regularized SLP shows a lower mean turnover with a wider interquartile spread — a direct consequence of the localized minibatch penalty requiring shuffled-batch sampling.

---

## Datasets

**US Equities**: 46 actively-traded US equities, Financials sector, CRSP daily data, market cap Small (300M-2B) to Mega (>200B), randomly sampled via the Nasdaq Stock Screener. Backtested 1990-2022. Full ticker list in Appendix B (e.g. AFG, AJG, BAC, C, JPM, MCO, STT, TROW, WFC, ZION).

**Equity Index Futures**: 12 ratio-adjusted continuous equity index futures contracts, Pinnacle Data Corp CLC Database. Backtested 2003-2020. Contracts: SP (S&P 500), YM (Mini Dow Jones), EN (NASDAQ Mini), ER (Russell 2000 Mini), MD (S&P 400 Mini), XU/XX (EuroStoxx50/Stoxx50), CA (CAC40), LX (FTSE 100), AX (German DAX), HS (Hang Seng), NK (Nikkei).

**Momentum features (d)**: (F.1) volatility-normalized returns at lookback scales k ∈ {1, 20, 63, 126, 252} days (daily, monthly, quarterly, semiannual, annual); (F.2) volatility-normalized MACD signals at short/long scale pairs S_k ∈ {8,16,32}, L_k ∈ {24,48,96}.

**Training**: Expanding-window backtest, retrained every 5 additional years. 90/10 train-validation split, Adam optimizer, early stopping, 100 iterations of random search hyperparameter tuning. L1 (LASSO) shrinkage penalty applied to the SLP weight matrix (Eq. 11) for feature sparsity, on top of the Sharpe-ratio loss (multitask-weighted, λ_i = 1/N when all assets/tasks treated equally).

---

## Signal Diversification (Section 5.5)

SLP shows mostly zero-to-moderately-positive, unstable correlation with other momentum strategies (~46% correlation with DMN). Combining TSMOM+CSMOM (Sharpe 0.177) or DMN+CSMOM (2.115) does **not** beat a standalone SLP (2.609) — meaning CSMOM adds little marginal value once STMOM is available. But combining DMN with SLP (both spatio-temporal-aware, one per-asset and one cross-sectional-aware) yields Sharpe **3.304** (Table 5), beating either alone — evidence the SLP is capturing genuine interaction structure that a per-asset DMN cannot, making the two complementary rather than redundant.

---

## Citations of Note

- Moskowitz, Ooi, Pedersen (2012): original time-series momentum documentation, 58 instruments
- Jegadeesh & Titman (1993): cross-sectional momentum, NYSE/AMEX winners-losers
- Baz et al. (2015): MACD-based trend estimation, the paper's MACD benchmark
- Lim, Zohren, Roberts (2019): Deep Momentum Networks (DMN), the paper's primary ML benchmark
- Caruana (1997): foundational multitask learning framework the paper adopts
- Lundberg & Lee (2017): SHAP, used for SLP interpretability analysis
- Wood, Giegerich, Roberts, Zohren (2023, arXiv 2112.08534): "Trading with the Momentum Transformer" — cited as future work direction (attention-based architectures)

---

## Provenance Note

All 17 main-text pages plus Appendices A (architecture equations, hyperparameter tables) and B (dataset ticker lists) directly read from PDF. All equations, tables (1-8), and figures (1-6) sourced from direct reading. No sections omitted.

---

## See Also

- [[Turnover-Regularization]] — the concept page on explicit vs. implicit turnover control, built from this paper's Section 5.6
- [[Trend-Following]] — time-series momentum as one half of what this paper unifies
- [[zhang2026-benchmarking-deep-ts-equity]] — parallel finding that turnover, not gross accuracy, decides which equity model survives costs
- [[pollok2026-end-to-end-portfolio-policies]] — transformer's implicit low turnover vs. this paper's explicit turnover penalty, two different routes to the same net-Sharpe-preserving goal
- [[quantitative-finance]] — domain page
