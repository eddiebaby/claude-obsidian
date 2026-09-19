"""Signals. Deliberately slow, deliberately few.

Each strategy is a callable: given the adjusted price history available at the
decision date (oldest first, last element = the decision bar), return a signal
in [-1, +1], or None to stand aside. Sizing is not the signal's business —
`sizing.py` turns a signal into contracts.

Fast trend (days to weeks) is dead on small-tick, dense-order-book contracts
post-2009; slow trend (months) survives. Nothing here runs faster than a
50/200-day crossover, and the defaults are months-scale on purpose.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


def _sign(x: float) -> float:
    return 1.0 if x > 0 else (-1.0 if x < 0 else 0.0)


@dataclass
class TimeSeriesMomentum:
    """Sign of the trailing `lookback`-day change. The canonical trend signal."""

    lookback: int = 252
    allow_short: bool = True
    skip: int = 0                 # bars to skip at the end (12-1 style)

    @property
    def min_history(self) -> int:
        return self.lookback + self.skip + 1

    @property
    def label(self) -> str:
        return f"tsm{self.lookback}{'' if self.allow_short else '-long-only'}"

    def __call__(self, values: list[float]) -> float | None:
        need = self.min_history
        if len(values) < need:
            return None
        end = len(values) - 1 - self.skip
        start = end - self.lookback
        if start < 0:
            return None
        s = _sign(values[end] - values[start])
        return max(0.0, s) if not self.allow_short else s


@dataclass
class MovingAverageCross:
    """Fast SMA above slow SMA. Near-equivalent to 12-month momentum — pick one
    and do not optimise between them; that choice is where overfitting starts."""

    fast: int = 50
    slow: int = 200
    allow_short: bool = True

    @property
    def min_history(self) -> int:
        return self.slow + 1

    @property
    def label(self) -> str:
        return f"ma{self.fast}-{self.slow}"

    def __call__(self, values: list[float]) -> float | None:
        if len(values) < self.min_history:
            return None
        f = sum(values[-self.fast:]) / self.fast
        s = sum(values[-self.slow:]) / self.slow
        sig = _sign(f - s)
        return max(0.0, sig) if not self.allow_short else sig


@dataclass
class MultiSpeedMomentum:
    """Average of several momentum horizons — a forecast, not a switch.

    Returns a graded signal, so the book de-risks when horizons disagree instead
    of flipping on the fastest one. This is the one place extra complexity has
    paid for itself consistently in the published record.
    """

    lookbacks: tuple = (63, 126, 252)
    allow_short: bool = True

    @property
    def min_history(self) -> int:
        return max(self.lookbacks) + 1

    @property
    def label(self) -> str:
        return "multi" + "-".join(str(x) for x in self.lookbacks)

    def __call__(self, values: list[float]) -> float | None:
        if len(values) < self.min_history:
            return None
        sigs = [_sign(values[-1] - values[-1 - lb]) for lb in self.lookbacks]
        avg = sum(sigs) / len(sigs)
        return max(0.0, avg) if not self.allow_short else avg


@dataclass
class VolAdjustedMomentum:
    """Trailing return divided by its own volatility, squashed into [-1, 1].

    A continuous forecast: strong trends get full size, weak ones get a fraction.
    The tanh scaling caps conviction so one market cannot dominate the book.
    """

    lookback: int = 252
    cap_z: float = 2.0

    @property
    def min_history(self) -> int:
        return self.lookback + 2

    @property
    def label(self) -> str:
        return f"volmom{self.lookback}"

    def __call__(self, values: list[float]) -> float | None:
        if len(values) < self.min_history:
            return None
        window = values[-(self.lookback + 1):]
        # Differences, not ratios: a back-adjusted level is fictional and can be
        # negative, so anything dividing by it is unsafe.
        diffs = [b - a for a, b in zip(window, window[1:])]
        if len(diffs) < 20:
            return None
        m = sum(diffs) / len(diffs)
        var = sum((x - m) ** 2 for x in diffs) / (len(diffs) - 1)
        sd = math.sqrt(var)
        if sd <= 0:
            # A trend with no variation around it is maximal conviction, not an
            # error. (Only shows up in tests and in stale quotes.)
            return _sign(window[-1] - window[0])
        z = (window[-1] - window[0]) / (sd * math.sqrt(len(diffs)))
        return math.tanh(z / max(self.cap_z, 1e-9))


@dataclass
class Breakout:
    """Long above the `lookback`-day high channel midpoint, short below."""

    lookback: int = 252
    allow_short: bool = True

    @property
    def min_history(self) -> int:
        return self.lookback + 1

    @property
    def label(self) -> str:
        return f"breakout{self.lookback}"

    def __call__(self, values: list[float]) -> float | None:
        if len(values) < self.min_history:
            return None
        w = values[-self.lookback:]
        hi, lo = max(w), min(w)
        if hi == lo:
            return 0.0
        pos = (values[-1] - lo) / (hi - lo)     # 0..1 within the channel
        sig = _sign(pos - 0.5)
        return max(0.0, sig) if not self.allow_short else sig


@dataclass
class Constant:
    """Benchmark / test harness: always the same signal (1 = long everything)."""

    value: float = 1.0
    min_history: int = 2

    @property
    def label(self) -> str:
        return f"constant{self.value:+.0f}"

    def __call__(self, values: list[float]) -> float | None:
        return self.value


REGISTRY = {
    "tsm": TimeSeriesMomentum,
    "ma": MovingAverageCross,
    "multi": MultiSpeedMomentum,
    "volmom": VolAdjustedMomentum,
    "breakout": Breakout,
    "constant": Constant,
}


def build(name: str, **kwargs):
    try:
        return REGISTRY[name](**kwargs)
    except KeyError:
        raise KeyError(f"unknown strategy {name!r}; known: {sorted(REGISTRY)}") from None
