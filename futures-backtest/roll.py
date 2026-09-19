"""Roll logic: which contract you hold, when you swap, and the price gap it leaves.

Two jobs, kept strictly apart:

1. `roll_schedule` decides which delivery month is held on each trading day.
   The engine uses this to mark P&L against the contract it actually holds and
   to charge a real round-turn cost on the swap day.

2. `continuous` splices the segments into one gap-free price series *for signal
   purposes only*. Back-adjustment (panama) removes the roll gap by shifting
   history, which is what makes a 12-month momentum reading meaningful — and
   also why an adjusted series must never be used to compute dollar P&L or
   margin: its absolute level is fictional, only its differences are real.

Convention used throughout: on roll date `d` the old contract is sold and the
new one bought at that day's settles. So the old contract is marked through
`d`, and the new contract is marked from `d` onward. That is exactly the
assumption panama adjustment encodes, which is what makes the engine's
"hold one contract forever" P&L equal the adjusted price change minus costs.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from data import ContractSeries, MarketData

PANAMA = "panama"
RATIO = "ratio"
UNADJUSTED = "none"
ADJUSTMENTS = (PANAMA, RATIO, UNADJUSTED)

CALENDAR = "calendar"
VOLUME = "volume"
ROLL_METHODS = (CALENDAR, VOLUME)


@dataclass
class Segment:
    """One holding period of one delivery month."""

    contract: ContractSeries
    start: date                  # first date held (inclusive)
    end: date                    # last date held (inclusive) = roll date
    rolled: bool = True          # False on the final segment (nothing to roll into)
    gap_roll: bool = False       # True if old/new never quoted on the same day

    @property
    def code(self) -> str:
        return self.contract.code

    def dates(self) -> list[date]:
        return [d for d in self.contract.dates if self.start <= d <= self.end]

    def close(self, d: date) -> float | None:
        return self.contract.close(d)

    def __repr__(self) -> str:
        return f"<Segment {self.code} {self.start}..{self.end}>"


def _calendar_target(contract: ContractSeries, offset_days: int) -> date:
    """The date `offset_days` trading days before the contract's last quote."""
    ds = contract.dates
    idx = max(0, len(ds) - 1 - max(0, offset_days))
    return ds[idx]


def _volume_target(old: ContractSeries, new: ContractSeries,
                   candidates: list[date]) -> date | None:
    """First common date on which the back month trades more than the front.

    Liquidity-based rolls are what a discretionary desk does and what most
    vendors use. Returns None when the data carries no volume/OI, so the
    caller can fall back to the calendar rule.
    """
    for d in candidates:
        ob, nb = old.bars.get(d), new.bars.get(d)
        if ob is None or nb is None:
            continue
        if (nb.volume > ob.volume and nb.volume > 0) or \
           (nb.open_interest > ob.open_interest and nb.open_interest > 0):
            return d
    return None      # no crossover (or no volume/OI data): use the calendar rule


def roll_schedule(market: MarketData, offset_days: int | None = None,
                  method: str = CALENDAR, start: date | None = None,
                  end: date | None = None) -> list[Segment]:
    """Build the chain of held contracts over the sample.

    offset_days: trading days before a contract's last quote at which to roll
        (defaults to the spec's `roll_offset_days`).
    method: 'calendar' (fixed offset) or 'volume' (roll when the back month
        out-trades the front, capped at the calendar date so an illiquid tape
        can never push the roll past expiry).
    """
    if method not in ROLL_METHODS:
        raise ValueError(f"method must be one of {ROLL_METHODS}, got {method!r}")
    offset = market.spec.roll_offset_days if offset_days is None else offset_days

    chain = [c for c in market.contracts if len(c.bars) >= 2]
    if start is not None:
        chain = [c for c in chain if c.last_date >= start]
    if end is not None:
        chain = [c for c in chain if c.first_date <= end]
    if not chain:
        raise ValueError(f"{market.symbol}: no contracts with data in range")

    segments: list[Segment] = []
    cursor = chain[0].first_date
    if start is not None:
        cursor = max(cursor, start)

    i = 0
    while i < len(chain):
        cur = chain[i]
        held = [d for d in cur.dates if d >= cursor]
        if not held:                    # fully consumed by an earlier segment
            i += 1
            continue
        nxt = chain[i + 1] if i + 1 < len(chain) else None
        if nxt is None:
            segments.append(Segment(cur, held[0], held[-1], rolled=False))
            break

        common = [d for d in cur.dates if d in nxt.bars and d >= held[0]]
        target = _calendar_target(cur, offset)
        if common:
            if method == VOLUME:
                vd = _volume_target(cur, nxt, common)
                # never roll later than the calendar rule would
                usable = [d for d in common if d <= target] or [common[0]]
                roll_d = min(vd, usable[-1]) if vd is not None else usable[-1]
                roll_d = max(roll_d, common[0])
            else:
                roll_d = ([d for d in common if d <= target] or [common[0]])[-1]
            segments.append(Segment(cur, held[0], roll_d))
            follow = [d for d in nxt.dates if d > roll_d]
        else:
            # No overlapping quote: the chain has a hole. Hold to the last
            # quote and re-enter in the next contract; the engine pays a
            # round turn and the adjustment for this roll is unknown (0).
            segments.append(Segment(cur, held[0], held[-1], gap_roll=True))
            follow = [d for d in nxt.dates if d > held[-1]]

        if not follow:
            i += 1
            continue
        cursor = follow[0]
        i += 1

    if end is not None:
        trimmed = []
        for s in segments:
            if s.start > end:
                continue
            trimmed.append(s if s.end <= end
                           else Segment(s.contract, s.start, end, rolled=False,
                                        gap_roll=s.gap_roll))
        segments = trimmed
    return segments


def held_contract(segments: list[Segment]) -> dict[date, Segment]:
    """date -> the segment (hence contract) held at that day's close."""
    out: dict[date, Segment] = {}
    for s in segments:
        for d in s.dates():
            out[d] = s
    return out


def roll_dates(segments: list[Segment]) -> list[date]:
    return [s.end for s in segments if s.rolled]


def roll_gaps(segments: list[Segment]) -> list[dict]:
    """Per-roll diagnostics: the price step between old and new contract.

    Positive gap = the back month is dearer than the front (contango in a
    price-quoted market). Summed, these gaps are the entire difference between
    an adjusted and an unadjusted history — worth printing before trusting any
    long-horizon result.
    """
    rows = []
    for a, b in zip(segments, segments[1:]):
        old_px = a.close(a.end)
        new_px = b.contract.close(a.end)
        gap = None if (old_px is None or new_px is None) else new_px - old_px
        rows.append({
            "date": a.end,
            "out": a.code,
            "into": b.code,
            "old_close": old_px,
            "new_close": new_px,
            "gap": gap,
            "gap_roll": a.gap_roll,
        })
    return rows


def continuous(segments: list[Segment], method: str = PANAMA) -> dict[date, float]:
    """Splice segments into one series for signal use.

    panama : additive back-adjustment — differences are exact, levels drift.
    ratio  : multiplicative — percentage changes are exact, levels drift.
    none   : raw front-month stitch — levels are real, roll days carry a
             fictional jump that will corrupt any momentum signal.
    """
    if method not in ADJUSTMENTS:
        raise ValueError(f"method must be one of {ADJUSTMENTS}, got {method!r}")
    if not segments:
        return {}

    n = len(segments)
    adj = [0.0] * n if method == PANAMA else [1.0] * n
    # Walk backwards: the newest segment is left unadjusted (real prices),
    # history is shifted onto it so no roll gap survives.
    for i in range(n - 2, -1, -1):
        old, new = segments[i], segments[i + 1]
        d = old.end
        old_px, new_px = old.close(d), new.contract.close(d)
        if method == PANAMA:
            step = 0.0 if (old_px is None or new_px is None) else new_px - old_px
            adj[i] = adj[i + 1] + step
        elif method == RATIO:
            ok = old_px not in (None, 0) and new_px is not None
            adj[i] = adj[i + 1] * (new_px / old_px if ok else 1.0)

    out: dict[date, float] = {}
    for seg, a in zip(segments, adj):
        for d in seg.dates():
            px = seg.close(d)
            if px is None:
                continue
            if method == PANAMA:
                out[d] = px + a
            elif method == RATIO:
                out[d] = px * a
            else:
                out[d] = px
    return out
