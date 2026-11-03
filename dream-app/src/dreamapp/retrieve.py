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


def _reranked(candidate: dict) -> bool:
    return str(candidate.get("rerank_source", "")).startswith("cosine")


def _score(candidate: dict, use_rerank: bool) -> float:
    # Without the embedding model the reranker is a no-op that scores every hit 0.0;
    # the BM25 score is then the only signal that ranks hits across symbols. One basis per run:
    # a hit that missed the rerank (embed-error) keeps BM25 ~5-10, which would jump cosine hits (<1).
    if use_rerank:
        return candidate.get("rerank_score", 0.0) if _reranked(candidate) else 0.0
    return candidate.get("bm25_score", candidate.get("rerank_score", 0.0))


def _is_dream_entry(page_path: str) -> bool:
    # The dreamer's own journal is the series, not corpus: citing it as amplification
    # would pass his own past dreams off as Jung.
    return page_path.replace("\\", "/").startswith("wiki/dreams/")


def retrieve_passages(symbols: list) -> list:
    """symbols: list[Symbol]. Returns list[Passage], deduped by page_path, top MAX_UNIQUE_PAGES by score."""
    per_query = []
    for symbol in symbols:
        if symbol.salience < config.MIN_SALIENCE_FOR_RETRIEVAL:
            continue
        # over-fetch: the dreamer's own entries are the vault's densest text on his imagery and would
        # fill the top slots, then be dropped below with nothing behind them
        candidates = _run_query(symbol.query, config.TOP_K_PER_SYMBOL + config.DREAM_PAGE_OVERFETCH)
        per_query.append([c for c in candidates if not _is_dream_entry(c["page_path"])][: config.TOP_K_PER_SYMBOL])

    use_rerank = any(_reranked(c) for cands in per_query for c in cands)
    best_by_page = {}
    for cands in per_query:
        for candidate in cands:
            existing = best_by_page.get(candidate["page_path"])
            if existing is None or _score(candidate, use_rerank) > _score(existing, use_rerank):
                best_by_page[candidate["page_path"]] = candidate

    ranked = sorted(best_by_page.values(), key=lambda c: _score(c, use_rerank), reverse=True)
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
                score=_score(c, use_rerank),
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
