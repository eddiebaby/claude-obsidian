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


def test_search_gives_every_query_a_slot_before_any_query_gets_a_second(tmp_path):
    # the long whole-dream query outscores a two-word image query on every chunk it touches
    dream = "power-station waterfall energy dream series development personality " * 5
    hits = search(["stepmother cow", dream], top_k=2, data_dir=_corpus(tmp_path))
    assert H2 in [h.header for h in hits]


def test_search_round_robin_moves_past_a_chunk_another_query_already_took(tmp_path):
    # the first two queries both rank H2 first; the second one's turn goes to its next-best chunk (H3)
    # instead of passing to the third query
    queries = ["stepmother cow", "stepmother cow grandmother waterfall", "dream series personality"]
    assert [h.header for h in search(queries, top_k=2, data_dir=_corpus(tmp_path))] == [H2, H3]


def test_search_never_returns_more_than_top_k(tmp_path):
    assert len(search(["dream", "energy", "stepmother", "waterfall"], top_k=2, data_dir=_corpus(tmp_path))) == 2


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


def _paragraphs(tmp_path, vol_dir, volume, essay, paras):
    (tmp_path / vol_dir).mkdir(exist_ok=True)
    rows = [json.dumps({"volume": volume, "para": n, "essay": essay, "text": t}) for n, t in paras]
    (tmp_path / vol_dir / "paragraphs.jsonl").write_text("\n".join(rows), encoding="utf-8")


def test_method_canon_returns_the_listed_paragraphs_as_single_paragraph_passages(tmp_path):
    _paragraphs(tmp_path, "cw16", "CW 16", "The Practical Use of Dream-Analysis",
                [(316, "Every interpretation invalid until it wins the assent of the patient."), (317, "x")])
    canon = cw.method_canon(canon=(("CW 16", 316),), data_dir=tmp_path)
    assert [(p.header, p.para_start, p.role) for p in canon] == [
        ("CW 16 — The Practical Use of Dream-Analysis — para. 316", 316, "method")]
    assert canon[0].text.startswith("[316] Every interpretation")


def test_method_canon_skips_paragraphs_it_cannot_find(tmp_path):
    assert cw.method_canon(canon=(("CW 16", 316),), data_dir=tmp_path) == []


def test_with_method_canon_drops_a_canon_paragraph_already_in_a_retrieved_chunk():
    canon = [CWPassage(header="CW 9i — x — para. 155", volume="CW 9i", text="[155] t", score=0.0,
                       para_start=155, para_end=155, role="method")]
    hits = [CWPassage(header=H2, volume="CW 9i", text="[155] ...", score=3.0, para_start=155, para_end=158)]
    assert [p.header for p in cw.with_method_canon(hits, canon)] == [H2]
    assert [p.header for p in cw.with_method_canon([], canon)] == ["CW 9i — x — para. 155"]


def test_user_message_marks_method_passages():
    cwp = [CWPassage(header="CW 16 — P — para. 316", volume="CW 16", text="[316] t", score=0.0,
                     para_start=316, para_end=316, role="method")]
    msg = _build_user_message("A dream.", [_sym("bus")], [], capture=Capture(), cw_passages=cwp)
    assert '<cw header="CW 16 — P — para. 316" role="method">' in msg


def test_user_message_caps_an_oversized_chunk(monkeypatch):
    from dreamapp import config
    monkeypatch.setattr(config, "MAX_CHARS_PER_CW_CHUNK", 50)
    cwp = [CWPassage(header=H1, volume="CW 8", text="[560] " + "x" * 500, score=1.0, para_start=560, para_end=564)]
    msg = _build_user_message("A dream.", [_sym("bus")], [], capture=Capture(), cw_passages=cwp)
    assert "x" * 44 + " [truncated: later paragraphs of this range not shown]\n</cw>" in msg
    assert "x" * 45 not in msg


def test_run_supplies_the_method_canon_alongside_retrieved_passages(monkeypatch):
    seen = {}
    canon = [CWPassage(header="CW 16 — P — para. 316", volume="CW 16", text="[316] t", score=0.0,
                       para_start=316, para_end=316, role="method")]
    monkeypatch.setattr(pipeline, "extract_symbols", lambda t: [_sym("bus")])
    monkeypatch.setattr(pipeline, "retrieve_passages", lambda s: [])
    monkeypatch.setattr(pipeline, "search_cw", lambda queries: [])
    monkeypatch.setattr(pipeline, "method_canon", lambda: canon)
    monkeypatch.setattr(pipeline, "synthesize_interpretation",
                        lambda *a, cw_passages=(), **kw: seen.setdefault("cw", cw_passages) and None
                        or Interpretation(dramatic_structure="a", compensation="b", amplifications=[]))
    monkeypatch.setattr(pipeline, "write_note", lambda *a, **k: None)
    with contextlib.redirect_stdout(io.StringIO()):
        pipeline.run("A bus.", dry=True)
    assert [c.header for c in seen["cw"]] == ["CW 16 — P — para. 316"]


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
