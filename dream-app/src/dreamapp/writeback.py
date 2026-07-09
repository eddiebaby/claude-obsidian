import datetime
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

from . import config

_FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?\r?\n)---\r?\n", re.DOTALL)
_STOPWORDS = {"a", "an", "the", "of", "in", "on", "at", "and", "to", "is", "was",
              "i", "my", "me", "it", "this", "that", "with", "for", "as", "be", "am", "were", "are"}
_ARCHETYPE_TERMS = [
    ("wise old man", "wise-old-man"), ("great mother", "great-mother"),
    ("mother", "mother"), ("father", "father"), ("shadow", "shadow"),
    ("persona", "persona"), ("anima", "anima"), ("animus", "animus"),
    ("self", "self"), ("trickster", "trickster"), ("hero", "hero"),
    ("child", "child"), ("puer", "puer"), ("senex", "senex"),
]


class WritebackError(Exception):
    pass


def _dedupe_preserve(items):
    seen, out = set(), []
    for i in items:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def _kebab(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.strip().lower())
    return s.strip("-")


def _slug(title, dream_text) -> str:
    source = title if title else dream_text
    words = re.findall(r"[A-Za-z0-9']+", source.lower())
    if not title:
        words = [w for w in words if w not in _STOPWORDS] or words
    slug = re.sub(r"[^a-z0-9-]", "", "-".join(words[:5]))
    slug = re.sub(r"-+", "-", slug).strip("-")
    return (slug or "dream")[:40].rstrip("-")


def _new_note_path(date_str, slug) -> Path:
    base = f"{date_str}-{slug}"
    candidate = config.DREAMS_DIR / f"{base}.md"
    n = 2
    while candidate.exists():
        candidate = config.DREAMS_DIR / f"{base}-{n}.md"
        n += 1
    return candidate


def _derive_archetypes(interpretation) -> list:
    parts = [interpretation.dramatic_structure, interpretation.compensation,
             interpretation.objective_level, interpretation.subjective_level,
             interpretation.movement, interpretation.question]
    for a in interpretation.amplifications:
        parts += [a.corpus_says, a.personal_reading, a.archetypal_reading]
    blob = " ".join(p for p in parts if p).lower()
    found = []
    for phrase, tag in _ARCHETYPE_TERMS:
        if tag not in found and re.search(r"\b" + re.escape(phrase) + r"\b", blob):
            found.append(tag)
    return found


def _render_analysis_section(interpretation) -> str:
    lines = ["## Jungian Analysis", "", "### Dramatic Structure", interpretation.dramatic_structure, ""]
    lines += ["### Symbols & Amplification", ""]
    for a in interpretation.amplifications:
        entry = f"**{a.symbol}** — {a.corpus_says} / {a.personal_reading} / {a.archetypal_reading}"
        if a.thin_coverage:
            entry += " (corpus thin here)"
        lines.append(f"- {entry}")
    lines += ["", "### Archetypal Figures", ""]
    for a in interpretation.amplifications:
        if a.archetypal_reading.strip():
            lines.append(f"- **{a.symbol}**: {a.archetypal_reading}")
    lines += ["", "### Compensation / What the Unconscious Is Saying", interpretation.compensation, ""]
    lines += [f"**Objective level:** {interpretation.objective_level}", "",
              f"**Subjective level:** {interpretation.subjective_level}", ""]
    lines += ["### Movement Toward Individuation", interpretation.movement, ""]
    lines += ["### Open Questions", interpretation.question, ""]
    lines += ["### Sources", ""]
    for src in interpretation.sources:
        lines.append(f"- [[{Path(src).stem}]]")
    return "\n".join(lines).rstrip() + "\n"


def _render_new_note_body(dream_text, analysis, date_str, dayname) -> str:
    parts = [f"# {date_str} {dayname}", "", "## The Dream", "", dream_text.strip(), "",
             "## Waking Associations", "", "## Feeling-Tone", "", "## Day Residue", "",
             "---", "", analysis]
    return "\n".join(parts)


def _render_frontmatter(name, title, date_str, symbols, archetypes, related) -> str:
    lines = ["---", f"name: {name}", "type: dream", f'title: "{title}"',
              f"date: {date_str}", f"created: {date_str}", f"updated: {date_str}",
              "tags:", "  - dream", "status: analyzed", "mood:", "sleep:",
              "recurring: false", "lucid: false",
              f"archetypes: [{', '.join(archetypes)}]", f"symbols: [{', '.join(symbols)}]"]
    lines.append("related:" if related else "related: []")
    for r in related:
        lines.append(f'  - "{r}"')
    lines.append("---")
    return "\n".join(lines) + "\n"


def _render_related_block(related) -> str:
    if not related:
        return "related: []\n"
    out = ["related:\n"]
    for r in related:
        out.append(f'  - "{r}"\n')
    return "".join(out)


def _split_frontmatter(raw: str):
    m = _FRONTMATTER_RE.match(raw)
    if not m:
        raise WritebackError("no frontmatter found")
    return m.group(1), raw[m.end():]


def _patch_frontmatter_keys(fm_text: str, patches: dict) -> str:
    # Line-based regex patching, not a full YAML round-trip — preserves every
    # untouched key's exact formatting (required by the Case A byte-for-byte
    # contract) but won't handle folded/multi-line scalar values for the keys
    # being patched. Fine for Phase 0's flat key set; revisit if that changes.
    lines = fm_text.splitlines(keepends=True)
    out, i, n = [], 0, len(lines)
    key_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):")
    while i < n:
        m = key_re.match(lines[i])
        if m and m.group(1) in patches:
            i += 1
            while i < n and lines[i][:1] in (" ", "\t"):
                i += 1
            out.append(patches[m.group(1)])
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def _analysis_nonempty(section_text: str) -> bool:
    for line in section_text.splitlines()[1:]:
        s = line.strip()
        if s and not s.startswith(("#", ">", "[!")):
            return True
    return False


def _acquire_lock(vault_rel_path: str):
    bash = shutil.which("bash")
    if not bash:
        print("writeback: bash not found on PATH, proceeding without lock", file=sys.stderr)
        return
    for attempt in range(3):
        r = subprocess.run([bash, str(config.LOCK_SCRIPT), "acquire", vault_rel_path],
                            cwd=config.VAULT_ROOT, capture_output=True, text=True)
        if r.returncode == 0:
            return
        if r.returncode == 75 and attempt < 2:
            time.sleep(5)
            continue
        hint = ""
        if r.returncode not in (0, 75):
            hint = (" (if this persists, check for a stuck "
                    ".vault-meta/.wiki-lock.meta.d directory left by a crashed process)")
        raise WritebackError(f"could not acquire lock on {vault_rel_path}: {r.stderr.strip()}{hint}")


def _release_lock(vault_rel_path: str):
    bash = shutil.which("bash")
    if not bash:
        return
    subprocess.run([bash, str(config.LOCK_SCRIPT), "release", vault_rel_path],
                    cwd=config.VAULT_ROOT, capture_output=True, text=True)


def _write_case_b(dream_text, interpretation, symbols, *, dry, title, date) -> Path:
    date_str = date or datetime.date.today().isoformat()
    try:
        d = datetime.date.fromisoformat(date_str)
    except ValueError as e:
        raise WritebackError(f"bad date {date_str!r}: {e}") from e

    slug = _slug(title, dream_text)
    path = _new_note_path(date_str, slug)
    symbol_tags = _dedupe_preserve([_kebab(s.image) for s in symbols])
    archetypes = _derive_archetypes(interpretation)
    related = _dedupe_preserve([f"[[{Path(s).stem}]]" for s in interpretation.sources])
    display_title = title or " ".join(w.capitalize() for w in slug.split("-"))
    fm = _render_frontmatter(path.stem, f"{date_str} — {display_title}", date_str,
                              symbol_tags, archetypes, related)
    analysis = _render_analysis_section(interpretation)
    note = fm + "\n" + _render_new_note_body(dream_text, analysis, date_str, d.strftime("%A"))

    if dry:
        print(note)
        return path

    vault_rel = str(path.relative_to(config.VAULT_ROOT)).replace("\\", "/")
    _acquire_lock(vault_rel)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(note, encoding="utf-8")
    finally:
        _release_lock(vault_rel)
    return path


def _write_case_a(path: Path, interpretation, symbols, *, dry, force) -> Path:
    raw = path.read_text(encoding="utf-8")
    fm_text, body = _split_frontmatter(raw)
    existing = yaml.safe_load(fm_text) or {}

    idx = body.find("## Jungian Analysis")
    if idx == -1:
        raise WritebackError(f"{path} has no '## Jungian Analysis' heading")
    preamble, existing_section = body[:idx], body[idx:]

    if not force and _analysis_nonempty(existing_section):
        raise WritebackError(f"{path} already has analysis content; pass --force to overwrite")

    today = datetime.date.today().isoformat()
    symbol_tags = _dedupe_preserve(list(existing.get("symbols") or []) + [_kebab(s.image) for s in symbols])
    archetypes = _dedupe_preserve(list(existing.get("archetypes") or []) + _derive_archetypes(interpretation))
    related = _dedupe_preserve(list(existing.get("related") or []) +
                                [f"[[{Path(s).stem}]]" for s in interpretation.sources])
    patches = {
        "status": "status: analyzed\n",
        "updated": f"updated: {today}\n",
        "symbols": f"symbols: [{', '.join(symbol_tags)}]\n",
        "archetypes": f"archetypes: [{', '.join(archetypes)}]\n",
        "related": _render_related_block(related),
    }
    new_fm = _patch_frontmatter_keys(fm_text, patches)
    note = "---\n" + new_fm + "---\n" + preamble + _render_analysis_section(interpretation)

    if dry:
        print(note)
        return path

    vault_rel = str(path.relative_to(config.VAULT_ROOT)).replace("\\", "/")
    _acquire_lock(vault_rel)
    try:
        path.write_text(note, encoding="utf-8")
    finally:
        _release_lock(vault_rel)
    return path


def write_note(dream_text, interpretation, symbols, *, source_path=None,
                dry=False, force=False, title=None, date=None) -> Path:
    if source_path is not None:
        p = Path(source_path).resolve()
        if p.is_file():
            try:
                in_dreams_dir = p.is_relative_to(config.DREAMS_DIR.resolve())
            except AttributeError:
                in_dreams_dir = str(p).startswith(str(config.DREAMS_DIR.resolve()))
            if in_dreams_dir:
                raw = p.read_text(encoding="utf-8")
                if re.search(r"^type:\s*dream\s*$", raw, re.MULTILINE):
                    return _write_case_a(p, interpretation, symbols, dry=dry, force=force)
    return _write_case_b(dream_text, interpretation, symbols, dry=dry, title=title, date=date)
