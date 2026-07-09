---
name: dream-app-build-spec
type: spec
title: "Dream App — Build Spec (implementation contract)"
domain: business
created: 2026-07-01
updated: 2026-07-01
status: draft
tags:
  - project
  - dream-app
  - spec
  - implementation
related:
  - "[[dream-app-prd]]"
  - "[[dream-app-phase0-spec]]"
---

# Dream App Build Spec

**Audience: a coding agent (Claude Code) implementing Phase 0.** This is the contract. Follow it exactly. Where this file and [[dream-app-phase0-spec]] disagree, this file wins (it was verified against the actual vault on 2026-07-01). When something is ambiguous, choose the simplest implementation that passes the acceptance checks in §12.

## 1. Ground rules for the implementing agent

1. Build ONLY inside `<vault-root>/dream-app/`. The only files you may write outside it are dream notes in `wiki/dreams/` via Stage 4.
2. NEVER modify: `scripts/`, `bin/`, `_templates/`, `.raw/`, `.vault-meta/`, any existing wiki page outside `wiki/dreams/`, or any existing content in a dream note above the `## Jungian Analysis` heading.
3. Dependencies: `anthropic`, `python-frontmatter`, `pyyaml`, `pytest` (dev). Nothing else. No pydantic, no dotenv, no web framework, no vector DB, no async.
4. Python 3.10+ compatible syntax. Use stdlib `dataclasses`, `json`, `subprocess`, `argparse`, `pathlib`.
5. This machine is Windows. Shell out to vault scripts with `sys.executable` for Python and `bash` for `.sh` (Git Bash). Treat bash as possibly absent (see §9 locking).
6. Do not invent features. No Streamlit, no config file formats, no plugin hooks, no logging frameworks (stdlib `logging` at INFO to stderr is fine).
7. Keep every module under ~150 lines. Pure functions where possible; API calls isolated in `extract.py` and `synthesize.py` only.

## 2. Environment

- Vault root: the directory containing `CLAUDE.md` and `.vault-meta/`. Resolve by walking up from the package directory (§4 config contract).
- `ANTHROPIC_API_KEY`: read from environment first; if absent, parse `dream-app/.env` (simple `KEY=VALUE` lines, no dependency). Error clearly if neither.
- Retrieval must be provisioned once before first run: `bash bin/setup-retrieve.sh` (if chunks are missing it will say so; `python3 scripts/contextual-prefix.py --all` builds them). The app does NOT provision; it detects exit 10 and tells the user (§6).

## 3. Package layout (exact)

```
dream-app/
  pyproject.toml            # [project] name dreamapp, deps from §1.3, [project.scripts] dreamapp = "dreamapp.cli:main"
  .env.example              # ANTHROPIC_API_KEY=sk-ant-...
  .gitignore                # .env, __pycache__, *.egg-info
  README.md                 # 20 lines max: install, provision retrieval, usage
  src/dreamapp/
    __init__.py
    config.py
    models.py
    extract.py
    retrieve.py
    synthesize.py
    writeback.py
    pipeline.py
    cli.py
    prompts/
      extract.md
      synthesize.md
  tests/
    fixtures/
      dream_simple.txt      # 5-10 line invented dream, plain text
      dream_note.md         # copy of a real note from wiki/dreams/ (any one)
    test_models.py
    test_retrieve_parse.py
    test_writeback.py
    test_pipeline.py        # marked skip-unless ANTHROPIC_API_KEY set
```

## 4. config.py contract

```python
VAULT_ROOT: Path      # walk up from __file__ until a dir containing ".vault-meta" and "CLAUDE.md"; error after 6 levels
RETRIEVE_SCRIPT = VAULT_ROOT / "scripts" / "retrieve.py"
LOCK_SCRIPT     = VAULT_ROOT / "scripts" / "wiki-lock.sh"
DREAMS_DIR      = VAULT_ROOT / "wiki" / "dreams"
MODEL_EXTRACT   = os.environ.get("DREAMAPP_MODEL_EXTRACT", "claude-haiku-4-5-20251001")
MODEL_SYNTH     = os.environ.get("DREAMAPP_MODEL_SYNTH", "claude-sonnet-5")
TOP_K_PER_SYMBOL = 3      # retrieve.py --top
MAX_SYMBOLS      = 10     # hard cap after extraction
MIN_SALIENCE_FOR_RETRIEVAL = 3
MAX_UNIQUE_PAGES = 8      # context cap across all symbols
MAX_CHARS_PER_PAGE = 6000 # truncate page text fed to synthesis
MAX_DREAM_CHARS  = 8000   # reject longer input with exit 2
```

Model IDs are env-overridable; if an API call returns a model-not-found error, say so and point at `DREAMAPP_MODEL_*` env vars. Do not silently substitute models.

## 5. models.py contract (stdlib dataclasses)

```python
@dataclass
class Symbol:
    image: str            # as it appeared: "overflowing gallon of milk"
    kind: str             # "personal" | "archetypal" | "ambiguous"
    salience: int         # 1-5
    query: str            # retrieval query, e.g. "milk vessel nourishment mother"

@dataclass
class Passage:
    page_path: str        # vault-relative, e.g. "wiki/concepts/Vessel-Symbol.md"
    absolute_path: str
    snippet: str          # from retrieve.py (200 chars)
    score: float          # rerank_score
    page_text: str = ""   # filled by our bridge: full page, truncated to MAX_CHARS_PER_PAGE

@dataclass
class Amplification:
    symbol: str
    corpus_says: str      # grounded in supplied passages ONLY
    personal_reading: str
    archetypal_reading: str
    thin_coverage: bool   # True when passages gave little or nothing for this symbol

@dataclass
class Interpretation:
    dramatic_structure: str   # exposition / development / culmination / lysis, one short paragraph
    compensation: str
    amplifications: list[Amplification]
    objective_level: str
    subjective_level: str
    movement: str             # movement toward individuation
    question: str             # the single question the dream poses
    sources: list[str]        # page_paths actually cited
```

Each dataclass gets `to_dict()` / `from_dict()` (plain json-compatible). JSON parsing of model output lives in one helper: `parse_model_json(text) -> dict` which strips markdown fences and retries `json.loads` on the largest `{...}` span before failing.

## 6. Stage 2 first: retrieve.py bridge (`retrieve.py` in package)

Build and verify this stage BEFORE stages 1 and 3 (retrieval quality gates everything).

Call (subprocess, no imports from vault scripts):

```python
subprocess.run([sys.executable, str(RETRIEVE_SCRIPT), query, "--top", "3"],
               capture_output=True, text=True, cwd=VAULT_ROOT)
```

Facts about `scripts/retrieve.py` (verified):

- JSON on **stdout**, progress logs on **stderr**. Parse stdout only.
- Exit 0 success; exit 2 usage; **exit 10 = not provisioned** → raise `RetrievalNotProvisioned` with the message: "Retrieval index missing. Run: bash bin/setup-retrieve.sh (then python3 scripts/contextual-prefix.py --all if chunks are missing)."
- Output schema: `{"query", "strategy", "top_k", "candidates": [{"chunk_id", "page_address", "page_path", "absolute_path", "chunk_index", "bm25_score", "rerank_score", "rerank_source", "snippet", "path"}]}`. It already dedupes pages within one query.
- Works without ollama (falls back to BM25 order). Never require ollama.

Bridge behavior:

1. For each Symbol with `salience >= MIN_SALIENCE_FOR_RETRIEVAL`, run one query.
2. Merge candidates across symbols; dedupe by `page_path`, keeping highest `rerank_score`.
3. Sort by score, keep top `MAX_UNIQUE_PAGES`.
4. For each kept page, read `absolute_path`, strip YAML frontmatter, truncate to `MAX_CHARS_PER_PAGE`, store in `page_text`. Skip unreadable files with a stderr warning.
5. Return `list[Passage]`. Empty list is valid (synthesis must then flag thin coverage everywhere).

## 7. Stage 1: extract.py

One Claude call. `MODEL_EXTRACT`, `max_tokens=1500`, `temperature=0`. System prompt = `prompts/extract.md` verbatim. User content = raw dream text.

Post-processing: parse JSON; coerce salience to int and clamp 1-5; drop symbols with empty `image`; cap at `MAX_SYMBOLS` by salience desc. On parse failure after the §5 repair helper: ONE reprompt appending "Return ONLY the JSON array, no prose." Then fail with exit 4.

**Full contents of `prompts/extract.md`:**

```markdown
You extract salient symbols from a dream for a Jungian analysis pipeline. You are a router, not an interpreter. Do not interpret.

Return ONLY a JSON array. Each element:
{
  "image": "the symbol exactly as it appears in the dream, short noun phrase",
  "kind": "personal" | "archetypal" | "ambiguous",
  "salience": 1-5,
  "query": "3-6 word retrieval query for a Jung corpus"
}

Rules:
- 3 to 10 symbols. Prefer fewer, more salient ones.
- salience 5 = the dream's central image or point of highest affect; 1 = incidental scenery.
- kind: "personal" when the image is tied to the dreamer's named people, places, or biography (an ex, a childhood home). "archetypal" when the image carries collective/mythic weight independent of biography (snake, flood, wise old man, milk, court/judgment). "ambiguous" when genuinely both. When unsure, "ambiguous".
- query: generalize the image toward its symbolic family so corpus retrieval works. "half-drunk gallon of milk" -> "milk nourishment vessel mother". "my brother Dave" -> "brother shadow sibling figure". Do not include the dreamer's private names in queries.
- Include figures (people, animals, entities) as symbols too.
- No commentary, no markdown fences, JSON only.
```

## 8. Stage 3: synthesize.py

One Claude call. `MODEL_SYNTH`, `max_tokens=4000`, `temperature=0.3`. System prompt = `prompts/synthesize.md` verbatim.

User message layout (exact order):

```
<dream>
{raw dream text}
</dream>

<symbols>
{JSON array of extracted Symbols}
</symbols>

<corpus>
<page path="wiki/concepts/Foo.md">
{page_text}
</page>
... one block per Passage ...
</corpus>
```

If `<corpus>` is empty, still run; the prompt handles it. Output: single JSON object matching `Interpretation.to_dict()`. Same parse/repair/reprompt policy as Stage 1. Validate: `sources` may only contain `page_path` values that were actually supplied; strip any others (this is the anti-confabulation check).

**Full contents of `prompts/synthesize.md`:**

```markdown
You produce a Jungian dream interpretation for a reader who knows Jung's concepts thoroughly. Never define terms (shadow, anima, compensation). Never moralize. Never soften with wellness language.

Ground rules:
1. GROUNDED OR SILENT. Amplifications draw ONLY on the corpus passages supplied in <corpus>. If the corpus is thin or silent on a symbol, set "thin_coverage": true and say plainly what is missing instead of inventing material. Do not use general knowledge as a substitute for the corpus; you may use it only to connect supplied passages coherently.
2. Method order: dramatic structure first (exposition, development, culmination, lysis), then the compensatory function (what conscious attitude is this dream balancing or correcting), then amplification per symbol, personal associations BEFORE archetypal parallels, then the two levels (objective: figures as the real people/things; subjective: every figure as a part of the dreamer), then movement toward individuation.
3. A QUESTION, NOT A VERDICT. The interpretation ends with the single question the dream is asking the dreamer to sit with. No predictions, no instructions, no diagnosis.
4. Non-obvious or nothing. If a point is something a careful reader would get from rereading the dream, cut it.
5. Cite: every claim that leans on the corpus names the page it came from. List cited pages in "sources" (vault-relative paths exactly as given in <corpus>).

Return ONLY a JSON object:
{
  "dramatic_structure": "...",
  "compensation": "...",
  "amplifications": [
    {"symbol": "...", "corpus_says": "...", "personal_reading": "...", "archetypal_reading": "...", "thin_coverage": false}
  ],
  "objective_level": "...",
  "subjective_level": "...",
  "movement": "...",
  "question": "...",
  "sources": ["wiki/concepts/Foo.md"]
}

No markdown fences, no prose outside the JSON.
```

## 9. Stage 4: writeback.py

Two input cases:

**Case A: input is an existing note in `wiki/dreams/`** (path is inside DREAMS_DIR, has frontmatter with `type: dream`): update in place.
**Case B: input is raw text** (any other file, or stdin): create a new note.

Case B file naming: `wiki/dreams/<date>-<slug>.md`. Date = `--date` flag or today. Slug = `--title` flag or first 5 meaningful words of the dream; lowercase, `[a-z0-9-]` only, max 40 chars. On collision append `-2`, `-3`.

Note structure (matches the vault's real template `_templates/dream.md`, NOT the "## Interpretation" heading mentioned in the phase0 spec):

- Frontmatter: `name`, `type: dream`, `title: "YYYY-MM-DD — <Title>"`, `date`, `created`, `updated`, `tags: [dream]`, `status: analyzed`, `mood:`, `sleep:`, `recurring: false`, `lucid: false`, `archetypes: [...]`, `symbols: [...]`, `related: [...]`.
- `symbols:` = kebab-case of each Symbol.image (e.g. `half-drunk-gallon` style, match the existing notes).
- `archetypes:` = lowercase archetype names that appear in the interpretation's amplifications/archetypal readings (mother, shadow, persona, anima, animus, self, trickster, hero, wise-old-man...). Derive from Interpretation content; empty list is acceptable.
- `related:` = wikilinks for each source page: `"[[Vessel-Symbol]]"` (page filename stem, no path, no .md).
- Body for Case B: `# YYYY-MM-DD Dayname`, `## The Dream` (the raw text as given), empty `## Waking Associations`, `## Feeling-Tone`, `## Day Residue` sections, `---`, then the analysis section below.
- Analysis section (both cases), replacing/filling `## Jungian Analysis`:

```markdown
## Jungian Analysis

### Dramatic Structure
{dramatic_structure}

### Symbols & Amplification
{one bolded entry per amplification: **symbol** — corpus_says / personal / archetypal; append "(corpus thin here)" when thin_coverage}

### Archetypal Figures
{from amplifications with archetypal weight}

### Compensation / What the Unconscious Is Saying
{compensation, then objective_level and subjective_level as two short labeled paragraphs}

### Movement Toward Individuation
{movement}

### Open Questions
{question}

### Sources
{bulleted wikilinks of sources}
```

Case A hard rule: everything above `## Jungian Analysis` is preserved byte-for-byte except the frontmatter keys `status`, `updated`, `symbols`, `archetypes`, `related` (merge related, don't drop existing entries; same for existing symbols/archetypes: union, existing entries first). If the note already has non-empty analysis content under `## Jungian Analysis`, abort with exit 5 unless `--force` is passed.

Locking (vault convention): before writing, attempt `bash scripts/wiki-lock.sh acquire wiki/dreams/<file>.md` from VAULT_ROOT. Exit 0 = proceed; exit 75 = wait 5s, retry twice, then abort exit 5. If `bash` is not on PATH (Windows without Git Bash), log a warning and proceed without the lock. Always attempt `release` after writing (best-effort).

`--dry`: print the rendered note to stdout, write nothing, take no lock.

## 10. pipeline.py and cli.py

`pipeline.run(dream_text, source_path=None, dry=False, show_sources=False, force=False, title=None, date=None) -> Interpretation`

Order: extract → retrieve → synthesize → writeback. Print progress lines to stderr ("extract: 6 symbols", "retrieve: 5 pages", ...).

CLI:

```
dreamapp interpret <file|->  [--dry] [--show-sources] [--force] [--title "..."] [--date YYYY-MM-DD]
```

`-` reads stdin. `--show-sources` prints the retrieved page list with scores before the interpretation. Exit codes: 0 ok; 2 bad input (missing file, dream > MAX_DREAM_CHARS, bad date); 3 retrieval not provisioned; 4 model/API failure (after 2 retries with exponential backoff on 429/5xx and one JSON reprompt); 5 writeback/lock failure.

## 11. Tests

- `test_models.py`: round-trip to_dict/from_dict; `parse_model_json` on fenced, prefixed, and clean JSON.
- `test_retrieve_parse.py`: bridge parsing against a canned retrieve.py stdout fixture (embed the §6 schema as a string); exit-10 handling raises `RetrievalNotProvisioned`. No live calls.
- `test_writeback.py`: Case B renders a full valid note into a tmp dir (frontmatter parses, headings present, slug/collision rules); Case A on `fixtures/dream_note.md` preserves the pre-analysis body byte-for-byte and unions frontmatter lists. No live calls.
- `test_pipeline.py`: end-to-end with `--dry` on `fixtures/dream_simple.txt`; `@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"))`. Asserts: valid Interpretation, every entry in `sources` was a supplied page, output contains no markdown fence artifacts.

## 12. Acceptance checks (run in order; each step is "done" only when its check passes)

| # | Step | Check |
|---|------|-------|
| 0 | Provision retrieval (human runs `bash bin/setup-retrieve.sh`) | `python scripts/retrieve.py "snake" --top 3` prints JSON with non-empty candidates |
| 1 | Scaffold + config | `pip install -e dream-app` succeeds; `python -c "from dreamapp.config import VAULT_ROOT; print(VAULT_ROOT)"` prints the vault root |
| 2 | Bridge | `python -m dreamapp.retrieve "milk"` (add a tiny `__main__`) prints deduped Passages for "milk", "court", "father"; exit-10 path prints the provisioning message |
| 3 | Extract | Running extract on `wiki/dreams/2026-06-30-court-and-overflowing-milk.md` body yields 3-10 symbols; symbols overlap sensibly with the note's hand-filled `symbols:` frontmatter |
| 4 | Synthesize | On the same dream: valid JSON; every source was supplied; at least one amplification cites a real page; thin_coverage appears when corpus is silent |
| 5 | Writeback | `--dry` renders a note that `python-frontmatter` parses; Case A test passes |
| 6 | End-to-end | `dreamapp interpret fixtures/dream_simple.txt --dry --show-sources` runs clean; then one real run writes a valid note to `wiki/dreams/` and the note opens in Obsidian with working wikilinks |
| 7 | Tests | `pytest dream-app/tests` green (live test may skip without API key) |

## 13. Out of scope: do not build

Streamlit/web UI, FastAPI, auth, payments, databases, embeddings stores, longitudinal/series analysis (Phase 1), prompt A/B harnesses, caching layers, Docker, CI. Do not "improve" `scripts/retrieve.py`. Do not add an LLM call anywhere except extract and synthesize.
