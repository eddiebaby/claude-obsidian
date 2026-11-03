#!/usr/bin/env python3
"""Offline retrieval benchmark: does CW search find the paragraphs the dream analyses actually cited?

Gold: every "CW 8 ¶305" / "CW 9i ¶¶155–158" / "CW 12 §405" in a dream page's Jungian Analysis,
for volumes in the corpus. Queries: what `dreamapp log` would send — one per symbol (the page's
frontmatter symbols, plus the Waking Associations bullet for that image when there is one) and
one for the dream text.

Caveat: the analyses were written with keyword search over the same chunks, so the gold leans
lexical and flatters BM25. Use it to compare strategies against each other, not as an absolute.

Prints aggregate numbers only; no dream text leaves the machine.

Usage: python dream-app/scripts/bench_retrieval.py [--top-k 8] [--dreams-dir wiki/dreams]
"""
import argparse
import re
import sys
from pathlib import Path

import frontmatter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dreamapp import config, cw  # noqa: E402

CITE_RE = re.compile(r"CW ?(8|9i|12|16)\s*(?:¶¶?|§§?|pars?\.?)\s*(\d+)(?:\s*[–-]\s*(\d+))?")
SECTION_RE = r"^## {}\s*\n(.*?)(?=^## |\Z)"


def section(body: str, heading: str) -> str:
    m = re.search(SECTION_RE.format(re.escape(heading)), body, re.S | re.M)
    return m.group(1).strip() if m else ""


def gold_citations(body: str) -> set:
    analysis = body[body.find("## Jungian Analysis"):] if "## Jungian Analysis" in body else ""
    gold = set()
    for vol, start, end in CITE_RE.findall(analysis):
        lo = int(start)
        hi = int(end) if end and 0 <= int(end) - lo <= 20 else lo
        gold.update((f"CW {vol}", p) for p in range(lo, hi + 1))
    return gold


def dream_queries(post, extracted=None) -> tuple:
    """(symbol queries, dream text) as the pipeline would build them.

    extracted: the extract stage's output for this dream ([{image, salience, query}]); without it the
    page's frontmatter symbols stand in, which lack the extract stage's step into Jung's vocabulary.
    """
    body = post.content
    dream = re.sub(r"^>.*$", "", section(body, "The Dream"), flags=re.M).strip()
    assoc = {}
    for line in section(body, "Waking Associations").splitlines():
        m = re.match(r"-\s*\*\*(.+?)\*\*\s*[—:-]\s*(.+)", line.strip())
        if m:
            assoc[m.group(1).lower()] = m.group(2)
    if extracted is None:
        pairs = [(str(s).replace("-", " "), str(s).replace("-", " ")) for s in post.metadata.get("symbols") or []]
    else:
        pairs = [(s["image"].lower(), s["query"]) for s in extracted if s["salience"] >= config.MIN_SALIENCE_FOR_RETRIEVAL]
    queries = []
    for image, query in pairs:
        extra = next((text for img, text in assoc.items() if set(img.split()) & set(image.split())), "")
        queries.append(f"{query} {extra}".strip())
    return queries, dream


def load_cases(dreams_dir: Path, extracted_by_dream=None) -> list:
    cases = []
    for path in sorted(dreams_dir.glob("20*.md")):
        post = frontmatter.loads(path.read_text(encoding="utf-8"))
        gold = gold_citations(post.content)
        if not gold:
            continue
        extracted = (extracted_by_dream or {}).get(path.stem) if extracted_by_dream is not None else None
        if extracted_by_dream is not None and extracted is None:
            continue
        symbols, dream = dream_queries(post, extracted)
        if dream:
            cases.append((path.stem, symbols, dream, gold))
    return cases


# --- strategies: (index, symbol queries, dream text, k) -> chunk indices, best first ---

def max_merge(idx, symbols, dream, k):
    """cw.search before 2026-11-02: each chunk's best score over all queries, global top k."""
    best = {}
    for q in symbols + [dream]:
        for i, s in enumerate(idx.scores(q)):
            if s > best.get(i, 0):
                best[i] = s
    return [i for i, _ in sorted(best.items(), key=lambda kv: -kv[1])[:k]]


def shipped(idx, symbols, dream, k):
    """What the pipeline runs now: cw.search itself (round-robin across queries), not a copy of it."""
    return cw.search(symbols + [dream], top_k=k, data_dir=config.CW_DATA_DIR)


def symbols_only(idx, symbols, dream, k):
    return max_merge(idx, symbols, "", k) if symbols else []


def dream_only(idx, symbols, dream, k):
    return max_merge(idx, [], dream, k)


STRATEGIES = {"max-merge (before)": max_merge, "cw.search (now)": shipped,
              "symbols only": symbols_only, "dream text only": dream_only}


def covered(idx, picked, gold) -> set:
    """Gold paragraphs inside the picked chunks; picked holds chunk indices or CWPassage objects."""
    hits = set()
    for item in picked:
        if isinstance(item, int):
            c = idx.chunks[item]
            vol, start, end = c["volume"], c.get("para_start"), c.get("para_end")
        else:
            vol, start, end = item.volume, item.para_start, item.para_end
        if start is None:
            continue
        hits.update((v, p) for v, p in gold if v == vol and start <= p <= end)
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-k", type=int, default=config.MAX_CW_CHUNKS)
    ap.add_argument("--dreams-dir", default=str(config.DREAMS_DIR))
    ap.add_argument("--queries", help="JSON {dream name: extract-stage symbols}; default: frontmatter symbols")
    args = ap.parse_args()

    import json
    extracted = json.loads(Path(args.queries).read_text(encoding="utf-8")) if args.queries else None
    idx = cw._index(config.CW_DATA_DIR)
    in_corpus = {c["volume"] for c in idx.chunks}
    cases = [(n, s, d, {g for g in gold if g[0] in in_corpus})
             for n, s, d, gold in load_cases(Path(args.dreams_dir), extracted)]
    cases = [c for c in cases if c[3]]
    canon = set(config.METHOD_CANON)
    total = sum(len(g) for *_, g in cases)
    image_total = sum(len(g - canon) for *_, g in cases)
    print(f"{len(cases)} dreams, {total} cited paragraphs in the corpus "
          f"({total - image_total} in the method canon, {image_total} image-specific); top-k = {args.top_k}\n")
    print(f"{'strategy':<22} {'retrieval only':>15} {'+ method canon':>15} {'image-specific':>15}")
    results = {}
    for name, strategy in STRATEGIES.items():
        alone, with_canon, image_found = 0, 0, 0
        for _, symbols, dream, gold in cases:
            hits = covered(idx, strategy(idx, symbols, dream, args.top_k), gold)
            alone += len(hits)
            with_canon += len(hits | (gold & canon))
            image_found += len(hits - canon)
        results[name] = (alone, with_canon)
        print(f"{name:<22} {alone:>9}/{total:<5} {with_canon:>9}/{total:<5} {image_found:>9}/{image_total:<5}")
    before, now = results["max-merge (before)"][0], results["cw.search (now)"][1]
    print(f"\ncited paragraphs reaching synthesis: before {before}/{total} (max-merge, no canon), "
          f"now {now}/{total} (cw.search + canon). The canon was chosen from this same gold set, so its "
          f"{total - image_total} are in-sample.")


if __name__ == "__main__":
    main()
