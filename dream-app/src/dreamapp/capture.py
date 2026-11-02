"""Stage 0 (CAPTURE) and Stage 2 (ASSOCIATE) of the method in individuation-app/docs/design.md.

The pipeline pauses here so the dreamer's own context reaches the model before
anything is retrieved or interpreted: without it the model invents the personal
reading and infers the conscious situation from the dream itself.
"""
from dataclasses import dataclass, field, replace

PROVENANCES = ("dream", "fragment", "imagination", "test", "imported")
MAX_ASSOCIATION_QUESTIONS = 7
STOP_WORDS = {"q", "quit", "done"}
# The vault's verdict words, plus design.md's yes / partly / no.
VERDICTS = {"clicks": "clicks", "yes": "clicks", "y": "clicks",
            "partial": "partial", "partly": "partial", "p": "partial",
            "miss": "miss", "no": "miss", "n": "miss"}
LATER = {"later", "skip"}


@dataclass
class Capture:
    conscious_situation: str = ""
    affect: str = ""
    provenance: str = "dream"
    associations: dict = field(default_factory=dict)  # symbol image -> the dreamer's own words


def ask_capture(ask=input) -> Capture:
    situation = ask("What's live in your life right now (work, money, relationships, what you're pushing on or avoiding)? ").strip()
    affect = ask("Strongest feeling on waking, and how strong (1-5)? ").strip()
    options = " / ".join(PROVENANCES)
    while True:
        provenance = ask(f"What is this: {options}? [dream] ").strip().lower() or "dream"
        if provenance in PROVENANCES:
            break
    return Capture(conscious_situation=situation, affect=affect, provenance=provenance)


def ask_associations(symbols, ask=input, limit=MAX_ASSOCIATION_QUESTIONS) -> dict:
    """One question per image, most salient first. Blank skips an image; q stops."""
    associations = {}
    for symbol in sorted(symbols, key=lambda s: -s.salience)[:limit]:
        reply = ask(f"What does '{symbol.image}' bring up for you? (blank to skip, q to stop) ").strip()
        if reply.lower() in STOP_WORDS:
            break
        if reply:
            associations[symbol.image] = reply
    return associations


def ask_response(ask=input) -> tuple:
    """Stage 5's dreamer response: (verdict, one line). ('', '') when deferred with 'later'."""
    while True:
        reply = ask("Does this click? clicks / partial / miss (or later) ").strip().lower()
        if reply in LATER:
            return "", ""
        if reply in VERDICTS:
            break
    note = ask("One line: what hit, or what's off? ").strip()
    return VERDICTS[reply], note


def with_associations(symbols, associations) -> list:
    """Symbols whose retrieval query carries the dreamer's association (design.md Stage 3)."""
    return [replace(s, query=f"{s.query} {associations[s.image]}") if s.image in associations else s
            for s in symbols]
