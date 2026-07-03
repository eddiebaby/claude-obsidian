---
type: source
address: c-000016
title: "Building Cross-Sectional Systematic Strategies By Learning to Rank"
domain: quantitative-finance
source_type: paper
author: "Daniel Poh, Bryan Lim, Stefan Zohren, Stephen Roberts"
date_published: 2020-12-13
url: "https://arxiv.org/abs/2012.07149"
confidence: high
status: complete
created: 2026-07-02
updated: 2026-07-02
tags:
  - source
  - paper
  - quantitative-finance
  - machine-learning
  - learning-to-rank
  - cross-sectional-momentum
key_claims:
  - "Casting cross-sectional stock selection as a Learning-to-Rank (LTR) problem, rather than regression-then-sort, improves ranking accuracy and out-of-sample strategy performance."
  - "Pairwise (RankNet, LambdaMART) and listwise (ListNet, ListMLE) LTR algorithms boost Sharpe ratio approximately threefold over traditional cross-sectional momentum benchmarks."
  - "LambdaMART is the best performer overall across profitability, risk, and ranking-quality metrics; no clear superiority of listwise over pairwise methods despite listwise's broader structural information."
related:
  - "[[Learning-to-Rank]]"
  - "[[Cross-Sectional-Momentum]]"
  - "[[quantitative-finance]]"
sources: []
---

# Building Cross-Sectional Systematic Strategies By Learning to Rank

Navigation: [[quantitative-finance]]

---

## Bibliographic Record

| Field | Detail |
|-------|--------|
| Authors | Daniel Poh, Bryan Lim, Stefan Zohren, Stephen Roberts (Oxford-Man Institute of Quantitative Finance, Dept. of Engineering Science, University of Oxford) |
| Submitted | 13 December 2020 |
| arXiv | [2012.07149](https://arxiv.org/abs/2012.07149) [q-fin.TR] |
| PDF | https://arxiv.org/pdf/2012.07149 |
| Keywords | learning to rank; cross-sectional momentum; systematic trading; RankNet; LambdaMART; ListNet; ListMLE |
| Source | PDF directly read, full paper (12 pages incl. appendix), all text, tables, and figures |

---

## Abstract (verbatim)

"The success of a cross-sectional systematic strategy depends critically on accurately ranking assets prior to portfolio construction. Contemporary techniques perform this ranking step either with simple heuristics or by sorting outputs from standard regression or classification models, which have been demonstrated to be sub-optimal for ranking in other domains (e.g. information retrieval). To address this deficiency, we propose a framework to enhance cross-sectional portfolios by incorporating improvements of learning-to-rank algorithms, which lead to improvements of ranking accuracy by learning pairwise and listwise structures across instruments. Using cross-sectional momentum as a demonstrative case study, we show that the use of modern machine learning ranking algorithms can substantially improve the trading performance of cross-sectional strategies — providing approximately threefold boosting of Sharpe Ratios compared to traditional approaches."

---

## Motivation and Framing

The paper's core diagnosis: classical and modern cross-sectional strategies alike compute a per-asset **score**, then **sort** to select long/short buckets. The scoring step is either a hand-designed heuristic (raw returns, MACD) or the output of a supervised regression model trained to minimize mean-squared error (MSE) of forecast returns. Neither approach explicitly optimizes for the *ranking* itself — the thing that actually determines portfolio composition. This is the same deficiency identified and solved in the information retrieval (IR) literature, which developed Learning to Rank (LTR) specifically to train models against ranking-quality objectives rather than pointwise prediction error. This is presented as the first paper to bring LTR to cross-sectional momentum specifically.

---

## Strategy Framework (Section III)

Cross-sectional momentum (CSM) return at rebalance date is:

```
r_CSM(τm, τm+1) = (1/n_τm) Σ_i X_i(τm) · (σ_tgt / σ_i(τm)) · r_i(τm, τm+1)
```

where `X_i ∈ {-1, 0, 1}` is the position (long/short/flat) after ranking, `σ_tgt = 15%` annualized target volatility, and `σ_i` is a rolling 63-day EWM volatility estimate. Rebalancing is monthly (avoids excessive transaction costs).

**Four-component strategy pipeline** (general to all CSM variants):
1. **Score Calculation**: `Y_i = f(u_i)` — model f computes a score per asset from feature vector u.
2. **Score Ranking**: `Z_i = R(Y)` — sort operator assigns position index 1..N.
3. **Security Selection**: decile threshold — bottom 10% → short (-1), top 10% → long (+1), else 0.
4. **Portfolio Construction**: volatility-scale the selected instruments per Eq. (1).

The three score-calculation categories the paper studies:

| Category | Method | Loss / rule |
|----------|--------|-------------|
| Classical momentum | Jegadeesh & Titman (1993): raw cumulative return over 3-12mo | Heuristic, no training |
| Classical momentum | Baz et al. 2015: volatility-normalized MACD across time scales | Heuristic, no training |
| Regress-then-Rank | MLP trained on volatility-normalized future returns | MSE (pointwise) |
| **Learning to Rank** | RankNet, LambdaMART (pairwise); ListNet, ListMLE (listwise) | Ranking-specific losses |

---

## Data and Backtest Setup (Section V-A/B)

- **Universe**: US equities, NYSE-listed, CRSP share codes 10/11, actively traded, price > $1, valid prices, actively trading over prior year.
- **Period**: 1980-2019.
- **Rebalancing**: monthly, last trading day of month.
- **Portfolio size**: 100 stocks long, 100 stocks short (~10% of tradeable universe at each rebalance — decile construction).
- **Model re-tuning**: every 5 years (weights/hyperparameters fixed, then used out-of-sample for the following 5-year window). Classical heuristic strategies are not re-tuned (no free parameters).
- **Predictors** (16 features total, shared inputs across all models): raw cumulative returns (3, 6, 12mo); volatility-normalized returns (3, 6, 12mo, standardized by daily vol, scaled to horizon); MACD-based indicators (final Baz et al. signal + the 3 intermediate raw MACD signals at short/long scale pairs (8,24), (16,48), (32,96), each computed at lookback k=1,3,6mo — 16 features total for this group).
- **Training**: Adam optimizer, 100 max epochs, 90/10 train/validation split, early stopping (25-epoch patience on validation loss), dropout regularization, hyperparameters tuned via HyperOpt (50 iterations of search). RankNet/ListNet/ListMLE use TensorFlow with 2 hidden layers (width as tunable hyperparameter); LambdaMART uses XGBoost.
- **Training target for LTR models**: returns 21 trading days ahead (not full next month).

---

## Models Compared (8 total)

| Shorthand | Model | Type |
|-----------|-------|------|
| Rand | Random stock selection | Absolute baseline |
| JT | Raw cumulative returns (Jegadeesh & Titman 1993) | Classical heuristic |
| Baz | Volatility-normalized MACD (Baz et al. 2015) | Classical heuristic |
| MLP | Multi-Layer Perceptron, regress-then-rank | Regress-then-Rank (MSE) |
| RNet | RankNet (Burges et al. 2005) | LTR — pairwise |
| LM | LambdaMART (Burges et al. 2010) | LTR — pairwise |
| LNet | ListNet (Cao et al. 2007) | LTR — listwise |
| LMLE | ListMLE (Xia et al. 2008) | LTR — listwise |

---

## Full Performance Results

### Exhibit 2: Performance Metrics, Rescaled to Target Volatility (annualized where applicable)

| Metric | Rand | JT | Baz | MLP | RNet | **LM** | LNet | LMLE |
|--------|------|-----|-----|-----|------|--------|------|------|
| E[returns] | 0.024 | 0.092 | 0.112 | 0.044 | 0.243 | **0.359** | 0.306 | 0.260 |
| Volatility | 0.156 | 0.167 | 0.161 | 0.165 | 0.162 | 0.166 | **0.155** | 0.162 |
| Sharpe | 0.155 | 0.551 | 0.696 | 0.265 | 1.502 | **2.156** | 1.970 | 1.611 |
| Downside Dev. | 0.106 | 0.106 | 0.097 | 0.112 | 0.081 | **0.067** | 0.068 | 0.071 |
| MDD | 0.584 | 0.328 | 0.337 | 0.641 | 0.294 | **0.231** | 0.274 | 0.236 |
| Sortino | 0.228 | 0.872 | 1.157 | 0.389 | 3.012 | **5.321** | 4.470 | 3.647 |
| Calmar | 0.042 | 0.281 | 0.333 | 0.068 | 0.828 | **1.555** | 1.115 | 1.102 |
| % +ve Returns | 0.545 | 0.582 | 0.591 | 0.551 | 0.693 | **0.762** | 0.715 | 0.681 |
| Avg. P / Avg. L | 0.947 | 1.114 | 1.184 | 1.001 | 1.407 | 1.594 | **1.679** | 1.534 |

**This is the source of the "threefold Sharpe boosting" headline claim**: best classical benchmark (Baz, Sharpe 0.696) vs. best LTR model (LambdaMART, Sharpe 2.156) ≈ 3.1x. Even the *worst* LTR model (RankNet, 1.502) beats the *best* benchmark (Baz, 0.696) by more than 2x.

### Exhibit 3: Ranking-Quality Metrics (averaged over all rebalancing months)

| Metric | Rand | JT | Baz | MLP | RNet | **LM** | LNet | LMLE |
|--------|------|-----|-----|-----|------|--------|------|------|
| Kendall's Tau | 0.000 | 0.016 | 0.013 | 0.008 | 0.032 | 0.032 | **0.033** | 0.020 |
| NDCG@100 (Longs) | 0.549 | 0.555 | 0.562 | 0.550 | 0.576 | 0.576 | **0.578** | 0.565 |
| NDCG@100 (Shorts) | 0.552 | 0.562 | 0.555 | 0.564 | **0.585** | 0.578 | 0.579 | 0.567 |

Ranking metrics: Kendall's Tau (rank correlation over the entire cross-section) and NDCG@100 (Normalised Discounted Cumulative Gain, IR metric emphasizing top-ranked precision, cutoff k=100 to match long/short portfolio size). All LTR models beat all benchmarks on NDCG@100; the gap on Kendall's Tau is directionally the same but smaller in magnitude.

### Exhibit 4: Decile Portfolio Sharpe Ratios (Decile 1 = worst-ranked, Decile 10 = best-ranked; L-S = long-short)

| Strategy | D1 | D5 | D10 | **L-S** |
|----------|-----|-----|------|---------|
| Rand | 0.675 | 0.697 | 0.702 | 0.028 |
| JT | 0.360 | 0.746 | 0.938 | 0.167 |
| Baz | 0.582 | 0.566 | 1.130 | 0.161 |
| MLP | 0.443 | 0.780 | 0.806 | 0.097 |
| RNet | 0.263 | 0.698 | 1.238 | 1.527 |
| **LM** | 0.075 | 0.716 | 1.232 | **2.107** |
| LNet | 0.232 | 0.711 | 1.186 | 1.911 |
| LMLE | 0.360 | 0.671 | 1.186 | 1.530 |

The LTR models show a steeper monotonic rise from decile 1 to decile 10 than any benchmark — i.e. their ranking is more precise at correctly separating winners from losers, which is the direct mechanism behind the L-S Sharpe gains. LambdaMART's decile 1-10 spread (0.075 → 1.232) and L-S Sharpe of 2.107 (this column uses a different volatility-rescaling convention than Exhibit 2's headline 2.156; both are reported directly in the paper) are the largest of any model.

---

## LTR Algorithms Compared (Section IV-C)

**Pointwise vs. pairwise vs. listwise** — the three LTR categories in the IR literature:
- *Pointwise* (= regress-then-rank, e.g. MLP): treats ranking as independent classification/regression per item. Empirically inferior to pairwise/listwise because it ignores relative ordering information.
- *Pairwise*: casts ranking as classifying which of a pair of items should rank higher.
- *Listwise*: learns directly over entire ranked lists as training instances.

**RankNet (Burges et al. 2005)** — pairwise. First neural approach to LTR; trains on pairs, minimizing cross-entropy of the probability that one item outranks another (not MSE). Complexity O(N²) per rebalance date (quadratic in universe size) since training runs over all pairs.

**LambdaMART (Burges et al. 2010)** — pairwise. Combines LambdaRank with Multiple Additive Regression Trees (MART/gradient-boosted trees). Does not directly optimize a loss function; uses heuristic gradient approximations ("λ-gradients") that exploit the fact that only gradients (not loss values) are needed for training — allowing optimization of non-differentiable, non-smooth ranking metrics like NDCG. Combines LambdaRank's empirical optimality w.r.t. NDCG with MART's flexibility/speed (truncation-based tradeoffs important for search engines).

**ListNet (Cao et al. 2007)** — listwise. Resolves the pairwise problems (quadratic cost, mismatched pairwise-classification objective vs. true ranking objective) via a probabilistic "top-one" probability distribution over score lists, normalized with softmax; loss = cross-entropy between predicted and ground-truth list distributions. Complexity O(N) — linear, more efficient than RankNet.

**ListMLE (Xia et al. 2008)** — listwise. Casts ranking as maximum likelihood over a probability model of permutations; likelihood loss is continuous, differentiable, and convex (theoretically preferable properties: consistency, soundness, linear complexity). Same O(N) linear complexity as ListNet.

**Empirical finding on pairwise vs. listwise**: no clear superiority of listwise over pairwise despite listwise's theoretically broader structural information. The paper attributes this to financial data's inherently poor signal-to-noise ratio, compounded by limited sample size — listwise methods get ~12 × N_avg samples/year vs. pairwise methods' ~12 × N_avg² samples/year (pairwise has vastly more effective training data from the same universe, offsetting its worse theoretical properties).

---

## Model Confidence Set / Robustness Notes

- Across benchmarks, Random performs worst as expected; MLP (regress-then-rank) is only marginally better than Random — attributed to overfitting on limited/noisy financial data and the known difficulty of monthly return forecasting as a regression target, worsened by using only price-based features.
- LambdaMART is best or near-best across essentially every profitability, risk, and ranking metric reported (Exhibits 2, 3, 4) — the paper explicitly calls it out as the standout performer.
- All strategies rescaled to comparable volatility (15% target) for like-for-like Sharpe comparison; separately, all returns in the main results section are computed **without transaction costs** — the paper's main tables are gross-of-cost. (Contrast with [[zhang2026-benchmarking-deep-ts-equity]], which finds broad-universe decile signals can survive costs but constrained-QP portfolios go negative even at 20bps — this paper does not run an analogous net-of-cost decile analysis in the main text.)

---

## Conclusions and Future Work

LTR provides a general, modular framework for cross-sectional ranking that flexibly accepts different feature sets — the momentum predictors used here are a demonstrative case study, not an architectural constraint. Sharpe ratios improve by roughly a factor of three over traditional heuristic/regress-then-rank approaches. Future directions flagged: architecture innovation / model ensembling to push further gains; extending to higher-frequency data (order-book) and other asset classes.

---

## Citations in Paper (selected)

- Jegadeesh & Titman [3]: original cross-sectional momentum documentation (1993)
- Moskowitz, Ooi, Pedersen [2]: time-series momentum
- Baz, Granger, Harvey, Le Roux, Rattray [1]: MACD-based trend signal
- Burges et al. [44]: RankNet (2005)
- Burges [45]: "From RankNet to LambdaRank to LambdaMART: An Overview" (2010)
- Cao, Qin, Liu, Tsai, Li [46]: ListNet (2007)
- Xia, Liu, Wang, Zhang, Li [39]: ListMLE (2008)
- Wang & Klabjan [11]; Li, Qin, Wang, Metzler [12]; Wang, Liu, Yang, Huang [14]: LTR applications in finance/robo-advising
- Bergstra, Komer, Eliasmith, Yamins, Cox [42]: HyperOpt
- Chen & Guestrin [49]: XGBoost

---

## Provenance Note

Full 12-page paper directly read (main text Sections I-VI, all exhibits/tables, references, and Appendix VII on the LTR-for-CSM framework transposition and hyperparameter search grids). Appendix VII-B hyperparameter grids omitted from this summary as non-substantive detail (available in source PDF if needed).

---

## See Also

- [[Learning-to-Rank]] — concept page on the ranking-objective framework
- [[Cross-Sectional-Momentum]] — concept page on the strategy class
- [[quantitative-finance]] — domain page
