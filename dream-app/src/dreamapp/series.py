"""Series memory (design.md §3, feature 1): the dreamer's earlier dreams that share this dream's images.

Certainty comes only over a series, where later dreams correct the readings of earlier ones (CW 16 ¶322),
and the series is the vault's own dream notes. An image matches an earlier dream three ways, closest first:
a tag (`symbols:` or `figures:`) that is the image; every word of the image in the dream's tags or its own
text; a phrase listed for one of the dream's `motifs:` in wiki/dreams/motifs.md, the dreamer's own synonym map.
"""
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

from . import config
from .notes import words as _words
from .review import SERIES_PROVENANCES, load_dreams

EXACT, WORDS, MOTIF = 3, 2, 1
LEVEL_NAMES = {EXACT: "tag", WORDS: "words", MOTIF: "motif"}
# Words in motifs.md's "Covers" column that describe the motif rather than name an image.
_COVERS_STOP = {"thing", "noticed", "explicit", "outside", "dream", "figure", "people", "seen", "setting",
                "symbol", "returning"}


_MOTIF_ROW = re.compile(r"^\|\s*`([a-z0-9-]+)`\s*\|([^|\n]*)\|", re.M)


def motif_vocabulary(dreams_dir=None) -> list:
    """(tag, what it covers) for each motif in wiki/dreams/motifs.md; [] when the vault has none."""
    p = Path(dreams_dir or config.DREAMS_DIR) / "motifs.md"
    if not p.is_file():
        return []
    return [(m.group(1), re.sub(r"\s+", " ", re.sub(r"\([^)]*\)", "", m.group(2))).strip())
            for m in _MOTIF_ROW.finditer(p.read_text(encoding="utf-8"))]


def _phrase(text: str) -> frozenset:
    return frozenset(w for w in _words(text) if not w.isdigit() and w not in _COVERS_STOP)


def motif_map(motifs_md: str) -> dict:
    """motif -> the phrases that name it: the tag itself and each entry of its Covers column.

    A phrase matches an image holding all its words, so `burning-man` needs both "burning" and "man", and
    "standing water" needs both, while the single entry "water" matches on its own."""
    out = {}
    for m in _MOTIF_ROW.finditer(motifs_md):
        covers = re.sub(r"\([^)]*\)", " ", m.group(2))
        parts = [m.group(1).replace("-", " ")] + re.split(r",|;|:|\bor\b|\band\b", covers)
        out[m.group(1)] = [p for p in dict.fromkeys(_phrase(part) for part in parts) if p]
    return out


def load_series(dreams_dir=None) -> list:
    """The dream notes that count as the series, oldest first."""
    dreams_dir = Path(dreams_dir or config.DREAMS_DIR)
    if not dreams_dir.is_dir():
        return []
    return [d for d in load_dreams(dreams_dir) if d.provenance in SERIES_PROVENANCES]


def _motifs_for(dreams_dir: Path) -> dict:
    p = dreams_dir / "motifs.md"
    return motif_map(p.read_text(encoding="utf-8")) if p.is_file() else {}


def _level(key: tuple, d, mmap: dict) -> int:
    tags = d.symbols + d.figures
    if key in {tuple(_words(t.replace("-", " "))) for t in tags}:
        return EXACT
    if set(key) <= set(_words(" ".join(t.replace("-", " ") for t in tags) + " " + d.text)):
        return WORDS
    if _matched_motifs([set(key)], d, mmap):
        return MOTIF
    return 0


def _matched_motifs(keys: list, d, mmap: dict) -> list:
    return [m for m in d.motifs if any(p <= k for p in mmap.get(m, ()) for k in keys)]


def recurrences(image: str, dreams: list, mmap: dict) -> list:
    """(dream, level) for every dream the image matches, closest match first, then the most recent."""
    key = tuple(_words(image))
    if not key:
        return []
    hits = [(d, lv) for d in dreams if (lv := _level(key, d, mmap))]
    return sorted(hits, key=lambda h: (-h[1], -h[0].date.toordinal(), h[0].name))


@dataclass
class SeriesEntry:
    name: str
    date: date
    title: str
    path: str  # vault-relative, the form a source is cited in
    excerpt: str
    compensation: str
    response: str
    response_note: str
    agency: Optional[float]
    matched: list = field(default_factory=list)  # this dream's images it shares


class Series(list):
    """The entries shown, plus how many earlier dreams each image matched in all."""

    def __init__(self, entries=(), counts=None):
        super().__init__(entries)
        self.counts = counts or {}


def _clip(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def _plain(text: str) -> str:
    """The dreamer's words without the note's markup: editorial '>' lines, headings, emphasis, link syntax."""
    lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith((">", "#"))]
    text = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", "\n".join(lines))
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    return re.sub(r"\s+", " ", text.replace("**", "").replace("*", "")).strip()


def _excerpt(d, images: list, mmap: dict, limit: int) -> str:
    """The dream's own sentences that hold the image; its opening when none does (a tag or motif match).
    Adjacent sentences run on; a skipped stretch shows as ' … '."""
    plain = _plain(d.text)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", plain) if s]
    keys = [set(_words(i)) for i in images]
    near = set().union(*keys, *(p for m in _matched_motifs(keys, d, mmap) for p in mmap[m]))
    picked = [n for n, s in enumerate(sentences) if any(k and k <= set(_words(s)) for k in keys)]
    picked = picked or [n for n, s in enumerate(sentences) if near & set(_words(s))]
    if not picked:
        return _clip(plain, limit)
    out = sentences[picked[0]]
    for prev, n in zip(picked, picked[1:]):
        out += (" " if n == prev + 1 else " … ") + sentences[n]
    return _window(out, near, limit)


def _window(text: str, terms: set, limit: int) -> str:
    """Clip around the first word the excerpt is for: an unpunctuated speech-to-text dream is one sentence,
    and cutting it from the start can drop the image."""
    if len(text) <= limit:
        return text
    at = next((m.start() for m in re.finditer(r"[A-Za-z0-9']+", text) if set(_words(m.group())) & terms), 0)
    start = max(0, min(at - limit // 3, len(text) - limit))
    piece = text[start:start + limit].strip()
    return ("…" if start > 0 else "") + piece + ("…" if start + limit < len(text) else "")


def _vault_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(config.VAULT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


MOTIF_SUFFIX = " (motif)"


def _label_words(label: str) -> str:
    """The words an excerpt looks for: an image as written, a motif label as its tag."""
    return label[:-len(MOTIF_SUFFIX)].replace("-", " ") if label.endswith(MOTIF_SUFFIX) else label


def find_series(symbols, *, on_or_before: date, exclude: str = None, dreams_dir=None,
                per_image: int = None, max_dreams: int = None, excerpt_chars: int = None,
                min_salience: int = None) -> Series:
    """Earlier dreams (and same-night ones) sharing the salient images, the closest few per image; then,
    with what budget is left, the most recent few tagged with each motif extraction found."""
    per_image = per_image or config.MAX_SERIES_PER_IMAGE
    max_dreams = max_dreams or config.MAX_SERIES_DREAMS
    excerpt_chars = excerpt_chars or config.MAX_CHARS_SERIES_EXCERPT
    min_salience = config.MIN_SALIENCE_FOR_RETRIEVAL if min_salience is None else min_salience
    dreams_dir = Path(dreams_dir or config.DREAMS_DIR)
    dreams = [d for d in load_series(dreams_dir) if d.date <= on_or_before and d.name != exclude]
    if not dreams:
        return Series()
    mmap = _motifs_for(dreams_dir)
    salient = [s for s in sorted(symbols, key=lambda s: -s.salience) if s.salience >= min_salience]
    newest_first = sorted(dreams, key=lambda d: (-d.date.toordinal(), d.name))
    lookups = [(s.image, recurrences(s.image, dreams, mmap)) for s in salient]
    lookups += [(m + MOTIF_SUFFIX, [(d, MOTIF) for d in newest_first if m in d.motifs])
                for m in dict.fromkeys(m for s in salient for m in s.motifs)]

    picked, counts = {}, {}
    for label, hits in lookups:
        if not hits:
            continue
        counts[label] = len(hits)
        for d, _ in hits[:per_image]:
            if d.name in picked:
                if label not in picked[d.name][1]:
                    picked[d.name][1].append(label)
            elif len(picked) < max_dreams:
                picked[d.name] = (d, [label])

    entries = [SeriesEntry(name=d.name, date=d.date, title=d.title, path=_vault_path(d.path),
                           excerpt=_excerpt(d, [_label_words(x) for x in labels], mmap, excerpt_chars),
                           compensation=_clip(d.compensation, config.MAX_CHARS_SERIES_READING),
                           response=d.response, response_note=_clip(d.response_note, config.MAX_CHARS_SERIES_READING),
                           agency=d.agency, matched=labels)
               for d, labels in picked.values()]
    return Series(entries, counts)


def _short_title(title: str) -> str:
    return title.split(" — ", 1)[-1]


def render_timeline(image: str, dreams_dir=None) -> str:
    """Every dream in the series holding the image, oldest first: how its role and affect move (motif drift)."""
    dreams_dir = Path(dreams_dir or config.DREAMS_DIR)
    dreams = load_series(dreams_dir)
    mmap = _motifs_for(dreams_dir) if dreams_dir.is_dir() else {}
    hits = sorted(recurrences(image, dreams, mmap), key=lambda h: (h[0].date, h[0].name))
    if not hits:
        return f"{image}: no dream in the series holds this image yet."
    by_level = {name: sum(1 for _, lv in hits if LEVEL_NAMES[lv] == name) for name in LEVEL_NAMES.values()}
    how = ", ".join(f"{name} {n}" for name, n in by_level.items() if n)
    out = [f"{image}: {len(hits)} dream{'s' if len(hits) != 1 else ''} in the series ({how})", ""]
    for d, lv in hits:
        agency = f"agency {int(d.agency) if d.agency == int(d.agency) else d.agency}" if d.agency is not None else "agency —"
        verdict = d.response or "unrated"
        out.append(f"{d.date.isoformat()}  {_short_title(d.title)}  ·  {agency}  ·  {verdict}  ·  [{LEVEL_NAMES[lv]}]")
        out.append(f"    {_excerpt(d, [image], mmap, config.MAX_CHARS_SERIES_EXCERPT)}")
        feeling = [ln for ln in d.feeling.splitlines() if ln.strip() and not ln.lstrip().startswith("> [")]
        if feeling:
            out.append(f"    feeling: {_clip(feeling[0].lstrip('> '), 120)}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"
