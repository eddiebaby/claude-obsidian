---
type: concept
title: "LLM Filings Alpha Strategy"
domain: quantitative-finance
complexity: advanced
created: 2026-07-05
updated: 2026-07-05
tags:
  - strategy
  - quantitative-finance
  - equity
  - swing
  - llm
status: seed
aliases:
  - "Filings NLP Strategy"
  - "LLM Filings Pipeline"
related:
  - "[[Retail Alpha Strategy Roadmap]]"
  - "[[Post-Earnings Announcement Drift Strategy]]"
  - "[[Index Rebalance and Event-Driven Strategy]]"
  - "[[Maker-Checker-Pattern]]"
  - "[[Loop-Engineering]]"
  - "[[Backtest-Overfitting]]"
sources: []
---

# LLM Filings Alpha Strategy

Build guide. LLM-scored SEC filings in under-covered small caps. The strategy with the highest build effort and the deepest moat: it monetizes the exact skill stack already in hand.

## Thesis

Material information lands in EDGAR filings (8-Ks, 10-K/Q changes, Form 4 clusters) for thousands of small caps that no analyst reads promptly, or ever. An LLM pipeline can read every filing the hour it drops, score materiality and direction with near-analyst quality, and trade the multi-day drift while the information diffuses. Institutions do this in large caps with big NLP teams; in sub-$2B names the reaction time is still measured in days. Almost no retail competition executes this well because it requires both pipeline engineering and prompt/eval discipline.

**The architecture already exists in this repo.** The dream-app pipeline (fetch source → structured LLM extraction → score → writeback) is isomorphic to (fetch filing → structured extraction → materiality score → signal DB). This is version two of software already written.

## Universe

US small caps, market cap $50M-$2B, analyst coverage < 3, average dollar volume > $500K (must be exitable). Same universe and data layer as [[Post-Earnings Announcement Drift Strategy]]; build them adjacently.

## Pipeline Architecture

```
EDGAR poller ──► filter ──► extractor ──► verifier ──► scorer ──► signal DB ──► execution
 (RSS/API,        (form type,  (LLM: structured  (LLM pass 2:   (rubric →      (positions,   (orders +
  every 10 min)    universe,    JSON per filing)  quote check)   -5..+5)        entries/exits) fills log)
```

1. **Ingestion**: SEC EDGAR full-text search API + RSS feeds (free, no key). Poll every 10 minutes during market + after hours. Store raw filing text immutably (the `.raw/` discipline, same as the wiki).
2. **Filter**: form types 8-K (by item number: 1.01 material agreements, 2.02 results, 5.02 officer changes, 7.01/8.01 other events), Form 4 (transaction code P, cluster logic from [[Index Rebalance and Event-Driven Strategy]]), 10-K/Q (diff vs prior filing: risk-factor and MD&A changes).
3. **Extraction** (Claude API, structured output): event type, direction for shareholders, magnitude estimate, novelty vs the company's last 4 filings, plain-language one-line summary, key verbatim quotes supporting the score.
4. **Verification** ([[Maker-Checker-Pattern]], non-negotiable): a second, independent LLM pass confirms every extracted quote exists verbatim in the filing and the score follows the rubric. Hallucinated extraction is the failure mode of the whole strategy; 40-60% rejection at first is healthy, not broken.
5. **Scoring**: few-shot rubric prompt mapping extraction to a -5..+5 materiality-times-direction score. The rubric is a versioned file; every change is an experiment logged against outcomes ([[Loop-Engineering]]: engineer the loop, not the individual calls).
6. **Signal**: long scores ≥ +3 at next open, hold 5-20 days with a time stop and a thesis-invalidation stop (close below pre-filing low). Shorts: log but do not trade in v1 (borrow constraints).

## The Contamination Problem (read before backtesting)

An LLM backtest on historical filings has a unique lookahead risk: **the model may know what happened after the filing** (training-data contamination). A 2019 8-K scored by a model trained through 2025 can leak outcome knowledge into the score.

Mitigations, all three:
1. Prompt discipline: filing text only, company name optionally masked, no dates in the prompt.
2. **True out-of-sample = filings after the model's knowledge cutoff.** This is the only clean test. Run the pipeline live-paper for 3-6 months and treat that as the real backtest.
3. Contamination check: for a sample of historical filings, ask the model directly what happened to the stock after; if it knows, that period is contaminated and gets discounted.

Historical backtests here are hypothesis-formers, not evidence. The paper-trading period is the evidence. Plan for that emotionally and financially.

## Costs

~100-300 filings/day pass the filter at this universe size. At ~3K tokens per extraction + verification, this is single-digit dollars per day on current Claude pricing. Token cost is not a constraint; eval quality is.

## Evaluation Before Any Trading

1. Hand-label 200-300 historical filings (an afternoon per hundred with good tooling): direction, materiality. This is the eval set; the dream-app dreamer-response pattern, reused.
2. Measure scorer agreement with labels (aim > 80% direction agreement on |score| ≥ 3 before proceeding).
3. Event study: forward abnormal returns by score bucket. The monotonicity of returns across score buckets matters more than any single bucket's mean.

## Risks & Failure Modes

- **Hallucinated or mis-anchored extraction**: controlled by the verifier pass and quote grounding. Never trade an unverified score.
- **Contaminated backtest confidence**: see above; the discipline is refusing to believe pre-cutoff results.
- **Stale-information trades**: an 8-K about something already priced in (prior press release). The novelty field exists for this; it needs the last-4-filings context to work.
- **Liquidity**: same ADV caps as PEAD (position ≤ 1-2% of ADV).
- **Rubric drift**: silent prompt/model-version changes de-calibrate the scorer. Version-pin the model, checkpoint the rubric, re-run the eval set on every change.

## Kill Criteria

- Eval-set direction agreement < 70%: the scorer is not ready; iterate the rubric, not the portfolio.
- 6-month paper period shows no monotonic score-to-return relationship: the edge is not there at this universe/horizon; archive and revisit with better filters.

## Expansion Hooks

- Earnings-call transcript tone layer for the covered subset (merges with [[Post-Earnings Announcement Drift Strategy]]).
- 13F cluster analysis (multiple small funds initiating the same micro-cap).
- Sell the pipeline itself: a small-cap filings-alert product for other traders is a natural consulting/product spin-out (business domain crossover) once it works privately.

## Status

- [ ] Hypothesis formed (documented here)
- [ ] EDGAR ingestion + filter running
- [ ] Extraction + verification prompts built
- [ ] Eval set labeled, scorer validated
- [ ] Paper period (the real backtest)
- [ ] Live (small size)
