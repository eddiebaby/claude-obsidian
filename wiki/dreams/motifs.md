---
name: motifs
type: reference
title: "Dream Motifs & Figures — Controlled Vocabulary"
domain: depth-psychology
created: 2026-09-18
updated: 2026-09-18
tags:
  - dream
  - reference
status: developing
related:
  - "[[_index|Dream Journal]]"
  - "[[dreamer-context]]"
  - "[[dream-threads]]"
---

# Motifs & Figures

`symbols:` stays free-form (the specific images). `motifs:` and `figures:` are **controlled vocabularies**, so recurrence actually shows up in queries. Use only tags from the lists below. To add a new tag, append it here first with a one-line definition.

## Motif vocabulary

| Motif | Covers |
|---|---|
| `water` | ocean, river, lake, flood, pool, puddle, standing water |
| `snow-ice` | snow, ice, frozen things |
| `mountain` | mountains, summits, canyons seen from above |
| `underground` | basements, caverns, crawlspaces, holes, depths below a building |
| `house` | dwellings: homes, rentals, apartments, the unfinished house |
| `architecture` | grand or public buildings noticed *as* buildings |
| `construction` | building, road crews, repair, schematics, materials |
| `hotel` | hotels, hostels, Airbnbs |
| `bar` | bars, nightclubs, drinking venues |
| `classroom` | school, teacher, class |
| `workplace-photo` | photo industry, Milk Studios, studios |
| `job` | job offers, hiring, firing, work demands (outside photo) |
| `authority` | bosses, presidents, mentors, institutional power |
| `police-law` | cops, courts, arrest risk, lawyers |
| `gun` | firearms, shooting, bullet holes |
| `substances` | alcohol, drugs, cigarettes |
| `money-wealth` | money, property value, the rich, losses |
| `food` | eating, cooking, buying food |
| `sex` | erotic contact, sexual charge, exposure |
| `anima` | unknown or numinous feminine figure |
| `ex` | any ex-partner |
| `family` | family of origin, siblings, family gatherings |
| `car` | cars, driving, stalling, vehicles as setting |
| `travel` | trips, trains, planes, abroad |
| `chase` | pursuit, threat, flight |
| `leaving` | exits, expulsions, walking out, being kicked out |
| `animal` | animals, including the cat and the dog-creature |
| `plant-tree` | trees, roots, gardens, cuttings, mulch |
| `self` | explicit Self symbols: mandala, circle, world-tree |
| `burning-man` | Burning Man |
| `new-york` | NYC as setting |
| `hometown` | Ramsey, NJ, and the childhood home |

## Figures

Kebab-case person names, reused exactly across entries — a convention, not a closed list. The recurring ones with associations live in [[dreamer-context]]; a figure used in only one or two dreams (e.g. `kalei`, `gangster`, `keith-rukowski`) doesn't need a row there until it recurs. Before inventing a name, grep existing `figures:` lines so spellings match. Unknown figures: `unknown-woman`, `unknown-man`, `old-man`.

## Motif frequency

```dataview
TABLE WITHOUT ID motif, length(rows) AS dreams, rows.file.link AS entries
FROM "wiki/dreams"
WHERE type = "dream"
FLATTEN motifs AS motif
GROUP BY motif
SORT length(rows) DESC
```

## Figure frequency

```dataview
TABLE WITHOUT ID figure, length(rows) AS dreams, rows.file.link AS entries
FROM "wiki/dreams"
WHERE type = "dream"
FLATTEN figures AS figure
GROUP BY figure
SORT length(rows) DESC
```

## Motif × agency

Average agency score for dreams containing each motif. This shows where the dream-ego gets stuck and where it acts.

```dataview
TABLE WITHOUT ID motif, length(rows) AS n, round(sum(rows.agency) / length(rows), 1) AS "avg agency"
FROM "wiki/dreams"
WHERE type = "dream" AND agency
FLATTEN motifs AS motif
GROUP BY motif
SORT round(sum(rows.agency) / length(rows), 1) ASC
```
