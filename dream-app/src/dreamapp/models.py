import json
import re
import sys
from dataclasses import asdict, dataclass, field


def _warn_missing_keys(d: dict, required: tuple, context: str) -> None:
    missing = [k for k in required if k not in d]
    if missing:
        print(f"{context}: model response missing expected key(s) {missing}; using empty defaults", file=sys.stderr)


@dataclass
class Symbol:
    image: str
    kind: str
    salience: int
    query: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Symbol":
        return cls(image=d["image"], kind=d["kind"], salience=d["salience"], query=d["query"])


@dataclass
class Passage:
    page_path: str
    absolute_path: str
    snippet: str
    score: float
    page_text: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Passage":
        return cls(
            page_path=d["page_path"],
            absolute_path=d["absolute_path"],
            snippet=d["snippet"],
            score=d["score"],
            page_text=d.get("page_text", ""),
        )


@dataclass
class Amplification:
    symbol: str
    corpus_says: str
    personal_reading: str
    archetypal_reading: str
    thin_coverage: bool

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Amplification":
        _warn_missing_keys(d, ("symbol", "corpus_says", "personal_reading", "archetypal_reading", "thin_coverage"), "amplification")
        return cls(
            symbol=str(d.get("symbol", "")),
            corpus_says=str(d.get("corpus_says", "")),
            personal_reading=str(d.get("personal_reading", "")),
            archetypal_reading=str(d.get("archetypal_reading", "")),
            thin_coverage=bool(d.get("thin_coverage", False)),
        )


@dataclass
class Interpretation:
    dramatic_structure: str
    compensation: str
    amplifications: list = field(default_factory=list)  # list[Amplification]
    objective_level: str = ""
    subjective_level: str = ""
    movement: str = ""
    question: str = ""
    sources: list = field(default_factory=list)  # list[str]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["amplifications"] = [a.to_dict() if isinstance(a, Amplification) else a for a in self.amplifications]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Interpretation":
        _warn_missing_keys(d, ("dramatic_structure", "compensation", "amplifications",
                               "objective_level", "subjective_level", "movement", "question", "sources"),
                           "interpretation")
        return cls(
            dramatic_structure=str(d.get("dramatic_structure", "")),
            compensation=str(d.get("compensation", "")),
            amplifications=[Amplification.from_dict(a) for a in d.get("amplifications", []) if isinstance(a, dict)],
            objective_level=d.get("objective_level", ""),
            subjective_level=d.get("subjective_level", ""),
            movement=d.get("movement", ""),
            question=d.get("question", ""),
            sources=list(d.get("sources", [])),
        )


def parse_model_json(text: str):
    """Strip markdown fences and parse JSON, retrying on the largest {...} or [...] span."""
    stripped = text.strip()
    stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
    stripped = re.sub(r"\s*```$", "", stripped)
    stripped = stripped.strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    obj_start, obj_end = stripped.find("{"), stripped.rfind("}")
    arr_start, arr_end = stripped.find("["), stripped.rfind("]")

    candidates = []
    if obj_start != -1 and obj_end != -1 and obj_end > obj_start:
        candidates.append(stripped[obj_start : obj_end + 1])
    if arr_start != -1 and arr_end != -1 and arr_end > arr_start:
        candidates.append(stripped[arr_start : arr_end + 1])
    candidates.sort(key=len, reverse=True)

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    raise ValueError(f"could not parse JSON from model output: {text[:200]!r}")
