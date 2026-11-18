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
dreamapp series "silver chain"             # every dream holding an image, oldest first
```

Flags (both commands): `--dry`, `--show-sources`, `--force`, `--title`, `--date YYYY-MM-DD`, `--no-series`.

`log` runs Stages 0 and 2 of `individuation-app/docs/design.md` before any model reads the dream for meaning. It asks for:
1. your conscious situation
2. your strongest feeling on waking
3. what the entry is (`dream`, `fragment`, `imagination`, `test` or `imported`)
4. after symbol extraction, a check of the image list: Enter keeps it, `d 2 4` drops images, `+ silver chain` adds one the model missed
5. one association per image, most salient first (up to 7; blank skips one, `q` stops)

Your associations are added to each image's retrieval query. The interpretation prompt is told to build each personal reading from your association, and to say so when none was given. The answers are written into the note's Conscious Situation, Waking Associations and Feeling-Tone sections: a template prompt is replaced, an answer goes under text already there, a missing section is created, and an image already in Waking Associations isn't repeated. `provenance` goes into the frontmatter; the default `dream` never overwrites a note already marked otherwise (e.g. `imported`). `log` reads the dream from a file, because stdin carries your answers.

Once the note is written, `log` shows the compensation, a mandatory competing reading and the question, then asks for your verdict: `clicks`, `partial` or `miss` (`yes` / `partly` / `no` also work, `later` defers), plus one line. The verdict goes into `response:` and sets `status: responded`. The line goes into `## Dreamer Response`, replacing the template prompt or added after what you already wrote there. Nothing you wrote under Dreamer Response or Waking Action is overwritten, including by `--force`. If a run fails after the questions, your answers are printed to stderr. To rate a note later:

```
dreamapp respond wiki/dreams/2026-10-01-dad-stepmom-walkout.md --verdict clicks --note "the doorway part is it"
```

**Evidence.** Each run searches the primary-text chunks in `individuation-app/data/` (gitignored): CW 8, 9i and 12 Part II by paragraph (`extract_cw.py`), CW 16 by paragraph from its scan (`extract_cw_scan.py`), and two page-anchored sources: the Dream Analysis seminar (`extract_seminar.py`, cited as `Dream Analysis — Lecture II, 14 November 1928 — pp. 16-17`) and von Franz's *Dreams* (`extract_vonfranz.py`). It runs one query per salient image, with your association appended, plus one query for the whole dream. Those passages are the citable evidence, listed in Sources by header (`CW 9i — 1. On The Concept of the Archetype — para. 155`). Vault pages are orientation only, and your own `wiki/dreams/` entries are never retrieved as corpus. Without the data folder, runs continue with no CW passages and say so on stderr.

Passages are taken round-robin across the queries (each query's best, then each query's second, ...), so the long whole-dream query can't take every slot from the short image queries. Every run also gets the method canon (`config.METHOD_CANON`): six paragraphs on which level to read a figure on, compensation, the series and the dreamer's assent (CW 8 ¶¶509, 515, 545, 550; CW 16 ¶¶316, 322), marked `role="method"` for the model. No image query retrieves them, though they are what past analyses cite most. When `log` runs on an existing note, only its `## The Dream` section is read as the dream.

**Series.** Each run also looks up your earlier dreams that share this one's images (`series.py`, design.md §3). Later dreams correct the readings of earlier ones (CW 16 ¶322), so each earlier dream goes to the model with the sentences that hold the image, the compensation it was given then, and your verdict on it. The model writes a Series Context, which leads the analysis, and lists the earlier dreams it drew on in Sources; those become `related` links. An image matches an earlier dream three ways, closest first:
1. a `symbols:` or `figures:` tag that is the image (`silver chain` = `silver-chain`, `my father` = `father`; singular and plural meet: bus/buses, city/cities)
2. every word of the image in that dream's tags or its own text
3. a phrase listed for one of that dream's motifs in `wiki/dreams/motifs.md`

Extraction also tags each image from your motif vocabulary. Those tags find the most recent dreams with the same motif, and a new note records them in `motifs:`. A re-analysis fills `motifs:` only on a note that has none. At most 3 dreams per image and 12 in all are sent, closest first (`config.MAX_SERIES_*`); the model sees them oldest first, with a count for every image that matched, including one left no room. Only dreams up to the night's own date are sent. A re-analysed note is dated by its frontmatter even when `--date` is given, and never sees itself. Entries marked `test` or `imagination` never join the series.

What leaves the machine: for each earlier dream, the matching sentences, the compensation it was given, and your Dreamer Response text. stderr names the dates before the model call. The motif vocabulary goes to extraction too, Covers column included, and that column names real places (e.g. Ramsey, NJ). `--no-series` sends neither.

`dreamapp series IMAGE` prints the same lookup over the whole series, oldest first: each dream's date, title, agency, verdict, the sentences holding the image and the first line of its feeling-tone. That's how a motif's role and affect move over time. No API call.

**Series benchmark.** `python dream-app/scripts/bench_series.py` checks the lookup against the 28 analyses whose Series Context names earlier dreams (99 dream-dates). It prints aggregates only. On 2026-11-05 it found 31% with tags alone, 42% adding word and motif-phrase matches, and 59% with motif tags and the 12-dream budget. Sending the 12 most recent dreams instead finds 34%. Two caveats. The motif tags in that run are the analyses' own, so 59% is an upper bound until an API run measures extraction's tagging. The same analyses assigned the tags, which flatters tag matching.

Vault-page ranking uses the reranker's cosine score when the `nomic-embed-text` model is available through Ollama, and the BM25 score otherwise (one basis per run). Your own `wiki/dreams/` pages are over-fetched past, so they never use up the slots.

**Retrieval benchmark.** `python dream-app/scripts/bench_retrieval.py [--queries FILE]` checks whether search finds the CW paragraphs your past analyses cited (25 dreams, 36 citations). It prints aggregates only. `--queries` takes extract-stage output per dream; without it, frontmatter symbols stand in, which lack the extract stage's step into Jung's vocabulary. On 2026-11-02, with extract-style queries written in session to the extract prompt (an API run will replace them): before these changes, 1 of 36 cited paragraphs reached synthesis; after, 19 of 36. The canon covers 15 of those and was chosen from this same gold set, so they are in-sample; round-robin took image-specific hits from 1 to 4 of 21. With raw frontmatter symbols, retrieval alone finds none, which is the vocabulary gap the extract stage bridges. The gold set also leans lexical (those analyses were written with keyword search over the same chunks), so read the numbers as a comparison between strategies, not an absolute score.

## Periodic reviews (counted half)

```
dreamapp review --month 2026-10
dreamapp review --quarter 2026-Q3 --json stats.json
dreamapp review --year 2026 --today 2026-11-01
```

Prints every countable part of a monthly, quarterly or yearly review as markdown: numbers, agency series, cast, firsts, motif deltas, stance, elements, hit rate, waking-action ledger, association debt, and the interpreter tripwire. It reads frontmatter and a few sections, and makes no API calls. Entries marked `test` or `imagination` are left out of every count, and the count of them is shown. A note whose frontmatter won't parse is named on stderr and skipped. The `/dream` skill's Phase 5 writes the interpretive half on top of this output. Design: `docs/superpowers/specs/2026-11-01-dream-periodic-reviews-design.md`.

The tripwire is the counted half of the review's M23 check. It lists the content words in at least half of the period's Compensation sections, and of its Waking Actions, with method vocabulary left out. A word must appear in 3 at minimum, so with 3 or 4 readings that means 3. It also lists each reading's opening line in order. A word most readings land on may be the interpreter's complaint rather than the dream's. On the 2026 series it flags "work" in 14 of July's 25 readings, and "work" (6/9) and "app" (5/9) in August. October is clean.

Every note write (new note, re-analysis, verdict) goes to a temp file beside the note and is swapped in, so a failed write leaves the note as it was.
