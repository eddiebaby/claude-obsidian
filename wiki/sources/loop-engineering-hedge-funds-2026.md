---
type: source
title: "Loop Engineering for Self-Improving Hedge Funds"
authors:
  - "Anonymous (independent practitioner)"
year: 2026
version: "v1.0 (reformatted from open practitioner essay v260615)"
status: ingested
domain: quantitative-finance
tags:
  - source
  - quantitative-finance
  - loop-engineering
  - agentic-trading
  - maker-checker
  - autonomous-systems
related:
  - "[[Loop-Engineering]]"
  - "[[Maker-Checker-Pattern]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
  - "[[das2026-chronos-multivariate-forecasting]]"
  - "[[Andrej Karpathy]]"
---

# Loop Engineering for Self-Improving Hedge Funds

Independent practitioner research note (v1.0). Reformatted from open essay v260615 into conference style. Applies the "loop engineering" concept (spring 2026 convergence among Boris Cherny, Peter Steinberger, Addy Osmani, Andrej Karpathy) to autonomous quantitative trading.

**Central claim**: a single operator with a correctly engineered loop now competes structurally with desks that historically required 100 quant researchers and engineers. The binding scarce resource is no longer headcount — it is verification rigor.

---

## Origin of the Term

Spring 2026, three independent practitioners converged in one week:
- **Boris Cherny** (Anthropic, Claude Code lead): "I no longer prompt the agent directly; my job is to write loops that prompt the agent and decide what happens next."
- **Peter Steinberger** (OpenClaw essay "Stop Prompting Coding Agents"): argued one should design loops, not prompt agents
- **Addy Osmani** (Google Chrome): formalized the definition — "loop engineering is replacing oneself as the person who prompts the agent, and designing the system that does it instead"
- **Andrej Karpathy**: "Remove Yourself as the Bottleneck"

---

## Six Structural Primitives

Every working loop requires all six. Missing any one breaks compounding silently.

| Primitive | Role |
|-----------|------|
| **Automation** | The heartbeat. `/loop` (cadence-based) or `/goal` (run until verifiable stopping condition). |
| **Skill** (`SKILL.md`) | Procedure manual the agent reads every session. Lessons from past runs compound here; constraints tighten over time. |
| **State** (`STATE.md`) | Loop memory that survives between agent sessions. Agent forgets; file does not. "The spine of every working loop." |
| **Verifier** | Separate agent with different instructions (ideally different model) whose only job is to grade the maker's output. The maker is the worst judge of its own work. |
| **Worktrees** | Git worktrees give each agent its own isolated working directory. Prevents collisions when maker, checker, and risk monitor run in parallel. |
| **Connectors** (MCP) | Model Context Protocol connectors link the loop to broker APIs, databases, exchanges. The difference between a loop that suggests trades and a loop that places them. |

---

## Five-Stage Trading Loop

```
Stage 1: Data Ingestion      (@loop, 1h cadence) → bars.parquet
Stage 2: Maker               (@loop, trigger=data) → pending_signal.json
Stage 3: Checker             (@checker, Opus-class) → pass/reject + rejection log
Stage 4: Execution           (@loop, trigger=verified signal) → MCP broker
Stage 5: Risk Monitor        (@loop, 1min cadence, separate worktree) → kill switch
                                          ↓
                             STATE.md (shared memory across all 5 stages)
```

Each stage runs in its own worktree, has its own skill file, and shares a common persistent STATE.md.

### Verification Gates (Checker, Stage 3)

The checker applies five deterministic thresholds and kills any signal that fails one:

| Gate | Threshold |
|------|-----------|
| Annualized Sharpe | > 1.5 |
| Maximum drawdown | < 10% |
| Newey-West t-statistic | > 2.0 |
| Out-of-sample period | >= 24 months |
| Sector exposure | < 30% |

The checker does not need to understand the strategy. It computes five numbers and applies five inequalities.

---

## Self-Improvement Mechanism

After every closed trade, both maker and checker log a one-paragraph retrospective into the relevant `SKILL.md`. Representative entry: *"2026-02-14, lost 4.2% during earnings week; new rule: skip any signal within 48 hours of an earnings release."*

After 100 trades, the skill file is a living rulebook. After 1000, it surpasses what any single quant could hold in working memory. The key claim: **SKILL.md surpasses backtests after 1000 trades** because it contains lessons paid for in real P&L, not reconstructable artifacts.

---

## Economics of Compute

| Capital | Expected daily P&L (15% annual) | Daily token cost | Economic? |
|---------|----------------------------------|-----------------|-----------|
| $50K | ~$20 | $40-90 | No — token bill exceeds P&L |
| $250K | ~$100 | $40-90 | Yes — margin to spare |
| $1M+ | $400+ | $40-90 | Structurally dominant |

**Break-even**: somewhere between $100K and $250K of deployed capital. Loop engineering is not yet economical for small accounts.

---

## Institutional Parallels

| Function | Institutional Desk | Loop-Engineered Solo |
|----------|-------------------|---------------------|
| Data ingestion | 5-10 engineers | Stage 1 sub-agent |
| Signal research | 20-40 quants | Maker sub-agent |
| Model validation | 10-20 quants | Checker sub-agent |
| Execution | Trading desk | MCP broker connector |
| Risk management | Risk team | Parallel worktree |
| Post-trade review | Performance team | STATE.md lessons |
| Iteration cadence | Days to weeks | Minutes to hours |
| Fixed annual cost | $25M-$60M | $15K-$40K |

**The institution still wins on**: capital scale, prime brokerage rates, exchange co-location, exclusive datasets. It no longer wins on the loop itself.

**Renaissance**: Medallion Fund = one extraordinarily well-tuned loop running for ~40 years. $1 compounded to ~$27,000 over 30 years. The lesson: they found a brilliant loop and let it compound, not a single brilliant signal.

---

## Production Observations

- **Rejection rate**: 40-60% of candidate signals killed before execution is healthy. Below 40% is a warning sign — usually indicates verifier looseness, not maker excellence.
- **Latency**: 4-12 seconds end-to-end (Sonnet maker, Opus checker). Too slow for HFT; adequate for intraday momentum/mean-reversion/event-driven.
- **Cognitive load ceiling**: 7 concurrent agents is comfortable; above 12, operator starts dropping information.
- **Worktree discipline**: most common error is running the risk monitor in the same worktree as the maker. When the maker drifts, the monitor drifts with it and the kill switch never fires.
- **Curiosity budget**: 2-4 hours/week reading agent reasoning (not just alarm-triggered). Operators who do this report noticeably better long-run outcomes.

---

## Anti-Patterns (Four Ways Loops Quietly Fail)

| Anti-pattern | What happens | Cure |
|--------------|-------------|------|
| **Cognitive Surrender** | Operator stops reading agent reasoning; merges everything that compiles | Forced curiosity: fixed budget of attention per week |
| **Verification Rot** | Verifier tuned once, 6 months ago; market regime changed; gates still trigger occasionally but almost everything passes | Schedule recalibration loop against STATE.md outcomes log |
| **Comprehension Debt** | Loop ships faster than operator can understand; eventually operator can't make decisions without agent's help | Treat comprehension as a first-class cost |
| **Token Blowout** | No stopping condition checkable by something other than the agent's own claim | Every stopping condition must be a deterministic inequality over an observable variable |

---

## Two Cautions (Conclusion)

1. The loop does not manufacture alpha out of nothing. It compounds whatever signal the operator brings into it. Arrive without a research thesis: get a fast machine for losing money.
2. The verification gates matter more than the maker. A brilliant maker + loose checker = learns to lose efficiently. A mediocre maker + strict checker = compounds slowly and survives.

---

## See Also

- [[Loop-Engineering]] — the concept page with the core framework
- [[Maker-Checker-Pattern]] — the maker-checker split as institutional pattern
- [[zhang2026-benchmarking-deep-ts-equity]] — model selection and backtesting in the quant loop
- [[das2026-chronos-multivariate-forecasting]] — foundation model signal generation
- [[Andrej Karpathy]] — originator of the LLM wiki pattern; cited here for "remove yourself as bottleneck"
