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

MODEL_EXTRACT = os.environ.get("DREAMAPP_MODEL_EXTRACT", "claude-haiku-4-5-20251001")
MODEL_SYNTH = os.environ.get("DREAMAPP_MODEL_SYNTH", "claude-sonnet-5")

TOP_K_PER_SYMBOL = 3
MAX_SYMBOLS = 10
MIN_SALIENCE_FOR_RETRIEVAL = 3
MAX_UNIQUE_PAGES = 8
MAX_CHARS_PER_PAGE = 6000
MAX_DREAM_CHARS = 8000


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
