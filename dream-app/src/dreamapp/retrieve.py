import json
import subprocess
import sys

from . import config
from .models import Passage, Symbol

EXIT_NOT_PROVISIONED = 10


class RetrievalNotProvisioned(Exception):
    pass


def _run_query(query: str, top: int) -> list:
    result = subprocess.run(
        [sys.executable, str(config.RETRIEVE_SCRIPT), query, "--top", str(top)],
        capture_output=True,
        text=True,
        cwd=config.VAULT_ROOT,
    )
    if result.returncode == EXIT_NOT_PROVISIONED:
        raise RetrievalNotProvisioned(
            "Retrieval index missing. Run: bash bin/setup-retrieve.sh "
            "(then python3 scripts/contextual-prefix.py --all if chunks are missing)."
        )
    if result.returncode != 0:
        print(
            f"retrieve: query {query!r} failed (exit {result.returncode}): {result.stderr.strip()}",
            file=sys.stderr,
        )
        return []
    try:
        return json.loads(result.stdout).get("candidates", [])
    except json.JSONDecodeError:
        print(f"retrieve: could not parse stdout for query {query!r}", file=sys.stderr)
        return []


def _read_page_text(absolute_path: str) -> str:
    try:
        text = open(absolute_path, encoding="utf-8").read()
    except OSError as e:
        print(f"retrieve: could not read {absolute_path}: {e}", file=sys.stderr)
        return ""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
    return text.strip()[: config.MAX_CHARS_PER_PAGE]


def retrieve_passages(symbols: list) -> list:
    """symbols: list[Symbol]. Returns list[Passage], deduped by page_path, top MAX_UNIQUE_PAGES by score."""
    best_by_page = {}
    for symbol in symbols:
        if symbol.salience < config.MIN_SALIENCE_FOR_RETRIEVAL:
            continue
        for candidate in _run_query(symbol.query, config.TOP_K_PER_SYMBOL):
            page_path = candidate["page_path"]
            score = candidate["rerank_score"]
            existing = best_by_page.get(page_path)
            if existing is None or score > existing["rerank_score"]:
                best_by_page[page_path] = candidate

    ranked = sorted(best_by_page.values(), key=lambda c: c["rerank_score"], reverse=True)
    ranked = ranked[: config.MAX_UNIQUE_PAGES]

    passages = []
    for c in ranked:
        page_text = _read_page_text(c["absolute_path"])
        if not page_text:
            continue
        passages.append(
            Passage(
                page_path=c["page_path"],
                absolute_path=c["absolute_path"],
                snippet=c["snippet"],
                score=c["rerank_score"],
                page_text=page_text,
            )
        )
    return passages


def _main():
    if len(sys.argv) < 2:
        print("usage: python -m dreamapp.retrieve <query> [<query> ...]", file=sys.stderr)
        sys.exit(2)
    symbols = [Symbol(image=q, kind="ambiguous", salience=5, query=q) for q in sys.argv[1:]]
    try:
        passages = retrieve_passages(symbols)
    except RetrievalNotProvisioned as e:
        print(str(e), file=sys.stderr)
        sys.exit(EXIT_NOT_PROVISIONED)
    for p in passages:
        print(f"{p.page_path}\t{p.score:.3f}\t{p.snippet}")


if __name__ == "__main__":
    _main()
