# Individuation App — Design v0.1

Status: corpus extraction working (CW 8, CW 9i). This document specifies the
three depth pillars: paragraph-anchored citations, the encoded method, and
dream-series tracking.

v0.1 (2026-07-05): folds in the depth-quality review. Key additions: the
consolidation decision (§0), interpretive judgment rules in Stage 4, the
dreamer-response capture as validation + eval set, clinical-severity stance,
and a revised MVP priority order.

v0.2 (2026-07-07): folds in two defects surfaced by a nine-dream vault
session (2026-06-25 → 07-07). Both are interpreter-quality bugs the v0.1
stages don't catch: (a) **self-narrative confirmation bias** — the
synthesizer steering every dream toward the user's own stated self-story is
anti-compensatory and is the horoscope failure mode in Jungian dress
(Stage 4, new counter-reading rule); (b) **series data integrity** — a
fabricated/test entry polluting the series and therefore the motif threads
(Stage 0 provenance field + series filter). Empirical basis for (a): across
that session, association richness tracked interpretation quality
monotonically, yet every cross-dream "thread" resolved to the one line in
the loaded user profile — nine dreams fit to a prior.

---

## 0. Consolidation: this app absorbs dream-app

`dream-app/` (working extract → retrieve → synthesize → writeback pipeline
over the 297 wiki pages) and this design are the same product built twice.
Decision: port the dream-app pipeline code onto this design rather than
maintaining both.

- **Corpus**: wiki pages are Scott's own synthesis — citing them is citing
  yourself. They serve as the concept-graph *router* (Stage 3, step 1); the
  ¶-anchored CW chunks are the *citable evidence*. "CW 8 ¶¶483–492" rendered
  as a citation is the credibility feature; "wiki/concepts/Foo.md" is not.
- **Pipeline shape**: dream-app's biggest depth flaw is that it is a one-shot
  batch job while Jung's method is dialogical. Its synthesize prompt demands
  personal associations before archetypal parallels, but nothing collects
  them, so the model fabricates the personal reading — the horoscope failure
  mode. Same circularity with compensation: no captured conscious situation
  means the model infers it from the dream itself. Stages 0 and 2 below are
  the fix; the port must make the CLI actually pause and ask.
- **Keep from dream-app**: the extract prompt's `personal | archetypal |
  ambiguous` + salience tagging (it drives the Stage-4 judgment rules below),
  the JSON output contract, the writeback + frontmatter data model, tests.

---

## 1. Corpus layer (built)

`extraction/extract_cw.py` extracts paragraph-anchored text from digital-edition
CW PDFs. Two conversion formats handled: marker-on-own-line (CW 8) and
marker-inline (CW 9i).

Per-paragraph record:

```json
{"volume": "CW 8", "para": 505, "essay": "General Aspects of Dream Psychology",
 "section": null, "pdf_page": 306, "text": "As against Freud's view..."}
```

Retrieval chunk (consecutive paragraphs, essay-bounded, ~700 tokens):

```json
{"volume": "CW 8", "essay": "On the Nature of Dreams",
 "para_start": 560, "para_end": 564,
 "header": "CW 8 — On the Nature of Dreams — paras. 560-564",
 "text": "[560] But if dreams produce such essential compensations..."}
```

**Citation contract:** every passage shown to the user carries `header` as its
citation, and the answer template requires it. No uncited claims about "what
Jung says." This is the whole credibility feature — enforce it at the prompt
level and at the UI level (citation is a rendered element, not text the model
may omit).

Extraction status:

| Volume | Paragraphs | Coverage | Known issues |
|--------|-----------|----------|--------------|
| CW 8   | 997 / 997 | 100%     | inline footnote numerals in text |
| CW 9i  | 715 / 718 | 99.6%    | ¶119, ¶141, ¶156 missing (markers lost near illustration pages); flat TOC → `essay` sometimes holds a section heading |

Next corpus targets (in order of app value): Dream Analysis seminar (1928–30),
von Franz *Dreams*, CW 12 Part II (dream series case study — 400 dreams of
Wolfgang Pauli), CW 16 ("The Practical Use of Dream-Analysis").

Indexing: port the vault's pipeline (`scripts/bm25-index.py` + `rerank.py` +
`contextual-prefix.py`). The chunk `header` **is** the contextual prefix —
prepend it to the chunk text before embedding/BM25.

**Copyright:** derived corpus data lives in `individuation-app/data/`
(gitignored — this repo is public). A commercial app must paraphrase-with-
citation or license; quoting verbatim at scale is exposure. Decide before
launch, not after.

---

## 2. The encoded method (analysis session state machine)

Jung's technique, as a pipeline. Each stage gates the next; the app never
skips ahead to interpretation. Primary sources: CW 8 ¶¶443–569 (both dream
essays), CW 16 ¶¶294–352.

### Stage 0 — CAPTURE
- Dream text verbatim (user's words, no cleanup).
- Date, and the **conscious situation**: what is going on in the dreamer's
  life, what attitude dominates. Jung: the dream cannot be interpreted
  without knowledge of the conscious situation (CW 8 ¶477).
- Affect on waking (single strongest feeling + intensity).
- **Provenance** (enum, required): `dream` | `fragment` | `imagination` |
  `test` | `imported`. The series (§3) is the moat, and a series is only as
  trustworthy as its entries — a test or fabricated capture silently
  corrupts every motif thread built over it. All series features filter to
  `dream`/`fragment`/`imported` by default; `test`/`imagination` never enter
  recurrence or drift counts. One field at capture; retrofitting a mixed
  series later means re-auditing every entry by hand. (Origin: a pipeline
  test dream landed in the vault dream log and was synthesized across before
  anyone noticed.)

### Stage 1 — DECOMPOSE (structural read, no meaning yet)
Parse the dream into Jung's dramatic structure (CW 8 ¶¶561–564):
1. **Exposition** — locale, dramatis personae, initial situation
2. **Peripeteia** — development, complication
3. **Lysis** — culmination and result (or its absence — a dream without
   lysis is itself diagnostic)

Extract the symbol list: figures, animals, objects, settings, actions.
Model does this; user confirms/edits the list.

### Stage 2 — ASSOCIATE (before any retrieval)
For each symbol, ask the user for **personal associations** — what does this
specific image mean to *you*, what does it remind you of. Rule: stick to the
image (circumambulation), not Freudian free-association chains that walk away
from it. A snake in *your* dream is first *your* snake.

Why this gates retrieval: the associations become part of the retrieval
query. Retrieving before associating produces generic dictionary-of-symbols
output — the horoscope failure mode.

### Stage 3 — AMPLIFY (retrieval)
Per symbol, build the query: `{symbol} + {user's associations} + {dream
affect} + {dramatic role}`. Plus one whole-dream query from the capture text.

Two-stage retrieval:
1. **Concept graph first** — map symbol → wiki concept neighborhood
   (Shadow, Mother Archetype, Mandala Symbolism…) using the vault's curated
   pages as router.
2. **Chunk search within/boosted-by the neighborhood** — BM25 + embedding +
   rerank over the CW chunks.

Present results as **parallels**, not decodings: "Jung amplifies the serpent
this way in CW 9i ¶282…" Each parallel cited via `header`, quoted passage
shown, one-line relevance note.

### Stage 4 — COMPENSATE (hypothesis, not verdict)
The synthesis question: **what one-sided conscious attitude might this dream
be balancing?** (CW 8 ¶¶483–492). Requires the Stage-0 conscious situation.

Output rules:
- Framed as hypothesis + a question back to the dreamer, never "this dream
  means X." The only validation criterion Jung accepted is the dreamer's own
  response — does it click, does it change something (CW 16 ¶320: the
  interpretation is valid if it "wins the assent of the dreamer").
- Prospective function ≠ prophecy (CW 8 ¶¶491–493). No fortune-telling; the
  dream sketches a possible line of development, nothing more.
- If the material is thin (no associations given, fragment dream), say so
  and stop — a shallow honest answer beats a deep-sounding fabricated one.

Interpretive judgment rules (decisions, not parallel sections):
- **Objective vs. subjective level is a choice.** Figures the dreamer has a
  live, real relation to get the objective reading first; distant or
  impossible figures get the subjective one (CW 8 ¶¶508–510). The extract
  stage's `personal | archetypal | ambiguous` tag drives this — do not emit
  both levels for every figure by default.
- **Little dreams don't get big-dream treatment.** A fragmentary anxiety
  dream about a deadline doesn't warrant archetypal amplification; forcing
  it produces inflated readings. Gate amplification depth on salience and
  kind from Stage 1. "This is a little dream; here's the compensation,
  done" is a *more* Jungian output.
- **Absent lysis is diagnostic.** `lysis_present` isn't just stored — a
  dream that can't resolve says something about where the dreamer is stuck,
  and the compensation hypothesis should use it.
- **Do not confirm the dreamer's self-narrative — that inverts
  compensation.** The dream's job is to show the conscious standpoint what
  it is *not* seeing (CW 8 ¶¶483–492). So a reading that lands the dreamer
  back on the story they already tell about themselves is suspect *by
  construction* — it is the horoscope failure mode wearing Jungian clothes,
  and it is the specific way this app will fail, because the pipeline is fed
  the conscious situation (Stage 0) and, in an assistant context, an
  explicit user profile. Two hard rules:
  1. **No profile grounding.** The synthesizer must not cite the user's
     stated self-description (goals, self-diagnosed weaknesses, the loaded
     profile) as evidence for a compensation hypothesis. The conscious
     situation is the attitude the dream compensates, not the key it
     decodes to.
  2. **Mandatory counter-reading.** When the obvious compensation aligns
     with the dreamer's existing self-story, emit a second hypothesis that
     contradicts it (or reads off that axis entirely), marked as such. The
     dreamer-response field (below) adjudicates between the two — that is
     the correct Jungian arbiter (CW 16 ¶320), not the model's confidence.
  Series-level tripwire: if N consecutive sessions produce compensation
  hypotheses that all reduce to the same conscious complaint, that is a
  signal the *interpreter* is stuck, not the dreamer. Flag it in the series
  digest (§3).

### Stage 5 — FILE
Persist the session (schema below), update the symbol occurrence index,
surface series echoes ("this is the 4th water dream since March").

**Dreamer response is mandatory capture, not an optional field.** Jung's
only validation criterion is whether the interpretation wins the dreamer's
assent and changes something (CW 16 ¶320). After Stage 4, ask: did this
click — yes / partly / no — plus one free-text line. This single field is
three things at once: the method's validation step, the labeled data the
Phase-0 quality gate needs (rubric scoring alone with n=5 is not an eval
set), and the input to the compensation ledger (§3).

---

## 3. Dream series (the moat)

Jung: "every interpretation is a hypothesis" — but "a relative degree of
certainty is reached only in the interpretation of a series of dreams"
(CW 8 ¶533, CW 16 ¶322). Single-dream analysis is the commodity; the series
is the product.

### Storage (v0: SQLite)

```
dreams        id, date, text, conscious_situation, affect, lysis_present,
              provenance   -- dream|fragment|imagination|test|imported
symbols       id, lemma, canonical_id        -- canonical groups variants
occurrences   dream_id, symbol_id, dramatic_role, associations, affect
sessions      id, dream_id, stage_reached, amplifications(json),
              compensation_hypothesis, counter_hypothesis, dreamer_response
citations     session_id, volume, para_start, para_end, header
```

Every series query filters `WHERE provenance IN ('dream','fragment',
'imported')` — `test`/`imagination` rows persist but never contribute to
recurrence, drift, or lysis-rate stats. `counter_hypothesis` stores the
mandatory counter-reading (Stage 4) so the compensation ledger tracks
*both* hypotheses against later dreams, not just the flattering one.

### Symbol canonicalization
snake/serpent/viper must count as one motif. v0: lemma + small synonym map;
v1: embed symbol lemmas, cluster by cosine threshold. User can merge/split
clusters (their taxonomy outranks the model's).

### Series features
1. **Recurrence surfacing** — at Stage 3, inject the symbol's own history
   into amplification: last N occurrences with dates, roles, affects. The
   corpus parallel *and* the personal series parallel, side by side.
2. **Motif drift** — for each recurring symbol, a timeline of dramatic role
   and affect ("the pursuer in January, a companion by June"). Drift in a
   motif is the individuation signal Jung tracked across the Pauli series
   (CW 12 Part II — ingest this volume next for exactly this reason).
3. **Compensation ledger** — hypotheses are stored with the dreamer's
   response. Later dreams confirm or refute earlier hypotheses; the app
   revisits them ("three weeks ago the hypothesis was X; last night's dream
   suggests it held / didn't").
4. **Series digest** — periodic (monthly) review: active motifs, drifts,
   open hypotheses, lysis rate. This is the retention feature. Also runs the
   interpreter tripwire (Stage 4): if recent compensation hypotheses keep
   collapsing to one conscious complaint, surface it as "the reading may be
   stuck" rather than presenting it as a deepening insight.

### Privacy
Dreams + conscious situation are maximally sensitive personal data. Local-
first storage; nothing leaves the device except the LLM call, and the user
is told exactly what is sent. Never train on it, never log it server-side
in a multi-user version without explicit consent.

**Clinical severity.** Both required before any volunteer dream enters the
pipeline: (1) the written privacy page the PRD already calls for; (2) a
hard rule for trauma and suicidal imagery — the app declines to interpret
and says "this belongs with a human." "A question, not a verdict" is not
sufficient cover there.

---

## MVP cut (v0.1 priority order)

1. ~~Corpus extraction CW 8 + 9i~~ ✅
2. **Interactive Stage 0 + Stage 2** — retrofit the dream-app CLI to pause
   and collect conscious situation and per-symbol associations before any
   retrieval. Highest-leverage change in the whole plan; ~a day of work.
3. **Dreamer-response field** after Stage 4 (yes / partly / no + one line).
   Cheap, compounds forever. Bundle two more near-free capture fields here:
   the **provenance enum** (Stage 0) and the **counter-hypothesis** slot
   (Stage 4) — both are one column each and both are expensive to retrofit
   once a series has accumulated.
4. **The merge (§0)** — port the dream-app pipeline onto this corpus; index
   chunks (bm25 + rerank from vault scripts); wiki concept graph as router,
   CW chunks as citations. Bake the two v0.2 rules into the synthesize
   prompt during the port, not after: no profile grounding, and emit the
   counter-reading when the compensation flatters the dreamer's self-story.
5. Series features once ≥ ~10 dreams are on file — recurrence echo, motif
   drift, compensation ledger. Single-dream interpretation is the commodity
   (CW 8 ¶533); don't let Phase 1 wait for a perfect Phase 0.
6. Only then: app shell (mobile/web), auth, billing.

Corpus discipline: no ingestion beyond the planned targets (Dream Analysis
seminar, CW 12 Part II for series mechanics, CW 16). CW 8 + 9i plus the
wiki already cover most retrieval queries; the thin-coverage flag says
what's actually missing. Reading past that is study drift.

The app shell is commodity work; stages 0–5 over a cited corpus with series
memory is the product. Build it as a pipeline first, wrap it later.

Steps 2 + 3 + 4 turn the pipeline from a dream-explainer into an analysis
instrument, and they're all pre-Phase-2 work — directly on the path to the
paying-user gate.
