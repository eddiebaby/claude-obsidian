"""What `log` and `respond` must never lose: the dreamer's own writing, and answers already given."""
import contextlib
import re
import io
import shutil
import sys

import frontmatter
import pytest

from dreamapp import cli, config, pipeline
from dreamapp.models import Amplification, Interpretation, Symbol
from dreamapp.synthesize import SynthesizeError
from dreamapp.writeback import WritebackError, _is_placeholder, record_response, write_note

# The shape `_templates/dream.md` produces, Templater values resolved.
TEMPLATE_NOTE = """---
name: 2026-11-02-milk
type: dream
title: "2026-11-02 — Milk"
date: 2026-11-02
status: unanalyzed
archetypes: []
symbols: []
related: []
response:
action_done:
---

# 2026-11-02 Monday

## The Dream

Milk everywhere.

## Conscious Situation

> [What's live right now: what you're pushing on, worried about, avoiding.]


## Waking Associations

> [What each image/figure brings up FOR YOU.]

-

## Feeling-Tone

> [The emotional charge in the dream and on waking.]


## Day Residue

> [Anything from the previous day that may have seeded this.]


---

## Jungian Analysis

> Filled in by `analyze my dream`. Left empty during raw capture.

### Series Context

### Symbols & Amplification

### Sources

---

## Waking Action

> One concrete thing to do with this dream. Checked at the next entry.

---

## Dreamer Response

> [After reading the analysis: does it click, partly, or miss? Also set `response:` in frontmatter.]
"""


def _analyzed(status="analyzed", response=""):
    return (TEMPLATE_NOTE
            .replace("status: unanalyzed", f"status: {status}")
            .replace("response:\n", f"response: {response}\n" if response else "response:\n")
            .replace("### Series Context\n", "### Series Context\nFourth water dream.\n")
            .replace("> One concrete thing to do with this dream. Checked at the next entry.",
                     "Ask the milk-woman what she wants.")
            .replace("> [After reading the analysis: does it click, partly, or miss? Also set `response:` in frontmatter.]",
                     "the milk part hit"))


def _interp():
    return Interpretation(dramatic_structure="arc", compensation="against polite distance",
                          amplifications=[Amplification("milk", "c", "p", "a", False)],
                          counter_reading="plain grief", question="q?", sources=[])


def _sym():
    return Symbol(image="milk", kind="personal", salience=5, query="milk")


@pytest.fixture
def dreams(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "VAULT_ROOT", tmp_path)
    monkeypatch.setattr(config, "DREAMS_DIR", tmp_path / "wiki" / "dreams")
    monkeypatch.setattr(shutil, "which", lambda name: None)
    (tmp_path / "wiki" / "dreams").mkdir(parents=True)
    return tmp_path / "wiki" / "dreams"


def _note(dreams, text):
    path = dreams / "2026-11-02-milk.md"
    path.write_text(text, encoding="utf-8")
    return path


def _dry(path, force=False):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        write_note("", _interp(), [_sym()], source_path=str(path), dry=True, force=force)
    return buf.getvalue()


# --- Case A keeps what isn't the analysis ---

def test_case_a_analyzes_a_fresh_template_note_without_force(dreams):
    out = _dry(_note(dreams, TEMPLATE_NOTE))
    assert "### Competing Reading\nplain grief" in out
    assert "## Waking Action" in out


def test_case_a_force_replaces_the_analysis_but_keeps_waking_action_and_response(dreams):
    out = _dry(_note(dreams, _analyzed()), force=True)
    assert "Fourth water dream." not in out
    assert "### Competing Reading\nplain grief" in out
    assert "Ask the milk-woman what she wants." in out
    assert "the milk part hit" in out
    assert out.count("## Dreamer Response") == 1
    assert out.index("### Competing Reading") < out.index("## Waking Action") < out.index("## Dreamer Response")


def test_case_a_force_on_a_responded_note_keeps_its_verdict(dreams):
    post = frontmatter.loads(_dry(_note(dreams, _analyzed(status="responded", response="clicks")), force=True))
    assert post.metadata["status"] == "responded"
    assert post.metadata["response"] == "clicks"


def test_case_a_without_force_still_refuses_an_analyzed_note(dreams):
    with pytest.raises(WritebackError):
        _dry(_note(dreams, _analyzed()))


# --- respond never erases the dreamer's words ---

def test_record_response_without_a_note_keeps_what_the_dreamer_wrote(dreams):
    path = _note(dreams, _analyzed())
    record_response(path, "clicks", "")
    post = frontmatter.loads(path.read_text(encoding="utf-8"))
    assert post.metadata["response"] == "clicks"
    assert "the milk part hit" in post.content


def test_record_response_appends_to_an_existing_response(dreams):
    path = _note(dreams, _analyzed())
    record_response(path, "partial", "on second read, the brother part is off")
    text = path.read_text(encoding="utf-8")
    assert text.index("the milk part hit") < text.index("on second read, the brother part is off")


def test_record_response_replaces_the_template_placeholder(dreams):
    path = _note(dreams, TEMPLATE_NOTE)
    record_response(path, "miss", "too generic")
    text = path.read_text(encoding="utf-8")
    assert text.rstrip().endswith("## Dreamer Response\n\ntoo generic")
    assert "> [After reading" not in text


def test_record_response_refuses_a_page_that_is_not_a_dream(dreams):
    path = dreams / "motifs.md"
    path.write_text("---\ntype: meta\n---\n\n# Motifs\n", encoding="utf-8")
    with pytest.raises(WritebackError):
        record_response(path, "clicks", "")


def test_blockquoted_dreamer_text_is_not_a_placeholder():
    assert _is_placeholder("\n> [Pending]\n\n-\n")
    assert not _is_placeholder("\n> she said: go home\n")


# --- log: answers survive failures; the note exists before the verdict ---

def _stub_stages(monkeypatch, calls, synth=None):
    monkeypatch.setattr(pipeline, "extract_symbols", lambda text: calls.append("extract") or [_sym()])
    monkeypatch.setattr(pipeline, "retrieve_passages", lambda symbols: [])
    monkeypatch.setattr(pipeline, "search_cw", lambda queries: [])
    monkeypatch.setattr(pipeline, "synthesize_interpretation",
                        synth or (lambda *a, **kw: calls.append("synth") or _interp()))


def test_log_checks_for_existing_analysis_before_asking_anything(dreams, monkeypatch):
    calls = []
    _stub_stages(monkeypatch, calls)
    path = _note(dreams, _analyzed())

    def ask(prompt):
        calls.append("ask")
        return ""

    with pytest.raises(WritebackError):
        pipeline.run(path.read_text(encoding="utf-8"), source_path=str(path), interactive=True, ask=ask)
    assert calls == []


def test_log_writes_the_note_before_asking_for_the_verdict(monkeypatch, tmp_path):
    calls = []
    _stub_stages(monkeypatch, calls)
    note = tmp_path / "n.md"
    monkeypatch.setattr(pipeline, "write_note", lambda *a, **k: calls.append("write") or note)
    monkeypatch.setattr(pipeline, "record_response", lambda *a: calls.append(("record",) + a))
    replies = iter(["sit", "calm", "", "", "", "clicks", "yes"])  # 3 capture, confirm, assoc

    def ask(prompt):
        if prompt.startswith("Does this click"):
            calls.append("ask-verdict")
        return next(replies)

    with contextlib.redirect_stdout(io.StringIO()):
        pipeline.run("Milk.", interactive=True, ask=ask)
    assert calls == ["extract", "synth", "write", "ask-verdict", ("record", note, "clicks", "yes")]


def test_log_keeps_the_note_when_the_verdict_prompt_is_cancelled(monkeypatch, tmp_path, capsys):
    calls = []
    _stub_stages(monkeypatch, calls)
    monkeypatch.setattr(pipeline, "write_note", lambda *a, **k: calls.append("write") or tmp_path / "n.md")
    monkeypatch.setattr(pipeline, "record_response", lambda *a: calls.append("record"))
    replies = iter(["sit", "calm", "", "", ""])

    def ask(prompt):
        if prompt.startswith("Does this click"):
            raise EOFError
        return next(replies)

    pipeline.run("Milk.", interactive=True, ask=ask)
    assert calls == ["extract", "synth", "write"]
    assert "dreamapp respond" in capsys.readouterr().err


def test_log_prints_the_answers_when_a_later_stage_fails(monkeypatch, capsys):
    def boom(*a, **kw):
        raise SynthesizeError("credit balance is too low")

    _stub_stages(monkeypatch, [], synth=boom)
    replies = iter(["Fired last week.", "dread", "", "", "my grandmother"])
    with pytest.raises(SynthesizeError):
        pipeline.run("Milk.", interactive=True, ask=lambda prompt: next(replies))
    err = capsys.readouterr().err
    assert "Fired last week." in err and "my grandmother" in err


def test_a_note_is_read_for_its_dream_section_only(monkeypatch):
    seen = {}
    _stub_stages(monkeypatch, [])
    monkeypatch.setattr(pipeline, "extract_symbols", lambda text: seen.setdefault("extract", text) and [_sym()])
    monkeypatch.setattr(pipeline, "search_cw", lambda queries: seen.setdefault("queries", queries) and [])
    monkeypatch.setattr(pipeline, "write_note", lambda *a, **k: None)
    with contextlib.redirect_stdout(io.StringIO()):
        pipeline.run(_analyzed(), dry=True, force=True)
    assert seen["extract"] == "Milk everywhere."
    assert seen["queries"][-1] == "Milk everywhere."


def test_plain_dream_text_is_used_as_is():
    assert pipeline.dream_section("I was on a bus.\nThen a train.") == "I was on a bus.\nThen a train."


def test_dream_section_drops_the_template_prompt_and_keeps_the_dreamers_text():
    note = "## The Dream\n\n> [Present tense, first person.]\n\nI was on a bus.\n\n## Conscious Situation\n\nx"
    assert pipeline.dream_section(note) == "I was on a bus."


def test_a_long_analyzed_note_with_a_short_dream_is_accepted(monkeypatch):
    # past analyses run well beyond MAX_DREAM_CHARS; only the dream section counts
    _stub_stages(monkeypatch, [])
    monkeypatch.setattr(pipeline, "write_note", lambda *a, **k: None)
    long_note = _analyzed().replace("Fourth water dream.", "Fourth water dream. " * 1000)
    assert len(long_note) > pipeline.config.MAX_DREAM_CHARS
    with contextlib.redirect_stdout(io.StringIO()):
        pipeline.run(long_note, dry=True, force=True)


def test_a_note_with_no_dream_text_is_refused_before_the_interview(monkeypatch):
    asked = []
    _stub_stages(monkeypatch, [])  # never reach a live model, whatever the code under test does
    with pytest.raises(pipeline.InputError, match="no dream text"):
        pipeline.run(TEMPLATE_NOTE.replace("Milk everywhere.", ""), interactive=True,
                     ask=lambda prompt: asked.append(prompt) or "")
    assert asked == []


def test_cli_log_cancelled_during_the_interview_exits_cleanly(monkeypatch, tmp_path, capsys):
    dream = tmp_path / "dream.txt"
    dream.write_text("Milk.", encoding="utf-8")

    def interrupted(ask):
        raise KeyboardInterrupt

    monkeypatch.setattr(pipeline, "ask_capture", interrupted)
    monkeypatch.setattr(sys, "argv", ["dreamapp", "log", str(dream)])
    assert cli.main() == 130
    assert "cancelled" in capsys.readouterr().err


# --- capture answers always land somewhere ---

def _cap(**kw):
    from dreamapp.capture import Capture
    base = dict(conscious_situation="New job offer.", affect="dread, 4", provenance="dream",
                associations={"milk": "my grandmother's kitchen"})
    base.update(kw)
    return Capture(**base)


def _case_a(dreams, text, capture):
    path = _note(dreams, text)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        write_note("", _interp(), [_sym()], source_path=str(path), dry=True, force=True, capture=capture)
    return buf.getvalue()


def test_an_answer_for_a_section_the_note_lacks_gets_a_new_section(dreams):
    out = _case_a(dreams, TEMPLATE_NOTE.replace("## Conscious Situation\n\n> [What's live right now: what you're "
                                                "pushing on, worried about, avoiding.]\n\n\n", ""), _cap())
    assert "## Conscious Situation\n\nNew job offer." in out
    assert out.index("## Conscious Situation") < out.index("## Jungian Analysis")


def test_an_answer_for_a_filled_section_goes_under_what_is_there(dreams):
    filled = TEMPLATE_NOTE.replace("> [What's live right now: what you're pushing on, worried about, avoiding.]",
                                   "Quit the old job in October.")
    out = _case_a(dreams, filled, _cap())
    assert "Quit the old job in October." in out and "New job offer." in out
    assert out.index("Quit the old job") < out.index("New job offer.")


def test_a_rerun_does_not_repeat_an_association_already_written(dreams):
    once = TEMPLATE_NOTE.replace("> [What each image/figure brings up FOR YOU.]\n\n-",
                                 "- **milk** — my grandmother's kitchen")
    out = _case_a(dreams, once, _cap())
    associations = out[out.index("## Waking Associations"):out.index("## Feeling-Tone")]
    assert associations.count("**milk**") == 1


def test_the_default_provenance_does_not_overwrite_an_imported_note(dreams):
    imported = TEMPLATE_NOTE.replace("status: unanalyzed", "status: unanalyzed\nprovenance: imported")
    assert frontmatter.loads(_case_a(dreams, imported, _cap())).metadata["provenance"] == "imported"
    assert frontmatter.loads(_case_a(dreams, imported, _cap(provenance="fragment"))).metadata["provenance"] == "fragment"


def test_a_rerun_with_the_same_answers_adds_nothing_and_a_changed_one_is_kept(dreams):
    first = _case_a(dreams, TEMPLATE_NOTE, _cap())
    _note(dreams, first)
    again = _case_a(dreams, first, _cap())
    assert again.count("New job offer.") == 1 and again.count("dread, 4") == 1
    changed = _case_a(dreams, first, _cap(associations={"milk": "the farm, actually"}))
    associations = changed[changed.index("## Waking Associations"):changed.index("## Feeling-Tone")]
    assert "my grandmother's kitchen" in associations and "the farm, actually" in associations


def test_all_three_sections_missing_are_all_created_above_the_analysis(dreams):
    bare = re.sub(r"## (Conscious Situation|Waking Associations|Feeling-Tone)\n.*?(?=^## )", "", TEMPLATE_NOTE,
                  flags=re.S | re.M)
    assert "## Conscious Situation" not in bare
    out = _case_a(dreams, bare, _cap())
    for heading in ("## Conscious Situation", "## Waking Associations", "## Feeling-Tone"):
        assert out.index(heading) < out.index("## Jungian Analysis")


def test_an_image_with_no_ascii_name_never_writes_an_empty_symbol_tag(dreams):
    from dreamapp.models import Symbol
    path = write_note("A snake.", _interp(), [Symbol("🐍", "ambiguous", 4, "snake"), _sym()], dry=False,
                      title="Snake", date="2026-11-03")
    assert frontmatter.loads(path.read_text(encoding="utf-8")).metadata["symbols"] == ["milk"]
