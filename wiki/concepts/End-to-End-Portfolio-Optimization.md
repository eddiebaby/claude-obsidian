---
type: concept
address: c-000009
title: "End-to-End Portfolio Optimization"
domain: quantitative-finance
complexity: intermediate
created: 2026-07-02
updated: 2026-07-02
tags:
  - quantitative-finance
  - concept
  - portfolio-optimization
  - machine-learning
  - decision-focused-learning
status: developing
aliases:
  - "decision-focused learning"
  - "task-based end-to-end learning"
  - "parametric portfolio policies"
related:
  - "[[pollok2026-end-to-end-portfolio-policies]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
  - "[[Trend-Following]]"
  - "[[quantitative-finance]]"
---

# End-to-End Portfolio Optimization

Navigation: [[quantitative-finance]] | [[pollok2026-end-to-end-portfolio-policies]] | [[zhang2026-benchmarking-deep-ts-equity]]

---

## Definition

End-to-end portfolio optimization (also called decision-focused or task-based learning) trains a model to map market features **directly to portfolio weights**, using a differentiable performance objective (e.g. Sharpe ratio) as the training loss. This collapses forecasting and optimization into a single step: there is no intermediate return- or covariance-prediction target that gets fed to a separate optimizer afterward.

Contrast with the standard **predict-then-optimize** pipeline: (1) forecast returns/scores/covariances with a supervised model trained on a forecasting loss (e.g. MSE), then (2) hand those forecasts to a separate portfolio-construction step (mean-variance, constrained QP, risk parity, etc.) that was not part of the training loop. The two steps are optimized independently, so a model that forecasts well is not guaranteed to produce portfolios that perform well after the optimization layer and transaction costs are applied.

---

## The Core Mechanism

Portfolio weights are modeled as a direct function of market state:

$$w_t(\theta) = \pi_\theta(X_t)$$

where $\theta$ are the learned policy parameters, $X_t$ is the feature vector observed at time $t$, and $\pi_\theta$ is typically a neural network (LSTM, transformer, MLP). The network is trained by maximizing the **portfolio's own reward function** directly, rather than an intermediate return-forecasting loss:

$$\mathcal{L}_{Sharpe}(\theta) = -\frac{\mathbb{E}[R_{P,t}(\theta)]}{\sqrt{\mathbb{V}[R_{P,t}(\theta)]}}$$

This is differentiable because portfolio weights are themselves differentiable functions of the network parameters (via a signed-softmax or similar output layer), so gradients of the Sharpe ratio flow all the way back through the weight-generation process to the raw features. Constraints that would otherwise be imposed on a separate optimizer (long/short budget, gross exposure normalization) are instead built directly into the output layer's functional form.

A cost-aware variant penalizes turnover directly in the training loss:

$$R_{P,t}^{net}(\theta) = R_{P,t}(\theta) - \lambda_{tc}\sum_i |w_{i,t-1}(\theta) - w_{i,t-2}(\theta)|$$

so the optimizer itself, not a post-hoc adjustment, learns to trade off return against trading cost.

---

## Origins and Related Framings

The same underlying idea recurs across several fields under different names, per [[pollok2026-end-to-end-portfolio-policies]] (Section I):

- **Financial economics**: **parametric portfolio policies** (Brandt, Santa-Clara, Valkanov 2009) — portfolio weights modeled directly as functions of characteristics.
- **Operations research / management science**: **decision-focused** or **task-based end-to-end optimization** — models trained against the downstream decision objective rather than an intermediate prediction loss (Donti/Amos/Kolter 2017; Bertsimas/Kallus 2020; Elmachtoub/Grigas' "smart predict-then-optimize" 2022).
- **Reinforcement learning / stochastic optimization**: classified as **policy function approximation** — a model mapping states directly to actions rather than estimating a value function (Powell's taxonomy, 2022).
- **End-to-end trading literature**: Deep Momentum Networks (Lim/Zohren/Roberts 2019), deep reinforcement learning for futures (Zhang/Zohren/Roberts 2020), deep portfolio optimization over ETFs (Zhang/Zohren/Roberts 2020), differentiable weight layers for large equity universes (Zhang/Zhang/Cucuringu/Zohren 2021), attention-based futures momentum (Wood et al. 2021), and the Portfolio Transformer (Kisiel/Gorse 2022).

---

## Case Study: Pollok & Robik 2026

[[pollok2026-end-to-end-portfolio-policies]] is the clearest recent instantiation: a transformer and an LSTM are both trained end-to-end on 16 liquid CME futures using the differentiable Sharpe loss above, then benchmarked against equal weighting, risk parity, and time-series momentum ([[Trend-Following]]).

**Key finding — the mechanism, not just the result, matters**: the transformer's attention-based weight mapping produces naturally low turnover (~0.02/day) without an explicit turnover penalty, while the LSTM trades far more (~0.17/day on the cross-asset portfolio). Both models achieve comparable *gross* Sharpe ratios, but the transformer's net Sharpe survives transaction costs (0.55 to 0.50 across 0-10 bp) while the LSTM's collapses (0.50 to -0.38 over the same range). This demonstrates that end-to-end training does not automatically produce low turnover — it depends on the architecture's inductive bias, and an explicitly turnover-penalized loss term did not reliably fix this for the high-turnover LSTM without over-constraining the already-low-turnover transformer.

The paper's central finding is conditional, not universal: end-to-end policies beat simple rules on the pooled cross-asset portfolio and in some sub-asset-class sleeves (metals, agriculture) but not in others (interest rates and FX, where TSMOM wins outright; energy, where equal weighting is already sufficient). Where a learned result is statistically significant (the equity-index sleeve), factor decomposition shows the return is mostly market-beta exposure, not residual timing alpha — a caution against over-reading Sharpe improvements as evidence of skill.

---

## Contrast: Predict-Then-Optimize (Zhang et al. 2026)

[[zhang2026-benchmarking-deep-ts-equity]] is the predict-then-optimize counterpart on equities: 15 architectures are benchmarked purely as **return forecasters** (decile long-short portfolios formed from model scores), and only the five best-performing models are then promoted into a **separate constrained quadratic portfolio layer** (dollar neutrality, leverage cap, single-name capacity, beta neutrality, industry limits, explicit turnover/risk penalties in the objective). The forecasting step and the portfolio-construction step are two independent stages; the constrained-QP step is not differentiated back through the forecasting model.

The two papers converge on the same practical lesson despite opposite architectures: **turnover determines which model survives cost, regardless of gross forecasting or gross Sharpe quality**. Zhang's TS-RIDGE has the best gross Sharpe (3.88) but the highest turnover (7.95), and exits the net Model Confidence Set; the baseline constrained-QP net Sharpe at 20 bp is negative for every one of the five promoted models. Pollok & Robik's LSTM shows the same pattern at futures scale: high turnover erodes an otherwise-competitive gross Sharpe into a large net loss as costs rise.

| Dimension | End-to-end (Pollok & Robik) | Predict-then-optimize (Zhang et al.) |
|---|---|---|
| Training signal | Differentiable Sharpe ratio, direct | Forecasting loss (implicit; then decile sort) |
| Portfolio construction | Built into network output layer | Separate constrained-QP stage after model selection |
| Constraint handling | Long/short budget baked into signed-softmax | Explicit constraints (leverage, beta, industry, capacity) in optimizer |
| Where turnover is controlled | Implicitly, by architecture (or explicit turnover-loss term) | Explicitly, by optimizer penalty term |
| Common failure mode | High-turnover architecture (LSTM) erodes net Sharpe | High-turnover model (TS-RIDGE) exits net MCS; all promoted models negative net Sharpe post-QP |

---

## Why This Matters Practically

The choice between end-to-end and predict-then-optimize is not just an engineering preference — it changes *where* turnover gets controlled and *what gets optimized directly*. End-to-end training can produce a naturally low-turnover policy (as with the transformer) but offers less transparency into *why* a given weight was assigned, since there is no intermediate forecast to inspect. Predict-then-optimize keeps forecasting and portfolio construction auditable as separate stages but risks compounding forecasting error into the optimizer and requires the constraint/turnover logic to be engineered explicitly, as Zhang et al. do with their constrained-QP layer.

Both papers' shared conclusion: **do not evaluate a learned allocation model on gross accuracy or gross Sharpe alone.** Benchmark against the rule a practitioner would actually run (not just 1/N), and measure turnover and net-of-cost performance on the exact model in use before committing capital.

---

## See Also

- [[pollok2026-end-to-end-portfolio-policies]] - source paper, cross-asset futures
- [[zhang2026-benchmarking-deep-ts-equity]] - predict-then-optimize contrast, equities
- [[Trend-Following]] - the TSMOM benchmark rule both papers test against
- [[quantitative-finance]] - domain page
