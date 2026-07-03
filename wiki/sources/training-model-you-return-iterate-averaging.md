---
type: source
domain: ai-ml
title: "Training for the Model You Return: Improving Optimization for Iterate-Averaged Language Models"
authors:
  - "Kwok Chun Au"
  - "Adam Block"
institution: "Columbia University (CS + EE)"
arxiv: "2606.25086"
published: 2026-06-23
ingested_at: 2026-06-26
tags:
  - ml-optimization
  - iterate-averaging
  - language-model-training
  - adam
  - ema
  - optimal-control
domain: machine-learning
status: ingested
related:
  - "[[PACE Optimizer]]"
  - "[[Iterate Averaging in LLM Training]]"
  - "[[quantitative-finance]]"
---

# Training for the Model You Return: Improving Optimization for Iterate-Averaged Language Models

**Authors:** Kwok Chun Au, Adam Block (Columbia University)
**arXiv:** 2606.25086v1 — submitted 23 Jun 2026
**Domain:** ML optimization / LLM training

---

## One-Line Summary

Most LM training pipelines return an EMA of training iterates rather than the final checkpoint; this paper derives the theoretically optimal algorithm for that setting and instantiates it as **PACE** — a lightweight AdamW wrapper that strictly improves over AdamW + EMA across fine-tuning (1–2B param models) and GPT-2 pretraining.

---

## Core Problem

Modern LM pipelines return an *averaged* model (e.g., EMA of weights) rather than the final iterate. Prior work treated averaging as a post-hoc stabilizer. This paper asks:

> Given that we will return an iterate average, how should we *change training* to improve the performance of that average?

This reframes optimization as a problem about **the statistic of the full trajectory** rather than a single final point.

---

## Method: PACE (Pullback Averaging Control for Efficient Optimization)

### Derivation Path

1. **Quadratic continuous-time model**: dynamics follow an Ornstein–Uhlenbeck SDE with additive control input.
2. **Optimal control problem**: minimize squared error of the EMA estimator plus a penalty on control magnitude (linear-quadratic stochastic control / Riccati equation).
3. **Closed-form optimal controller** (Theorem 2): pull the live iterate toward the EMA point, weighted by curvature and remaining training time.
4. **Practical approximation**: two key approximations yield a simple per-step update —
   - replace the Bayesian posterior mean with the running EMA
   - assume `t << T` (early-training bias)
5. **Discretization + preconditioning**: replace diagonal curvature matrix with Adam's second-moment estimate `v_t`; replace fixed β with decaying `β_t = (1+t)^{-κ}`.

### PACE Update Rule (Algorithm 1)

At each step `t` (every `uf` steps in practice):

```
λ_{t,i} = min(η·c·(1+t)^{-κ} / (√v_{t,i} + ε),  1)     # clipped per-coordinate pullback gain
θ_t ← θ_t + λ_t ⊙ (θ^EMA_{t-1} − θ_{t-1})               # pullback toward EMA
θ^EMA_t ← (1 − β_t)·θ^EMA_{t-1} + β_t·θ_t               # EMA update
```

**Hyperparameters added over AdamW:**
- `c` — pullback strength (scalar; typically 3×10⁻³ works well)
- `κ` — EMA power / decay rate (0 < κ < 1; tested 0.2–0.7)
- `uf` — update frequency (how often pullback fires; 1, 5, or 10)

**Memory cost:** one additional copy of model weights (the EMA buffer). On large batch sizes this overhead is relatively minor.

**Special cases:**
- `c → ∞`: recovers the Lookahead optimizer
- `c = 0`: recovers AdamW + EMA

---

## Theoretical Results

**Theorem 3 (Convex guarantee):** For any convex, G-Lipschitz loss, PACE's iterate-average estimator converges at the same O(1/√T) rate as SGD, up to a constant factor depending on **C** and β. Never much worse than SGD.

**Proposition 2 (Quadratic improvement):** In the quadratic setting, there exists a choice of **C** such that PACE strictly achieves smaller limiting squared error than uncontrolled SGD. The improvement is provably arbitrarily large on some problem instances (Proposition 3).

Interpretation: PACE is at least as good as plain averaging in theory (up to constants), and can be strictly better when loss is locally quadratic — which is the common approximation in deep learning.

---

## Empirical Setup

| Model | Params | Task | Hardware |
|-------|--------|------|----------|
| SmolLM2-1.7B | 1.7B | Fine-tuning (smol-smoltalk) | NVIDIA RTX PRO 6000 |
| Qwen3-1.7B | 1.7B | Fine-tuning (smol-smoltalk) | NVIDIA RTX PRO 6000 |
| Gemma3-1B | 1.0B | Fine-tuning (smol-smoltalk) | NVIDIA RTX PRO 6000 |
| SmolLM2-135M | 135M | Fine-tuning ablations | NVIDIA RTX PRO 6000 |
| GPT-2-124M | 124M | Pretraining (FineWeb, 2.5B tokens) | Google Cloud TPU v6e |

Baselines: vanilla AdamW, AdamW + EMA, Schedule-Free (Defazio et al. 2024).

---

## Key Results

1. **Fine-tuning:** PACE strictly improves over AdamW and EMA on all three 1–2B models at all tested learning rates (Figure 1). Improvement is consistent across model families.

2. **Pretraining:** PACE outperforms AdamW and EMA baselines in GPT-2 pretraining under all three LR schedules — constant LR, cosine decay, and WSD (Figure 2).

3. **Hyperparameter robustness:** Optimal pullback strength `c` is broadly stable across learning rates and update frequencies (Figure 3). Small values (`c ≈ 3×10⁻³`) suffice.

4. **Schedule-free comparison:** PACE is competitive with Schedule-Free (SF) optimizer and outperforms SF + WSD in token-budget comparisons. SF requires one fewer model copy but runs slower in practice (12 vs 10 hours for 1.7B fine-tune on v6e TPU).

5. **LR decay robustness:** PACE strictly improves over AdamW + WSD baselines at equivalent token budgets, suggesting PACE as an effective alternative or complement to learning rate decay.

---

## Limitations

- Theoretical derivation assumes quadratic loss + constant LR; momentum and adaptive preconditioning are not in the proof.
- Scale only tested to 2B params (fine-tuning) and 124M (pretraining); efficacy at 7B+ unknown.
- Additional memory: one extra copy of model weights during training.
- Headline experiments use single seed 42 (multi-seed robustness confirmed in appendix Figs 17–18).

---

## Related Optimizers

| Method | Relation to PACE |
|--------|-----------------|
| AdamW + EMA | Baseline; PACE = AdamW + EMA + pullback term |
| Schedule-Free (Defazio 2024) | Also eliminates need for LR decay via averaging; different algorithm; competitive |
| Lookahead | Special case of PACE when `c → ∞` |
| AdEMAMix (Pagliardini 2024) | Averages gradients rather than iterates; more like momentum |
| EASGD (Zhang 2015) | Periodically transports live weights toward slow EMA; similar when pullback is large |

---

## Trading / Applied ML Relevance

See [[Iterate Averaging in LLM Training]] for the fuller concept note. Key implications for Scott's work:

- **Fine-tuning models for trading signals**: PACE could be a drop-in improvement when fine-tuning open-weight LLMs (Qwen, Gemma, SmolLM2) on domain-specific financial corpora. Demonstrated gains at 1–2B scale with minimal hyperparameter effort.
- **Optimizer choice for small-scale training**: PACE adds memory overhead of one model copy — at 135M–1B parameters this is modest. For strategy-relevant fine-tuning on one GPU, this is practical.
- **LR schedule flexibility**: PACE is competitive with cosine and WSD decay schedules, and works with constant LR. Useful when token budgets are uncertain.
- **AI consulting context**: Understanding that most production LM pipelines already use EMA and that PACE strictly improves this setup is a differentiating insight when advising clients on training pipelines or fine-tuning for vertical applications.

---

## Pages Created from This Source

- [[PACE Optimizer]] — full technical concept note on the algorithm
- [[Iterate Averaging in LLM Training]] — broader concept covering EMA, Polyak-Ruppert, and the training-vs-inference model distinction
