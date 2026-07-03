---
name: dreams-index
type: index
title: "Dream Journal"
created: 2026-06-25
updated: 2026-06-25
tags:
  - dream
  - index
status: evergreen
related:
  - "[[Dream-Analysis-and-Interpretation]]"
  - "[[Individuation]]"
  - "[[index]]"
---

# Dream Journal

Personal dream record + Jungian analysis, drawing on the [[Dream-Analysis-and-Interpretation|amplification method]] and the vault's concept base ([[Shadow]], [[Anima and Animus]], [[Self (archetype)]], [[Mother Archetype]], [[Hero_Archetype]], [[Trickster]], [[Individuation]]).

## How to log a dream

1. **Capture raw, fast, on waking.** New note in `wiki/dreams/`, name it `YYYY-MM-DD-keyword`. Use the `dream` template. Fill *The Dream*, *Associations*, *Feeling-Tone*, *Day Residue*. Leave the Jungian Analysis section empty.
2. **Tell Claude:** `analyze my dream` (or `analyze wiki/dreams/2026-06-25-snake.md`). Claude reads the entry, amplifies symbols against the ingested Jung sources, fills the analysis section, sets `archetypes`/`symbols`/`related`, flips `status` to `analyzed`.
3. Over time, patterns surface — recurring figures, symbol drift, individuation movement.

You don't have to use the template by hand — you can also just paste a dream into chat and say `log this dream`, and Claude will create the entry for you.

## All Dreams

```dataview
TABLE date, status, archetypes, symbols
FROM "wiki/dreams"
WHERE type = "dream"
SORT date DESC
```

## Recurring Symbols

```dataview
TABLE rows.file.link AS dreams
FROM "wiki/dreams"
WHERE type = "dream"
FLATTEN symbols AS symbol
GROUP BY symbol
SORT length(rows) DESC
```

## Archetypes Appearing

```dataview
TABLE rows.file.link AS dreams
FROM "wiki/dreams"
WHERE type = "dream"
FLATTEN archetypes AS archetype
GROUP BY archetype
SORT length(rows) DESC
```
