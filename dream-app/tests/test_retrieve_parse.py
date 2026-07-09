import json
from unittest.mock import patch

import pytest

from dreamapp import config
from dreamapp.models import Symbol
from dreamapp.retrieve import RetrievalNotProvisioned, retrieve_passages

def _canned_stdout(absolute_path: str) -> str:
    return json.dumps({
        "query": "milk nourishment vessel mother",
        "strategy": "bm25+rerank",
        "top_k": 3,
        "candidates": [
            {
                "chunk_id": "c1", "page_address": "a1", "page_path": "wiki/concepts/Vessel-Symbol.md",
                "absolute_path": absolute_path, "chunk_index": 0, "bm25_score": 1.1,
                "rerank_score": 0.9, "rerank_source": "cosine", "snippet": "milk as vessel...",
                "path": "wiki/concepts/Vessel-Symbol.md",
            },
            {
                "chunk_id": "c2", "page_address": "a2", "page_path": "wiki/concepts/Vessel-Symbol.md",
                "absolute_path": absolute_path, "chunk_index": 1, "bm25_score": 0.8,
                "rerank_score": 0.5, "rerank_source": "cosine", "snippet": "lower scoring chunk...",
                "path": "wiki/concepts/Vessel-Symbol.md",
            },
            {
                "chunk_id": "c3", "page_address": "a3", "page_path": "wiki/concepts/Mother-Archetype.md",
                "absolute_path": absolute_path, "chunk_index": 0, "bm25_score": 1.0,
                "rerank_score": 0.7, "rerank_source": "cosine", "snippet": "mother archetype...",
                "path": "wiki/concepts/Mother-Archetype.md",
            },
        ],
    })


class _FakeResult:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_dedupe_keeps_highest_score(tmp_path):
    page_file = tmp_path / "page.md"
    page_file.write_text("---\ntitle: x\n---\nActual body text.", encoding="utf-8")
    stdout = _canned_stdout(str(page_file))

    with patch("dreamapp.retrieve.subprocess.run", return_value=_FakeResult(0, stdout=stdout)):
        symbols = [Symbol(image="milk", kind="archetypal", salience=5, query="milk nourishment")]
        passages = retrieve_passages(symbols)

    by_path = {p.page_path: p for p in passages}
    assert len(by_path) == 2
    assert by_path["wiki/concepts/Vessel-Symbol.md"].score == 0.9  # kept highest of c1/c2
    assert "Actual body text." in by_path["wiki/concepts/Vessel-Symbol.md"].page_text
    assert "title: x" not in by_path["wiki/concepts/Vessel-Symbol.md"].page_text  # frontmatter stripped


def test_below_min_salience_skipped():
    with patch("dreamapp.retrieve.subprocess.run") as mock_run:
        symbols = [Symbol(image="scenery", kind="ambiguous", salience=1, query="incidental")]
        passages = retrieve_passages(symbols)
    mock_run.assert_not_called()
    assert passages == []


def test_exit_10_raises_not_provisioned():
    with patch("dreamapp.retrieve.subprocess.run", return_value=_FakeResult(10)):
        symbols = [Symbol(image="milk", kind="archetypal", salience=5, query="milk")]
        with pytest.raises(RetrievalNotProvisioned):
            retrieve_passages(symbols)


def test_max_unique_pages_cap(tmp_path, monkeypatch):
    page_file = tmp_path / "page.md"
    page_file.write_text("body", encoding="utf-8")
    candidates = [
        {
            "chunk_id": f"c{i}", "page_address": f"a{i}", "page_path": f"wiki/concepts/P{i}.md",
            "absolute_path": str(page_file), "chunk_index": 0, "bm25_score": 1.0,
            "rerank_score": float(i), "rerank_source": "cosine", "snippet": "s",
            "path": f"wiki/concepts/P{i}.md",
        }
        for i in range(20)
    ]
    stdout = json.dumps({"query": "q", "strategy": "s", "top_k": 20, "candidates": candidates})
    monkeypatch.setattr(config, "MAX_UNIQUE_PAGES", 8)

    with patch("dreamapp.retrieve.subprocess.run", return_value=_FakeResult(0, stdout=stdout)):
        symbols = [Symbol(image="x", kind="ambiguous", salience=5, query="q")]
        passages = retrieve_passages(symbols)

    assert len(passages) == 8
    assert passages[0].score == 19.0  # highest score kept first
