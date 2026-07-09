# Individuation App

Jungian dream-analysis app. Working prototype layer lives here until it
graduates to its own repo.

- [docs/design.md](docs/design.md) — the three depth pillars: paragraph-anchored
  citations, the encoded method (6-stage session), dream-series tracking
- [extraction/extract_cw.py](extraction/extract_cw.py) — CW PDF → ¶-numbered
  JSONL (paragraphs + retrieval chunks)
- `data/` — **gitignored**: derived from copyrighted Bollingen editions;
  regenerate with the extractor

Extracted so far: CW 8 (997/997 ¶¶), CW 9i (715/718 ¶¶).

```
python extraction/extract_cw.py <pdf> --volume "CW 8"
```
