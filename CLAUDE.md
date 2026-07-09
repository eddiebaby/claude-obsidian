# User Profile — Scott

> Loaded every session. This is who I'm working with and how to work with him.

## Who I Am
Scott. Based in Hilo, Hawaii. Three overlapping pursuits:
- **Markets** — trade stocks and financial instruments including futures and options.
- **Code** — programmer; want to build alpha-generating trading strategies and a Jungian individuation app.
- **Inner work** — deep into Jungian psychology: individuation, dream interpretation, active imagination. Read a lot of Jung directly.

## Goals for 2026
1. **Make more money** trading and coding. This is the priority.
2. **Launch an AI consulting business** serving local businesses in Hilo / Hawaii.
3. **Do the Jungian inner work** — and get help decoding dense Jung.

## How to Talk to Me
- Direct. No need to be warm.
- Straight answer, least possible fluff. No padding, no trailing summaries.
- When decoding Jung: I understand the concepts, so translate the hard text plainly. Don't over-explain ideas I already hold.

## Strengths & Weaknesses
- **Strength:** I grasp Jung's concepts even when the text is challenging.
- **Weakness:** Focus and monetization. I drift toward study over income-generating work. Keep me pointed at making money. When I'm reading Jung instead of building or trading, call it.

## Current Projects
Starting from the ground up on all of it — trading systems, the AI consulting business, and the individuation app. Nothing is in flight yet; everything is greenfield.

---

# claude-obsidian — Claude + Obsidian Wiki Vault

This folder is both a Claude Code plugin and an Obsidian vault.

**Plugin name:** `claude-obsidian` (v1.7+ "Compound Vault" — see [docs/compound-vault-guide.md](docs/compound-vault-guide.md); v1.8+ adds methodology modes — see [docs/methodology-modes-guide.md](docs/methodology-modes-guide.md))
**Skills:** `/wiki`, `/wiki-ingest`, `/wiki-query`, `/wiki-lint`, `/wiki-cli` (v1.7), `/wiki-retrieve` (v1.7, opt-in), `/wiki-mode` (v1.8)
**Vault path:** This directory (open in Obsidian directly)

## What This Vault Is For

This vault demonstrates the LLM Wiki pattern — a persistent, compounding knowledge base for Claude + Obsidian. Drop any source, ask any question, and the wiki grows richer with every session.

## Vault Structure

```
.raw/           source documents — immutable, Claude reads but never modifies
wiki/           Claude-generated knowledge base
_templates/     Obsidian Templater templates
_attachments/   images and PDFs referenced by wiki pages
```

## Domain Conventions

Every wiki page (except `type: meta`) must have a `domain:` field:

| Value | Use for |
|-------|---------|
| `depth-psychology` | Jung, archetypes, individuation, dreams |
| `quantitative-finance` | Trading, market research, ML for finance |
| `ai-ml` | AI/ML papers not finance-specific, LLM research |
| `business` | AI consulting, client work, Hawaii market |

Cross-domain pages get the *application* domain (e.g. AI applied to trading → `quantitative-finance`).

This field powers the [[dashboard]] domain balance check. The dashboard is the first thing to open when session focus is unclear — it shows whether the wiki is drifting toward study instead of income.

## Latin Phrases (standing ingest rule)

When ingesting any future text (Jung, alchemical sources, etc.), pull out every Latin phrase encountered and give each its own full concept page (frontmatter, domain, definition, context where the source uses it, related concepts/entities) — same treatment as any other concept, not a glossary stub. Cross-link from the parent source/concept page. Applies to `wiki-ingest`, `/autoresearch`, and `/save` going forward.

## How to Use

Drop a source file into `.raw/`, then tell Claude: "ingest [filename]".

Ask any question. Claude reads the index first, then drills into relevant pages.

Run `/wiki` to scaffold a new vault or check setup status.

Run "lint the wiki" every 10-15 ingests to catch orphans and gaps.

## Cross-Project Access

To reference this wiki from another Claude Code project, add to that project's CLAUDE.md:

```markdown
## Wiki Knowledge Base
Path: /path/to/this/vault

When you need context not already in this project:
1. Read wiki/hot.md first (recent context, ~500 words)
2. If not enough, read wiki/index.md
3. If you need domain specifics, read wiki/<domain>/_index.md
4. Only then read individual wiki pages

Do NOT read the wiki for general coding questions or things already in this project.
```

## Plugin Skills

| Skill | Trigger |
|-------|---------|
| `/wiki` | Setup, scaffold, route to sub-skills |
| `ingest [source]` | Single or batch source ingestion |
| `query: [question]` | Answer from wiki content |
| `lint the wiki` | Health check |
| `/save` | File the current conversation as a structured wiki note |
| `/autoresearch [topic]` | Autonomous research loop: search, fetch, synthesize, file |
| `/canvas` | Visual layer: add images, PDFs, notes to Obsidian canvas |
| `/wiki-cli` (v1.7) | Obsidian CLI transport wrapper; default mutation path on desktop |
| `/wiki-retrieve` (v1.7) | Hybrid contextual + BM25 + cosine-rerank retrieval (opt-in via `bash bin/setup-retrieve.sh`) |
| `/wiki-mode` (v1.8) | Methodology modes (LYT / PARA / Zettelkasten / Generic). Set via `bash bin/setup-mode.sh`; consumed by wiki-ingest / save / autoresearch for routing new pages |
| `/think` (v1.9) | The 10-principle thinking loop (OBSERVE-OBSERVE-LISTEN-THINK-CONNECT-CONNECT-FEEL-ACCEPT-CREATE-GROW) as an invocable workflow. Apply to architectural decisions, audits, post-mortems, ambiguous user requests. Every other skill has a "How to think" appendix mapping this framework to its specific work |

## Output Conventions

When answering a question that produces useful analysis, offer to file it as a wiki page — not just leave it in chat history. Domain-specific defaults:

| Domain | Default output format | Offer to file as |
|--------|-----------------------|-----------------|
| `quantitative-finance` | Markdown table + key finding | Strategy note (`_templates/strategy-note.md`) or concept page |
| `business` | Bulleted action list | Business page update or new concept |
| `depth-psychology` | Prose interpretation | Concept page or dream analysis note |
| `ai-ml` | Technical summary | Concept page |

The goal: analysis doesn't disappear into chat history. If Scott asks "what's the best entry signal for momentum strategies?" and the answer is good, file it.

## Transport (v1.7+)

`scripts/detect-transport.sh` writes `.vault-meta/transport.json` on first run and refreshes weekly. Skills consult it before mutating the vault. Fallback chain: Obsidian CLI → mcp-obsidian → mcpvault → filesystem (always-available floor). Decision tree: [wiki/references/transport-fallback.md](wiki/references/transport-fallback.md).

## Concurrency (v1.7+)

`scripts/wiki-lock.sh` provides per-file advisory locks for safe multi-writer ingest. Every wiki page write should be guarded by `wiki-lock acquire`/`release`. Stale-after default is 60s; cross-process release allowed by design. The PostToolUse hook defers `git add` while locks are held. Closes the latent multi-writer corruption hole from v1.6.

## Methodology Modes (v1.8+)

Pick an organizational style for the vault via `bash bin/setup-mode.sh`. Four modes available: **generic** (v1.7 default — no opinion), **LYT** (Linking Your Thinking — MOCs + atomic notes), **PARA** (Projects/Areas/Resources/Archives), **Zettelkasten** (timestamped IDs, flat, dense linking). The mode is written to `.vault-meta/mode.json` (gitignored by default; `git add -f` to commit). `wiki-ingest`, `save`, and `autoresearch` consult `python3 scripts/wiki-mode.py route <type> "<name>"` before filing new pages — no special-casing needed in the consumer skills. Full guide: [docs/methodology-modes-guide.md](docs/methodology-modes-guide.md). Closes priority gap 5 from the May 2026 compass artifact.

## Pre-commit verifier (v1.7.1+)

After staging changes for a non-trivial workstream but BEFORE running `git commit`, dispatch the `verifier` agent (`agents/verifier.md`). It reads `git diff --cached`, applies the /best-practices six-cut + agent kernel, and returns findings in four tiers (BLOCKER / HIGH / MEDIUM / LOW) with file:line citations. The agent has read-only tools (Read, Grep, Glob, Bash) — it can inspect but never modify, so its output is purely advisory. This closes the loop the v1.7 audit revealed: code went worker → commit with no separate verifier pass, which is how BLOCKER B1 (data-egress consent gap) slipped through. See `docs/audits/v1.7.0-audit-2026-05-17.md` §10 for the retrospective.

## MCP (Optional)

If you configured the MCP server, Claude can read and write vault notes directly.
See `skills/wiki/references/mcp-setup.md` for setup instructions.

## Release Blog Post

After cutting a new release (git tag + `gh release create`), run:

```
/release-blog
```

This generates a blog post on https://agricidaniel.com/blog/, handles cover image generation, SEO metadata, FAQ schema, internal linking, sitemap/llms.txt updates, Vercel deployment, and Google indexing.
