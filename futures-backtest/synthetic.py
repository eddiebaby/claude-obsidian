"""Deterministic synthetic futures data, so the engine is runnable with no vendor feed.

Why this exists: a futures backtester's hard parts (rolls, integer contracts,
margin, mark-to-market) can be verified without paying for history, and the
test suite has to be hermetic. Everything here is seeded — same seed, same
bars, on any machine.

Read this twice: **synthetic paths contain trend by construction.** A slow
mean-reverting drift process is layered on the noise, so a trend-following
strategy will show a flattering Sharpe. That number validates the *plumbing*,
not the *edge*. Any performance claim has to come from real bars (Norgate,
Databento, CME) loaded through `data.load_book`.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import date, timedelta

import contracts as cx
from data import Bar, ContractSeries, MarketData, RateSeries

# --- calendar ---------------------------------------------------------------

def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    d = date(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(days=7 * (n - 1))


def _last_weekday(year: int, month: int, weekday: int) -> date:
    d = date(year, month, 1) + timedelta(days=31)
    d = d.replace(day=1) - timedelta(days=1)      # last day of `month`
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def _observed(d: date) -> date:
    """US market holiday convention: Saturday -> Friday, Sunday -> Monday."""
    if d.weekday() == 5:
        return d - timedelta(days=1)
    if d.weekday() == 6:
        return d + timedelta(days=1)
    return d


def holidays(year: int) -> set[date]:
    """CME-ish full-holiday approximation. Good enough for a synthetic tape."""
    return {
        _observed(date(year, 1, 1)),                    # New Year's Day
        _nth_weekday(year, 1, 0, 3),                    # MLK
        _nth_weekday(year, 2, 0, 3),                    # Presidents' Day
        _last_weekday(year, 5, 0),                      # Memorial Day (last Mon)
        _observed(date(year, 7, 4)),                    # Independence Day
        _nth_weekday(year, 9, 0, 1),                    # Labor Day
        _nth_weekday(year, 11, 3, 4),                   # Thanksgiving
        _observed(date(year, 12, 25)),                  # Christmas
    }


def trading_days(start: date, end: date) -> list[date]:
    """Weekdays minus approximate US holidays."""
    hol: set[date] = set()
    for y in range(start.year, end.year + 1):
        hol |= holidays(y)
    out, d = [], start
    while d <= end:
        if d.weekday() < 5 and d not in hol:
            out.append(d)
        d += timedelta(days=1)
    return out


# --- price paths ------------------------------------------------------------

TRADING_DAYS = 252


def _gauss_stream(seed: int):
    rng = random.Random(seed)
    while True:
        yield rng.gauss(0.0, 1.0)


@dataclass
class PathParams:
    ann_vol: float = 0.16
    ann_drift: float = 0.03
    trend_vol: float = 0.03      # size of the slow drift process (annualised)
    trend_halflife: int = 250    # trading days — this is what makes trend exist
    carry: float = 0.02          # annualised futures-vs-spot basis
    start_price: float = 100.0
    beta: float = 0.0            # loading on a shared asset-class factor
    floor: float | None = None   # reflecting barrier for additive paths (yields)


# Per-asset-class defaults. Rough, but the relative ordering is the point:
# crypto and energy move several times as much as FX, and that is what drives
# how many contracts a vol target lets you hold.
CLASS_DEFAULTS: dict[str, PathParams] = {
    "equity": PathParams(ann_vol=0.17, ann_drift=0.06, carry=0.025, beta=0.85),
    "metal":  PathParams(ann_vol=0.16, ann_drift=0.03, carry=0.02, beta=0.55),
    "energy": PathParams(ann_vol=0.34, ann_drift=0.01, carry=-0.04, beta=0.25),
    "fx":     PathParams(ann_vol=0.08, ann_drift=0.00, carry=-0.005, beta=0.35),
    "crypto": PathParams(ann_vol=0.60, ann_drift=0.10, carry=0.05, beta=0.45),
    "rates":  PathParams(ann_vol=0.14, ann_drift=0.00, carry=0.02, beta=0.20,
                         floor=0.25),
}

START_PRICES = {
    "MES": 5900.0, "MNQ": 21000.0, "M2K": 2350.0, "MYM": 44000.0,
    "ES": 5900.0, "NQ": 21000.0,
    "MGC": 3350.0, "GC": 3350.0, "SIL": 38.0,
    "MCL": 71.0, "CL": 71.0,
    "M6E": 1.085, "M6B": 1.27,
    "MBT": 96000.0,
    "10Y": 4.25, "ZN": 111.5,
}


def factor_path(n: int, seed: int, halflife: int = 180) -> list[float]:
    """Shared standardised factor returns — gives the book realistic correlation."""
    g = _gauss_stream(seed)
    phi = 0.5 ** (1.0 / max(1, halflife))
    trend, out = 0.0, []
    for _ in range(n):
        trend = phi * trend + math.sqrt(1 - phi * phi) * next(g)
        # 0.03, not 0.3: the coefficient IS the per-market trend Sharpe knob.
        # At 0.3 a 12-month momentum signal prints Sharpe > 2 and the whole
        # demo becomes a lie about how easy this is.
        out.append(0.03 * trend + next(g))
    return out


def spot_path(dates: list[date], p: PathParams, seed: int,
              factor: list[float] | None = None,
              absolute: bool = False) -> dict[date, float]:
    """One market's 'spot' series: slow trending drift + noise (+ factor).

    absolute=True generates an additive path (for yield-quoted markets, where a
    multiplicative path is nonsense near zero).
    """
    g = _gauss_stream(seed)
    n = len(dates)
    phi = 0.5 ** (1.0 / max(1, p.trend_halflife))
    dvol = p.ann_vol / math.sqrt(TRADING_DAYS)
    tvol = p.trend_vol / TRADING_DAYS
    beta = p.beta if factor else 0.0
    idio = math.sqrt(max(0.0, 1.0 - beta * beta))

    drift, px = 0.0, p.start_price
    out: dict[date, float] = {}
    for i, d in enumerate(dates):
        shock = (beta * factor[i] + idio * next(g)) if factor else next(g)
        drift = phi * drift + math.sqrt(1 - phi * phi) * tvol * next(g)
        r = p.ann_drift / TRADING_DAYS + drift + dvol * shock
        px = px + r * p.start_price if absolute else px * math.exp(r)
        if absolute and p.floor is not None and px < p.floor:
            px = p.floor + (p.floor - px)     # reflect: yields do not go to -3%
        out[d] = px if absolute else max(px, 1e-6)
    return out


# --- contract construction --------------------------------------------------

def expiry_for(spec: cx.ContractSpec, year: int, month: int) -> date:
    """Third Friday for financials; ~20th for physical commodities."""
    if spec.asset_class in ("equity", "fx", "rates", "crypto"):
        return _nth_weekday(year, month, 4, 3)
    d = date(year, month, 20)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def _volume_shape(days_to_expiry: int, spacing_days: int) -> float:
    """Unimodal liquidity profile that makes the back month overtake the front
    roughly `spacing/2 - peak` days out, so volume-based rolls have something
    to detect."""
    peak = spacing_days / 2.0 + 10.0
    width = max(20.0, spacing_days * 0.5)
    return math.exp(-(((days_to_expiry - peak) / width) ** 2))


def synthetic_market(spec: cx.ContractSpec, start: date, end: date, seed: int = 0,
                     params: PathParams | None = None,
                     factor: list[float] | None = None,
                     life_months: int = 12) -> MarketData:
    """Build every delivery month of one market from a single spot path."""
    p = params or CLASS_DEFAULTS.get(spec.asset_class, PathParams())
    p = PathParams(**{**p.__dict__,
                      "start_price": START_PRICES.get(spec.symbol, p.start_price)})
    absolute = spec.vol_basis == "abs"
    days = trading_days(start, end)
    spot = spot_path(days, p, seed, factor=factor, absolute=absolute)

    spacing = 365 // max(1, len(spec.roll_months))
    series: list[ContractSeries] = []
    for year in range(start.year, end.year + 2):
        for month in spec.roll_months:
            exp = expiry_for(spec, year, month)
            listed = exp - timedelta(days=int(30.4 * life_months))
            bars: dict[date, Bar] = {}
            for d in days:
                if not (listed <= d <= exp):
                    continue
                s = spot.get(d)
                if s is None:
                    continue
                yrs = (exp - d).days / 365.0
                if absolute:
                    f = s + p.carry * yrs
                else:
                    f = s * math.exp(p.carry * yrs)
                f = spec.round_price(f)
                dte = (exp - d).days
                vol = 1e5 * _volume_shape(dte, spacing)
                bars[d] = Bar(d, f, f, f, f, round(vol), round(vol * 8))
            if len(bars) >= 20:
                series.append(ContractSeries(spec.symbol, year, month, bars,
                                             expiry=min(exp, days[-1])))
    if not series:
        raise ValueError(f"{spec.symbol}: synthetic range too short")
    return MarketData(spec=spec, contracts=series)


def synthetic_book(symbols=cx.MICRO_UNIVERSE, start: date = date(2010, 1, 4),
                   end: date = date(2026, 6, 30), seed: int = 20260919,
                   life_months: int = 12) -> dict[str, MarketData]:
    """A whole correlated universe. Markets in the same asset class share a factor."""
    days = trading_days(start, end)
    factors: dict[str, list[float]] = {}
    book: dict[str, MarketData] = {}
    for i, sym in enumerate(symbols):
        spec = cx.get(sym)
        cls = spec.asset_class
        if cls not in factors:
            factors[cls] = factor_path(len(days), seed + 977 * (len(factors) + 1))
        book[sym] = synthetic_market(spec, start, end, seed=seed + 31 * (i + 1),
                                     factor=factors[cls], life_months=life_months)
    return book


def synthetic_rates(start: date = date(2010, 1, 4), end: date = date(2026, 6, 30),
                    seed: int = 7, level: float = 0.025, swing: float = 0.02,
                    haircut: float = 0.005) -> RateSeries:
    """A slowly cycling collateral rate, floored at zero (2010s ZIRP, 2020s 5%)."""
    days = trading_days(start, end)
    g = _gauss_stream(seed)
    phi = 0.5 ** (1.0 / 500.0)
    x, rates = 0.0, {}
    for d in days:
        x = phi * x + math.sqrt(1 - phi * phi) * next(g)
        rates[d] = max(0.0, level + swing * x)
    return RateSeries(rates=rates, haircut=haircut)
