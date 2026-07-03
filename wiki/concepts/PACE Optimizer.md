---
type: concept
title: "PACE Optimizer"
aliases:
  - "Pullback Averaging Control for Efficient Optimization"
  - "PACE"
status: developing
created: 2026-06-26
updated: 2026-06-26
tags:
  - ml-optimization
  - lm-training
  - iterate-averaging
  - optimal-control
  - adamw
domain: machine-learning
related:
  - "[[Iterate Averaging in LLM Training]]"
  - "[[training-model-you-return-iterate-averaging]]"
  - "[[World Models]]"
  - "[[Looped Transformers]]"
source: "[[training-model-you-return-iterate-averaging]]"
---

# PACE Optimizer

**PACE** (Pullback Averaging Control for Efficient Optimization) is an AdamW wrapper derived from an optimal-control formulation of the iterate-average estimator problem. It adds a single per-step "pullback" that nudges the live model weights back toward the EMA checkpoint, thereby steering the training trajectory to improve the quality of the final returned average.

Introduced by Kwok Chun Au and Adam Block (Columbia University), arXiv 2606.25086, June 2026.

---

## The Core Idea

Standard LM training with EMA is passive: the EMA follows wherever the live weights go. PACE makes the relationship bidirectional — the live weights are also pulled *toward* the EMA, creating a controlled feedback loop that reduces the expected error of the returned average.

Intuitively: if the live iterate wanders far from the EMA, the return model (which is the EMA) suffers. PACE taxes that wandering by gently pulling the live weights back into a region consistent with good average performance.

---

## Algorithm

**Inputs:** learning rate η, pullback strength c, EMA power κ, scale ε, update frequency uf.

```
Initialize: θ^EMA_0 ← θ_0

For t = 1, 2, ..., T:
  1. Take AdamW step:
       θ_t ← AdamW.step(θ_{t-1}; η)
       v_t ← AdamW.preconditioner(θ_t)   # Adam's 2nd-moment estimate

  2. Every uf steps — apply pullback:
       λ_{t,i} = min( η·c·(1+t)^{-κ} / (√v_{t,i} + ε),  1 )
       θ_t ← θ_t + λ_t ⊙ (θ^EMA_{t-1} − θ_{t-1})

  3. EMA update:
       β_t = (1+t)^{-κ}
       θ^EMA_t ← (1 − β_t)·θ^EMA_{t-1} + β_t·θ_t

Return: θ^EMA_T
```

### Hyperparameters (beyond AdamW)

| Parameter | Symbol | Typical range | Role |
|-----------|--------|---------------|------|
| Pullback strength | `c` | 3×10⁻³ – 10⁻¹ | How hard to pull toward EMA |
| EMA power | `κ` | 0.2 – 0.7 | Controls EMA decay rate / memory |
| Update frequency | `uf` | 1, 5, 10 | Steps between pullback applications |

`c` is the key knob. Small values (c ≈ 3×10⁻³) already provide substantial gains; the optimal value is relatively stable across learning rates and model families.

### Pullback Gain Interpretation

The per-coordinate gain `λ_{t,i}` has a natural structure:
- Scaled by the Adam preconditioner `1/√v_t`: coordinates with high curvature get a smaller pullback (they're already near the right value; noisy).
- Decays as `(1+t)^{-κ}`: less intervention as training matures (when the EMA is presumably more accurate).
- Clipped at 1: ensures the update is always a convex combination of current iterate and EMA (never overshoots).
- When clipped = 1, PACE fully transports that coordinate to the EMA value — recovers the Lookahead optimizer on that coordinate.

---

## Theoretical Guarantees

**Convex setting (Theorem 3):** For any convex G-Lipschitz loss, PACE's flat iterate-average converges at O(1/√T), the standard SGD rate, up to a constant factor from **C** and β. PACE is never significantly worse than plain SGD.

**Quadratic setting (Propositions 2–3):** In the quadratic model from which PACE is derived:
- There exists a **C** such that PACE strictly achieves smaller limiting squared error than uncontrolled SGD.
- This improvement can be **arbitrarily large** on certain quadratic instances (for appropriate choices of **C** and β).

Interpretation: PACE is theoretically safe to use (bounded penalty vs. SGD), and can be drastically better when the loss is locally quadratic — which is standard in practice.

---

## Derivation Sketch

1. Model training as Ornstein–Uhlenbeck dynamics on a quadratic: `dθ_t = [A(μ* − θ_t) + u_t]dt + Σ^{1/2} dW_t`
2. Return statistic: the time-average `θ^EMA_T = (1/T)∫θ_t dt`
3. Control objective: `J_T(u) = E[‖θ^EMA_T − μ*‖²] + λ∫‖u_t‖² dt`
4. Optimal controller (Theorem 2, via Riccati equation): pull toward current EMA point; weight by curvature and remaining time.
5. Practical approximation: replace posterior mean with running EMA; assume `t << T`; discretize; use Adam's `v_t` as curvature proxy.

---

## Empirical Results Summary

Tested on fine-tuning (SmolLM2-1.7B, Qwen3-1.7B, Gemma3-1B) and pretraining (GPT-2-124M on FineWeb):

- **Strictly improves** over AdamW and AdamW+EMA on all fine-tuning tasks at all tested learning rates.
- **Strictly improves** over pretraining baselines under constant LR, cosine decay, and WSD schedules.
- **Competitive** with Schedule-Free optimizer (Defazio 2024); PACE trains faster in wall-clock time (10h vs 12h for 1.7B on v6e TPU).
- Optimal `c` is robust to learning rate choice and update frequency (Figure 3 in source).

---

## Practical Notes

- **Memory:** requires one additional copy of model weights (the EMA buffer). At 1–2B parameters, this is significant but manageable.
- **Integration:** wraps AdamW — just add pullback after AdamW step. No changes to gradient computation.
- **LR schedules:** works with constant LR, cosine, and WSD. Best overall results come from combining PACE with a decay schedule, though constant LR + PACE beats WSD + AdamW alone.
- **Scale limit:** tested to 2B (fine-tuning) and 124M (pretraining); efficacy at 7B+ not yet demonstrated.
- **Future:** potential to reduce memory by 1× if the pullback term alone can substitute for momentum (preliminary open question from authors).

---

## Relation to Other Optimizers

| Optimizer | Relationship |
|-----------|--------------|
| AdamW + EMA | PACE = AdamW + EMA + pullback; at c=0 they are identical |
| Schedule-Free | Competitive performance; different algorithm; SF removes need for LR schedule |
| Lookahead | PACE recovers Lookahead when all λ_{t,i} are clipped to 1 (large c) |
| AdEMAMix | Averages gradients not iterates; different mechanism |
| EASGD | Similar spirit (transport toward slow EMA) but different derivation and scale |

---

## For Scott's Trading / ML Work

This is a practical, drop-in improvement to AdamW for anyone fine-tuning open-weight LLMs. The three new hyperparameters are low-sensitivity (c ≈ 3e-3, κ ≈ 0.5, uf ∈ {1,5,10} all work). If fine-tuning a model on financial text or proprietary signals, PACE should be the default over plain AdamW + EMA at no meaningful additional engineering cost.

See also: [[Iterate Averaging in LLM Training]] for broader context on why EMA is ubiquitous in production LM pipelines.
