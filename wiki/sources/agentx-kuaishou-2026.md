---
type: source
title: "AgentX: Towards Agent-Driven Self-Iteration of Industrial Recommender Systems"
authors:
  - "AgentX Team (Kuaishou)"
year: 2026
arxiv: "2606.26859"
submitted: 2026-06-25
status: ingested
domain: ai-ml
tags:
  - source
  - ai-ml
  - agentic-systems
  - loop-engineering
  - self-evolving
  - recommender-systems
  - SGPO
related:
  - "[[Loop-Engineering]]"
  - "[[Maker-Checker-Pattern]]"
  - "[[SGPO]]"
---

# AgentX: Towards Agent-Driven Self-Iteration of Industrial Recommender Systems

Kuaishou production deployment (Jun 2026). AgentX is a multi-agent system that replaces human algorithm engineers in the idea-to-rollout loop for industrial recommender systems. It demonstrates at scale that agentic self-iteration delivers compounding returns in real A/B production environments.

**Central claim**: The bottleneck is no longer algorithmic — it is operational. 91.4% of experiment failures trace to infrastructure constraints and resource conflicts, not agent reasoning quality.

---

## Architecture: Four Stages in a Closed Loop

```
Brainstorm Agent → Developing Agent → Evaluation Agent
       ↑                                      |
       └────── Harness Evolution (SGPO) ──────┘
                    (trajectory → semantic gradient → prompt edit)
```

### Stage 1: Brainstorm Agent
Converts vague business intent into a ranked set of executable experiment proposals. Solves the *ambiguity problem*: input is intentionally under-specified; output must be operationally precise.

**Four evidence sources** (K = {Experiment KB, System KB, Data Analysis, Model Research}):
- **Experiment KB**: historical launch reviews, past experiment conclusions, documented lessons. Prevents rediscovering known failures.
- **System KB**: model architecture, feature definitions, DSL behavior, pipeline boundaries. Built as a structured domain wiki (ingest-query-lint lifecycle). Rejects ideas that violate pipeline constraints before coding.
- **Data Analysis**: SQL-based empirical checks. Grounds candidate ideas in observed data patterns rather than intuition.
- **Model Research**: converts paper claims into production-feasible proposals by checking against feature contracts and training constraints.

**Three proposal maturity states**: READY-TO-IMPLEMENT (concrete target, enough evidence), PROBE-FIRST (promising but needs a data/source check), MOONSHOT-BACKLOG (preserve for future capability).

**Candidate scoring** (Eq. 4): S(c|q) = λ_o·O + λ_b·B + λ_f·F + λ_h·H + λ_e·E(c|q) − λ_r·R

Where O = objective alignment, B = business validity, F = implementation feasibility, H = handoff completeness, E = weighted evidence across K, R = risk penalty.

### Stage 2: Developing Agent
Two tracks:

**Online strategy track**: turns proposal into production code artifact. Repository-grounded generation using schema query tools (must query attribute structs before use; field names become verified facts, not LLM guesses), ranking DSL checker (compiler-backed), C++ syntax checker, auto-evolving static linter.

Eight-dimensional quality scoring Q_code (weights sum to 1):
| Factor | Weight | Severity |
|--------|--------|----------|
| Attribute hallucinations (N3) | 22% | S |
| Correctness loop iterations (N6) | 18% | S |
| Manual operator interventions (N7) | 18% | S |
| Harness pattern violations (N2) | 12% | A |
| Dryrun pipeline passes (N8) | 10% | A |
| Ranking DSL corrections (N4) | 8% | A |
| C++ syntactic-sugar violations (N1) | 6% | B |
| C++ syntax check corrections (N5) | 6% | B |

**Offline model track**: training experiment artifacts. Policy declares causal mechanism + expected observables. Expert panel (N isolated agents, supermajority ≥ 2N/3 by Python vote counting, never LLM). AUC extracted by deterministic regex from raw training logs — no LLM interpretation of metrics. Falsifiable attribution: all causal-chain links must be verified/broken/unclear; UNCLEAR = brake signal (result not recorded).

*Key principle*: An LLM is permitted to be wrong only on judgment; every objective fact is produced by deterministic code.

### Stage 3: Evaluation Agent
Closes the production loop. Not a reporting module — it turns real online A/B feedback into the authoritative reward signal and reusable constraints for future iterations.

**A/B judgement**: KEEP / EXTEND / DISCARD verdict. Statistical methods: CUPED (variance reduction when pre-experiment history available), difference-in-differences, or direct group comparison.

**Guardrail design** (three principles):
1. Business-scoped, not universal: each domain (consumption, live streaming, e-commerce, advertising) has its own guardrail calibration
2. Composite economic-exchange metrics (LTV exchange score), not single-indicator vetoes
3. Thresholds are attention signals, not absolute blocks: hard block for severe deterioration, escalation for moderate, monitoring-only for observation metrics

**Negative-result assetization**: DISCARD results are written with root cause, indexed by pipeline stage, business objective, affected segment, strategy lever. These become pruning constraints for future brainstorming. Prevents rediscovering failed directions.

### Stage 4: Harness Evolution (SGPO)
See [[SGPO]] for the full technical treatment.

Semantic-Gradient-based Prompt Optimization. Turns accumulated execution trajectories into natural-language "semantic gradients" that revise individual subagent prompts. Updates one subagent specification at a time; the rest of AgentX remains fixed. Admitted only through paired replay (old vs. new harness on same tasks).

---

## Experimental Results (3-week Kuaishou App Deployment)

**Setup**: 3 AgentX workers, 2 production scenarios (main feed recommendation + life-service commercialization), Kuaishou App.

**Conversion funnel** (Table 5, Eq. 10):
```
374 ideas → (28.34% idea pass) → 106 passed → (94.3% code-and-launch) → 100 launched → (9.9% positive eval) → 10 LR
```

**Per-worker productivity vs. human algorithm engineer** (Table 8):

| Metric (per worker-week) | AgentX | Engineer | Ratio |
|--------------------------|--------|----------|-------|
| Concurrent experiments | 12 | 1.5 | **8×** |
| LR Count | 1.1 | 0.08 | **13.8×** |
| Cumulative app-time gain | 0.0623% | 0.0167% | **3.7×** |
| Per-idea rollout conversion | 2.7% | 5.1% | **0.53×** |

AgentX loses on per-idea precision (humans hand-pick; agents produce volume). Wins decisively on realized business value per unit human capacity.

**Business gains from 10 LRs**:
- Main Feed: +0.561% cumulative user app consumption time gain
- Life Service: >RMB 100M annualized revenue

**Self-evolution over 3 weeks** (Figure 10):
- Concurrent experiments: 15 → 60 (4×)
- Idea pass rate: 15% → 45% (3×)
- Weekly LRs: 2 → 5 (2.5×)

---

## Key Diagnostic Findings

**What blocks ideas (Table 6)**: 91.4% of 268 rejected ideas trace to platform/infrastructure constraints:
- 64.7%: parameter-resource conflict (target already held by holdout or in-flight experiment)
- 12.2%: operational frictions (enable flags off, duplicates, infeasible DSL)
- 14.5%: missing user/item attribute in feature store

Only 8.7% are genuine agent reasoning failures.

**Implication**: the bottleneck is operational, not algorithmic. The highest-leverage next step is an *upstream conflict checker* that queries AB-platform state before brainstorming, so resource-locked parameters never enter the candidate pool.

**What causes coding failures (Table 7)**: >95% are infrastructure-side:
- 35%: DSL/force-enable wiring errors
- 20%: C++/MaTX compiler constraint violations
- 15%: mis-structured if/else across parallel ideas

Genuine algorithmic mistakes by the coding agent: under 5%.

---

## Showcase: PCV-Enhanced Constrained Fine-Ranking

Two-loop iteration demonstrating closed feedback:

**Loop 1** (Direct PCV boosting): S₁ = B_r · (1 + βP). Result: weak positive but too noisy (active devices −0.023%, 18-30 age segment −0.032%). Diagnosed: all high-PCV content boosted without quality gating.

**Loop 2** (Constrained PCV ranking): S₂ = B_d · (1 + β(u)·G(P)), where G(P) = max(P − τ, 0) quality-gated PCV, β(u) activity-aware dynamic weight. Result: user watch time +0.071%, real-show +0.118%, guardrails stable.

The second loop used Loop 1's failure diagnosis as its starting evidence — demonstrating cumulative improvement across iterations.

---

## Connections to Loop Engineering Framework

AgentX maps to the [[Loop-Engineering]] six primitives:
| Loop Primitive | AgentX Implementation |
|----------------|----------------------|
| Automation | Agent-driven closed loop, no human stitching |
| Skill | System KB + Experiment KB (the wiki that grounds brainstorming) |
| State | Trajectory Memory (persistent across all sessions) |
| Verifier | Evaluation Agent + guardrail-veto A/B judgement |
| Worktrees | Parallel idea processing, concurrent experiments |
| Connectors | OpenAPI Gateway to production AB infrastructure |

The [[Maker-Checker-Pattern]] maps to: Brainstorm (maker) → Developing (coder) → Evaluation (checker with real-world reward). But AgentX adds a fourth layer — SGPO (harness evolver) — that the original two-agent maker-checker pattern doesn't have.

---

## See Also

- [[SGPO]] — Semantic-Gradient-based Prompt Optimization; the self-improvement mechanism
- [[Loop-Engineering]] — the general framework AgentX instantiates at industrial scale
- [[Maker-Checker-Pattern]] — the core verification pattern, extended here to a four-stage loop
