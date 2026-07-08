---
type: concept
title: "Volatility Risk Premium Strategy"
domain: quantitative-finance
complexity: intermediate
created: 2026-07-05
updated: 2026-07-05
tags:
  - strategy
  - quantitative-finance
  - options
  - swing
status: seed
aliases:
  - "VRP"
  - "VRP Harvesting"
  - "Short Volatility Strategy"
related:
  - "[[Retail Alpha Strategy Roadmap]]"
  - "[[Micro-Futures Trend Strategy]]"
  - "[[Regime-Trust-Gating]]"
sources: []
---

# Volatility Risk Premium Strategy

Build guide. Selling defined-risk option premium to harvest the persistent gap between implied and realized volatility.

## Thesis

Index implied volatility exceeds subsequently realized volatility most of the time because option buyers pay for insurance and crash convexity. Selling that insurance with *strictly defined risk* collects the premium. This is not alpha; it is a risk premium with a fat left tail. Its role in the book is diversification and steady carry, sized so the worst case is survivable by construction.

**Standing rule from the [[Retail Alpha Strategy Roadmap]]: never undefined risk. One tail event erases years. Every structure below has a bought wing.**

## Module 1: Index Premium (the core)

- **Instrument**: SPX or XSP (cash-settled, European, Section 1256 tax treatment; XSP is 1/10th size for small accounts). Avoid SPY options in v1 (assignment risk).
- **Structure**: put credit spread or iron condor, 30-45 DTE.
- **Strikes**: short strike at ~0.15-0.20 delta; long wing 25-50 points below (XSP: 2.5-5).
- **Entry cadence**: mechanical, weekly or biweekly tranches (time diversification beats entry timing).
- **Exit**: take profit at 50% of max credit, or close at 21 DTE, whichever first. Never hold to expiry (gamma week is where defined-risk trades still blow out their sleeve budget).
- **Volatility filter**: only enter when the premium is worth selling: IV rank > 25 as baseline. Optionally skip entries when VIX term structure inverts (backwardation = crash regime; [[Regime-Trust-Gating]] applied to carry).

## Module 2: Earnings Volatility Crush (optional, after Module 1 is live)

- **Event**: liquid single names (options volume > 10K/day) into earnings with IV rank > 70 and implied earnings move > 1.5x the median realized earnings move over the last 8 quarters.
- **Structure**: iron condor spanning the implied move, entered the day before the announcement, closed at next open. Defined wings always (single names gap through short strikes).
- **Expectation**: high hit-rate, small edge per trade, occasional full-width loss. This module lives or dies on the historical implied-vs-realized earnings-move dataset, which must be built first.

## Sizing (this section is the strategy)

- Max loss per position (spread width minus credit) ≤ 1% of portfolio equity.
- Total VRP sleeve max loss if *every* open position hits max loss simultaneously ≤ 10% of portfolio equity. Crashes correlate everything; assume they all lose together because in the tail they will.
- Expected annual return contribution at this sizing: low single digits. That is the honest size of the edge at survivable risk; anyone advertising more is selling undefined risk with extra steps.

## Data Required

| Data | Source | Cost |
|---|---|---|
| Options chains + Greeks (live) | Broker API (IBKR / Tastytrade) | Free with account |
| Historical chains for backtest | ORATS / CBOE DataShop / MarketData.app | $30-100/mo |
| Earnings dates + implied move history | ORATS covers both | included |
| VIX, VIX3M (term structure filter) | CBOE / FRED | Free |

## Backtest Plan

1. Historical options backtests are the least trustworthy of any asset class (stale quotes, wide EOD spreads). Model fills at mid minus 20% of the half-spread and treat results as an upper bound.
2. Sample must include Feb 2018 (Volmageddon), Mar 2020, and 2022. If the sample does not contain a vol event, the backtest measures nothing.
3. Metric: return over max drawdown and worst-month, not Sharpe (the return distribution is short-vol skewed; Sharpe flatters it).
4. Compare against the lazy benchmark: the same capital in T-bills plus a small SPX allocation. VRP must beat that on risk-adjusted terms to be worth the operational load.

## Risks & Failure Modes

- **Tail loss clustering**: the defining risk. Controlled only by the sizing rules above; filters reduce frequency, sizing bounds magnitude.
- **Path pain**: spreads can sit at 2-3x credit against you for weeks without breaching; the 21-DTE exit rule prevents rolling denial.
- **Regime shift**: sustained high-realized-vol regimes (2022) turn the premium negative for months. The IV-rank and term-structure filters are the defense; sitting out is a position.
- **Operational**: assignment mechanics, margin expansion in stress. XSP/SPX cash settlement removes most of this; that is why not SPY.

## Kill Criteria

- Sleeve drawdown exceeds 1.5x the backtest worst case: halt, resize.
- Two consecutive years where the sleeve underperforms T-bills: retire it; the premium is not being paid at survivable size.

## Expansion Hooks

- Term-structure carry (VX calendar spreads) once comfortable with futures via [[Micro-Futures Trend Strategy]].
- Dispersion-lite: short index vol vs long single-name vol in small size (advanced; only after years of Module 1).
- Systematic wheel on quality small caps as a stock-acquisition mechanism (blends into the equity book).

## Status

- [ ] Hypothesis formed (documented here)
- [ ] Historical implied-vs-realized dataset built
- [ ] Backtested / paper traded (Module 1)
- [ ] Live (small size)
- [ ] Module 2 evaluated
