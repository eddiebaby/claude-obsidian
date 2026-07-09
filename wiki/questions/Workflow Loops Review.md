---
type: synthesis
title: "Workflow Loops Review"
created: 2026-07-08
updated: 2026-07-08
domain: quantitative-finance
address: c-000030
tags:
  - loop-engineering
  - workflow
  - productivity
  - claude-code
status: developing
question: "Given the ClaudeDevs loops article, what five changes to the current workflow would raise productivity the most?"
answer_quality: solid
related:
  - "[[ClaudeDevs-Getting-Started-with-Loops]]"
  - "[[Claude Code Loop Taxonomy]]"
  - "[[Loop-Engineering]]"
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[Sector-ETF Momentum Strategy]]"
  - "[[Retail Alpha Strategy Roadmap]]"
  - "[[Maker-Checker-Pattern]]"
  - "[[dashboard]]"
sources:
  - "[[.raw/2026-07-06-claudedevs-getting-started-with-loops.md]]"
---

# Workflow Loops Review

Review of the current working setup (2026-07-08) against the four-type loop taxonomy in [[ClaudeDevs-Getting-Started-with-Loops]]. The taxonomy is a ladder of delegation: turn-based loops hand off the check, goal-based the stop condition, time-based the trigger, proactive the prompt itself ([[Claude Code Loop Taxonomy]]).

## Where the workflow stands

The vault machinery is mature turn-based infrastructure: hot-cache SessionStart hooks, PostToolUse auto-commit, per-file advisory locks, and a pre-commit verifier agent — the article's "second agent with fresh context for review" recommendation, already implemented. But nearly everything runs turn-based: every session starts with a typed prompt and every result ends with a human reading the output. **The knowledge loops are industrialized; the money loops are almost entirely manual** — the sole exception is the [[Equity-Upside-Book-2026H2]] scheduled tasks (weekly Monday sweep + three catalyst one-shots, created 2026-07-08), the first time-based handoff in the vault. The five recommendations move the rest of the income-generating work up the delegation ladder.

## The five recommendations

### 1. Encode backtest verification as a skill — hand off the check

The verification discipline exists but lives in prose across wiki pages: [[Deflated-Sharpe-Ratio]], walk-forward IS/OOS split, net-of-costs accounting, benchmark comparison, per-strategy kill criteria. The article's claim: the more quantitative the check, the more the agent self-verifies — and these checks are maximally quantitative. A `verify-backtest` SKILL.md should require, before any sleeve is declared done: `walkforward.py` run, DSR reported, summary table vs SPY/equal-weight, and the kill criteria from the strategy page explicitly checked. Removes the human as the verification step on every quant iteration.

### 2. Use goal-based loops for the next strategy sleeves — hand off the stop condition

The [[LucidFlex Automated Scalping PRD]] build order (overnight drift, first-half-hour momentum) already has deterministic gates: ≥ 2 ticks/trade net before any eval dollar, PF ≥ 1.3 OOS, DSR threshold. That is exactly the article's `/goal` case: *"build the first-half-hour momentum sleeve in sector-momentum; done = walkforward passes, DSR reported, summary.csv row added; stop after 5 tries."* If `/goal` is unavailable, the same effect comes from putting the stop condition in the prompt plus the skill from #1 — the agent iterates against the gates instead of the human re-prompting each variant.

### 3. Schedule the monthly rebalance — hand off the trigger

`sector-momentum/` is a monthly-rebalance, market-on-close strategy — the textbook time-based loop (task constant, only inputs change). A `/schedule` routine on the last trading day of each month: run `data.py`, compute the current top-3 + T-bill overlay signal, file the rebalance note to the wiki. Turns a finished backtest into a live decision-support system. **Cheapest step from study to money in the repo — the code already exists and produces the signal.** Highest-priority item of the five.

### 4. Point a proactive loop at the consulting business — hand off the prompt

The 2026 consulting goal has zero artifacts anywhere in the vault; the `business` domain starves while depth-psychology and quant-finance compound daily (visible on [[dashboard]]). Prospecting is recurring, well-defined work — the article's proactive-loop fit. Weekly scheduled routine: research a handful of Hilo/Hawaii businesses, identify one concrete AI use case each, draft one outreach note, file to `wiki/business/`. A loop that runs without the operator is the one that survives the drift toward study.

### 5. When a loop stalls, fix the system, not the instance

The article: when a result fails the standard, encode the fix so all future iterations improve. Two live counterexamples as of 2026-07-08:

- `allocate-address.sh` broken on Windows (missing `flock`) since 2026-07-03; addresses hand-allocated in three sessions now (c-000003..25, c-000026..28, c-000030). Fix the script once — reuse `wiki-lock.sh`'s locking, which works.
- The auto-commit hook covers only `wiki/`, `.raw/`, `.vault-meta/`. App code sits outside any commit discipline: dream-app staged-but-uncommitted for days, sector-momentum and individuation-app untracked. The income-generating code has less durability than the dream journal. Extend commit discipline (or a Stop-hook reminder) to the app directories.

## Sequencing

Per the article's own advice — pick one task where the operator is the bottleneck, run it, observe, iterate. Here that is unambiguously **#3 (rebalance routine)**: the code is done and the loop pays. Then #1/#2 (they compound each other), then #4, with #5 as background hygiene.
