import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extract_cw_scan import number_markers, pretty_title  # noqa: E402


def _nums(tokens, start):
    return [n for n, _ in number_markers(tokens, start=start)]


def test_markers_between_clean_numbers_fill_in_when_the_counts_match():
    # CW 16 pdf p. 156-157: "S03" and "3°3" are OCR for 302 and 303
    out = number_markers(["301", "S03", "3°3", "3°4", "305"], start=301)
    assert out == [(301, "clean"), (302, "clean"), (303, "clean"), (304, "clean"), (305, "clean")]


def test_a_lost_marker_leaves_a_gap_but_keeps_later_numbers_right():
    # 306's marker was never OCR'd; 305's paragraph absorbs it
    assert _nums(["305", "307", "308"], start=305) == [305, 307, 308]


def test_a_gap_with_a_lost_marker_reads_what_it_can_and_flags_the_guesses():
    # the real CW 16 run 313-322 (pdf pp. 159-164): 320's marker was lost, the rest are garbled
    out = number_markers(["313", "3M", "3'5", "Sl6", "3'7", "Sl8", "3l9", "32»", "322"], start=313)
    assert [n for n, _ in out] == [313, 314, 315, 316, 317, 318, 319, 320, 322]
    assert dict(out)[316] == "read" and dict(out)[318] == "read"
    # 32» is really 321; from its token alone it could be either, so it is marked as a guess
    assert dict(out)[320] == "guessed" and dict(out)[314] == "guessed"


def test_a_stray_number_far_out_of_sequence_is_not_trusted():
    # a footnote or figure number in the margin must not reset the count
    assert _nums(["294", "295", "5", "297"], start=294) == [294, 295, 296, 297]


def test_pretty_title_drops_the_roman_numeral_and_title_cases():
    assert pretty_title("II. THE PRACTICAL USE OF DREAM-ANALYSIS") == "The Practical Use of Dream-Analysis"
    assert pretty_title("IV.THE AIMS OF PSYCHOTHERAPY") == "The Aims of Psychotherapy"
    assert pretty_title("EPILOGUE") == "Epilogue"
