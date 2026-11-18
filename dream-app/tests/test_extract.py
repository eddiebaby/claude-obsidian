from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from dreamapp.extract import ExtractError, extract_symbols


def _client(text, stop_reason="end_turn"):
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(content=[SimpleNamespace(type="text", text=text)],
                                                          stop_reason=stop_reason)
    return client


def test_a_truncated_symbol_list_fails_once_instead_of_paying_for_a_reprompt():
    client = _client('[{"image": "snake", "kind": "arche', stop_reason="max_tokens")
    with patch("dreamapp.extract.anthropic.Anthropic", return_value=client), \
         patch("dreamapp.extract.config.get_api_key", return_value="k"), \
         pytest.raises(ExtractError, match="MAX_TOKENS_EXTRACT"):
        extract_symbols("A snake by the river.")
    assert client.messages.create.call_count == 1


def test_extract_reads_a_complete_symbol_list():
    client = _client('[{"image": "snake", "kind": "archetypal", "salience": 5, "query": "snake serpent"}]')
    with patch("dreamapp.extract.anthropic.Anthropic", return_value=client), \
         patch("dreamapp.extract.config.get_api_key", return_value="k"):
        symbols = extract_symbols("A snake by the river.")
    assert [(s.image, s.salience) for s in symbols] == [("snake", 5)]


MOTIFS_MD = "| Motif | Covers |\n|---|---|\n| `water` | ocean, river, flood |\n| `substances` | alcohol, drugs |\n"


def _vocab():
    from dreamapp import config
    config.DREAMS_DIR.mkdir(parents=True, exist_ok=True)
    (config.DREAMS_DIR / "motifs.md").write_text(MOTIFS_MD, encoding="utf-8")


def test_each_image_is_tagged_from_the_dreamers_motif_vocabulary():
    _vocab()
    client = _client('[{"image": "flood", "kind": "archetypal", "salience": 5, "query": "flood",'
                     ' "motifs": ["water", "invented-tag", "water"]},'
                     ' {"image": "xanax", "kind": "personal", "salience": 3, "query": "drug", "motifs": "substances"}]')
    with patch("dreamapp.extract.anthropic.Anthropic", return_value=client), \
         patch("dreamapp.extract.config.get_api_key", return_value="k"):
        symbols = extract_symbols("A flood. Someone hands me a xanax.")
    assert [s.motifs for s in symbols] == [["water"], []]
    system = client.messages.create.call_args.kwargs["system"]
    assert "- water: ocean, river, flood" in system and "- substances: alcohol, drugs" in system


def test_without_a_vocabulary_no_motifs_are_asked_for():
    client = _client('[{"image": "flood", "kind": "archetypal", "salience": 5, "query": "flood", "motifs": ["water"]}]')
    with patch("dreamapp.extract.anthropic.Anthropic", return_value=client), \
         patch("dreamapp.extract.config.get_api_key", return_value="k"):
        symbols = extract_symbols("A flood.")
    assert symbols[0].motifs == []
    assert "motifs" not in client.messages.create.call_args.kwargs["system"]


def test_no_series_means_the_motif_vocabulary_is_not_sent_either():
    _vocab()
    client = _client('[{"image": "flood", "kind": "archetypal", "salience": 5, "query": "flood", "motifs": ["water"]}]')
    with patch("dreamapp.extract.anthropic.Anthropic", return_value=client), \
         patch("dreamapp.extract.config.get_api_key", return_value="k"):
        symbols = extract_symbols("A flood.", motifs=False)
    assert symbols[0].motifs == []
    assert "ocean, river" not in client.messages.create.call_args.kwargs["system"]


def test_sending_the_motif_vocabulary_is_said_before_the_call(capsys):
    _vocab()
    client = _client('[{"image": "flood", "kind": "archetypal", "salience": 5, "query": "flood", "motifs": []}]')
    with patch("dreamapp.extract.anthropic.Anthropic", return_value=client), \
         patch("dreamapp.extract.config.get_api_key", return_value="k"):
        extract_symbols("A flood.")
    assert "motif vocabulary" in capsys.readouterr().err
