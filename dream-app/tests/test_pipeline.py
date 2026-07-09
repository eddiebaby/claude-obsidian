import os
from pathlib import Path

import pytest

from dreamapp.pipeline import run

FIXTURES = Path(__file__).parent / "fixtures"

pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY for live model calls"
)


def test_end_to_end_dry_run():
    dream_text = (FIXTURES / "dream_simple.txt").read_text(encoding="utf-8")
    interpretation = run(dream_text, dry=True, show_sources=True, title="Fixture Dream")

    assert interpretation.dramatic_structure
    assert interpretation.question
    assert isinstance(interpretation.sources, list)

    for field in (interpretation.dramatic_structure, interpretation.compensation,
                  interpretation.movement, interpretation.question):
        assert "```" not in field
    for amp in interpretation.amplifications:
        assert "```" not in amp.corpus_says
        assert "```" not in amp.personal_reading
        assert "```" not in amp.archetypal_reading
