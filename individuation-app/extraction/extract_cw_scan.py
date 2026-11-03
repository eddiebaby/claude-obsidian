#!/usr/bin/env python3
"""extract_cw_scan.py — paragraph-anchored extraction of a *scanned* CW volume (OCR text layer).

extract_cw.py handles digital editions, whose text carries "[315]" markers. A scan
(here CW 16) has the Bollingen paragraph numbers as separate OCR'd tokens in the
outer margin, level with each paragraph's first line, and the OCR misreads some of
them ("S03" for 302, "3l9" for 319) or loses them. So:

  - a margin token (short, left of the text column) opens a paragraph at the body
    line it sits level with
  - numbers come from the sequence, not the token alone: clean readings are trusted
    when they fit the run; between two of them, markers are numbered consecutively
    when the counts match, and from their OCR reading otherwise. A lost marker
    merges two paragraphs, so chunk ranges ("paras. 301-305") stay correct.
  - footnotes (~7.7pt median against ~10.4pt body), all-caps running heads and
    titles, and bottom-centre page numbers are dropped

Output matches extract_cw.py: paragraphs.jsonl and chunks.jsonl, in ../data/<volume>/.

Usage:
  python extract_cw_scan.py <pdf> --volume "CW 16" [--out-dir ../data/cw16]
                                  [--target-tokens 700] [--max-tokens 1100] [--paras 294-352]
"""

import argparse
import re
import statistics
from bisect import bisect_right
from pathlib import Path

import fitz  # PyMuPDF

from extract_common import write_jsonl
from extract_cw import chunk, clean_line, essay_breakpoints, filter_paras, join_lines, validate

BODY_MIN_SIZE = 9.3   # body ~10.4pt median; footnotes ~7.7, running heads ~8.5, page numbers ~8.9
MAX_SKIP = 5          # a clean reading may jump past this many lost markers and still be trusted
LEVEL_TOLERANCE = 6   # px between a margin token and the first line of its paragraph
_OCR_DIGITS = str.maketrans({"S": "3", "l": "1", "I": "1", "i": "1", "O": "0", "o": "0", "°": "0", "ο": "0"})
_SMALL_WORDS = {"a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or", "the", "to", "with"}


def _reading(token: str):
    t = token.translate(_OCR_DIGITS)
    return int(t) if t.isdigit() else None


def number_markers(tokens, start=1):
    """(number, basis) for each margin token, in order; (None, None) for a token that can't be a marker.

    basis: "clean" — read exactly, or counted between two exact readings with no marker lost;
           "read"  — taken from the token's OCR reading inside a run where a marker was lost;
           "guessed" — unreadable token in such a run, numbered one past its predecessor. It can be
                       off by one when the lost marker comes before it.
    """
    out = [(None, None)] * len(tokens)
    anchors = []  # (index, number) of clean readings that fit the run
    prev, prev_i = start - 1, -1
    for i, tok in enumerate(tokens):
        v = int(tok) if tok.isdigit() else None
        if v is not None and prev < v <= prev + (i - prev_i) + MAX_SKIP:
            anchors.append((i, v))
            out[i] = (v, "clean")
            prev, prev_i = v, i

    bounds = [(-1, start - 1)] + anchors + [(len(tokens), None)]
    for (i, a), (j, b) in zip(bounds, bounds[1:]):
        gap = list(range(i + 1, j))
        if not gap:
            continue
        if b is not None and b - a - 1 == len(gap):
            for k, v in zip(gap, range(a + 1, b)):
                out[k] = (v, "clean")
            continue
        lo = a
        for n, k in enumerate(gap):
            room = len(gap) - n - 1          # markers still to place before b
            hi = (b - 1 - room) if b is not None else None
            v, basis = _reading(tokens[k]), "read"
            if v is None or v <= lo or (hi is not None and v > hi):
                v, basis = lo + 1, "guessed"
            if hi is not None and v > hi:
                continue                     # no number left for it: not a paragraph marker
            out[k] = (v, basis)
            lo = v
    return out


def pretty_title(title: str) -> str:
    """'II. THE PRACTICAL USE OF DREAM-ANALYSIS' -> 'The Practical Use of Dream-Analysis'."""
    title = re.sub(r"^[IVXLC]+\.\s*", "", title.strip())
    if title != title.upper():
        return title
    words = title.lower().split()
    return " ".join(w if n and w in _SMALL_WORDS else "-".join(_cap(p) for p in w.split("-"))
                    for n, w in enumerate(words))


def _cap(word: str) -> str:
    """Capitalize the first letter, past any opening quote ('“rosarium' -> '“Rosarium')."""
    i = next((k for k, c in enumerate(word) if c.isalpha()), len(word))
    return word[:i] + word[i:].capitalize()


def _is_furniture(text: str, size: float, x0: float, y0: float, page_height: float) -> bool:
    """Footnotes, running heads, titles and page numbers."""
    letters = [c for c in text if c.isalpha()]
    if len(letters) >= 4 and text == text.upper():
        return True
    if len(text) <= 4 and text.translate(_OCR_DIGITS).isdigit():
        return True                                       # page number or stray figure numeral
    return size < BODY_MIN_SIZE or y0 > page_height - 40


def page_events(page):
    """[(token or None, text)] for one page's body lines, top to bottom; token is the margin marker opening it."""
    rows = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = clean_line("".join(s["text"] for s in line["spans"]).replace("\xad", "-"))
            if text:
                x0, y0 = line["bbox"][0], line["bbox"][1]
                rows.append((y0, x0, text, statistics.median(s["size"] for s in line["spans"])))
    long_lines = [x0 for _, x0, text, _ in rows if len(text) > 30]
    if not long_lines:
        return []
    body_left = min(long_lines)
    is_marker = [len(text) <= 4 and " " not in text and x0 < body_left - 6 and any(c.isdigit() for c in text)
                 for _, x0, text, _ in rows]
    markers = [(y0, text) for (y0, _, text, _), m in zip(rows, is_marker) if m]
    # sorted by y then x, so two lines at one height keep their left-to-right order
    body = [(y0, text) for (y0, x0, text, size), m in sorted(zip(rows, is_marker), key=lambda r: r[0][:2])
            if not m and not _is_furniture(text, size, x0, y0, page.rect.height)]
    events = [[None, text] for _, text in body]
    for my, token in markers:
        nearest = min(range(len(body)), key=lambda k: abs(body[k][0] - my), default=None)
        if nearest is not None and abs(body[nearest][0] - my) <= LEVEL_TOLERANCE:
            events[nearest][0] = token
    return [tuple(e) for e in events]


def extract_paragraphs(doc, volume):
    breaks, stop_page = essay_breakpoints(doc)
    breaks = [(p, pretty_title(e) if e else e, s) for p, e, s in breaks]
    break_pages = [b[0] for b in breaks]

    def locate(page):
        i = bisect_right(break_pages, page) - 1
        return (breaks[i][1], breaks[i][2]) if i >= 0 else (None, None)

    events = []  # (pdf_page, token, text)
    for pno in range(doc.page_count):
        if stop_page is not None and pno + 1 >= stop_page:
            break
        events += [(pno + 1, token, text) for token, text in page_events(doc[pno])]

    tokens = [token for _, token, _ in events if token]
    numbers = iter(number_markers(tokens))
    paragraphs, current = [], None
    for page, token, text in events:
        number, basis = next(numbers) if token else (None, None)
        if number is not None:
            if current:
                paragraphs.append(current)
            current = {"para": number, "numbering": basis, "pdf_page": page, "lines": []}
        if current:
            current["lines"].append(text)
    if current:
        paragraphs.append(current)

    records = []
    for p in paragraphs:
        essay, section = locate(p["pdf_page"])
        text = join_lines(p["lines"])
        if text:
            records.append({"volume": volume, "para": p["para"], "numbering": p["numbering"], "essay": essay,
                            "section": section, "pdf_page": p["pdf_page"], "text": text})
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--volume", required=True, help='e.g. "CW 16"')
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--target-tokens", type=int, default=700)
    ap.add_argument("--max-tokens", type=int, default=1100)
    ap.add_argument("--paras", default=None, help='inclusive paragraph range to keep, e.g. "294-352"')
    args = ap.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else (
        Path(__file__).parent.parent / "data" / args.volume.replace(" ", "").lower())
    out_dir.mkdir(parents=True, exist_ok=True)

    records = filter_paras(extract_paragraphs(fitz.open(args.pdf), args.volume), args.paras)
    warnings = validate(records)
    guessed = [r["para"] for r in records if r["numbering"] == "guessed"]
    if guessed:
        warnings.append(f"{len(guessed)} paragraph numbers guessed (may be off by one): {guessed[:15]}")
    chunks = chunk(records, args.volume, args.target_tokens, args.max_tokens)
    print(f"\nchunks: {len(chunks)}  (target {args.target_tokens} tok, max {args.max_tokens} tok)\n")
    write_jsonl(out_dir / "paragraphs.jsonl", records)
    write_jsonl(out_dir / "chunks.jsonl", chunks)

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
