---
type: concept
title: "Loop Engineering"
status: mature
created: 2026-06-27
updated: 2026-06-27
domain: quantitative-finance
tags:
  - concept
  - loop-engineering
  - agentic-systems
  - quantitative-finance
  - automation
related:
  - "[[Maker-Checker-Pattern]]"
  - "[[loop-engineering-hedge-funds-2026]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
  - "[[Andrej Karpathy]]"
---

# Loop Engineering

**Definition** (Addy Osmani, Jun 2026): Loop engineering is replacing oneself as the person who prompts the agent, and designing the system that prompts the agent instead.

The practitioner is no longer *inside* the loop. They are *outside*, building the loop. The agent is no longer the tool. The system that orchestrates the agent is.

---

## The Shift in One Sentence

Old: sit at keyboard, prompt the agent line by line; it finishes, stops, waits; you are the human clock inside the loop.

New: write the loop once, walk away; the loop holds the clock; every iteration runs without a context switch.

This is "one floor above harness engineering." Harness engineering still assumed a human initiating each session. Loop engineering removes that assumption entirely.

---

## Origin

Spring 2026. Three practitioners converged in one week:
- Boris Cherny (Anthropic, Claude Code): "My job is to write loops that prompt the agent and decide what happens next."
- Peter Steinberger (OpenClaw): "Stop prompting coding agents. Design the loops."
- Addy Osmani (Google Chrome): coined the canonical definition above
- Andrej Karpathy: "Remove yourself as the bottleneck"

The predecessor terms — prompt engineering, context engineering, harness engineering — all assumed a human seated at the keyboard. Loop engineering deletes that assumption.

---

## Six Structural Primitives

A working loop requires all six. Missing any one produces a loop that appears to run while no compounding ever happens.

```
┌─────────────────────────────────────────────────────────┐
│                    LOOP SKELETON                        │
│                                                         │
│  AUTOMATION ──→ triggers without human typing           │
│  SKILL.md   ──→ procedure manual read every session     │
│  STATE.md   ──→ memory that survives between sessions   │
│  VERIFIER   ──→ independent judge; never the maker      │
│  WORKTREES  ──→ isolated dirs for parallel agents       │
│  CONNECTORS ──→ MCP links to external systems           │
└─────────────────────────────────────────────────────────┘
```

### Automation
Two flavors: `/loop` (reruns on a cadence regardless of state) and `/goal` (iterates until a verifiable stopping condition is true, with a separate evaluator). In trading: `/loop` drives data refresh; `/goal` drives signal search until Sharpe target is reached.

### SKILL.md — Persistent Knowledge
A procedure manual the agent reads at the start of every session. Holds conventions, hard rules, and accumulated lessons from past runs. Without it, every iteration starts from zero. With it, a lesson written today becomes a constraint tomorrow. After 1000 trades, SKILL.md surpasses any backtest: it contains rules paid for in real P&L.

### STATE.md — Loop Memory
A markdown file that survives between agent sessions. The agent forgets; the file does not. Agent reads it at the start of every run, writes the outcome at the end. This is the spine of every working loop. Sophistication added on top of an absent state file is wasted.

### Verifier — Independent Judge
The maker is the worst possible judge of its own output. The verifier is a second agent with different instructions (ideally a different model) with no exposure to the maker's reasoning trace. It applies deterministic threshold checks. See [[Maker-Checker-Pattern]].

### Worktrees — Parallel Isolation
Git worktrees give each agent its own isolated working directory. Without this, two agents writing to the same file produce silent corruption. With it, maker, checker, and risk monitor can run concurrently without contamination.

### Connectors — MCP
Model Context Protocol connectors let the loop reach external systems: broker API, databases, exchanges. This is the difference between a loop that *suggests* trades and a loop that *places* them.

---

## Applied to Quantitative Trading

Trading is the highest-stakes loop available to a private operator because it was already a five-stage recursive process (ingest → signal → validate → execute → monitor → repeat). Every serious institution runs exactly this cycle. Loop engineering automates each stage:

```
Data Ingestion  →  Maker (signal gen)  →  Checker (verify)  →  Execution  →  Risk Monitor
     ↑                                                                              ↓
     └─────────────────────────── STATE.md (shared memory) ──────────────────────┘
```

Full treatment: [[loop-engineering-hedge-funds-2026]].

The iteration cadence advantage is the key structural change. A 100-person quant desk cycles a research idea once per week. A loop of agents cycles the same idea every 15 minutes. The institution wins on capital and data exclusivity. It no longer wins on the loop.

---

## Economics of the Loop

Token costs: $40-90/day (Sonnet maker + Opus checker, ~5 candidates/hour).

Break-even capital: $100K-$250K deployed at 15% annualized expected return. Below $100K, token cost exceeds expected daily P&L. Above $250K, the loop is structurally advantageous and increasingly dominant as scale rises.

---

## Anti-Patterns

| Anti-pattern | Description |
|--------------|-------------|
| Cognitive Surrender | Operator stops reading agent reasoning; eventual inability to diagnose failure |
| Verification Rot | Verifier gates stale vs. current regime; system *feels* rigorous but passes almost everything |
| Comprehension Debt | Loop ships faster than operator can understand it; operator eventually can't make decisions without agent help |
| Token Blowout | No deterministic stopping condition; loop runs until half-finished trades are left open |

---

## Two Cautions

1. The loop compounds whatever signal the operator brings. No signal thesis: fast machine for losing money.
2. Verification gates matter more than maker quality. Brilliant maker + loose checker = compounds losses efficiently. Mediocre maker + strict checker = compounds slowly and survives.

---

## See Also

- [[Maker-Checker-Pattern]] — the most important single mechanism inside any trading loop
- [[loop-engineering-hedge-funds-2026]] — the source with the full five-stage architecture
- [[zhang2026-benchmarking-deep-ts-equity]] — signal generation research applicable to the maker stage
- [[das2026-chronos-multivariate-forecasting]] — foundation model applicable to Stage 1 (data ingestion/signal seeding)
