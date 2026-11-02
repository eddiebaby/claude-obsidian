import argparse
import sys
from pathlib import Path

from .extract import ExtractError
from .pipeline import InputError, run
from .retrieve import RetrievalNotProvisioned
from .synthesize import SynthesizeError
from .writeback import WritebackError


def _read_dream_text(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    p = Path(source)
    if not p.is_file():
        raise InputError(f"no such file: {source}")
    return p.read_text(encoding="utf-8")


def _review(args) -> int:
    import json
    from datetime import date

    from . import config
    from .review import compute, load_dreams, period_from_spec, render_markdown

    kind, spec = next((k, v) for k, v in (("month", args.month), ("quarter", args.quarter), ("year", args.year)) if v)
    try:
        period = period_from_spec(kind, spec)
        today = date.fromisoformat(args.today) if args.today else None
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    dreams_dir = Path(args.dreams_dir) if args.dreams_dir else config.DREAMS_DIR
    stats = compute(load_dreams(dreams_dir), period, today=today, reviews_dir=dreams_dir / "reviews")
    if args.json:
        Path(args.json).write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(render_markdown(stats))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="dreamapp")
    sub = parser.add_subparsers(dest="command", required=True)

    interpret = sub.add_parser("interpret")
    interpret.add_argument("input", help="file path or '-' for stdin")
    interpret.add_argument("--dry", action="store_true")
    interpret.add_argument("--show-sources", action="store_true")
    interpret.add_argument("--force", action="store_true")
    interpret.add_argument("--title")
    interpret.add_argument("--date")

    review = sub.add_parser("review", help="counted half of a periodic dream review")
    which = review.add_mutually_exclusive_group(required=True)
    which.add_argument("--month", help="YYYY-MM")
    which.add_argument("--quarter", help="YYYY-Qn")
    which.add_argument("--year", help="YYYY")
    review.add_argument("--dreams-dir", help="defaults to the vault's wiki/dreams")
    review.add_argument("--json", help="also write the stats as JSON to this path")
    review.add_argument("--today", help="YYYY-MM-DD; marks a period still in progress as partial")

    args = parser.parse_args()

    if args.command == "review":
        return _review(args)

    try:
        dream_text = _read_dream_text(args.input)
        source_path = None if args.input == "-" else args.input
        interpretation = run(
            dream_text,
            source_path=source_path,
            dry=args.dry,
            show_sources=args.show_sources,
            force=args.force,
            title=args.title,
            date=args.date,
        )
    except InputError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except RetrievalNotProvisioned as e:
        print(f"error: {e}", file=sys.stderr)
        return 3
    except (ExtractError, SynthesizeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 4
    except WritebackError as e:
        print(f"error: {e}", file=sys.stderr)
        return 5

    print(f"\nQuestion: {interpretation.question}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
