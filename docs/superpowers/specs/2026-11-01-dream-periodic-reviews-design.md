# Dream Periodic Reviews — Design

**Date:** 2026-11-01 · **Status:** approved in chat, built same day · **Owner:** Scott (first user)

## Intent

Monthly, quarterly and yearly reviews of the dream series, as milestones alongside the [[longitudinal-study]]. Every review answers one question first: **what was this period about?** It's the "series digest" of `individuation-app/docs/design.md` §3.4 (the retention feature), expanded.

## Goals

- One review page per calendar month, quarter (Q1 = Jan–Mar) and year, in `wiki/dreams/reviews/`.
- All 39 features Scott selected on the 2026-11-01 board (listed below), plus the design doc's "reading may be stuck" tripwire.
- Tiered page: the top (verdict, numbers, firsts) reads in a minute; everything else sits below.
- The review states its own confidence: association debt, hit rate, predictions graded.

## Non-goals

- Waking life. The review reads only the dreams. Conscious situation, associations and day residue come in only as Scott wrote them into entries.
- Other users. Designed for Scott; the multi-user version gets its own pass.
- The app shell / UI. Pages are Obsidian markdown for now.

## Anti-goals

- Numbers that can't be reproduced. Every count comes from code over frontmatter, never from the model.
- A verdict that hides its confidence. A month analyzed without associations says so at the top.

## Architecture: two halves

1. **Counted half: `dreamapp review`** (`dream-app/src/dreamapp/review.py`). Reads `wiki/dreams/2026-*.md` frontmatter and sections, excludes `type != dream`, and emits markdown (stdout) plus JSON (`--json`). Deterministic and unit-tested.
   - `dreamapp review --month 2026-10 | --quarter 2026-Q3 | --year 2026 [--json PATH] [--today YYYY-MM-DD]`
2. **Read half: the `/dream` skill, Phase 5** (`.claude/skills/dream/SKILL.md`). Claude runs the script, reads the period's dreams, [[dream-threads]], [[longitudinal-study]] and the previous review, then writes the interpretive sections. No API key needed. Later the app can call the same script and use the API for this half.

## Features, and which half supplies each

C = computed by script · R = read by Claude from computed inputs · C+R = script supplies the data, Claude writes it up.

**Monthly:** M1 verdict (R) · M2 numbers (C) · M3 agency chart (C) · M4 thread movement board (R) · M5 figure arcs (C+R) · M6 cast list: new / returning / gone (C) · M7 rising/falling motifs (C) · M8 what the unconscious was correcting (R) · M9 stance profile (C+R: agency bands, exits, fights) · M10 firsts (C+R: first-in-series figures/motifs, plus thread firsts) · M11 dream of the month (R) · M12 image of the month (R) · M13 signals re-sent (C+R: recurring motifs/symbols) · M14 elements and states (C heuristic + R) · M15 feeling-tone (C extract + R) · M16 synchronicities (R) · M17 hit rate (C) · M18 waking-action ledger (C) · M19 association debt (C) · M20 last period's predictions graded (C extract + R) · M21 watch next period (R) · M22 questions to sit with (R) · **M23 tripwire, "the reading may be stuck"** (R, from design.md).

**Quarterly** adds: Q1 phase call · Q2 agency trend across months (C) · Q3 thread lifecycle · Q4 readings to revise · Q5 figure transformations · Q6 calibration: hit rate and predictions over time (C+R) · Q7 big dreams · Q8 the quarter's one assignment.

**Yearly** adds: Y1 the year's story · Y2 the initial dream re-read · Y3 arcs-and-phases timeline · Y4 then vs. now · Y5 figure census (C+R) · Y6 dreams of the year · Y7 assignments done vs. open · Y8 anniversary view (from year two) · Y9 what to carry forward.

## Decisions (builder's calls, flagged for Scott)

- **Periods are calendar-based.** A period still in progress is marked *partial*, and cadence divides by days elapsed.
- **"Previous period"** is the immediately preceding month/quarter/year. Comparisons (motif deltas, gone figures, agency change) are against it.
- **Generic figures** (`unknown-woman`, `unknown-man`, `old-man`, `old-woman`) count in totals but never as "new" or "gone."
- **Elements** come from a keyword heuristic over motifs and symbols. The script labels it heuristic; Claude supplies the *state* (frozen, flowing, released).
- **The 06-27 dream** lives in `wiki/questions/`, outside `wiki/dreams/`, so it isn't counted. Move it to count it.
- **Page names:** `reviews/2026-10-month.md`, `reviews/2026-Q3-quarter.md`, `reviews/2026-year.md`. Frontmatter `type: dream-review`, so Dataview tables of `type = dream` are unaffected.
