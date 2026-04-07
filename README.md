# cosmic-brain

Claude + Obsidian knowledge companion. A running notetaker that builds and maintains a persistent, compounding wiki vault. Every source you add gets integrated. Every question you ask pulls from everything that has been read. Knowledge compounds like interest.

Based on Andrej Karpathy's LLM Wiki pattern.

---

## What It Does

You drop sources. Claude reads them, extracts entities and concepts, updates cross-references, and files everything into a structured Obsidian vault. The wiki gets richer with every ingest.

You ask questions. Claude reads the hot cache (recent context), scans the index, drills into relevant pages, and synthesizes an answer. It cites specific wiki pages, not training data.

You lint. Claude finds orphans, dead links, stale claims, and missing cross-references. Your wiki stays healthy without manual cleanup.

At the end of every session, Claude updates a hot cache. The next session starts with full recent context, no recap needed.

---

## Quick Start

**Option 1: Clone and open as vault**

```bash
git clone https://github.com/AgriciDaniel/cosmic-brain
```

Open the folder in Obsidian as a vault. Open it in Claude Code. Type `/wiki`.

**Option 2: Install as plugin**

```bash
claude plugin install github:AgriciDaniel/cosmic-brain
```

Then in any Claude Code session: `/wiki`

**Option 3: Add to existing vault**

Copy `WIKI.md` into your project root or `~/.claude/`. Paste this into Claude:

```
Read WIKI.md in this project. Then:
1. Check if Obsidian is installed. If not, install it or walk me through it.
2. Check if the Local REST API plugin is running (port 27124). If not, guide me through enabling it.
3. Configure the MCP server so you can read and write my vault.
4. Ask me ONE question: "What is this vault for?"

Then build the entire wiki structure based on my answer.
```

---

## Commands

| You say | Claude does |
|---------|------------|
| `/wiki` | Setup check, scaffold, or continue where you left off |
| `ingest [file]` | Read source, create 8-15 wiki pages, update index and log |
| `ingest all of these` | Batch process multiple sources, then cross-reference |
| `what do you know about X?` | Read index > relevant pages > synthesize answer |
| `/save` | File the current conversation as a wiki note |
| `/save [name]` | Save with a specific title (skips the naming question) |
| `/autoresearch [topic]` | Run the autonomous research loop: search, fetch, synthesize, file |
| `lint the wiki` | Health check: orphans, dead links, gaps, suggestions |
| `update hot cache` | Refresh hot.md with latest context summary |

---

## Cross-Project Power Move

Point any Claude Code project at this vault. Add to that project's `CLAUDE.md`:

```markdown
## Wiki Knowledge Base
Path: ~/path/to/vault

When you need context not already in this project:
1. Read wiki/hot.md first (recent context cache)
2. If not enough, read wiki/index.md
3. If you need domain details, read the relevant domain sub-index
4. Only then drill into specific wiki pages

Do NOT read the wiki for general coding questions or tasks unrelated to [domain].
```

Your executive assistant, coding projects, and content workflows all draw from the same knowledge base.

---

## Six Wiki Modes

| Mode | Use when |
|------|---------|
| A: Website | Sitemap, content audit, SEO wiki |
| B: GitHub | Codebase map, architecture wiki |
| C: Business | Project wiki, competitive intelligence |
| D: Personal | Second brain, goals, journal synthesis |
| E: Research | Papers, concepts, thesis |
| F: Book/Course | Chapter tracker, course notes |

Modes can be combined.

---

## What Gets Created

A typical scaffold creates:
- Folder structure for your chosen mode
- `wiki/index.md` — master catalog
- `wiki/log.md` — append-only operation log
- `wiki/hot.md` — recent context cache
- `wiki/overview.md` — executive summary
- `wiki/meta/dashboard.md` — Dataview dashboard
- `_templates/` — Obsidian Templater templates for each note type
- `.obsidian/snippets/vault-colors.css` — color-coded file explorer
- Vault `CLAUDE.md` — auto-loaded project instructions

---

## MCP Setup (Optional)

MCP lets Claude read and write vault notes directly without copy-paste.

Option A (REST API based):
1. Install the Local REST API plugin in Obsidian
2. Copy your API key
3. Run:
```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "uvx",
  "args": ["mcp-obsidian"],
  "env": {
    "OBSIDIAN_API_KEY": "your-key",
    "OBSIDIAN_HOST": "127.0.0.1",
    "OBSIDIAN_PORT": "27124",
    "NODE_TLS_REJECT_UNAUTHORIZED": "0"
  }
}' --scope user
```

Option B (filesystem based, no plugin needed):
```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@bitbonsai/mcpvault@latest", "/path/to/your/vault"]
}' --scope user
```

---

## Recommended Plugins

Install via Obsidian > Settings > Community Plugins:

| Plugin | What it does |
|--------|-------------|
| Dataview | Powers the dashboard queries |
| Templater | Auto-populates frontmatter from templates |
| Obsidian Git | Auto-commits every 15 minutes |
| Minimal Theme | Best dark theme for this setup |

Also install the **Obsidian Web Clipper** browser extension. It sends web pages to `.raw/` in one click.

---

## File Structure

```
cosmic-brain/
├── .claude-plugin/
│   ├── plugin.json              # manifest
│   └── marketplace.json         # distribution
├── skills/
│   ├── wiki/                    # orchestrator + references (7 ref files)
│   ├── wiki-ingest/             # INGEST operation
│   ├── wiki-query/              # QUERY operation
│   ├── wiki-lint/               # LINT operation
│   ├── save/                    # /save — file conversations to wiki
│   └── autoresearch/            # /autoresearch — autonomous research loop
│       └── references/
│           └── program.md       # configurable research objectives
├── agents/
│   ├── wiki-ingest.md           # parallel ingestion agent
│   └── wiki-lint.md             # health check agent
├── commands/
│   ├── wiki.md                  # /wiki bootstrap command
│   ├── save.md                  # /save command
│   └── autoresearch.md          # /autoresearch command
├── hooks/
│   └── hooks.json               # SessionStart + Stop hot cache hooks
├── _templates/                  # Obsidian Templater templates
├── wiki/
│   ├── Wiki Map.canvas          # visual hub — central graph node
│   ├── concepts/                # seeded: LLM Wiki Pattern, Hot Cache, Compounding Knowledge
│   ├── entities/                # seeded: Andrej Karpathy
│   ├── sources/                 # seeded: Nate Herk LLM Wiki Transcript
│   └── meta/dashboard.md        # Dataview dashboard
├── .raw/                        # source documents (hidden in Obsidian)
├── .obsidian/snippets/          # vault-colors.css (3-color scheme)
├── WIKI.md                      # full schema reference
├── CLAUDE.md                    # project instructions
└── README.md                    # this file
```

---

## AutoResearch: program.md

The `/autoresearch` command is configurable. Edit `skills/autoresearch/references/program.md` to control:

- What sources to prefer (academic, official docs, news)
- Confidence scoring rules
- Max rounds and max pages per session
- Domain-specific constraints

The default program works for general research. Override it for your domain. A medical researcher would add "prefer PubMed". A business analyst would add "focus on market data and filings".

---

## Seed Vault

This repo ships with a seeded vault. Open it in Obsidian and you'll see:

- `wiki/concepts/` — LLM Wiki Pattern, Hot Cache, Compounding Knowledge
- `wiki/entities/` — Andrej Karpathy
- `wiki/sources/` — Nate Herk LLM Wiki Transcript
- `wiki/meta/dashboard.md` — Dataview dashboard (requires Dataview plugin)

The graph view will show a connected cluster of 5 pages. This is what the wiki looks like after one ingest. Add more sources and it grows from there.

---

*Based on [Andrej Karpathy's LLM Wiki pattern](https://github.com/karpathy). Hot cache and cross-project patterns demonstrated by [Nate Herk](https://youtube.com/@nateherk). Built by [AgriciDaniel](https://github.com/AgriciDaniel) / AI Marketing Hub.*
