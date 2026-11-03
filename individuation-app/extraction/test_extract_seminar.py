import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extract_common import chunk_pages as chunk, mend_page_breaks, page_offset  # noqa: E402
from extract_seminar import extract_pages, lecture_heading, page_lines, parse_date  # noqa: E402


class FakePage:
    """Stands in for a PyMuPDF page: get_text("dict") over (size, text) lines."""

    def __init__(self, *lines):
        self.lines = lines

    def get_text(self, kind):
        return {"blocks": [{"lines": [{"spans": [{"size": size, "text": text}]} for size, text in self.lines]}]}


class FakeDoc:
    def __init__(self, *pages):
        self.pages = pages
        self.page_count = len(pages)

    def __getitem__(self, i):
        return self.pages[i]


BODY = 10.9


def _numbered(n, *lines):
    return FakePage(*lines, (9.9, str(n)))


def _page(page, text, lecture="Lecture II", date="14 November 1928"):
    return {"source": "Dream Analysis", "section": f"{lecture}, {date}" if date else lecture,
            "lecture": lecture, "date": date, "page": page, "pdf_page": page + 26, "text": text}


def test_parse_date_reads_a_clean_date():
    assert parse_date("14 November 1928") == "14 November 1928"


def test_parse_date_repairs_ocr_years():
    assert parse_date("20 March ig2g") == "20 March 1929"
    assert parse_date("14 NOVEMBER I928") == "14 November 1928"
    assert parse_date("18 June 193O") == "18 June 1930"


def test_parse_date_rejects_body_text():
    assert parse_date("A Swiss lieutenant, an infantry officer") is None
    assert parse_date("14 November 1950") is None


def test_lecture_heading_reads_plain_and_letter_spaced_headings():
    assert lecture_heading("LECTURE II") == "Lecture II"
    assert lecture_heading("L E C T U R E V I I I") == "Lecture VIII"
    assert lecture_heading("LECTURE Ill") == "Lecture III"


def test_lecture_heading_ignores_running_heads():
    assert lecture_heading("WINTER · FIRST PART · LECTURE II") is None
    assert lecture_heading("in the lecture I gave") is None


def test_page_lines_keeps_page_numbers_and_running_head_dates_out_of_the_text():
    # in this scan the page number is set at 9.9pt, above the body floor
    headings, body, small = page_lines(FakePage((9.9, "18 JUNE 193O"), (BODY, "ations with which he"), (9.9, "655")))
    assert body == ["ations with which he"]
    assert small == ["18 JUNE 193O", "655"]


def test_page_lines_drops_ocr_garbled_page_numbers():
    for garbled in ("3°3", "3*7", ".9"):
        _, body, small = page_lines(FakePage((BODY, "the end of a lecture page"), (9.9, garbled)))
        assert body == ["the end of a lecture page"] and small == [garbled]


def test_page_lines_routes_letter_spaced_lecture_headings_at_body_size():
    headings, body, _ = page_lines(FakePage((BODY, "L E C T U R E I I I"), (BODY, "21 November 1928")))
    assert headings == ["L E C T U R E I I I"] and body == ["21 November 1928"]


def test_extract_pages_tracks_lectures_drops_date_lines_and_divider_pages():
    prose = "and we shall have to see what the dream says about the conscious attitude of the dreamer"
    doc = FakeDoc(
        FakePage((13.2, "INTRODUCTION"), (BODY, "Front matter before any lecture, " + prose)),
        _numbered(3, (13.2, "LECTURE I"), (BODY, "7 November 1928"), (BODY, "Ladies and Gentlemen: " + prose)),
        _numbered(4, (BODY, "The central problem of the analytical treatment, " + prose)),
        _numbered(5, (13.2, "WINTER TERM"), (BODY, "Second Part: January / March 1929")),
        _numbered(6, (13.2, "LECTURE I"), (BODY, "23 January 1929"), (BODY, "We will now go on with the dreams, " + prose)),
        _numbered(7, (13.2, "INDEX"), (BODY, "Achumawi, 325")),
    )
    pages, offset = extract_pages(doc)
    assert offset == -1
    assert [(p["page"], p["lecture"], p["date"]) for p in pages] == [
        (3, "Lecture I", "7 November 1928"), (4, "Lecture I", "7 November 1928"), (6, "Lecture I", "23 January 1929")]
    assert pages[0]["text"].startswith("Ladies and Gentlemen:")


def test_mend_page_breaks_only_joins_consecutive_pages_of_one_lecture():
    pages = mend_page_breaks([_page(14, "the anti-"), _page(16, "dote")])
    assert pages[0]["text"] == "the anti-"


def test_chunk_header_without_a_parsed_date_names_the_lecture_only():
    c = chunk([_page(16, "a" * 100, date=None)], 700, 1100)[0]
    assert c["header"] == "Dream Analysis — Lecture II — p. 16"


def test_page_offset_is_the_most_common_gap():
    # (pdf_page, printed number) pairs; one OCR misread
    assert page_offset([(42, "16"), (43, "17"), (44, "18"), (101, "75"), (60, "3O")]) == 26


def test_mend_page_breaks_rejoins_a_word_split_across_pages():
    pages = mend_page_breaks([_page(14, "like Mme de Pom-"), _page(15, "padour. When a femme")])
    assert pages[0]["text"] == "like Mme de Pompadour."
    assert pages[1]["text"] == "When a femme"


def test_mend_page_breaks_keeps_a_real_hyphen_before_a_capital():
    pages = mend_page_breaks([_page(14, "the anti-"), _page(15, "Freudian view")])
    assert pages[0]["text"] == "the anti-"


def test_chunk_headers_cite_lecture_date_and_pages():
    pages = [_page(16, "a" * 400), _page(17, "b" * 400)]
    chunks = chunk(pages, target_tokens=700, max_tokens=1100)
    assert len(chunks) == 1
    c = chunks[0]
    assert c["header"] == "Dream Analysis — Lecture II, 14 November 1928 — pp. 16-17"
    assert c["page_start"] == 16 and c["page_end"] == 17
    assert c["text"].startswith("[p. 16] aaa") and "\n\n[p. 17] bbb" in c["text"]


def test_chunk_never_crosses_a_lecture():
    pages = [_page(41, "a" * 100, lecture="Lecture I", date="7 November 1928"), _page(42, "b" * 100)]
    chunks = chunk(pages, target_tokens=700, max_tokens=1100)
    assert [c["header"] for c in chunks] == ["Dream Analysis — Lecture I, 7 November 1928 — p. 41",
                                              "Dream Analysis — Lecture II, 14 November 1928 — p. 42"]


def test_chunk_splits_at_the_token_target():
    pages = [_page(p, "x" * 3000) for p in (20, 21, 22)]
    assert [(c["page_start"], c["page_end"]) for c in chunk(pages, 700, 1100)] == [(20, 20), (21, 21), (22, 22)]
