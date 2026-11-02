import datetime
import sys

from . import config
from .capture import ask_associations, ask_capture, ask_response, with_associations
from .cw import search as search_cw
from .extract import extract_symbols
from .retrieve import retrieve_passages
from .synthesize import synthesize_interpretation
from .writeback import check_writable, record_response, write_note


class InputError(Exception):
    pass


def run(dream_text, source_path=None, dry=False, show_sources=False, force=False, title=None, date=None,
        interactive=False, ask=input):
    if len(dream_text) > config.MAX_DREAM_CHARS:
        raise InputError(f"dream text exceeds MAX_DREAM_CHARS ({config.MAX_DREAM_CHARS})")
    if date is not None:
        try:
            datetime.date.fromisoformat(date)
        except ValueError as e:
            raise InputError(f"bad date {date!r}: {e}") from e

    # A refusal to overwrite must come before the interview, not after it.
    check_writable(source_path, force)

    # Stage 0: the conscious situation is collected before anything reads the dream.
    capture = ask_capture(ask) if interactive else None

    try:
        symbols = extract_symbols(dream_text)
        print(f"extract: {len(symbols)} symbols", file=sys.stderr)

        # Stage 2: associations gate retrieval, and become part of each query.
        query_symbols = symbols
        if capture is not None:
            capture.associations = ask_associations(symbols, ask)
            query_symbols = with_associations(symbols, capture.associations)

        # Stage 3: vault pages route; Collected Works paragraphs are the citable evidence.
        # One query per salient symbol (carrying its association) plus one for the whole dream.
        passages = retrieve_passages(query_symbols)
        cw_passages = search_cw([s.query for s in query_symbols if s.salience >= config.MIN_SALIENCE_FOR_RETRIEVAL]
                                + [dream_text.strip()])
        print(f"retrieve: {len(passages)} pages, {len(cw_passages)} CW passages", file=sys.stderr)
        if show_sources:
            for c in cw_passages:
                print(f"{c.score:.3f}  {c.header}")
            for p in passages:
                print(f"{p.score:.3f}  {p.page_path}  {p.snippet}")

        interpretation = synthesize_interpretation(dream_text, symbols, passages, capture=capture,
                                                   cw_passages=cw_passages)
        print("synthesize: done", file=sys.stderr)

        path = write_note(dream_text, interpretation, symbols, source_path=source_path,
                          dry=dry, force=force, title=title, date=date, capture=capture)
    except BaseException:
        if capture is not None:
            _print_capture(capture)
        raise
    print(f"writeback: {'dry run, not written' if dry else path}", file=sys.stderr)

    # Stage 5: the dreamer's verdict is the method's only validation (design.md, CW 16 ¶320).
    # Asked after the write, so cancelling here loses nothing.
    if capture is not None and not dry:
        print(f"\nCompensation: {interpretation.compensation}\n\n"
              f"Competing reading: {interpretation.counter_reading}\n\n"
              f"Question: {interpretation.question}\n")
        try:
            verdict, note = ask_response(ask)
        except (EOFError, KeyboardInterrupt):
            verdict, note = "", ""
        if verdict:
            record_response(path, verdict, note)
        else:
            print(f"verdict not recorded; later: dreamapp respond {path} --verdict clicks|partial|miss",
                  file=sys.stderr)

    return interpretation


def _print_capture(capture):
    """Echo the dreamer's answers to stderr when a run dies before they reach the note."""
    lines = ["log: stopped before the note was written. Your answers:",
             f"  conscious situation: {capture.conscious_situation}",
             f"  feeling-tone: {capture.affect}",
             f"  provenance: {capture.provenance}"]
    lines += [f"  - {image}: {text}" for image, text in capture.associations.items()]
    print("\n".join(lines), file=sys.stderr)
