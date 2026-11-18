import os
from pathlib import Path


def _find_vault_root() -> Path:
    d = Path(__file__).resolve().parent
    for _ in range(6):
        if (d / ".vault-meta").is_dir() and (d / "CLAUDE.md").is_file():
            return d
        d = d.parent
    raise RuntimeError(
        "Could not locate vault root (dir containing .vault-meta/ and CLAUDE.md) "
        "within 6 levels of dream-app/src/dreamapp/config.py"
    )


VAULT_ROOT = _find_vault_root()
RETRIEVE_SCRIPT = VAULT_ROOT / "scripts" / "retrieve.py"
LOCK_SCRIPT = VAULT_ROOT / "scripts" / "wiki-lock.sh"
DREAMS_DIR = VAULT_ROOT / "wiki" / "dreams"
CW_DATA_DIR = VAULT_ROOT / "individuation-app" / "data"

MODEL_EXTRACT = os.environ.get("DREAMAPP_MODEL_EXTRACT", "claude-haiku-4-5-20251001")
MODEL_SYNTH = os.environ.get("DREAMAPP_MODEL_SYNTH", "claude-sonnet-5")

TOP_K_PER_SYMBOL = 3
DREAM_PAGE_OVERFETCH = 10  # extra hits per query, so dropped wiki/dreams pages leave others behind
MAX_SYMBOLS = 10
MIN_SALIENCE_FOR_RETRIEVAL = 3
MAX_UNIQUE_PAGES = 8
MAX_CW_CHUNKS = 8
# the answer carries a counter-reading, method citations and up to ten amplifications
MAX_TOKENS_SYNTH = 8000
MAX_TOKENS_EXTRACT = 1500  # up to ten symbols of four short fields
# a few chunks (essay-final paragraphs with appended footnotes) run past 30,000 chars
MAX_CHARS_PER_CW_CHUNK = 6000
# Method paragraphs supplied on every run (cw.method_canon): which level to read a figure on
# (CW 8 ¶¶509, 515), compensation (¶545), the series (¶550), the patient's assent (CW 16 ¶316),
# every interpretation a hypothesis (CW 16 ¶322).
METHOD_CANON = (("CW 8", 509), ("CW 8", 515), ("CW 8", 545), ("CW 8", 550), ("CW 16", 316), ("CW 16", 322))
MAX_CHARS_PER_PAGE = 6000
MAX_DREAM_CHARS = 8000
# Series memory (series.py): earlier dreams sharing an image, sent with this one.
MAX_SERIES_PER_IMAGE = 3
# scripts/bench_series.py: with extraction's motifs, 8 found 47% of the earlier dreams the analyses named and
# 12 found 59%; the 12 most recent dreams found 34%
MAX_SERIES_DREAMS = 12
MAX_CHARS_SERIES_EXCERPT = 500
MAX_CHARS_SERIES_READING = 400  # the earlier compensation, and the dreamer's response to it


def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    env_file = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == "ANTHROPIC_API_KEY":
                v = v.strip()
                if v:
                    return v
    raise RuntimeError(
        "ANTHROPIC_API_KEY not set in environment and not found in dream-app/.env. "
        "Copy .env.example to .env and fill in your key, or export ANTHROPIC_API_KEY."
    )
