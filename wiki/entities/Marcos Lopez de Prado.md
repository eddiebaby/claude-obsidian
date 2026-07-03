---
type: entity
address: c-000025
title: "Marcos Lopez de Prado"
entity_type: person
domain: quantitative-finance
role: "Quantitative researcher and practitioner; author, Advances in Financial Machine Learning"
first_mentioned: "[[bailey-lopez-de-prado-2014-deflated-sharpe]]"
created: 2026-07-02
updated: 2026-07-02
tags:
  - entity
  - person
  - quantitative-finance
status: developing
related:
  - "[[bailey-lopez-de-prado-2014-deflated-sharpe]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[Backtest-Overfitting]]"
  - "[[das2026-chronos-multivariate-forecasting]]"
sources:
  - "[[bailey-lopez-de-prado-2014-deflated-sharpe]]"
---

# Marcos Lopez de Prado

Navigation: [[quantitative-finance]]

## Overview

Marcos Lopez de Prado is a quantitative finance researcher and practitioner working at the intersection of statistics, machine learning, and investment management. At the time of the 2014 paper ingested into this vault ([[bailey-lopez-de-prado-2014-deflated-sharpe]]), he held the title of Senior Managing Director at Guggenheim Partners (New York) and Research Affiliate at the Computational Research Division of Lawrence Berkeley National Laboratory (LBNL). He is best known in the vault's context for co-developing rigorous statistical corrections for backtest overfitting and selection bias in strategy research, and for authoring the widely cited book *Advances in Financial Machine Learning* (2018), already cited (uncredited with a dedicated page until now) in [[das2026-chronos-multivariate-forecasting]].

## Key Facts

- Co-author, with David H. Bailey (LBNL, retired; UC Davis), of "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality" (Journal of Portfolio Management, 2014) — see [[bailey-lopez-de-prado-2014-deflated-sharpe]].
- Co-developer of the **Probabilistic Sharpe Ratio (PSR)** (Bailey & Lopez de Prado, 2012a), the statistical building block underneath the **Deflated Sharpe Ratio (DSR)** — see [[Deflated-Sharpe-Ratio]].
- Co-developer of the **Probability of Backtest Overfitting (PBO)** framework (Bailey et al., 2013), a non-parametric cross-validation diagnostic for [[Backtest-Overfitting]].
- Author of *Advances in Financial Machine Learning* (Wiley, 2018) — a standard reference text on applying ML rigorously to finance, cited in [[das2026-chronos-multivariate-forecasting]] as prior literature.
- Research focus: statistically sound strategy validation, guarding against false discoveries in systematic/quant finance, meta-labeling, and financial ML methodology generally.

## Connections

- Co-author David H. Bailey — recurring collaborator on backtest-overfitting statistics (2012a PSR, 2013 PBO, 2014 DSR, 2014a expected-maximum-Sharpe derivation).
- His DSR/PBO framework is conceptually related to the multiple-testing corrections (BH-FDR, Bonferroni, SPA, Model Confidence Set) used in [[zhang2026-benchmarking-deep-ts-equity]] — same underlying statistical problem (selection bias across many trials), different specific tools.
- Cited as background literature in [[das2026-chronos-multivariate-forecasting]] via *Advances in Financial Machine Learning* (2018).

## Sources

- [[bailey-lopez-de-prado-2014-deflated-sharpe]]
