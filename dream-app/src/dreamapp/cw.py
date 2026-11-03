"""Search over the primary-text chunks in individuation-app/data/<source>/chunks.jsonl.

These are the citable evidence of design.md §1: every passage carries its `header`
("CW 8 — On the Nature of Dreams — paras. 560-564", or page-anchored for the seminar and
von Franz: "Dream Analysis — Lecture II, 14 November 1928 — pp. 16-17"), which the
synthesize prompt must cite. The header is also indexed as the chunk's contextual prefix. The data is
derived from copyrighted PDFs and gitignored, so a checkout without it degrades to
no CW passages rather than failing.
"""
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import config

_STOP = {"the", "and", "for", "that", "this", "with", "was", "are", "but", "not", "his", "her", "its", "from",
         "they", "have", "has", "had", "which", "who", "what", "when", "there", "their", "them", "into", "than",
         "then", "also", "been", "were", "one", "all", "can", "would", "could", "about", "only", "very", "such",
         "you", "your", "she", "him", "our", "out", "over", "more", "some", "any", "same", "even", "just", "like"}
K1, B = 1.5, 0.75


@dataclass
class CWPassage:
    """A chunk of Jung's own text. CW volumes anchor by paragraph; the seminars, which have none, by page."""
    header: str
    volume: str
    text: str
    score: float
    para_start: Optional[int] = None
    para_end: Optional[int] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None


def _tokens(text: str) -> list:
    return [t for t in re.findall(r"[a-z]+", text.lower()) if len(t) > 2 and t not in _STOP]


def load_chunks(data_dir) -> list:
    """Every chunk from every source; a corrupt line (an interrupted re-extraction) is skipped, not fatal."""
    chunks = []
    for path in sorted(Path(data_dir).glob("*/chunks.jsonl")):
        bad = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            if "header" in chunk and "text" in chunk:
                chunks.append(chunk)
            else:
                bad += 1
        if bad:
            print(f"cw: skipped {bad} unreadable line{'s' if bad > 1 else ''} in {path}", file=sys.stderr)
    return chunks


class _Index:
    def __init__(self, chunks):
        self.chunks = chunks
        self.docs = [Counter(_tokens(f"{c['header']} {c['text']}")) for c in chunks]
        self.lengths = [sum(d.values()) for d in self.docs]
        self.avg = sum(self.lengths) / len(self.lengths) if self.lengths else 0
        df = Counter(t for d in self.docs for t in d)
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: str) -> list:
        q = set(_tokens(query))
        out = []
        for doc, length in zip(self.docs, self.lengths):
            s = 0.0
            for t in q & doc.keys():
                tf = doc[t]
                s += self.idf[t] * tf * (K1 + 1) / (tf + K1 * (1 - B + B * length / self.avg))
            out.append(s)
        return out


_CACHE = {}


def _index(data_dir) -> _Index:
    key = str(Path(data_dir).resolve())
    if key not in _CACHE:
        _CACHE[key] = _Index(load_chunks(data_dir))
    return _CACHE[key]


def search(queries, top_k: int = None, data_dir=None) -> list:
    """Best-scoring CW chunks across all queries, each chunk once, zero-score hits dropped."""
    data_dir = Path(data_dir or config.CW_DATA_DIR)
    top_k = top_k or config.MAX_CW_CHUNKS
    if not any(data_dir.glob("*/chunks.jsonl")):
        print(f"cw: CW corpus not found at {data_dir}; continuing without CW passages "
              "(run individuation-app/extraction/extract_cw.py or extract_seminar.py)", file=sys.stderr)
        return []
    idx = _index(data_dir)
    best = {}
    for query in queries:
        for i, s in enumerate(idx.scores(query)):
            if s > best.get(i, 0.0):
                best[i] = s
    ranked = sorted(best.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    out = []
    for i, s in ranked:
        c = idx.chunks[i]
        out.append(CWPassage(header=c["header"], volume=c.get("volume", ""), text=c["text"], score=round(s, 3),
                             para_start=c.get("para_start"), para_end=c.get("para_end"),
                             page_start=c.get("page_start"), page_end=c.get("page_end")))
    return out
