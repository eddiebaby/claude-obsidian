---
type: concept
address: c-000007
title: "Trend-Following"
domain: quantitative-finance
complexity: intermediate
status: developing
created: 2026-07-02
updated: 2026-07-03
tags:
  - concept
  - quantitative-finance
  - trend-following
  - cta
  - momentum
aliases:
  - "time-series momentum"
  - "TSM"
  - "CTA strategy"
related:
  - "[[kurth2026-trend-following-demise]]"
  - "[[Tick-Size-Microstructure]]"
  - "[[tan2023-spatio-temporal-momentum]]"
  - "[[Cross-Sectional-Momentum]]"
  - "[[quantitative-finance]]"
sources:
  - "[[kurth2026-trend-following-demise]]"
  - "[[tan2023-spatio-temporal-momentum]]"
---

# Trend-Following

Navigation: [[quantitative-finance]] | [[kurth2026-trend-following-demise]]

## Definition

Trend-following (also time-series momentum, TSM) is a strategy class that takes a position proportional to a normalised measure of an asset's recent directional movement — long after a run-up, short after a sell-off — independent of any relative comparison to other assets (contrast with cross-sectional momentum). The canonical implementation: the difference between a fast and a slower moving average of price, normalised by volatility, applied across a diversified basket of liquid futures. This is the methodology the Commodity Trading Advisor (CTA) industry converged on by the 1990s.

Formally (per [[kurth2026-trend-following-demise]]): for contract *i*, signal s(t) = EWMA_fast(price) − EWMA_slow(price), normalised by an exponentially weighted standard deviation, clipped at ±2 SD. A signal built with fast decay τ is denoted EWM-τ-4τ.

Time-series momentum was documented across 58 instruments and three-and-a-half decades by Moskowitz, Ooi, and Pedersen (2012), and traced back at least two centuries by Lempérière et al. (2014) and Hurst, Ooi, and Pedersen (2017). It is one of the most robust anomalies ever catalogued in finance — and one of the most theoretically awkward, since it directly contradicts the Efficient Market Hypothesis (obvious information — past price — not being priced in).

## Why It Works: The Impact Feedback-Loop Mechanism

[[kurth2026-trend-following-demise]] proposes that trend is best understood as a market *mechanism*, not merely a statistical anomaly:

> "Trend signals trigger directional trades, whose market impact reinforces the very price moves that produced the signal, which in turn sustains the signal for the next trader to act on."

Under this framing, trend's profitability and its very existence are the same phenomenon: aggressive directional flow pushes price via market impact, and that price move sustains (or creates) the signal the next trend follower detects. This is not the only mechanism proposed in the literature — behavioural underreaction to public news (Hong and Stein 1999; Daniel et al. 1998), slow diffusion of information across heterogeneously informed investors (Hong et al. 2000), and staggered accumulation by informed anticipatory traders all coexist as partial explanations — but the impact loop is the one that makes the sharpest, most falsifiable cross-sectional prediction, and the one the paper's evidence most directly supports.

The loop has two preconditions:
1. Trend followers can execute aggressively at a cost that doesn't exceed the impact-mediated alpha they create.
2. The relationship between aggressive flow and price (the impact function) stays intact.

Anything that breaks either precondition — rising execution costs to the point of disengagement, or a change in how flow translates into price — attacks profitability and signal strength *simultaneously*, not just one or the other.

## Why Short-Term Variants Decayed Post-2009

Kurth, Eisler, Rej, and Bouchaud (2026) document an abrupt, structural break in short-horizon trend performance starting ~2008-2009: pre-break Sharpe ratios were *highest* for the fastest signals (τ=5 days: 0.84), but post-break the fastest signal collapsed hardest (τ=5: Sharpe 0.12), while the slowest signal tested (τ=50) retained the most (Sharpe 0.70 → 0.40).

Four candidate explanations were tested; three were rejected:
- **Capacity constraints** — rejected: CTA AUM growth postdates the PnL break (reverse causality); no recovery despite rising post-2018 liquidity; square-root-impact-implied drag (~0.1 Sharpe) is an order of magnitude too small; and critically, removing execution costs entirely (zero-lag execution) still produces flat post-break returns — meaning the *signal itself*, not just the cost of harvesting it, degraded.
- **Market electronification** — rejected: gradual transition, abrupt PnL break; sectoral timing/ordering mismatches.
- **CTA-order-flow regime shift** — insufficient at the asset-class level (no monotonic mapping between correlation change and PnL outcome across sectors).
- **Microstructural mechanism (accepted)** — see [[Tick-Size-Microstructure]]. The post-crisis shift to HFT-dominated market making withdraws liquidity in front of predictable directional flow, breaking the impact loop specifically on small-tick (sparse order book) contracts, while leaving it intact on large-tick (dense order book) contracts.

The mechanism is structural, not a temporary cost problem: passive (limit-order) execution doesn't rescue short-term trend either, because (a) passive fills are adversely timed against an informative signal (missed-opportunity cost, not classic adverse selection), and (b) passive orders don't generate the aggressive-flow impact that feeds the loop in the first place.

## Where It Survives

- **Slow/long-horizon signals** (weeks to months) remain largely intact across the futures universe — information-diffusion-style trend generation operates on these horizons and doesn't require the same aggressive-execution intensity.
- **Large-tick contracts** (dense limit order books — see [[Tick-Size-Microstructure]]) retain trend profitability at *all* signal horizons, including fast ones, because residual book depth still absorbs aggressive CTA flow at reasonable cost.
- Concentrated in yields (YLD) and most commodities (CMD) in the tested universe; largely absent in equity indices (IDX) and currencies (FXR), which cluster in the small-tick tier.

## Relation to Cross-Sectional / Equity Return Forecasting

[[kurth2026-trend-following-demise]] is a futures/CTA-specific microstructural account, distinct from the cross-sectional deep-learning equity forecasting benchmarked in [[zhang2026-benchmarking-deep-ts-equity]]. Both papers converge on a broader theme in this vault: strategy profitability claims from raw signal accuracy or historical Sharpe collapse once realistic execution frictions (transaction costs, turnover, liquidity constraints) are imposed. Where Zhang et al. show constrained-portfolio net Sharpe turning negative for all promoted equity models at 20bps, Kurth et al. show trend's own signal (not just its harvest) structurally decaying once the microstructure underlying its execution changes.

[[pollok2026-end-to-end-portfolio-policies]] uses time-series momentum (TSM) as a benchmark strategy for evaluating end-to-end learned portfolio policies — a parallel ingest in this vault; see that page for the comparison once filed.

## Unification with Cross-Sectional Momentum

Trend-following (TSMOM) and [[Cross-Sectional-Momentum]] (CSMOM) have historically been treated as distinct strategy classes: TSMOM builds a signal for each asset from only that asset's own history; CSMOM ranks assets against each other and takes a maximum long/short position on the top/bottom deciles, ignoring signal strength for everything in between. [[tan2023-spatio-temporal-momentum]] (Tan, Roberts, Zohren 2023) unifies both into a single learned "spatio-temporal momentum" (STMOM) model: a multitask neural network takes a spatio-temporal tensor of momentum features from the *entire asset universe* as input and directly outputs a trading signal for every asset simultaneously, learning cross-asset interactions that pure TSMOM cannot see while avoiding CSMOM's binary long/short discretization. Notably, the paper finds the simplest possible architecture — a single fully-connected layer — outperforms deeper networks (MLP, CNN, LSTM) at this task, and that the resulting strategy retains its edge over TSMOM/CSMOM/long-only benchmarks at realistic transaction costs (5-10 bps).

## See Also

- [[kurth2026-trend-following-demise]] — the primary source for this concept
- [[Tick-Size-Microstructure]] — the cross-sectional variable that discriminates surviving from collapsed trend
- [[Jean-Philippe Bouchaud]] — senior author, prior work on price impact and market microstructure
- [[Capital Fund Management]] — authors' affiliation; industry-scale CTA proxy validated against CFM proprietary data
- [[quantitative-finance]] — domain page
