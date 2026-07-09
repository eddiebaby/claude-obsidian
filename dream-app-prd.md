---
name: dream-app-prd
type: prd
title: "Jungian Dream App — PRD v1"
domain: business
created: 2026-07-01
updated: 2026-07-01
status: draft
tags:
  - project
  - dream-app
  - prd
related:
  - "[[dream-app-phase0-spec]]"
  - "[[dream-app-build-spec]]"
---

# Jungian Dream App — PRD v1

Companion to [[dream-app-phase0-spec]]. The spec says how to build Phase 0. This says why the product exists, who pays, what the phases are, and exactly how to start this week.

## One-liner

A dream interpretation engine grounded in a curated Jung corpus: source-cited, methodologically Jungian interpretations plus longitudinal symbol tracking across a dream series. For people who read Jung, not people who read horoscopes.

## Problem

Dream journal apps store dreams; they don't interpret them. Raw LLM chat interprets them badly: generic, ungrounded, no method, no memory across dreams. Serious Jung readers want compensation, amplification, and the objective/subjective levels applied with citations to real texts, and they want to see a symbol evolve across months of dreams (dream series = individuation, CW 8 ¶550). Nothing on the market does this.

## Target user

Primary: serious Jung readers. Analysands, individuation practitioners, Jungian-adjacent therapists, people who journal dreams and read the Collected Works directly. Payment hypothesis: this segment already pays $150+/session for analysis and buys $30 Bollingen hardcovers; $10-20/mo for a tool that does real amplification is plausible. Validate in Phase 2, not before.

Explicitly not the target yet: the general wellness market. Designing for them is how the output goes generic.

## Moat

1. **The corpus**: 297 wiki pages built from direct reading (CW 5, 8, 9i, 9ii, 12, 13 in progress, von Franz, Edinger, Hillman, Man and His Symbols). Every interpretation retrieves from this, not from model memory.
2. **The method**: interpretation follows Jung's actual procedure. Compensatory function first, amplification gated by [[Working with Dream Symbols]] (when archetypal reading is licensed at all), objective and subjective levels, ends with a question rather than a verdict. [[CW8 Dream Methodology]] is the theoretical backbone.
3. **The data model**: `symbols:`/`archetypes:` frontmatter on every analyzed dream. Phase 1 longitudinal tracking reads it directly. Journaling apps have no equivalent.

## Product principles

1. Grounded or silent: cite corpus pages or flag thin coverage. Never confabulate.
2. Non-obvious or nothing: output a careful reader could produce by rereading the dream is failure.
3. A question, not a verdict: no fortune-telling.
4. Written for people who already hold the concepts: no definitions of "shadow."
5. Dreams are sensitive: a written privacy stance before any volunteer dream enters the pipeline.

## Phases and gates

**Phase 0: prove the engine** (now through ~end of July). Local Python CLI, 4-stage pipeline (extract → retrieve → synthesize → writeback). Full detail: [[dream-app-phase0-spec]]. Gate to Phase 1/2: majority of 20-30 real dreams score as non-obvious, grounded, Jungian, and honest about gaps.

**Phase 1: longitudinal tracking.** Reads `symbols:`/`archetypes:` across `wiki/dreams/`, surfaces recurrence, transformation arcs, compensation patterns over time. Still local. Gate: produces at least one series-level insight per month that single-dream reads miss.

**Phase 2: product.** FastAPI, web UI, auth, payments, per-user store, data-handling policy. Nothing here starts until the Phase 0 gate clears. Business signal: 10 paying users at ~$15/mo; 100 means it's real.

## Current state (verified against the vault, 2026-07-01)

| Asset | State |
|---|---|
| Corpus | 297 wiki pages, depth-psychology dominant |
| `scripts/retrieve.py` | Exists. **BM25 index NOT built** (`.vault-meta/bm25/index.json` missing, chunks empty). Exits 10 today. |
| `_templates/dream.md` | Exists with `symbols:`/`archetypes:`/`status:` fields |
| `wiki/dreams/` | 5 dreams (06-25 to 07-01), 3 hand-analyzed with frontmatter filled |
| Methodology pages | [[Working with Dream Symbols]], [[CW8 Dream Methodology]], [[Dream Compensation]], [[Amplification]] |
| `dream-app/` package | Does not exist. Greenfield. |

The 3 hand-analyzed dreams are the reference standard: pipeline output gets compared against what the manual sessions produced.

## The two real bottlenecks

**1. Retrieval isn't live.** The spec's Stage 2 assumes `retrieve.py` works. It doesn't until `bash bin/setup-retrieve.sh` builds the index. This is step zero.

**2. Validation set is 5 dreams; the gate needs 20-30.** Plan: keep the daily logging pace (~1/day since 06-25 puts you at ~25 by end of July), recruit 2-3 volunteers for 5+ dreams each (also forces the privacy stance early), optionally backfill remembered big dreams. Corpus gaps that the thin-coverage flag surfaces become the only sanctioned Jung reading during the build: read to fill retrieval gaps, nothing else. Building is the priority; the corpus is already deep enough to start.

## Kickoff plan (week of 2026-07-01)

Day 1: `bash bin/setup-retrieve.sh`, confirm index builds. Run `scripts/retrieve.py` on "snake", "water", "father", "milk", "court". Eyeball that it returns sane pages (the last two test against real logged dreams). If retrieval is bad, stop and fix it; it gates everything.
Day 2: scaffold `dream-app/` per [[dream-app-build-spec]] (the implementation contract; hand that file to the coding agent). Stage 1 extract + prompt; test on the 5 existing dream notes; check extracted symbols against the hand-filled frontmatter.
Day 3-4: Stage 3 synthesize + prompt. Iterate on the 3 hand-analyzed dreams; compare against the manual interpretations. Most of the total project risk dies or survives here.
Day 5: Stage 4 writeback, `pipeline.py`, `cli.py`. End-to-end on all 5 dreams. Score each on the 4-point rubric; log scores in a `validation.md` inside `dream-app/`.
Ongoing: every new dream goes through the pipeline the morning after. Prompt tuning weekly. Volunteer outreach starts week 2. Gate review when the set hits 20.

## Risks

Generic output: mitigated by grounding + the exit bar (spec covers this). Small validation set: covered above. Scope creep: Phase 2 is hard-gated; no Streamlit before the CLI proves the engine. Study drift: reading beyond thin-coverage flags is off-plan while Phase 0 is open. Privacy: one page written before the first volunteer dream (local processing, API data handling, deletion on request); reuse the thinking in `PRIVACY.md`.

## Open decisions

1. Volunteer channel: Jung reading groups, r/Jung, or local Hilo contacts.
2. Whether Phase 1 ships before Phase 2 starts or in parallel after the gate.
3. Name. Working title "dream-app" until the engine earns a real one.
