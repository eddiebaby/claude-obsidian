import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from extract_cw import filter_paras  # noqa: E402


def _recs(*paras):
    return [{"para": p, "text": "t"} for p in paras]


def test_filter_paras_keeps_the_inclusive_range():
    assert [r["para"] for r in filter_paras(_recs(43, 44, 200, 331, 332), "44-331")] == [44, 200, 331]


def test_filter_paras_without_a_range_keeps_everything():
    assert len(filter_paras(_recs(1, 2), None)) == 2


def test_filter_paras_rejects_a_malformed_range():
    with pytest.raises(ValueError):
        filter_paras(_recs(1), "44")
