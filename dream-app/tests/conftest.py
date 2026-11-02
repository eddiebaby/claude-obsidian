import pytest

from dreamapp import config


@pytest.fixture(autouse=True)
def _no_real_cw_corpus(tmp_path, monkeypatch):
    """Keep tests off the gitignored CW data on the dreamer's machine; tests that need chunks pass data_dir."""
    monkeypatch.setattr(config, "CW_DATA_DIR", tmp_path / "no-cw-data")
