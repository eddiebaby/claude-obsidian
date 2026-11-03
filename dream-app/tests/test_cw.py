import contextlib
import io
import json

from dreamapp import cw, pipeline
from dreamapp.capture import Capture
from dreamapp.cw import CWPassage, load_chunks, search
from dreamapp.models import Amplification, Interpretation, Passage, Symbol
from dreamapp.synthesize import _build_user_message, _filter_sources
from dreamapp.writeback import _render_analysis_section

H1 = "CW 8 — On the Nature of Dreams — paras. 560-564"
H2 = "CW 9i — The Psychological Aspects of the Mother Archetype — paras. 155-158"
H3 = "CW 8 — On Psychic Energy — paras. 83-84"


def _corpus(tmp_path):
    rows = {
        "cw8": [
            {"volume": "CW 8", "essay": "On the Nature of Dreams", "para_start": 560, "para_end": 564,
             "header": H1, "text": "[560] The dream series shows a development of the personality."},
            {"volume": "CW 8", "essay": "On Psychic Energy", "para_start": 83, "para_end": 84,
             "header": H3, "text": "[83] A power-station imitates a waterfall and gains its energy."},
        ],
        "cw9i": [
            {"volume": "CW 9i", "essay": "The Psychological Aspects of the Mother Archetype", "para_start": 155,
             "para_end": 158, "header": H2, "text": "[155] The stepmother, the grandmother, the cow."},
        ],
    }
    for vol, chunks in rows.items():
        (tmp_path / vol).mkdir()
        (tmp_path / vol / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in chunks), encoding="utf-8")
    return tmp_path


def _sym(image, salience=5, query=None):
    return Symbol(image=image, kind="personal", salience=salience, query=query or image)


def test_load_chunks_reads_every_volume(tmp_path):
    assert sorted(c["header"] for c in load_chunks(_corpus(tmp_path))) == sorted([H1, H2, H3])


def test_search_ranks_the_matching_paragraphs_first(tmp_path):
    hits = search(["stepmother cow"], data_dir=_corpus(tmp_path))
    assert hits[0].header == H2
    assert hits[0].para_start == 155 and hits[0].score > 0


def test_search_indexes_the_header_as_context(tmp_path):
    assert search(["mother archetype"], data_dir=_corpus(tmp_path))[0].header == H2


def test_search_keeps_each_chunk_once_across_queries(tmp_path):
    hits = search(["stepmother", "cow grandmother", "waterfall"], top_k=5, data_dir=_corpus(tmp_path))
    assert [h.header for h in hits].count(H2) == 1
    assert {h.header for h in hits} == {H2, H3}


def test_search_without_the_corpus_returns_nothing(tmp_path, capsys):
    assert search(["anything"], data_dir=tmp_path / "missing") == []
    assert "CW corpus not found" in capsys.readouterr().err


def test_user_message_carries_cw_passages_by_header():
    cwp = [CWPassage(header=H2, volume="CW 9i", para_start=155, para_end=158, text="[155] The stepmother...", score=3.0)]
    msg = _build_user_message("A dream.", [_sym("stepmom")], [], capture=Capture(), cw_passages=cwp)
    assert f'<cw header="{H2}">\n[155] The stepmother...\n</cw>' in msg


def test_sources_keep_supplied_cw_headers_and_drop_invented_ones():
    pages = [Passage(page_path="wiki\\concepts\\Mother Archetype.md", absolute_path="x", snippet="", score=1, page_text="")]
    cwp = [CWPassage(header=H2, volume="CW 9i", para_start=155, para_end=158, text="t", score=1)]
    cited = [H2, "CW 8 — Invented Essay — paras. 1-2", "wiki/concepts/Mother Archetype.md", "wiki/concepts/Made-Up.md"]
    assert _filter_sources(cited, pages, cwp) == [H2, "wiki/concepts/Mother Archetype.md"]


def test_sources_render_cw_as_citation_and_pages_as_links():
    interp = Interpretation(dramatic_structure="a", compensation="b", amplifications=[],
                            sources=[H2, "wiki/concepts/Mother Archetype.md"])
    md = _render_analysis_section(interp)
    assert f"- {H2}" in md
    assert "- [[Mother Archetype]]" in md


DA = "Dream Analysis — Lecture II, 14 November 1928 — pp. 16-17"


def _seminar(tmp_path):
    (tmp_path / "dream-analysis").mkdir()
    chunk = {"volume": "Dream Analysis", "essay": "Lecture II, 14 November 1928", "page_start": 16, "page_end": 17,
             "header": DA, "text": "[p. 16] A Swiss lieutenant came limping, pains in the heel."}
    (tmp_path / "dream-analysis" / "chunks.jsonl").write_text(json.dumps(chunk), encoding="utf-8")
    return tmp_path


def test_load_chunks_skips_a_corrupt_line_and_says_so(tmp_path, capsys):
    (tmp_path / "cw8").mkdir()
    good = json.dumps({"volume": "CW 8", "header": H1, "text": "[560] The dream series."})
    (tmp_path / "cw8" / "chunks.jsonl").write_text(good + '\n{"volume": "CW 8", "head', encoding="utf-8")
    assert [c["header"] for c in load_chunks(tmp_path)] == [H1]
    assert "skipped 1 unreadable line" in capsys.readouterr().err


def test_search_reads_page_anchored_seminar_chunks(tmp_path):
    hit = search(["lieutenant heel"], data_dir=_seminar(_corpus(tmp_path)))[0]
    assert hit.header == DA
    assert (hit.page_start, hit.page_end) == (16, 17)
    assert hit.para_start is None


def test_seminar_citations_render_as_citations_not_links():
    interp = Interpretation(dramatic_structure="a", compensation="b", amplifications=[],
                            sources=[DA, "wiki/concepts/Mother Archetype.md"])
    md = _render_analysis_section(interp)
    assert f"- {DA}" in md
    assert "[[Dream Analysis" not in md


def test_seminar_citations_stay_out_of_related(tmp_path, monkeypatch):
    import shutil

    import frontmatter

    from dreamapp import config
    from dreamapp.writeback import write_note

    monkeypatch.setattr(config, "VAULT_ROOT", tmp_path)
    monkeypatch.setattr(config, "DREAMS_DIR", tmp_path / "wiki" / "dreams")
    monkeypatch.setattr(shutil, "which", lambda name: None)
    interp = Interpretation(dramatic_structure="a", compensation="b", amplifications=[],
                            sources=[DA, "wiki/concepts/Mother Archetype.md"])
    path = write_note("Heel pain.", interp, [_sym("heel")], title="Heel", date="2026-11-02")
    assert frontmatter.loads(path.read_text(encoding="utf-8")).metadata["related"] == ["[[Mother Archetype]]"]


def test_run_searches_cw_with_association_queries_and_the_dream(monkeypatch):
    seen = {}
    monkeypatch.setattr(pipeline, "extract_symbols", lambda t: [_sym("stepmom"), _sym("mall", salience=1)])
    monkeypatch.setattr(pipeline, "retrieve_passages", lambda s: [])
    monkeypatch.setattr(pipeline, "search_cw", lambda queries: seen.setdefault("queries", queries) and [])

    def synth(text, symbols, passages, capture=None, cw_passages=()):
        seen["cw"] = cw_passages
        return Interpretation(dramatic_structure="a", compensation="b",
                              amplifications=[Amplification("stepmom", "c", "p", "a", False)])

    monkeypatch.setattr(pipeline, "synthesize_interpretation", synth)
    monkeypatch.setattr(pipeline, "write_note", lambda *a, **k: None)
    replies = iter(["", "", "", "took my mother's place", "", "later"])
    with contextlib.redirect_stdout(io.StringIO()):
        pipeline.run("The stepmom at the mall.", dry=True, interactive=True, ask=lambda p: next(replies))
    assert seen["queries"] == ["stepmom took my mother's place", "The stepmom at the mall."]
