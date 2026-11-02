import contextlib
import io
import shutil
import sys

import frontmatter

from dreamapp import cli, config, pipeline, retrieve
from dreamapp.capture import Capture, ask_response
from dreamapp.models import Amplification, Interpretation, Symbol
from dreamapp.writeback import _render_analysis_section, record_response, write_note


def _answers(*replies):
    replies = list(replies)
    prompts = []

    def ask(prompt):
        prompts.append(prompt)
        return replies.pop(0)

    ask.prompts = prompts
    return ask


def _interp(**kw):
    base = dict(dramatic_structure="arc", compensation="against polite distance",
                amplifications=[Amplification("milk", "c", "p", "a", False)],
                counter_reading="plain grief, no compensation", question="q?", sources=[])
    base.update(kw)
    return Interpretation(**base)


def _sym(image="milk", salience=5):
    return Symbol(image=image, kind="personal", salience=salience, query=image)


def test_interpretation_reads_counter_reading():
    i = Interpretation.from_dict({"dramatic_structure": "a", "compensation": "b", "amplifications": [],
                                  "counter_reading": "the opposite", "objective_level": "", "subjective_level": "",
                                  "movement": "", "question": "", "sources": []})
    assert i.counter_reading == "the opposite"


def test_analysis_renders_competing_reading_after_compensation():
    md = _render_analysis_section(_interp())
    assert "### Competing Reading\nplain grief, no compensation" in md
    assert md.index("### Compensation") < md.index("### Competing Reading") < md.index("### Movement")


def test_ask_response_accepts_verdict_and_note():
    assert ask_response(_answers("clicks", "the stepmom part hit")) == ("clicks", "the stepmom part hit")


def test_ask_response_maps_yes_partly_no():
    assert ask_response(_answers("partly", "")) == ("partial", "")
    assert ask_response(_answers("no", "too generic")) == ("miss", "too generic")


def test_ask_response_later_leaves_it_unrated():
    ask = _answers("later")
    assert ask_response(ask) == ("", "")
    assert len(ask.prompts) == 1


def test_ask_response_reasks_until_it_understands():
    ask = _answers("maybe", "", "miss", "wrong figure")
    assert ask_response(ask) == ("miss", "wrong figure")
    assert len(ask.prompts) == 4


def test_case_b_note_records_response(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "VAULT_ROOT", tmp_path)
    monkeypatch.setattr(config, "DREAMS_DIR", tmp_path / "wiki" / "dreams")
    monkeypatch.setattr(shutil, "which", lambda name: None)
    path = write_note("Milk.", _interp(), [_sym()], dry=False, title="Milk", date="2026-11-02")
    record_response(path, "partial", "the milk part hit")
    post = frontmatter.loads(path.read_text(encoding="utf-8"))
    assert post.metadata["response"] == "partial"
    assert post.metadata["status"] == "responded"
    assert post.content.rstrip().endswith("## Dreamer Response\n\nthe milk part hit")


def test_case_b_note_without_response_stays_analyzed_with_empty_section(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "VAULT_ROOT", tmp_path)
    monkeypatch.setattr(config, "DREAMS_DIR", tmp_path / "wiki" / "dreams")
    monkeypatch.setattr(shutil, "which", lambda name: None)
    path = write_note("Milk.", _interp(), [_sym()], dry=False, title="Milk", date="2026-11-02")
    post = frontmatter.loads(path.read_text(encoding="utf-8"))
    assert post.metadata["status"] == "analyzed"
    assert not post.metadata.get("response")
    assert "## Dreamer Response" in post.content


def test_interactive_run_shows_compensation_and_competing_reading_before_the_verdict(monkeypatch, tmp_path):
    monkeypatch.setattr(pipeline, "extract_symbols", lambda text: [_sym()])
    monkeypatch.setattr(pipeline, "retrieve_passages", lambda symbols: [])
    monkeypatch.setattr(pipeline, "synthesize_interpretation", lambda *a, **kw: _interp())
    monkeypatch.setattr(pipeline, "write_note", lambda *a, **k: tmp_path / "n.md")
    monkeypatch.setattr(pipeline, "record_response", lambda *a: None)
    buf = io.StringIO()
    replies = iter(["sit", "calm", "", ""])

    def ask(prompt):
        if prompt.startswith("Does this click"):
            shown = buf.getvalue()
            assert "against polite distance" in shown and "plain grief, no compensation" in shown
            return "later"
        return next(replies)

    with contextlib.redirect_stdout(buf):
        pipeline.run("Milk.", interactive=True, ask=ask)


def test_cli_respond_updates_existing_note(tmp_path, monkeypatch):
    note = tmp_path / "2026-10-01-walkout.md"
    note.write_text("---\nname: x\ntype: dream\nstatus: analyzed\nresponse:\n---\n\n# x\n\n## Jungian Analysis\n\nA.\n\n"
                    "---\n\n## Dreamer Response\n\n> [After reading the analysis...]\n", encoding="utf-8")
    monkeypatch.setattr(shutil, "which", lambda name: None)
    monkeypatch.setattr(sys, "argv", ["dreamapp", "respond", str(note), "--verdict", "clicks",
                                      "--note", "the doorway part is exactly it"])
    assert cli.main() == 0
    post = frontmatter.loads(note.read_text(encoding="utf-8"))
    assert post.metadata["response"] == "clicks"
    assert post.metadata["status"] == "responded"
    assert post.content.rstrip().endswith("## Dreamer Response\n\nthe doorway part is exactly it")


def test_cli_respond_rejects_unknown_verdict(tmp_path, monkeypatch, capsys):
    note = tmp_path / "n.md"
    note.write_text("---\ntype: dream\n---\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["dreamapp", "respond", str(note), "--verdict", "great"])
    assert cli.main() == 2


def _candidate(page, bm25, rerank, source):
    return {"page_path": page, "absolute_path": page, "snippet": "s", "bm25_score": bm25,
            "rerank_score": rerank, "rerank_source": source}


def test_retrieve_ranks_by_bm25_when_rerank_did_not_run(monkeypatch):
    hits = {"a": [_candidate("wiki/concepts/Low.md", 2.0, 0.0, "noop-no-model")],
            "b": [_candidate("wiki/concepts/High.md", 9.0, 0.0, "noop-no-model")]}
    monkeypatch.setattr(retrieve, "_run_query", lambda q, top: hits[q])
    monkeypatch.setattr(retrieve, "_read_page_text", lambda p: "text")
    passages = retrieve.retrieve_passages([Symbol("a", "personal", 5, "a"), Symbol("b", "personal", 5, "b")])
    assert [p.page_path for p in passages] == ["wiki/concepts/High.md", "wiki/concepts/Low.md"]
    assert passages[0].score == 9.0


def test_retrieve_never_returns_the_dreamers_own_dream_pages(monkeypatch):
    hits = [_candidate("wiki\\dreams\\2026-06-30-milk.md", 9.0, 0.9, "cosine:nomic-embed-text"),
            _candidate("wiki/jung/symbols/Breast.md", 5.0, 0.5, "cosine:nomic-embed-text")]
    monkeypatch.setattr(retrieve, "_run_query", lambda q, top: hits)
    monkeypatch.setattr(retrieve, "_read_page_text", lambda p: "text")
    passages = retrieve.retrieve_passages([Symbol("milk", "personal", 5, "milk")])
    assert [p.page_path for p in passages] == ["wiki/jung/symbols/Breast.md"]
