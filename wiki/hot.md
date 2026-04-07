---
type: meta
title: "Hot Cache"
updated: 2026-04-07T12:00:00
tags:
  - meta
  - hot-cache
status: evergreen
related:
  - "[[index]]"
  - "[[log]]"
---

# Recent Context

Navigation: [[index]] | [[log]] | [[overview]]

---

## Last Updated
2026-04-07 — cosmic-brain v1.1.0 initialized. First ingest complete: Nate Herk LLM Wiki transcript.

## Key Recent Facts
- The wiki pattern was originated by [[Andrej Karpathy]] and makes knowledge compound like interest
- [[Hot Cache]] (this file) enables cross-project context at minimal token cost (~500 tokens)
- [[Compounding Knowledge]] is the core insight: unlike RAG, the wiki pre-compiles synthesis
- One user dropped token usage by 95% switching from inline context files to the wiki pattern
- The index file alone is sufficient at hundreds of pages — no vector RAG needed

## Recent Changes
- Created: [[LLM Wiki Pattern]], [[Hot Cache]], [[Compounding Knowledge]], [[Andrej Karpathy]]
- Created: [[Nate Herk LLM Wiki Transcript]] (first source)
- Created: seed vault structure (index, log, overview, dashboard)
- Plugin v1.1.0: added /save and /autoresearch commands

## Active Threads
- Vault is fresh. No user-specific domain scaffolded yet.
- Next step: run /wiki to scaffold for your domain, then start ingesting sources.
