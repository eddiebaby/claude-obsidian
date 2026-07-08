---
type: concept
title: "Sector-ETF Momentum Strategy"
domain: quantitative-finance
complexity: intermediate
created: 2026-07-05
updated: 2026-07-05
tags:
  - strategy
  - quantitative-finance
  - equity
  - position
status: seed
aliases:
  - "Sector Momentum Build"
  - "ETF Rotation Strategy"
related:
  - "[[Retail Alpha Strategy Roadmap]]"
  - "[[Cross-Sectional-Momentum]]"
  - "[[Sector-Rotation]]"
  - "[[Trend-Following]]"
  - "[[Turnover-Regularization]]"
  - "[[Regime-Trust-Gating]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[Learning-to-Rank]]"
  - "[[Online-Ensemble-Learning]]"
sources:
  - "[[miao-polak-online-ensemble-sector-rotation]]"
  - "[[karatas2021-two-stage-sector-rotation]]"
  - "[[tan2023-spatio-temporal-momentum]]"
  - "[[poh2020-learning-to-rank-cross-sectional]]"
  - "[[sanderink2026-when-alpha-breaks]]"
---

# Sector-ETF Momentum Strategy

Build guide for the baseline strategy and the infrastructure carrier. This is the open build (sector-ETF backtest repo, session 21).

## Thesis

Sectors that outperformed over the past 6-12 months continue to outperform over the next 1-3 months, driven by investor underreaction and slow institutional rebalancing. Mostly a documented risk premium rather than proprietary alpha; its job here is to be the reliable portfolio base and to force the harness into existence.

## Universe

11 SPDR sector ETFs: XLK, XLF, XLV, XLE, XLI, XLY, XLP, XLB, XLU, XLRE, XLC. Alternative: iShares sector set (matches [[karatas2021-two-stage-sector-rotation]]). Add SHY or BIL as the cash leg for the absolute-momentum filter.

## Signal Construction (baseline first, ML later)

**Baseline (build this before anything clever):**
1. Monthly, at last close: compute 12-1 momentum for each ETF (return from t-252 to t-21; skipping the last month avoids short-term reversal contamination).
2. Rank cross-sectionally. Hold the top 3, equal weight.
3. Absolute-momentum overlay: any selected ETF whose own 12-month return is below the T-bill return goes to cash instead ([[Trend-Following]] filter; this is what cuts the 2008-style left tail).
4. Rebalance monthly. Trade only when membership changes (tolerance band, e.g. hold unless the ETF drops out of the top 4, to cut turnover; see [[Turnover-Regularization]]).

**Sizing:** target 10% annualized portfolio vol; scale gross exposure by realized 60-day vol. Cap leverage at 1.0 to start.

## Data Required

| Data | Source | Cost |
|---|---|---|
| Daily OHLCV, ETFs (1998+) | Tiingo / Stooq / Norgate | Free-$30/mo |
| T-bill yield (cash leg) | FRED (DGS3MO) | Free |
| Dividends/splits adjusted closes | Same vendors, use adjusted | Included |

ETF universe means no survivorship-bias problem, which is exactly why this is the right first build.

## Backtest Plan

1. Sample: 2000-present (covers two bear markets and the 2022 rate shock).
2. Costs: 5 bps per side base case; stress at 15 bps (Miao-Polak show sector-level monthly signals survive 5-15 bps).
3. Benchmarks that must be beaten net of costs: SPY buy-and-hold, equal-weight all-sector, and the plain 12-1 top-3 without overlay. If the overlay does not improve on the plain version, ship the plain version.
4. Walk-forward: parameters (lookback, top-N, band) chosen on 2000-2015, validated 2016-present, untouched.
5. Report [[Deflated-Sharpe-Ratio]] with the honest trial count, not the plain Sharpe.

## Execution

- Broker: any zero-commission (IBKR preferred for later strategies).
- Orders: market-on-close on rebalance day, or limit at mid during the last 30 minutes. Sector ETFs are penny-wide; execution is not the hard part here.
- One order batch per month. Total operational load: ~15 minutes/month once automated.

## Expansion Hooks (later, in order of evidence)

1. **Ranking model**: replace the 12-1 sort with LambdaMART pairwise ranking ([[poh2020-learning-to-rank-cross-sectional]]: 3x gross Sharpe vs classical sorts, but validate net).
2. **Ensemble**: online R²-weighted model combination ([[miao-polak-online-ensemble-sector-rotation]], [[Online-Ensemble-Learning]]).
3. **Regime gate**: trade/abstain gate on top ([[sanderink2026-when-alpha-breaks]]: the gate, not the model, drives value; inverse-uncertainty *sizing* backfires).
4. **Joint TSM+CSM**: single-layer spatio-temporal model ([[tan2023-spatio-temporal-momentum]]: shallow beats deep here).

## Risks & Failure Modes

- Momentum crashes (2009-style sharp reversals) hit cross-sectional momentum hardest; the absolute-momentum overlay is the main defense.
- Whipsaw regimes (2015-2016, 2023) generate turnover without payoff; the tolerance band matters more than the lookback.
- Crowding: this exact strategy is published everywhere. Expect the premium to be thin and treat any backtest Sharpe above ~1 as an overfit warning, not a discovery.

## Kill Criteria

- Net of costs, fails to beat SPY buy-and-hold over the full sample: do not trade it.
- Live 12-month tracking error vs backtest expectation exceeds 2x modeled slippage: halt and audit execution.

## Backtest Result (2026-07-07)

Built as the `sector-momentum/` repo (pandas/numpy, free Yahoo data). 2000–2026, net of 5 bps/side, monthly rebalance. Six configs evaluated.

| Config | CAGR | Sharpe | MaxDD |
|---|---|---|---|
| Plain top-3 (no overlay) | 9.4% | 0.47 | −45.0% |
| Top-3 + abs-mom overlay | 8.5% | 0.46 | −31.7% |
| **Top-3 + overlay + band(5)** | **10.3%** | **0.57** | **−30.3%** |
| SPY buy & hold | 8.2% | 0.41 | −55.2% |
| Equal-weight sectors | 8.7% | 0.45 | −53.5% |

**Full-sample verdict**: band(5) beats SPY on every axis (13.2x vs 8.1x terminal, higher Sharpe, half the drawdown). **Passes the spec kill criterion.**

**Walk-forward verdict (the honest test)**: params picked on 2000–2015 (band(5), IS Sharpe 0.47) then read untouched on 2016–2026 → OOS Sharpe **0.71 vs SPY 0.75**, CAGR 13.8% vs 15.1%, MaxDD −30% vs −34%. SPY edges it on risk-adjusted return in the pure-bull decade.

**Interpretation**: the entire edge is **crash avoidance** — the lead is built in 2000–02 and 2008 (2008: strategy 1.50 vs SPY 0.72). In a decade without a sustained bear it tracks/slightly lags SPY with lower drawdown. This is a **defensive equity sleeve, not standalone alpha** — precisely what the momentum literature ([[Cross-Sectional-Momentum]], [[Trend-Following]]) and the "treat Sharpe >1 as overfit" discipline predicted. The absolute-momentum overlay's real job is the drawdown cut (−45% → −30%), not return.

**Implication for the roadmap**: momentum tuning has diminishing returns; the capacity-constrained edges ([[Post-Earnings Announcement Drift Strategy]], [[LLM Filings Alpha Strategy]]) are where genuine retail alpha lives. This repo is now the reusable harness (data → signal → backtest → DSR → walk-forward) those builds inherit.

### Improvement experiments (2026-07-07, `experiments.py`) — NEGATIVE RESULT

Tested six *principled* variants (not a config sweep) on two windows and kept only what beats SPY on **both**:

| Idea | Last 15y Sharpe (SPY 0.78) | Full Sharpe (SPY 0.41) | Robust? |
|---|---|---|---|
| Baseline top-3 + overlay + band(5) | 0.71 | 0.57 | crash-only |
| Faster momentum (6-1 lookback) | 0.57 | 0.47 | crash-only |
| Multi-horizon blend (3/6/9/12) | 0.63 | 0.50 | crash-only |
| Market-regime gate (SPY dual-mom) | 0.69 | 0.59 | crash-only |
| Concentrated top-2, no overlay | 0.65 | 0.51 | crash-only |
| Gate + blend combined | 0.59 | 0.58 | crash-only |

**Every variant is "crash-only": beats SPY on the full sample (has 2008) but NONE beats SPY over the last 15 years (no sustained bear).** The regime gate barely fired because SPY's 12-mo momentum was positive almost the whole 2011-26 window. Conclusion: **you cannot make long-only sector rotation beat buy-and-hold in a bull regime by tuning the signal** — the win mechanism *is* crash avoidance. Do not re-run signal-tuning experiments on this universe expecting to beat SPY; the next build must be a genuinely uncorrelated edge, not a better momentum signal.

## Status

- [x] Hypothesis formed
- [x] Literature base ingested (2026-07-03 sweep)
- [x] Backtested (2026-07-07 — `sector-momentum/` repo; defensive sleeve, not standalone alpha)
- [ ] Paper traded
- [ ] Live (small size)
- [ ] Scaled
