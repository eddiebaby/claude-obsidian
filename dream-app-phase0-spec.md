---
name: dream-app-phase0-spec
type: spec
title: "Jungian Dream App — Phase 0 Prototype Spec"
domain: business
created: 2026-06-29
updated: 2026-06-29
status: draft
tags:
  - project
  - dream-app
  - phase-0
---

# Jungian Dream App — Phase 0 Prototype Spec

## The one question this phase answers

**Does the interpretation come out good enough that a serious Jung reader would pay for it?**

Nothing else matters yet. No auth, no payments, no cloud, no mobile. If the engine produces non-obvious, genuinely Jungian interpretations grounded in the vault corpus, the rest is commodity plumbing. If it produces horoscope-generic output, we found that out in a weekend instead of a quarter.

Phase 0 is a **local Python CLI** that takes a dream and returns a structured Jungian interpretation grounded in the existing Obsidian vault. Stack chosen: **Claude API** for the LLM calls, **the Obsidian vault itself** as the corpus (via the existing `scripts/retrieve.py`).

---

## Scope

**In scope**
- Read a dream (paste into terminal, or point at a file).
- Extract salient symbols, tag each personal vs. archetypal.
- Retrieve relevant passages from the vault's depth-psychology pages.
- Synthesize a structured interpretation (compensatory function, amplification, personal/objective levels).
- Write the result back as a dream note in the existing vault format, filling `symbols:` and `archetypes:` frontmatter.
- Show which vault pages were used (trust + debugging).

**Out of scope (deferred to Phase 2)**
- Web/mobile UI, auth, payments.
- Per-user databases — the vault is the only corpus and the only store.
- Longitudinal cross-dream tracking *logic* (but we populate the frontmatter fields now so the data exists when we build it).
- Voice capture, image generation, sharing.

---

## Architecture

Single linear pipeline. Four stages, two of them Claude API calls.

```
dream text
   │
   ▼
[1] EXTRACT  ──(Claude call #1)──►  symbols[] with {image, personal_or_archetypal, salience}
   │
   ▼
[2] RETRIEVE ──(scripts/retrieve.py per symbol)──►  vault passages with paths + snippets
   │
   ▼
[3] SYNTHESIZE ──(Claude call #2: dream + symbols + passages)──►  structured interpretation
   │
   ▼
[4] WRITE  ──►  wiki/dreams/<date>-<slug>.md  (uses _templates/dream.md, fills symbols/archetypes)
```

### Stage 1 — Extract
One Claude call. Input: raw dream text. Output: JSON list of symbols. For each symbol: the image as it appeared ("mountain of garbage"), a guess at whether it reads personal or archetypal, and a 1–5 salience score so retrieval focuses on what matters. Keep this call cheap and structured — it's a router, not the interpretation.

### Stage 2 — Retrieve
For each high-salience symbol, call the existing `scripts/retrieve.py "<symbol query>" --top 3`. It already does BM25 over contextualized chunks of the vault, then cosine rerank (via ollama `nomic-embed-text`; no-ops gracefully to BM25 order if ollama isn't running — fine for prototype). It returns JSON with `absolute_path`, `snippet`, and scores. We read the top chunks' source pages and collect them as context. **This is the moat: interpretation grounded in Scott's curated Jung, not the model's vague memory.** Deduplicate pages across symbols.

### Stage 3 — Synthesize
The interpretation call. Input: the dream, the extracted symbols, and the retrieved vault passages. Output structured the Jungian way, not as free prose:

- **Compensatory function** — what waking-life attitude is this dream balancing or correcting? (Jung's central thesis: dreams compensate the conscious position.)
- **Symbol amplification** — for each major symbol, what the vault corpus says, personal association vs. archetypal/collective resonance.
- **Two levels** — objective (people/things as themselves) vs. subjective (every figure as a part of the dreamer).
- **A question, not a verdict** — end with what the dream is asking the dreamer to look at. Avoids the fortune-teller failure mode.
- **Sources** — list the vault pages cited.

The system prompt enforces: stay grounded in supplied passages, flag when the corpus is thin on a symbol rather than confabulating, never moralize, write for someone who already knows the concepts (Scott's stated preference).

### Stage 4 — Write back
Render into the existing `_templates/dream.md` structure. Critically, fill the `symbols:` and `archetypes:` frontmatter arrays — these already exist in your dream notes and are what Phase 1 longitudinal tracking will read. Set `status: analyzed`. Write to `wiki/dreams/<date>-<slug>.md`. Append the interpretation under an `## Interpretation` heading so the raw dream stays immutable above it.

---

## File structure

A self-contained package inside the vault repo so it can read scripts and wiki directly. Lifts cleanly into FastAPI in Phase 2.

```
dream-app/
  pyproject.toml          # deps: anthropic, python-frontmatter, pyyaml
  .env                    # ANTHROPIC_API_KEY (gitignored)
  README.md
  src/dreamapp/
    __init__.py
    config.py             # paths, model name, vault root resolution
    extract.py            # Stage 1 — Claude call, returns Symbol[]
    retrieve.py           # Stage 2 — wraps scripts/retrieve.py, dedupes pages
    synthesize.py         # Stage 3 — Claude call, returns Interpretation
    writeback.py          # Stage 4 — render + write dream note
    pipeline.py           # orchestrates 1→2→3→4
    prompts/
      extract.md          # system prompt for stage 1
      synthesize.md       # system prompt for stage 3
    cli.py                # `dreamapp interpret <file|->`
  tests/
    fixtures/             # 2-3 real dreams from wiki/dreams/
    test_extract.py
    test_pipeline.py      # golden-ish: assert structure + grounding, not exact text
```

---

## Tech stack & dependencies

- **Python 3.11+**, `uv` or `venv`.
- **`anthropic`** — Claude API client.
- **`python-frontmatter`** — read/write vault note YAML cleanly.
- **`pyyaml`**, stdlib `subprocess`/`json` for the retrieve.py bridge.
- Model: start with the current Claude Sonnet for synthesis (quality/cost balance), Haiku for extraction (cheap router). Make the model a config value so it's a one-line swap.
- **No web framework, no database, no vector DB** — retrieve.py + the vault are the retrieval layer.

---

## CLI (the whole UI for Phase 0)

```
dreamapp interpret dream.txt          # interpret a file
pbpaste | dreamapp interpret -        # interpret from stdin
dreamapp interpret dream.txt --dry    # print interpretation, don't write to vault
dreamapp interpret dream.txt --show-sources
```

A Streamlit one-pager is a nice-to-have *after* the CLI proves the engine — not before. Don't build UI around an unvalidated engine.

---

## Validation criteria (the Phase 0 exit bar)

Run the pipeline on **20–30 real dreams** (your existing `wiki/dreams/` notes + a few volunteers'). For each, score honestly:

1. **Non-obvious** — does it say something a careful reader wouldn't get from re-reading the dream? (The killer metric. Generic = fail.)
2. **Grounded** — are the amplifications actually traceable to vault content, not invented?
3. **Jungian, not pop-psych** — compensation, amplification, personal/objective levels actually used.
4. **Honest about gaps** — when the corpus is thin, does it say so instead of confabulating?

Bar to proceed to Phase 2: **a serious Jung reader finds the majority non-obvious and useful.** If not, the fix is corpus + prompts, not product features.

---

## Cost

At prototype volume this is rounding-error money. ~2 Claude calls per dream; extraction is small, synthesis is the bulk. Tens of dreams during validation = well under a few dollars total. Cost is not a Phase 0 constraint; quality is.

---

## Build order

1. Scaffold package + `.env` + config; confirm it resolves the vault root and can shell out to `scripts/retrieve.py`.
2. **Stage 2 first** — wrap retrieve.py, run it on hand-picked symbols ("snake", "water", "father"), eyeball that it returns sane vault pages. (Retrieval quality gates everything; verify it before building around it.)
3. Stage 1 extract + prompt; test on existing dream notes.
4. Stage 3 synthesize + prompt; this is where most iteration happens.
5. Stage 4 writeback into the dream template.
6. Wire `pipeline.py` + `cli.py`.
7. Run the 20–30 dream validation set; tune prompts and corpus.

---

## Risks & mitigations

- **Generic output** (the main risk) → grounding in vault passages + strict synthesis prompt + the "non-obvious" exit bar. If it fails, enrich the corpus, don't add features.
- **Retrieval misses** (thin corpus on a symbol) → prompt instructs the model to flag thin coverage; surfaces gaps to fill in the vault. This is a feature — it tells you what Jung notes to write next.
- **Privacy** — dreams are sensitive. Phase 0 is local + your own API key, so fine. Flag for Phase 2: a real product needs a data-handling stance before it touches other people's dreams. (Note: your vault already has `PRIVACY.md`/`SECURITY.md` — reuse that thinking.)
- **Scope creep into product** → the exit bar is the gate. No FastAPI, no auth, no Streamlit until the engine clears it.

---

## What Phase 0 deliberately sets up for later

- `symbols:`/`archetypes:` frontmatter populated on every analyzed dream → Phase 1 longitudinal symbol tracking reads these directly, no rework.
- Clean stage separation (`extract`/`retrieve`/`synthesize`/`writeback`) → each becomes a FastAPI endpoint or service in Phase 2 with minimal change.
- The retrieve.py bridge → swaps to a hosted vector store in Phase 2 behind the same interface.
