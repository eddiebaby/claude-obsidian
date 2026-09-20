---
name: dreams-index
type: index
title: "Dream Journal"
created: 2026-06-25
updated: 2026-09-18
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

**Series synthesis:** [[dream-threads]] — recurring motifs across all entries (the unfinished structure, the gun's trajectory, water states, anima development, agency arc). Updated 2026-09-15 with the **second arc** (2026-07-14 → 09-12): 27 entries backlog-ingested from the Claude app Dreams project.

**Longitudinal study:** [[longitudinal-study]] — the whole series as one process (2026-06-25 → 09-12): five phases, per-dream SDA agency scoring, seven developmental lines, findings and assignments. Prototype of the individuation-app timeline feature. Extend per ~10 new dreams.

**Personal context:** [[dreamer-context]] (biography and recurring figures, read before every analysis). **Motifs:** [[motifs]] (controlled vocabulary, frequency, motif × agency). **Phone capture:** [[inbox]].

**Backlog worksheet:** [[backlog-associations]] — retroactive association questions for all past dreams. Answer, then say `re-analyze the backlog`.

## How to log a dream

Workflow is enforced by the project skill `.claude/skills/dream/SKILL.md`.

1. **Capture fast on waking.** Paste the dream into chat with `log this dream` (or fill the `dream` template by hand in `wiki/dreams/YYYY-MM-DD-keyword`). Include a line on your **conscious situation**: what's live right now.
2. **Answer the association questions.** Claude asks one short question per key image before interpreting. Say `skip, just analyze` to bypass; the analysis gets flagged as low-confidence.
3. **Analysis.** Claude reads the series first, then writes Series Context → cited amplification (CW ¶ / vault pages) → compensation against your conscious situation → agency score (1–5). It also updates [[dream-threads]] and the agency table in [[longitudinal-study]].
4. **Give your verdict:** `clicks`, `partial`, or `miss`, plus why. That gets recorded in *Dreamer Response*, and partial/miss readings get revised.

Status flow: `unanalyzed` → `associated` → `analyzed` → `responded`.

## All Dreams

```dataview
TABLE date, status, agency, response, motifs
FROM "wiki/dreams"
WHERE type = "dream"
SORT date DESC
```

## Awaiting Your Response

```dataview
LIST
FROM "wiki/dreams"
WHERE type = "dream" AND status = "analyzed" AND !response
SORT date DESC
```

## Agency Over Time

```dataview
TABLE WITHOUT ID date, file.link AS dream, agency
FROM "wiki/dreams"
WHERE type = "dream" AND agency
SORT date ASC
```

## Interpretation Hit Rate

```dataview
TABLE WITHOUT ID response, length(rows) AS count
FROM "wiki/dreams"
WHERE type = "dream" AND response
GROUP BY response
```

## Recurring Motifs

```dataview
TABLE WITHOUT ID motif, length(rows) AS n, rows.file.link AS dreams
FROM "wiki/dreams"
WHERE type = "dream"
FLATTEN motifs AS motif
GROUP BY motif
SORT length(rows) DESC
```

## Recurring Figures

```dataview
TABLE WITHOUT ID figure, length(rows) AS n, rows.file.link AS dreams
FROM "wiki/dreams"
WHERE type = "dream"
FLATTEN figures AS figure
GROUP BY figure
SORT length(rows) DESC
```

## Open Waking Actions

```dataview
LIST
FROM "wiki/dreams"
WHERE type = "dream" AND status != "unanalyzed" AND !action_done AND date >= date(2026-09-18)
SORT date DESC
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
