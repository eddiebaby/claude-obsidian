---
type: concept
address: c-000074
title: "Psychometric Validity for LLMs"
domain: ai-ml
status: developing
created: 2026-07-10
updated: 2026-07-10
tags:
  - concept
  - ai-ml
  - psychometrics
  - validity
  - reliability
related:
  - "[[li2026-llm-psychology-measurement-survey]]"
  - "[[LLM Psychological Assessment Paradigms]]"
  - "[[Machine Theory of Mind]]"
  - "[[Orphic Listening]]"
  - "[[Maker-Checker-Pattern]]"
---

# Psychometric Validity for LLMs

The map of which classical psychometric properties LLM-based assessment has demonstrated and which it hasn't, per [[li2026-llm-psychology-measurement-survey]]. This is the page to consult before trusting any LLM claim about a psyche — the model's or a human's.

---

## The Validity Scorecard

| Property | Meaning | Status for LLM assessment |
|----------|---------|---------------------------|
| Convergent validity | Agrees with established instruments measuring the same construct | **Demonstrated** (moderate-to-strong for Big Five; GPT-4 r ≈ 0.443 zero-shot) |
| Internal consistency | Items hang together | Demonstrated in spots (PsychoGAT α = 0.97) |
| Test-retest reliability | Same answer tomorrow | **Largely untested**; known temporal instability |
| Discriminant validity | Distinguishes closely related constructs | **Unresolved** |
| Criterion validity | Predicts real-world outcomes | **Lacks empirical support** |
| Cross-cultural invariance | Holds outside English/Western samples | **Largely untested** |

The pattern: the easy column is filled, the hard columns are empty. Convergent validity is the cheapest property to demonstrate and the only one consistently shown.

---

## Systematic Failure Modes

1. **Temporal instability** — repeated administrations drift; a measurement that changes on re-test is not a measurement.
2. **Reverse-item inconsistency** — negatively-worded items mishandled; instruments assume item polarity is respected.
3. **Social desirability bias** — LLMs reproduce the human tendency to answer virtuously, defeating the controls built into instruments.
4. **Structural validity drift** — trait intercorrelations diverge from human norms (e.g. unusual openness-conscientiousness relations), so scores don't sit in the same construct space.
5. **Prompt sensitivity** — the "instrument" changes with phrasing; named a principal unresolved issue.
6. **Opacity** — outputs "inherently opaque and difficult to audit"; traditional questionnaires retain a hard interpretability advantage. RAG (grounding claims in retrievable evidence) is the proposed partial fix.

---

## The Practical Doctrine

- LLMs are **screening and triage** instruments today, not diagnostic ones: "cannot yet be considered reliable substitutes for human-administered assessments in high-stakes contexts."
- The robust deployment pattern is **hybrid**: LLM automation anchored by a validated traditional instrument — the LLM proposes, the instrument disposes. Structurally this is the [[Maker-Checker-Pattern]] with a psychometric checker.
- Interpretability demands provenance: claims should point at the evidence (quotes, retrieved items) that produced them — same discipline as [[Source-First Synthesis]] in this vault.

---

## For the Individuation App

This scorecard is the epistemic guardrail for every LLM reading of dreams, journals, or check-ins:

- Present LLM interpretations as **hypotheses carrying uncertainty**, never as verdicts — the psychometric argument for what [[Orphic Listening]] argues clinically.
- Prefer designs where the *dreamer's confirmation* is the criterion — the dreamer-response field in the app design is exactly the missing criterion-validity loop.
- Log interpretations over time: temporal instability is measurable in-app (re-run an old dream, diff the reading), and the individuation timeline feature could double as a stability audit.
- If a validated anchor is wanted, [[Structural Dream Analysis]] is the natural one for dream material — an empirically confirmed coding scheme the LLM's output can be checked against.

---

## See Also

- [[li2026-llm-psychology-measurement-survey]] — source
- [[LLM Psychological Assessment Paradigms]] — the methods this scorecard evaluates
- [[Machine Theory of Mind]] — the capability question underneath
