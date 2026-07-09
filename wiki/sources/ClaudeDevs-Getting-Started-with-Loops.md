---
type: source
title: "Getting Started with Loops (ClaudeDevs)"
created: 2026-07-08
updated: 2026-07-08
domain: ai-ml
address: c-000026
tags:
  - source
  - ai-ml
  - loop-engineering
  - claude-code
  - agentic-systems
status: ingested
source_type: article
author: "Delba de Oliveira"
date_published: 2026-07-06
url: "https://x.com/ClaudeDevs/article/2074208949205881033"
confidence: high
key_claims:
  - "A loop is an agent repeating cycles of work until a stop condition is met; loops are classified by trigger, stop criteria, and primitive"
  - "Four loop types: turn-based, goal-based (/goal), time-based (/loop, /schedule), proactive (composed)"
  - "Deterministic success criteria (tests passed, score thresholds) are what make goal loops effective"
  - "Loop output quality depends on the system around it: clean codebase, encoded verification, reachable docs, fresh-context reviewer"
  - "When a result fails the standard, encode the fix into the system (skills) so all future iterations improve"
related:
  - "[[Loop-Engineering]]"
  - "[[Claude Code Loop Taxonomy]]"
  - "[[loop-engineering-hedge-funds-2026]]"
  - "[[agentx-kuaishou-2026]]"
  - "[[Delba de Oliveira]]"
sources:
  - "[[.raw/2026-07-06-claudedevs-getting-started-with-loops.md]]"
---

# Getting Started with Loops (ClaudeDevs)

Official Claude Code team article (published via @ClaudeDevs on X, 2026-07-06; written by [[Delba de Oliveira]]). The first *canonical* definition and taxonomy of loops from Anthropic itself — until now the term circulated through practitioner essays ([[loop-engineering-hedge-funds-2026]], Osmani, Steinberger, Cherny). Raw capture: `.raw/2026-07-06-claudedevs-getting-started-with-loops.md`.

**Definition**: loops are agents repeating cycles of work until a stop condition is met. Classified by (1) how triggered, (2) how stopped, (3) which Claude Code primitive, (4) which tasks fit.

## The four loop types

| Loop | You hand off | Use it when | Reach for |
|------|-------------|-------------|-----------|
| Turn-based | The check | You're exploring or deciding | Custom verification skills |
| Goal-based | The stop condition | You know what done looks like | `/goal` |
| Time-based | The trigger | Work happens outside your project on a schedule | `/loop`, `/schedule` |
| Proactive | The prompt | The work is recurring and well-defined | All of the above + dynamic workflows |

Full breakdown: [[Claude Code Loop Taxonomy]].

## Key mechanics

- **Turn-based**: every prompt is a manual loop (gather context → act → check → respond). Improve it by encoding manual verification steps as a `SKILL.md` so the agent self-verifies end-to-end. The more quantitative the checks, the better the self-verification.
- **Goal-based (`/goal`)**: an evaluator model checks the completion condition each time Claude tries to stop, and sends it back until goal met or turn cap hit. Deterministic criteria (tests passed, Lighthouse ≥ 90) work best.
- **Time-based (`/loop`, `/schedule`)**: re-runs a prompt on an interval; `/loop` runs locally, `/schedule` moves the routine to the cloud.
- **Proactive**: compose `/schedule` + `/goal` + skills + dynamic workflows + auto mode into human-out-of-the-loop routines (bug triage, migrations, dependency upgrades).

## Quality & token discipline

Quality: keep the codebase clean (agents follow existing conventions); encode "what good looks like" as skills; make docs reachable; use a second fresh-context agent for review. **When a result fails, don't just fix the instance — encode the fix so every future iteration improves.** (This is the compounding move; same insight as SKILL.md-as-paid-lessons in [[loop-engineering-hedge-funds-2026]].)

Tokens: right-size primitive and model; explicit success/stop criteria; pilot before large workflow runs; script deterministic work instead of reasoning through it; match routine cadence to how fast the watched thing changes; review with `/usage`.

## Relation to existing wiki claims

Consistent with [[Loop-Engineering]] — no contradictions. The practitioner essay defines *why* (replace yourself as prompter) and the six primitives; this article defines *what Anthropic officially ships* (the four types and their primitives). The `/goal` evaluator-model detail and the explicit token-management guidance are new to the wiki.

## Application for Scott

The article is the method sheet for handing off recurring quant work: turn-based for exploratory analysis (this session's stock screen), `/goal` for signal search with a Sharpe/backtest threshold, `/loop`/`/schedule` for market-hours monitoring, proactive routines for earnings-season sweeps. See [[Loop-Engineering]] §Applied to Quantitative Trading.
