---
type: concept
address: c-000073
title: "Machine Theory of Mind"
domain: ai-ml
status: developing
created: 2026-07-10
updated: 2026-07-10
tags:
  - concept
  - ai-ml
  - theory-of-mind
  - llm-cognition
  - benchmarks
related:
  - "[[li2026-llm-psychology-measurement-survey]]"
  - "[[LLM Psychological Assessment Paradigms]]"
  - "[[Psychometric Validity for LLMs]]"
---

# Machine Theory of Mind

Whether LLMs can represent other minds — beliefs, intentions, emotions — well enough to reason about them. This is the **theoretical-plausibility leg** of the LLM-psychometrics argument in [[li2026-llm-psychology-measurement-survey]]: if a model has no working model of mental states, it has no business measuring them.

---

## The Evidence For

| Test | Result |
|------|--------|
| Sally-Anne (first-order false belief) | GPT-3.5 ≈ 93%, comparable to 9-year-old children |
| Strange Stories (sarcasm, metaphor, nonliteral mental states) | GPT-4 ≈ adult humans |
| Hi-ToM (higher-order ToM) | Adult-level for some models; degrades on second-order tasks |

The developmental framing is deliberate: LLM ToM performance is benchmarked against children's milestones, and the trajectory across model generations resembles a compressed developmental curve. This underwrites the survey's position against the "sophisticated statistical learners" null hypothesis — something measurement-relevant is emerging, whether or not it deserves the word "understanding."

## The Critique

The survey is blunt about benchmark validity:

- Most benchmarks measure **literal ToM** — predicting behavior from stated beliefs in a vignette — not **functional ToM** — adapting to a real partner in live context. The distinction is the difference between passing a test about minds and using a model of a mind.
- Cited verbatim position: "theory of mind benchmarks are broken for large language models" — training contamination and shortcut features inflate scores.
- Performance is brittle: second-order tasks (what A believes B believes) degrade sharply relative to first-order.

Benchmarks in the space: ToMBench (bilingual, 8 task categories), Hi-ToM, MindGames (dynamic epistemic logic), EmoBench (emotional intelligence), ValueBench (value orientations).

---

## Why It Matters Here

- For **measurement**: functional ToM is the capability actually needed by active conversational assessment ([[LLM Psychological Assessment Paradigms]] paradigm 1) — an interviewer that cannot track what the interviewee believes mid-conversation cannot probe. Literal-ToM benchmark scores overstate readiness.
- For the **individuation app**: interpreting a dream requires modeling the dreamer's conscious attitude (compensation is defined against it — [[Dream Compensation]]). That is a functional-ToM demand. The broken-benchmark caveat says: don't infer this capability from published scores; test it against the actual dreamer's corrections.

---

## See Also

- [[li2026-llm-psychology-measurement-survey]] — source
- [[Psychometric Validity for LLMs]] — the same skepticism applied to the measurement claims themselves
