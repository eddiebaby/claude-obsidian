#!/usr/bin/env python3
"""extract_vonfranz.py — page-anchored extraction of Marie-Louise von Franz, *Dreams* (Shambhala, 1998).

Input: the Internet Archive scan, OCR text layer. No paragraph numbers, so the anchor
is chapter + printed page: "von Franz, Dreams — The Dream of Socrates — pp. 37-38".

Layout facts this relies on (checked against the PDF):
  - the OCR breaks each printed line into fragments a few px apart in height,
    so lines are rebuilt by clustering fragments on y, then ordering them on x
  - odd pages carry "Chapter Title • 37" in the top 60px, even pages "38 • DREAMS";
    a chapter's opening page has a decorative title (>25pt) and no running head
  - footnotes start at the foot of the page with "a ", "b " ... in smaller type;
    each chapter's numbered endnotes begin at "Notes 1." and run to the next chapter
  - a chapter's first letter is a drop cap (>20pt), set apart from its line

Output (JSONL, UTF-8) in ../data/vonfranz-dreams/: pages.jsonl and chunks.jsonl,
in the shapes extract_seminar.py writes.

Usage:
  python extract_vonfranz.py <pdf> [--out-dir ../data/vonfranz-dreams]
                                   [--target-tokens 700] [--max-tokens 1100]
"""

import argparse
import re
from pathlib import Path

from extract_common import MIN_PAGE_CHARS, page_offset, run_page_extractor
from extract_cw import clean_line, join_lines

SOURCE = "von Franz, Dreams"
ROW_GAP = 8               # px: fragments closer than this in y belong to one printed line
HEAD_ZONE = 60            # px from the top: running head and page number
SPECK_ZONE = 10           # rows above this are scan specks ("a", ",") at or past the top edge
TITLE_MIN_SIZE = 20       # decorative chapter titles and drop caps
OPENING_TITLE_SIZE = 25
MIN_FRAGMENT_SIZE = 7     # smaller is a footnote reference or a bullet
SMALL_TYPE = 9.5          # rows below this are notes wherever they sit
FOOTNOTE_ZONE = 480       # px: footnotes only start in the lower half
FOOTNOTE_START = re.compile(r"^[a-z\d]{1,2} [A-Z“\"]")
FOOTNOTE_MAX_SIZE = 11
# each chapter ends in numbered endnotes ("Notes 1. C. G. Jung, ..."), running on until the next chapter
NOTES_RE = re.compile(r"\bNotes\s+1\.\s")


def _fragments(page):
    out = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            spans = line["spans"]
            text = clean_line("".join(s["text"] for s in spans))
            if text:
                chars = sum(len(s["text"]) for s in spans) or 1
                size = sum(s["size"] * len(s["text"]) for s in spans) / chars
                out.append((line["bbox"][0], line["bbox"][1], size, text))
    return out


def _rows(fragments):
    """Cluster fragments into printed lines: [(y, char-weighted size, text)], top to bottom."""
    rows, current = [], []
    for frag in sorted(fragments, key=lambda f: f[1]):
        if current and frag[1] - current[0][1] > ROW_GAP:
            rows.append(current)
            current = []
        current.append(frag)
    if current:
        rows.append(current)
    out = []
    for row in rows:
        row.sort(key=lambda f: f[0])
        chars = sum(len(t) for *_, t in row)
        size = sum(s * len(t) for _, _, s, t in row) / chars
        out.append((row[0][1], size, clean_line(" ".join(t for *_, t in row))))
    return out


def page_rows(page):
    return _rows(_fragments(page))


def head_text(rows) -> str:
    """The running head: rows in the head zone, below the scan specks above the top edge."""
    return " ".join(text for y, _, text in rows if SPECK_ZONE <= y < HEAD_ZONE)


def head_title(row_text: str):
    """'The Dream ofDescartes • 109' -> 'The Dream of Descartes'; None for an even page's '38 • DREAMS'."""
    if re.search(r"\bDREAMS\b", row_text):
        return None  # even page; whatever else is in the zone is leaked body text or specks
    text = re.split(r"[•*·]|\b\d+\b", row_text)[0].strip()  # the title precedes the bullet and page number
    if not text or text.upper() == text:
        return None
    text = re.sub(r"\bof(?=[A-Z])", "of ", text)
    text = re.sub(r"\.(?=[A-Z])", ". ", text)
    return re.sub(r"\s+", " ", text).strip()


def assign_chapters(pages):
    """Chapter for each page from [(is_opening, odd-page head or None)]; None before the first opening."""
    out, current = [], None
    for i, (opening, head) in enumerate(pages):
        if opening:
            current = None
            for later_opening, later_head in pages[i + 1:]:
                if later_opening:
                    break
                if later_head:
                    current = later_head
                    break
        elif head and current is not None:
            current = head
        out.append(current)
    return out


def body_text(page) -> str:
    frags = _fragments(page)
    drop_cap = next((t for _, y, s, t in frags if s > TITLE_MIN_SIZE and len(t) == 1 and t.isalpha()), "")
    frags = [f for f in frags if MIN_FRAGMENT_SIZE <= f[2] <= TITLE_MIN_SIZE]
    lines = []
    for y, size, text in _rows(frags):
        if y < HEAD_ZONE or text.startswith("Translated by") or size < SMALL_TYPE:
            continue
        if y > FOOTNOTE_ZONE and size < FOOTNOTE_MAX_SIZE and FOOTNOTE_START.match(text):
            break  # the notes run to the foot of the page
        lines.append(text)
    if drop_cap and lines:
        lines[0] = drop_cap + lines[0]
    return join_lines(lines)


def extract_pages(doc):
    info = []  # (pdf_page, is_opening, head title, head number text)
    for pno in range(doc.page_count):
        page = doc[pno]
        frags = _fragments(page)
        rows = _rows(frags)
        head = head_text(rows)
        first = next((text for y, _, text in rows if y >= SPECK_ZONE), "")
        if "GLOSSARY" in (head or first).upper():
            break
        opening = any(s > OPENING_TITLE_SIZE and y < 350 for _, y, s, _ in frags)
        number = re.search(r"\b(\d{1,3})\b", head)
        info.append((pno + 1, opening, head_title(head) if head else None, number.group(1) if number else None))

    chapters = assign_chapters([(opening, head) for _, opening, head, _ in info])
    offset = page_offset([(pdf_page, n) for pdf_page, _, _, n in info if n])
    records, notes_of = [], None  # notes_of: the chapter whose endnotes are running
    for (pdf_page, *_), chapter in zip(info, chapters):
        if chapter is None or pdf_page - offset < 1:
            continue  # front matter, including the Foreword by another hand (roman-numbered pages)
        if chapter == notes_of:
            continue
        text = body_text(doc[pdf_page - 1])
        notes = NOTES_RE.search(text)
        if notes:
            text, notes_of = text[:notes.start()].rstrip(), chapter
        if len(text) >= MIN_PAGE_CHARS:
            records.append({"source": SOURCE, "section": chapter, "page": pdf_page - offset,
                            "pdf_page": pdf_page, "text": text})
    return records, offset


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out-dir", default=Path(__file__).parent.parent / "data" / "vonfranz-dreams")
    ap.add_argument("--target-tokens", type=int, default=700)
    ap.add_argument("--max-tokens", type=int, default=1100)
    args = ap.parse_args()
    run_page_extractor(extract_pages, args.pdf, args.out_dir, args.target_tokens, args.max_tokens)


if __name__ == "__main__":
    main()
