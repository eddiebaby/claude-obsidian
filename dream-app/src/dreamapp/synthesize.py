import json
import sys
import time
from pathlib import Path

import anthropic

from . import config
from .models import Interpretation, parse_model_json

PROMPT_PATH = Path(__file__).parent / "prompts" / "synthesize.md"


class SynthesizeError(Exception):
    pass


def _is_retryable(e: Exception) -> bool:
    status = getattr(e, "status_code", None)
    return status == 429 or (isinstance(status, int) and status >= 500)


def _build_user_message(dream_text: str, symbols: list, passages: list) -> str:
    symbols_json = json.dumps([s.to_dict() for s in symbols], ensure_ascii=False, indent=2)
    corpus_blocks = "\n".join(
        f'<page path="{p.page_path}">\n{p.page_text}\n</page>' for p in passages
    )
    return (
        f"<dream>\n{dream_text}\n</dream>\n\n"
        f"<symbols>\n{symbols_json}\n</symbols>\n\n"
        f"<corpus>\n{corpus_blocks}\n</corpus>"
    )


def _call(client, user_message: str, extra_instruction: str = None) -> str:
    system = PROMPT_PATH.read_text(encoding="utf-8")
    if extra_instruction:
        system = system + "\n\n" + extra_instruction

    last_err = None
    for attempt in range(3):
        try:
            # No `temperature`: claude-sonnet-5 rejects it unconditionally —
            # "Error code: 400 ... `temperature` is deprecated for this model"
            # — confirmed even with thinking explicitly disabled, so this
            # isn't a workaround for the thinking budget, it's a hard model
            # constraint. thinking is disabled because leaving it on the
            # default silently consumed the whole max_tokens budget on
            # reasoning, truncating or emptying the JSON response.
            resp = client.messages.create(
                model=config.MODEL_SYNTH,
                max_tokens=4000,
                thinking={"type": "disabled"},
                system=system,
                messages=[{"role": "user", "content": user_message}],
            )
            return "".join(block.text for block in resp.content if block.type == "text")
        except anthropic.APIStatusError as e:
            last_err = e
            if not _is_retryable(e) or attempt == 2:
                raise SynthesizeError(f"synthesize: model API call failed: {e}") from e
            wait = 2**attempt
            print(f"synthesize: retryable error ({e}), retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
        except anthropic.APIError as e:
            raise SynthesizeError(f"synthesize: model API call failed: {e}") from e
    raise SynthesizeError(f"synthesize: model API call failed after retries: {last_err}")


def synthesize_interpretation(dream_text: str, symbols: list, passages: list) -> Interpretation:
    client = anthropic.Anthropic(api_key=config.get_api_key())
    user_message = _build_user_message(dream_text, symbols, passages)

    text = _call(client, user_message)
    try:
        data = parse_model_json(text)
    except ValueError:
        print("synthesize: JSON parse failed, reprompting once", file=sys.stderr)
        text = _call(client, user_message, "Return ONLY the JSON object, no prose.")
        try:
            data = parse_model_json(text)
        except ValueError as e:
            raise SynthesizeError(f"synthesize: could not parse model output after reprompt: {e}") from e

    if not isinstance(data, dict):
        raise SynthesizeError("synthesize: model output was not a JSON object")

    interpretation = Interpretation.from_dict(data)

    # Anti-confabulation: sources may only cite pages we actually supplied.
    # Normalize separators: retrieve.py emits OS-native page_path (backslashes on
    # Windows), but the model tends to echo back forward slashes regardless.
    supplied_paths = {p.page_path.replace("\\", "/") for p in passages}
    interpretation.sources = [
        s for s in interpretation.sources if s.replace("\\", "/") in supplied_paths
    ]

    return interpretation
