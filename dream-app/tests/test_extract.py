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
