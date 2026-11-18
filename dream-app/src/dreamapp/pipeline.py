import datetime
import sys
from pathlib import Path

from . import config
from .capture import ask_associations, ask_capture, ask_response, confirm_symbols, with_associations
from .cw import method_canon, with_method_canon
from .cw import search as search_cw
from .extract import extract_symbols
from .notes import dream_section, frontmatter_date
from .retrieve import retrieve_passages
from .series import find_series
from .synthesize import synthesize_interpretation
from .writeback import _case_a_path, check_writable, record_response, write_note


class InputError(Exception):
    pass


def run(dream_text, source_path=None, dry=False, show_sources=False, force=False, title=None, date=None,
        interactive=False, ask=input, series=True):
    # A note's own date bounds its series: re-reading an old dream must not see the dreams that came after.
    series_date = frontmatter_date(dream_text)
    # Only the dream itself is measured and sent: an analyzed note runs far past MAX_DREAM_CHARS.
    dream_text = dream_section(dream_text)
    if not dream_text:
        raise InputError("no dream text: the note's '## The Dream' section is empty")
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
        symbols = extract_symbols(dream_text, motifs=series)
        print(f"extract: {len(symbols)} symbols", file=sys.stderr)

        # Stage 1: the dreamer checks the model's image list. Stage 2: associations gate retrieval,
        # and become part of each query.
        query_symbols = symbols
        if capture is not None:
            symbols = confirm_symbols(symbols, ask)
            capture.associations = ask_associations(symbols, ask)
            query_symbols = with_associations(symbols, capture.associations)

        # Stage 3: vault pages route; Collected Works paragraphs are the citable evidence.
        # One query per salient symbol (carrying its association) plus one for the whole dream,
        # and the method canon on every run, since no image query retrieves it.
        passages = retrieve_passages(query_symbols)
        cw_passages = with_method_canon(
            search_cw([s.query for s in query_symbols if s.salience >= config.MIN_SALIENCE_FOR_RETRIEVAL]
                      + [dream_text.strip()]),
            method_canon())
        print(f"retrieve: {len(passages)} pages, {len(cw_passages)} CW passages", file=sys.stderr)
        if show_sources:
            for c in cw_passages:
                print(f"{c.score:.3f}  {c.header}")
            for p in passages:
                print(f"{p.score:.3f}  {p.page_path}  {p.snippet}")

        # Stage 3, the personal parallel (design.md §3): earlier dreams sharing an image, beside the corpus.
        found = None
        if series:
            # a re-analysed note is read as of its own date; --date dates a new one
            note_date = series_date if _case_a_path(source_path) else None
            cutoff = (note_date or (datetime.date.fromisoformat(date) if date else None)
                      or series_date or datetime.date.today())
            found = find_series(symbols, on_or_before=cutoff,
                                exclude=Path(source_path).stem if source_path else None)
            _disclose_series(found, show_sources)

        interpretation = synthesize_interpretation(dream_text, symbols, passages, capture=capture,
                                                   cw_passages=cw_passages, series=found)
        print("synthesize: done", file=sys.stderr)

        path = write_note(dream_text, interpretation, symbols, source_path=source_path,
                          dry=dry, force=force, title=title, date=date, capture=capture)
    except BaseException:
        if capture is not None:
            _print_capture(capture)
        raise
    print(f"writeback: {'dry run, not written' if dry else path}", file=sys.stderr)

    # Stage 5: the dreamer's verdict is the method's only validation (design.md, CW 16 ¶316).
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


def _disclose_series(found, show_sources=False):
    """Earlier dreams are the dreamer's private material too: say which ones go to the model."""
    if not found:
        print("series: no earlier dream shares these images", file=sys.stderr)
        return
    n = len(found)
    print(f"series: excerpts, the readings given then and your responses from {n} earlier dream{'s' if n != 1 else ''} "
          f"go to the model with this one ({', '.join(e.date.isoformat() for e in found)}); "
          "--no-series leaves them and your motif vocabulary out", file=sys.stderr)
    if show_sources:
        for e in found:
            print(f"series  {e.path}  [{', '.join(e.matched)}]")


def _print_capture(capture):
    """Echo the dreamer's answers to stderr when a run dies before they reach the note."""
    lines = ["log: stopped before the note was written. Your answers:",
             f"  conscious situation: {capture.conscious_situation}",
             f"  feeling-tone: {capture.affect}",
             f"  provenance: {capture.provenance}"]
    lines += [f"  - {image}: {text}" for image, text in capture.associations.items()]
    print("\n".join(lines), file=sys.stderr)
