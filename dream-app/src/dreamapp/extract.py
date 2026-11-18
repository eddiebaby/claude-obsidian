import sys
import time
from pathlib import Path

import anthropic

from . import config
from .models import Symbol, parse_model_json
from .series import motif_vocabulary

PROMPT_PATH = Path(__file__).parent / "prompts" / "extract.md"


class ExtractError(Exception):
    pass


def _is_retryable(e: Exception) -> bool:
    status = getattr(e, "status_code", None)
    return status == 429 or (isinstance(status, int) and status >= 500)


def _motif_instruction(vocabulary) -> str:
    """The dreamer's motif vocabulary, so the series can find earlier dreams no image word reaches."""
    lines = "\n".join(f"- {tag}: {covers}" for tag, covers in vocabulary)
    return ('Add to each element "motifs": the tags from this controlled vocabulary the image belongs to, '
            "spelled exactly as listed; [] when none fits. Tag what the image is, not what it might mean.\n"
            + lines)


def _call(client, dream_text: str, extra_instruction: str = None, vocabulary=()) -> str:
    system = PROMPT_PATH.read_text(encoding="utf-8")
    if vocabulary:
        system = system + "\n\n" + _motif_instruction(vocabulary)
    if extra_instruction:
        system = system + "\n\n" + extra_instruction

    last_err = None
    for attempt in range(3):  # 1 try + 2 retries
        try:
            resp = client.messages.create(
                model=config.MODEL_EXTRACT,
                max_tokens=config.MAX_TOKENS_EXTRACT,
                temperature=0,
                system=system,
                messages=[{"role": "user", "content": dream_text}],
            )
            if getattr(resp, "stop_reason", None) == "max_tokens":
                # a cut-off JSON array won't parse, and a reprompt would be cut off the same way
                raise ExtractError(f"extract: the answer hit MAX_TOKENS_EXTRACT ({config.MAX_TOKENS_EXTRACT}) "
                                   "before it finished; raise it in config.py")
            return "".join(block.text for block in resp.content if block.type == "text")
        except anthropic.APIStatusError as e:
            last_err = e
            if not _is_retryable(e) or attempt == 2:
                raise ExtractError(f"extract: model API call failed: {e}") from e
            wait = 2**attempt
            print(f"extract: retryable error ({e}), retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
        except anthropic.APIError as e:
            raise ExtractError(f"extract: model API call failed: {e}") from e
    raise ExtractError(f"extract: model API call failed after retries: {last_err}")


def extract_symbols(dream_text: str, motifs: bool = True) -> list:
    """motifs=False (--no-series) keeps the dreamer's motif vocabulary out of the call: it names real places."""
    client = anthropic.Anthropic(api_key=config.get_api_key())
    vocabulary = motif_vocabulary() if motifs else []
    if vocabulary:
        print(f"extract: your motif vocabulary ({len(vocabulary)} tags from wiki/dreams/motifs.md) goes with the "
              "dream; --no-series leaves it out", file=sys.stderr)
    tags = {tag for tag, _ in vocabulary}
    text = _call(client, dream_text, vocabulary=vocabulary)
    try:
        data = parse_model_json(text)
    except ValueError:
        print("extract: JSON parse failed, reprompting once", file=sys.stderr)
        text = _call(client, dream_text, "Return ONLY the JSON array, no prose.", vocabulary=vocabulary)
        try:
            data = parse_model_json(text)
        except ValueError as e:
            raise ExtractError(f"extract: could not parse model output after reprompt: {e}") from e

    if not isinstance(data, list):
        raise ExtractError("extract: model output was not a JSON array")

    symbols = []
    for item in data:
        image = str(item.get("image", "")).strip()
        if not image:
            continue
        try:
            salience = int(item.get("salience", 1))
        except (TypeError, ValueError):
            salience = 1
        salience = max(1, min(5, salience))
        kind = item.get("kind", "ambiguous")
        if kind not in ("personal", "archetypal", "ambiguous"):
            kind = "ambiguous"
        query = str(item.get("query", image)).strip()
        raw = item.get("motifs")
        tags_found = list(dict.fromkeys(str(m) for m in raw if str(m) in tags)) if isinstance(raw, list) else []
        symbols.append(Symbol(image=image, kind=kind, salience=salience, query=query, motifs=tags_found))

    symbols.sort(key=lambda s: s.salience, reverse=True)
    return symbols[: config.MAX_SYMBOLS]
