"""Reading a dream note's parts: the dream itself, its date, and one section's own text."""
import datetime
import re


_STOP = {"a", "an", "the", "of", "in", "on", "at", "and", "or", "to", "is", "was", "my", "me", "his", "her",
         "their", "our", "your", "it", "its", "this", "that", "with", "for", "as", "by", "from", "into", "be",
         "am", "are", "were", "some", "any", "other", "etc", "including", "like"}
# Words ending in s that aren't plurals, which the rules below would cut ("does" -> "doe").
_KEEP = {"does", "always", "perhaps", "news", "series", "species", "chaos", "canvas", "atlas", "lens", "bias",
         "thus", "yes", "hers", "ours", "yours", "theirs", "whereas"}
# Plurals the suffix rules get wrong: an -ies plural of an -ie word, an -es plural of an -s word.
_PLURALS = {"buses": "bus", "gases": "gas", "movies": "movie", "cookies": "cookie", "zombies": "zombie",
            "brownies": "brownie", "selfies": "selfie", "hippies": "hippie", "rookies": "rookie",
            "calories": "calorie", "niches": "niche"}


def _norm(word: str) -> str:
    """The singular of a plural, by suffix only, so bus/buses, city/cities, beach/beaches and headache/headaches
    meet. Only a plural ending is ever removed: dropping a final e or y as well merged care with car and plane
    with plan."""
    if word in _KEEP:
        return word
    if word in _PLURALS:
        return _PLURALS[word]
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 4 and word.endswith(("sses", "xes", "shes", "zzes", "eaches", "oaches")):
        return word[:-2]
    if len(word) > 4 and word.endswith("ches") and not word.endswith("aches"):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def word_pairs(text: str) -> list:
    """(as written, normalised) for each content word."""
    text = text.lower().replace("’", "'").replace("'s", "")
    return [(w, _norm(w)) for w in re.findall(r"[a-z0-9]+", text) if len(w) > 1 and w not in _STOP]


def words(text: str) -> list:
    """Content words, lowercased and normalised, for matching an image or a motif across notes."""
    return [n for _, n in word_pairs(text)]


def dream_section(text: str) -> str:
    """The dream itself: a note's '## The Dream' section without template prompts, or plain text as given.

    A note also holds frontmatter, the dreamer's answers and any earlier analysis; none of that may
    reach symbol extraction, the whole-dream query, or the model as part of "the dream".
    """
    m = re.search(r"^## The Dream\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return text
    lines = [ln for ln in m.group(1).splitlines() if not ln.strip().startswith("> [")]
    return "\n".join(lines).strip()


def frontmatter_date(text: str):
    """The `date:` in a note's frontmatter, or None for plain text or a note without one."""
    m = re.match(r"\A---\r?\n(.*?)\r?\n---", text, re.S)
    d = m and re.search(r"^date:\s*['\"]?(\d{4}-\d{2}-\d{2})", m.group(1), re.M)
    if not d:
        return None
    try:
        return datetime.date.fromisoformat(d.group(1))
    except ValueError:
        return None


def section(body: str, heading: str, level: int = 2) -> str:
    """Text under the first heading of this level that starts with `heading`, up to the next heading of the
    same or a higher level or a '---' rule, without template prompts ('> [...' lines)."""
    hashes = "#" * level
    m = re.search(rf"^{hashes} {re.escape(heading)}[^\n]*\n(.*?)(?=^#{{1,{level}}} |^---\s*$|\Z)", body, re.S | re.M)
    if not m:
        return ""
    lines = [ln for ln in m.group(1).splitlines() if not ln.strip().startswith("> [")]
    return "\n".join(lines).strip()
