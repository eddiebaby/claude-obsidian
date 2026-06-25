---
name: adaptive-depth
type: concept
title: "Adaptive Depth"
status: developing
created: 2026-06-24
updated: 2026-06-24
tags:
  - architecture
  - computation
  - efficiency
  - neural-networks
related:
  - "[[Looped Transformers]]"
  - "[[Adaptive Computation Time]]"
  - "[[World Models]]"
  - "[[facemind-looped-world-models-2026]]"
---

# Adaptive Depth

## Definition

**Adaptive depth** is a technique where a neural network dynamically determines how many computational steps (iterations, layers) are needed for each input, rather than using a fixed depth.

Instead of:
```
All inputs → 10 layers → output
```

Adaptive depth:
```
Input 1 (simple) → [Block] → [Block] → exit (2 steps)
Input 2 (complex) → [Block] → [Block] → [Block] → [Block] → [Block] → exit (5 steps)
```

## Intuition

Complex inputs warrant deeper processing; simple inputs don't. Why waste computation on trivial problems?

**Example from world models**:
- Simple transition (free-flight): "object moves in straight line" → 1-2 loop iterations sufficient
- Complex transition (collision): "two objects collide, bounce, deform" → 4-5 iterations needed for accurate dynamics

---

## Implementation in LoopWM

At each loop iteration t, a learned **exit gate** evaluates whether to halt:

$$q^{(t)} = \sigma(w_g^T h^{(t)} + b_g)$$

where:
- **h^(t)**: latent state at iteration t
- **w_g**: learned weight vector
- **σ**: sigmoid (output ∈ [0, 1])

**Halt if** q^(t) > threshold τ (e.g., τ = 0.5). Otherwise, continue to next iteration.

## Training

During training, loop count **T** is sampled from a Poisson distribution with learnable mean μ_trc:

$$T \sim \text{Poisson}(\mu_{\text{trc}})$$

This encourages the model to learn variable-depth computation. Gradient backprop is truncated at μ_trc/2 steps to limit memory cost.

## Benefits

1. **Computational Efficiency**: Simple inputs exit early, saving FLOPs.
2. **Matched Complexity**: Allocate computation to where it's needed.
3. **Graceful Degradation**: Model scales smoothly between fast inference (low depth) and accurate inference (high depth).
4. **Planning Efficiency**: In world models, simple trajectories (e.g., "robot walks forward 5 steps") can be simulated with fewer iterations than complex trajectories (multi-agent interactions, physics).

## Trade-offs

### Pros
- Lower average inference cost
- Learned automatically (no manual tuning of depth per task)
- Combines speed and accuracy

### Cons
- Adds latency variance (some inputs fast, some slow)
- Exit gate adds parameters and complexity
- Hard to predict inference time (worst-case still requires max depth)

## Historical Context

Early adaptive-depth mechanisms:
- **Adaptive Computation Time (Graves, 2016)**: Halt mechanism with a learned "ponder" cost
- **BranchyNet (Teerapittayanon et al., 2017)**: Early-exit from intermediate layers
- **Mixture-of-Experts (Shazeer et al., 2017)**: Route inputs to varying-depth sub-networks

Modern applications:
- **DistilBERT** variants: early-exit heads on intermediate layers
- **LoopWM** (2026): First use in looped transformers for world modeling

---

**See also**: [[Looped Transformers]], [[Adaptive Computation Time]], [[World Models]]
