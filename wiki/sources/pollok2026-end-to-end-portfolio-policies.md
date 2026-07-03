---
type: source
address: c-000004
title: "End-to-End Parametric Portfolio Policies for Cross-Asset Futures Timing"
domain: quantitative-finance
status: complete
created: 2026-07-02
updated: 2026-07-02
tags:
  - source
  - paper
  - quantitative-finance
  - machine-learning
  - portfolio-optimization
  - futures
  - transformers
related:
  - "[[quantitative-finance]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
  - "[[End-to-End-Portfolio-Optimization]]"
  - "[[Trend-Following]]"
source_type: paper
author: "Austin Pollok (USC), Kevin Robik (Critical Technologies, LLC)"
date_published: 2026-07-01
url: "https://arxiv.org/abs/2607.00475"
confidence: high
key_claims:
  - "No architecture dominates universally; the transformer generally beats the LSTM on gross risk-adjusted return and trades far less, so it survives transaction costs better"
  - "Learned policies rank above simple rules (equal weight, risk parity, time-series momentum) on the pooled cross-asset portfolio and several sub-sleeves, but not uniformly across all seven universes"
  - "The only learned-policy result statistically distinguishable from zero after Bonferroni correction is the equity-index sleeve, and there factor decomposition shows it is mostly market-exposure (beta), not residual alpha"
  - "Value is bench-mark-dependent, asset-class-dependent, and cost-dependent: AI helps most where naive rules are weak (cross-asset, agriculture) and least where equal weighting or trend already captures the return (equity, energy)"
---

# End-to-End Parametric Portfolio Policies for Cross-Asset Futures Timing

Navigation: [[quantitative-finance]] | [[zhang2026-benchmarking-deep-ts-equity]] | [[End-to-End-Portfolio-Optimization]]

---

## Bibliographic Record

| Field | Detail |
|-------|--------|
| Authors | Austin Pollok (Data Science and Operations, Finance and Business Economics, USC, Los Angeles); Kevin Robik (Managing Partner, Critical Technologies LLC, New York) |
| Submitted | July 1, 2026 |
| arXiv | [2607.00475](https://arxiv.org/abs/2607.00475) [q-fin.ST] |
| Keywords | Cross-asset allocation, Deep learning, End-to-end portfolio optimization, Managed futures, Policy function approximation, Transaction costs, Transformers |
| Source | PDF directly read (all 8 pages, main text, tables, figures) |

---

## Abstract (verbatim)

"Timing-based tilts across asset classes can drive much of the risk and return of a diversified cross-asset portfolio. The standard approach forecasts returns and then optimizes weights. We instead study an end-to-end AI-based policy that maps market states directly to portfolio weights, and we then ask when this one-step modeling approach outperforms simple rules-based strategies. We train these policies on the sixteen most liquid CME futures, where an edge is unlikely to be due to illiquidity, using a differentiable Sharpe ratio loss function, and we benchmark them against equal weighting, risk parity, and time-series momentum. The learned policies rank above the rules on the pooled cross-asset portfolio and in several sub-asset classes, but not uniformly. In gross terms, an LSTM and a transformer-based architecture perform comparably out-of-sample, but diverge when we consider transaction costs. The transformer generates the stronger learned policy, trades far less than the LSTM, and matches or exceeds equal weighting through moderate cost."

---

## Section Structure

1. Introduction
2. Data (universe, features, benchmark portfolio construction)
3. Models and Methodology (policy mapping, differentiable Sharpe objective, transformer architecture)
4. In-Sample Results: Optimization (train/validation diagnostics)
5. Out-of-Sample Results: Generalization
   - A. Performance Across Asset Classes
   - B. Risk-Adjusted Performance and Transaction Costs
   - C. Skill versus Market Exposure
   - D. Does Added Complexity Help?
   - E. Why Cross-Asset Timing Is Hard
6. Conclusion and Future Work

---

## Data and Universe

**Instruments**: 16 most liquid CME futures across 6 asset classes (Table I).

| Asset Class | Contracts |
|---|---|
| Equity Index | ES, NQ, RTY |
| Interest Rates | ZT, ZF, ZN, ZB |
| Foreign Exchange | 6E, 6J |
| Energy | CL, NG |
| Metals | GC, HG, SI |
| Agriculturals | ZC, ZW |

**Source**: End-of-day continuous-contract series from Barchart, exchange-sourced, roll-adjusted on volume/open interest; only trailing data used throughout (no look-ahead).

**Sample period**: 2000-2024. Rolling one-year Sharpe by asset class alternates sign repeatedly within every class (Fig. 1a); mean pairwise daily-return correlation is 0.67 within an asset class but only 0.05 across classes (Fig. 1b) — the six classes behave as near-orthogonal return processes, which is why a single pooled rule must handle very different regimes simultaneously.

**Feature set**: a deliberately simple, economically interpretable set capturing three dimensions of market behavior: trend (rate of change), mean reversion (lagged autocorrelation), and randomness/regime structure (Hurst exponent, skewness, kurtosis), plus realized volatility and pairwise correlation. Each computed over 1/5/20/60-day horizons and standardized with rolling 252-day z-scores. Engineered features improved in-sample fit modestly but did not transfer to a stable out-of-sample gain in preliminary walk-forward runs, so the reported out-of-sample results use the cross-section of daily returns as the policy state; fuller integration of the engineered regime features is left to future work.

**Walk-forward design**: expanding-window. Each model first trains on the initial 40% of the sample (2000-2024), then re-fit in roughly four-year test blocks with chronological 90/10 train-validation split, no shuffling. Run once per asset class and once for a pooled model over all sixteen contracts (the cross-asset universe). Out-of-sample period for the cross-asset portfolio: 2011-2024.

---

## Models and Methodology (Section III)

**Policy mapping**: the policy maps market features to per-asset scores, then converts scores to portfolio weights through a differentiable output layer — the long/short budget constraint is built into the policy itself rather than imposed as an optimization constraint.

Portfolio weights: $w_t(\theta) = \pi_\theta(X_t)$, where $\theta$ are learned policy parameters and $X_t$ is the market-state feature vector observed at time $t$.

Portfolio return before costs: $R_{P,t}(\theta) = \sum_i w_{i,t-1}(\theta) R_{i,t}$.

**Differentiable Sharpe loss** (the training objective): $\mathcal{L}_{Sharpe}(\theta) = -\mathbb{E}[R_{P,t}(\theta)] / \sqrt{\mathbb{V}[R_{P,t}(\theta)]}$. Differentiable because portfolio weights are differentiable functions of the neural-network parameters — this is what collapses prediction and optimization into a single training step (no intermediate return-forecasting loss).

**Cost-aware variant**: net returns $R_{P,t}^{net}(\theta) = R_{P,t}(\theta) - \lambda_{tc}\sum_i |w_{i,t-1}(\theta) - w_{i,t-2}(\theta)|$, with $\lambda$ set to 2 basis points (realistic for liquid futures, following Zhang/Zhang/Cucuringu/Zohren 2021), also tested at larger values as a turnover regularizer. Headline results optimize gross-of-cost performance; net performance is reported separately in Section V.

**Transformer architecture** (the primary policy class, following Kisiel & Gorse's Portfolio Transformer): embeds input features (daily returns + engineered regime features), adds a Time2Vec embedding (decomposes the temporal signal into learnable frequencies/phase shifts since attention is order-agnostic) to capture periodic structure. Encoder: 4 identical layers of multi-head self-attention across assets and time, each followed by a gated residual network (GRN), producing a context vector summarizing market state. Decoder: 4 layers attend to this context, produce output representations forming portfolio weights. Causal masking ensures each weight depends only on information available at the time it is formed.

Attention: $\text{Attention}(Q,K,V) = \text{softmax}(QK^\top/\sqrt{d_k} + M)V$, with $M$ a causal mask (0 for admissible positions, $-\infty$ for masked).

Weights via signed-softmax output layer: $w_{i,t}(\theta) = \text{sign}(s_{i,t}(\theta)) \cdot \exp(|s_{i,t}(\theta)|) / \sum_j \exp(|s_{j,t}(\theta)|)$ — permits long and short positions while normalizing total absolute exposure across assets.

**LSTM**: the other neural-network baseline; roughly 30x faster to train than the transformer, so the training recipe (AdamW, OneCycleLR schedule, GELU activations, pre-activation layer normalization, explicit initialization, gradient clipping) was searched coordinate-wise on the LSTM and then verified on the transformer, rather than jointly grid-searched (the joint hyperparameter space was judged too large).

**Benchmark rules** (all rebalance daily; Sharpe ratios are scale-invariant so leverage does not affect comparison):
- **Equal weight (1/N)**: long-only, unit gross exposure. A well-documented benchmark that is hard to beat.
- **Risk parity**: long-only, 60-day inverse-volatility weighting.
- **Time-series momentum (TSMOM)**: long/short, standard 12-month signal, unit gross exposure (Moskowitz/Ooi/Pedersen-style, per Lim/Zohren/Roberts 2019).

---

## In-Sample Diagnostics (Section IV)

Purpose: measure learnability and policy-class capacity separately from out-of-sample generalization (poor OOS performance could reflect failed optimization rather than a genuinely weak signal). Run on the initial 40% of the sample; remainder held for walk-forward validation. Findings: (1) both policy classes can learn the training windows and can also overfit them — with the correct recipe, in-sample Sharpe improves steadily while a train-validation gap opens once training is pushed too far (confirms sufficient capacity; early stopping is necessary; removing normalization/clipping causes gradient instability); (2) the engineered regime features (trend, mean reversion, Hurst, volatility, correlation, higher moments) improved in-sample fit modestly but did not deliver a stable out-of-sample gain in preliminary runs — hence the state is the raw return cross-section in the main results.

---

## Key Results

### Table II: Out-of-sample risk/return by universe (annualized; 2 bp net-Sharpe; best value bolded per column/panel; `*` = Sharpe significantly different from zero at 5% after Bonferroni correction across the 7 universes, requiring |t| > 2.69)

| Universe | Strategy | Return | Vol | Sharpe | Net Sharpe | Sortino | MDD | Calmar | Turnover |
|---|---|---|---|---|---|---|---|---|---|
| Cross-asset | 1/N | 0.05 | 0.09 | 0.52 | 0.52 | 0.73 | 0.24 | 0.20 | 0.00 |
| Cross-asset | Risk parity | 0.01 | 0.08 | 0.15 | 0.14 | 0.19 | 0.15 | 0.04 | 0.01 |
| Cross-asset | TSMOM | 0.03 | 0.08 | 0.37 | 0.35 | 0.53 | 0.21 | 0.14 | 0.02 |
| Cross-asset | LSTM | 0.02 | 0.05 | 0.50 | 0.33 | 0.70 | 0.10 | 0.26 | 0.17 |
| Cross-asset | **transformer** | 0.05 | 0.08 | **0.55** | **0.54** | **0.74** | 0.27 | 0.17 | 0.02 |
| Equity index | 1/N | 0.15 | 0.19 | 0.78* | 0.78 | 0.98 | 0.40 | 0.37 | 0.00 |
| Equity index | LSTM | 0.09 | 0.10 | **0.87*** | 0.83 | **1.02** | 0.19 | **0.47** | 0.07 |
| Equity index | transformer | 0.12 | 0.15 | 0.80* | 0.79 | 0.99 | 0.36 | 0.34 | 0.02 |
| Interest rates | TSMOM | 0.02 | 0.05 | **0.43** | **0.41** | **0.62** | 0.10 | **0.20** | 0.02 |
| FX | TSMOM | 0.02 | 0.07 | **0.25** | **0.23** | **0.35** | 0.20 | 0.08 | 0.03 |
| Metals | transformer | 0.05 | 0.16 | **0.35** | **0.35** | **0.47** | 0.58 | 0.10 | 0.01 |
| Energy | 1/N | 0.11 | 0.36 | **0.30** | **0.30** | 0.43 | 1.07 | **0.10** | 0.00 |
| Agriculture | transformer | 0.06 | 0.18 | **0.34** | **0.33** | **0.51** | 0.48 | **0.13** | 0.03 |

(Table condensed to the leading strategy per universe plus the two learned models throughout; full 5-strategy table spans all 7 universes in the source PDF.)

**Per-universe leaders (Sharpe)**: transformer leads cross-asset, metals, agriculture; LSTM leads equity index; equal weighting leads energy; TSMOM leads interest rates and FX.

**Statistical significance**: only the equity-index Sharpe ratios for both learned models remain significant after Bonferroni correction across the seven universes (t ≈ 3). The cross-asset transformer reaches t ≈ 2 — clears the uncorrected 5% level but not the Bonferroni threshold.

**Bootstrap pairwise test** (cross-asset universe, one-month block bootstrap, 5,000 resamples): transformer beats risk parity with probability 0.99; beats TSMOM with probability 0.68; beats equal weighting with probability only 0.59 (statistical tie/match rather than a significant win against 1/N).

### Table III: Net Sharpe of the cross-asset portfolio as transaction costs rise

| Strategy | 0 bp | 1 bp | 2 bp | 5 bp | 10 bp |
|---|---|---|---|---|---|
| 1/N | 0.52 | 0.52 | 0.52 | **0.52** | **0.52** |
| Risk parity | 0.15 | 0.14 | 0.14 | 0.13 | 0.11 |
| TSMOM | 0.37 | 0.36 | 0.35 | 0.33 | 0.29 |
| LSTM | 0.50 | 0.42 | 0.33 | 0.06 | -0.38 |
| **transformer** | **0.55** | **0.54** | **0.54** | **0.52** | 0.50 |

The transformer's Sharpe falls only from 0.55 to 0.54 across 0-2 bp and stays at 0.50 through 10 bp — essentially cost-insensitive because turnover is ~0.02/day. The LSTM collapses from 0.50 to -0.38 over the same range because its turnover is ~0.17/day (8.5x the transformer's). The ranking between the two learned models is stable across the 1-10 bp range: transformer wins net at every cost level tested.

### Turnover comparison (all universes)

Transformer turnover holds steady near 0.02/day across universes (low, ~0.01-0.03/day per the Conclusion). LSTM turnover ranges 0.07-0.17/day depending on universe (0.17 on the cross-asset portfolio specifically). This ~8.5x turnover gap is the central mechanism explaining why gross performance is comparable but net performance diverges sharply.

### Table IV: Per-universe alpha/beta decomposition (Newey-West HAC regression against each universe's 1/N benchmark; annualized % alpha; `*` = significant at 5%)

| Universe | LSTM alpha | LSTM beta | transformer alpha | transformer beta |
|---|---|---|---|---|
| Equity | +3.9* | 0.50* | +0.8 | 0.63* |
| Metals | -0.1 | 0.41* | +1.4 | 0.67* |
| Agriculture | -4.9 | 0.38* | +2.0 | 0.47* |
| FX | -0.6 | 0.31* | +0.5 | 0.22* |
| Rates | +0.1 | 0.18* | -0.3 | 0.52* |
| Energy | -0.4 | 0.56* | +0.3 | 0.75* |

Only the LSTM's equity-index alpha is significant (Newey-West). The transformer's equity alpha is small and statistically insignificant; its market-exposure component (beta) explains most of its return there. No other universe shows a residual alpha distinguishable from zero for either model. The transformer has larger residual-alpha point estimates in metals and energy than the LSTM, but neither clears significance. Skill-versus-exposure attribution is model-specific and should not be assumed to transfer between architectures.

---

## When AI Beats Simple Rules (the paper's central question)

**Where the learned policy adds the most value**:
- The broad **cross-asset** portfolio (widest cross-section: 16 contracts) — transformer Sharpe 0.55 gross / 0.54 net vs. equal weight 0.52, TSMOM 0.37, risk parity 0.15.
- **Agriculture** — transformer Sharpe 0.34, more than double the best long-only rule (0.16 for LSTM as long-only-style comparator; equal weight only 0.12).
- **Metals** — transformer 0.35 vs. equal weight 0.29 and LSTM 0.30.

**Where it does not help / where simple rules win**:
- **Interest rates**: TSMOM (0.43) beats both learned models by a wide margin; transformer is actually near zero (0.09) or slightly negative depending on config.
- **Foreign exchange**: TSMOM (0.25) wins; both learned models are flat-to-negative.
- **Energy**: equal weighting (0.30) matches or beats the learned policies; naive diversification captures most of the available return in the post-2020 recovery.
- **Equity index**: the learned models' Sharpe ratios are statistically distinguishable from zero (the only universe where this holds after Bonferroni correction), but factor decomposition shows this is mostly market-exposure (beta ~0.5-0.6), not residual timing skill — "not best interpreted as market-neutral alpha... closer to a risk-efficient directional exposure."

**General pattern** (the paper's stated main lesson): value from end-to-end AI allocation is conditional, not universal. It is strongest where simple rules are weakest and where the model can exploit breadth across contracts (the 16-contract cross-asset universe). It is least compelling where naive diversification (equal weighting in energy) or a standard trend rule (TSMOM in rates/FX) already captures most of the available return. Added complexity does not automatically help: mixture-of-experts, per-class tuning, larger feature sets, and cross-model ensembling were tested in simple out-of-the-box form and did not reliably improve out-of-sample performance after costs. Seed averaging (3 independently-seeded transformer runs) is the one enhancement that reliably helps — a single transformer seed is highly variable and can be statistically indistinguishable from zero; averaging removes much of that seed-level noise.

**Why cross-asset timing is hard** (Section V.E, five structural reasons given):
1. The liquid-universe design removes illiquidity as a likely return source — cleaner test, thinner signal to exploit.
2. The Sharpe objective has a natural solution in markets that drift upward: a model can improve the objective by learning a steady, sub-unit exposure to risk even with little residual alpha (risk-efficient beta exposure rather than market-neutral timing skill).
3. Single-asset-class sleeves are small (2-4 contracts), leaving little cross-section for the models to exploit; the 16-contract cross-asset universe is the widest and is where the transformer most clearly benefits from breadth.
4. The benchmark is demanding: equal weighting and risk parity are hard to beat on liquid futures, so a learned policy must clear a high practical bar.
5. Daily frequency, one asset universe tested; higher frequency or a wider contract set could give the model more signal and breadth to exploit (flagged as future work).

---

## Conclusion (verbatim key lines)

"This leaves a useful allocator. On the full sixteen-contract cross-asset portfolio, the transformer attains the highest Sharpe ratio of any strategy. It also trades much less than the LSTM, so its performance is largely preserved after realistic transaction costs. The result is not standalone, market-neutral alpha. It is closer to a low-turnover, risk-efficient allocation rule that can compete with simple benchmarks in some settings."

Two lessons the authors state extend beyond this study: (1) learned allocation policies should be benchmarked against the rule a practitioner would actually run, not against 1/N alone; (2) risk, turnover, and attribution should be measured on the exact model in use — the LSTM and transformer differ not only in performance but in turnover and in the split between beta exposure and residual alpha; costs and averaging across seeds should be evaluated before committing capital.

**Stated limitations**: transformer turnover 0.01-0.03/day (gross and net performance close); results are seed-sensitive (individual estimates indicative, not definitive); training recipe tuned mostly on the faster LSTM, so transformer-specific tuning could change the attribution; only one daily frequency and two architectures tested, not a broader model class.

**Stated future extensions**: higher-frequency data; a larger futures universe (more contracts per asset class, more asset classes) for more breadth; contract and asset-class embeddings to let one model share information across related instruments while still learning contract-specific behavior.

---

## Citations in Paper (References)

- [1] Zhang, Zohren, Roberts — "Deep reinforcement learning for trading," J. Financ. Data Sci., 2020
- [2] Lim, Zohren, Roberts — "Enhancing time series momentum strategies using deep neural networks," J. Financ. Data Sci., 2019 (TSMOM benchmark source)
- [3] Zhang, Zohren, Roberts — "Deep learning for portfolio optimization," J. Financ. Data Sci., 2020
- [4] Wood, Giegerich, Roberts, Zohren — "Trading with the momentum transformer," arXiv:2112.08534, 2021
- [5] Brandt, Santa-Clara, Valkanov — "Parametric portfolio policies," Rev. Financ. Stud., 2009 (origin of the parametric-policy framing)
- [6] DeMiguel, Garlappi, Uppal — "Optimal versus naive diversification: How inefficient is the 1/N portfolio strategy?" Rev. Financ. Stud., 2009 (source for "equal weighting is hard to beat")
- [7] Zhang, Zhang, Cucuringu, Zohren — "A universal end-to-end approach to portfolio optimization via deep learning," arXiv:2111.09170, 2021 (primary methodological precedent; source of the 2 bp cost convention and weight-mapping approach)
- [8] Powell — *Reinforcement Learning and Stochastic Optimization: A Unified Framework for Sequential Decisions*, Wiley, 2022 (policy function approximation taxonomy)
- [9] Kisiel, Gorse — "Portfolio transformer for attention-based asset allocation," ICAISC 2022 (source of the Portfolio Transformer architecture used here)
- [10] Simon, Weibels, Zimmermann — "Deep parametric portfolio policies," SSRN Working Paper 4150292, 2022
- [11] Jensen, Kelly, Malamud, Pedersen — "Machine learning and the implementable efficient frontier," Swiss Finance Inst. Res. Paper No. 22-63, 2024 (source of the 2 bp cost calibration)
- [12] Markowitz — "Portfolio selection," J. Finance, 1952
- [13] Fama — "Efficient capital markets," J. Finance, 1970
- [14] Moody, Saffell — "Reinforcement learning for trading," NeurIPS 1998
- [15] Elmachtoub, Grigas — "Smart 'predict, then optimize'," Manage. Sci., 2022 (decision-focused learning contrast)
- [16] Donti, Amos, Kolter — "Task-based end-to-end model learning in stochastic optimization," NeurIPS 2017
- [17] Bertsimas, Kallus — "From predictive to prescriptive analytics," Manage. Sci., 2020

---

## Relationship to Zhang et al. 2026 ([[zhang2026-benchmarking-deep-ts-equity]])

Both papers benchmark deep-learning architectures against simpler alternatives for portfolio construction and both find transaction costs decisive, but they differ in framing and universe:

| Dimension | Pollok & Robik 2026 (this paper) | Zhang et al. 2026 |
|---|---|---|
| Universe | 16 liquid CME futures, 6 asset classes | CRSP daily equities, 5,451 stocks |
| Pipeline | **End-to-end**: features -> weights directly via differentiable Sharpe loss | **Predict-then-optimize**: forecast returns/scores, then a separate constrained-QP portfolio layer |
| Architectures compared | 2 (LSTM, transformer) | 15 (linear, recurrent, transformer/patch, mixer/graph) |
| Cost finding | Transformer's low turnover (~0.02/day) survives costs; LSTM's high turnover (~0.17/day) erodes net Sharpe from 0.50 to -0.38 at 10 bp | TS-RIDGE's high turnover (7.95) erodes cost-adjusted performance and exits the net Model Confidence Set; **constrained-QP net Sharpe at 20 bp is negative for every one of the five promoted models** |
| Common thread | Turnover, not gross accuracy, is the deciding factor for which model survives in practice | Same: "no architecture dominates," and the deployment-adjusted acceptability index downweights high-turnover winners |

Both papers converge on the same practical conclusion from opposite pipeline designs: **gross-return rankings and net-of-cost rankings diverge, and the divergence is driven by turnover**. Zhang's constrained-QP layer imposes turnover explicitly as a penalty in the optimizer; Pollok & Robik's transformer architecture achieves low turnover implicitly through its attention-based weight mapping, without an explicit turnover penalty in the primary (gross-trained) model. Zhang's finding that a turnover-penalized loss does not reliably help (per Pollok & Robik's own turnover-penalized-training test, Section V.D) is corroborated here: the authors tested an explicit turnover penalty on both the LSTM and transformer and found it reduced LSTM trading without materially improving net performance ranking, while it over-constrained the already-low-turnover transformer.

---

## Provenance Note

All 8 pages of the PDF directly read (title, abstract, all sections I-VI, all tables, all figures, references). No appendices exist in this paper (main text only). Table II condensed above to leading results per universe; the source PDF contains the full 5-strategy x 7-universe matrix.

---

## See Also

- [[quantitative-finance]] - domain page
- [[zhang2026-benchmarking-deep-ts-equity]] - predict-then-optimize contrast on equities
- [[End-to-End-Portfolio-Optimization]] - the decision-focused learning concept this paper instantiates
- [[Trend-Following]] - TSMOM benchmark rule
