---
type: concept
title: "Post-Earnings Announcement Drift Strategy"
domain: quantitative-finance
complexity: advanced
created: 2026-07-05
updated: 2026-07-05
tags:
  - strategy
  - quantitative-finance
  - equity
  - swing
status: seed
aliases:
  - "PEAD"
  - "PEAD Strategy"
  - "Earnings Drift Build"
related:
  - "[[Retail Alpha Strategy Roadmap]]"
  - "[[LLM Filings Alpha Strategy]]"
  - "[[Short-Term Mean Reversion Strategy]]"
  - "[[Cross-Sectional-Momentum]]"
  - "[[Deflated-Sharpe-Ratio]]"
sources: []
---

# Post-Earnings Announcement Drift Strategy

Build guide. Buying positive earnings surprises in under-covered small caps and riding the slow repricing.

## Thesis

Prices underreact to earnings news when too few people are paying attention. In large caps PEAD was arbitraged away in the 2000s; in small caps with thin or zero analyst coverage, information diffuses over weeks, not minutes. The constraint that keeps the edge alive is capacity: a fund cannot put $50M into a $300M market-cap name without becoming the price. Retail size fits exactly.

## Universe

US common stocks, market cap $50M-$2B, price > $3, 20-day average dollar volume > $500K, analyst coverage < 3 estimates (or zero). Exclude biotech pre-revenue names (binary FDA risk, not earnings drift).

## Signal Construction

**The surprise measure (retail workaround, no IBES needed):**
The cleanest institutional measure is SUE (standardized unexpected earnings vs analyst consensus), but consensus data for uncovered small caps is sparse or nonexistent, which is the point. Use the market's own first reaction as the surprise proxy:

1. **Earnings-day abnormal return**: return from pre-announcement close to post-announcement close, minus the sector ETF return same day. Require > +5%.
2. **Volume confirmation**: earnings-day volume > 3x the 20-day average (separates real repricing from noise).
3. Optional fundamental confirmation once the fundamentals layer exists: YoY EPS acceleration, revenue beat vs own trailing trend.

**Trade construction:**
1. Enter at the open on day +2 after the announcement (skip day +1: the gap-and-fade crowd trades that day; drift is what remains after them).
2. Hold 30-60 calendar days, or exit early on a close below the earnings-day low (thesis invalidation level).
3. Portfolio: rank all qualifying events by abnormal-return-times-volume score, hold up to 10-15 concurrent positions, equal risk weight, ~1% portfolio risk each.
4. Short side optional and hard (borrow on small caps is expensive/unavailable); the long side carries the edge.

## Data Required

| Data | Source | Cost |
|---|---|---|
| Earnings announcement dates + times (point-in-time) | Sharadar EVENTS / Alpha Vantage / EODHD calendar | ~$30-80/mo |
| Daily OHLCV with delistings | Norgate / Sharadar SEP | shared with other strategies |
| Fundamentals (point-in-time, as-reported) | Sharadar SF1 | included in Sharadar bundle |

**The dangerous detail is announcement timestamps**: trading a "reaction" to an announcement your data says was pre-market when it was actually post-close creates phantom alpha. Verify BMO/AMC flags on a sample by hand against actual press-release timestamps before trusting the vendor.

## Backtest Plan

1. Sample: 2010-present (small-cap microstructure before that is a different market).
2. Costs: 20-30 bps per side all-in for small caps (spread is the cost, not commission). Stress at 50 bps.
3. Fill honesty: cap assumed position size at 1-2% of the stock's average daily dollar volume.
4. Benchmarks: IWM buy-and-hold; a random-entry same-holding-period bootstrap on the same universe (controls for small-cap beta); alpha vs size/value/momentum factors.
5. Event-study plot first (average cumulative abnormal return by day 0-60 across all events) before building the portfolio version; if the event study shows no drift, stop there.

## Risks & Failure Modes

- **Liquidity**: exits are slow in names like these; the position-size-vs-ADV cap is the control, not optional.
- **Data quality**: small-cap earnings dates are the dirtiest data in equities. Bad dates create fake alpha in both directions.
- **Regime sensitivity**: drift weakens in high-VIX regimes when macro swamps micro news.
- **One bad cohort**: 10-15 concurrent small caps can correlate on a factor shock; the per-name risk cap and universe diversification (no sector > 30%) are the controls.

## Kill Criteria

- Event-study drift (day 2-60 CAR) statistically indistinguishable from zero on the validation period: no trade.
- Live fills degrade the modeled edge by more than half over 30 trades: reduce size or halt.

## Expansion Hooks

- Feed each qualifying event through the [[LLM Filings Alpha Strategy]] scorer (read the actual 8-K/press release, score quality of the beat: organic vs one-time). This is the planned merge point of the two strategies.
- Add earnings-call-transcript tone scoring for the subset that hosts calls.
- Extend to guidance revisions and 10-K/Q filing-date drift, not just earnings dates.

## Status

- [ ] Hypothesis formed (documented here)
- [ ] Event study run
- [ ] Backtested as portfolio
- [ ] Paper traded
- [ ] Live (small size)
- [ ] Scaled
