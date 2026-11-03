"""Shared by the extractors: atomic JSONL output, and the page-anchored pipeline
(extract_seminar.py, extract_vonfranz.py) for sources without paragraph numbers.

Page records: {source, section, page, pdf_page, text}, where section is the
citation label within the source ("Lecture II, 14 November 1928", "The Dream of
Socrates"). Chunks match extract_cw.py's shape with page_start/page_end in place
of para_start/para_end, so dreamapp/cw.py loads every source the same way.
"""

import json
import os
from collections import Counter
from pathlib import Path

from extract_cw import CHARS_PER_TOKEN

MIN_PAGE_CHARS = 60
_DIGIT_FIX = str.maketrans({"I": "1", "i": "1", "l": "1", "O": "0", "o": "0", "g": "9"})


def write_jsonl(path, rows):
    """Write rows atomically: dreamapp reads every chunks.jsonl, so a half-written file must never be visible."""
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
    print(f"wrote {path}")


def page_offset(pairs) -> int:
    """Most common (pdf page - printed number) over (pdf_page, page-number text) pairs."""
    gaps = Counter()
    for pdf_page, text in pairs:
        digits = text.strip().translate(_DIGIT_FIX)
        if digits.isdigit():
            gaps[pdf_page - int(digits)] += 1
    if not gaps:
        raise ValueError("no printed page numbers found")
    return gaps.most_common(1)[0][0]


def mend_page_breaks(pages):
    """Pull a word hyphenated across a page break back onto the page it starts on."""
    pages = [dict(p) for p in pages]
    for a, b in zip(pages, pages[1:]):
        consecutive = b["page"] == a["page"] + 1 and b["section"] == a["section"] and " " in b["text"]
        if consecutive and a["text"].endswith("-") and b["text"][:1].islower():
            first, _, rest = b["text"].partition(" ")
            a["text"] = a["text"][:-1] + first
            b["text"] = rest
    return pages


def chunk_pages(pages, target_tokens, max_tokens):
    """Group consecutive pages of one section into retrieval chunks."""
    chunks, buf = [], []

    def flush():
        if not buf:
            return
        first, last = buf[0], buf[-1]
        span = f"p. {first['page']}" if first["page"] == last["page"] else f"pp. {first['page']}-{last['page']}"
        chunks.append({
            "volume": first["source"],
            "essay": first["section"],
            "section": None,
            "page_start": first["page"],
            "page_end": last["page"],
            "pdf_page": first["pdf_page"],
            "header": f"{first['source']} — {first['section']} — {span}",
            "text": "\n\n".join(f"[p. {p['page']}] {p['text']}" for p in buf),
        })
        buf.clear()

    for p in pages:
        p_tokens = len(p["text"]) // CHARS_PER_TOKEN
        buf_tokens = sum(len(b["text"]) for b in buf) // CHARS_PER_TOKEN
        if buf and (p["section"] != buf[0]["section"]
                    or buf_tokens + p_tokens > max_tokens or buf_tokens >= target_tokens):
            flush()
        buf.append(p)
    flush()
    return chunks


def validate_pages(pages, offset):
    """Print extraction diagnostics; return warning strings."""
    if not pages:
        return ["no pages extracted"]
    print(f"pages: {len(pages)}  printed {pages[0]['page']}..{pages[-1]['page']}  (pdf offset {offset})")
    warnings = []
    nums = [p["page"] for p in pages]
    gaps = [(a, b) for a, b in zip(nums, nums[1:]) if b - a != 1]
    if gaps:
        warnings.append(f"{len(gaps)} page-sequence breaks: {gaps[:10]}")
    sections = []
    for p in pages:
        if not sections or sections[-1][0] != p["section"]:
            sections.append([p["section"], p["page"]])
    print(f"\nsections: {len(sections)}")
    for section, start in sections:
        print(f"  p. {start:>3}  {section}")
    undated = [p["lecture"] for p in pages if "date" in p and not p["date"]]
    if undated:
        warnings.append(f"{len(set(undated))} lectures without a parsed date: {sorted(set(undated))}")
    thin = [p["page"] for p in pages if len(p["text"]) < 200]
    if thin:
        warnings.append(f"{len(thin)} pages under 200 chars: {thin[:15]}")
    return warnings


def run_page_extractor(extract_pages, pdf, out_dir, target_tokens, max_tokens):
    """extract -> mend -> validate -> chunk -> write, for a page-anchored source."""
    import fitz  # PyMuPDF

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pages, offset = extract_pages(fitz.open(pdf))
    pages = mend_page_breaks(pages)
    warnings = validate_pages(pages, offset)
    chunks = chunk_pages(pages, target_tokens, max_tokens)
    print(f"\nchunks: {len(chunks)}  (target {target_tokens} tok, max {max_tokens} tok)\n")
    write_jsonl(out_dir / "pages.jsonl", pages)
    write_jsonl(out_dir / "chunks.jsonl", chunks)
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  - {w}")
