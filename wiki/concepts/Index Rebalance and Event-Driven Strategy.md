---
type: concept
title: "Index Rebalance and Event-Driven Strategy"
domain: quantitative-finance
complexity: intermediate
created: 2026-07-05
updated: 2026-07-05
tags:
  - strategy
  - quantitative-finance
  - equity
  - swing
status: seed
aliases:
  - "Event-Driven Build"
  - "Index Rebalance Trades"
related:
  - "[[Retail Alpha Strategy Roadmap]]"
  - "[[Post-Earnings Announcement Drift Strategy]]"
  - "[[LLM Filings Alpha Strategy]]"
  - "[[Deflated-Sharpe-Ratio]]"
sources: []
---

# Index Rebalance and Event-Driven Strategy

Build guide. A basket of small, structurally-caused, calendar-driven edges: forced flows and attention gaps around corporate and index events. Individually episodic; together a steady side-stream that stacks on top of the systematic book.

## Thesis

When flows are *forced* (index funds must buy adds and sell deletes on a known date) or attention is structurally absent (spun-off entities dumped by index holders who never chose to own them), price moves are predictable in direction and window without any information advantage. Each edge is small and capacity-constrained; institutions arb the big-cap versions, leaving the small-cap tail.

## The Event Menu (build as separate modules, one at a time)

### 1. Index deletion reversal (start here; the add-pop is mostly dead)
- **Event**: stock deleted from S&P 400/600 or Russell 2000 for reasons *other than* fundamentals (migration, size cutoff), sold off by trackers into the effective date.
- **Trade**: buy at close on the effective date, hold 20-60 days for the flow reversal.
- **Filter**: exclude deletions caused by distress/delisting (that selling is informed).
- **Data**: S&P and FTSE Russell press releases (free); Russell reconstitution calendar each June.

### 2. Spin-offs
- **Event**: parent distributes shares of a subsidiary; index funds and mandate-constrained holders sell the spun entity mechanically for 1-3 months.
- **Trade**: buy the spun-off entity after the initial dump stabilizes (typically 2-6 weeks post-distribution, first higher-low on volume decline), hold 6-12 months. Classic Greenblatt setup; still works best in sub-$1B spins nobody covers.
- **Data**: Form 10-12B filings on EDGAR (free), spin-off calendars.

### 3. Insider cluster buys
- **Event**: 3+ distinct insiders (officers/directors) open-market buying within 30 days, in a small cap, aggregate purchase > $250K.
- **Trade**: long at next open after the cluster completes, hold 3-6 months.
- **Rationale**: single insider buys are noise; clusters are the strongest documented insider signal, and in uncovered names the market is slow to notice.
- **Data**: EDGAR Form 4 feed, free, real-time. Parseable with a small script (form type 4, transaction code P).

### 4. Buyback announcements
- **Event**: new or upsized repurchase authorization in a small cap trading below book or after a drawdown.
- **Trade**: long, hold 1-3 months. Weakest of the four edges standalone; best used as a confirming overlay on the other modules.
- **Data**: 8-K filings / press releases via EDGAR full-text search (free).

## Portfolio Construction

- Each module gets a fixed risk budget (e.g. 0.5-1% portfolio risk per position, max 3 concurrent positions per module).
- Events are irregular; expected utilization is 30-60% of the budget. Do not force trades to fill the sleeve.
- This sleeve shares the small-cap data layer and execution constraints with [[Post-Earnings Announcement Drift Strategy]] (position size capped vs ADV, 20-50 bps cost assumption).

## Backtest Plan

1. Backtest each module separately; small event counts mean the statistics are weak, so favor event studies (average CAR with bootstrap confidence bands) over Sharpe optimization.
2. Sample sizes will be 50-300 events per module per decade. Resist parameter tuning: with N that small, anything tuned is overfit ([[Backtest-Overfitting]]). Fix the rules from the literature, test once, and report [[Deflated-Sharpe-Ratio]] honestly.
3. Validate module-by-module against the null of matched random entries in the same names.

## Risks & Failure Modes

- **Small N**: a module can look great on 80 events and be luck. Treat every module as provisional until it has 30+ live-or-paper events.
- **Regime clustering**: spin-offs and deletions cluster in drawdowns; the sleeve is not as diversified from the main book as it appears.
- **Rule changes**: index providers change methodology (announcement lead times have shortened); the deletion edge is a moving target that needs re-verification yearly.
- **Crowding in the well-known versions**: the S&P 500 add-pop decayed to roughly zero post-2010; assume any edge published before 2015 is half its published size at best.

## Kill Criteria (per module)

- Event-study CAR loses significance on a rolling 5-year window: retire the module.
- Two consecutive years of negative net contribution: retire the module.

## Expansion Hooks

- The EDGAR ingestion built for Form 4 and 8-K here is the same plumbing [[LLM Filings Alpha Strategy]] needs; build once.
- LLM classification of deletion reasons (distress vs mechanical) and buyback quality (new money vs refresh) upgrades filters that are currently manual.
- Merger-arb on small definitive deals is the natural fifth module once execution is trusted.

## Status

- [ ] Hypothesis formed (documented here)
- [ ] Module 1 (deletions) event study
- [ ] Module 3 (insider clusters) Form 4 parser + event study
- [ ] Paper traded
- [ ] Live (small size)
