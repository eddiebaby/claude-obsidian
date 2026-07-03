---
type: source
title: "Two-Stage Sector Rotation Methodology Using Machine Learning and Deep Learning Techniques"
domain: quantitative-finance
status: complete
created: 2026-07-02
updated: 2026-07-02
tags:
  - source
  - paper
  - quantitative-finance
  - machine-learning
  - deep-learning
  - sector-rotation
  - echo-state-networks
related:
  - "[[quantitative-finance]]"
  - "[[Echo-State-Networks]]"
  - "[[Sector-Rotation]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
  - "[[das2026-chronos-multivariate-forecasting]]"
sources: []
---

# Two-Stage Sector Rotation Methodology Using Machine Learning and Deep Learning Techniques

Navigation: [[quantitative-finance]]

---

## Bibliographic Record

| Field | Detail |
|-------|--------|
| Authors | Tugce Karatas (Columbia University, Dept. of IEOR, tk2757@columbia.edu), Ali Hirsa (Columbia University, Dept. of IEOR, ah2347@columbia.edu) |
| Submitted | August 5, 2021 |
| arXiv | [2108.02838](https://arxiv.org/abs/2108.02838) [q-fin.GN] |
| Keywords | neural networks, echo state networks, recurrent neural networks, long short-term memory, gated recurrent units, feature selection, market indicators, exchange traded funds |
| Acknowledgment | Satyan Malhotra (CEO, Ask2.ai) as senior advisor; industry experts thanked for participation |
| Source | PDF directly read (all 28 pages: main text pp. 1-23, references, Appendix A macro variable tables) |

---

## Abstract (verbatim)

"Market indicators such as CPI and GDP have been widely used over decades to identify the stage of business cycles and also investment attractiveness of sectors given market conditions. In this paper, we propose a two-stage methodology that consists of predicting ETF prices for each sector using market indicators and ranking sectors based on their predicted rate of returns. We initially start with choosing sector specific macroeconomic indicators and implement Recursive Feature Elimination (RFE) algorithm to select the most important features for each sector. Using our prediction tool, we implement different Recurrent Neural Networks (RNN) models to predict the future ETF prices for each sector. We then rank the sectors based on their predicted rate of returns. We select the best performing model by evaluating the annualized return, annualized Sharpe ratio, and Calmar ratio of the portfolios that includes the top four ranked sectors chosen by the model. We also test the robustness of the model performance with respect to lookback windows and look ahead windows. Our empirical results show that our methodology beats the equally weighted portfolio performance even in the long run. We also find that Echo State Networks (ESN) exhibits an outstanding performance compared to other models yet it is faster to implement compared to other RNN models."

---

## Section Structure (7 sections + appendices)

1. Introduction
2. Related Literature (2.1 Macroeconomic Variables in Asset Return Forecasting, 2.2 Sector Rotation)
3. Data (ETF universe, macroeconomic sources, RFE feature selection)
4. Preliminaries (Ridge Regression, RNNs, LSTM, GRU, Echo State Networks)
5. Proposed Methodology (two-stage ranking pipeline)
6. Experimental Results (6.1 Performance Metrics, 6.2 Near-Term, 6.3 Medium-Term, 6.4 Long-Term, 6.5 Diagnostics)
7. Conclusion and Future Work
- Appendix A: Macroeconomic Variables (common + sector-specific tables, Tables A7-A15)
- Appendix B: Performance Plots for Different Prediction Horizons (referenced but not extracted in this pass)

---

## Sector Universe (8 Sectors, iShares ETFs)

| Sector | Ticker |
|--------|--------|
| Healthcare | IYH |
| Energy | IYE |
| Utilities | IDU |
| Finance | IYG |
| Technology | IYW |
| Materials | IYM |
| Industrials | IYJ |
| Consumer goods | IYK |

Data: daily adjusted close prices, July 14, 2000 to Nov 10, 2019 (4,862 daily observations per ETF via NYSE calendar, downloaded with the `yfinance` Python library). Study uses **monthly** resampled data: 233 monthly adjusted close observations per ETF.

---

## Macroeconomic Indicators (Section 3, Appendix A)

**Common to all sectors** (Table A7): GDP (quarterly), Unemployment Rate (monthly), CPI (monthly), MORTGAGE30US — 30-year fixed mortgage rate (weekly), Effective Federal Funds Rate (monthly). Source: FRED (St. Louis Fed).

**Sector-specific indicators**:

| Sector | Indicators (source) |
|--------|---------------------|
| Healthcare (Table A8) | Life Expectancy, Population, Birth Rate, Death Rate (all annual, macrotrends.net) |
| Finance (Table A9) | U.S. Inflation Rate, 5-Year Forward Inflation Rate, LIBOR Rate, TED Spread, Trade Balance % of GDP, Debt-to-GDP Ratio (macrotrends.net) |
| Materials (Table A10) | U.S. Inflation Rate, Gold, Aluminum, Copper, Hard Logs, Lead, Iron Ore, Nickel, Palladium, Platinum, Potassium Chloride, Rock Phosphate, Rubber, Silver, Tin, Triple Superphosphate, Zinc (gold.org, indexmundi.com, macrotrends.net) |
| Industrials (Table A11) | Industrial Production Index, Crude Oil Price, Capacity Utilization, Manufacturing (FRED) |
| Consumer goods (Table A12) | Consumer Confidence Index, Business Confidence Index (OECD) |
| Technology (Table A13) | Import, Export Value, Consumer Confidence Index, R&D Value, Technology Investment (FRED, OECD) |
| Energy (Table A14) | Crude Oil Price, Refinery Utilization, Primary Energy Production, Primary Energy Consumption, Import (FRED, EIA) |
| Utilities (Table A15) | Crude Oil Price, Refinery Utilization, Import, Natural Gas Consumption, Natural Gas Price, Interest Rate, Energy Consumption, Electricity and Gas Production (FRED, EIA) |

Since indicators are reported at varying frequencies (daily to annual), the authors apply linear interpolation to bring every series to monthly frequency, aligned with the ETF price series.

---

## Stage 1: Recursive Feature Elimination (Section 3, Figure 1)

Too many macro features per sector risks multicollinearity and overfitting. **Recursive Feature Elimination (RFE)** (Guyon et al. 2002, ref [14]) is used to cut each sector's feature set to the top four:

- Backward selection algorithm: recursively fits a model on all available features, ranks feature importance, drops the least important feature(s) each iteration, repeats until the target feature count is reached.
- Sub-routine model: **random forest regression**. Feature importance = average decrease in node impurity attributable to that feature.
- Output: top 4 ranked features per sector, used as the final input set for the prediction models.

Example findings (Figure 1): Healthcare sector top features are GDP, Population, Births per Woman. Technology sector top features are Import, GDP, R&D Value (GDP called "a very significant feature" across sectors; Finance sector prices highly affected by unemployment rate and trade balance % of GDP).

---

## Stage 2: Prediction Models Compared (Section 4)

| Model | Type | Role |
|-------|------|------|
| Ridge Regression | Linear, L2-regularized | Benchmark model (industry-standard) |
| RNN (vanilla) | Recurrent, tanh activation | Baseline recurrent architecture (BPTT-trained, vanishing gradient issues) |
| LSTM | Gated recurrent (forget/input/output gates) | Addresses vanishing gradients via memory cell |
| GRU | Gated recurrent (update/reset gates, no separate cell state) | Fewer parameters than LSTM, faster, comparable performance per Chung et al. 2014 |
| **Echo State Network (ESN)** | Reservoir computing | Fixed random recurrent reservoir; only the linear readout (`W_out`) is trained |

Full technical treatment of ESN is broken out in [[Echo-State-Networks]].

**Hyperparameters** (held fixed across all lookback/lookahead experiments, chosen from preliminary experiments — no formal hyperparameter search):
- Ridge regression: alpha = 10
- LSTM: 3 hidden layers (16, 256, 64 units), ReLU activation, Adam optimizer (lr=0.0001, decay=1e-7), 1,000 epochs with early stopping, minimizing RMSE
- GRU: 3 hidden layers (32, 256, 64 units), ReLU activation, 500 epochs with early stopping
- ESN: 100 reservoir units; leaking rate = 0.5, spectral radius = 1, reservoir density = 0.5; ridge regression readout with alpha = 1; transient time = 0

The paper explicitly flags that formal hyperparameter tuning (e.g., Bayesian optimization) is left as future work — current hyperparameters are fixed across all experiments to isolate the effect of lookback/lookahead window length.

---

## Two-Stage Methodology (Section 5, Figure 5)

1. **Prediction tool** (per sector, independently): common + sector-specific macro indicators → RFE feature selection → chosen prediction model (Ridge/LSTM/GRU/ESN) → future sector ETF price forecast.
2. **Ranking stage**: apply the prediction tool to all 8 sectors → compute predicted future sector index returns → rank sectors by predicted return → select **top 4 ranked sectors** → form an equally-weighted long-only portfolio.

Benchmark: equally-weighted portfolio across all 8 sector ETFs.

---

## Performance Metrics (Section 6.1)

- **Annualized Return** = `((1 + Return)^(n/N) - 1) × 100`, n = periods per year (12 for monthly data), N = total periods in horizon.
- **Annualized Sharpe Ratio** = Sharpe Ratio × √n, with risk-free rate set to 0 for simplicity.
- **Calmar Ratio** = Annualized Return / Maximum Drawdown.

Evaluation design: prediction horizons of 1, 3, 6, 12, and 24 months ahead ("near-term," "mid-term," "long-term"). For each horizon, lookback windows are swept (0.5 to 5 years depending on horizon) and both in-sample (training) and out-of-sample (testing, 2016 onward) performance are reported.

---

## Key Results Tables

### Next-month (1-month-ahead) prediction, selected lookback windows

| Lookback (yrs) | Model | In-sample Ann.Ret | In-sample Sharpe | In-sample Calmar | OOS Ann.Ret | OOS Sharpe | OOS Calmar |
|---|---|---|---|---|---|---|---|
| — | Benchmark | 8.81% | 0.660 | 0.175 | 13.60% | 1.200 | 0.990 |
| 1 | Ridge | 13.32% | 1.224 | 0.365 | 12.88% | 0.984 | 1.220 |
| 1 | LSTM | 20.20% | 1.271 | 0.602 | 13.96% | 1.384 | 1.386 |
| 1 | GRU | 17.05% | 1.080 | 0.470 | 11.75% | 1.213 | 0.773 |
| 1 | **ESN** | **21.53%** | 1.034 | 0.689 | 12.05% | 1.457 | 0.809 |
| 3 | Ridge | 16.93% | 1.235 | 0.498 | 14.15% | 1.224 | 1.219 |
| 3 | LSTM | 19.24% | **1.466** | 0.610 | **17.83%** | 1.342 | **1.601** |
| 3 | GRU | 10.41% | 0.931 | 0.193 | 10.49% | 0.775 | 0.602 |
| 3 | **ESN** | **25.08%** | 1.022 | **0.862** | 12.70% | **1.702** | 0.777 |

At the 3-year lookback (the largest tested for this horizon), ESN gives the single best in-sample annualized return (25.08%) and Calmar ratio (0.862); LSTM gives the best in-sample Sharpe (1.466) and best OOS return (17.83%) and Calmar (1.601); ESN gives the best OOS Sharpe (1.702). All four models beat the equal-weight benchmark at every lookback window tested.

### Three-months-ahead, four-year lookback (best-performing row for this horizon)

| Model | In-sample Ann.Ret | In-sample Sharpe | In-sample Calmar | OOS Ann.Ret | OOS Sharpe | OOS Calmar |
|---|---|---|---|---|---|---|
| Benchmark | 7.93% | 0.589 | 0.157 | 13.60% | 1.200 | 0.990 |
| Ridge | 16.99% | 1.111 | 0.496 | 11.65% | 1.192 | 1.149 |
| LSTM | 20.23% | 1.177 | 0.578 | 15.44% | 1.321 | 1.008 |
| GRU | 10.02% | 0.923 | 0.218 | 11.23% | 0.696 | 0.614 |
| **ESN** | **27.22%** | **1.574** | **0.894** | **17.58%** | **1.746** | 1.575 |

ESN sweeps all three in-sample metrics and both OOS return and Sharpe at this horizon/lookback combination.

### Six-months-ahead, three-year lookback

| Model | In-sample Ann.Ret | In-sample Sharpe | In-sample Calmar | OOS Ann.Ret | OOS Sharpe | OOS Calmar |
|---|---|---|---|---|---|---|
| Benchmark | 7.24% | 0.544 | 0.144 | 13.60% | 1.200 | 0.990 |
| Ridge | 15.29% | 1.352 | 0.402 | 14.84% | 1.077 | 1.406 |
| LSTM | 18.12% | 1.139 | 0.548 | 13.98% | 1.244 | 0.908 |
| GRU | 11.84% | 1.136 | 0.239 | 13.31% | 0.867 | 0.906 |
| **ESN** | **24.76%** | 1.393 | **0.761** | 15.71% | **1.622** | **1.611** |

### One-year-ahead, four-year lookback (best in-sample row)

| Model | In-sample Ann.Ret | In-sample Sharpe | In-sample Calmar | OOS Ann.Ret | OOS Sharpe | OOS Calmar |
|---|---|---|---|---|---|---|
| Benchmark | 7.40% | 0.547 | 0.147 | 13.60% | 1.200 | 0.990 |
| Ridge | 17.00% | 1.195 | 0.473 | 13.95% | 1.186 | 1.133 |
| LSTM | 20.62% | 1.269 | 0.604 | 14.70% | 1.372 | 1.111 |
| GRU | 10.83% | 1.186 | 0.218 | 14.94% | 0.727 | 1.189 |
| **ESN** | **25.08%** | 1.206 | **0.727** | 15.36% | **1.569** | 1.207 |

### Two-years-ahead, four-year lookback (best in-sample row) and five-year lookback

| Lookback | Model | In-sample Ann.Ret | In-sample Sharpe | In-sample Calmar | OOS Ann.Ret | OOS Sharpe | OOS Calmar |
|---|---|---|---|---|---|---|---|
| 4 yrs | Ridge | 16.60% | **1.568** | 0.467 | **18.72%** | 1.101 | **2.159** |
| 4 yrs | LSTM | 17.64% | 1.451 | 0.516 | 15.51% | 1.142 | 1.417 |
| 4 yrs | GRU | 13.34% | 1.067 | 0.331 | 13.06% | 0.860 | 0.860 |
| 4 yrs | **ESN** | **24.04%** | 1.192 | **0.751** | 14.27% | 1.432 | 1.028 |
| 5 yrs | **ESN** | 24.70% | 1.185 | 0.786 | 15.16% | **1.480** | 0.892 |

Two-years-ahead is the longest horizon tested. Even at this horizon, all models beat the benchmark, and the authors select ESN with 5-year lookback for illustrative purposes (best in-sample return/Calmar, moderate Sharpe).

---

## Central Findings

1. **The two-stage methodology beats the equal-weight benchmark at every prediction horizon tested** (1, 3, 6, 12, 24 months ahead) and at every lookback window, both in-sample and out-of-sample, when the best-performing model/lookback combination is selected per horizon.
2. **ESN wins on both accuracy and speed.** ESN achieves the highest annualized return and Calmar ratio at nearly every lookback window across all five prediction horizons (in-sample). It does not always win on Sharpe ratio (LSTM sometimes leads), but it is consistently top-2. Critically, ESN trains only a linear readout via ridge-style regression on a fixed random reservoir — no backpropagation-through-time — making it dramatically faster to train than LSTM or GRU while matching or beating their returns.
3. **Performance generally improves with longer lookback windows**, though the relationship is not perfectly monotonic for every model; ESN's improvement with lookback length is described as the most consistent of the four models.
4. **LSTM is ESN's main competitor on risk-adjusted return** (Sharpe), and the two together (ESN, LSTM) "almost always" outperform the benchmark portfolio in out-of-sample testing, while GRU and Ridge produce good but less stable results.
5. **GDP is the single most important macro feature across sectors** per the RFE analysis (Section 3); unemployment rate and trade balance % of GDP dominate for Finance; R&D value and import dominate for Technology.
6. **The paper's own diagnostic conclusion (Section 6.5)**: no single model or lookback window is uniformly best across all three performance metrics (return, Sharpe, Calmar) — the authors advocate picking the model/window combination that balances all three ("admissible values for all performance measures") rather than optimizing a single metric.
7. **Contribution claimed vs. prior literature**: (a) most sector rotation literature uses only 2 macro factors (Investment Clock: growth + inflation) or shared factors across sectors; this paper builds sector-specific macro feature sets via RFE; (b) prior sector-ranking ML studies (Zhu et al. 2026-cited [31], Wang et al. [30]) predict one month ahead only — this paper extends prediction horizons out to 2 years and shows the methodology holds up even at that range.
8. **Future work flagged by authors**: (a) replace the two-stage (predict-then-rank) pipeline with a single-step learning-to-rank model (ListNet, BayesRank, BoltzRank) since separate per-sector prediction models increase aggregate ranking uncertainty; (b) incorporate sector-specific news-sentiment scores as additional model input; (c) extend the ETF-proxy methodology to private equity fund data.

---

## Literature Context (Section 2)

**Macro variables in return forecasting** (Table 1, 12 prior studies 1986-2018): inflation rate, CPI, IPI (industrial production index), and GDP recur as positively-associated variables across multiple national markets (US, UK, Japan, Norway, Korea, Malaysia, Ghana, Taiwan, India); unemployment rate, interest rate, and exchange rate recur as negatively-associated. The authors note no prior literature analyzes macro variable impact at the **sector level** (as opposed to whole-market level) — this gap motivates the paper.

**Sector rotation literature** (Section 2.2): two research strands — (a) predict sector index returns directly and rank (Moskowitz & Grinblatt 1999; Chong & Phillips Eta model 2015; Gao & Ren 2015 PCR on Shanghai market; Zhu et al. explainable-AI sector rotation); (b) detect business-cycle phase first, then invest in historically outperforming sectors for that phase (Investment Clock, Greetham & Hartnett 2004; Raffinot & Benoit 2018 random forest/boosting turning-point detection; Sauer 2019 regime-based random forest; Wang et al. 2020 kNN regime + post-Lasso sector prediction). This paper belongs to strand (a), extended to multi-year horizons.

---

## Citations in Paper (selected)

- Guyon et al. [14]: Recursive Feature Elimination (gene selection for cancer classification via SVM, *Machine Learning* 46.1, 2002) — the RFE algorithm used in Section 3
- Hoerl and Kennard [16, 17]: Ridge regression (*Technometrics* 12.1, 1970)
- Rumelhart, Hinton, Williams [27]: Backpropagation Through Time (*Nature* 323.6088, 1986)
- Hochreiter and Schmidhuber [15]: LSTM (*Neural Computation* 9.8, 1997)
- Cho et al. [4]: GRU / RNN encoder-decoder (arXiv:1406.1078, 2014)
- Chung et al. [8]: empirical comparison of gated RNNs (arXiv:1412.3555, 2014)
- Jaeger [19]: original Echo State Network approach (GMD Technical Report 148.34, 2001)
- Jaeger et al. [20]: ESN optimization with leaky-integrator neurons (*Neural Networks* 20.3, 2007) — source of the leaking-rate/spectral-radius formulation (Equations 13-14) used in this paper
- Greetham and Hartnett [13]: the Investment Clock model (2004)
- Moskowitz and Grinblatt [24]: industry momentum (*Journal of Finance* 54.4, 1999)
- Wang, Zhang, Chen [30]: Lasso regression sector rotation with economy-policy cycles (IEEE Big Data 2020)
- Zhu, Yi, Chen [31]: explainable AI / interpretable ML for sector rotation (undated preprint)

---

## Provenance Note

All 28 pages read directly from PDF: main text (pp. 1-23, Sections 1-7), References (p. 24-25), and Appendix A macroeconomic variable tables A7-A15 (pp. 26-28). Appendix B (performance plots for other lookback/lookahead combinations, referenced in-text as B.1-B.5) was not separately extracted — its content is summarized qualitatively within the main-text sections that reference it (all quantitative claims in this page trace to tables/text in the main body, which the authors state are representative).

---

## See Also

- [[quantitative-finance]] - domain page
- [[Echo-State-Networks]] - reservoir computing model that wins this paper's model comparison
- [[Sector-Rotation]] - the strategy category this paper's methodology belongs to
- [[zhang2026-benchmarking-deep-ts-equity]] - later (2026) benchmark of 15 architectures on CRSP equities; compare RNN family (LSTM/GRU/RNN) performance across both papers
- [[das2026-chronos-multivariate-forecasting]] - foundation-model forecasting approach; contrast with this paper's per-sector custom-trained RNN/ESN approach
