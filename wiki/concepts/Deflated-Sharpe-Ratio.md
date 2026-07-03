---
type: concept
address: c-000023
title: "Deflated Sharpe Ratio"
domain: quantitative-finance
complexity: advanced
aliases:
  - "DSR"
status: developing
created: 2026-07-02
updated: 2026-07-02
tags:
  - concept
  - quantitative-finance
  - backtesting
  - statistics
  - sharpe-ratio
related:
  - "[[bailey-lopez-de-prado-2014-deflated-sharpe]]"
  - "[[Backtest-Overfitting]]"
  - "[[Marcos Lopez de Prado]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
sources:
  - "[[bailey-lopez-de-prado-2014-deflated-sharpe]]"
---

# Deflated Sharpe Ratio

Navigation: [[quantitative-finance]] | [[bailey-lopez-de-prado-2014-deflated-sharpe]]

---

## What It Corrects

A raw, reported Sharpe ratio (SR) from a single "best" backtest is inflated by two independent effects, and DSR corrects both at once:

1. **Selection bias under multiple testing.** If you tried N strategy variants and are only looking at the best one, its SR is inflated even if none of the variants has any true skill — this is the "winner's curse." The more variants tried, the bigger the expected inflation.
2. **Non-Normal returns.** Standard Sharpe ratio inference assumes Normally distributed returns. Real strategy returns usually have negative skew and excess kurtosis (fat left tails), which makes the raw SR distribution's true variance wider than the Normal-theory formula assumes — inflating apparent significance.

DSR answers one question: **given how many variants you tried and how non-Normal your returns are, what's the probability the true (population) Sharpe ratio is actually above zero?** If that probability is low, the backtest is a statistical fluke, not a discovery — no matter how good the raw number looks.

---

## The Formula, Plain Terms

```
DSR = Z[ (ŜR − SR₀)·√(T−1)  /  √(1 − γ̂₃·ŜR + (γ̂₄−1)/4 · ŜR²) ]
```

Read left to right:

- **ŜR** — the Sharpe ratio your selected (best) strategy actually reported.
- **SR₀** — the rejection threshold: the Sharpe ratio you'd *expect the best of N random, skill-less trials* to produce, just from chance. This is the number you deflate against, not zero.
- **T** — track length (number of return observations — daily, weekly, whatever your sampling frequency is).
- **γ̂₃, γ̂₄** — skewness and kurtosis of the selected strategy's return distribution. Negative skew and high kurtosis shrink the denominator, which shrinks DSR — i.e., ugly tail risk gets penalized even before you look at multiple-testing effects.
- **Z[·]** — standard Normal CDF. The whole expression converts a z-score into a probability. DSR is literally "the probability that the true Sharpe ratio exceeds SR₀."

### The threshold SR₀ (this is where "how many trials" enters)

```
SR₀ = √V[{ŜR_n}] · ( (1−γ)·Z⁻¹[1 − 1/N]  +  γ·Z⁻¹[1 − 1/(N·e)] )
```

- **N** — number of *independent* trials attempted (every parameter combination, every variant backtested — the full search, not just the winner).
- **V[{ŜR_n}]** — variance of the Sharpe ratios across all N trials (how spread out the trial results were).
- **γ** ≈ 0.5772 (Euler-Mascheroni constant), **e** — Euler's number. Fixed constants from extreme-value theory.

This is the **expected maximum Sharpe ratio you'd get from N trials even if the true underlying skill were zero**. It's derived from extreme value theory (max of N draws from a Normal distribution). As N grows, SR₀ grows too — more trials, higher bar to clear, because pure noise alone produces bigger "winners" the more times you roll the dice.

---

## Inputs You Need, Checklist

To compute DSR for a backtest you must be able to state:

| Input | What it is | Where it comes from |
|-------|-----------|---------------------|
| ŜR | reported Sharpe of the selected/winning strategy | your backtest output |
| N | number of independent trials/variants tried | your own search log — **you must have kept this** |
| V[{ŜR_n}] | variance of Sharpe ratios across all N trials | your own search log |
| T | number of return observations (track length) | sample size |
| γ̂₃, γ̂₄ | skewness, kurtosis of the winning strategy's returns | standard moment calcs on the return series |

The paper's central practical point: **if you cannot report N and V[{ŜR_n}], your backtest cannot be evaluated at all** — "a backtest where the researcher has not controlled for the extent of the search involved in his or her finding is worthless, regardless of how excellent the reported performance might be."

---

## How to Apply It in Practice

1. **Log every trial, not just the winner.** Every parameter combination, every architecture variant, every hyperparameter sweep run against the data counts toward N. If you don't log unsuccessful trials, you cannot compute DSR honestly.
2. **Compute V[{ŜR_n}]** — the variance of Sharpe ratios across all logged trials (not just the survivors).
3. **Estimate independent N if trials are correlated.** If M trials were run but many are near-duplicates (small parameter tweaks), use N̂ = ρ̂ + (1−ρ̂)·M, where ρ̂ is the average pairwise correlation across trials. Highly correlated trials collapse toward N̂→1; independent trials keep N̂→M. See [[bailey-lopez-de-prado-2014-deflated-sharpe]] for the derivation and its caveats (numerically ill-conditioned correlation estimates when sample length is short relative to M).
4. **Compute skew/kurtosis** of the winning strategy's actual return series.
5. **Plug into the DSR formula.** Interpret DSR as a probability — e.g. DSR = 0.90 means 90% confidence the true Sharpe ratio is positive. Compare against your required confidence level (commonly 95%).
6. **If DSR fails your bar, don't fund/trade the strategy** — no matter how good ŜR looks. The paper's worked numerical example: ŜR=2.5 (annualized), N=100, V=1/2, T=1250 days, skew=-3, kurtosis=10 → **DSR = 0.9004**, below a 95% bar, and the strategy is rejected. The same ŜR at N=46 trials would have cleared 95% (DSR=0.9505).
7. **Compute this every time N grows.** The threshold moves as your search grows — a strategy that looked significant after 46 trials can stop looking significant after 100, even with an unchanged reported Sharpe ratio. Re-run the deflation whenever you add more trials to the same search.
8. **Consider running the complementary Harvey-Liu (HL) threshold too** — a Benjamini-Hochberg-derived alternative bar for the same purpose, described as complementary rather than competing.

---

## Relationship to Other Tools

- **Probabilistic Sharpe Ratio (PSR)**: DSR is a special case of PSR where the threshold is not arbitrary (e.g. zero) but is set to SR₀, the multiple-testing-adjusted expected maximum under the null.
- **[[Backtest-Overfitting]]**: DSR is the primary *statistical correction* the paper proposes for the broader backtest-overfitting problem; see that page for the mechanism (memory effects, holdout-method failure) and other defenses (walk-forward, recording every trial, OOS discipline).
- **Model Confidence Set / BH-FDR / Bonferroni / SPA** (used in [[zhang2026-benchmarking-deep-ts-equity]]): same underlying disease (selection bias across many model comparisons) treated with different statistical machinery — MCS/FDR/SPA operate over a *set* of models being compared to each other, DSR corrects a *single selected* strategy's own reported Sharpe against the trial history that produced it. Complementary lenses on the same problem.

---

## See Also

- [[bailey-lopez-de-prado-2014-deflated-sharpe]] — source paper, full derivation and worked example
- [[Backtest-Overfitting]] — the broader problem DSR is built to correct
- [[Marcos Lopez de Prado]] — co-author
- [[zhang2026-benchmarking-deep-ts-equity]] — related multiple-testing corrections in an equity-forecasting benchmark
