import anthropic
import pytest

from dreamapp import config


def pytest_configure(config):
    config.addinivalue_line("markers", "live: calls the real Anthropic API (paid); everything else is blocked")


@pytest.fixture(autouse=True)
def _no_real_cw_corpus(tmp_path, monkeypatch):
    """Keep tests off the gitignored CW data on the dreamer's machine; tests that need chunks pass data_dir."""
    monkeypatch.setattr(config, "CW_DATA_DIR", tmp_path / "no-cw-data")


@pytest.fixture(autouse=True)
def _no_real_vault(tmp_path, monkeypatch):
    """A test that reaches write_note un-dried writes into a temp vault, never the dreamer's wiki/dreams."""
    monkeypatch.setattr(config, "VAULT_ROOT", tmp_path)
    monkeypatch.setattr(config, "DREAMS_DIR", tmp_path / "wiki" / "dreams")


@pytest.fixture(autouse=True)
def _no_live_api(request, monkeypatch):
    """A test that forgets to stub a model stage fails here instead of spending the dreamer's credits."""
    if request.node.get_closest_marker("live"):
        return

    def blocked(*args, **kwargs):
        raise AssertionError("test tried to call the live Anthropic API; stub the stage or mark it @pytest.mark.live")

    monkeypatch.setattr(anthropic, "Anthropic", blocked)
