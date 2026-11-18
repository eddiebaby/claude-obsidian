import io
import contextlib
import shutil
from pathlib import Path

import frontmatter
import pytest

from dreamapp import config
from dreamapp.models import Amplification, Interpretation, Symbol
from dreamapp.writeback import WritebackError, _split_frontmatter, write_note

FIXTURES = Path(__file__).parent / "fixtures"


def _interp(sources=None):
    return Interpretation(
        dramatic_structure="A short arc.",
        compensation="Balances neglect of nourishment.",
        amplifications=[Amplification("milk", "corpus says X", "personally Y", "archetypally Z", False)],
        objective_level="obj", subjective_level="subj", movement="toward wholeness",
        question="What are you not receiving?", sources=sources or ["wiki/concepts/Vessel-Symbol.md"],
    )


def _symbols():
    return [Symbol("half-drunk gallon of milk", "archetypal", 5, "milk nourishment vessel mother")]


def test_case_b_dry_render_parses_and_has_headings():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        write_note("I saw milk overflowing.", _interp(), _symbols(), dry=True, title="Milk Test")
    rendered = buf.getvalue()

    post = frontmatter.loads(rendered)
    assert post.metadata["type"] == "dream"
    assert post.metadata["status"] == "analyzed"
    assert post.metadata["symbols"] == ["half-drunk-gallon-of-milk"]
    for heading in ("## The Dream", "## Jungian Analysis", "### Sources"):
        assert heading in post.content


def test_case_b_writes_file_and_handles_collision(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "VAULT_ROOT", tmp_path)
    monkeypatch.setattr(config, "DREAMS_DIR", tmp_path / "wiki" / "dreams")
    monkeypatch.setattr(shutil, "which", lambda name: None)

    p1 = write_note("Milk overflowing everywhere.", _interp(), _symbols(), dry=False,
                     title="Milk Test", date="2026-07-01")
    assert p1.is_file()
    assert p1.name == "2026-07-01-milk-test.md"

    p2 = write_note("Milk overflowing everywhere again.", _interp(), _symbols(), dry=False,
                     title="Milk Test", date="2026-07-01")
    assert p2.name == "2026-07-01-milk-test-2.md"
    assert p2 != p1


def test_case_a_preserves_preamble_and_unions_frontmatter(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DREAMS_DIR", tmp_path)
    src = tmp_path / "dream_note.md"
    src.write_text((FIXTURES / "dream_note.md").read_text(encoding="utf-8"), encoding="utf-8")

    orig = src.read_text(encoding="utf-8")
    _, orig_body = _split_frontmatter(orig)
    orig_preamble = orig_body[: orig_body.find("## Jungian Analysis")]

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        write_note("", _interp(sources=["wiki/concepts/Vessel-Symbol.md"]), _symbols(),
                    source_path=str(src), dry=True, force=True)
    rendered = buf.getvalue()

    _, new_body = _split_frontmatter(rendered)
    new_preamble = new_body[: new_body.find("## Jungian Analysis")]
    assert new_preamble == orig_preamble

    post = frontmatter.loads(rendered)
    assert "milk" in post.metadata["symbols"]  # existing entries preserved
    assert "half-drunk-gallon-of-milk" in post.metadata["symbols"]  # new entry unioned in
    assert "mother" in post.metadata["archetypes"]  # existing preserved


def test_case_a_aborts_without_force(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DREAMS_DIR", tmp_path)
    src = tmp_path / "dream_note.md"
    src.write_text((FIXTURES / "dream_note.md").read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(WritebackError):
        write_note("", _interp(), _symbols(), source_path=str(src), dry=True, force=False)


def test_series_context_leads_the_analysis_and_an_earlier_dream_becomes_related():
    i = _interp(sources=["wiki/dreams/2026-10-07-chain.md"])
    i.series_context = "Third chain dream: broken 10-07, given away tonight."
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        write_note("A chain.", i, _symbols(), dry=True, title="Chain")
    rendered = buf.getvalue()
    analysis = rendered[rendered.index("## Jungian Analysis"):]
    assert analysis.index("### Series Context") < analysis.index("### Dramatic Structure")
    assert "Third chain dream: broken 10-07, given away tonight." in analysis
    assert "[[2026-10-07-chain]]" in frontmatter.loads(rendered).metadata["related"]


def test_no_series_context_means_no_empty_heading():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        write_note("Milk.", _interp(), _symbols(), dry=True, title="Milk")
    assert "### Series Context" not in buf.getvalue()


def test_a_new_note_records_the_motifs_extraction_found():
    symbols = [Symbol("flood", "archetypal", 5, "flood", ["water"]), Symbol("pill", "personal", 2, "drug",
                                                                             ["substances", "water"])]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        write_note("A flood.", _interp(), symbols, dry=True, title="Flood")
    assert frontmatter.loads(buf.getvalue()).metadata["motifs"] == ["water", "substances"]


def _case_a_render(tmp_path, monkeypatch, fm_extra=""):
    monkeypatch.setattr(config, "DREAMS_DIR", tmp_path)
    src = tmp_path / "dream_note.md"
    text = (FIXTURES / "dream_note.md").read_text(encoding="utf-8")
    src.write_text(text.replace("archetypes: [", fm_extra + "archetypes: [", 1), encoding="utf-8")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        write_note("", _interp(), [Symbol("milk", "archetypal", 5, "milk", ["food", "water"])],
                   source_path=str(src), dry=True, force=True)
    return frontmatter.loads(buf.getvalue()).metadata


def test_reanalysis_fills_motifs_on_a_note_that_has_none(tmp_path, monkeypatch):
    assert _case_a_render(tmp_path, monkeypatch)["motifs"] == ["food", "water"]
    assert _case_a_render(tmp_path, monkeypatch, "motifs: []\n")["motifs"] == ["food", "water"]


def test_reanalysis_never_changes_motifs_already_chosen(tmp_path, monkeypatch):
    # the dreamer's (or the /dream skill's) tagging outranks extraction's
    assert _case_a_render(tmp_path, monkeypatch, "motifs: [house, family]\n")["motifs"] == ["house", "family"]
