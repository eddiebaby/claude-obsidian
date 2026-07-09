import datetime
import sys

from . import config
from .extract import extract_symbols
from .retrieve import retrieve_passages
from .synthesize import synthesize_interpretation
from .writeback import write_note


class InputError(Exception):
    pass


def run(dream_text, source_path=None, dry=False, show_sources=False, force=False, title=None, date=None):
    if len(dream_text) > config.MAX_DREAM_CHARS:
        raise InputError(f"dream text exceeds MAX_DREAM_CHARS ({config.MAX_DREAM_CHARS})")
    if date is not None:
        try:
            datetime.date.fromisoformat(date)
        except ValueError as e:
            raise InputError(f"bad date {date!r}: {e}") from e

    symbols = extract_symbols(dream_text)
    print(f"extract: {len(symbols)} symbols", file=sys.stderr)

    passages = retrieve_passages(symbols)
    print(f"retrieve: {len(passages)} pages", file=sys.stderr)
    if show_sources:
        for p in passages:
            print(f"{p.score:.3f}  {p.page_path}  {p.snippet}")

    interpretation = synthesize_interpretation(dream_text, symbols, passages)
    print("synthesize: done", file=sys.stderr)

    path = write_note(dream_text, interpretation, symbols, source_path=source_path,
                       dry=dry, force=force, title=title, date=date)
    print(f"writeback: {'dry run, not written' if dry else path}", file=sys.stderr)

    return interpretation
