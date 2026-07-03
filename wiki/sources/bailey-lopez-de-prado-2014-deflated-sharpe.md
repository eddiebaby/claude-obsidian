---
type: source
address: c-000018
title: "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality"
domain: quantitative-finance
source_type: paper
author: "David H. Bailey, Marcos Lopez de Prado"
date_published: 2014-07-31
url: "http://ssrn.com/abstract=2460551"
confidence: high
status: complete
created: 2026-07-02
updated: 2026-07-02
tags:
  - source
  - paper
  - quantitative-finance
  - backtesting
  - statistics
  - sharpe-ratio
key_claims:
  - "A backtest where the researcher has not controlled for the number of trials attempted is worthless, regardless of reported performance."
  - "The expected maximum Sharpe ratio across N independent trials grows with N even when the true Sharpe ratio is zero — pure selection produces apparent skill."
  - "The Deflated Sharpe Ratio (DSR) corrects an estimated Sharpe ratio for both selection bias under multiple testing and non-Normality (skew, kurtosis) of returns."
  - "In the worked example, a strategist's SR=2.5 backtest is rejected at 95% confidence once N=100 trials and negative skew/high kurtosis are accounted for (DSR=0.9004 < 0.95)."
related:
  - "[[quantitative-finance]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[Backtest-Overfitting]]"
  - "[[Marcos Lopez de Prado]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
sources: []
---

# The Deflated Sharpe Ratio

Navigation: [[quantitative-finance]]

---

## Bibliographic Record

| Field | Detail |
|-------|--------|
| Authors | David H. Bailey (LBNL, retired; UC Davis research fellow), Marcos Lopez de Prado (Senior Managing Director, Guggenheim Partners; Research Affiliate, LBNL Computational Research Division) |
| First version | April 15, 2014 |
| This version | July 31, 2014 |
| Venue | Journal of Portfolio Management, forthcoming 2014 |
| URL | http://ssrn.com/abstract=2460551 |
| JEL | G0, G1, G2, G15, G24, E44 |
| Source | Full PDF read (11 pages main text + appendices A.1-A.3 + exhibits 1-4) |

---

## Abstract (paraphrased)

Large datasets, machine learning, and cheap compute let quant teams backtest millions of strategy variants. Backtest optimizers search parameter space for whatever maximizes simulated historical performance — this is **backtest overfitting**. The same inflation shows up whenever researchers report only positive outcomes (**selection bias**): file-drawer effect, publication bias, survivorship bias, self-selection/backfilling. The paper's fix, the **Deflated Sharpe Ratio (DSR)**, corrects an estimated Sharpe ratio for both sources of inflation — selection under multiple testing, and non-Normal returns — helping separate real findings from statistical flukes.

---

## Core Argument

### Multiple testing → selection bias → backtest overfitting

Three linked problems, escalating in severity:

1. **Multiple testing**: testing more strategies at a fixed Type I error rate α (e.g. 5%) raises the overall probability that *at least one* accepted strategy is actually a false positive. Standard problem, well known since early 20th-century statistics (Bonferroni; Holm 1979; Benjamini-Hochberg FDR).
2. **Selection bias**: when only positive results get reported (file-drawer effect, publication bias, survivorship bias, backfilling), the decision-maker never sees the denominator — the number of trials that failed. Hiding trials makes "improbable" results look probable (Hand 2014). The American Statistical Association's 1997 Ethical Guidelines (#8) explicitly warn against this.
3. **Backtest overfitting**: a special, more expensive case of selection bias specific to finance. After enough trials, a researcher is *guaranteed* to find a strategy that fits chance patterns in the historical sample. The strategy is fit to noise, not signal, and the paper argues this is provably worse than harmless underperformance when the underlying series has **memory effects** (mean-reversion / "spring" behavior): an overfit strategy identifies the *most extreme* random patterns in-sample, and if those patterns are actively undone out-of-sample (as memory effects imply), the strategy doesn't just fail to repeat — it loses money by design. See Bailey et al. (2014) for the formal proof; the paper's companion "Probability of Backtest Overfitting" (PBO) tool.

The coin-toss illustration: ten fair-coin tosses might by chance read `{+,+,+,+,+,-,-,-,-,-}`. A researcher fits a rule ("bet + first half, - second half") to this. Next ten tosses come out `{-,-,+,-,+,+,-,+,-}` — 5 wins, 5 losses, i.e. the "seasonality" rule had null predictive power. It only looked good because it was fit to noise that happened once.

**The holdout method does not fix this.** Splitting into in-sample/out-of-sample subsets (or k-fold CV) validates a *single* trial. But if you retry holdout enough times (the paper notes ~20 retries at 95% confidence), a false positive that passes OOS validation becomes *expected*, not surprising — and it gets published as if it were a single-trial result. Model validation techniques address "Type III errors" (testing hypotheses suggested by the data) but do not control for backtest overfitting itself.

An online tool built at LBNL (http://datagrid.lbl.gov/backtest) demonstrates this directly: it fits a "profitable" strategy of any target Sharpe ratio to a pseudorandom price series, then shows that strategy flounders on a second independent pseudorandom series of the same length.

### Expected maximum Sharpe ratio under the null

Core formal result (proved in Appendix A.1, extending Bailey et al. 2014a). Consider N independent trials, each producing a Sharpe ratio estimate {ŜR_n}, assumed Normally distributed with mean E[{ŜR_n}] and variance V[{ŜR_n}]. Then for N ≫ 1:

```
E[max{ŜR_n}] ≈ E[{ŜR_n}] + √V[{ŜR_n}] · ( (1-γ)Z⁻¹[1 - 1/N] + γZ⁻¹[1 - 1/(N·e)] )
```

— where γ ≈ 0.5772 is the Euler-Mascheroni constant, Z is the standard Normal CDF, e is Euler's number. (Equation 1 / Appendix eq. 6.)

**Key implication**: even when the *true* Sharpe ratio is zero (E[{ŜR_n}]=0, no investment skill at all), the expected maximum of N random Sharpe estimates grows with N. At V=1, expected max SR rises from ~1.3 (N=10) toward ~3.2 (N=1000); at V=4 it rises toward ~6.5. This is pure "winner's curse" — parsing through more candidates surfaces better-looking candidates even with zero skill, purely from variance. Appendix A.2/A.3 verify the formula numerically (Monte Carlo, 10,000 iterations) and show error converges toward zero as N grows, consistent with the N≫1 assumption.

### Estimating N when trials are correlated (Appendix A.3)

The N in the formula must be the number of *independent* trials. If M trials were run but are correlated with average pairwise correlation ρ̂, the implied number of independent trials is interpolated:

```
N̂ = ρ̂ + (1 - ρ̂)·M
```

As ρ→1, N̂→1 (fully redundant trials count as one). As ρ→0, N̂→M (fully independent trials all count). Caveat: correlation is a limited (linear) dependence measure, and when the sample length T < ½M(M-1), the correlation matrix is numerically ill-conditioned — there are more pairwise correlations than independent observations to estimate them from. The paper flags information-theoretic alternatives (entropy, total correlation, multiinformation) as a more principled path, without fully developing one here.

---

## The Deflated Sharpe Ratio (DSR)

See [[Deflated-Sharpe-Ratio]] for the full concept treatment. Summary:

DSR = PSR(SR₀) evaluated at a rejection threshold SR₀ that itself accounts for the number of independent trials N and their variance V[{ŜR_n}]. Formula (Eq. 2):

```
DSR ≡ PSR(SR₀) = Z[ (ŜR - SR₀)·√(T-1) / √(1 - γ̂₃·ŜR + (γ̂₄-1)/4 · ŜR²) ]
```

where SR₀ = √V[{ŜR_n}] · ((1-γ)Z⁻¹[1-1/N] + γZ⁻¹[1-1/(N·e)]) is exactly the expected-maximum-SR-under-null from Eq. 1. T is track length (sample size), γ̂₃ is skewness, γ̂₄ is kurtosis of the selected strategy's returns.

DSR is built on the **Probabilistic Sharpe Ratio (PSR)** (Bailey & Lopez de Prado 2012a), which computes the probability that a strategy's true Sharpe ratio exceeds a chosen threshold, correcting for sample length and the first four moments of the returns distribution (Normal returns inflate/deflate PSR depending on skew/kurtosis). DSR = PSR where the threshold is set to the multiple-testing-adjusted SR₀ rather than an arbitrary cutoff (often zero).

The paper explicitly relates this to Harvey & Liu (2014, "HL"), who derive an analogous multiple-testing threshold from the Benjamini-Hochberg framework; DSR and HL are complementary (different threshold derivations feeding the same deflation logic), and the authors recommend computing DSR under both.

---

## Worked Example (paper's numbers, Sharpe/Treasury seasonality)

A strategist backtests Treasury auction-cycle seasonality (buy/sell around auction dates), trying many combinations of pre-/post-auction windows, tenors, holding periods, stop-losses. Many configurations yield annualized ŜR ≈ 2, and the best hits ŜR = 2.5 over a 5-year daily sample.

The investor demands four disclosures before funding: N (independent trials), V[{ŜR_n}] (variance across trial SRs), T (sample length), and (γ̂₃, γ̂₄) (skew/kurtosis of the selected strategy's returns). Strategist discloses: **N=100, V[{ŜR_n}]=1/2, T=1250 (daily, 5 years), γ̂₃=-3, γ̂₄=10**.

Computation:
- Non-annualized ŜR = 2.5/√250 (converting from the annualized figure)
- SR₀ = √(1/(2·250)) · ((1-γ)Z⁻¹[1-1/100] + γZ⁻¹[1-1/(100·e)]) ≈ **0.1132**
- DSR = Z[ ((2.5/√250 - 0.1132)·√1249) / √(1 - (-3)·(2.5/√250) + (10-1)/4·(2.5/√250)²) ] = **0.9004**

0.9004 < 0.95, so the investor **rejects the offer** at 95% confidence — there's only a 90% chance the true Sharpe ratio is even positive. Sensitivity checks in the paper:
- Had the strategist stopped at **N=46** independent trials (same ŜR=2.5), DSR would have been 0.9505 — just above the 95% bar, and the investor would likely have funded it. More trials attempted with the same reported result *lowers* statistical credibility.
- Had the returns been **Normal** (γ̂₃=0, γ̂₄=3, no fat tails/negative skew) instead of the actual non-Normal distribution, DSR would reach 0.9505 already at N=88 trials — i.e., non-Normality alone accounts for roughly the gap between N=46 and N=88 in trials-tolerance. Both selection bias and non-Normality must be corrected jointly; neither alone captures the full inflation.

Exhibit 2 in the paper plots SR₀ rising and DSR falling as N grows, for both the N∈[0,100] and N∈[0,1000] ranges, holding the reported ŜR fixed.

---

## When Should You Stop Testing?

The paper closes with a practical rule drawn from the "secretary problem" / optimal stopping theory (Bruss 1984, the 1/e-law of optimal choice): given a set of theoretically justifiable strategy configurations, randomly sample a fraction 1/e (≈37%) and measure their performance without selecting any. Then continue drawing from the remaining set, in order, and select the first one that beats every previously measured candidate. This is the stopping rule that maximizes the probability of selecting the actual best strategy while explicitly bounding the number of trials — because every additional trial irreversibly raises the false-positive probability.

---

## Minimum Backtest Length / Minimum Track Record Length

The paper's keywords list both **Minimum Track Record Length** and **Minimum Backtest Length** as companion concepts (developed more fully in the authors' related work, e.g. Bailey & Lopez de Prado 2012a and the PBO paper, Bailey et al. 2013/2014). In this paper's own frame: given a target confidence level and an assumed number of independent trials N, DSR's SR₀ term implies a **minimum sample length T** (or, dually, a minimum number of trials to avoid) needed before a given observed Sharpe ratio can be called statistically significant — directly visible in the worked example, where the *same* ŜR=2.5 clears the bar at N=46 trials but fails it at N=100. The provenance note below flags that MinBTL / MinTRL are not derived as standalone formulas in the 11 pages read here; they are named in the keywords and referenced through the surrounding literature (Bailey & Lopez de Prado 2012a, PBO paper) rather than fully derived in this specific paper.

---

## Citations of Note

- Sharpe (1966, 1975, 1994): the Sharpe ratio itself
- Bailey & Lopez de Prado (2012a): Probabilistic Sharpe Ratio
- Bailey et al. (2013): Probability of Backtest Overfitting (PBO), cross-validation-based
- Bailey et al. (2014): formal proof that backtest overfitting under memory effects leads to loss maximization out-of-sample
- Harvey & Liu (2014) ["HL"]: Benjamini-Hochberg-based multiple-testing threshold for Sharpe ratios, complementary to DSR
- Efron (2011): shrinkage estimation / regression-to-the-mean framing of the "winner's curse"
- Hand (2014); Roulston & Hand (2013): selection bias mechanics
- American Statistical Association (1997), Ethical Guidelines #8: explicit warning against multiple-testing abuse
- Bruss (1984): secretary problem / 1/e-law optimal stopping

---

## Provenance Note

Full PDF read directly: title page, abstract, all main-text sections (Multiple Testing, Selection Bias, Backtest Overfitting, memory-effects discussion, holdout-method critique, general approaches to multiple testing, Expected Sharpe Ratios Under Multiple Trials, the Deflated Sharpe Ratio, the numerical example, When Should We Stop Testing, Conclusions), Appendices A.1-A.3 (derivation, experimental verification, estimating independent trials), and Exhibits 1-4 (all read and interpreted from rendered page images).

---

## See Also

- [[quantitative-finance]] — domain page
- [[Deflated-Sharpe-Ratio]] — dedicated concept page for the DSR formula and application
- [[Backtest-Overfitting]] — dedicated concept page for the broader multiple-testing/selection-bias problem
- [[Marcos Lopez de Prado]] — co-author entity page
- [[zhang2026-benchmarking-deep-ts-equity]] — uses BH-FDR, Bonferroni, and SPA multiple-testing screens on the same underlying disease (selection bias across many model/architecture trials)
