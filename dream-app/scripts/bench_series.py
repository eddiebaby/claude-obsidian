#!/usr/bin/env python3
"""Offline series benchmark: does series.find_series find the earlier dreams the analyses tied each dream to?

Gold: every earlier dream a page's "### Series Context" names, as a wikilink ([[2026-10-07-...]]) or a
short date ("10-07", "10-01b"), resolved to the dates of dreams on file. Scored by date, since "10-01b"
names one of two dreams that night without saying which file. Images: what extraction would hand the
lookup, stood in for by the page's own frontmatter (figures first, then symbols, ten at most).

Caveat: the same analyses assigned the tags, often while reading dream-threads, so tag matching is
flattered. Compare strategies against each other, not as an absolute. Precision is a floor: a Series
Context names the priors it chose to discuss, not every one that shares an image.

Prints aggregate numbers only; no dream text leaves the machine.

Usage: python dream-app/scripts/bench_series.py [--dreams-dir wiki/dreams]
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dreamapp import config, series  # noqa: E402
from dreamapp.models import Symbol  # noqa: E402
from dreamapp.notes import section  # noqa: E402

LINK_RE = re.compile(r"\[\[(\d{4}-\d{2}-\d{2})-[^\]|]*(?:\|[^\]]*)?\]\]")
SHORT_RE = re.compile(r"(?<![\d-])(\d{2})-(\d{2})[a-z]?(?![\d-])")
MAX_IMAGES = 10


def gold_dates(body: str, dream, on_file: set) -> set:
    text = section(body, "Series Context", level=3)
    found = {date.fromisoformat(d) for d in LINK_RE.findall(text)}
    for mm, dd in SHORT_RE.findall(LINK_RE.sub(" ", text)):
        try:
            found.add(date(dream.date.year, int(mm), int(dd)))
        except ValueError:
            continue
    return {d for d in found if d in on_file and d <= dream.date and d != dream.date}


def images(dream, with_motifs=False) -> list:
    """with_motifs: extraction's motif tags, stood in for by the page's own (an upper bound on tagging)."""
    tags = list(dict.fromkeys(dream.figures + dream.symbols))[:MAX_IMAGES]
    out = [Symbol(image=t.replace("-", " "), kind="ambiguous", salience=5, query=t.replace("-", " ")) for t in tags]
    if with_motifs and out:
        out[0].motifs = list(dream.motifs)
    return out


def _restricted(full, levels):
    def level(key, d, mmap):
        lv = full(key, d, mmap)
        return lv if lv in levels else 0
    return level


def run(dreams_dir: Path):
    every = series.load_series(dreams_dir)
    on_file = {d.date for d in every}
    cases = []
    for d in every:
        gold = gold_dates(d.path.read_text(encoding="utf-8"), d, on_file)
        if gold:
            cases.append((d, gold))
    if not cases:
        sys.exit("no dream page has a Series Context naming an earlier dream on file")

    every_level = {series.EXACT, series.WORDS, series.MOTIF}
    now = config.MAX_SERIES_DREAMS
    strategies = [  # (label, match levels or None for recency, dreams sent at most, extraction's motifs)
        ("recency only, 8 dreams", None, 8, False),
        (f"recency only, {now}", None, now, False),
        ("tags only, 8", {series.EXACT}, 8, False),
        ("tags + words, 8", {series.EXACT, series.WORDS}, 8, False),
        ("+ motif phrases, 8", every_level, 8, False),
        ("+ extraction's motifs*, 8", every_level, 8, True),
        (f"+ extraction's motifs*, {now} (now)", every_level, now, True),
    ]
    gold_total = sum(len(g) for _, g in cases)
    print(f"{len(cases)} dreams with a Series Context naming earlier dreams; {gold_total} earlier dream-dates named\n")
    print(f"{'strategy':34} {'found':>9} {'recall':>7} {'sent/run':>9} {'named':>6}")
    original = series._level
    try:
        for label, levels, max_dreams, with_motifs in strategies:
            hit = sent = named = 0
            for d, gold in cases:
                if levels is None:
                    earlier = [x for x in every if x.date <= d.date and x.name != d.name]
                    picked = {x.date for x in earlier[-max_dreams:]}
                    n = min(len(earlier), max_dreams)
                else:
                    series._level = _restricted(original, levels)
                    found = series.find_series(images(d, with_motifs), on_or_before=d.date, exclude=d.name,
                                               dreams_dir=dreams_dir, max_dreams=max_dreams)
                    picked, n = {e.date for e in found}, len(found)
                hit += len(gold & picked)
                sent += n
                named += len({x for x in picked if x in gold})
            print(f"{label:34} {hit:>4}/{gold_total:<4} {hit / gold_total:>7.0%} {sent / len(cases):>9.1f} "
                  f"{named / max(sent, 1):>6.0%}")
    finally:
        series._level = original
    print("\n* the page's own motifs stand in for extraction's: an upper bound until an API run measures it.\n"
          "found: named earlier dream-dates the lookup returned. sent/run: earlier dreams sent per run.\n"
          "named: share of what was sent that the Series Context named (a floor on precision).")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dreams-dir", default=str(config.DREAMS_DIR))
    run(Path(ap.parse_args().dreams_dir))


if __name__ == "__main__":
    main()
