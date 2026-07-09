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
