---
type: overview
title: "Retail Alpha Strategy Roadmap"
domain: quantitative-finance
created: 2026-07-05
updated: 2026-07-05
tags:
  - quantitative-finance
  - strategy
  - roadmap
  - overview
status: developing
related:
  - "[[Sector-ETF Momentum Strategy]]"
  - "[[Short-Term Mean Reversion Strategy]]"
  - "[[Post-Earnings Announcement Drift Strategy]]"
  - "[[Index Rebalance and Event-Driven Strategy]]"
  - "[[Volatility Risk Premium Strategy]]"
  - "[[Micro-Futures Trend Strategy]]"
  - "[[LLM Filings Alpha Strategy]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[Backtest-Overfitting]]"
  - "[[Turnover-Regularization]]"
  - "[[Regime-Trust-Gating]]"
  - "[[Loop-Engineering]]"
  - "[[quantitative-finance]]"
sources: []
---

# Retail Alpha Strategy Roadmap

The master page for the seven retail-scale alpha strategy build guides. Each strategy has its own page with full build instructions; this page holds the ranking logic, the shared infrastructure, and the build order.

## The Core Thesis

At retail scale (single coder, five-to-low-six figures), you do not beat institutions at their game. You harvest edges they *cannot* touch because the capacity is too small to matter to them. Two structural advantages:

1. **No capacity constraints pricing you out of illiquid corners.** A strategy that dies above $5M deployed is invisible to a fund and wide open to you.
2. **LLM build speed.** You can build LLM pipelines faster than 95% of retail. The same fetch, extract, score, writeback architecture already built for dream-app applies directly to SEC filings.

Rank every strategy idea by those two advantages, then by effort-to-edge ratio.

## The Seven Strategies

| Strategy | Edge source | Capacity fit | Build effort | Honest assessment |
|---|---|---|---|---|
| [[Sector-ETF Momentum Strategy]] | Behavioral underreaction | Unlimited | Low (in progress) | Mostly risk premium, not alpha. Portfolio base; expect Sharpe ~0.6-0.8 |
| [[Short-Term Mean Reversion Strategy]] | Liquidity provision | Dies above ~$1-5M | Medium | Real alpha, decays fast, needs clean execution modeling. Classic retail-sized edge |
| [[Post-Earnings Announcement Drift Strategy]] | Slow information diffusion | Small-cap only (that is the point) | Medium | Still alive where analyst coverage is thin. Institutions cannot size into it |
| [[Index Rebalance and Event-Driven Strategy]] | Forced flows, attention gaps | Small | Medium | Episodic but high hit-rate. Calendar-driven, stacks on top of other strategies |
| [[Volatility Risk Premium Strategy]] | Insurance premium | Large | Medium | A premium with tail risk, not alpha. Retail-accessible and diversifying. Defined risk always |
| [[Micro-Futures Trend Strategy]] | Behavioral + hedging flows | Large | Medium | Micro contracts made diversified trend viable at retail size. Crisis-alpha profile |
| [[LLM Filings Alpha Strategy]] | Speed + attention in uncovered names | Small | High | **The actual moat.** Exact skill-stack match; almost no retail competition doing this well |

## Build Order

1. **[[Sector-ETF Momentum Strategy]] first.** Not the biggest edge, but it forces building the infrastructure every other row needs: data pipeline, backtest harness with costs, walk-forward validation, execution tracking. The literature base is already ingested (see [[quantitative-finance]], eight-paper sweep of 2026-07-03).
2. **Then [[Post-Earnings Announcement Drift Strategy]] or [[LLM Filings Alpha Strategy]]**, which is where genuine, defensible alpha lives. The two share the small-cap universe and the point-in-time fundamentals data layer, so build them adjacently.
3. **[[Micro-Futures Trend Strategy]] and [[Volatility Risk Premium Strategy]]** as diversifiers once the equity stack runs. Both have return streams with low correlation to equity momentum.
4. **[[Short-Term Mean Reversion Strategy]] and [[Index Rebalance and Event-Driven Strategy]]** slot in opportunistically; both reuse the harness and the equity data layer.

## Shared Infrastructure (build once, reuse seven times)

- **Data layer**: daily OHLCV with survivorship-bias-free universe membership (Norgate Data or Sharadar); point-in-time fundamentals for the small-cap strategies; EDGAR feed for filings and Form 4.
- **Backtest harness**: vectorized daily backtester with explicit cost model (spread + commission in bps per side), position sizing module, walk-forward splits. No backtest is believed without costs.
- **Validation discipline** (applies to every strategy, from the 2026-07-03 sweep):
  1. Simple architecture + low turnover + cost-awareness from day one ([[Turnover-Regularization]]: turnover, not gross accuracy, decides net survival).
  2. Rank cross-sectionally; do not forecast levels.
  3. Regime gate on top ([[Regime-Trust-Gating]]).
  4. Deflate the Sharpe by number of trials attempted ([[Deflated-Sharpe-Ratio]], [[Backtest-Overfitting]]).
  5. Beat 12-1 momentum rotation and SPY buy-and-hold net of costs, or it is not alpha.
- **Execution and journaling**: fills logged against model prices so slippage is measured, not assumed. Feeds the [[Maker-Checker-Pattern]] verification loop later.

## What to Avoid at This Scale

- **Anything HFT-adjacent.** You lose on infrastructure before the first fill.
- **Undefined-risk option selling.** One tail event erases years of premium.
- **More paper reading before the first backtest runs.** The literature base is sufficient; the bottleneck is the harness.

## Portfolio Logic

The end state is not one strategy; it is a small book of 3-5 uncorrelated return streams (equity momentum, small-cap event alpha, trend on futures, volatility premium), each individually modest, combined at vol-targeted weights. Diversification across edge *types* (behavioral, structural, informational) is the retail replacement for institutional leverage.

## Status

- [x] Strategy set defined and ranked
- [ ] Shared harness built (in progress via sector-ETF backtest repo)
- [ ] First strategy live at small size
- [ ] Second uncorrelated stream added
- [ ] Book-level vol targeting and reporting
