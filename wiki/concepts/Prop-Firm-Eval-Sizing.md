---
type: concept
title: "Prop-Firm-Eval-Sizing"
domain: quantitative-finance
complexity: intermediate
created: 2026-07-07
updated: 2026-07-07
tags:
  - quantitative-finance
  - position-sizing
  - prop-firm
  - risk-management
status: developing
aliases:
  - "Eval Sizing"
  - "Drawdown-Constrained Sizing"
related:
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[Overnight-Drift]]"
sources:
  - "[[busseti-ryu-boyd-2016-risk-constrained-kelly]]"
---

# Prop-Firm Eval Sizing

Position sizing for accounts that die at a fixed trailing drawdown (the prop-eval structure). The problem is NOT growth maximization — it is passing probability × eval cost minimization, then funded-account extraction.

## The formal frame

[[busseti-ryu-boyd-2016-risk-constrained-kelly]]: maximize log-growth subject to P(drawdown > α) < β, solved as a convex program; dominates fractional Kelly at equal drawdown risk. For a LucidFlex 50K eval: α = $2,000 (MLL), β = tolerated failure-by-drawdown probability. Input is the backtested per-trade P&L distribution; output is the per-trade size that hits the profit target fastest within the ruin budget.

## Practitioner numbers (medium confidence — aggregator sources, primary guide 403'd)

- Industry eval pass rates: ~5–20% of attempts.
- Risk per trade sweet spots: 0.5–1% of account → highest pass rate; 1.5–2% → highest expected ROI per eval dollar. (For LucidFlex sizing, percentage should be taken of the MLL, not the nominal account — $2,000 is the real account.)
- 60–70% of trailing-drawdown liquidations occur **immediately after the trader's best day** — with intraday-trailing firms the ratchet chases the equity high tick-by-tick. LucidFlex's EOD-trailing + lock-at-breakeven+$100 structurally mitigates this specific failure mode, one reason the Flex product suits automation.

## Design rules distilled

1. Size from the per-trade P&L distribution and the MLL via risk-constrained Kelly, not from round-number percentages.
2. In eval, the objective function includes the consistency cap: daily profit cap changes optimal size vs a pure race to target.
3. After funding, resize DOWN until the MLL locks at breakeven+$100 (the lock removes ruin risk entirely; growth optimization only starts after the lock).
4. Monte Carlo the whole eval as a system (target, MLL, consistency cap, daily stop) — pass probability per attempt × $130 gives expected eval spend before funding; if expected spend exceeds ~2 payouts, the strategy is not worth running even if profitable.
