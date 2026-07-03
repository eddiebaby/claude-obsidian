---
type: source
title: "Multivariate Financial Forecasting using the Chronos Time Series Foundation Models"
domain: quantitative-finance
status: complete
created: 2026-06-24
updated: 2026-06-24
tags:
  - source
  - paper
  - quantitative-finance
  - foundation-models
  - time-series
  - multivariate-forecasting
related:
  - "[[quantitative-finance]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
---

# Multivariate Financial Forecasting using the Chronos Time Series Foundation Models

Navigation: [[quantitative-finance]]

---

## Bibliographic Record

| Field | Detail |
|-------|--------|
| Authors | Sanjiv R. Das, Tarang Goyal, Mohini Yadav (Santa Clara University, Leavey School of Business) |
| Submitted | May 22, 2026 |
| arXiv | [2605.21504](https://arxiv.org/abs/2605.21504) [q-fin.ST, cs.AI] |
| GitHub | https://github.com/srdas/timeseries-fm/tree/main |
| Corresponding | srdas@scu.edu |
| Source | PDF directly read (all 10 pages: main text + Appendix A) |

Note: Appendix A discloses that the paper was produced with AI assistance (Gemini for coding and literature review, OpenAI Prism/GPT-5.2 for drafting the Results and Methodology sections, human-led final editing passes).

---

## Abstract (verbatim)

"Using Chronos-2, an open-source time-series foundation model, we evaluate pretrained time-series models for economic and financial forecasting with an emphasis on whether multivariate (MV) inputs improve accuracy relative to univariate (UV) baselines. The study covers two panels - the Magnificent-7 equities and U.S. Treasury interest rates - as well as a combined panel, using rolling monthly evaluations from 2000-2025. We vary input window lengths and forecast horizons and report RMSE and MAPE. Across datasets, MV forecasts consistently outperform UV forecasts, with especially strong gains for interest rates and meaningful improvements for equities. Series-level comparisons show MV improvements in every case, and error dispersion is generally lower under MV inputs. We also provide parameter-heatmap and time-series visualizations. However, mixing time series across equity and interest rate markets reduces forecast accuracy, indicating that adding noisy context degrades model performance. Overall, the results indicate that foundation models can leverage cross-series information to improve forecast accuracy in finance, and that the benefits are strongest when related series are modeled jointly under disciplined rolling protocols."

---

## Research Questions (Section 2.1)

1. Does multivariate (MV) forecasting with Chronos-2 yield more accurate predictions than univariate (UV) methods?
2. Do MV gains differ across asset classes (stocks vs. interest rates)?
3. Does joint modeling of stocks and rates together improve accuracy vs. modeling each group separately?

---

## Chronos-2 Architecture (Section 2.2)

Chronos-2 (Ansari et al., 2025) extends Chronos (2024) by moving beyond purely univariate inputs to a universal zero-shot framework supporting multivariate groups and covariate-informed tasks. Key components:

**1. Tokenization and Robust Scaling**: Input normalized via robust scaling + sinh^-1 transformation to stabilize variance and reduce outlier impact. Categorical covariates converted via target or ordinal encoding. Data augmented with relative time index and binary observed/missing mask.

**2. Patch-Based Representation**: Time series divided into non-overlapping patches of length P, mapped to high-dimensional embeddings via residual network. A unique REG token separates historical context from future patches (attention sink and separator).

**3. Core Architecture**: Encoder-only transformer alternating between two attention layers:
- Time Attention: aggregates information within a single series across temporal patches; uses Rotary Position Embeddings (RoPE) to maintain temporal order
- Group Attention (core innovation): allows the model to share information across different time series within a "group" at each patch index. A group can be variates of a multivariate series, a target with covariates, or a collection of related univariate series.

**4. Multivariate and Covariate Integration**: Handles univariate, multivariate, and covariate-informed tasks via Group IDs. For multivariate tasks, all related variates share an ID, enabling the group attention layer to model dependencies. Known future covariate values provided in future input matrix W.

**5. Training and Quantile Forecasting**: Two-stage training with context 2048-8192 steps. Quantile regression over 21 quantiles (0.01 to 0.99). ICL (in-context learning) capabilities largely learned from synthetic datasets (TSI approach: randomized trend/seasonality/noise; TCM approach: temporal causal models with complex graph-based patterns).

Zero-shot at inference time: no task-specific fine-tuning required.

---

## Data and Experimental Design (Section 2.3)

**Three panels:**
- Magnificent-7 stocks: AAPL, AMZN, GOOGL, MSFT, NFLX, NVDA, TSLA (K = 7)
- U.S. Treasury interest rates: 10 maturities - DGS3MO, DGS6MO, DGS1, DGS2, DGS3, DGS5, DGS7, DGS10, DGS20, DGS30 (K = 10)
- Combined panel: all stocks + rates (K = 17)

**Evaluation period**: 2000-2025, rolling monthly forecasts. Combined panel: July 2010 through December 2025 (when complete data available for all series).

**Parameters varied:**
- Input window lengths n in {126, 252, 504, 756} trading days (0.5 to 3 years of history)
- Forecast horizons m in {21, 63} trading days (1 month and 3 months forward)

**Metrics**: RMSE (root mean squared error, scale-dependent) and MAPE (mean absolute percentage error, scale-free).

**Temporal robustness**: Pre-2023 vs. post-2023 split to check for leakage from Chronos pre-training data.

---

## Key Results

### Table 1: Average performance by dataset and mode

| Dataset | Mode | MAPE mean | MAPE std | RMSE mean | RMSE std |
|---------|------|-----------|----------|-----------|----------|
| Rates | MV | 0.0497 | 0.1673 | 0.0418 | 0.0445 |
| Rates | UV | 0.1233 | 0.2213 | 0.1865 | 0.1783 |
| Stocks | MV | 0.0706 | 0.0834 | 3.9619 | 9.0440 |
| Stocks | UV | 0.0844 | 0.0834 | 5.0395 | 11.5710 |

MV MAPE improvement: ~60% for rates; ~16% for stocks. MV RMSE improvement: ~78% for rates; ~21% for stocks.

### Table 2: UV vs. MV by individual series

**Rates** (averaged over n in {126,252,504,756}, m in {21,63}):

| Series | MAPE (MV) | MAPE (UV) | RMSE (MV) | RMSE (UV) | MAPE Imp. | RMSE Imp. |
|--------|-----------|-----------|-----------|-----------|-----------|-----------|
| DGS3MO | 0.2355 | 0.3186 | 0.0618 | 0.1227 | 0.0831 | 0.0609 |
| DGS6MO | 0.0833 | 0.1770 | 0.0455 | 0.1257 | 0.0937 | 0.0802 |
| DGS1 | 0.0572 | 0.1326 | 0.0454 | 0.1424 | 0.0754 | 0.0970 |
| DGS2 | 0.0334 | 0.1270 | 0.0413 | 0.1845 | 0.0936 | 0.1432 |
| DGS3 | 0.0243 | 0.1181 | 0.0388 | 0.2068 | 0.0938 | 0.1680 |
| DGS5 | 0.0171 | 0.0972 | 0.0359 | 0.2232 | 0.0801 | 0.1873 |
| DGS7 | 0.0134 | 0.0827 | 0.0345 | 0.2278 | 0.0693 | 0.1933 |
| DGS10 | 0.0114 | 0.0703 | 0.0344 | 0.2184 | 0.0589 | 0.1840 |
| DGS20 | 0.0099 | 0.0572 | 0.0364 | 0.2120 | 0.0473 | 0.1756 |
| DGS30 | 0.0113 | 0.0520 | 0.0442 | 0.2012 | 0.0407 | 0.1570 |

**Stocks** (same averaging):

| Series | MAPE (MV) | MAPE (UV) | RMSE (MV) | RMSE (UV) | MAPE Imp. | RMSE Imp. |
|--------|-----------|-----------|-----------|-----------|-----------|-----------|
| AAPL | 0.0599 | 0.0720 | 3.3016 | 4.1563 | 0.0121 | 0.8547 |
| AMZN | 0.0567 | 0.0707 | 3.0825 | 4.0517 | 0.0140 | 0.9692 |
| GOOGL | 0.0478 | 0.0635 | 3.1803 | 4.0070 | 0.0157 | 0.8267 |
| MSFT | 0.0368 | 0.0466 | 4.2003 | 6.1519 | 0.0098 | 1.9516 |
| NFLX | 0.1040 | 0.1145 | 1.7871 | 2.0192 | 0.0105 | 0.2321 |
| NVDA | 0.0906 | 0.1107 | 1.5994 | 1.8420 | 0.0201 | 0.2426 |
| TSLA | 0.1098 | 0.1242 | 13.6796 | 16.7870 | 0.0144 | 3.1074 |

MV improves both MAPE and RMSE for every single rate and stock series.

### Table 3: Combined dataset (rates + stocks together, July 2010 - December 2025)

Cross-domain combination degrades rates forecasts slightly vs. rates-only MV. Example: DGS3MO combined MAPE(MV) 0.2392 vs. 0.2355 rates-only; DGS3MO rates combined RMSE(MV) 0.0655 vs. 0.0618 rates-only. Same qualitative pattern holds across all rates. Stock forecasts also marginally degrade. Conclusion: same-domain MV beats cross-domain MV.

### Parameter heatmap (Figure 1)

Input window length n (126-756 days) has little effect on accuracy for either rates or stocks. Forecast horizon matters: m=63 (3 months) produces substantially larger errors than m=21 (1 month) for both rates (UV MAPE ~0.153-0.166 at 63 days vs. ~0.088-0.090 at 21 days) and stocks.

### Leakage check (Section 3.3)

Post-2023 forecasts are more accurate than pre-2023 for both stocks and rates under MV (Figure 3). If leakage were material, pre-2023 should be better (as that data would be in Chronos pre-training). The opposite pattern rules out leakage as the explanation for MV gains. Chronos was not trained on the specific CRSP stock or FRED rate series used here.

---

## Key Conclusions

1. **MV beats UV consistently**: Chronos-2 can exploit cross-series structure; MV inputs improve accuracy for every individual series.
2. **Gains are domain-conditional**: Rates benefit most (shared term-structure dynamics). Stocks benefit meaningfully. Cross-domain mixing (combining rates and stocks) adds noise and hurts.
3. **Window length does not matter much**: Input history from 0.5 to 3 years yields similar accuracy; the model's in-context learning is relatively robust to history length.
4. **Foundation models transfer without fine-tuning**: The zero-shot deployment works; no task-specific retraining was needed.
5. **Not a trading claim**: Results are about forecast accuracy (RMSE/MAPE), not portfolio-level alpha or net-of-cost returns.

---

## How This Relates to Zhang et al. 2026

[[zhang2026-benchmarking-deep-ts-equity]] evaluates 15 architectures on CRSP daily equities and asks which model survives portfolio constraints and transaction costs. Das et al. 2026 evaluates a single foundation model (Chronos-2) and asks whether multivariate inputs improve raw forecast accuracy. Complementary questions: Zhang et al. addresses model selection for deployment; Das et al. addresses whether MV structure in the forecast helps pre-deployment.

---

## Key Citations

- Ansari et al. (2025): Chronos-2 technical report (arXiv:2510.15821)
- Ansari et al. (2024): Chronos original (arXiv:2403.07815)
- Challu et al. (2023): N-HiTS (AAAI 2023)
- Singh, Ogunfunmi, Das (2025): Yield curve forecasting comparison, Journal of Investment Management 23(4), 37-58
- Sambasivan and Das (2017): Statistical ML approach to yield curve forecasting
- Lopez de Prado (2018): Advances in Financial Machine Learning
- Godahewa et al. (2021): Monash Time Series Forecasting Archive (arXiv:2105.06643)
- Makridakis et al. (2020): M4 Competition (IJF 36(1), 54-74)
- Zhang and Zhang (2026): Review of LLMs for stock price forecasting, hedge-fund perspective (arXiv:2605.05211)
- Bahrpeyma et al. (2021): TSI synthetic diversity methodology (MethodsX 8, 101459)
- Runge et al. (2023): TCM causal time-series methodology (Nature Reviews E&E)

---

## Provenance Note

All 10 pages read directly from PDF, including all tables (1-3), all figures (1-3), and Appendix A. Complete coverage.

---

## See Also

- [[quantitative-finance]] - domain page
- [[zhang2026-benchmarking-deep-ts-equity]] - complementary paper (model selection, portfolio layer)
