import json
import sys
from datetime import date

import pytest

from dreamapp import cli
from dreamapp.review import compute, load_dreams, period_from_spec, previous, render_markdown


def _write(d, day, slug, agency=None, figures=(), motifs=(), symbols=(), response="", action_done="",
           type_="dream", no_assoc=False, waking_action="Do one thing.", feeling="> [Pending]",
           assoc="- **Niky** — home the day before."):
    fm = [
        "---",
        f"name: {day}-{slug}",
        f"type: {type_}",
        f'title: "{day} — {slug}"',
        f"date: {day}",
        "status: analyzed",
        f"agency: {'' if agency is None else agency}",
        f"figures: [{', '.join(figures)}]",
        f"motifs: [{', '.join(motifs)}]",
        f"symbols: [{', '.join(symbols)}]",
        f"response: {response}",
        f"action_done: {action_done}",
        "---",
    ]
    flag = "> Analyzed without associations — lower confidence.\n" if no_assoc else ""
    assoc_section = f"## Waking Associations\n\n{assoc}\n\n" if assoc is not None else ""
    body = (f"\n# {day}\n\n## The Dream\n\nText.\n\n{assoc_section}## Feeling-Tone\n\n{feeling}\n\n---\n\n"
            f"## Jungian Analysis\n\n{flag}"
            f"\n### Agency\n\n**{agency}**\n\n---\n\n## Waking Action\n\n{waking_action}\n\n---\n\n## Dreamer Response\n\n")
    (d / f"{day}-{slug}.md").write_text("\n".join(fm) + body, encoding="utf-8")


def test_month_period_bounds():
    p = period_from_spec("month", "2026-10")
    assert (p.start, p.end, p.label) == (date(2026, 10, 1), date(2026, 10, 31), "2026-10")


def test_quarter_period_bounds():
    p = period_from_spec("quarter", "2026-Q3")
    assert (p.start, p.end) == (date(2026, 7, 1), date(2026, 9, 30))


def test_year_period_bounds():
    p = period_from_spec("year", "2026")
    assert (p.start, p.end) == (date(2026, 1, 1), date(2026, 12, 31))


def test_previous_month_crosses_year_boundary():
    assert previous(period_from_spec("month", "2026-01")).label == "2025-12"


def test_previous_quarter():
    assert previous(period_from_spec("quarter", "2026-Q1")).label == "2025-Q4"


def test_bad_spec_raises():
    with pytest.raises(ValueError):
        period_from_spec("month", "2026-13")


def test_load_skips_non_dream_types(tmp_path):
    _write(tmp_path, "2026-10-01", "real", agency=3)
    _write(tmp_path, "2026-10-02", "pipeline-test", agency=3, type_="dream-test")
    assert [d.name for d in load_dreams(tmp_path)] == ["2026-10-01-real"]


def test_agency_mean_ignores_unscored_fragments(tmp_path):
    _write(tmp_path, "2026-10-01", "a", agency=2)
    _write(tmp_path, "2026-10-02", "b", agency=4)
    _write(tmp_path, "2026-10-03", "fragment")
    s = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))
    assert s["numbers"]["dreams"] == 3
    assert s["numbers"]["scored"] == 2
    assert s["numbers"]["agency_mean"] == 3.0


def test_agency_change_against_previous_period(tmp_path):
    _write(tmp_path, "2026-09-10", "sept", agency=2)
    _write(tmp_path, "2026-10-10", "oct", agency=4)
    s = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))
    assert s["numbers"]["agency_mean_previous"] == 2.0


def test_partial_period_cadence_uses_days_elapsed(tmp_path):
    for day in ("2026-11-01", "2026-11-02"):
        _write(tmp_path, day, "x", agency=3)
    s = compute(load_dreams(tmp_path), period_from_spec("month", "2026-11"), today=date(2026, 11, 4))
    assert s["partial"] is True
    assert s["numbers"]["days"] == 4
    assert s["numbers"]["cadence"] == 0.5


def test_cadence_counts_from_series_start_when_it_falls_inside_period(tmp_path):
    _write(tmp_path, "2026-06-25", "first", agency=1)
    _write(tmp_path, "2026-06-30", "second", agency=2)
    n = compute(load_dreams(tmp_path), period_from_spec("month", "2026-06"))["numbers"]
    assert (n["days"], n["cadence"]) == (6, 0.33)


def test_new_and_gone_figures_exclude_generic_figures(tmp_path):
    _write(tmp_path, "2026-09-10", "sept", figures=["sharon", "unknown-woman", "niky"])
    _write(tmp_path, "2026-10-10", "oct", figures=["martin", "unknown-man", "niky"])
    cast = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))["cast"]
    assert cast["new"] == ["martin"]
    assert cast["gone"] == ["sharon"]
    assert cast["counts"]["unknown-man"] == 1


def test_motif_deltas_against_previous_period(tmp_path):
    _write(tmp_path, "2026-09-10", "s1", motifs=["water", "car"])
    _write(tmp_path, "2026-09-11", "s2", motifs=["water"])
    _write(tmp_path, "2026-10-10", "o1", motifs=["car", "family"])
    _write(tmp_path, "2026-10-11", "o2", motifs=["car"])
    m = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))["motifs"]
    rows = {r["motif"]: r for r in m["rows"]}
    assert (rows["car"]["count"], rows["car"]["previous"]) == (2, 1)
    assert (rows["water"]["count"], rows["water"]["previous"]) == (0, 2)
    assert m["new_in_series"] == ["family"]


def test_hit_rate_counts_responses_and_unrated(tmp_path):
    _write(tmp_path, "2026-10-01", "a", response="clicks")
    _write(tmp_path, "2026-10-02", "b", response="miss")
    _write(tmp_path, "2026-10-03", "c")
    hr = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))["hit_rate"]
    assert hr == {"clicks": 1, "partial": 0, "miss": 1, "unrated": 1}


def test_association_debt_counts_flagged_entries(tmp_path):
    _write(tmp_path, "2026-10-01", "a", no_assoc=True)
    _write(tmp_path, "2026-10-02", "b")
    s = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))
    assert s["association_debt"] == {"without_associations": 1, "dreams": 2}


def test_association_debt_counts_entries_with_no_associations(tmp_path):
    _write(tmp_path, "2026-10-01", "missing-section", assoc=None)
    _write(tmp_path, "2026-10-02", "placeholder-only", assoc="> [To fill: who is Drew?]\n\n-")
    _write(tmp_path, "2026-10-03", "answered")
    s = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))
    assert s["association_debt"] == {"without_associations": 2, "dreams": 3}


def test_action_ledger_counts_and_lists_actions(tmp_path):
    _write(tmp_path, "2026-10-01", "a", action_done="yes", waking_action="Call your dad.")
    _write(tmp_path, "2026-10-02", "b", waking_action="Set a 9-minute timer.")
    led = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))["actions"]
    assert led["counts"] == {"yes": 1, "partial": 0, "no": 0, "unchecked": 1}
    assert led["items"][1]["action"] == "Set a 9-minute timer."


def test_same_night_groups(tmp_path):
    _write(tmp_path, "2026-10-11", "one")
    _write(tmp_path, "2026-10-11", "two")
    _write(tmp_path, "2026-10-12", "three")
    s = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))
    assert s["same_night"] == {"2026-10-11": ["2026-10-11-one", "2026-10-11-two"]}


def test_firsts_list_figures_first_seen_this_period(tmp_path):
    _write(tmp_path, "2026-09-10", "s", figures=["niky"])
    _write(tmp_path, "2026-10-10", "o", figures=["niky", "martin"])
    firsts = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))["firsts"]
    assert firsts["figures"] == [{"figure": "martin", "dream": "2026-10-10-o"}]


def test_recurring_symbols_within_period(tmp_path):
    _write(tmp_path, "2026-10-01", "a", symbols=["silver-chain", "bike"])
    _write(tmp_path, "2026-10-05", "b", symbols=["silver-chain"])
    rec = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))["recurring_symbols"]
    assert rec == [{"symbol": "silver-chain", "count": 2}]


def test_stance_bands(tmp_path):
    for i, a in enumerate((2, 3, 4, 5)):
        _write(tmp_path, f"2026-10-0{i + 1}", f"d{i}", agency=a)
    st = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))["stance"]
    assert st == {"blocked_or_regressive": 1, "engaged_incomplete": 1, "completed": 2, "unscored": 0,
                  "leaving": 0, "fight": 0}


def test_elements_heuristic_counts_dreams(tmp_path):
    _write(tmp_path, "2026-10-01", "a", motifs=["water"], symbols=["steam"])
    _write(tmp_path, "2026-10-02", "b", symbols=["rock-cliffs"])
    el = compute(load_dreams(tmp_path), period_from_spec("month", "2026-10"))["elements"]
    assert (el["water"], el["fire"], el["earth"], el["air"]) == (1, 1, 1, 0)


def test_quarter_has_month_breakdown(tmp_path):
    _write(tmp_path, "2026-07-01", "a", agency=2)
    _write(tmp_path, "2026-08-01", "b", agency=4)
    s = compute(load_dreams(tmp_path), period_from_spec("quarter", "2026-Q3"))
    assert [(m["month"], m["dreams"], m["agency_mean"]) for m in s["months"]] == [
        ("2026-07", 1, 2.0), ("2026-08", 1, 4.0), ("2026-09", 0, None)]


def test_render_markdown_has_counted_sections(tmp_path):
    _write(tmp_path, "2026-10-01", "a", agency=3, figures=["niky"], motifs=["car"])
    md = render_markdown(compute(load_dreams(tmp_path), period_from_spec("month", "2026-10")))
    for heading in ("## By the numbers", "## Agency across the period", "## Cast", "## Motifs",
                    "## Hit rate", "## Waking-action ledger", "## Association debt"):
        assert heading in md


def test_cli_review_writes_json(tmp_path, monkeypatch, capsys):
    _write(tmp_path, "2026-10-01", "a", agency=3)
    out = tmp_path / "stats.json"
    monkeypatch.setattr(sys, "argv", ["dreamapp", "review", "--month", "2026-10", "--dreams-dir", str(tmp_path),
                                      "--json", str(out), "--today", "2026-11-01"])
    assert cli.main() == 0
    assert json.loads(out.read_text(encoding="utf-8"))["numbers"]["dreams"] == 1
    assert "## By the numbers" in capsys.readouterr().out
