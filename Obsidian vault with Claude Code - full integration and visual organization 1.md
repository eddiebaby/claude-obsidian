# Obsidian vault with Claude Code: full integration and visual organization

**MCPVault or obsidian-mcp-server paired with the Local REST API plugin gives Claude Code full read/write/search access to any Obsidian vault today.** The setup takes under 10 minutes: install one Obsidian plugin, run one CLI command, and Claude can create notes, patch frontmatter, execute Dataview queries, and search across thousands of files. Visual organization layers on top through CSS snippets, graph view groups, and a consistent frontmatter schema — all of which Claude itself can generate and maintain programmatically. This guide covers every piece of the stack, from raw API endpoints to color-coded folder hierarchies, with copy-paste configurations tested as of early 2026.

---

## Section 1: Obsidian Local REST API — complete endpoint reference

The **Local REST API** plugin (coddingtonbear/obsidian-local-rest-api, v3.5.0) runs an HTTPS server inside Obsidian on port **27124** (HTTP on 27123). It exposes the vault as a RESTful service authenticated via Bearer token. The API key is a 256-bit SHA-256 hash auto-generated on first load, found in Settings → Local REST API.

### Authentication and SSL

Every request except `GET /` requires `Authorization: Bearer <api-key>`. The plugin auto-generates a self-signed RSA 2048-bit certificate valid for 365 days. Download it at `https://127.0.0.1:27124/obsidian-local-rest-api.crt`.

**Node.js SSL handling:**
```javascript
// Option 1: Disable verification (local-only, acceptable for localhost)
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

// Option 2: Trust the specific cert
const https = require('https');
const fs = require('fs');
const agent = new https.Agent({
  ca: fs.readFileSync('/path/to/obsidian-local-rest-api.crt')
});
```

**Python SSL handling:**
```python
import requests
# Option 1: Skip verification
response = requests.get("https://127.0.0.1:27124/vault/",
    headers={"Authorization": "Bearer <key>"}, verify=False)
# Option 2: Use downloaded cert
response = requests.get("https://127.0.0.1:27124/vault/",
    headers={"Authorization": "Bearer <key>"},
    verify="/path/to/obsidian-local-rest-api.crt")
```

### File operations on /vault/{path}

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/vault/` | List files in vault root |
| `GET` | `/vault/{path}` | Read file or list directory |
| `PUT` | `/vault/{filename}` | Create or replace file entirely |
| `POST` | `/vault/{filename}` | Append to file (creates if absent) |
| `PATCH` | `/vault/{filename}` | Surgical edit by heading/block/frontmatter |
| `DELETE` | `/vault/{filename}` | Delete a file |

The `GET` endpoint supports three `Accept` headers: `text/markdown` (raw content), `application/vnd.olrapi.note+json` (structured JSON with frontmatter, tags, stat), and `application/vnd.olrapi.document-map+json` (returns available PATCH targets — headings, blocks, frontmatter fields). The **NoteJson** response includes `content`, `frontmatter` (parsed object), `path`, `stat` (ctime/mtime/size), and `tags` array.

### PATCH — surgical section targeting

PATCH is the API's most powerful feature. Three headers control behavior:

| Header | Required | Values |
|--------|----------|--------|
| `Operation` | Yes | `append`, `prepend`, `replace` |
| `Target-Type` | Yes | `heading`, `block`, `frontmatter` |
| `Target` | Yes | Target identifier (heading name, block ID, field name) |

**Nested headings** use `::` as delimiter: `Target: Heading 1::Subheading 1::Deep Heading`. **Block references** use the block ID without the `^` prefix. **Frontmatter fields** target by key name. Three optional headers add precision: `Create-Target-If-Missing: true` creates the target if absent, `Content-Type: application/json` enables smart merge (table rows as JSON arrays, frontmatter list appends), and `Target-Delimiter` overrides the `::` default.

```bash
# Append below a heading
curl -k -X PATCH -H "Authorization: Bearer <key>" \
  -H "Operation: append" -H "Target-Type: heading" \
  -H "Target: Tasks" -H "Content-Type: text/markdown" \
  --data "- [ ] New task" https://127.0.0.1:27124/vault/projects/sprint.md

# Replace a frontmatter field (create if missing)
curl -k -X PATCH -H "Authorization: Bearer <key>" \
  -H "Operation: replace" -H "Target-Type: frontmatter" \
  -H "Target: status" -H "Create-Target-If-Missing: true" \
  -H "Content-Type: application/json" \
  --data '"done"' https://127.0.0.1:27124/vault/projects/sprint.md
```

**Discover available targets** before patching:
```bash
curl -k -H "Authorization: Bearer <key>" \
  -H "Accept: application/vnd.olrapi.document-map+json" \
  https://127.0.0.1:27124/vault/projects/sprint.md
# Returns: { "headings": [...], "blocks": [...], "frontmatterFields": [...] }
```

### Search endpoints

**`POST /search/simple/?query=terms&contextLength=100`** performs Obsidian's built-in fuzzy search. Since v3.3.0, it also matches filenames. Returns scored results with context snippets:
```json
[{"filename": "path/to/file.md", "score": 0.85,
  "matches": [{"match": {"start": 42, "end": 55}, "context": "...text..."}]}]
```

**`POST /search/`** supports two content types. With `Content-Type: application/vnd.olrapi.dataview.dql+txt`, send any Dataview TABLE query as the body (requires the Dataview plugin). With `Content-Type: application/vnd.olrapi.jsonlogic+json`, send a JsonLogic expression evaluated against each note's metadata. Extended operators include `glob` and `regexp` for pattern matching.

```bash
# Dataview query via API
curl -k -X POST -H "Authorization: Bearer <key>" \
  -H "Content-Type: application/vnd.olrapi.dataview.dql+txt" \
  --data 'TABLE status, priority FROM "projects" WHERE status = "active" SORT priority DESC' \
  https://127.0.0.1:27124/search/

# JsonLogic query — find notes with specific tag
curl -k -X POST -H "Authorization: Bearer <key>" \
  -H "Content-Type: application/vnd.olrapi.jsonlogic+json" \
  --data '{"in": ["project", {"var": "tags"}]}' \
  https://127.0.0.1:27124/search/
```

### Commands, tags, periodic notes, and active file

**`GET /commands/`** lists all registered Obsidian commands with `id` and `name`. **`POST /commands/{commandId}/`** executes any command (useful for triggering Templater, QuickAdd, or graph refresh). **`GET /tags/`** returns all tags with usage counts, including hierarchical rollups. **`/periodic/{period}/`** supports `daily`, `weekly`, `monthly`, `quarterly`, `yearly` — each with GET/PUT/POST/PATCH/DELETE. Since v3.1.0, arbitrary dates work via `/periodic/{period}/{year}/{month}/{day}/`. **`/active/`** operates on the currently open file in Obsidian's UI with all CRUD methods.

### Error codes and operational limits

Standard HTTP codes apply (200, 204, 400, 404, 405). A **422** occurs when both URL-embedded and header-based targets conflict. Plugin-specific 5-digit error codes (40144–50000) provide detailed diagnostics in JSON responses. **No rate limits** exist since the server runs locally. No documented max payload size — limited by Node.js/Express defaults (~100KB JSON). The plugin is **desktop-only** and single-threaded within Obsidian's Electron process.

### V2 vs V3 PATCH migration

V3 (current) replaced V2's heading-only PATCH with the `markdown-patch` library supporting headings, blocks, and frontmatter. V2 headers (`Heading`, `Content-Insertion-Position`) are deprecated and scheduled for removal in v4.0. Requests with a `Heading` header but no `Target-Type` header route to V2 compatibility mode and return deprecation headers.

---

## Section 2: Every MCP server for connecting Obsidian to Claude

Nine MCP servers were identified as of April 2026. The field has matured rapidly — options range from 7-tool Python wrappers to 44-tool Rust engines with graph analysis.

### The leading contenders

**mcp-obsidian** (MarkusPfundstein) is the most popular by stars (**2,800+**). It's a Python server installed via `uvx mcp-obsidian` that proxies the Local REST API. It offers 7 tools: `list_files_in_vault`, `list_files_in_dir`, `get_file_contents`, `search`, `patch_content`, `append_content`, `delete_file`. Known limitation: `patch_content` has reported timeout issues, and there's no tag management or dedicated frontmatter tools.

**obsidian-mcp-server** (cyanheads, **363 stars**) is a TypeScript server with **10+ tools** including `obsidian_get_properties`, `obsidian_update_properties`, `obsidian_complex_search` (JsonLogic), and `obsidian_search_replace`. It adds an in-memory vault cache with periodic refresh, Zod schema validation, and case-insensitive path fallback. Install: `npm install -g obsidian-mcp-server`.

**MCPVault** (bitbonsai, formerly mcp-obsidian) operates on **direct filesystem access** — no Obsidian plugin required. Its **14 tools** include `search_notes` (BM25-ranked), `get_frontmatter`, `update_frontmatter`, `read_multiple_notes` (batch), and `list_all_tags`. Token-optimized responses are **40–60% smaller** than competitors. Install: `npx @bitbonsai/mcpvault@latest /path/to/vault`.

**obsidian-mcp** (StevenStavrakis, **635 stars**) also uses filesystem access with **12 tools** including strong tag management: `add_tags`, `remove_tags`, `rename_tag` across the entire vault. No Obsidian plugin needed. Install: `npx -y obsidian-mcp /path/to/vault`.

**TurboVault** (Epistates) is a Rust-based server with **44 specialized tools** spanning file operations, BM25 search via Tantivy, **link graph analysis** (backlinks, hub notes, orphans, cycles), batch transactional edits, vault health scoring, and an audit trail with rollback. Sub-100ms performance. Install: `cargo install turbovault`.

### Specialized options

**MegaMem** (C-Bjorn) syncs notes to a **Neo4j/FalkorDB temporal knowledge graph** via the Graphiti framework, exposing 21 MCP tools. Entities become graph nodes with AI-extracted relationships and timestamps. Setup requires Neo4j Desktop or FalkorDB Docker, Python dependencies, and an LLM API key for entity extraction — significant infrastructure overhead. Best for users who want cross-conversation memory and relationship discovery across very large vaults, but overkill for most solo creators.

**obsidian-mcp-tools** (jacksteamdev) is an Obsidian plugin bundling its own MCP server binary. It's the **only option offering true semantic search** via Smart Connections embeddings, plus Templater template execution through MCP. Auto-configures Claude Desktop but works with Claude Code too.

**obsidian-mcp** (aleksakarac) provides **45 tools** including Tasks plugin integration, Dataview field extraction, and Kanban board manipulation — the most comprehensive plugin integration of any MCP server.

### Recommendation for a solo creator with 1000+ notes

**Primary pick: MCPVault.** Zero dependencies on running Obsidian, 14 well-designed tools, token-optimized responses critical for large vaults, safe frontmatter handling via gray-matter, and the simplest install of any option. BM25 search handles keyword queries well.

**Runner-up: obsidian-mcp-server (cyanheads)** if you prefer REST API integration with vault caching and need JsonLogic-based complex search.

**For semantic search: add obsidian-mcp-tools** alongside your primary server — it's the only way to get meaning-based retrieval rather than keyword matching. Both can coexist as separate MCP servers in your Claude config.

**For power users: TurboVault** if you want link graph analysis, vault health scoring, and transactional batch edits across 1000+ notes. Requires Rust toolchain.

---

## Section 3: Claude Code configuration for Obsidian MCP

### Adding the MCP server via CLI

The `claude mcp add` command requires all flags **before** the server name, with `--` separating Claude's flags from the server command:

```bash
claude mcp add-json mcp-obsidian '{
  "type": "stdio",
  "command": "uvx",
  "args": ["mcp-obsidian"],
  "env": {
    "OBSIDIAN_API_KEY": "your_api_key_here",
    "OBSIDIAN_HOST": "127.0.0.1",
    "OBSIDIAN_PORT": "27124",
    "NODE_TLS_REJECT_UNAUTHORIZED": "0"
  }
}' --scope user
```

For filesystem-based servers (no REST API needed):
```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "npx",
  "args": ["@bitbonsai/mcpvault@latest", "/path/to/your/vault"]
}' --scope user
```

### Manual JSON configuration

Claude Code stores config in **`~/.claude.json`** (not the Claude Desktop path). Edit the `mcpServers` block directly:

```json
{
  "mcpServers": {
    "obsidian-vault": {
      "type": "stdio",
      "command": "npx",
      "args": ["@bitbonsai/mcpvault@latest", "/path/to/your/vault"]
    }
  }
}
```

Restart Claude Code after manual edits. If `uvx` or `npx` isn't found, use the full path from `which uvx`.

### Scopes: user vs project vs local

| Scope | Storage | Visibility | Best for |
|-------|---------|------------|----------|
| `user` | `~/.claude.json` (global) | You, all projects | **Obsidian vault** — cross-project, private credentials |
| `project` | `.mcp.json` in project root | Everyone via git | Team-shared tools (exposes API key!) |
| `local` | `~/.claude.json` under project | You, one project only | Per-project dev servers |

**Use `--scope user`** for Obsidian. The vault serves all projects, and credentials should stay private. If you must use project scope, reference environment variables: `"OBSIDIAN_API_KEY": "${OBSIDIAN_API_KEY}"`.

### Verification

```bash
claude mcp list              # List all configured servers
claude mcp get mcp-obsidian  # Details for specific server
claude --mcp-debug           # Launch with debug logging
```

Inside a Claude Code session, type `/mcp` to see connection status. Test with: "List all files in my Obsidian vault."

### CLAUDE.md for vault context

Place a `CLAUDE.md` at the vault root. It loads automatically every session started from that directory:

```markdown
# Vault Context
This is a knowledge base organized into 6 domains.

## Structure
- skills/ — capabilities and learning notes
- system/ — vault conventions, workflows, configs
- concepts/ — ideas, mental models, reference
- tools/ — software, libraries, services
- projects/ — active work with deliverables
- people/ — contacts, collaborators
- _attachments/ — images and PDFs (skip these)
- _templates/ — Obsidian templates (skip these)

## Conventions
- Frontmatter uses type/status/domain/created/updated fields
- Tags use #domain/subcategory format
- Wikilinks: [[Note Name]] (unique filenames, no path needed)

## MCP Tools Available
- Use vault search tools for finding notes
- Use file read tools for content retrieval
- Use frontmatter update tools for metadata changes
- Prefer targeted PATCH over full file replacement
```

Keep CLAUDE.md **under 300 lines** — it loads on every message and consumes tokens. Use pointers ("see projects/api-design.md") instead of pasting content.

### Context window management

Each MCP tool definition costs **400–800 tokens**. A 20-tool server burns ~14K tokens on tool schemas alone. Since January 2026, Claude Code's **MCP Tool Search** feature defers tool definitions when they exceed 10% of context, reducing initial overhead by ~85%.

Practical strategies: use `/compact` proactively at ~60% context usage, scope requests to specific folders rather than vault-wide sweeps, use `/clear` between unrelated tasks, and set `MAX_MCP_OUTPUT_TOKENS=50000` if vault files are large. For verbose operations, Claude Code's subagent feature gives each subtask its own context window.

### When to use curl vs MCP

Use **MCP tools** for interactive Claude Code sessions — multi-step operations, synthesis, analysis. Use **curl via the Bash tool** for debugging connectivity, one-off queries, or when you need precise control over headers. Always **test with curl first** when setting up, then configure MCP.

---

## Section 4: Visual customization — colors, icons, and canvas

### CSS snippets for folder colors

Place `.css` files in `.obsidian/snippets/`, enable via Settings → Appearance → CSS Snippets. The key selector is `.nav-folder-title[data-path="foldername"]`:

```css
:root {
  --color-skills: #4fc1ff;    /* Blue */
  --color-system: #c586c0;    /* Purple */
  --color-concepts: #dcdcaa;  /* Yellow */
  --color-tools: #ce9178;     /* Orange */
  --color-projects: #6a9955;  /* Green */
  --color-people: #d16969;    /* Red */
}

.nav-folder-title[data-path="skills"] {
  color: var(--color-skills);
  background-color: rgba(79, 193, 255, 0.08);
}
.nav-folder-title[data-path^="skills/"],
.nav-file-title[data-path^="skills/"] {
  border-left: 2px solid rgba(79, 193, 255, 0.25);
}
/* Repeat for system, concepts, tools, projects, people */
```

Use `[data-path="exact"]` for exact match, `[data-path^="prefix"]` for starts-with (catches subfolders). The community snippet [CyanVoxel/Obsidian-Colored-Sidebar](https://github.com/CyanVoxel/Obsidian-Colored-Sidebar) (816+ stars) provides a complete numbered-prefix approach with 8+ colors.

### Custom callouts for note types

Callouts use `.callout[data-callout='typename']` with two CSS variables. Colors must be **RGB numeric** (not hex), and icons use the `lucide-` prefix:

```css
.callout[data-callout='skill']   { --callout-color: 79, 193, 255; --callout-icon: lucide-zap; }
.callout[data-callout='system']  { --callout-color: 197, 134, 192; --callout-icon: lucide-settings; }
.callout[data-callout='concept'] { --callout-color: 220, 220, 170; --callout-icon: lucide-lightbulb; }
.callout[data-callout='tool']    { --callout-color: 206, 145, 120; --callout-icon: lucide-wrench; }
.callout[data-callout='project'] { --callout-color: 106, 153, 85; --callout-icon: lucide-folder-kanban; }
.callout[data-callout='person']  { --callout-color: 209, 105, 105; --callout-icon: lucide-user; }
```

Usage: `> [!skill] Learning Goal` in any note renders with the custom color and icon.

### Graph view color groups

Open Graph View → gear icon → **Groups**. Add groups in priority order (top = highest priority):

| Query | Color | Domain |
|-------|-------|--------|
| `path:skills` | Blue (#4fc1ff) | Skills |
| `path:system` | Purple (#c586c0) | System |
| `path:concepts` | Yellow (#dcdcaa) | Concepts |
| `path:tools` | Orange (#ce9178) | Tools |
| `path:projects` | Green (#6a9955) | Projects |
| `path:people` | Red (#d16969) | People |

Force settings to tune: **Center force** pulls nodes inward, **Repel force** pushes them apart, **Link force** attracts connected nodes. For a 1000-note vault, increase repel force and decrease link distance for readable clusters. **Local graph** (right-click any note tab) shows only that note's connections — use it for focused exploration. **Global graph** shows everything — filter with the search bar (`path:projects -path:raw`). Note: color groups set in global graph do **not** auto-apply to local graphs; use the **Sync Graph Settings** plugin.

### Tag colors via CSS

Obsidian has **no native tag coloring**. Use CSS with the `href` attribute:

```css
.tag[href^="#skills"]  { background-color: #4fc1ff; color: #1a1a2e; border-radius: 14px; padding: 1px 8px; }
.tag[href^="#project"] { background-color: #6a9955; color: white; border-radius: 14px; padding: 1px 8px; }
```

The `href^=` prefix selector catches child tags automatically (#skills/python matches `#skills`).

### Canvas JSON format — Claude can write these

Canvas files are plain JSON stored as `.canvas` in the vault. Claude can create them programmatically:

```json
{
  "nodes": [
    {"id": "n1", "type": "text", "text": "# Central Concept\nCore idea here.",
     "x": 0, "y": 0, "width": 300, "height": 200, "color": "4"},
    {"id": "n2", "type": "file", "file": "projects/website.md",
     "x": 400, "y": 0, "width": 300, "height": 200, "color": "#6a9955"}
  ],
  "edges": [
    {"id": "e1", "fromNode": "n1", "fromSide": "right",
     "toNode": "n2", "toSide": "left", "toEnd": "arrow", "label": "relates to"}
  ]
}
```

Four node types exist: `text` (markdown content), `file` (vault file embed), `link` (external URL), `group` (visual container). Colors use palette values `"1"` through `"6"` or hex strings. The spec is open-standard at jsoncanvas.org.

### Themes and folder icons

**Minimal Theme** is the most popular dark theme (~500K downloads, official Best Theme award). Install via Settings → Appearance → Manage → search "Minimal". Pair with the **Minimal Theme Settings** plugin for GUI customization and **Style Settings** for deep control. Built-in color schemes include Catppuccin, Dracula, Nord, Gruvbox, and Solarized. **AnuPpuccin** (Catppuccin-based, Gem of the Year 2022) offers rainbow folder sidebars and custom checkboxes but is currently on hiatus. **Things** provides a Mac-native aesthetic with custom task statuses.

For folder icons, install the **Iconize** plugin (formerly Icon Folder). Right-click any folder → Change icon → browse **1,700+ Lucide icons** or add custom SVG packs. The newer **Iconic** plugin offers rule-based auto-icons (assign icons by file extension, folder path, or frontmatter property).

### Properties UI (Obsidian 1.4+)

Properties render frontmatter as a visual widget supporting types: Text, List, Number, Checkbox, Date, Date & time, Tags, Aliases, Links. Type definitions are **vault-wide** — setting a property to "Date" applies everywhere. Properties cannot be natively styled per-property with colors, but CSS can target `[data-property-key="status"]` for basic highlighting. The **Iconic** plugin can add custom icons to properties in the sidebar.

---

## Section 5: Essential community plugins for AI-assisted vaults

### Dataview — the query backbone

Dataview indexes all frontmatter, inline fields (`Key:: Value`), tags, and tasks. Its DQL language powers dynamic dashboards that Claude can both generate and execute via the REST API:

```dataview
TABLE status, priority, due FROM "projects" WHERE status != "done" SORT priority DESC
```
```dataview
LIST FROM #concept WHERE contains(tags, "ai") SORT file.mtime DESC LIMIT 10
```
```dataview
TASK WHERE !completed AND contains(tags, "#urgent") SORT created ASC
```

Claude executes DQL programmatically via `POST /search/` with `Content-Type: application/vnd.olrapi.dataview.dql+txt`. Four query types: `LIST`, `TABLE`, `CALENDAR`, `TASK`. Inline queries embed single values: `` `= this.file.name` ``. **Rating: Essential** — the backbone of any structured vault.

### Templater and QuickAdd — automation engines

**Templater** provides a template language with JS execution (`<% tp.date.now("YYYY-MM-DD") %>`) and shell command support. Claude can author template files and trigger insertion via the REST API commands endpoint (`POST /commands/templater-obsidian:insert-templater/`). **QuickAdd** chains Templates, Captures, Macros, and user scripts into automated workflows. Both can be triggered via the commands API or Advanced URI plugin.

### Smart Connections — semantic search layer

Smart Connections builds local embeddings (default: TaylorAI/bge-micro-v2, 384-dimensional vectors) for meaning-based retrieval. It's **complementary to Claude, not redundant**: Smart Connections pre-computes embeddings for fast retrieval, Claude provides reasoning. A dedicated MCP server (`smart-connections-mcp`) exposes the embeddings to Claude Code. For a 1000+ note vault, this is the difference between finding "notes about machine learning" via keyword and finding conceptually related notes about "neural network architectures" or "gradient descent optimization."

### Obsidian Git — version control against AI-induced data loss

Auto-commit on a 10–15 minute interval protects against any MCP server mishap. Recommended `.gitignore`:

```gitignore
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.smart-connections/
.obsidian-git-data
.trash/
.DS_Store
```

Track `.obsidian/community-plugins.json` and `.obsidian/core-plugins.json` for plugin consistency across machines.

### Other notable plugins

**Folder Notes** (LostPaul) makes folders clickable to open an attached index note — Claude creates these by writing `Projects/Projects.md` with a Dataview query listing folder contents. **Advanced URI** enables command execution from terminal: `open "obsidian://adv-uri?vault=V&commandid=<id>"`. **Obsidian Claude Code MCP** (iansinnott) is an Obsidian plugin running a native MCP server with WebSocket auto-discovery — type `/ide` in Claude Code and select Obsidian. **Text Generator** provides in-editor LLM access but is largely redundant with Claude Code.

---

## Section 6: Frontmatter schemas for six domains

### Design principles

Use **flat YAML only** — Obsidian's Properties UI does not support nested objects. Every note gets `type`, `status`, `domain`, `created`, `updated`, and `tags`. Use **ISO 8601 dates**, **snake_case** for property names, **plural forms** (`tags` not `tag`), and quote wikilinks in YAML (`"[[Note Name]]"`).

### Complete schemas

**skills/ notes:**
```yaml
---
type: skill
domain: skills
title: "Python Type Hints"
status: learning  # learning | practicing | mastered
category: programming  # programming | design | communication | analysis
proficiency: 3  # 1-5
created: 2026-04-06
updated: 2026-04-06
tags:
  - skill
  - programming
related:
  - "[[Python]]"
  - "[[Static Typing]]"
---
```

**system/ notes:**
```yaml
---
type: system
domain: system
title: "Vault Naming Conventions"
status: active  # active | deprecated | draft
category: convention  # convention | workflow | template | config
scope: vault-wide  # vault-wide | domain-specific
created: 2026-04-06
updated: 2026-04-06
tags:
  - system
  - convention
review_interval: quarterly
---
```

**concepts/ notes:**
```yaml
---
type: concept
domain: concepts
title: "Retrieval Augmented Generation"
status: developing  # seed | developing | mature | evergreen
category: ai  # ai | philosophy | business | science
complexity: advanced  # basic | intermediate | advanced
created: 2026-04-06
updated: 2026-04-06
tags:
  - concept
  - ai
related:
  - "[[Vector Databases]]"
source: "[[RAG Paper 2023]]"
aliases:
  - RAG
---
```

**tools/ notes:**
```yaml
---
type: tool
domain: tools
title: "Obsidian Local REST API"
status: active  # active | evaluating | archived
category: software  # software | hardware | service | library
url: https://github.com/coddingtonbear/obsidian-local-rest-api
version: "3.5.0"
created: 2026-04-06
updated: 2026-04-06
tags:
  - tool
  - obsidian
  - api
use_case: "Vault automation and AI integration"
---
```

**projects/ notes:**
```yaml
---
type: project
domain: projects
title: "AI Second Brain Build"
status: active  # planning | active | paused | completed | archived
priority: 1  # 1-5
start_date: 2026-04-01
due_date: 2026-06-30
created: 2026-04-06
updated: 2026-04-06
tags:
  - project
  - ai
deliverables:
  - "Working MCP integration"
  - "Vault architecture documentation"
---
```

**people/ notes:**
```yaml
---
type: person
domain: people
title: "Jane Smith"
status: active  # active | inactive
category: colleague  # colleague | mentor | collaborator | contact
company: "Acme Corp"
role: "Senior Engineer"
created: 2026-04-06
updated: 2026-04-06
tags:
  - person
  - colleague
last_contact: 2026-03-15
topics:
  - "[[Machine Learning]]"
---
```

### Tags vs properties — when to use which

Use **tags** for broad categorization and cross-cutting concerns (`#project`, `#urgent`, `#meeting`) — they're natively indexed, clickable, and support hierarchical nesting (`#area/work/project`). Use **properties** for typed metadata that drives dashboards and API filtering (`status: active`, `priority: 3`, `due_date: 2026-06-30`). In large vaults, both are indexed and performant. The two systems serve different purposes: tags are for discovery and navigation, properties are for structured queries and automation.

---

## Section 7: Vault architecture at scale

### When Obsidian slows down and why

Desktop performance remains solid to approximately **10,000 markdown notes** for most users. Benchmarks have tested up to 100,000 highly-linked files with Obsidian handling them, albeit with longer startup times. **The bottleneck is rarely note count itself** — it's total file count (a vault with 2,700 .md files but **570,000 attachments** was "unusably slow"), heavy vault-scanning plugins (Dataview and Tasks re-read the entire vault on edits), and oversized individual notes (100+ pages caused 5-second keystroke delays). Mobile is far more constrained: a 40,000-note vault on iPhone 14 Pro was "almost completely unusable."

Mitigation: minimize vault-scanning plugins, keep attachments in a centralized `_attachments/` folder, use SSD storage, split large notes into atomic notes, and use Settings → Community Plugins → **Debug startup time** to identify slow plugins.

### Search scaling and the REST API

The `/search/simple/` endpoint uses Obsidian's built-in indexed search — fast and scales with the metadata cache. Dataview DQL queries via `/search/` leverage Dataview's own index but can be slow on very large vaults with complex queries. JsonLogic evaluates against metadata and scales linearly with vault size. For 1000+ notes, prefer `/search/simple/` for text and JsonLogic for metadata filtering. MCP servers like cyanheads' obsidian-mcp-server add an in-memory cache (refreshes every 10 minutes) as a performance buffer.

### Excluding files from indexing

Obsidian has **no native `.obsidianignore` file**. Three exclusion methods:

- **Dot-prefixed folders** (`.raw/`, `.archive/`) — Obsidian completely ignores these. Most reliable method.
- **Settings → Files & Links → Excluded files** — uses glob patterns but only hides from file explorer/search, not all parsers.
- **File Ignore plugin** — applies `.gitignore`-style patterns by dot-prefixing folders.

Exclude: `.raw/` (data dumps), `.archive/` (cold storage), `.git/`, `node_modules/`, large attachment subfolders.

### Folder depth and naming

Keep folders to **maximum 2–3 levels deep**. Deeper nesting burns tokens on path resolution when AI agents traverse the vault, complicates wikilinks, and creates friction when reorganizing. Use **unique filenames** so wikilinks work without paths (`[[Note Name]]` instead of `[[folder/subfolder/Note Name]]`).

```
vault/
├── skills/
├── system/
├── concepts/
├── tools/
├── projects/
│   ├── active/
│   └── archived/
├── people/
├── daily/
│   └── 2026/
│       └── 04-April/
├── _attachments/
├── _templates/
└── _meta/          # MOCs, dashboards, vault config notes
```

**Naming conventions:** spaces for note titles (Obsidian's default, most readable), dashes for folder names (CLI-friendly), snake_case for frontmatter property names, kebab-case for tags. The **Front Matter Title** plugin can display a frontmatter `title` property instead of the filename in the explorer.

### Attachments strategy

Use a **centralized `_attachments/` folder** (Settings → Files & Links → Default location → "In the folder specified below"). This cleanly separates binary files from notes, simplifies exclusion from indexing, and prevents the file count explosion that degrades performance. Store large files (videos, big PDFs) **outside the vault** and link with `file:///` protocol. The **Attachment Management** plugin auto-names attachments with variables like `${notename}` and `${date}`.

### Daily notes with the periodic endpoint

Set the Daily Notes date format to `YYYY/MM-MMMM/YYYY-MM-DD-dddd` for auto-created folder hierarchy. The REST API's `/periodic/daily/` endpoint reads and writes today's note, while `/periodic/daily/2026/4/6/` accesses any specific date. Template:

```yaml
---
date: 2026-04-06
type: daily
tags:
  - daily
energy: null
mood: null
---
```

## Conclusion

The Obsidian + Claude Code integration stack is production-ready today. **MCPVault or obsidian-mcp-server** provides the fastest path to full vault access — install, configure one JSON block, and Claude can read, write, search, and patch any note. The Local REST API's **PATCH endpoint with heading/block/frontmatter targeting** is the key differentiator: Claude can surgically update a single frontmatter field or append beneath a specific heading without touching anything else. For a 1000+ note vault, the combination of consistent frontmatter schemas (flat YAML with `type`/`status`/`domain`), folder-based graph coloring, and Dataview queries executed via API creates a system where Claude can navigate, query, and maintain the knowledge base as effectively as a human — and considerably faster. The one gap remaining is semantic search: add Smart Connections with its MCP bridge if keyword matching proves insufficient for your retrieval needs.