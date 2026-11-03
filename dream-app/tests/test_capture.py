import contextlib
import io
import shutil
import sys

import frontmatter
import pytest

from dreamapp import cli, config, pipeline
from dreamapp.capture import Capture, ask_associations, ask_capture, confirm_symbols, with_associations
from dreamapp.models import Amplification, Interpretation, Symbol
from dreamapp.synthesize import _build_user_message
from dreamapp.writeback import write_note


def _answers(*replies):
    """An `ask` stand-in that returns the given replies in order and records each prompt."""
    replies = list(replies)
    prompts = []

    def ask(prompt):
        prompts.append(prompt)
        return replies.pop(0)

    ask.prompts = prompts
    return ask


def _sym(image, salience, query=None):
    return Symbol(image=image, kind="personal", salience=salience, query=query or image)


def _interp():
    return Interpretation(dramatic_structure="arc", compensation="comp",
                          amplifications=[Amplification("milk", "c", "p", "a", False)],
                          question="q?", sources=[])


def test_ask_capture_records_answers():
    cap = ask_capture(_answers("Fired last week, job hunting.", "dread, 4/5", "dream"))
    assert cap == Capture(conscious_situation="Fired last week, job hunting.", affect="dread, 4/5",
                          provenance="dream", associations={})


def test_ask_capture_blank_provenance_defaults_to_dream():
    assert ask_capture(_answers("", "", "")).provenance == "dream"


def test_ask_capture_reasks_on_unknown_provenance():
    ask = _answers("situation", "calm", "nightmare", "fragment")
    assert ask_capture(ask).provenance == "fragment"
    assert len(ask.prompts) == 4


def test_ask_associations_highest_salience_first_and_skips_blanks():
    symbols = [_sym("bus", 2), _sym("stepmom", 5), _sym("silver chain", 4)]
    ask = _answers("she took my mother's place", "", "my grandfather's train set")
    assoc = ask_associations(symbols, ask)
    assert assoc == {"stepmom": "she took my mother's place", "bus": "my grandfather's train set"}
    assert "stepmom" in ask.prompts[0] and "silver chain" in ask.prompts[1]


def test_ask_associations_caps_the_number_of_questions():
    symbols = [_sym(f"s{i}", 5) for i in range(10)]
    ask = _answers(*["x"] * 10)
    assert len(ask_associations(symbols, ask, limit=3)) == 3
    assert len(ask.prompts) == 3


def test_ask_associations_stops_on_q():
    symbols = [_sym("a", 5), _sym("b", 4), _sym("c", 3)]
    assert ask_associations(symbols, _answers("first", "q")) == {"a": "first"}


def test_confirm_symbols_keeps_the_list_on_enter():
    symbols = [_sym("stepmom", 5), _sym("bus", 2)]
    assert confirm_symbols(symbols, _answers(""), show=lambda *a: None) == symbols


def test_confirm_symbols_drops_and_adds_images():
    symbols = [_sym("stepmom", 5), _sym("mall", 1), _sym("bus", 2)]
    shown = []
    out = confirm_symbols(symbols, _answers("d 2", "+ silver chain", ""), show=shown.append)
    assert [s.image for s in out] == ["stepmom", "bus", "silver chain"]
    added = out[-1]
    assert (added.kind, added.salience, added.query) == ("ambiguous", 4, "silver chain")
    assert any("1. stepmom" in line for line in shown)


def test_confirm_symbols_reasks_on_input_it_does_not_understand():
    ask = _answers("drop the bus", "d 9", "d 1", "")
    assert [s.image for s in confirm_symbols([_sym("stepmom", 5), _sym("bus", 2)], ask, show=lambda *a: None)] \
        == ["bus"]
    assert len(ask.prompts) == 4


def test_with_associations_appends_association_to_query_without_mutating():
    symbols = [_sym("stepmom", 5, query="stepmother mother complex")]
    out = with_associations(symbols, {"stepmom": "took my mother's place"})
    assert out[0].query == "stepmother mother complex took my mother's place"
    assert symbols[0].query == "stepmother mother complex"


def test_user_message_carries_capture_and_marks_missing_associations():
    cap = Capture(conscious_situation="Fired last week.", affect="dread", provenance="dream",
                  associations={"stepmom": "took my mother's place"})
    msg = _build_user_message("A dream.", [_sym("stepmom", 5), _sym("bus", 2)], [], capture=cap)
    assert "<conscious_situation>\nFired last week.\n</conscious_situation>" in msg
    assert "<affect>\ndread\n</affect>" in msg
    assert "- stepmom: took my mother's place" in msg
    assert "- bus: (no association given)" in msg


def test_user_message_without_capture_says_nothing_was_collected():
    msg = _build_user_message("A dream.", [_sym("bus", 2)], [])
    assert "<associations>\n(none collected" in msg


def test_case_b_note_records_capture(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "VAULT_ROOT", tmp_path)
    monkeypatch.setattr(config, "DREAMS_DIR", tmp_path / "wiki" / "dreams")
    monkeypatch.setattr(shutil, "which", lambda name: None)
    cap = Capture(conscious_situation="Fired last week.", affect="dread, 4/5", provenance="fragment",
                  associations={"milk": "my grandmother's kitchen"})
    path = write_note("Milk everywhere.", _interp(), [_sym("milk", 5)], dry=False, title="Milk",
                      date="2026-11-02", capture=cap)
    post = frontmatter.loads(path.read_text(encoding="utf-8"))
    assert post.metadata["provenance"] == "fragment"
    assert "## Conscious Situation\n\nFired last week." in post.content
    assert "- **milk** — my grandmother's kitchen" in post.content
    assert "## Feeling-Tone\n\ndread, 4/5" in post.content


def test_case_a_fills_empty_capture_sections(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DREAMS_DIR", tmp_path)
    src = tmp_path / "2026-11-02-milk.md"
    src.write_text("---\nname: x\ntype: dream\nstatus: unanalyzed\nsymbols: []\narchetypes: []\nrelated: []\n---\n\n"
                   "# x\n\n## The Dream\n\nMilk.\n\n## Conscious Situation\n\n> [Pending]\n\n"
                   "## Waking Associations\n\n-\n\n## Feeling-Tone\n\n\n---\n\n## Jungian Analysis\n\n", encoding="utf-8")
    cap = Capture(conscious_situation="Job hunting.", affect="calm", provenance="dream",
                  associations={"milk": "my grandmother"})
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        write_note("", _interp(), [_sym("milk", 5)], source_path=str(src), dry=True, capture=cap)
    post = frontmatter.loads(buf.getvalue())
    assert post.metadata["provenance"] == "dream"
    assert "## Conscious Situation\n\nJob hunting." in post.content
    assert "- **milk** — my grandmother" in post.content
    assert "## Feeling-Tone\n\ncalm" in post.content


def test_interactive_run_asks_before_extract_and_before_retrieve(monkeypatch):
    calls = []
    monkeypatch.setattr(pipeline, "extract_symbols", lambda text: calls.append("extract") or [_sym("milk", 5)])

    def retrieve(symbols):
        calls.append(("retrieve", symbols[0].query))
        return []

    monkeypatch.setattr(pipeline, "retrieve_passages", retrieve)
    monkeypatch.setattr(pipeline, "synthesize_interpretation",
                        lambda text, symbols, passages, capture=None, **kw: calls.append(("synth", capture.affect)) or _interp())
    monkeypatch.setattr(pipeline, "write_note", lambda *a, **k: calls.append(("write", k["capture"].provenance)))

    def ask(prompt):
        calls.append("confirm" if prompt.startswith("Enter to keep") else "ask")
        return {0: "situation", 1: "dread", 2: "", 3: "", 4: "grandmother"}[len([c for c in calls if c in ("ask", "confirm")]) - 1]

    with contextlib.redirect_stdout(io.StringIO()):
        pipeline.run("Milk everywhere.", dry=True, interactive=True, ask=ask)
    # Stage 1 check between extract and the association questions; dry run, so no verdict is asked
    assert calls == ["ask", "ask", "ask", "extract", "confirm", "ask", ("retrieve", "milk grandmother"),
                     ("synth", "dread"), ("write", "dream")]


def test_cli_log_refuses_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["dreamapp", "log", "-"])
    assert cli.main() == 2
    assert "needs the dream in a file" in capsys.readouterr().err


def test_confirm_symbols_does_not_add_an_image_twice():
    shown = []
    out = confirm_symbols([_sym("Snake", 5)], _answers("+ snake", "+ chain", "+ Chain", ""), show=shown.append)
    assert [s.image for s in out] == ["Snake", "chain"]
    assert any("already" in line for line in shown)


def test_confirm_symbols_asks_before_going_on_with_no_images():
    ask = _answers("d 1", "", "n", "+ chain", "")
    assert [s.image for s in confirm_symbols([_sym("bus", 2)], ask, show=lambda *a: None)] == ["chain"]
    ask = _answers("d 1", "", "y")
    assert confirm_symbols([_sym("bus", 2)], ask, show=lambda *a: None) == []


def test_confirm_symbols_says_why_it_reasks():
    shown = []
    confirm_symbols([_sym("bus", 2)], _answers("d 7", "+", "d²", ""), show=shown.append)
    assert sum("Didn't understand" in line for line in shown) == 3
