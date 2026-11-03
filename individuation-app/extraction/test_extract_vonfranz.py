import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extract_vonfranz import assign_chapters, body_text, extract_pages, head_text, head_title, page_rows  # noqa: E402

PROSE = "and the dream compensates the one-sidedness of the conscious attitude of the dreamer"


class FakeDoc:
    def __init__(self, *pages):
        self.pages = pages
        self.page_count = len(pages)

    def __getitem__(self, i):
        return self.pages[i]


def _body(*texts):
    return [(50, 100 + 20 * i, 12.0, t) for i, t in enumerate(texts)]


class FakePage:
    """PyMuPDF page stand-in: fragments are (x0, y0, size, text)."""

    def __init__(self, *fragments):
        self.fragments = fragments

    def get_text(self, kind):
        return {"blocks": [{"lines": [{"bbox": (x, y, x + 10, y + 10), "spans": [{"size": s, "text": t}]}
                                      for x, y, s, t in self.fragments]}]}


def test_page_rows_rebuilds_a_line_from_fragments_at_nearby_heights():
    page = FakePage((128, 409, 15.2, "recent book on"), (78, 411, 14.4, "n"), (97, 414, 11.1, "his"),
                    (262, 413, 11.9, "Socrates,"), (78, 431, 12.1, "analyzed the so-called"))
    assert [text for _, _, text in page_rows(page)] == ["n his recent book on Socrates,", "analyzed the so-called"]


def test_head_title_reads_odd_page_heads_and_repairs_spacing():
    assert head_title("The Dream ofDescartes • 109") == "The Dream of Descartes"
    assert head_title("How C. G.Jung Lived with His Dreams * 27") == "How C. G. Jung Lived with His Dreams"
    assert head_title("38 • DREAMS") is None
    assert head_title("The Dream ofDescartes 131 •") == "The Dream of Descartes"


def test_head_title_ignores_even_page_heads_with_leaked_text():
    assert head_title("DREAMS Hannibal was unnaturally torn away at the age of nine.") is None
    assert head_title("DREAMS f") is None


def test_head_text_skips_scan_specks_and_joins_a_split_head():
    assert head_text([(-10, 12.0, "a"), (35, 13.8, "The Dream of Descartes • 129"), (76, 12.4, "foot is")]) \
        == "The Dream of Descartes • 129"
    assert head_text([(-4, 12.0, ","), (30, 13.0, "DREAMS"), (39, 12.0, "128 •")]) == "DREAMS 128 •"


def test_assign_chapters_runs_to_the_next_opening_page():
    # (is_opening, odd-page head); the even page before an opening still belongs to the old chapter
    pages = [(True, None), (False, None), (False, "A"), (False, None), (True, None), (False, None), (False, "B")]
    assert assign_chapters(pages) == ["A", "A", "A", "A", "B", "B", "B"]


def test_extract_pages_cuts_each_chapter_at_its_endnotes():
    doc = FakeDoc(
        FakePage((300, 150, 38.0, "Chapter"), *_body("Opening of A, " + PROSE)),
        FakePage((40, 36, 12.0, "2 • DREAMS"), *_body("Middle of A, " + PROSE)),
        FakePage((300, 36, 13.8, "Chapter A • 3"), *_body("End of A, " + PROSE + ". Notes 1. C. G. Jung, CW 8.")),
        FakePage((40, 36, 12.0, "4 • DREAMS"), *_body("2. Ibid., p. 4. 3. Cf. Sirven, p. 122. " + PROSE)),
        FakePage((300, 150, 38.0, "Chapter"), *_body("Opening of B, " + PROSE)),
        FakePage((40, 36, 12.0, "6 • DREAMS"), *_body("Middle of B, " + PROSE)),
        FakePage((300, 36, 13.8, "Chapter B • 7"), *_body("More of B, " + PROSE)),
        FakePage((300, 36, 13.8, "GLOSSARY"), *_body("Alchemy: the chemistry from prehistory onward")),
    )
    pages, offset = extract_pages(doc)
    assert offset == 0
    assert [(p["page"], p["section"]) for p in pages] == [(1, "Chapter A"), (2, "Chapter A"), (3, "Chapter A"),
                                                          (5, "Chapter B"), (6, "Chapter B"), (7, "Chapter B")]
    assert pages[2]["text"].endswith("of the dreamer.")


def test_body_text_drops_head_titles_credits_and_footnotes_and_keeps_the_drop_cap():
    page = FakePage((294, 36, 13.8, "The Dream of Socrates"), (489, 40, 12.2, "51"),
                    (307, 167, 38.4, "DneaM of"), (298, 297, 12.2, "Translated by Elizabeth Welsh"),
                    (50, 433, 34.0, "I"), (78, 411, 14.4, "n"), (128, 409, 15.2, "his recent book"),
                    (78, 448, 12.4, "Socrates sifted the tradition."),
                    (51, 830, 9.9, "a A whole incestuous chain of connections."))
    assert body_text(page) == "In his recent book Socrates sifted the tradition."
