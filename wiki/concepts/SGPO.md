---
type: concept
title: "Semantic-Gradient-based Prompt Optimization (SGPO)"
status: mature
created: 2026-06-27
updated: 2026-06-27
domain: ai-ml
tags:
  - concept
  - ai-ml
  - prompt-optimization
  - self-evolving
  - agentic-systems
  - loop-engineering
related:
  - "[[agentx-kuaishou-2026]]"
  - "[[Loop-Engineering]]"
  - "[[Maker-Checker-Pattern]]"
---

# Semantic-Gradient-based Prompt Optimization (SGPO)

SGPO is the harness evolution mechanism in [[agentx-kuaishou-2026]]. It turns accumulated execution trajectories into natural-language "semantic gradients" that revise individual subagent prompts — making the system self-improving rather than merely automated.

**The insight**: standard agent improvement methods update model weights or retrieve more examples. SGPO instead updates the *harness specification* — the instructions, validation rules, output contracts, and tool-use discipline that govern how a subagent behaves. The target is not the recommendation strategy, but the agent controlling it.

---

## The Problem SGPO Solves

Online experiment analysis explains whether a recommendation strategy worked. It does not explain *why* the upstream agent failed to capture the right constraints, missed a business-causal chain, produced an incomplete handoff, or generated code that violated repository conventions. These are failures of the harness, not the strategy.

Without harness evolution, the loop starts from the same specification every run. It may compound strategies but it does not compound capability.

---

## How SGPO Works

Two-step process per evolution round:

### Step 1: Semantic Gradient Calculation

Given:
- Current harness specification for subagent i at evolution round t: h_{t,i}
- Sampled trace evidence T (compact rubrics, not full session verbatim)
- Extracted rubrics R (explicit task constraints + implicit constraints revealed during interaction)

An evaluator agent E_agent produces:
- A natural-language loss report l_{t,i}
- A semantic gradient g_{t,i}

```
l_{t,i}, g_{t,i} = E_agent(h_{t,i}; T, R)      (Eq. 7)
```

The semantic gradient g_{t,i} is **not a numerical derivative**. It is a structured diagnosis of:
- Missing constraints
- Weak step ordering
- Underspecified evidence requirements
- Incomplete downstream contracts

### Step 2: Semantic Gradient Update

A refinement agent R_agent converts the gradient into a local harness edit:

```
h'_{t,i} = R_agent(h_{t,i}, g_{t,i})            (Eq. 8)
```

The edit is limited to: the target subagent's instruction, validation rule, output contract, or tool-use discipline. It does not rewrite the full AgentX harness.

---

## Paired Replay Validation

After h'_{t,i} is generated, SGPO immediately evaluates old vs. new harnesses on the same replay tasks:
- Replay tasks are generated from the same trace pool: an LLM rewrites user queries + later user inputs into standalone tasks
- Each task preserves business domain, objective, guardrails, allowed change type, expected artifact, known constraints — while removing dependence on the original session context
- An improvement is only admitted when the new harness scores better on the replay set

This is the key safety constraint: **updates are admitted only through paired replay**. No online A/B, no human approval required — but the gate prevents the harness from being updated based on a single trace or a lucky outcome.

---

## Two Variants

### SGPO-I (Session Traces as Evidence)
Uses session traces from the accumulated online trace pool. Evaluator extracts compact rubrics from initial user query and later user inputs (these fields contain the explicit and implicit constraints most useful for diagnosis). Standard production deployment.

### SGPO-II (Model Research Exploration Loop)
Extends SGPO to the model-research track. Beyond single-paper reproduction, the same grounded knowledge drives a systematic exploration loop: reproduction → module ablation → cross-paper composition. The exploration memory accumulates:
- `anti_patterns`: failure modes with log and diff regexes for recognizing analogous failures in future runs
- `playbook`: successful recipes, recorded when ΔAUC > 0.001

Threshold gate: each candidate experience entry must pass two gates from at least two independent runs before entering future rounds.

Adversarial review gate: a dedicated agent attempts to falsify the claimed causal mechanism. Entries that survive become `confirmed`; disputed entries become `contested` (injected with a warning); falsified entries are permanently excluded.

---

## Why This Matters (vs. Standard Methods)

| Approach | What it updates | Self-improvement scope |
|----------|----------------|----------------------|
| Fine-tuning | Model weights | Broad but slow, requires labeled data |
| RAG / in-context retrieval | Context provided to model | No update to reasoning policy |
| Reinforcement from outcomes | Reward model / policy | Requires differentiable objective |
| **SGPO** | **Harness specification (prompt)** | **Local, inspectable, paired-replay-validated** |

Key advantage: updates are fully inspectable. Any score change can be isolated to a local harness edit rather than a sweeping system rewrite. This makes old-vs-new replays meaningful — the change surface is bounded.

---

## SGPO in the AgentX Loop

After three weeks of self-evolution in production:
- Concurrent experiments: 15 → 60 (4×)
- Idea pass rate: 15% → 45% (3×)
- Weekly launchable results: 2 → 5 (2.5×)

The system simultaneously expanded throughput and tightened selectivity. It no longer just produces more — it produces more of the right ideas, because SGPO tightened the harness constraints that define what "right" looks like.

---

## Applicability to Other Loops

SGPO generalizes to any [[Loop-Engineering]] deployment where:
1. Execution trajectories can be recorded (STATE.md equivalent)
2. A distinction exists between strategy failures and harness failures
3. Paired replay is feasible (same tasks rerunnable under old and new harness)

In a trading loop: SGPO would update the SKILL.md / verification rules based on *why* the maker's reasoning failed or *why* the checker's gates produced false positives — not just what the backtest result was. This is precisely what the loop engineering paper calls recalibrating against the STATE.md outcomes log, but now with an agent doing the diagnosis automatically.

---

## See Also

- [[agentx-kuaishou-2026]] — full architecture and results
- [[Loop-Engineering]] — the general framework SGPO's self-improvement mechanism extends
- [[Maker-Checker-Pattern]] — the verification layer that SGPO improves over time
