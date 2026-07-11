---
type: source
address: c-000071
title: "A Survey of Large Language Models for Perception and Measurement of Human Psychology"
domain: ai-ml
status: complete
created: 2026-07-10
updated: 2026-07-10
tags:
  - source
  - paper
  - ai-ml
  - llm-psychometrics
  - personality-assessment
  - mental-health
  - theory-of-mind
related:
  - "[[ai-ml]]"
  - "[[LLM Psychological Assessment Paradigms]]"
  - "[[Machine Theory of Mind]]"
  - "[[Psychometric Validity for LLMs]]"
  - "[[Individuation App Differentiators]]"
  - "[[Psychological Types]]"
  - "[[Structural Dream Analysis]]"
source_type: paper
author: "Yudong Li, Xiaoyi Chen, Jiawei Cai, Zehao Zhong, Haoyang Yang, Huajin Tang, Linlin Shen"
date_published: 2026-05-20
url: "https://arxiv.org/abs/2606.20603"
confidence: medium-high
key_claims:
  - "LLMs can measure psychological constructs through three paradigms — active conversational assessment, passive natural language analysis, and multimodal fusion — with best-in-class results approaching but not matching validated instruments."
  - "GPT-4 zero-shot Big Five inference from open-ended interviews correlates up to r=0.443 with standardized measures; interactive assessment (PsychoGAT) reaches Cronbach's α=0.97; fine-tuned models reach R²=0.59 on PANDORA."
  - "Convergent validity is demonstrated for Big Five, but test-retest reliability, discriminant validity, criterion validity, and cross-cultural invariance remain largely untested — LLMs cannot yet substitute for human-administered assessment in high-stakes contexts."
  - "LLM self- and other-assessment suffers systematic failure modes: temporal instability, inconsistent reverse-item handling, and human-like social desirability bias."
  - "Most Theory-of-Mind benchmarks measure literal ToM (predicting behavior from stated beliefs) rather than functional ToM (adapting to a partner in context), weakening the theoretical-plausibility case built on them."
---

# A Survey of Large Language Models for Perception and Measurement of Human Psychology

Navigation: [[ai-ml]] | [[sources/_index|Sources]]

---

## Bibliographic Record

| Field | Detail |
|-------|--------|
| Authors | Yudong Li, Xiaoyi Chen, Jiawei Cai, Zehao Zhong, Haoyang Yang, Huajin Tang, Linlin Shen |
| Submitted | May 20, 2026 |
| arXiv | [2606.20603](https://arxiv.org/abs/2606.20603) [cs.CY] |
| Venue | Accepted, IEEE Transactions on Cognitive and Developmental Systems |
| Positioning | Focuses on the **psychometric properties of LLMs as measurement instruments** — distinct from the "LLM psychology" literature that treats models as subjects of study |

---

## What the Survey Does

Asks whether LLMs can *measure* human psychological constructs — personality, emotion, mental health — reliably enough to matter. Organizes the entire literature along a three-dimensional framework:

1. **Theoretical plausibility (why measurement is possible)** — do LLMs have the cognitive prerequisites? The evidence marshalled is Theory-of-Mind performance approaching human developmental milestones → [[Machine Theory of Mind]].
2. **Measurement methodology (how to measure)** — three paradigms: active conversational assessment, passive natural language analysis, multimodal fusion → [[LLM Psychological Assessment Paradigms]].
3. **Application effectiveness (what has been measured)** — personality and mental-health results, and the reliability/validity gaps → [[Psychometric Validity for LLMs]].

Constructs covered: Big Five, MBTI, HEXACO, Dark Triad, 16PF (personality); depression, anxiety, PTSD, stress, emotion/sentiment (mental health & affect); Theory of Mind, cognitive workload, moral reasoning (cognitive).

---

## Headline Results

### Personality assessment

| Result | Number | Caveat |
|--------|--------|--------|
| GPT-4 zero-shot Big Five from open-ended interview | r ≈ 0.443 vs standardized measures | Moderate, not clinical-grade |
| PsychoGAT interactive (survey items → game scenarios) | Cronbach's α = 0.97 (extraversion) | Internal consistency, not accuracy |
| RoBERTa fine-tuned on PANDORA (~17M Reddit comments) | R² = 0.59 | Fine-tuned beats zero-shot |
| MBTI prediction from social media | up to 93.5% | Varies substantially by trait and context |

### Mental health assessment

- Staged chain-of-thought (sentiment → binary classification → cause → severity) substantially improves detection accuracy (Teng et al.).
- Instruction-tuned models (Mental-Alpaca, Mental-FLAN-T5) match state-of-the-art task-specific models on depression/stress from online text.
- Multimodal integration of wearable behavioral data with LLM reasoning: 61.1% accuracy (Englhardt et al.) — promising direction, unimpressive absolute number.
- Zero-shot GPT is competitive with fine-tuned models for multilingual psychological text analysis (~48k instances).

### The verdict

> LLMs "cannot yet be considered reliable substitutes for human-administered assessments in high-stakes contexts."

Suited today for **screening and triage**, not diagnosis. The surviving use case is hybrid: LLM automation + validated traditional instruments as anchor.

---

## Failure Modes Documented

- **Temporal instability** — repeated administrations of the same personality test to the same model/person-model pair drift.
- **Reverse-item inconsistency** — negatively-worded questionnaire items are mishandled, a basic psychometric failure.
- **Social desirability bias** — models skew toward socially desirable answers, mimicking the human response bias that instruments were designed to control for.
- **Structural validity drift** — trait intercorrelations in LLM responses diverge from human norms.
- **Hallucination** — plausible but ungrounded clinical judgments; flagged as misdiagnosis risk.
- **Prompt sensitivity** — named a "principal unresolved issue"; results move with phrasing.

---

## Future Directions (authors')

Contamination-resistant benchmarks; multilingual and cross-cultural validation; psychometrically grounded standards for LLM assessment; hybrid LLM + validated-instrument paradigms; hallucination mitigation; extension to underrepresented frameworks (Eysenck PEN, MMPI-2, CPI, HPI); clinical virtual patients for clinician training; longitudinal stability research.

---

## Named Systems, Datasets, Benchmarks (selected)

| Category | Names |
|----------|-------|
| Active assessment systems | PsyCoT, PsychoGAT, WundtGPT, Chain of Empathy, GATE, PsyChat, CaiTI |
| Passive assessment models | Mental-Alpaca, Mental-FLAN-T5, Affective-NLI, PostToPersonality (RAG for MBTI), ProMind-LLM, EmoLLMs |
| Multimodal | A2II (Q-Former fusion), EmoVerse |
| Datasets | PANDORA (~17M Reddit, Big Five+MBTI+Enneagram), Essays, Dreaddit (stress), E-DAIC (clinical interviews), PsyQA, CPED, Globem (longitudinal wearables) |
| ToM/EQ benchmarks | ToMBench, Hi-ToM, EmoBench, MindGames, ValueBench, Sally-Anne, Strange Stories |

---

## Relevance to the Individuation App

This survey is the **validity map** for any feature where an LLM reads Scott's psychological material:

- Dream-journal and active-imagination analysis is exactly the survey's *passive natural language analysis* paradigm — its documented failure modes (temporal instability, social desirability, opacity) are the app's failure modes.
- Check-in dialogues and association-test onboarding ([[Individuation App Differentiators]]) fall under *active conversational assessment* — PsychoGAT's game-ification of survey items is prior art for the association-test onboarding idea.
- The "cannot substitute for validated instruments" verdict supports the app's existing design stance: LLM as amplifier and mirror, never as diagnostic verdict — converging with [[Orphic Listening]]'s no-confirming-verdict rule from the depth-psychology side.
- MBTI results connect to Jung's typology ([[Psychological Types]]): the typology the field measures at 93.5% accuracy is the pop-derivative of CW 6, and the survey notes even that number is unstable across traits and contexts.
- [[Structural Dream Analysis]] (Roesler) is the depth-psychology counterpart: an empirically validated coding scheme for psychological material in text. A future app pipeline could treat SDA patterns as the validated instrument that anchors LLM passive assessment.

---

## Provenance Note

Ingested from the arXiv HTML rendering (arxiv.org/html/2606.20603v1) via three WebFetch extraction passes (structure/framework, findings/limitations, systems/datasets); the PDF was not read directly. Specific figures (r=0.443, α=0.97, 93.5%, 61.1%, R²=0.59) are as reported by the extraction and should be re-verified against the PDF before being cited anywhere that matters. No Latin phrases found (standing ingest rule checked).

---

## See Also

- [[LLM Psychological Assessment Paradigms]] — the three-paradigm taxonomy (concept)
- [[Machine Theory of Mind]] — the theoretical-plausibility leg (concept)
- [[Psychometric Validity for LLMs]] — the validity/reliability gap map (concept)
- [[ai-ml]] — domain page
- [[jung-dream-app-design]] — the app design this survey's caveats apply to
