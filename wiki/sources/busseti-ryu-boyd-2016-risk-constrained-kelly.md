---
type: source
source_type: paper
title: "Risk-Constrained Kelly Gambling"
author: "Enzo Busseti, Ernest K. Ryu, Stephen Boyd"
date_published: 2016-03-20
url: "https://arxiv.org/abs/1603.06183"
domain: quantitative-finance
created: 2026-07-07
updated: 2026-07-07
confidence: high
tags:
  - source
  - quantitative-finance
  - position-sizing
  - kelly
key_claims:
  - "Maximize log-growth subject to P(drawdown > alpha) < beta, made tractable via a computable bound and convex optimization"
  - "Resulting bets outperform fractional-Kelly at the same drawdown risk level"
  - "A single risk-aversion parameter trades off growth rate against drawdown probability"
status: developing
related:
  - "[[Prop-Firm-Eval-Sizing]]"
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[Volatility Risk Premium Strategy]]"
---

# Busseti, Ryu & Boyd 2016 — Risk-Constrained Kelly Gambling

The formal machinery for the exact problem a prop-eval account poses: maximize growth subject to a hard constraint on the probability of hitting a fixed drawdown level (the MLL). The intractable drawdown-probability constraint is replaced with a computable bound, yielding a convex problem whose solutions **dominate fractional Kelly** — more growth at the same drawdown risk, or less risk at the same growth. The quadratic approximation recovers Markowitz mean-variance.

## Application in [[Prop-Firm-Eval-Sizing]]

Set α = the MLL distance ($2,000 on LucidFlex 50K), β = acceptable eval-failure probability from drawdown (e.g., 20%), plug in the backtested per-trade return distribution, solve for size. The eval fee budget (5 attempts) then maps directly to expected total cost: fee / (1 − β-realized). Replaces the PRD's ad-hoc "5% of MLL per trade" with a principled, distribution-aware number.
