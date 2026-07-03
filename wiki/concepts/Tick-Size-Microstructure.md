---
type: concept
title: "Tick-Size Microstructure"
domain: quantitative-finance
complexity: advanced
status: developing
created: 2026-07-02
updated: 2026-07-02
tags:
  - concept
  - quantitative-finance
  - market-microstructure
  - tick-size
  - limit-order-book
aliases:
  - "volatility-normalised tick size"
  - "small-tick vs large-tick"
related:
  - "[[kurth2026-trend-following-demise]]"
  - "[[Trend-Following]]"
  - "[[quantitative-finance]]"
sources:
  - "[[kurth2026-trend-following-demise]]"
---

# Tick-Size Microstructure

Navigation: [[quantitative-finance]] | [[kurth2026-trend-following-demise]]

## Definition

Tick size is the minimum price increment a contract can move on an exchange. On its own, it is a fixed contractual parameter — but relative to an asset's volatility, it determines the *geometry* of that asset's limit order book (LOB), and that geometry has first-order consequences for who can trade cheaply and how.

[[kurth2026-trend-following-demise]] formalises this via the **volatility-normalised tick size**: for contract *i* in month *m*, compute the average ratio of tick size to daily volatility (τ_i,m / σ_i,m), rank all contracts by this ratio each month, and split into two equal-sized tiers:

- **Small tick (ST)**: bottom 50% of the tick-to-volatility ranking — tick size is negligible relative to how much the asset actually moves.
- **Large tick (LT)**: top 50% — tick size is large relative to typical price moves.

The tiering is recomputed monthly and used causally (no look-ahead), but in practice contracts rarely migrate between tiers — it behaves like a structural, near-permanent asset characteristic.

## Why It Conditions Strategy Profitability: Sparse vs Dense Order Books

The mechanism is about limit order book *density*, not liquidity or asset class per se:

- **Small-tick books are intrinsically sparse.** Because gaining price priority requires improving the price by a full tick — and a full tick is large relative to typical volatility — the expected gain from queueing is small relative to adverse-selection risk. Equilibrium posted depth is thin, and gaps between filled price levels are common.
- **Large-tick books are intrinsically dense.** The spread is meaningfully wider than what's needed to compensate for adverse selection, so the queueing rent at the front of the book is substantial, and resting volume builds up at multiple deep levels.

This distinction is independent of any particular generation of market makers — it is a structural consequence of tick-size-to-volatility geometry. But it interacts critically with *who* is providing that liquidity (see below).

## The HFT Market-Maker Interaction

The paper's central mechanism combines this LOB geometry with a documented regime change in liquidity provision: the post-2008 transition from traditional bank-affiliated/proprietary-desk market making (inventory horizons of hours to days) to HFT-dominated market making (intraday flat-inventory mandates, tight spread-capture economics). HFT market-making is structurally incompatible with absorbing the predictable, persistent directional flow that aggregate CTA/trend trading generates — the empirical literature (Korajczyk and Murphy 2019; Van Kervel and Menkveld 2019) documents HFTs withdrawing liquidity in front of large institutional orders rather than supplying it.

This liquidity withdrawal happens in *both* tick-size tiers (documented via Corr(CTA trade, book imbalance) flipping sign around 2010 for fast signals in both tiers). But the consequence is asymmetric:

- **On sparse small-tick books**, withdrawal removes the residual depth that previously let trend followers execute large size at reasonable cost. Trend followers either "walk the book" (high cost) or retreat. Once they retreat, the [[Trend-Following]] impact feedback loop breaks on its input side — the nascent trend signal itself, not just its harvest, decays.
- **On dense large-tick books**, residual depth at multiple levels remains sufficient even after the same rotation of liquidity provision. Execution proceeds largely unperturbed; the loop continues to operate; both signal and PnL survive.

## Empirical Signature

Two direct pieces of evidence in the paper:

1. **The dichotomy is stark and horizon-independent.** Post-2008: small-tick trend Sharpes collapse from ~0.8 to ~0 (100% relative degradation) across *all* signal horizons tested (τ = 5, 10, 20, 50 days). Large-tick Sharpes stay in the 1.0-1.2 range (0-30% relative degradation), even at the highest tested frequency.
2. **Return-vs-book-imbalance relationship flattens post-2011 on small ticks only.** Pre-2011, small-tick contracts show clear adverse selection (negative correlation between 5-minute return and contemporaneous book imbalance, peaking around imbalance ≈ 0.1). Post-2011, this correlation collapses to near zero — the mechanical signature of liquidity withdrawal: depth that would have been "run over" by aggressive directional flow no longer rests long enough to register in the imbalance statistics. Large-tick contracts retain the negative correlation throughout (wide spreads absorb the adverse-selection cost).

## Why Liquidity and Asset Class Don't Replicate the Dichotomy

A natural alternative hypothesis is that raw liquidity (not tick size) drives the split — the two are negatively correlated (log-log Pearson r = −0.35 ± 0.08). But tiering by liquidity instead of tick size does *not* cleanly dichotomise: fast signals on liquid contracts don't uniformly collapse, and there's no clean ordering between high- and low-liquidity sub-portfolios. Asset-class tiering also fails as an explanation on its own — it works only because equity indices and currencies happen to cluster in the small-tick tier, and yields/most commodities cluster in the large-tick tier. Tiering *within* asset class reproduces the same tick-size dichotomy, confirming tick size (not sector) is doing the causal work.

## Within-Contract Confirmations

- **Volatility decomposition**: partitioning each contract's own trading days by realized volatility shows that in low-volatility regimes, the tick-to-volatility ratio rises — small-tick contracts start behaving microstructurally like large-tick contracts, and PnL continues to accrue even post-break in those regimes. This is exactly what the τ/σ (not τ alone) framing predicts.
- **Return-magnitude decomposition**: the trend break is a phenomenon of *large*-return days only. PnL contribution from sub-1σ return days is essentially invariant to the post-2008 regime change across all horizons and tiers — liquidity withdrawal is triggered specifically by the size of detected directional flow, since the adverse-selection cost of providing depth against a weak signal is small.

## Practical Implication

Capacity estimation for trend-following portfolios should be done at the **tick-size-tier level**, not the asset-class or aggregate-participation-rate level. Aggregate participation rates can look comfortably below historical bounds while still binding hard within the small-tick subset specifically — the constraint is local to LOB geometry, not global to the strategy.

## See Also

- [[kurth2026-trend-following-demise]] — the primary source for this concept
- [[Trend-Following]] — the strategy class whose survival this variable discriminates
- [[Jean-Philippe Bouchaud]] — senior author; prior work on price impact (Bouchaud et al. 2018, *Trades, Quotes and Prices*) underlies the impact-function framing here
- [[Capital Fund Management]] — proprietary 5-minute bar data source for the order-book analysis
- [[quantitative-finance]] — domain page
