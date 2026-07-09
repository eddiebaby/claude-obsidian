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

    args = parser.parse_args()

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
