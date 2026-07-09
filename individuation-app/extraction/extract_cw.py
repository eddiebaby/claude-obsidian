#!/usr/bin/env python3
"""extract_cw.py — paragraph-anchored extraction of Jung's Collected Works.

Input: a digital-edition CW PDF whose text layer carries the Bollingen
paragraph numbers as bracketed markers on their own line ([315]).

Output (JSONL, UTF-8):
  paragraphs.jsonl — one record per numbered paragraph:
    {volume, para, essay, section, pdf_page, text}
  chunks.jsonl — retrieval chunks (consecutive paragraphs, essay-bounded):
    {volume, essay, section, para_start, para_end, pdf_page, header, text}

The `header` field is the contextual prefix for embedding/BM25
("CW 8 — On the Nature of Dreams — paras. 530-533") and doubles as the
citation string shown to the app user.

Known noise accepted in v0:
  - inline footnote reference numbers stuck to words ("substance.53")
  - footnote bodies at essay end may be appended to the final paragraph

Usage:
  python extract_cw.py <pdf> --volume "CW 8" [--out-dir ../data/cw8]
                             [--target-tokens 700] [--max-tokens 1100]
"""

import argparse
import json
import re
import sys
import unicodedata
from bisect import bisect_right
from pathlib import Path

import fitz  # PyMuPDF

# marker alone on its own line (CW 8 conversion) or at line start with the
# paragraph text following on the same line (CW 9i conversion)
PARA_MARKER = re.compile(r"^\[(\d{1,4})\]\s*(.*)$")
PAGE_NUMBER_LINE = re.compile(r"^\d{1,4}$")
ROMAN_ONLY = re.compile(r"^[IVXLC]+\.?$")
FRONT_MATTER = re.compile(
    r"cover|title page|copyright|editorial|translator|contents|"
    r"about the author|index$|bibliography",
    re.IGNORECASE,
)
# chars-per-token heuristic; good enough for chunk sizing
CHARS_PER_TOKEN = 4


def clean_line(line: str) -> str:
    line = unicodedata.normalize("NFC", line).strip()
    return line


def essay_breakpoints(doc):
    """Return ([(pdf_page, essay, section)], stop_page) from the built-in TOC.

    Level-1 roman-numeral entries are part dividers, not essays; the
    essays under them appear at level 2. Deeper levels are sections.
    stop_page is where back matter (index/bibliography) begins — bracketed
    numbers there are list entries, not paragraph markers.
    """
    breaks = []
    stop_page = None
    essay = None
    section = None
    parent_is_part = False
    for level, title, page in doc.get_toc():
        title = clean_line(title)
        if FRONT_MATTER.search(title):
            if re.search(r"index|bibliography", title, re.IGNORECASE) and breaks:
                stop_page = page if stop_page is None else min(stop_page, page)
            continue
        if level == 1:
            if ROMAN_ONLY.match(title):
                parent_is_part = True
                continue
            parent_is_part = False
            essay, section = title, None
        elif level == 2:
            if parent_is_part:
                essay, section = title, None
            else:
                section = title
        else:
            section = title
        breaks.append((page, essay, section))
    return breaks, stop_page


def extract_lines(doc):
    """Yield (pdf_page, line) for every non-furniture line."""
    for pno in range(doc.page_count):
        lines = doc[pno].get_text().split("\n")
        # drop trailing bare page-number lines
        while lines and (not lines[-1].strip() or PAGE_NUMBER_LINE.match(lines[-1].strip())):
            lines.pop()
        for raw in lines:
            line = clean_line(raw)
            if line:
                yield pno + 1, line  # 1-based to match TOC pages


def join_lines(lines):
    """Rejoin hard-wrapped lines; undo end-of-line hyphenation."""
    out = ""
    for line in lines:
        if not out:
            out = line
        elif out.endswith("-") and line[:1].islower():
            out = out[:-1] + line
        else:
            out += " " + line
    return re.sub(r"\s+", " ", out).strip()


def extract_paragraphs(doc, volume):
    breaks, stop_page = essay_breakpoints(doc)
    break_pages = [b[0] for b in breaks]

    def locate(page):
        i = bisect_right(break_pages, page) - 1
        return breaks[i][1], breaks[i][2] if i >= 0 else (None, None)

    paragraphs = []
    current = None  # {para, pdf_page, lines}
    for page, line in extract_lines(doc):
        if stop_page is not None and page >= stop_page:
            break
        m = PARA_MARKER.match(line)
        if m:
            if current:
                paragraphs.append(current)
            rest = m.group(2).strip()
            current = {
                "para": int(m.group(1)),
                "pdf_page": page,
                "lines": [rest] if rest else [],
            }
        elif current:
            current["lines"].append(line)
    if current:
        paragraphs.append(current)

    records = []
    for p in paragraphs:
        essay, section = locate(p["pdf_page"])
        text = join_lines(p["lines"])
        if not text:
            continue
        records.append(
            {
                "volume": volume,
                "para": p["para"],
                "essay": essay,
                "section": section,
                "pdf_page": p["pdf_page"],
                "text": text,
            }
        )
    return records


def validate(records):
    """Print extraction diagnostics; return list of warning strings."""
    warnings = []
    if not records:
        return ["no paragraphs extracted"]
    paras = [r["para"] for r in records]
    print(f"paragraphs: {len(records)}  range: {paras[0]}..{paras[-1]}")

    non_monotonic = [
        (a, b) for a, b in zip(paras, paras[1:]) if b <= a
    ]
    if non_monotonic:
        warnings.append(f"{len(non_monotonic)} non-monotonic para transitions: {non_monotonic[:10]}")
    gaps = [(a, b) for a, b in zip(paras, paras[1:]) if b - a > 1]
    if gaps:
        warnings.append(f"{len(gaps)} numbering gaps (first 10): {gaps[:10]}")

    by_essay = {}
    for r in records:
        by_essay.setdefault(r["essay"], []).append(r["para"])
    print("\nessay -> para range")
    for essay, ps in by_essay.items():
        print(f"  {str(essay)[:60]:60s} paras. {min(ps)}-{max(ps)}  ({len(ps)})")

    tiny = [r["para"] for r in records if len(r["text"]) < 40]
    if tiny:
        warnings.append(f"{len(tiny)} suspiciously short paragraphs (<40 chars): {tiny[:10]}")
    return warnings


def chunk(records, volume, target_tokens, max_tokens):
    """Group consecutive same-essay paragraphs into retrieval chunks."""
    chunks = []
    buf = []

    def flush():
        if not buf:
            return
        first, last = buf[0], buf[-1]
        span = (
            f"para. {first['para']}"
            if first["para"] == last["para"]
            else f"paras. {first['para']}-{last['para']}"
        )
        header = f"{volume} — {first['essay']} — {span}"
        chunks.append(
            {
                "volume": volume,
                "essay": first["essay"],
                "section": first["section"],
                "para_start": first["para"],
                "para_end": last["para"],
                "pdf_page": first["pdf_page"],
                "header": header,
                "text": "\n\n".join(f"[{r['para']}] {r['text']}" for r in buf),
            }
        )
        buf.clear()

    for r in records:
        r_tokens = len(r["text"]) // CHARS_PER_TOKEN
        buf_tokens = sum(len(b["text"]) for b in buf) // CHARS_PER_TOKEN
        if buf and (
            r["essay"] != buf[0]["essay"]
            or buf_tokens + r_tokens > max_tokens
            or buf_tokens >= target_tokens
        ):
            flush()
        buf.append(r)
    flush()
    return chunks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--volume", required=True, help='e.g. "CW 8"')
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--target-tokens", type=int, default=700)
    ap.add_argument("--max-tokens", type=int, default=1100)
    args = ap.parse_args()

    pdf = Path(args.pdf)
    out_dir = Path(args.out_dir) if args.out_dir else Path(__file__).parent.parent / "data" / args.volume.replace(" ", "").lower()
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf)
    records = extract_paragraphs(doc, args.volume)
    warnings = validate(records)

    chunks = chunk(records, args.volume, args.target_tokens, args.max_tokens)
    print(f"\nchunks: {len(chunks)}  (target {args.target_tokens} tok, max {args.max_tokens} tok)")

    with open(out_dir / "paragraphs.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out_dir / "chunks.jsonl", "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\nwrote {out_dir / 'paragraphs.jsonl'}")
    print(f"wrote {out_dir / 'chunks.jsonl'}")

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
