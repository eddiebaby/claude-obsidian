#!/usr/bin/env python3
"""extract_seminar.py — page-anchored extraction of Jung's Dream Analysis seminar (1928–30).

Input: the Bollingen XCIX edition (Princeton, 1984, ed. McGuire), OCR text layer.
The seminar has no paragraph numbers, so the citable anchor is the printed page
plus the lecture date ("Dream Analysis — Lecture II, 14 November 1928 — p. 17").

Layout facts this relies on (checked against the PDF):
  - body text is set at 10.9pt and quotations / dream texts at ~9.9pt; footnotes
    (9.0pt), running heads (8.0pt) and footnote superscripts are smaller, so a
    font-size floor drops all of them at once
  - each lecture opens with a "LECTURE n" line (letter-spaced for III and VIII,
    and not always at the 13.2pt heading size in the OCR) followed by its date
  - the printed page number (9.9pt, so filtered by text, not size) is a bare
    numeral at the foot; printed = pdf page - offset. Running-head dates
    ("18 JUNE 1930") are filtered the same way, and term-divider pages skipped

Output (JSONL, UTF-8) in ../data/dream-analysis/:
  pages.jsonl  — {source, section, lecture, date, page, pdf_page, text}
  chunks.jsonl — page-anchored chunks (extract_common.chunk_pages), "[p. N]" markers in text

Known noise accepted in v0: OCR misreads inside words ("I929", "3O3ff."), and
participants' questions are kept inline with Jung's answers.

Usage:
  python extract_seminar.py <pdf> [--out-dir ../data/dream-analysis]
                                  [--target-tokens 700] [--max-tokens 1100]
"""

import argparse
import re
from pathlib import Path

from extract_common import MIN_PAGE_CHARS, page_offset, run_page_extractor
from extract_cw import clean_line, join_lines

SOURCE = "Dream Analysis"
BODY_MIN_SIZE = 9.4      # keeps 9.9pt quotations and 10.9pt body; drops 9.0pt footnotes
HEADING_MIN_SIZE = 12.5  # "LECTURE" is 13.2pt
BACK_MATTER = re.compile(r"^(INDEX|APPENDIX|BIBLIOGRAPHY|LIST OF)", re.IGNORECASE)
MONTHS = ("January February March April May June July August September October November December").split()
DATE_RE = re.compile(r"^\s*([0-9Il]{1,2})\s+([A-Za-z]+)\s+([0-9IilOog]{4,5})\s*$")
# OCR confusions in this scan: I/l/i for 1, O/o for 0, g for 9 ("20 March ig2g")
_DIGIT_FIX = str.maketrans({"I": "1", "i": "1", "l": "1", "O": "0", "o": "0", "g": "9"})
_ROMAN_FIX = str.maketrans({"l": "I", "1": "I"})
LECTURE_RE = re.compile(r"^LECTURE([IVXl1]+)$")
RUNNING_DATE_RE = re.compile(r"^\d{1,2} [A-Z]{3,9} [0-9IiOol]{4}$")
TERM_DIVIDER_RE = re.compile(r"\bTERM\b")  # "WINTER TERM" pages between parts carry no lecture text
# a page number, clean or OCR-garbled ("303", "3°3", "3*7", ".9"): short, digit-led noise characters only
PAGE_NUMBER_RE = re.compile(r"[\dIlOo*°'.�]{1,4}")


def parse_date(line: str):
    """'20 March ig2g' -> '20 March 1929'; None for anything that isn't a 1928-30 lecture date."""
    m = DATE_RE.match(line)
    if not m:
        return None
    month = next((mo for mo in MONTHS if mo.lower() == m.group(2).lower()), None)
    day = m.group(1).translate(_DIGIT_FIX)
    year = m.group(3).translate(_DIGIT_FIX)[:4]  # a 5th char is a glued footnote mark
    if month is None or not (day.isdigit() and year.isdigit()) or not 1928 <= int(year) <= 1930:
        return None
    return f"{int(day)} {month} {year}"


def page_lines(page):
    """(headings, body, small) lines of one PDF page, split by font size."""
    headings, body, small = [], [], []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            spans = line["spans"]
            whole = clean_line("".join(s["text"] for s in spans))
            if not whole:
                continue
            if lecture_heading(whole) or any(s["size"] >= HEADING_MIN_SIZE for s in spans):
                headings.append(whole)
                continue
            kept = clean_line("".join(s["text"] for s in spans if s["size"] >= BODY_MIN_SIZE))
            if kept and not _is_furniture(kept):
                body.append(kept)
            else:
                small.append(whole)
    return headings, body, small


def _is_furniture(line: str) -> bool:
    # page numbers (set at 9.9pt in this scan, above the body floor) and running-head dates ("18 JUNE 193O")
    is_page_number = PAGE_NUMBER_RE.fullmatch(line) and any(c.isdigit() for c in line)
    return bool(is_page_number) or bool(RUNNING_DATE_RE.match(line))


def lecture_heading(line: str):
    """'LECTURE II' / 'L E C T U R E V I I I' (III and VIII are letter-spaced) -> 'Lecture VIII'; else None.

    Matched on text, not font size: the OCR reports some headings below HEADING_MIN_SIZE.
    Running heads ('WINTER · FIRST PART · LECTURE II') don't match because they carry more text.
    """
    m = LECTURE_RE.match(line.replace(" ", ""))
    return f"Lecture {m.group(1).translate(_ROMAN_FIX)}" if m else None


def extract_pages(doc):
    """One record per printed page of the lectures, front and back matter skipped."""
    raw = []  # (pdf_page, headings, body, small)
    for pno in range(doc.page_count):
        raw.append((pno + 1, *page_lines(doc[pno])))
    offset = page_offset([(p, small[-1]) for p, _, _, small in raw if small])

    records, lecture, date = [], None, None
    for pdf_page, headings, body, _ in raw:
        if lecture and any(BACK_MATTER.match(h) for h in headings):
            break
        lecture_heads = [name for name in map(lecture_heading, headings) if name]
        if lecture_heads:
            lecture = lecture_heads[0]
            # the date is the first body line under the heading
            for i, line in enumerate(body[:3]):
                parsed = parse_date(line)
                if parsed:
                    date = parsed
                    body = body[:i] + body[i + 1:]
                    break
            else:
                date = None
        if lecture is None or any(TERM_DIVIDER_RE.search(h) for h in headings):
            continue
        text = join_lines(body).replace("�", "—")
        if len(text) >= MIN_PAGE_CHARS:
            records.append({"source": SOURCE, "section": f"{lecture}, {date}" if date else lecture,
                            "lecture": lecture, "date": date, "page": pdf_page - offset,
                            "pdf_page": pdf_page, "text": text})
    return records, offset


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out-dir", default=Path(__file__).parent.parent / "data" / "dream-analysis")
    ap.add_argument("--target-tokens", type=int, default=700)
    ap.add_argument("--max-tokens", type=int, default=1100)
    args = ap.parse_args()
    run_page_extractor(extract_pages, args.pdf, args.out_dir, args.target_tokens, args.max_tokens)


if __name__ == "__main__":
    main()
