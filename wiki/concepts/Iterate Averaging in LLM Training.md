---
type: concept
title: "Iterate Averaging in LLM Training"
aliases:
  - "Polyak-Ruppert Averaging"
  - "EMA in LLM training"
  - "iterate averaging"
  - "model weight averaging"
status: developing
created: 2026-06-26
updated: 2026-06-26
tags:
  - ml-optimization
  - iterate-averaging
  - ema
  - lm-training
  - stochastic-optimization
domain: machine-learning
related:
  - "[[PACE Optimizer]]"
  - "[[training-model-you-return-iterate-averaging]]"
  - "[[World Models]]"
source: "[[training-model-you-return-iterate-averaging]]"
---

# Iterate Averaging in LLM Training

Iterate averaging is the practice of returning a running average of model weights during training rather than the final checkpoint. It is ubiquitous in modern language model training and is the foundational assumption behind the PACE optimizer.

---

## What It Is

During SGD or Adam training, weight parameters `θ_t` trace a noisy trajectory around the loss minimum. The final checkpoint `θ_T` is just one noisy sample from that trajectory. An **iterate average** reduces noise by averaging across the trajectory:

**Polyak-Ruppert (uniform) average:**
```
θ̄_T = (1/T) Σ_{t=0}^{T-1} θ_t
```

**Exponential moving average (EMA):**
```
θ^EMA_t = (1 − β_t) · θ^EMA_{t-1} + β_t · θ_t
```

With decaying `β_t = (1+t)^{-κ}` (κ ∈ (0,1)), the EMA up-weights recent iterates. At κ=1 this recovers uniform averaging. Modern pipelines use decaying EMA (BEMA) as the default.

---

## Why It Matters

**Theoretical motivation:** Polyak (1992) and Ruppert (1988) proved that the uniform iterate average of SGD achieves the optimal statistical rate for stochastic convex optimization. The final iterate alone does not.

**Practical motivation in LMs:**
- EMA of weights produces smoother, more generalizable models.
- Stabilizes training — the EMA serves as a "shadow" model less sensitive to noisy gradient steps.
- Virtually all modern open-source LMs (SmolLM2, Qwen, OLMo, Gemma) return an EMA checkpoint rather than the raw final iterate.
- Model soups (Wortsman 2022) — averaging weights of multiple fine-tuned checkpoints — are a related technique that also exploits iterate/weight averaging.

---

## The Training–Inference Model Gap

A subtle but important issue: standard optimization algorithms (SGD, Adam, AdamW) are designed to minimize the loss at the **final iterate**. But if the *returned* model is an EMA, the optimizer's objective is misaligned with what actually gets deployed.

This misalignment motivates the core question of Au & Block (2026):

> Given that we will return an iterate average after training, how should we modify optimization algorithms to minimize the loss of the returned weights?

This is the insight behind [[PACE Optimizer]].

---

## Variants and Taxonomy

| Method | Description | When used |
|--------|-------------|-----------|
| Polyak-Ruppert (uniform) | Plain arithmetic mean of all iterates | Classic theory; rarely used in DL practice |
| EMA (constant β) | Fixed exponential decay | Simple, common |
| BEMA / decaying β | β_t decays as training progresses; upweights recent | State-of-the-art in LM training |
| Stochastic weight averaging (SWA) | Average checkpoints at end of cyclical LR | Fine-tuning, wider optima |
| Model soups | Average multiple independently fine-tuned models | Post-hoc ensemble; no training cost |
| Schedule-Free (Defazio 2024) | Iterate averaging replaces LR schedule entirely | Removes need for LR decay |

---

## Key Empirical Facts (from Au & Block 2026)

- EMA consistently outperforms the final iterate across fine-tuning and pretraining benchmarks.
- The optimal EMA power κ varies by task but κ ≈ 0.5 is robust.
- PACE (pulling live weights toward EMA during training) strictly improves over passive EMA.
- The improvement is robust to learning rate, decay schedule, model family, and parameter count (1B–2B tested).

---

## Connection to Control Theory

The key theoretical contribution of [[PACE Optimizer]] is reframing iterate averaging as an optimal control problem:

- The training trajectory is a stochastic process (Ornstein–Uhlenbeck in the continuous-time quadratic model).
- The optimizer's modifications are a **control input** applied to the dynamics.
- The objective is to minimize the squared error of the time-average (the EMA) subject to a penalty on the size of the intervention.
- This is a **linear-quadratic Gaussian (LQG) problem** solvable via the Riccati equation.

The optimal controller turns out to be a simple pullback toward the EMA — PACE.

---

## Practical Takeaways

1. **If you're fine-tuning an open-weight LLM, use EMA by default.** Most frameworks (HuggingFace Trainer, PyTorch Lightning) support it natively.
2. **PACE is the next step** — a low-overhead improvement that pulls live weights toward EMA during training. Roughly 3 new hyperparameters with low sensitivity.
3. **Learning rate schedule and iterate averaging interact.** WSD (warmup-stable-decay) combines well with averaging; constant LR + PACE approaches WSD performance.
4. **The returned checkpoint matters.** When evaluating training runs, always compare EMA checkpoints, not raw final-iterate checkpoints — the EMA is what gets deployed.

---

## For Scott's Applications

**Trading model fine-tuning:** When fine-tuning an LLM on financial text or instruction-following for trading analysis, iterate averaging (especially PACE) is likely to produce a better deployed model than raw AdamW. The gains are most visible in low-data-budget fine-tuning settings where noisy gradients dominate.

**AI consulting:** Understanding the training–inference model gap (the model returned vs. the model trained) is a subtle but impactful insight for clients who are training or fine-tuning LLMs. Many teams evaluate their optimizer on the live-iterate loss and miss that the EMA is what ships.

**Related:** [[PACE Optimizer]] — the concrete algorithm; [[World Models]] — context for where LM optimization fits in broader AI system design.
