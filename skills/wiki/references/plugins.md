# Obsidian Setup

---

## Install Obsidian

### Linux (Flatpak — recommended)

Check if installed:
```bash
flatpak list 2>/dev/null | grep -i obsidian && echo "FOUND via flatpak" || \
which obsidian 2>/dev/null && echo "FOUND in PATH" || echo "NOT FOUND"
```

Install if not found:
```bash
flatpak install flathub md.obsidian.Obsidian
```

### macOS

```bash
ls /Applications/Obsidian.app 2>/dev/null && echo "FOUND" || brew install --cask obsidian
```

### Windows

```powershell
Test-Path "$env:LOCALAPPDATA\Obsidian" && echo "FOUND" || winget install Obsidian.Obsidian
```

### All platforms: direct download

https://obsidian.md/download

---

## Open the Vault

After installing: Obsidian > Manage Vaults > Open Folder as Vault > select your vault directory.

---

## Recommended Plugins

Install via Settings > Community Plugins > Turn off Restricted Mode > Browse.

| Plugin | Purpose |
|--------|---------|
| **Dataview** | Query vault as a database. Powers dashboards in `wiki/meta/`. |
| **Templater** | Auto-populate frontmatter on note creation from `_templates/`. |
| **Obsidian Git** | Auto-commit every 15 minutes. Protects against bad writes. |
| **Iconize** | Visual folder icons for navigation. |
| **Minimal Theme** | Best dark theme for dense information display. |

Optional additions:
- **Smart Connections** — semantic search across all notes
- **QuickAdd** — macros for fast note creation
- **Folder Notes** — click a folder to open an overview note

---

## Web Clipper

The Obsidian Web Clipper browser extension converts web articles to markdown and sends them to `.raw/` in one click.

Install for Chrome, Firefox, or Safari from the Obsidian website.

Set the default folder to `.raw/` in the extension settings.

---

## After Installing Plugins

1. Enable Dataview: Settings > Community Plugins > toggle on
2. Enable Templater: Settings > Templater > set template folder to `_templates`
3. Enable Obsidian Git: Settings > Obsidian Git > Auto backup interval: 15 minutes
4. Enable the CSS snippet: Settings > Appearance > CSS Snippets > toggle on `vault-colors`
