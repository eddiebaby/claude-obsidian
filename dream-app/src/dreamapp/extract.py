import sys
import time
from pathlib import Path

import anthropic

from . import config
from .models import Symbol, parse_model_json

PROMPT_PATH = Path(__file__).parent / "prompts" / "extract.md"


class ExtractError(Exception):
    pass


def _is_retryable(e: Exception) -> bool:
    status = getattr(e, "status_code", None)
    return status == 429 or (isinstance(status, int) and status >= 500)


def _call(client, dream_text: str, extra_instruction: str = None) -> str:
    system = PROMPT_PATH.read_text(encoding="utf-8")
    if extra_instruction:
        system = system + "\n\n" + extra_instruction

    last_err = None
    for attempt in range(3):  # 1 try + 2 retries
        try:
            resp = client.messages.create(
                model=config.MODEL_EXTRACT,
                max_tokens=1500,
                temperature=0,
                system=system,
                messages=[{"role": "user", "content": dream_text}],
            )
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


def extract_symbols(dream_text: str) -> list:
    client = anthropic.Anthropic(api_key=config.get_api_key())
    text = _call(client, dream_text)
    try:
        data = parse_model_json(text)
    except ValueError:
        print("extract: JSON parse failed, reprompting once", file=sys.stderr)
        text = _call(client, dream_text, "Return ONLY the JSON array, no prose.")
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
        symbols.append(Symbol(image=image, kind=kind, salience=salience, query=query))

    symbols.sort(key=lambda s: s.salience, reverse=True)
    return symbols[: config.MAX_SYMBOLS]
