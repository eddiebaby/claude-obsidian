# dreamapp
Jungian dream interpretation: extract symbols, retrieve corpus, synthesize, write to `wiki/dreams/`.

## Install

```
pip install -e dream-app
bash bin/setup-retrieve.sh                 # once, from vault root
cp dream-app/.env.example dream-app/.env   # fill in ANTHROPIC_API_KEY
```

## Usage

```
dreamapp log path/to/dream.txt             # asks first, then interprets (recommended)
dreamapp interpret path/to/dream.txt       # one-shot, no questions
dreamapp interpret - < dream.txt           # stdin
dreamapp interpret wiki/dreams/....md --force
```

Flags (both commands): `--dry`, `--show-sources`, `--force`, `--title`, `--date YYYY-MM-DD`.

`log` runs Stages 0 and 2 of `individuation-app/docs/design.md` before any model reads the dream for meaning. It asks for:
1. your conscious situation
2. your strongest feeling on waking
3. what the entry is (`dream`, `fragment`, `imagination`, `test` or `imported`)
4. after symbol extraction, one association per image, most salient first (up to 7; blank skips one, `q` stops)

Your associations are added to each image's retrieval query. The interpretation prompt is told to build each personal reading from your association, and to say so when none was given. The answers are written into the note's Conscious Situation, Waking Associations and Feeling-Tone sections, and `provenance` goes into its frontmatter. `log` reads the dream from a file, because stdin carries your answers.

Once the note is written, `log` shows the compensation, a mandatory competing reading and the question, then asks for your verdict: `clicks`, `partial` or `miss` (`yes` / `partly` / `no` also work, `later` defers), plus one line. The verdict goes into `response:` and sets `status: responded`. The line goes into `## Dreamer Response`, replacing the template prompt or added after what you already wrote there. Nothing you wrote under Dreamer Response or Waking Action is overwritten, including by `--force`. If a run fails after the questions, your answers are printed to stderr. To rate a note later:

```
dreamapp respond wiki/dreams/2026-10-01-dad-stepmom-walkout.md --verdict clicks --note "the doorway part is it"
```

**Evidence.** Each run searches the paragraph-anchored Collected Works chunks in `individuation-app/data/` (CW 8 and CW 9i, built by `extract_cw.py`; gitignored). It runs one query per salient image, with your association appended, plus one query for the whole dream. Those passages are the citable evidence, listed in Sources by header (`CW 9i — 1. On The Concept of the Archetype — para. 155`). Vault pages are orientation only, and your own `wiki/dreams/` entries are never retrieved as corpus. Without the data folder, runs continue with no CW passages and say so on stderr.

Vault-page ranking uses the reranker's cosine score when the `nomic-embed-text` model is available through Ollama, and the BM25 score otherwise.

## Periodic reviews (counted half)

```
dreamapp review --month 2026-10
dreamapp review --quarter 2026-Q3 --json stats.json
dreamapp review --year 2026 --today 2026-11-01
```

Prints every countable part of a monthly, quarterly or yearly review as markdown: numbers, agency series, cast, firsts, motif deltas, stance, elements, hit rate, waking-action ledger, association debt. It reads frontmatter only and makes no API calls. The `/dream` skill's Phase 5 writes the interpretive half on top of this output. Design: `docs/superpowers/specs/2026-11-01-dream-periodic-reviews-design.md`.
