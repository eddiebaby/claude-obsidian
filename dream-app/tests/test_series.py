"""Series memory (design.md §3): earlier dreams that share this dream's images, found from the vault's own notes."""
from datetime import date

import pytest

from dreamapp import config
from dreamapp.models import Symbol
from dreamapp.notes import words
from dreamapp.series import find_series, load_series, motif_map, recurrences, render_timeline

MOTIFS_MD = """# Motifs

| Motif | Covers |
|---|---|
| `water` | ocean, river, lake, flood, pool, puddle, standing water |
| `jewelry` | chains, necklaces, jewelry stores (added 2026-11-01) |
| `snow-ice` | snow, ice, frozen things |

## Figures
"""


def _note(d, day, slug, *, text="Text.", symbols=(), figures=(), motifs=(), provenance=None, agency=None,
          compensation="", response="", response_note="", type_="dream"):
    fm = ["---", f"name: {day}-{slug}", f"type: {type_}", f'title: "{day} — {slug.replace("-", " ").title()}"',
          f"date: {day}", f"symbols: [{', '.join(symbols)}]", f"figures: [{', '.join(figures)}]",
          f"motifs: [{', '.join(motifs)}]", f"agency: {'' if agency is None else agency}", f"response: {response}"]
    if provenance:
        fm.append(f"provenance: {provenance}")
    fm.append("---")
    body = (f"\n# {day}\n\n## The Dream\n\n{text}\n\n## Feeling-Tone\n\nuneasy, 3\n\n---\n\n"
            "## Jungian Analysis\n\n### Series Context\n\n- earlier stuff\n\n"
            f"### Compensation / What the Unconscious Is Saying\n\n{compensation}\n\n### Sources\n\n---\n\n"
            "## Waking Action\n\nDo one thing.\n\n---\n\n"
            f"## Dreamer Response\n\n{response_note}\n")
    path = d / f"{day}-{slug}.md"
    path.write_text("\n".join(fm) + body, encoding="utf-8")
    return path


@pytest.fixture
def dreams():
    config.DREAMS_DIR.mkdir(parents=True)
    return config.DREAMS_DIR


def P(phrase):
    return frozenset(words(phrase))


def _sym(image, salience=5):
    return Symbol(image=image, kind="ambiguous", salience=salience, query=image)


def _names(entries):
    return [e.name for e in entries]


def test_an_image_matches_an_earlier_dream_tagged_with_it(dreams):
    _note(dreams, "2026-10-07", "chain-breaks", symbols=["silver-chain", "solder"])
    _note(dreams, "2026-10-08", "bus", symbols=["bus"])
    found = find_series([_sym("silver chain")], on_or_before=date(2026, 11, 1))
    assert _names(found) == ["2026-10-07-chain-breaks"]
    assert found[0].matched == ["silver chain"]


def test_plurals_and_stopwords_do_not_break_a_tag_match(dreams):
    _note(dreams, "2026-10-07", "chain-breaks", symbols=["silver-chain"])
    assert _names(find_series([_sym("my silver chains")], on_or_before=date(2026, 11, 1))) == [
        "2026-10-07-chain-breaks"]


def test_a_figure_tag_matches_the_person_named_as_an_image(dreams):
    _note(dreams, "2026-10-01", "walkout", figures=["father", "stepmom"])
    assert _names(find_series([_sym("my father")], on_or_before=date(2026, 11, 1))) == ["2026-10-01-walkout"]


def test_an_untagged_dream_matches_on_its_own_words(dreams):
    _note(dreams, "2026-08-01", "garden", text="A snake lies coiled under the steps. I step over it.")
    assert _names(find_series([_sym("snake")], on_or_before=date(2026, 11, 1))) == ["2026-08-01-garden"]


def test_a_many_word_image_needs_every_word_to_match_on_words(dreams):
    _note(dreams, "2026-08-01", "timing", text="The timing chain slips in the engine.")
    assert find_series([_sym("gold chain")], on_or_before=date(2026, 11, 1)) == []


def test_the_motif_vocabulary_groups_variants_of_an_image(dreams):
    (dreams / "motifs.md").write_text(MOTIFS_MD, encoding="utf-8")
    _note(dreams, "2026-07-23", "flood", text="Water rises over the platform.", motifs=["water"])
    _note(dreams, "2026-07-24", "dry", text="A desert.", motifs=["mountain"])
    found = find_series([_sym("river")], on_or_before=date(2026, 11, 1))
    assert _names(found) == ["2026-07-23-flood"]


def test_motif_map_reads_the_covers_column_as_phrases():
    m = motif_map(MOTIFS_MD)
    assert {P("river"), P("water"), P("standing water")} <= set(m["water"])
    assert {P("chain"), P("necklace"), P("jewelry store")} <= set(m["jewelry"])
    assert {P("snow"), P("ice")} <= set(m["snow-ice"])
    assert not any("added" in p or "2026" in p for p in m["jewelry"])


def test_plural_es_endings_are_reduced_to_the_word():
    m = motif_map("| `authority` | bosses, presidents |\n| `jewelry` | boxes, watches |")
    assert P("boss") in m["authority"] and P("president") in m["authority"]
    assert P("box") in m["jewelry"] and P("watch") in m["jewelry"]


def test_a_motif_named_in_two_words_needs_both_of_them(dreams):
    (dreams / "motifs.md").write_text("| `burning-man` | Burning Man |\n| `new-york` | NYC as setting |",
                                      encoding="utf-8")
    _note(dreams, "2026-08-03", "playa", motifs=["burning-man", "new-york"], text="Dust.")
    assert find_series([_sym("old man"), _sym("new car")], on_or_before=date(2026, 11, 1)) == []
    assert _names(find_series([_sym("NYC")], on_or_before=date(2026, 11, 1))) == ["2026-08-03-playa"]


def test_closer_matches_rank_first_then_the_most_recent(dreams):
    (dreams / "motifs.md").write_text(MOTIFS_MD, encoding="utf-8")
    _note(dreams, "2026-10-20", "motif-only", motifs=["jewelry"], text="A ring box.")
    _note(dreams, "2026-09-01", "words-old", text="My silver chain is on the table.")
    _note(dreams, "2026-10-01", "words-new", text="A silver chain, tangled.")
    _note(dreams, "2026-07-01", "tagged-old", symbols=["silver-chain"])
    found = recurrences("silver chain", load_series(dreams), motif_map(MOTIFS_MD))
    assert [d.name for d, _ in found] == ["2026-07-01-tagged-old", "2026-10-01-words-new",
                                          "2026-09-01-words-old", "2026-10-20-motif-only"]


def test_later_dreams_and_the_dream_itself_are_left_out(dreams):
    _note(dreams, "2026-10-01", "before", symbols=["bus"])
    _note(dreams, "2026-11-01", "same-night", symbols=["bus"])
    _note(dreams, "2026-11-01", "this-one", symbols=["bus"])
    _note(dreams, "2026-11-02", "after", symbols=["bus"])
    found = find_series([_sym("bus")], on_or_before=date(2026, 11, 1), exclude="2026-11-01-this-one")
    assert sorted(_names(found)) == ["2026-10-01-before", "2026-11-01-same-night"]


def test_test_and_imagination_entries_never_enter_the_series(dreams):
    _note(dreams, "2026-10-01", "real", symbols=["bus"])
    _note(dreams, "2026-10-02", "imported", symbols=["bus"], provenance="imported")
    _note(dreams, "2026-10-03", "pipeline-test", symbols=["bus"], provenance="test")
    _note(dreams, "2026-10-04", "active-imagination", symbols=["bus"], provenance="imagination")
    found = find_series([_sym("bus")], on_or_before=date(2026, 11, 1))
    assert sorted(_names(found)) == ["2026-10-01-real", "2026-10-02-imported"]


def test_low_salience_images_are_not_looked_up(dreams):
    _note(dreams, "2026-10-01", "bus", symbols=["bus"])
    assert find_series([_sym("bus", salience=1)], on_or_before=date(2026, 11, 1)) == []


def test_each_image_shows_its_closest_few_and_counts_the_rest(dreams):
    for day in range(1, 7):
        _note(dreams, f"2026-10-0{day}", f"bus-{day}", symbols=["bus"])
    found = find_series([_sym("bus")], on_or_before=date(2026, 11, 1), per_image=3)
    assert _names(found) == ["2026-10-06-bus-6", "2026-10-05-bus-5", "2026-10-04-bus-4"]
    assert found.counts == {"bus": 6}


def test_a_dream_matching_two_images_appears_once(dreams):
    _note(dreams, "2026-10-01", "both", symbols=["bus", "milk"])
    found = find_series([_sym("bus"), _sym("milk")], on_or_before=date(2026, 11, 1))
    assert _names(found) == ["2026-10-01-both"]
    assert found[0].matched == ["bus", "milk"]


def test_the_whole_series_is_capped(dreams):
    for day in range(1, 10):
        _note(dreams, f"2026-10-0{day}", f"d{day}", symbols=[f"img{day}"])
    found = find_series([_sym(f"img{day}") for day in range(1, 10)], on_or_before=date(2026, 11, 1),
                        max_dreams=4)
    assert len(found) == 4


def test_an_entry_carries_the_matching_lines_the_earlier_reading_and_the_verdict(dreams):
    _note(dreams, "2026-10-07", "chain", symbols=["silver-chain"],
          text="I'm at a counter. The silver chain breaks at the clasp. The jeweler shrugs.",
          compensation="The break compensates a belief that things hold on their own.",
          response="partial", response_note="The clasp part hit; the jeweler didn't.", agency=2)
    e = find_series([_sym("silver chain")], on_or_before=date(2026, 11, 1))[0]
    assert e.excerpt == "The silver chain breaks at the clasp."
    assert e.compensation.startswith("The break compensates")
    assert (e.response, e.response_note, e.agency) == ("partial", "The clasp part hit; the jeweler didn't.", 2.0)
    assert e.path == "wiki/dreams/2026-10-07-chain.md"
    assert e.date == date(2026, 10, 7)


def test_editorial_lines_and_markdown_stay_out_of_an_excerpt(dreams):
    _note(dreams, "2026-09-19", "dogs", symbols=["bus"],
          text="> Speech-to-text capture, lightly cleaned.\n\n**Scene 1: The bus.** I'm on a *bus* with "
               "[[2026-07-01-x|Ian]].\n\n### Part 2\n\nThe bus stops.")
    e = find_series([_sym("bus")], on_or_before=date(2026, 11, 1))[0]
    assert e.excerpt == "Scene 1: The bus. I'm on a bus with Ian. The bus stops."


def test_an_excerpt_marks_the_gap_between_sentences_it_skips(dreams):
    _note(dreams, "2026-09-19", "gap", symbols=["bus"], text="A bus comes. I wait. Rain. The bus leaves.")
    e = find_series([_sym("bus")], on_or_before=date(2026, 11, 1))[0]
    assert e.excerpt == "A bus comes. … The bus leaves."


def test_an_excerpt_falls_back_to_the_opening_and_is_capped(dreams):
    _note(dreams, "2026-10-07", "long", symbols=["bus"], text="On a road. " + "Then more. " * 200)
    e = find_series([_sym("bus")], on_or_before=date(2026, 11, 1), excerpt_chars=80)[0]
    assert e.excerpt.startswith("On a road.") and len(e.excerpt) <= 81


def test_a_missing_dreams_folder_means_no_series(tmp_path):
    assert find_series([_sym("bus")], on_or_before=date(2026, 11, 1), dreams_dir=tmp_path / "nope") == []


def test_a_note_with_broken_frontmatter_is_skipped_not_fatal(dreams, capsys):
    _note(dreams, "2026-10-01", "good", symbols=["bus"])
    (dreams / "2026-10-02-bad.md").write_text("---\ntitle: [unclosed\n---\n\n## The Dream\n\nbus\n", encoding="utf-8")
    assert _names(find_series([_sym("bus")], on_or_before=date(2026, 11, 1))) == ["2026-10-01-good"]
    assert "2026-10-02-bad" in capsys.readouterr().err


def test_render_timeline_lists_every_occurrence_oldest_first(dreams):
    _note(dreams, "2026-10-07", "chain", symbols=["silver-chain"], text="The silver chain breaks.", agency=2,
          response="partial")
    _note(dreams, "2026-10-25", "father", symbols=["silver-chain"], text="I give my father the silver chain.",
          agency=4)
    out = render_timeline("silver chain", dreams_dir=dreams)
    assert out.index("2026-10-07") < out.index("2026-10-25")
    assert "2 dreams" in out and "agency 2" in out and "partial" in out
    assert "I give my father the silver chain." in out


def test_render_timeline_says_when_an_image_is_new(dreams):
    assert "no dream" in render_timeline("zeppelin", dreams_dir=dreams)


# --- the pipeline: the series is looked up after the images are settled, and the dreamer is told ---

def _stub_run(monkeypatch, seen, symbols=None):
    import contextlib
    import io

    from dreamapp import pipeline
    from dreamapp.models import Interpretation
    monkeypatch.setattr(pipeline, "extract_symbols", lambda text, **kw: symbols or [_sym("bus")])
    monkeypatch.setattr(pipeline, "retrieve_passages", lambda s: [])
    monkeypatch.setattr(pipeline, "search_cw", lambda queries: [])
    monkeypatch.setattr(pipeline, "method_canon", lambda: [])

    def synth(*a, series=None, **kw):
        seen["series"] = series
        return Interpretation(dramatic_structure="a", compensation="b", amplifications=[])

    monkeypatch.setattr(pipeline, "synthesize_interpretation", synth)
    monkeypatch.setattr(pipeline, "write_note", lambda *a, **k: None)
    return pipeline, contextlib.redirect_stdout(io.StringIO())


def test_a_run_sends_the_earlier_dreams_and_says_which(dreams, monkeypatch, capsys):
    _note(dreams, "2026-10-01", "before", symbols=["bus"])
    _note(dreams, "2026-11-05", "later", symbols=["bus"])
    seen = {}
    pipeline, quiet = _stub_run(monkeypatch, seen)
    with quiet:
        pipeline.run("A bus.", dry=True, date="2026-11-02")
    assert [e.name for e in seen["series"]] == ["2026-10-01-before"]
    err = capsys.readouterr().err
    assert "1 earlier dream" in err and "2026-10-01" in err and "--no-series" in err


def test_no_series_sends_none_and_reads_no_notes(dreams, monkeypatch, capsys):
    _note(dreams, "2026-10-01", "before", symbols=["bus"])
    seen = {}
    pipeline, quiet = _stub_run(monkeypatch, seen)
    monkeypatch.setattr(pipeline, "find_series", lambda *a, **k: pytest.fail("series read with --no-series"))
    with quiet:
        pipeline.run("A bus.", dry=True, series=False)
    assert seen["series"] is None
    assert "series:" not in capsys.readouterr().err


def test_reanalysing_a_note_leaves_it_out_and_dates_the_series_by_the_note(dreams, monkeypatch):
    _note(dreams, "2026-09-01", "before", symbols=["bus"])
    _note(dreams, "2026-11-01", "after", symbols=["bus"])
    target = _note(dreams, "2026-10-01", "target", symbols=["bus"], text="A bus.")
    seen = {}
    pipeline, quiet = _stub_run(monkeypatch, seen)
    with quiet:
        pipeline.run(target.read_text(encoding="utf-8"), source_path=str(target), dry=True, force=True)
    assert [e.name for e in seen["series"]] == ["2026-09-01-before"]


def test_the_series_uses_the_images_the_dreamer_kept(dreams, monkeypatch):
    _note(dreams, "2026-10-01", "bus", symbols=["bus"])
    _note(dreams, "2026-10-02", "snake", symbols=["snake"])
    seen = {}
    pipeline, quiet = _stub_run(monkeypatch, seen, symbols=[_sym("bus"), _sym("snake")])
    replies = iter(["", "", "", "d 1", "", ""])  # capture x3, drop 'bus', keep, one association skipped
    with quiet:
        pipeline.run("A bus and a snake.", dry=True, interactive=True, ask=lambda prompt: next(replies))
    assert [e.name for e in seen["series"]] == ["2026-10-02-snake"]


def test_cli_series_prints_the_timeline(dreams, monkeypatch, capsys):
    import sys

    from dreamapp import cli
    _note(dreams, "2026-10-07", "chain", symbols=["silver-chain"], text="The silver chain breaks.")
    monkeypatch.setattr(sys, "argv", ["dreamapp", "series", "silver chain"])
    assert cli.main() == 0
    out = capsys.readouterr().out
    assert "2026-10-07" in out and "The silver chain breaks." in out


def test_cli_passes_no_series_through(monkeypatch, tmp_path):
    import sys

    from dreamapp import cli
    seen = {}
    monkeypatch.setattr(cli, "run", lambda text, **kw: seen.update(kw) or
                        __import__("dreamapp.models", fromlist=["Interpretation"]).Interpretation("a", "b"))
    dream = tmp_path / "d.txt"
    dream.write_text("A bus.", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["dreamapp", "interpret", str(dream), "--dry", "--no-series"])
    assert cli.main() == 0
    assert seen["series"] is False


# --- motifs from extraction: the dreamer's own categories reach dreams no image word does ---

def test_a_motif_from_extraction_finds_dreams_tagged_with_it(dreams):
    _note(dreams, "2026-09-08", "bar", motifs=["substances"], text="Someone passes me a pill.")
    _note(dreams, "2026-09-09", "fish", motifs=["food"], text="Raw fish.")
    found = find_series([Symbol("xanax", "personal", 4, "drug", ["substances"])], on_or_before=date(2026, 11, 1))
    assert _names(found) == ["2026-09-08-bar"]
    assert found[0].matched == ["substances (motif)"]
    assert found.counts == {"substances (motif)": 1}


def test_images_claim_the_budget_before_motifs(dreams):
    _note(dreams, "2026-10-01", "bus", symbols=["bus"])
    _note(dreams, "2026-10-02", "car", motifs=["car"])
    found = find_series([Symbol("bus", "ambiguous", 5, "bus", ["car"])], on_or_before=date(2026, 11, 1),
                        max_dreams=1)
    assert _names(found) == ["2026-10-01-bus"]


def test_a_low_salience_images_motif_is_not_looked_up(dreams):
    _note(dreams, "2026-10-02", "car", motifs=["car"])
    assert find_series([Symbol("van", "ambiguous", 1, "van", ["car"])], on_or_before=date(2026, 11, 1)) == []


def test_a_motif_match_shows_the_sentence_that_carries_it(dreams):
    (dreams / "motifs.md").write_text(MOTIFS_MD.replace("| `jewelry`", "| `substances` | alcohol, drugs |\n| `jewelry`"),
                                      encoding="utf-8")
    _note(dreams, "2026-09-08", "bar", motifs=["substances"], text="A long hallway. There are drugs on the table.")
    e = find_series([Symbol("xanax", "personal", 4, "drug", ["substances"])], on_or_before=date(2026, 11, 1))[0]
    assert e.excerpt == "There are drugs on the table."


# --- verifier round: egress honesty, cutoff, counts, order, long sentences ---

def test_no_series_also_keeps_the_motif_vocabulary_back(dreams, monkeypatch):
    seen = {}
    pipeline, quiet = _stub_run(monkeypatch, seen)
    monkeypatch.setattr(pipeline, "extract_symbols", lambda text, **kw: seen.setdefault("kw", kw) and [_sym("bus")])
    with quiet:
        pipeline.run("A bus.", dry=True, series=False)
    assert seen["kw"] == {"motifs": False}


def test_the_disclosure_says_what_goes_with_each_earlier_dream(dreams, monkeypatch, capsys):
    _note(dreams, "2026-10-01", "before", symbols=["bus"])
    pipeline, quiet = _stub_run(monkeypatch, {})
    with quiet:
        pipeline.run("A bus.", dry=True, date="2026-11-02")
    err = capsys.readouterr().err
    assert "excerpts" in err and "readings" in err and "your responses" in err


def test_a_notes_own_date_bounds_its_series_even_with_a_later_date_flag(dreams, monkeypatch):
    _note(dreams, "2026-09-01", "before", symbols=["bus"])
    _note(dreams, "2026-11-01", "after", symbols=["bus"])
    target = _note(dreams, "2026-10-01", "target", symbols=["bus"], text="A bus.")
    seen = {}
    pipeline, quiet = _stub_run(monkeypatch, seen)
    with quiet:
        pipeline.run(target.read_text(encoding="utf-8"), source_path=str(target), dry=True, force=True,
                     date="2026-12-01")
    assert [e.name for e in seen["series"]] == ["2026-09-01-before"]


def test_an_image_with_hits_but_no_room_left_is_still_counted(dreams):
    for day in range(1, 4):
        _note(dreams, f"2026-10-0{day}", f"bus-{day}", symbols=["bus"])
    _note(dreams, "2026-09-01", "snake", symbols=["snake"])
    found = find_series([_sym("bus", 5), _sym("snake", 4)], on_or_before=date(2026, 11, 1), max_dreams=3)
    assert "snake" not in [m for e in found for m in e.matched]
    assert found.counts["snake"] == 1


def test_an_unpunctuated_dream_is_excerpted_around_the_image(dreams):
    _note(dreams, "2026-09-19", "run-on", symbols=["bus"],
          text=" ".join(["and then we walk"] * 60) + " and the bus pulls up and " + " ".join(["we keep going"] * 60))
    e = find_series([_sym("bus")], on_or_before=date(2026, 11, 1), excerpt_chars=120)[0]
    assert "bus" in e.excerpt and len(e.excerpt) <= 122


def test_cli_series_says_when_the_dreams_folder_is_missing(tmp_path, monkeypatch, capsys):
    import sys

    from dreamapp import cli
    monkeypatch.setattr(sys, "argv", ["dreamapp", "series", "bus", "--dreams-dir", str(tmp_path / "typo")])
    assert cli.main() == 2
    assert "no dreams folder" in capsys.readouterr().err


def test_normalising_gives_singular_and_plural_one_form():
    from dreamapp.notes import words
    for one, many in [("bus", "buses"), ("headache", "headaches"), ("axe", "axes"), ("die", "dies"),
                      ("city", "cities"), ("box", "boxes"), ("glass", "glasses"), ("house", "houses"),
                      ("church", "churches"), ("boy", "boys"), ("tree", "trees")]:
        assert words(one) == words(many), (one, many)


def test_normalising_never_merges_two_different_words():
    from dreamapp.notes import words
    for a, b in [("car", "care"), ("bar", "bare"), ("plan", "plane"), ("star", "stare"), ("ski", "skies"),
                 ("win", "wine"), ("hat", "hate"), ("cares", "car"), ("spin", "spine")]:
        assert words(a) != words(b), (a, b)


def test_normalising_meets_the_harder_plurals():
    from dreamapp.notes import words
    for one, many in [("sky", "skies"), ("fly", "flies"), ("movie", "movies"), ("beach", "beaches"),
                      ("care", "cares"), ("plane", "planes"), ("story", "stories"), ("key", "keys")]:
        assert words(one) == words(many), (one, many)


def test_a_new_case_b_input_is_dated_by_the_date_flag_not_its_own_frontmatter(dreams, monkeypatch, tmp_path):
    _note(dreams, "2026-11-20", "later", symbols=["bus"])
    draft = tmp_path / "draft.md"
    draft.write_text("---\ndate: 2026-10-01\n---\n\n## The Dream\n\nA bus.\n", encoding="utf-8")
    seen = {}
    pipeline, quiet = _stub_run(monkeypatch, seen)
    with quiet:
        pipeline.run(draft.read_text(encoding="utf-8"), source_path=str(draft), dry=True, date="2026-12-01")
    assert [e.name for e in seen["series"]] == ["2026-11-20-later"]
