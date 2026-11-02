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
dreamapp interpret path/to/dream.txt
dreamapp interpret - < dream.txt           # stdin
dreamapp interpret wiki/dreams/....md --force
```

Flags: `--dry`, `--show-sources`, `--force`, `--title`, `--date YYYY-MM-DD`.

## Periodic reviews (counted half)

```
dreamapp review --month 2026-10
dreamapp review --quarter 2026-Q3 --json stats.json
dreamapp review --year 2026 --today 2026-11-01
```

Prints every countable part of a monthly, quarterly or yearly review as markdown: numbers, agency series, cast, firsts, motif deltas, stance, elements, hit rate, waking-action ledger, association debt. It reads frontmatter only and makes no API calls. The `/dream` skill's Phase 5 writes the interpretive half on top of this output. Design: `docs/superpowers/specs/2026-11-01-dream-periodic-reviews-design.md`.
