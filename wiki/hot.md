---
type: meta
title: "Hot Cache"
updated: 2026-04-08T19:00:00
tags:
  - meta
  - hot-cache
status: evergreen
related:
  - "[[index]]"
  - "[[log]]"
  - "[[Wiki Map]]"
  - "[[getting-started]]"
  - "[[claude-obsidian-v1.4-release-session]]"
---

# Recent Context

Navigation: [[index]] | [[log]] | [[overview]]

## Last Updated
2026-04-15 (2): Claude SEO v1.9.0 slides + GitHub release complete. Built 15-slide HTML deck (`claude-seo-slides/v190.html`) with scroll-snap, IntersectionObserver, and screenshot fallbacks. Fixed hardcoded `/home/agricidaniel/` path in `release_report.py` (use `Path.home()`). Added `.claude/` and `.superpowers/` to `.gitignore`. Pushed 68 files (9,662 insertions). Tagged v1.9.0, created GitHub release with PDF attached. Session: [[2026-04-15-slides-and-release-session]].

2026-04-15 (1): Claude SEO v1.9.0 Release Report PDF complete. 13 pages, dark theme, 1.53 MB at `~/Desktop/Claude-SEO-v1.9.0-Release-Report.pdf`. Key WeasyPrint fixes: file:// URI spaces need `urllib.parse.quote()`; `display:table-cell` is atomic (no page breaks inside); fixed `height:297mm` causes empty space; logo filename had double space "hub  pro". Pro Hub Challenge v2 live: keyword LEADS, $600 prize pool ($400/$200), deadline April 28. Session: [[2026-04-15-release-report-session]].

## Plugin State
- **Version**: 1.4.1 (installed, enabled, user scope)
- **Install ID**: `claude-obsidian@claude-obsidian-marketplace`
- **Releases**: v1.1, v1.4.0, v1.4.1 on GitHub
- **Skills**: 10 (wiki, wiki-ingest, wiki-query, wiki-lint, save, autoresearch, canvas, defuddle, obsidian-bases, obsidian-markdown)
- **Hooks**: 4 (SessionStart, PostCompact, PostToolUse, Stop)
- **Multi-agent**: bootstrap files for Codex, OpenCode, Gemini, Cursor, Windsurf, GitHub Copilot

## Install Command (Correct Two-Step Flow)
```bash
claude plugin marketplace add AgriciDaniel/claude-obsidian
claude plugin install claude-obsidian@claude-obsidian-marketplace
```

There is no `claude plugin install github:owner/repo` shortcut. Both steps are required. Full session note: [[claude-obsidian-v1.4-release-session]].

## Recent Release Cycle (v1.1 → v1.4.1)
- **v1.1**: URL ingestion, vision ingestion, delta tracking manifest, 3 new skills (defuddle, obsidian-bases, obsidian-markdown), multi-depth query modes, PostToolUse auto-commit, removed invalid `allowed-tools` frontmatter field
- **v1.4.0**: Dataview to Bases migration (new `wiki/meta/dashboard.base`), Canvas JSON 1.0 spec completeness, PostCompact hook, Obsidian CLI MCP option, 6 multi-agent bootstrap files, 249 em dashes scrubbed, security git history rewrite to remove placeholder email
- **v1.4.1**: hotfix for wrong plugin install command syntax in README and install-guide.md

## Key Lessons (Recent)
1. Plugin install is always two-step: `marketplace add` then `install plugin@marketplace`
2. `allowed-tools` is NOT valid in skill frontmatter. Use only `name` and `description` (kepano convention).
3. Obsidian Bases uses `filters/views/formulas`, not Dataview `from/where`
4. Canvas edges have asymmetric defaults: `fromEnd="none"`, `toEnd="arrow"`
5. Hook-injected context does not survive compaction. PostCompact hook is required to restore hot cache.
6. `git filter-repo` needs two passes: `--replace-text` for blobs, `--replace-message` for commit messages

## Style Preferences (Saved to Memory)
- **No em dashes** (U+2014) or `--` as punctuation anywhere. Use periods, commas, colons, or parentheses. Hyphens in compound words are fine (auto-commit, multi-agent).
- Keep responses short and direct. No trailing "here's what I did" summaries.
- Parallel tool calls when independent.

## Ecosystem Research (Done 2026-04-08)
16+ Claude + Obsidian projects mapped. Full feature matrix at [[claude-obsidian-ecosystem]]. Prioritized backlog at [[cherry-picks]]. Top competitors: [[Ar9av-obsidian-wiki]] (multi-agent + delta tracking), [[rvk7895-llm-knowledge-bases]] (multi-depth query), [[ballred-obsidian-claude-pkm]] (goal cascade + auto-commit), [[kepano-obsidian-skills]] (authoritative Obsidian skills from Obsidian's own creator).

## Blog Posts (agricidaniel.com)
- 16 total blog posts, 23 sitemap URLs (+ claude-ads-v1-5-release not yet in sitemap)
- Latest: how-i-got-8000-github-stars, claude-canvas-ai-visual-production, claude-obsidian-ai-second-brain (2026-04-10), claude-ads-v1-5-release (2026-04-13)
- claude-ads-v1-5-release audited and fixed: added Key Takeaways box, 7/9 H2s as questions, answer-first stats, personal experience callout, cover PNG→WebP, meta desc trimmed, ads-demo.gif added
- Google Indexing API submitted, Bing IndexNow submitted
- Workflow: write JSON -> blogPosts.ts -> sitemap.xml -> llms.txt -> vite build -> prerender.mjs -> vercel deploy --prod -> google-index.py --submit -> IndexNow curl

## GitHub Backlink State
- 26 repos have Author section with agricidaniel.com + Skool + YouTube links
- 5 SEO repos have rankenstein.pro mentions (claude-seo, claude-blog, on-page-seo, Keywordo-kun, marketing-skill-pack)
- All repos have topics/tags set
- All repos have homepage URLs set
- For new repos: always add Author section + homepage URL + topics

## Active Threads
- v1.5.0 backlog: `/adopt` command, vault graph analysis in wiki-lint, semantic search via qmd, Marp output
- `community` remote (`avalonreset-pro/claude-obsidian`) still has pre-rewrite history. Force-push needed next time that remote is configured.

## Repo Locations
- Working: `~/Desktop/claude-obsidian/`
- Public: https://github.com/AgriciDaniel/claude-obsidian
- Community (private): https://github.com/avalonreset-pro/claude-obsidian
