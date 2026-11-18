"""Counted half of the periodic dream reviews (month / quarter / year).

Reads dream-entry frontmatter and a few body sections from wiki/dreams/ and
computes everything a review states as a number. Interpretation is left to
the /dream skill's Phase 5, which reads this output.
"""
import calendar
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import yaml

from .notes import dream_section, section, word_pairs, words

SERIES_PROVENANCES = ("dream", "fragment", "imported")  # test and imagination entries never enter a count
TRIPWIRE_MIN_READINGS = 3
# Method vocabulary and filler: in every reading by construction, so never the complaint a stuck reading repeats.
TRIPWIRE_STOP = {
    "dream", "dreamer", "conscious", "unconscious", "attitude", "compensation", "compensate",
    "compensating", "compensatory", "ego", "image", "figure", "reading", "scene", "level", "objective",
    "subjective", "psyche", "waking", "show", "material", "residue", "question", "part", "real", "against",
    "here", "there", "what", "but", "not", "no", "one", "two", "three", "first", "he", "him", "she", "they",
    "them", "we", "you", "scott", "without", "so", "than", "then", "just", "only", "more", "most", "much", "many",
    "when", "where", "who", "which", "how", "can", "has", "have", "had", "does", "do", "did", "being", "been",
    "out", "up", "down", "over", "again", "still", "also", "even", "way", "thing", "something", "nothing", "own",
    "same", "while", "toward", "through", "both", "each", "every", "too", "very", "all", "else", "if", "because",
    "about", "before", "after", "now", "will", "would", "isn", "doesn", "don", "line", "point", "side", "case",
    "kind", "sense", "less", "make", "made", "get", "give", "take", "say", "said", "keep",
}

GENERIC_FIGURES = {"unknown-woman", "unknown-man", "old-man", "old-woman"}
RESPONSES = ("clicks", "partial", "miss")
ACTION_STATES = ("yes", "partial", "no")
NO_ASSOC_FLAG = "Analyzed without associations"
ELEMENT_KEYWORDS = {
    "water": {"water", "snow", "ice", "river", "ocean", "beach", "flood", "rain", "lake", "pool", "sea", "boat",
              "pond", "swim", "underwater", "milk"},
    "fire": {"fire", "steam", "burning", "burn", "smoke", "arson", "fireworks", "capsaicin", "chilies", "refinery",
             "furnace", "lantern", "explosions"},
    "earth": {"rock", "rocks", "stone", "cliff", "cliffs", "mountain", "canyon", "soil", "mulch", "dirt", "aggregate",
              "desert", "sand", "dunes", "cave", "cavern"},
    "air": {"plane", "planes", "bombers", "sky", "flight", "bird", "airport", "wind", "drone", "stars"},
}


@dataclass
class Dream:
    name: str
    date: date
    title: str
    agency: float = None
    figures: list = field(default_factory=list)
    motifs: list = field(default_factory=list)
    symbols: list = field(default_factory=list)
    response: str = ""
    action_done: str = ""
    no_assoc: bool = False
    has_assoc: bool = True
    waking_action: str = ""
    feeling: str = ""
    provenance: str = "dream"
    text: str = ""
    compensation: str = ""
    response_note: str = ""
    path: Path = None


@dataclass
class Period:
    kind: str
    start: date
    end: date
    label: str


def period_from_spec(kind: str, spec: str) -> Period:
    if kind == "month":
        m = re.fullmatch(r"(\d{4})-(\d{2})", spec)
        if not m or not 1 <= int(m.group(2)) <= 12:
            raise ValueError(f"month must look like 2026-10, got {spec!r}")
        y, mo = int(m.group(1)), int(m.group(2))
        return Period("month", date(y, mo, 1), date(y, mo, calendar.monthrange(y, mo)[1]), f"{y}-{mo:02d}")
    if kind == "quarter":
        m = re.fullmatch(r"(\d{4})-Q([1-4])", spec)
        if not m:
            raise ValueError(f"quarter must look like 2026-Q3, got {spec!r}")
        y, q = int(m.group(1)), int(m.group(2))
        last = 3 * q
        return Period("quarter", date(y, last - 2, 1), date(y, last, calendar.monthrange(y, last)[1]), f"{y}-Q{q}")
    if kind == "year":
        if not re.fullmatch(r"\d{4}", spec):
            raise ValueError(f"year must look like 2026, got {spec!r}")
        y = int(spec)
        return Period("year", date(y, 1, 1), date(y, 12, 31), str(y))
    raise ValueError(f"unknown period kind {kind!r}")


def previous(p: Period) -> Period:
    before = p.start - timedelta(days=1)
    if p.kind == "month":
        return period_from_spec("month", f"{before.year}-{before.month:02d}")
    if p.kind == "quarter":
        return period_from_spec("quarter", f"{before.year}-Q{(before.month - 1) // 3 + 1}")
    return period_from_spec("year", str(before.year))


def _section(body: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\s*\n(.*?)(?=^---\s*$|^## |\Z)", body, re.S | re.M)
    if not m:
        return ""
    lines = [ln for ln in m.group(1).strip().splitlines()
             if not (ln.startswith(">") and ("[Pending" in ln or "One concrete thing" in ln))]
    return "\n".join(lines).strip()


def _has_associations(body: str) -> bool:
    lines = _section(body, "Waking Associations").splitlines()
    return any(ln.strip() not in ("", "-") and not ln.lstrip().startswith("> [") for ln in lines)


def _as_date(v) -> date:
    return v if isinstance(v, date) else date.fromisoformat(str(v))


def _as_state(v) -> str:
    # YAML 1.1 reads a bare `yes` / `no` as a boolean.
    if isinstance(v, bool):
        return "yes" if v else "no"
    return str(v or "").strip().lower()


def _as_list(v) -> list:
    return [str(x) for x in v] if isinstance(v, list) else []


def _load_one(path: Path):
    parts = path.read_text(encoding="utf-8").split("---", 2)
    if len(parts) < 3:
        return None
    fm = yaml.safe_load(parts[1]) or {}
    if not isinstance(fm, dict) or fm.get("type") != "dream":
        return None
    body = parts[2]
    agency = fm.get("agency")
    return Dream(
        name=path.stem,
        date=_as_date(fm.get("date")),
        title=str(fm.get("title") or path.stem),
        agency=float(agency) if isinstance(agency, (int, float)) and not isinstance(agency, bool) else None,
        figures=_as_list(fm.get("figures")),
        motifs=_as_list(fm.get("motifs")),
        symbols=_as_list(fm.get("symbols")),
        response=_as_state(fm.get("response")),
        action_done=_as_state(fm.get("action_done")),
        no_assoc=NO_ASSOC_FLAG in body,
        has_assoc=_has_associations(body),
        waking_action=_section(body, "Waking Action"),
        feeling=_section(body, "Feeling-Tone"),
        provenance=str(fm.get("provenance") or "dream").strip().lower(),
        text=dream_section(body),
        compensation=section(body, "Compensation", level=3),
        response_note=section(body, "Dreamer Response"),
        path=path,
    )


class Dreams(list):
    """The dream notes, oldest first, plus the names of notes that wouldn't parse."""

    def __init__(self, dreams=(), skipped=()):
        super().__init__(dreams)
        self.skipped = list(skipped)


def load_dreams(dreams_dir) -> Dreams:
    """Every dream note in the folder. A note that won't parse is reported and skipped: one bad file must
    not take down a review or a run, and the review names it so a count can't be quietly short."""
    dreams, skipped = [], []
    for path in sorted(Path(dreams_dir).glob("[0-9][0-9][0-9][0-9]-*.md")):
        try:
            d = _load_one(path)
        except (yaml.YAMLError, ValueError, TypeError, UnicodeDecodeError) as e:
            print(f"dreams: skipped {path.name}: {type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}",
                  file=sys.stderr)
            skipped.append(path.stem)
            continue
        if d is not None:
            dreams.append(d)
    return Dreams(sorted(dreams, key=lambda d: (d.date, d.name)), skipped)


def _mean(values):
    vals = [v for v in values if v is not None]
    return round(sum(vals) / len(vals), 2) if vals else None


def _within(dreams, p):
    return [d for d in dreams if p.start <= d.date <= p.end]


def _first_seen(dreams, attr):
    seen = {}
    for d in dreams:
        for x in getattr(d, attr):
            seen.setdefault(x, d)
    return seen


def _elements(d):
    tokens = set()
    for tag in d.motifs + d.symbols:
        tokens.add(tag)
        tokens.update(tag.split("-"))
    return {el for el, kws in ELEMENT_KEYWORDS.items() if tokens & kws}


def _months(p):
    out, y, m = [], p.start.year, p.start.month
    while date(y, m, 1) <= p.end:
        out.append(period_from_spec("month", f"{y}-{m:02d}"))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def _previous_watch(reviews_dir, prev):
    if not reviews_dir:
        return None
    path = Path(reviews_dir) / f"{prev.label}-{prev.kind}.md"
    if not path.is_file():
        return None
    body = path.read_text(encoding="utf-8")
    m = re.search(r"^## [^\n]*Watch[^\n]*\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    return {"path": str(path), "watch": m.group(1).strip() if m else ""}


_TRIPWIRE_STOP_FORMS = {n for w in TRIPWIRE_STOP for n in words(w)}


def _recurring(texts: list) -> list:
    """Content words in at least half the texts, and in TRIPWIRE_MIN_READINGS at minimum, each text counted once.
    Matched in normalised form ("monei"), shown as most often written ("money")."""
    if len(texts) < TRIPWIRE_MIN_READINGS:
        return []
    counts, written = Counter(), {}
    for t in texts:
        pairs = [(w, n) for w, n in word_pairs(t) if len(n) > 2 and not n.isdigit() and n not in _TRIPWIRE_STOP_FORMS]
        counts.update({n for _, n in pairs})
        for w, n in pairs:
            written.setdefault(n, Counter())[w] += 1
    floor = max(TRIPWIRE_MIN_READINGS, -(-len(texts) // 2))
    return [{"word": written[n].most_common(1)[0][0], "count": k}
            for n, k in sorted(counts.items(), key=lambda x: (-x[1], x[0])) if k >= floor]


def _lead(text: str) -> str:
    """The reading's opening, run on past a sentence too short to judge ("Two-sided.")."""
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    lead = sentences[0]
    for s in sentences[1:]:
        if len(lead) >= 40:
            break
        lead += " " + s
    return lead if len(lead) <= 200 else lead[:200].rstrip() + "…"


def _tripwire(inp) -> dict:
    """The counted half of the review's M23: what keeps coming back across a period's readings and waking actions.
    A complaint every reading lands on may be the interpreter's, not the dream's (design.md §2, Stage 4)."""
    readings = [d for d in inp if d.compensation]
    actions = [d.waking_action for d in inp if d.waking_action]
    return {"readings": len(readings), "compensation_words": _recurring([d.compensation for d in readings]),
            "actions": len(actions), "action_words": _recurring(actions),
            "leads": [{"dream": d.name, "lead": _lead(d.compensation)} for d in readings]}


def compute(dreams, period: Period, today: date = None, reviews_dir=None) -> dict:
    today = today or date.today()
    skipped = list(getattr(dreams, "skipped", []))
    left_out = sum(1 for d in _within(dreams, period) if d.provenance not in SERIES_PROVENANCES)
    dreams = [d for d in dreams if d.provenance in SERIES_PROVENANCES]
    prev = previous(period)
    inp = _within(dreams, period)
    before = [d for d in dreams if d.date < period.start]
    prev_dreams = _within(dreams, prev)

    partial = period.start <= today < period.end
    end = today if partial else period.end
    # A series that begins mid-period shouldn't be diluted by the days before its first dream.
    start = max(period.start, dreams[0].date) if dreams else period.start
    days = max((end - start).days + 1, 0)
    scored = [d.agency for d in inp if d.agency is not None]

    seen_before = {f for d in before for f in d.figures}
    in_period = Counter(f for d in inp for f in d.figures)
    in_prev = {f for d in prev_dreams for f in d.figures}
    first_fig = _first_seen(inp, "figures")
    new = [f for f in first_fig if f not in seen_before and f not in GENERIC_FIGURES]

    motifs_now = Counter(m for d in inp for m in d.motifs)
    motifs_prev = Counter(m for d in prev_dreams for m in d.motifs)
    motifs_before = {m for d in before for m in d.motifs}
    first_motif = _first_seen(inp, "motifs")
    rows = [{"motif": m, "count": motifs_now[m], "previous": motifs_prev[m], "delta": motifs_now[m] - motifs_prev[m]}
            for m in set(motifs_now) | set(motifs_prev)]
    rows.sort(key=lambda r: (-r["count"], -r["delta"], r["motif"]))

    symbols = Counter(s for d in inp for s in set(d.symbols))
    by_date = {}
    for d in inp:
        by_date.setdefault(d.date.isoformat(), []).append(d.name)

    elements = Counter(el for d in inp for el in _elements(d))
    stats = {
        "period": {"kind": period.kind, "label": period.label, "start": period.start.isoformat(),
                   "end": period.end.isoformat()},
        "previous_label": prev.label,
        "partial": partial,
        "numbers": {
            "dreams": len(inp),
            "scored": len(scored),
            "fragments": len(inp) - len(scored),
            "agency_mean": _mean(scored),
            "agency_mean_previous": _mean(d.agency for d in prev_dreams),
            "days": days,
            "cadence": round(len(inp) / days, 2) if days else None,
            "series_dreams_to_date": len([d for d in dreams if d.date <= period.end]),
        },
        "agency_series": [{"date": d.date.isoformat(), "name": d.name, "title": d.title, "agency": d.agency}
                          for d in inp],
        "months": [{"month": m.label, "dreams": len(_within(inp, m)),
                    "agency_mean": _mean(d.agency for d in _within(inp, m))}
                   for m in _months(period)] if period.kind != "month" else [],
        "cast": {
            "counts": dict(in_period.most_common()),
            "new": new,
            "returning": sorted(f for f in in_period if f in seen_before and f not in in_prev
                                and f not in GENERIC_FIGURES),
            "gone": sorted(f for f in in_prev if f not in in_period and f not in GENERIC_FIGURES),
        },
        "firsts": {
            "figures": [{"figure": f, "dream": first_fig[f].name} for f in new],
            "motifs": [{"motif": m, "dream": first_motif[m].name} for m in first_motif if m not in motifs_before],
        },
        "motifs": {"rows": rows, "new_in_series": [m for m in first_motif if m not in motifs_before]},
        "recurring_symbols": [{"symbol": s, "count": c}
                              for s, c in sorted(symbols.items(), key=lambda x: (-x[1], x[0])) if c >= 2],
        "stance": {
            "blocked_or_regressive": sum(1 for a in scored if a < 3),
            "engaged_incomplete": sum(1 for a in scored if 3 <= a < 4),
            "completed": sum(1 for a in scored if a >= 4),
            "unscored": len(inp) - len(scored),
            "leaving": sum(1 for d in inp if "leaving" in d.motifs),
            "fight": sum(1 for d in inp if "fight" in d.motifs),
        },
        "elements": {**{el: elements[el] for el in ELEMENT_KEYWORDS}, "note": "keyword heuristic over motifs+symbols"},
        "same_night": {k: v for k, v in by_date.items() if len(v) > 1},
        "feeling": [{"dream": d.name, "feeling": d.feeling} for d in inp if d.feeling],
        "hit_rate": {**{r: sum(1 for d in inp if d.response == r) for r in RESPONSES},
                     "unrated": sum(1 for d in inp if d.response not in RESPONSES)},
        "actions": {
            "counts": {**{s: sum(1 for d in inp if d.action_done == s) for s in ACTION_STATES},
                       "unchecked": sum(1 for d in inp if d.action_done not in ACTION_STATES)},
            "items": [{"dream": d.name, "action": d.waking_action, "done": d.action_done or None} for d in inp],
        },
        "association_debt": {"without_associations": sum(1 for d in inp if d.no_assoc or not d.has_assoc),
                             "dreams": len(inp)},
        "previous_review": _previous_watch(reviews_dir, prev),
        "tripwire": _tripwire(inp),
    }
    stats["numbers"]["left_out"] = left_out
    stats["numbers"]["skipped"] = skipped
    return stats


def _short(d: str) -> str:
    return d[5:] if len(d) == 10 else d


def render_markdown(s: dict) -> str:
    p, n = s["period"], s["numbers"]
    prev_mean = n["agency_mean_previous"]
    out = [f"# Counted half: {p['label']} ({p['kind']}{', partial' if s['partial'] else ''})", "",
           "## By the numbers", "",
           f"- Dreams: **{n['dreams']}** over {n['days']} days, {n['cadence']}/night"
           f" ({n['series_dreams_to_date']} in the series to date)",
           f"- Agency mean: **{n['agency_mean']}** across {n['scored']} scored ({n['fragments']} unscored)"
           f" · previous period ({s['previous_label']}): {prev_mean}"]
    if n.get("left_out"):
        out.append(f"- Left out of every count: {n['left_out']} entr{'y' if n['left_out'] == 1 else 'ies'} whose "
                   "provenance isn't dream, fragment or imported (test, imagination)")
    if n.get("skipped"):
        out.append(f"- Not counted, frontmatter won't parse: {', '.join(n['skipped'])}")
    out.append("")

    out += ["## Agency across the period", "", "| Date | Dream | Agency | |", "|---|---|---|---|"]
    for r in s["agency_series"]:
        a = r["agency"]
        bar = "█" * int(round(a)) if a is not None else "·"
        out.append(f"| {_short(r['date'])} | [[{r['name']}\\|{r['title'].split(' — ', 1)[-1]}]] | "
                   f"{'—' if a is None else (int(a) if a == int(a) else a)} | {bar} |")
    out.append("")

    if s["months"]:
        out += ["## Months", "", "| Month | Dreams | Agency mean |", "|---|---|---|"]
        out += [f"| {m['month']} | {m['dreams']} | {m['agency_mean'] if m['agency_mean'] is not None else '—'} |"
                for m in s["months"]]
        out.append("")

    c = s["cast"]
    out += ["## Cast", "", "- " + " · ".join(f"{f} {k}" for f, k in c["counts"].items()) if c["counts"] else "- none",
            f"- New to the series: {', '.join(c['new']) or 'none'}",
            f"- Returning after absence: {', '.join(c['returning']) or 'none'}",
            f"- Gone since {s['previous_label']}: {', '.join(c['gone']) or 'none'}", ""]

    f = s["firsts"]
    out += ["## Firsts (computed)", ""]
    out += [f"- figure **{x['figure']}**: [[{x['dream']}]]" for x in f["figures"]]
    out += [f"- motif **{x['motif']}**: [[{x['dream']}]]" for x in f["motifs"]]
    if not f["figures"] and not f["motifs"]:
        out.append("- none")
    out.append("")

    out += ["## Motifs", "", f"| Motif | {p['label']} | {s['previous_label']} | Δ |", "|---|---|---|---|"]
    out += [f"| {r['motif']} | {r['count']} | {r['previous']} | {'+' if r['delta'] > 0 else ''}{r['delta']} |"
            for r in s["motifs"]["rows"]]
    out.append("")

    out += ["## Recurring symbols", ""]
    out += [f"- {r['symbol']} ×{r['count']}" for r in s["recurring_symbols"]] or ["- none"]
    out.append("")

    st = s["stance"]
    out += ["## Stance", "",
            f"- Completed acts (4–5): {st['completed']} · engaged, incomplete (3): {st['engaged_incomplete']}"
            f" · blocked/regressive (1–2): {st['blocked_or_regressive']} · unscored: {st['unscored']}",
            f"- Exits (`leaving`): {st['leaving']} · fights (`fight`): {st['fight']}", ""]

    el = s["elements"]
    out += ["## Elements (heuristic)", "",
            " · ".join(f"{k} {el[k]}" for k in ELEMENT_KEYWORDS) + f" (dreams touching each; {el['note']})", ""]

    if s["same_night"]:
        out += ["## Same-night dreams", ""]
        out += [f"- {_short(k)}: " + ", ".join(f"[[{x}]]" for x in v) for k, v in s["same_night"].items()]
        out.append("")

    out += ["## Feeling-tone (as recorded)", ""]
    out += [f"- [[{x['dream']}]]: {x['feeling'].lstrip('> ').splitlines()[0]}" for x in s["feeling"]] or ["- none recorded"]
    out.append("")

    h = s["hit_rate"]
    out += ["## Hit rate", "", f"- Clicks {h['clicks']} · partial {h['partial']} · miss {h['miss']} · unrated {h['unrated']}", ""]

    a = s["actions"]
    out += ["## Waking-action ledger", "",
            f"- Done {a['counts']['yes']} · partial {a['counts']['partial']} · not done {a['counts']['no']}"
            f" · unchecked {a['counts']['unchecked']}", ""]
    for x in a["items"]:
        if x["action"]:
            first = x["action"].splitlines()[0]
            out.append(f"- [[{x['dream']}]] ({x['done'] or 'unchecked'}): {first}")
    out.append("")

    d = s["association_debt"]
    out += ["## Association debt", "", f"- {d['without_associations']} of {d['dreams']} analyzed without associations", ""]

    t = s["tripwire"]

    def _listed(found, total):
        return ", ".join(f"{w['word']} ({w['count']}/{total})" for w in found) or "none"
    out += ["## Interpreter tripwire (counted half of M23)", "",
            f"- Words in at least half of the {t['readings']} readings (Compensation), {TRIPWIRE_MIN_READINGS} at minimum: "
            f"{_listed(t['compensation_words'], t['readings'])}",
            f"- Words in at least half of the {t['actions']} waking actions, {TRIPWIRE_MIN_READINGS} at minimum: "
            f"{_listed(t['action_words'], t['actions'])}",
            "- A word most readings land on may be the interpreter's complaint, not the dream's.", "",
            "Each reading's opening line, in order:", ""]
    out += [f"- [[{x['dream']}]]: {x['lead']}" for x in t["leads"]] or ["- none"]
    out.append("")

    pr = s["previous_review"]
    out += ["## Previous review's watch list", ""]
    out += [pr["watch"] or "- (section empty)"] if pr else [f"- no review on file for {s['previous_label']}"]
    out.append("")
    return "\n".join(out)
