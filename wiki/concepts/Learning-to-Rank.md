---
type: concept
address: c-000020
title: "Learning to Rank"
domain: quantitative-finance
complexity: intermediate
status: developing
created: 2026-07-02
updated: 2026-07-02
tags:
  - quantitative-finance
  - concept
  - machine-learning
  - ranking
aliases:
  - "LTR"
related:
  - "[[Cross-Sectional-Momentum]]"
  - "[[poh2020-learning-to-rank-cross-sectional]]"
sources:
  - "[[poh2020-learning-to-rank-cross-sectional]]"
---

# Learning to Rank

Navigation: [[quantitative-finance]]

---

## Definition

Learning to Rank (LTR) is a family of supervised learning techniques, developed primarily in information retrieval (search engines, recommendation), that train models to directly optimize the *ordering* of a set of items rather than to predict an accurate value for each item independently. Applied to cross-sectional asset ranking: instead of forecasting each stock's expected return as accurately as possible (a regression problem) and then sorting the forecasts, LTR trains the model against the ranking outcome itself.

## Why Regress-then-Sort Is Suboptimal

The dominant approach in both classical and modern cross-sectional strategies is "regress-then-rank": train a model (MSE loss) to predict a numeric target — usually forward return — then sort the predictions and take the top/bottom deciles. This has a structural mismatch: the model is optimized to minimize squared prediction error across *all* assets uniformly, but the strategy only cares about correctly identifying the *relative order* of assets, and in practice only the extremes (top and bottom deciles) matter for portfolio construction. A model can have low MSE while still getting the ranking of the assets that matter (the extremes) wrong, and a model can have a "worse" MSE while nailing the ranking. [[poh2020-learning-to-rank-cross-sectional]] demonstrates this empirically: an MLP trained with MSE (regress-then-rank) barely outperforms a random baseline (Sharpe 0.265 vs. 0.155), while LTR models trained on the same input features reach Sharpe ratios of 1.5-2.16.

## The Three LTR Categories

| Category | Approach | Complexity | Example algorithms |
|----------|----------|-----------|---------------------|
| Pointwise | Predicts a score per item independently (equivalent to regress-then-rank) | O(N) | MSE regression, classification |
| Pairwise | Classifies which of a *pair* of items should rank higher | O(N²) | RankNet, LambdaMART |
| Listwise | Learns directly over entire ranked lists as training instances | O(N) | ListNet, ListMLE |

Pointwise methods have been shown (in IR research, and confirmed in [[poh2020-learning-to-rank-cross-sectional]]'s finance application) to be empirically inferior to pairwise and listwise methods, because they discard the relative-ordering information that a ranking task actually needs.

## Key Algorithms (as applied to cross-sectional asset ranking)

- **RankNet** (Burges et al. 2005) — pairwise, neural network. Trains on pairs of samples via stochastic gradient descent, minimizing cross-entropy of the probability that one asset outranks another, instead of MSE. Quadratic complexity O(N²) per rebalance date since it trains over asset pairs.
- **LambdaMART** (Burges et al. 2010) — pairwise, gradient-boosted trees (MART = Multiple Additive Regression Trees). Combines LambdaRank's heuristic "λ-gradients" (which permit training against non-differentiable ranking metrics like NDCG by only requiring gradient approximations, not actual loss values) with tree-based flexibility and speed. Empirically the strongest performer in [[poh2020-learning-to-rank-cross-sectional]] across nearly every metric.
- **ListNet** (Cao et al. 2007) — listwise. Converts scores into "top-one" probability distributions via softmax, minimizes cross-entropy between predicted and ground-truth list distributions. Linear complexity O(N), more efficient than pairwise methods since it doesn't need to enumerate pairs.
- **ListMLE** (Xia et al. 2008) — listwise. Casts ranking as maximum-likelihood estimation over a probability model of permutations. Continuous, differentiable, convex loss — theoretically the most well-behaved of the four, same O(N) complexity as ListNet.

## Ranking Evaluation Metrics

LTR borrows metrics from information retrieval, applied here to how well a model orders assets by future return within a monthly cross-section:

- **Kendall's Tau**: rank correlation coefficient computed across the *entire* asset universe at each rebalance.
- **NDCG@k** (Normalised Discounted Cumulative Gain): position-sensitive metric that weights correct ranking at the *top* of the list more heavily — appropriate for cross-sectional momentum since only the top/bottom decile ends up in the portfolio. [[poh2020-learning-to-rank-cross-sectional]] sets k=100 to match its 100-stock long/short portfolio size.

## Pairwise vs. Listwise: No Clear Winner in Finance

Despite listwise methods' theoretical advantage of learning the full relational structure of a ranked list (rather than isolated pairs), [[poh2020-learning-to-rank-cross-sectional]] found no consistent superiority of listwise (ListNet, ListMLE) over pairwise (RankNet, LambdaMART) methods in the cross-sectional momentum application — LambdaMART, a pairwise method, was the best overall performer. The explanation offered: financial data has an inherently poor signal-to-noise ratio, exacerbated by limited sample size. Listwise approaches see roughly `12 × N_avg` training samples per year (one ranked list per month), while pairwise approaches effectively see `12 × N_avg²` samples per year (every pair within each monthly cross-section is a training instance) — the much larger effective sample size may offset pairwise methods' theoretically weaker objective.

## Application Beyond Momentum

The LTR framework is explicitly modular with respect to input features — [[poh2020-learning-to-rank-cross-sectional]] uses momentum-derived predictors (raw returns, volatility-normalized returns, MACD) as a demonstrative case study, but the same ranking algorithms could be trained on any cross-sectional feature set (value, quality, sentiment, macro), making LTR a general-purpose replacement for the sort step in any cross-sectional systematic strategy — not specific to momentum.

## Relation to [[Cross-Sectional-Momentum]]

Cross-sectional momentum is the strategy [[poh2020-learning-to-rank-cross-sectional]] uses to demonstrate LTR's value; it is not a defining feature of LTR itself. The paper explicitly frames CSM as the "demonstrative use-case" precisely because the strategy already requires a ranking step (sort assets, buy winners, sell losers) that classical implementations fill with heuristics or regress-then-rank models — making the deficiency LTR addresses directly visible.

## See Also

- [[Cross-Sectional-Momentum]]
- [[poh2020-learning-to-rank-cross-sectional]]
- [[quantitative-finance]]
