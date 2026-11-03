import json
import re
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


def _capture_blocks(symbols: list, capture) -> str:
    if capture is None:
        return ("<conscious_situation>\n(not collected)\n</conscious_situation>\n\n"
                "<associations>\n(none collected; the dreamer was not asked)\n</associations>\n\n")
    lines = [f"- {s.image}: {capture.associations.get(s.image) or '(no association given)'}" for s in symbols]
    return (f"<conscious_situation>\n{capture.conscious_situation or '(not given)'}\n</conscious_situation>\n\n"
            f"<affect>\n{capture.affect or '(not given)'}\n</affect>\n\n"
            "<associations>\n" + "\n".join(lines) + "\n</associations>\n\n")


def _cw_block(c) -> str:
    role = ' role="method"' if c.role == "method" else ""
    text = c.text
    if len(text) > config.MAX_CHARS_PER_CW_CHUNK:
        # the header still names the full range; say so, so nothing past the cut gets cited
        text = text[:config.MAX_CHARS_PER_CW_CHUNK] + " [truncated: later paragraphs of this range not shown]"
    return f'<cw header="{c.header}"{role}>\n{text}\n</cw>'


def _build_user_message(dream_text: str, symbols: list, passages: list, capture=None, cw_passages=()) -> str:
    symbols_json = json.dumps([s.to_dict() for s in symbols], ensure_ascii=False, indent=2)
    corpus_blocks = "\n".join(
        [_cw_block(c) for c in cw_passages]
        + [f'<page path="{p.page_path}">\n{p.page_text}\n</page>' for p in passages]
    )
    return (
        f"<dream>\n{dream_text}\n</dream>\n\n"
        + _capture_blocks(symbols, capture)
        + f"<symbols>\n{symbols_json}\n</symbols>\n\n"
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
                max_tokens=config.MAX_TOKENS_SYNTH,
                thinking={"type": "disabled"},
                system=system,
                messages=[{"role": "user", "content": user_message}],
            )
            if getattr(resp, "stop_reason", None) == "max_tokens":
                # a cut-off JSON object won't parse, and a reprompt would be cut off the same way
                raise SynthesizeError(f"synthesize: the answer hit MAX_TOKENS_SYNTH ({config.MAX_TOKENS_SYNTH}) "
                                      "before it finished; raise it in config.py")
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


_DASHES = re.compile(r"[‐-―−-]")
_QUOTES = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"})
_RANGE = r"\d+(?:\s*[‐-―-]\s*\d+)?"
# "CW 8 ¶509", "CW 8 ¶¶ 509–512", "CW 8 ¶¶509, ¶515", "CW 8 ¶509–10"; \s also matches a non-breaking space
_INLINE_CW = re.compile(rf"CW\s+(\d+i{{0,2}})\s*¶¶?\s*({_RANGE}(?:\s*,\s*¶?\s*{_RANGE})*)")
_PARA_MARK = re.compile(r"\[(\d+)\]")


def _citation_key(s: str) -> str:
    """Compare citations past the slips a model makes echoing them: dash style, quotes, spacing, case,
    and path separators (retrieve.py emits OS-native page_path; the model echoes forward slashes)."""
    s = _DASHES.sub("-", s.replace("\\", "/").translate(_QUOTES))
    return re.sub(r"\s+", " ", s).strip().casefold()


def _filter_sources(cited: list, passages: list, cw_passages=()) -> list:
    """Anti-confabulation: keep only citations of pages and CW chunks actually supplied, each in its
    supplied form and once; report the rest."""
    supplied = {}
    for s in [p.page_path.replace("\\", "/") for p in passages] + [c.header for c in cw_passages]:
        supplied.setdefault(_citation_key(s), s)
    kept, dropped = [], []
    for s in cited:
        canonical = supplied.get(_citation_key(s))
        if canonical is None:
            dropped.append(s)
        elif canonical not in kept:
            kept.append(canonical)
    if dropped:
        print(f"synthesize: dropped {len(dropped)} source(s) not in the supplied corpus: {'; '.join(dropped)}",
              file=sys.stderr)
    return kept


def _shown_paragraphs(c) -> tuple:
    """(first, last) paragraph the model actually saw: a chunk cut at MAX_CHARS_PER_CW_CHUNK shows fewer."""
    if len(c.text) <= config.MAX_CHARS_PER_CW_CHUNK:
        return c.para_start, c.para_end
    marks = [int(n) for n in _PARA_MARK.findall(c.text[:config.MAX_CHARS_PER_CW_CHUNK])]
    return c.para_start, max(marks) if marks else c.para_start


def _expand(item: str) -> tuple:
    """'509' -> (509, 509); '509–512' -> (509, 512); abbreviated '509–10' -> (509, 510)."""
    nums = re.findall(r"\d+", item)
    lo = int(nums[0])
    if len(nums) == 1:
        return lo, lo
    hi_text = nums[1]
    hi = int(hi_text) if int(hi_text) >= lo else int(nums[0][: len(nums[0]) - len(hi_text)] + hi_text)
    return lo, hi


def unsupported_inline_citations(interpretation, cw_passages) -> list:
    """'CW 8 ¶999' in the prose whose paragraph the model was not shown. Advisory: never raises on odd fields."""
    fields = [interpretation.dramatic_structure, interpretation.compensation, interpretation.counter_reading,
              interpretation.objective_level, interpretation.subjective_level, interpretation.movement,
              interpretation.question]
    for a in interpretation.amplifications:
        fields += [a.corpus_says, a.personal_reading, a.archetypal_reading]
    prose = " ".join(str(f) for f in fields if f)  # the model can return a list where text belongs
    shown = [(c.volume, *_shown_paragraphs(c)) for c in cw_passages if c.para_start is not None]
    found = []
    for vol, numbers in _INLINE_CW.findall(prose):
        for item in re.split(r"\s*,\s*¶?\s*", numbers):
            lo, hi = _expand(item)
            held = all(any(v == f"CW {vol}" and a <= p <= b for v, a, b in shown)
                       for p in range(lo, min(hi, lo + 30) + 1))
            cite = f"CW {vol} ¶{lo}" + (f"–{hi}" if hi != lo else "")
            if not held and cite not in found:
                found.append(cite)
    return found


def synthesize_interpretation(dream_text: str, symbols: list, passages: list, capture=None,
                              cw_passages=()) -> Interpretation:
    client = anthropic.Anthropic(api_key=config.get_api_key())
    user_message = _build_user_message(dream_text, symbols, passages, capture=capture, cw_passages=cw_passages)

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

    interpretation.sources = _filter_sources(interpretation.sources, passages, cw_passages)
    try:
        unsupported = unsupported_inline_citations(interpretation, cw_passages)
    except Exception as e:  # advisory only: a paid answer is never lost to this check
        print(f"synthesize: inline-citation check skipped ({e})", file=sys.stderr)
        unsupported = []
    if unsupported:
        print(f"synthesize: cited in the text but not supplied (check these): {', '.join(unsupported)}",
              file=sys.stderr)
    return interpretation
