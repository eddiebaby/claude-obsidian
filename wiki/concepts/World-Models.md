---
name: world-models
type: concept
title: "World Models"
status: mature
created: 2026-06-24
updated: 2026-06-24
tags:
  - reinforcement-learning
  - generative-models
  - planning
  - embodied-AI
  - simulation
related:
  - "[[Looped Transformers]]"
  - "[[Adaptive Depth]]"
  - "[[Deferred Decoding]]"
  - "[[facemind-looped-world-models-2026]]"
---

# World Models

## Definition

A **world model** is a learned neural network that predicts how an environment evolves in response to agent actions. Given current observations and an action, the model predicts the next observation, reward, and termination signal.

**Function**: 
$$\hat{o}_{k+1}, \hat{r}_k, \hat{c}_k = \text{WM}(o_k, a_k)$$

where:
- **o_k**: current observation
- **a_k**: action taken
- **ô_{k+1}**: predicted next observation
- **r_k**: predicted reward
- **c_k**: predicted continuation (not-terminal) signal

## Why World Models Matter

### Motivation: The Sample Efficiency Problem

Standard RL (DQN, PPO, etc.) requires millions of environment interactions to learn policies. In robotics, games, or simulations, every environment step is expensive (real-world robots, rendering, simulation physics).

**World models enable**:
1. **Model-based RL**: Plan actions by simulating trajectories in the learned world model rather than the real environment.
2. **Sample Efficiency**: Reduce real environment interactions by 10-100×.
3. **Imagination-based Training**: Train the policy on imagined rollouts (dreamer-style learning).
4. **Offline RL**: Pre-train on logged data; use the world model to bootstrap policy learning.

### The Tension: Fidelity vs. Cost

To be useful for long-horizon planning, world models must:
- Predict **faithfully** over many steps (low error accumulation)
- Remain **computationally tractable** (can't be infinitely deep)

This is the core problem LoopWM solves.

---

## Architecture Components

### 1. Observation Encoder (ℰ_o)

Maps raw observation (image, sensor readings) to a compact latent representation:

$$e_k = \mathcal{E}_o(o_k) \in \mathbb{R}^d$$

- Typically a CNN for images
- Reduces dimensionality, extracts features relevant for prediction

### 2. Action Embedding (𝒜)

Projects action into the same latent space:

$$u_k = \mathcal{A}(a_k) \in \mathbb{R}^d$$

### 3. Latent Dynamics Core (ℒ_d)

The heart of the model: predicts next latent state given current state and action:

$$h_{k+1} = \mathcal{L}_d(h_k, e_k, u_k)$$

**Standard designs**:
- **RSSM** (Recurrent State-Space Model; Hafner et al., 2020): LSTM + sampling latent variables → stochastic predictions
- **Transformer-based**: Multi-head attention over history
- **Looped**: Iteratively refine latent state (LoopWM)

### 4. Prediction Heads

Decode latent state to observation and RL signals:

$$\hat{o}_{k+1} = \mathcal{D}(\tilde{h}_{k+1})$$
$$\hat{r}_k = R(\tilde{h}_{k+1})$$
$$\hat{c}_k = C(\tilde{h}_{k+1})$$

where ℒ denotes a lightweight MLP.

---

## Training Objective

Combine observation prediction, reward prediction, and continuation prediction:

$$\mathcal{L}_{\text{wm}} = \mathbb{E}[\ell_{\text{obs}}(\hat{o}, o) + \lambda_r \ell_r(\hat{r}, r) + \lambda_c \ell_c(\hat{c}, c)]$$

- **ℓ_obs**: MSE or perceptual loss (reconstruction)
- **ℓ_r**: MSE or cross-entropy (reward prediction)
- **ℓ_c**: binary cross-entropy (continuation/termination)

## Usage Patterns

### 1. Dreaming (Imagination-Based Training)

After training the world model, use it to generate imagined trajectories:

1. Encode real observation: $h_0 = \mathcal{E}_o(o_0)$
2. Sample action from policy: $a_0 \sim \pi(h_0)$
3. Imagine next state: $h_1 = \mathcal{L}_d(h_0, u_0)$
4. Decode: $\hat{o}_1 = \mathcal{D}(h_1)$
5. Repeat for K steps (dreaming horizon)
6. Use imagined trajectory to train policy via RL loss

**Benefits**:
- Policy sees diverse imagined environments, not just real data
- Can pre-train policy before interacting with the environment

### 2. Planning

Given a world model and reward function, plan optimal action sequences:

$$a_0^*, \ldots, a_{K-1}^* = \arg\max_{a_0, \ldots, a_{K-1}} \sum_{k=0}^{K-1} \hat{r}_k$$

Common solvers:
- **Cross-Entropy Method (CEM)**: Sample action sequences, rank by imagined reward, refine
- **MPPI**: Model Predictive Path Integral control
- **Shooting methods**: Iterative optimization of action sequences

### 3. Offline RL

Train world model on logged experience; use it as a surrogate:
- Lower sample complexity (don't need more real experience)
- Risk: distributional shift (model encounters states outside training data)

---

## Key Challenges

### 1. Compounding Prediction Error

At each time step k, errors accumulate:
$$\text{Error}(k) \sim k \times \text{Error}(1)$$

Over long horizons, the predicted trajectory diverges from reality. This is why **faithful long-horizon prediction is hard**.

### 2. Stochasticity in Environments

Real environments are stochastic (randomness, unmodeled effects). World model must either:
- **Learn distributions** (use VAE, diffusion, or other generative models)
- **Learn deterministic approximations** (mean of the distribution)

Option 1 is more faithful but computationally expensive.

### 3. Computational Cost vs. Depth

To reduce compounding error, the dynamics core needs to be deep (many parameters). But deeper models are slower:
- **LoopWM solves this** via looped architectures + adaptive depth.

---

## State of the Art (2026)

### Transformer-Based World Models
- **Dreamer v3** (Hafner et al., 2025): Achieved human-level performance on 150 diverse tasks with hyperparameter sharing
- **Genie** (Google DeepMind, 2025): Can generate interactive, explorable environments from video
- **DIAMOND** (Alonso et al., 2024): Diffusion models for faithful world simulations
- **EMERALD** (Burchi & Timote, 2025): Masked latent transformers for coherent long-form video

### Looped Architectures
- **LoopWM** (FaceMind, 2026): First looped transformers for world modeling; 100× parameter efficiency, stable long-horizon rollouts
- **Hyperloop Transformers** (Zeitoun et al., 2026): Matrix-valued hidden states for efficient latent reasoning

### Open Questions
- How to scale world models to high-resolution environments (full HD video)?
- Can world models capture rare, high-impact events (crashes, anomalies)?
- How to certify safety for world-model-based planning?

---

**See also**: [[Looped Transformers]], [[Deferred Decoding]], [[Adaptive Depth]], [[facemind-looped-world-models-2026]]
