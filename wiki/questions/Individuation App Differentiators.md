---
type: synthesis
title: "Individuation App Differentiators"
domain: business
created: 2026-07-05
updated: 2026-07-05
tags:
  - individuation-app
  - dream-app
  - product-strategy
  - roadmap
status: developing
question: "What 10 things would improve the individuation app and separate it from every other dream app?"
answer_quality: solid
related:
  - "[[Working with Dream Symbols]]"
  - "[[CW8 Dream Methodology]]"
  - "[[Dream Compensation]]"
  - "[[Amplification]]"
  - "[[Dream Dramatic Structure]]"
  - "[[Structural Dream Analysis]]"
  - "[[Dream Recall]]"
---

# Individuation App Differentiators

Ten features that separate the app from dream journals and raw-LLM dream chat.
Companion to `individuation-app/docs/design.md` v0.1, which already covers the
foundation (interactive stages, ¶-anchored citations, series tracking, the
dream-app merge). These are the next layer — ordered roughly by
differentiation-per-effort, with build phase noted.

Competitive frame: journaling apps store dreams and don't interpret; LLM chat
interprets without method, grounding, or memory. Everything below is something
neither category can copy cheaply, because each depends on the corpus, the
encoded method, or accumulated per-user data.

## 1. Wake-time voice capture

Dreams decay within minutes of waking; typing is the single biggest friction
in dream journaling (see [[Dream Recall]]). A voice note at 6am →
transcription → Stage 0 capture, with the app asking the conscious-situation
and affect questions aloud. Every competitor assumes a typed entry hours
later. Cheap (transcription API + prompt), and it raises the volume and
fidelity of the core asset — the dream series. **Phase 0–1.**

## 2. Association-test onboarding (the complex map)

Jung's word-association experiment (CW 2) as onboarding: a short
reaction-word session whose delays, repetitions, and blanks sketch the
user's feeling-toned complexes. Interpretations then reference the user's
own complex map — "the delay on *bridge* in your onboarding session is
worth holding next to this dream." No app on the market has this; it is
maximally Jungian and impossible to fake without the method. **Phase 1;
prototype as a CLI session.**

## 3. Personal symbol lexicon

The app accumulates the dreamer's per-symbol associations (Stage 2 output)
into a personal lexicon that **outranks** corpus amplification once a symbol
has ≥2–3 associated occurrences. *Your* snake, learned from you, cited back
to your own dreams. This is the per-user data moat: a year in, the lexicon
is irreplaceable and switching cost is total. Journaling apps have the raw
text but no structure; LLM chat has neither. **Phase 1 — falls out of the
occurrences table almost for free.**

## 4. Active imagination mode

After Stage 4, offer a guided [[Amplification]]-adjacent session: dialogue
with a dream figure, circumambulation of the central image, transcript filed
alongside the dream. Jung's actual prescription was never interpretation
alone — the dream material is worked further. This moves the app from
"explains dreams" to "conducts the practice," a category no competitor
occupies. Needs the clinical-severity guardrail from design v0.1 first.
**Phase 1–2.**

Design note: [[Mental Screen]] (Turchin's mental-screen/visual-screen
typology, see [[turchin-active-imagination-lucid-dreaming]]) is directly
actionable here — screen the user's imaginal type before promising "vivid"
visualization, accept text/verbal-only engagement as first-class (not a
degraded fallback; see [[Aphantasia]]), and decide explicitly whether this
feature follows the classical discovery-not-invention model or a more
scripted, goal-formulating protocol — [[Active Imagination]] now documents
a live `[!contradiction]` between the two.

## 5. Big-dream detection

Score each dream on affect intensity × archetypal density × collective
imagery (extract stage already tags `kind` and `salience`). Little dreams
get the light treatment design v0.1 mandates; flagged big dreams get the
full apparatus and are marked as milestones. The inverse discipline —
*refusing* depth on trivial dreams — is itself the credibility feature.
**Phase 0–1 — mostly a scoring rule over existing tags.**

## 6. Individuation timeline

The series view: motif drift mapped against Jung's individuation markers —
shadow figures → anima/animus encounters → Self/mandala imagery — modeled on
the Pauli series (CW 12 Part II, next corpus target). This is the visual
artifact that makes the moat *visible to the user*: months of dreams
rendered as an arc, big dreams as milestones, open compensation hypotheses
as threads. The screenshot people share. **Phase 2; needs ≥30 dreams and
CW 12 ingested.**

## 7. Proactive compensation check-ins

The compensation ledger goes active: days or weeks after a hypothesis is
filed, the app asks whether the one-sidedness shifted ("three weeks ago the
hypothesis was X — did anything move?"). Closes the hypothesis → outcome
loop that [[Dream Compensation]] requires, generates longitudinal validation
data no one else has, and is the retention mechanic. **Phase 1 — a scheduled
prompt over the sessions table.**

## 8. Analyst-ready session export

One clean page per session: dream text, dramatic structure, the dreamer's
own associations, cited parallels (CW volume + ¶), open hypothesis, dreamer
response. An analysand brings it to their real analyst. Positions the app as
adjunct rather than replacement — defuses the "AI analysis" objection — and
opens the B2B channel to Jungian therapists, who become distributors instead
of critics. **Phase 2, trivial rendering work once sessions persist.**

## 9. Provenance-tiered corpus

Every retrieved passage labeled by tier: Jung primary (CW, seminars) vs
post-Jungian (von Franz, Edinger, Hillman), with a "Jung only" filter.
The target user knows the difference between Jung and Jungians; showing the
seams is scholarly credibility no black-box competitor can match, and it
makes the citation contract stronger, not weaker. **Phase 1 — one metadata
field at ingest time; retrofitting later is expensive.**

## 10. Fully-local privacy mode

An optional local-LLM path so no dream ever leaves the device — privacy as a
paid tier, not a policy page. Dreams plus conscious situation are maximally
sensitive data; for analysands and therapists this is the difference between
usable and not. Quality will trail the API path, so frame it as a mode, not
the default. **Phase 2+; revisit when local models clear the synthesis bar.**

## What this list deliberately excludes

More corpus ingestion beyond the planned targets (Dream Analysis seminar,
CW 12 Part II, CW 16), social/community features (wrong for this data), and
the general wellness market (designing for it is how output goes generic —
per the PRD). The moat compounds through method + citations + per-user data,
not breadth.

## Build order summary

| Now (Phase 0–1) | Next (Phase 1–2) | Later (Phase 2+) |
|---|---|---|
| 5 big-dream detection | 2 association test | 6 individuation timeline |
| 1 voice capture | 4 active imagination | 8 analyst export |
| 9 provenance tags at ingest | 7 compensation check-ins | 10 local mode |
| 3 symbol lexicon | | |
