import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from dreamapp.models import Passage, Symbol
from dreamapp.synthesize import synthesize_interpretation

VALID_RESPONSE = {
    "dramatic_structure": "exposition then culmination",
    "compensation": "balances neglect",
    "amplifications": [
        {"symbol": "milk", "corpus_says": "corpus", "personal_reading": "p",
         "archetypal_reading": "a", "thin_coverage": False}
    ],
    "objective_level": "obj",
    "subjective_level": "subj",
    "movement": "toward wholeness",
    "question": "what are you avoiding?",
    # Model echoes forward slashes even though page_path below uses backslashes
    # (Windows-native, as retrieve.py emits), plus one fabricated page never supplied.
    "sources": ["wiki/concepts/Vessel-Symbol.md", "wiki/concepts/Fabricated-Page.md"],
}


def _fake_client(response_text):
    fake_block = SimpleNamespace(type="text", text=response_text)
    fake_resp = SimpleNamespace(content=[fake_block])
    client = MagicMock()
    client.messages.create.return_value = fake_resp
    return client


def test_sources_filtered_to_supplied_pages_with_separator_normalization():
    passages = [
        Passage(page_path="wiki\\concepts\\Vessel-Symbol.md", absolute_path="x",
                snippet="s", score=1.0, page_text="text"),
    ]
    symbols = [Symbol(image="milk", kind="archetypal", salience=5, query="milk")]

    with patch("dreamapp.synthesize.anthropic.Anthropic", return_value=_fake_client(json.dumps(VALID_RESPONSE))), \
         patch("dreamapp.synthesize.config.get_api_key", return_value="dummy-key"):
        interpretation = synthesize_interpretation("a dream", symbols, passages)

    assert interpretation.sources == ["wiki/concepts/Vessel-Symbol.md"]


def test_no_supplied_pages_means_no_sources_survive():
    symbols = [Symbol(image="milk", kind="archetypal", salience=5, query="milk")]

    with patch("dreamapp.synthesize.anthropic.Anthropic", return_value=_fake_client(json.dumps(VALID_RESPONSE))), \
         patch("dreamapp.synthesize.config.get_api_key", return_value="dummy-key"):
        interpretation = synthesize_interpretation("a dream", symbols, [])

    assert interpretation.sources == []


def test_synthesis_gets_the_configured_output_budget():
    client = _fake_client(json.dumps(VALID_RESPONSE))
    with patch("dreamapp.synthesize.anthropic.Anthropic", return_value=client), \
         patch("dreamapp.synthesize.config.get_api_key", return_value="k"):
        synthesize_interpretation("A dream.", [Symbol("milk", "archetypal", 5, "milk")], [])
    from dreamapp import config
    assert client.messages.create.call_args.kwargs["max_tokens"] == config.MAX_TOKENS_SYNTH


def test_a_truncated_answer_fails_once_instead_of_paying_for_a_reprompt():
    import pytest

    from dreamapp.synthesize import SynthesizeError
    client = _fake_client('{"dramatic_structure": "cut off mid-')
    client.messages.create.return_value.stop_reason = "max_tokens"
    with patch("dreamapp.synthesize.anthropic.Anthropic", return_value=client), \
         patch("dreamapp.synthesize.config.get_api_key", return_value="k"), \
         pytest.raises(SynthesizeError, match="MAX_TOKENS_SYNTH"):
        synthesize_interpretation("A dream.", [Symbol("milk", "archetypal", 5, "milk")], [])
    assert client.messages.create.call_count == 1


# --- the series (design.md §3): earlier dreams sharing an image, sent beside the corpus ---

def _entry(**kw):
    from datetime import date

    from dreamapp.series import SeriesEntry
    base = dict(name="2026-10-07-chain", date=date(2026, 10, 7), title="2026-10-07 — Chain",
                path="wiki/dreams/2026-10-07-chain.md", excerpt="The silver chain breaks at the clasp.",
                compensation="The break compensates a belief that things hold.", response="partial",
                response_note="The clasp hit.", agency=2.0, matched=["silver chain"])
    base.update(kw)
    return SeriesEntry(**base)


def test_the_series_block_carries_each_earlier_dream_its_reading_and_the_verdict():
    from dreamapp.series import Series
    from dreamapp.synthesize import _series_block
    block = _series_block(Series([_entry()], counts={"silver chain": 5}))
    assert block.startswith("<series>\n") and block.rstrip().endswith("</series>")
    assert 'path="wiki/dreams/2026-10-07-chain.md"' in block and 'date="2026-10-07"' in block
    assert 'images="silver chain"' in block and 'verdict="partial"' in block
    assert "The silver chain breaks at the clasp." in block
    assert "The break compensates a belief that things hold." in block
    assert "The clasp hit." in block
    assert "silver chain: 5 earlier dreams, 1 shown" in block


def test_an_unrated_earlier_reading_says_so():
    from dreamapp.series import Series
    from dreamapp.synthesize import _series_block
    block = _series_block(Series([_entry(response="", response_note="", compensation="")]))
    assert 'verdict="unrated"' in block and "(no reading on file)" in block


def test_no_earlier_dream_and_no_lookup_are_told_apart():
    from dreamapp.series import Series
    from dreamapp.synthesize import _series_block
    assert "no earlier dream in the series shares these images" in _series_block(Series())
    assert "(not consulted)" in _series_block(None)


def test_an_attribute_quote_in_an_image_cannot_break_the_block():
    from dreamapp.series import Series
    from dreamapp.synthesize import _series_block
    block = _series_block(Series([_entry(matched=['the "red" door'])]))
    assert "images=\"the 'red' door\"" in block


def test_the_series_reaches_the_model_and_an_earlier_dream_survives_as_a_source():
    from dreamapp.series import Series
    response = dict(VALID_RESPONSE, series_context="Third chain dream.",
                    sources=["wiki/dreams/2026-10-07-chain.md", "wiki/dreams/2026-01-01-invented.md"])
    client = _fake_client(json.dumps(response))
    with patch("dreamapp.synthesize.anthropic.Anthropic", return_value=client), \
         patch("dreamapp.synthesize.config.get_api_key", return_value="k"):
        interpretation = synthesize_interpretation("A chain.", [Symbol("silver chain", "personal", 5, "chain")], [],
                                                   series=Series([_entry()]))
    sent = client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "<series>" in sent and "The silver chain breaks at the clasp." in sent
    assert interpretation.series_context == "Third chain dream."
    assert interpretation.sources == ["wiki/dreams/2026-10-07-chain.md"]


def test_the_series_block_counts_every_image_with_hits_and_runs_oldest_first():
    from datetime import date

    from dreamapp.series import Series
    from dreamapp.synthesize import _series_block
    newer = _entry(name="2026-10-20-b", date=date(2026, 10, 20), path="wiki/dreams/2026-10-20-b.md")
    older = _entry(name="2026-08-01-a", date=date(2026, 8, 1), path="wiki/dreams/2026-08-01-a.md")
    block = _series_block(Series([newer, older], counts={"silver chain": 2, "snake": 4}))
    assert block.index("2026-08-01") < block.index("2026-10-20")
    assert "snake: 4 earlier dreams, 0 shown" in block
