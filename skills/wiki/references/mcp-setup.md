# MCP Setup

MCP lets Claude read and write vault notes directly without copy-paste. Two options.

---

## Step 1: Install the Local REST API Plugin

You must do this in Obsidian (Claude cannot do it programmatically):

1. Obsidian > Settings > Community Plugins > Turn off Restricted Mode
2. Browse > Search "Local REST API" > Install > Enable
3. Settings > Local REST API > Copy the API key

The plugin runs on `https://127.0.0.1:27124` with a self-signed certificate.

Test it:
```bash
curl -sk -H "Authorization: Bearer <YOUR_KEY>" https://127.0.0.1:27124/
```

You should get a JSON response with vault info.

---

## Option A: mcp-obsidian (REST API based)

Uses MarkusPfundstein's mcp-obsidian. Requires the Local REST API plugin running.

```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "uvx",
  "args": ["mcp-obsidian"],
  "env": {
    "OBSIDIAN_API_KEY": "<YOUR_KEY>",
    "OBSIDIAN_HOST": "127.0.0.1",
    "OBSIDIAN_PORT": "27124",
    "NODE_TLS_REJECT_UNAUTHORIZED": "0"
  }
}' --scope user
```

`NODE_TLS_REJECT_UNAUTHORIZED: "0"` is required because the REST API uses a self-signed certificate.

Capabilities: read notes, write notes, search, patch frontmatter fields, append under headings.

---

## Option B: MCPVault (filesystem based)

No Obsidian plugin needed. Reads the vault directory directly.

```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@bitbonsai/mcpvault@latest", "/absolute/path/to/your/vault"]
}' --scope user
```

Replace `/absolute/path/to/your/vault` with the actual vault path.

Tools available: `search_notes` (BM25), `read_note`, `create_note`, `update_note`, `get_frontmatter`, `update_frontmatter`, `list_all_tags`, `read_multiple_notes`.

---

## Option C: Direct REST API via curl

No MCP needed. Use curl in bash throughout the session. See `rest-api.md` for all commands.

---

## Use `--scope user`

Both MCP options use `--scope user` so the vault is available across all Claude Code projects, not just the one where you ran the command.

---

## Verification

After setup:

```bash
claude mcp list               # confirm the server appears
claude mcp get obsidian-vault # confirm the path or URL is correct
```

In a Claude Code session, type `/mcp` to check connection status.

Then test: "List all notes in my wiki folder."
