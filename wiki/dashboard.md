---
type: meta
title: "Dashboard"
updated: 2026-06-27
tags:
  - meta
  - dashboard
status: evergreen
related:
  - "[[index]]"
  - "[[log]]"
  - "[[hot]]"
---

# Dashboard

Navigation: [[index]] | [[log]] | [[hot]] | [[overview]]

---

## Domain Balance

> [!warning] Money Focus Check
> If Depth Psychology has more pages than Quantitative Finance + Business combined, you are studying instead of building. Call it.

```dataviewjs
const domains = [
  { name: "Depth Psychology", tag: "depth-psychology" },
  { name: "Quantitative Finance", tag: "quantitative-finance" },
  { name: "AI / ML", tag: "machine-learning" },
  { name: "Business", tag: "business" },
]

const rows = domains.map(d => {
  const n = dv.pages('"wiki"')
    .where(p => p.file.tags && p.file.tags.includes(d.tag) && p.type !== "meta")
    .length
  return [d.name, n]
})

const total = rows.reduce((s, [, n]) => s + n, 0)
const withPct = rows.map(([name, n]) => [name, n, total > 0 ? Math.round(n / total * 100) + "%" : "—"])

dv.table(["Domain", "Pages", "% of Wiki"], withPct)
```

---

## Income-Generating Content

### Trading & Markets

```dataview
TABLE title as "Page", status, updated as "Updated"
FROM "wiki" AND #quantitative-finance
WHERE type != "meta" AND type != "domain"
SORT updated DESC
```

### Business / Consulting

```dataview
TABLE title as "Page", status, updated as "Updated"
FROM "wiki" AND #business
WHERE type != "meta" AND type != "domain"
SORT updated DESC
```

---

## Recent Activity

```dataview
TABLE title as "Page", type, status, updated as "Updated"
FROM "wiki"
WHERE type != "meta"
SORT updated DESC
LIMIT 15
```

---

## Pages Needing Work

```dataview
TABLE title as "Page", type, updated as "Last Touched"
FROM "wiki"
WHERE status = "seed" OR status = "developing"
AND type != "meta"
SORT updated ASC
LIMIT 20
```

---

## Sources Ingested

```dataview
TABLE title as "Source", date_published as "Published", author, confidence
FROM "wiki/sources"
SORT file.ctime DESC
```
