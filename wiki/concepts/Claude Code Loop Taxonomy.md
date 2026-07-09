---
type: concept
title: "Claude Code Loop Taxonomy"
created: 2026-07-08
updated: 2026-07-08
domain: ai-ml
address: c-000027
tags:
  - concept
  - ai-ml
  - loop-engineering
  - claude-code
  - agentic-systems
status: developing
complexity: intermediate
aliases:
  - "loop types"
  - "agent loops"
  - "four loop types"
related:
  - "[[Loop-Engineering]]"
  - "[[ClaudeDevs-Getting-Started-with-Loops]]"
  - "[[Maker-Checker-Pattern]]"
sources:
  - "[[ClaudeDevs-Getting-Started-with-Loops]]"
---

# Claude Code Loop Taxonomy

Anthropic's official classification of agent loops (Claude Code team, Jul 2026). A loop = an agent repeating cycles of work until a stop condition is met. Four types, ordered by how much of the work you hand off.

## The taxonomy

| Type | Triggered by | Stops when | Primitive | Best for |
|------|-------------|-----------|-----------|----------|
| **Turn-based** | User prompt | Claude judges task done / needs context | Verification skills | Short, one-off tasks |
| **Goal-based** | Manual prompt | Goal met OR turn cap | `/goal` | Verifiable exit criteria |
| **Time-based** | Time interval | You cancel, or work completes | `/loop` (local), `/schedule` (cloud) | Recurring work; polling external systems |
| **Proactive** | Event or schedule, no human | Each task exits at goal; routine runs until disabled | All of the above + dynamic workflows + auto mode | Recurring streams of well-defined work |

The progression is a ladder of delegation: turn-based hands off **the check**, goal-based hands off **the stop condition**, time-based hands off **the trigger**, proactive hands off **the prompt itself**.

## Design rules that make loops work

1. **Deterministic stop criteria.** `/goal` uses a separate evaluator model to test the condition each time Claude tries to stop. "Tests pass" or "score ≥ 90" beats "looks good."
2. **Encode verification as skills.** Turn a manual review checklist into `SKILL.md` with tools that let the agent see/measure the result. Quantitative checks → self-verification.
3. **Fresh-context reviewer.** A second agent unexposed to the maker's reasoning is less biased — the official version of [[Maker-Checker-Pattern]].
4. **Encode failures into the system.** Fixing one bad result is linear; encoding the fix as a skill/convention compounds across all future iterations.
5. **Token discipline.** Right-size primitive and model; pilot workflows on a slice; script deterministic steps; match cadence to the watched system's rate of change.

## Relation to Loop-Engineering

[[Loop-Engineering]] (practitioner convergence, spring 2026) is the *stance*: remove yourself as the prompter, build the system that prompts. This taxonomy is the *vendor's instruction set* for that stance — which primitive implements which delegation level. The six structural primitives (automation, SKILL.md, STATE.md, verifier, worktrees, connectors) map onto it: automation = the trigger column, verifier + SKILL.md = the check, STATE.md/worktrees/connectors = the infrastructure every type shares.

## Quant application

- Turn-based: exploratory research, one-off screens.
- Goal-based: "iterate on this signal until out-of-sample Sharpe ≥ X, stop after N tries."
- Time-based: refresh data, poll positions/PRs, morning market summaries.
- Proactive: earnings-season sweeps, triage of incoming fills/alerts — the five-stage trading loop in [[loop-engineering-hedge-funds-2026]] is a proactive loop.
