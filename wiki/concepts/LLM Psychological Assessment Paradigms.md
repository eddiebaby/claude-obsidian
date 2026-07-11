---
type: concept
address: c-000072
title: "LLM Psychological Assessment Paradigms"
domain: ai-ml
status: developing
created: 2026-07-10
updated: 2026-07-10
tags:
  - concept
  - ai-ml
  - llm-psychometrics
  - assessment
related:
  - "[[li2026-llm-psychology-measurement-survey]]"
  - "[[Psychometric Validity for LLMs]]"
  - "[[Machine Theory of Mind]]"
  - "[[Individuation App Differentiators]]"
  - "[[Structural Dream Analysis]]"
---

# LLM Psychological Assessment Paradigms

The three ways an LLM can measure a human's psychological state, per [[li2026-llm-psychology-measurement-survey]] (Li et al. 2026). The taxonomy matters because each paradigm has different data requirements, different validity ceilings, and different failure modes.

---

## 1. Active / Conversational Assessment

The LLM engages the person in real-time dialogue — conducting an interview, administering a questionnaire, or steering an interaction toward diagnostic signal.

**Methods**: zero-shot open-ended interviewing; few-shot with demonstrations; chain-of-thought decomposition of assessment into reasoning stages; agent architectures with dedicated behavior-recognition and response-generation modules.

**Representative systems**: PsyCoT (questionnaire items as iterative reasoning chains), PsychoGAT (survey items converted into game scenarios — reached Cronbach's α=0.97 for extraversion), WundtGPT (fine-tuned empathetic interviewer), Chain of Empathy (therapeutic reasoning steps), GATE (information-gathering dialogues with clarification).

**Strength**: can adaptively probe, like a clinician. **Weakness**: the model's own response biases (social desirability, prompt sensitivity) contaminate the instrument itself.

## 2. Passive Assessment from Natural Language

The LLM infers psychological states from text the person already produced — social media, diaries, clinical notes — with no interaction.

**Methods**: zero/few-shot classification; staged chain-of-thought (e.g. sentiment → classification → cause → severity); task reformulation (personality as natural-language inference); retrieval-augmented generation to ground outputs; instruction fine-tuning on labeled corpora (Dreaddit for stress, PANDORA for Big Five).

**Strength**: ecological validity — real behavior, not test-taking behavior. **Weakness**: no ability to probe; label quality of training corpora caps everything.

## 3. Multimodal Fusion Assessment

Text plus other channels — speech prosody, facial expression, physiological/wearable data — approximating a clinician's multi-channel perception.

**Examples**: Q-Former text-image fusion (A2II); smartphone/wearable behavioral streams (activity, sleep) fused with text reasoning (61.1% accuracy, Englhardt et al.); native multimodal LLMs on audio-visual emotional cues (EmoVerse).

**Strength**: constructs like depression are partly somatic; text alone misses it. **Weakness**: least mature; modest absolute accuracy so far.

---

## The Enclosing Framework

The paradigms are the middle leg of the survey's three-dimension frame:

| Dimension | Question | Where it lives |
|-----------|----------|----------------|
| Theoretical plausibility | *Why* can a language model measure a psyche at all? | [[Machine Theory of Mind]] |
| Measurement methodology | *How* to measure | this page |
| Application effectiveness | *What* has been measured, how well | [[Psychometric Validity for LLMs]] |

---

## Application to the Individuation App

- Dream-journal analysis = paradigm 2 (passive). The staged-CoT result transfers directly: amplification-style structured reasoning over a dream text should beat single-shot interpretation, which matches the existing [[Working with Dream Symbols]] loop design.
- Association-test onboarding and compensation check-ins ([[Individuation App Differentiators]]) = paradigm 1 (active). PsychoGAT is prior art for disguising assessment items inside an engaging interaction.
- Voice capture opens paradigm 3 later (prosody as affect channel).
- Whatever paradigm is used, the validity ceilings in [[Psychometric Validity for LLMs]] apply — the app should treat LLM readings as hypotheses for the dreamer to test, never verdicts ([[Orphic Listening]]).

---

## See Also

- [[li2026-llm-psychology-measurement-survey]] — source
- [[Psychometric Validity for LLMs]] — what these paradigms can and cannot claim
- [[Machine Theory of Mind]] — the plausibility argument underneath all three
