"""Daily P&L paths: representation, loaders, synthetic generator, bootstrap.

A day is the cumulative mark-to-market P&L of ONE unit of size (one contract,
or whatever unit `size` multiplies), net of costs, sampled bar by bar from the
open. The last value is the realized P&L at the flat-by-close cutoff.

Each path is compressed once into "record segments": every time the path makes
a new intraday high (relative to the open), a segment starts; the segment keeps
that high and the lowest value reached before the next new high. That is
exactly the information needed to evaluate trailing-drawdown breaches, daily
stops and profit caps in the right order, so the engine is exact while looping
over ~10 segments instead of ~400 bars.
"""
from __future__ import annotations

import csv
import warnings
from dataclasses import dataclass
from typing import Iterator, Sequence

import numpy as np


@dataclass(frozen=True)
class Day:
    segments: tuple[tuple[float, float], ...]
    """(record_high, segment_min) pairs in time order, per unit of size."""
    close: float
    traded: bool
    label: str = ""

    @property
    def low(self) -> float:
        return min(m for _, m in self.segments)

    @property
    def high(self) -> float:
        return self.segments[-1][0]


def compress(path: Sequence[float], label: str = "") -> Day:
    """Compress a cumulative intraday P&L path (excluding the implicit 0 at the open)."""
    p = np.concatenate(([0.0], np.asarray(path, dtype=float)))
    if not np.all(np.isfinite(p)):
        raise ValueError(f"non-finite P&L in day {label!r}")
    runmax = np.maximum.accumulate(p)
    is_record = np.empty(len(p), dtype=bool)
    is_record[0] = True
    is_record[1:] = p[1:] > runmax[:-1]
    idx = np.flatnonzero(is_record)
    mins = np.minimum.reduceat(p, idx)
    segs = tuple((float(p[i]), float(m)) for i, m in zip(idx, mins))
    traded = bool(np.any(p != 0.0))
    return Day(segments=segs, close=float(p[-1]), traded=traded, label=label)


def eod_only(days: Sequence[Day]) -> list[Day]:
    """Drop intraday information: each day becomes open -> close.

    This is what a daily-P&L-only compliance check sees. Comparing results on
    eod_only(bank) vs bank measures how optimistic an EOD-only check is.
    """
    return [compress([d.close], d.label) if d.traded else d for d in days]


# --------------------------------------------------------------------------
# Loaders
# --------------------------------------------------------------------------

def load_bar_csv(path: str, date_col: str = "date", pnl_col: str = "pnl") -> list[Day]:
    """Bar-level file: one row per bar, in time order.

    `pnl` is the cumulative MTM P&L for one unit since that day's open, net of
    costs. Days with no position can be omitted or given a single 0 row.
    """
    by_day: dict[str, list[float]] = {}
    order: list[str] = []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            d = row[date_col]
            if d not in by_day:
                by_day[d] = []
                order.append(d)
            by_day[d].append(float(row[pnl_col]))
    return [compress(by_day[d], d) for d in order]


def load_daily_csv(path: str) -> list[Day]:
    """Daily file: columns date, pnl, and optionally mae, mfe, mfe_first.

    mae = worst unrealized P&L during the day, signed (<= 0); mfe = best (>= 0).
    A positive mae (stored as a magnitude) is rejected rather than guessed at.
    mfe_first = 1 if the best point came before the worst. Missing mfe_first
    defaults to 1: the worst case for trailing drawdowns, but the BEST case for
    a daily profit cap (the cap fires before the dip). Without mae/mfe the
    file is EOD-only and intraday breaches are invisible: results are optimistic.
    """
    days: list[Day] = []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        cols = set(reader.fieldnames or ())
        has_excursions = {"mae", "mfe"} <= cols
        if not has_excursions:
            warnings.warn(
                "daily file has no mae/mfe columns: only closing P&L is known, so "
                "intraday drawdown breaches are invisible and pass rates are optimistic",
                stacklevel=2,
            )
        for line, row in enumerate(reader, start=2):
            def num(col: str) -> float:
                try:
                    return float(row[col])
                except (TypeError, ValueError):
                    raise ValueError(f"{path}:{line}: bad {col!r} value {row.get(col)!r}") from None

            pnl = num("pnl")
            if not has_excursions:
                days.append(compress([pnl], row["date"]))
                continue
            raw_mae, raw_mfe = num("mae"), num("mfe")
            if raw_mae > 0 or raw_mfe < 0:
                raise ValueError(
                    f"{path}:{line}: mae must be <= 0 and mfe >= 0 (signed P&L), got mae={raw_mae}, mfe={raw_mfe}"
                )
            mae = min(raw_mae, pnl)
            mfe = max(raw_mfe, pnl)
            flag = (row.get("mfe_first") or "1").strip().lower()
            mfe_first = flag not in ("0", "false", "no")
            seq = [mfe, mae, pnl] if mfe_first else [mae, mfe, pnl]
            days.append(compress(seq, row["date"]))
    return days


# --------------------------------------------------------------------------
# Synthetic days
# --------------------------------------------------------------------------

def synthetic_days(
    n_days: int,
    mean: float,
    sd: float,
    bars: int = 30,
    trade_frac: float = 1.0,
    seed: int = 0,
) -> list[Day]:
    """Gaussian random-walk days.

    mean, sd: P&L per trade per unit, in dollars (one trade per traded day).
    bars: path resolution within the holding window (30 = a 30-minute hold on
    1-minute bars). trade_frac: share of days with a trade.
    """
    rng = np.random.default_rng(seed)
    steps = rng.normal(0.0, 1.0, size=(n_days, bars))
    paths = np.cumsum(steps, axis=1)
    traded = rng.random(n_days) < trade_frac
    # Moment-match the traded days' closes to exactly (mean, sd). Sampling noise in
    # a 2,500-day bank is ~sd/50 per day, as large as the edges being tested.
    if traded.sum() < 2:
        raise ValueError("synthetic_days needs at least 2 traded days; raise n_days or trade_frac")
    ramp = np.arange(1, bars + 1) / bars
    c = paths[traded, -1]
    paths = (paths - c.mean() * ramp) * (sd / c.std()) + mean * ramp
    days = []
    for i in range(n_days):
        days.append(compress(paths[i] if traded[i] else [0.0], f"syn{i}"))
    return days


# --------------------------------------------------------------------------
# Resampling
# --------------------------------------------------------------------------

def stationary_bootstrap_indices(n: int, length: int, block: float, rng: np.random.Generator) -> np.ndarray:
    """Politis-Romano stationary bootstrap: blocks of geometric mean length `block`."""
    if n <= 0:
        raise ValueError("empty day bank")
    p_new = 1.0 / max(block, 1.0)
    new_block = rng.random(length) < p_new
    starts = rng.integers(0, n, size=length)
    out = np.empty(length, dtype=np.int64)
    cur = int(starts[0])
    out[0] = cur
    for t in range(1, length):
        cur = int(starts[t]) if new_block[t] else (cur + 1) % n
        out[t] = cur
    return out


class DayStream:
    """Iterator over resampled days that counts how many were consumed."""

    def __init__(self, days: Sequence[Day], idx: np.ndarray) -> None:
        self._days = days
        self._idx = idx
        self.used = 0

    def __iter__(self) -> Iterator[Day]:
        return self

    def __next__(self) -> Day:
        if self.used >= len(self._idx):
            raise StopIteration
        d = self._days[self._idx[self.used]]
        self.used += 1
        return d
