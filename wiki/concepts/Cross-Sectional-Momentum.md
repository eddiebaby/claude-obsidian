---
type: concept
title: "Cross-Sectional Momentum"
domain: quantitative-finance
complexity: intermediate
status: developing
created: 2026-07-02
updated: 2026-07-02
tags:
  - quantitative-finance
  - concept
  - momentum
  - trading-strategy
aliases:
  - "CSM"
related:
  - "[[Learning-to-Rank]]"
  - "[[Sector-Rotation]]"
  - "[[Trend-Following]]"
  - "[[poh2020-learning-to-rank-cross-sectional]]"
  - "[[karatas2021-two-stage-sector-rotation]]"
sources:
  - "[[poh2020-learning-to-rank-cross-sectional]]"
---

# Cross-Sectional Momentum

Navigation: [[quantitative-finance]]

---

## Definition

Cross-sectional momentum (CSM) is a systematic trading style that ranks assets *against each other* at each rebalance date and trades the relative winners against the relative losers — buying the top decile (or quintile) of performers and shorting the bottom decile, betting that the *relative ordering* of returns persists. This is distinct from time-series momentum, which asks only whether a single asset's own trailing return is positive or negative, with no reference to how other assets performed.

## Cross-Sectional vs. Time-Series Momentum

| | Time-Series Momentum | Cross-Sectional Momentum |
|---|---|---|
| Signal source | Asset's own historical returns only | Asset's return *relative to* the rest of the universe |
| Position sizing | Directional bet per asset independently | Ranking-based decile/quintile long-short construction |
| Market exposure | Can be net long or net short the whole universe | Dollar/market-neutral by construction (buys winners, sells losers) |
| Classic reference | Moskowitz, Ooi, Pedersen — documented profitability trading ~60 liquid instruments individually over 25 years | Jegadeesh & Titman (1993) — original documentation in US equities |

Because CSM trades assets against each other rather than against their own history, cross-sectional strategies are more insulated from common market-wide moves and can perform even when asset returns are correlated (e.g., equity markets), since the strategy profits from the *dispersion* in returns, not the overall market direction.

## Classical Construction (Score → Rank → Select → Size)

The general CSM pipeline, per [[poh2020-learning-to-rank-cross-sectional]]:

1. **Score calculation**: compute a per-asset score `Y_i = f(u_i)` from an input feature vector.
2. **Score ranking**: sort assets by score to get a position index.
3. **Security selection**: threshold into buckets — typically bottom 10% short (-1), top 10% long (+1), middle 80% flat (0). This is the decile construction; quintile (20%/20%) is a coarser variant.
4. **Portfolio construction**: volatility-scale the selected long/short positions to a target annualized volatility (commonly 15%).

Classical scoring methods (heuristic, no training):
- **Jegadeesh & Titman (1993)**: score = raw cumulative return over the trailing 3-12 months.
- **Baz et al. (2015)**: score = a composite of volatility-normalized MACD indicators across multiple short/long time-scale pairs — a more sophisticated trend estimator than raw returns.

Modern approaches replace the heuristic score with a trained model — either "regress-then-rank" (train a regression model to predict future returns via MSE loss, then sort the predictions) or, as [[poh2020-learning-to-rank-cross-sectional]] argues is superior, [[Learning-to-Rank]] models trained directly against the ranking objective. See [[Learning-to-Rank]] for why regress-then-rank is a structurally mismatched objective for this problem.

## Rebalancing and Universe

CSM strategies typically rebalance monthly (rather than daily) specifically to control transaction costs — Poh et al. rebalance on the last trading day of each month and trade the top/bottom 100 stocks (~10% of the tradeable universe) at each rebalance, using US equities (NYSE, CRSP codes 10/11) from 1980-2019.

## Relation to Sector Rotation

[[Sector-Rotation]] is a specific application of cross-sectional ranking logic at the sector level rather than the individual-security level: instead of ranking individual stocks against each other, sector rotation ranks entire sectors/industries and rotates capital toward the top-ranked ones. The same score-rank-select-size pipeline applies; only the unit of cross-section changes (sector vs. stock).

> [!note] Forward reference
> [[karatas2021-two-stage-sector-rotation]] (not yet ingested as of this writing) is understood to explicitly name learning-to-rank as *future work* for improving sector-rotation ranking accuracy — i.e., it identifies the same regress-then-rank deficiency that [[poh2020-learning-to-rank-cross-sectional]] already solves at the individual-stock level, one asset class removed. When that source is ingested, this page and [[Learning-to-Rank]] should be cross-linked into it directly, since Poh et al. (2020) predates and directly answers the gap that paper flags.

## Relation to Trend-Following

[[Trend-Following]] strategies are typically time-series momentum applied systematically across futures/instruments (each asset traded on its own trend signal, independent of others). CSM and trend-following are often confused because both exploit the broader "momentum" phenomenon, but they differ in the fundamental unit of comparison: trend-following compares an asset to *itself over time*; cross-sectional momentum compares assets *to each other at a point in time*.

## Why Learning to Rank Matters Here

CSM strategies are unusually well-suited to demonstrate the value of [[Learning-to-Rank]] because the ranking step is not incidental — it *is* the strategy. The portfolio literally consists of "top decile long, bottom decile short," so the accuracy of the cross-sectional ranking directly determines return, and a scoring model that is accurate in aggregate (low MSE) but sloppy about the ordering of the assets that end up at the extremes will underperform a model explicitly trained to get that ordering right. [[poh2020-learning-to-rank-cross-sectional]] shows this empirically: switching only the scoring step from heuristics/regress-then-rank to LTR algorithms (same feature inputs, same monthly CSM construction) roughly triples the strategy's Sharpe ratio (best classical benchmark 0.696 vs. best LTR model 2.156).

## See Also

- [[Learning-to-Rank]]
- [[Sector-Rotation]]
- [[Trend-Following]]
- [[poh2020-learning-to-rank-cross-sectional]]
- [[quantitative-finance]]
