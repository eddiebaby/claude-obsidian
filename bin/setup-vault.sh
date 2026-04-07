#!/usr/bin/env bash
# cosmic-brain vault setup script
# Run this ONCE before opening Obsidian for the first time.
# Usage: bash bin/setup-vault.sh [optional: /path/to/vault]
# Default: uses the directory where this script lives (the vault root)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT="${1:-$(dirname "$SCRIPT_DIR")}"
OBSIDIAN="$VAULT/.obsidian"

echo "Setting up cosmic-brain vault at: $VAULT"

# ── 1. Create directories ─────────────────────────────────────────────────────
mkdir -p "$OBSIDIAN/snippets"
mkdir -p "$VAULT/.raw"
mkdir -p "$VAULT/wiki/concepts" "$VAULT/wiki/entities" "$VAULT/wiki/sources" "$VAULT/wiki/meta"
mkdir -p "$VAULT/_templates"

# ── 2. Write graph.json ───────────────────────────────────────────────────────
cat > "$OBSIDIAN/graph.json" << 'EOF'
{
  "collapse-filter": false,
  "search": "path:wiki",
  "showTags": false,
  "showAttachments": false,
  "hideUnresolved": true,
  "showOrphans": false,
  "collapse-color-groups": false,
  "colorGroups": [
    { "query": "path:wiki/entities",    "color": { "a": 1, "rgb": 12945088 } },
    { "query": "path:wiki/concepts",    "color": { "a": 1, "rgb": 5227007  } },
    { "query": "path:wiki/sources",     "color": { "a": 1, "rgb": 6986069  } },
    { "query": "path:wiki/meta",        "color": { "a": 1, "rgb": 5676246  } },
    { "query": "path:wiki",             "color": { "a": 1, "rgb": 5676246  } }
  ],
  "showArrow": true,
  "textFadeMultiplier": -1,
  "nodeSizeMultiplier": 1.8,
  "lineSizeMultiplier": 1.2,
  "centerStrength": 0.5,
  "repelStrength": 30,
  "linkStrength": 1.5,
  "linkDistance": 120,
  "scale": 1.0
}
EOF

# ── 3. Write app.json (excluded files) ───────────────────────────────────────
cat > "$OBSIDIAN/app.json" << 'EOF'
{
  "userIgnoreFilters": [
    "agents/",
    "commands/",
    "hooks/",
    "skills/",
    "_templates/",
    "README.md",
    "CLAUDE.md",
    "WIKI.md",
    "Welcome.md"
  ]
}
EOF

# ── 4. Write appearance.json (enable CSS snippet) ────────────────────────────
cat > "$OBSIDIAN/appearance.json" << 'EOF'
{
  "enabledCssSnippets": ["vault-colors"]
}
EOF

echo ""
echo "Setup complete."
echo ""
echo "Next steps:"
echo "  1. Open Obsidian"
echo "  2. Manage Vaults → Open folder as vault → select: $VAULT"
echo "  3. Install community plugins: Dataview, Templater, Obsidian Git"
echo "  4. Type /wiki in Claude Code to scaffold your knowledge base"
echo ""
echo "Graph view will show only wiki pages, color-coded by type."
echo "If colors reset after closing Obsidian: open Graph settings → Color groups"
echo "and re-add them once. After that, they persist permanently."
