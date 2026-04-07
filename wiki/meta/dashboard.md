---
type: meta
title: "Dashboard"
updated: 2026-04-07
tags:
  - meta
  - dashboard
status: evergreen
related:
  - "[[index]]"
  - "[[overview]]"
  - "[[log]]"
  - "[[concepts/_index]]"
  - "[[Compounding Knowledge]]"
---

# Wiki Dashboard

Navigation: [[index]] | [[overview]] | [[log]] | [[hot]]

Requires the **Dataview** plugin: Settings > Community Plugins > Browse > "Dataview".

---

## Recent Activity

```dataview
TABLE type, status, updated FROM "wiki" SORT updated DESC LIMIT 15
```

---

## Seed Pages (Need Development)

```dataview
LIST FROM "wiki" WHERE status = "seed" SORT updated ASC
```

---

## Entities Missing Sources

```dataview
LIST FROM "wiki/entities" WHERE !sources OR length(sources) = 0
```

---

## Open Questions

```dataview
LIST FROM "wiki/questions" WHERE answer_quality = "draft" SORT created DESC
```

---

## Sources by Confidence

```dataview
TABLE author, date_published, confidence FROM "wiki/sources" SORT confidence ASC
```
