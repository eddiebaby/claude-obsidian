"""Data layer: individual delivery-month bars, plus the cash-collateral rate.

The engine is deliberately built on *individual contract* bars, not on a
vendor's back-adjusted continuous series. That ordering matters:

  - signals come from a continuous series (roll.py builds it),
  - P&L comes from the contract actually held, at its own settle price,
  - the roll itself is a real trade with a real cost.

A back-adjusted continuous file cannot express the third point, which is why
"continuous-only" mode (load_continuous) is offered but labelled approximate.

Expected layout for real data (Norgate / Databento / CME exports all reshape
into this with a few lines of glue):

    data/MES/MESH26.csv
    data/MES/MESM26.csv
    ...
    date,open,high,low,close,volume,open_interest
    2026-01-02,5901.25,5930.00,5895.50,5925.75,182340,1204553

`volume` / `open_interest` are optional but enable liquidity-based rolls.
"""
from __future__ import annotations

import bisect
import csv
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import contracts as cx

_FILENAME_RE = re.compile(r"^([A-Z0-9]{1,4})([FGHJKMNQUVXZ])(\d{2})$")


def parse_date(s: str) -> date:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%Y%m%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognised date {s!r}")


@dataclass(frozen=True)
class Bar:
    date: date
    open: float
    high: float
    low: float
    close: float          # settlement price — what P&L is marked against
    volume: float = 0.0
    open_interest: float = 0.0


@dataclass
class ContractSeries:
    """One delivery month of one market."""

    symbol: str
    year: int
    month: int
    bars: dict[date, Bar] = field(default_factory=dict)
    expiry: date | None = None     # None -> inferred as the last quoted bar

    @property
    def code(self) -> str:
        return cx.contract_code(self.symbol, self.year, self.month)

    @property
    def dates(self) -> list[date]:
        return sorted(self.bars)

    @property
    def last_date(self) -> date:
        return self.dates[-1]

    @property
    def first_date(self) -> date:
        return self.dates[0]

    @property
    def delivery(self) -> tuple[int, int]:
        return (self.year, self.month)

    def expiry_date(self) -> date:
        return self.expiry or self.last_date

    def close(self, d: date) -> float | None:
        bar = self.bars.get(d)
        return None if bar is None else bar.close

    def __repr__(self) -> str:
        if not self.bars:
            return f"<ContractSeries {self.code} empty>"
        return (f"<ContractSeries {self.code} {len(self.bars)} bars "
                f"{self.first_date}..{self.last_date}>")


@dataclass
class MarketData:
    """All delivery months of one market, chronologically ordered."""

    spec: cx.ContractSpec
    contracts: list[ContractSeries] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.contracts.sort(key=lambda c: (c.delivery, c.expiry_date()))

    @property
    def symbol(self) -> str:
        return self.spec.symbol

    def all_dates(self) -> list[date]:
        seen: set[date] = set()
        for c in self.contracts:
            seen.update(c.bars)
        return sorted(seen)

    def by_code(self, code: str) -> ContractSeries:
        for c in self.contracts:
            if c.code == code:
                return c
        raise KeyError(f"{self.symbol}: no contract {code}")

    def __repr__(self) -> str:
        return f"<MarketData {self.symbol} {len(self.contracts)} contracts>"


# --- CSV loading -------------------------------------------------------------

def load_contract_csv(path: str | Path, symbol: str | None = None,
                      year: int | None = None, month: int | None = None,
                      expiry: date | None = None,
                      century: int = 2000) -> ContractSeries:
    """Read one delivery month's bars. Delivery is parsed from the filename
    (e.g. MESH26.csv) unless given explicitly."""
    path = Path(path)
    if symbol is None or year is None or month is None:
        m = _FILENAME_RE.match(path.stem.upper())
        if not m:
            raise ValueError(
                f"cannot parse contract from filename {path.name!r}; expected "
                "<ROOT><MONTHCODE><YY>.csv such as MESH26.csv, or pass "
                "symbol/year/month explicitly")
        symbol = symbol or m.group(1)
        month = month or cx.CODE_MONTHS[m.group(2)]
        year = year or century + int(m.group(3))

    if not (1 <= int(month) <= 12):
        raise ValueError(f"{path.name}: delivery month {month} is not 1-12")

    bars: dict[date, Bar] = {}
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            keys = {k.strip().lower(): v for k, v in row.items() if k}
            d = parse_date(keys["date"])
            close = float(keys["close"])
            bars[d] = Bar(
                date=d,
                open=float(keys.get("open") or close),
                high=float(keys.get("high") or close),
                low=float(keys.get("low") or close),
                close=close,
                volume=float(keys.get("volume") or 0.0),
                open_interest=float(keys.get("open_interest")
                                    or keys.get("openinterest") or 0.0),
            )
    if not bars:
        raise ValueError(f"{path}: no rows")
    return ContractSeries(symbol=symbol, year=year, month=month, bars=bars,
                          expiry=expiry)


def load_market(directory: str | Path, spec: cx.ContractSpec | str,
                expiries: dict[str, date] | None = None,
                use_proxy: bool = True) -> MarketData:
    """Load every <ROOT><CODE><YY>.csv in `directory` for one market.

    If no files match the spec's own root and it declares a `history_proxy`,
    the parent contract's files are used instead: ES bars under the MES spec,
    CL under MCL, and so on. That is how a twenty-year backtest of a 2019
    contract is done honestly — the price series is the same underlying, and
    the multiplier, tick and margin stay the micro's, which is what you trade.
    Pass use_proxy=False to forbid the substitution.
    """
    spec = cx.get(spec) if isinstance(spec, str) else spec
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"{directory} is not a directory")

    roots = [spec.symbol]
    if use_proxy and spec.history_proxy:
        roots.append(spec.history_proxy)

    for root in roots:
        series = []
        for path in sorted(directory.glob("*.csv")):
            m = _FILENAME_RE.match(path.stem.upper())
            if not m or m.group(1) != root:
                continue
            exp = (expiries or {}).get(path.stem.upper())
            cs = load_contract_csv(path, expiry=exp)
            if root != spec.symbol:
                # Keep the traded contract's identity; only the bars are borrowed.
                cs = ContractSeries(spec.symbol, cs.year, cs.month, cs.bars, cs.expiry)
            series.append(cs)
        if series:
            if root != spec.symbol:
                print(f"  {spec.symbol}: using {root} history "
                      f"({len(series)} contracts) — micro multiplier, parent bars")
            return MarketData(spec=spec, contracts=series)

    want = " or ".join(f"{r}H26.csv" for r in roots)
    raise FileNotFoundError(
        f"no contract files for {spec.symbol} in {directory} (expected e.g. {want})")


def load_book(root: str | Path, symbols=cx.MICRO_UNIVERSE) -> dict[str, MarketData]:
    """Load data/<SYMBOL>/*.csv for each symbol in the universe."""
    root = Path(root)
    book = {}
    for sym in symbols:
        book[sym] = load_market(root / sym, cx.get(sym))
    return book


def load_continuous(path: str | Path, spec: cx.ContractSpec | str,
                    roll_dates: list[date] | None = None,
                    rolls_per_year: int = 4) -> MarketData:
    """APPROXIMATE mode: wrap a single back-adjusted continuous CSV so the
    engine can run on vendor data you already have.

    The series is chopped into synthetic "contracts" at `roll_dates` (or at
    quarter ends). Because the file is already adjusted, roll gaps are zero by
    construction, so the engine charges the modelled round-turn cost at each
    roll but cannot see real calendar-spread slippage. Results are optimistic
    on cost and blind to term structure. Use individual contracts for anything
    you intend to trade.
    """
    spec = cx.get(spec) if isinstance(spec, str) else spec
    bars: dict[date, Bar] = {}
    with Path(path).open(newline="") as fh:
        for row in csv.DictReader(fh):
            keys = {k.strip().lower(): v for k, v in row.items() if k}
            d = parse_date(keys["date"])
            close = float(keys["close"])
            bars[d] = Bar(d, float(keys.get("open") or close),
                          float(keys.get("high") or close),
                          float(keys.get("low") or close), close,
                          float(keys.get("volume") or 0.0),
                          float(keys.get("open_interest") or 0.0))
    dates = sorted(bars)
    if roll_dates is None:
        step = max(1, round(252 / max(1, rolls_per_year)))
        roll_dates = [dates[i] for i in range(step, len(dates), step)]
    cuts = [d for d in sorted(set(roll_dates)) if dates[0] < d < dates[-1]]

    # Each segment spans [lo, hi] inclusive, so consecutive segments share the
    # roll-date bar and roll.py can price both legs on that date. (With a
    # pre-adjusted file the two legs are equal, so the roll gap is zero.)
    bounds = [dates[0]] + cuts + [dates[-1]]
    segments: list[ContractSeries] = []
    for lo, hi in zip(bounds, bounds[1:]):
        seg = {d: b for d, b in bars.items() if lo <= d <= hi}
        if len(seg) < 2:
            continue
        segments.append(ContractSeries(spec.symbol, hi.year, hi.month, seg,
                                       expiry=hi))
    return MarketData(spec=spec, contracts=segments)


# --- cash collateral rate ----------------------------------------------------

TRADING_DAYS = 252


@dataclass
class RateSeries:
    """Annualised collateral rate (decimal, e.g. 0.042) by date.

    Futures margin is posted, not spent: the unencumbered balance earns
    interest, and over 20 years that interest is a material part of a trend
    book's total return. Ignoring it is the most common futures backtest
    overstatement's mirror image — it understates.
    """

    rates: dict[date, float] = field(default_factory=dict)
    default: float = 0.0
    haircut: float = 0.005   # broker keeps a spread over the bill rate
    _keys: list = field(default_factory=list, repr=False)

    def _sorted_keys(self) -> list:
        if len(self._keys) != len(self.rates):
            self._keys = sorted(self.rates)
        return self._keys

    def annual(self, d: date) -> float:
        """Rate in force on `d`, carrying the last observation forward.

        Bisect, not a scan: this is called once per market per day, and a linear
        scan over a 20-year series turns the inner loop quadratic."""
        if not self.rates:
            return max(0.0, self.default - self.haircut)
        r = self.rates.get(d)
        if r is None:
            keys = self._sorted_keys()
            i = bisect.bisect_right(keys, d)
            r = self.rates[keys[i - 1]] if i else self.default
        return max(0.0, r - self.haircut)

    def daily(self, d: date) -> float:
        return (1.0 + self.annual(d)) ** (1.0 / TRADING_DAYS) - 1.0


def constant_rate(annual: float = 0.04, haircut: float = 0.005) -> RateSeries:
    return RateSeries(default=annual, haircut=haircut)


def load_rates(path: str | Path, column: str = "close",
               percent: bool = True, haircut: float = 0.005) -> RateSeries:
    """Load an annualised short rate (e.g. ^IRX, which quotes in percent)."""
    rates: dict[date, float] = {}
    with Path(path).open(newline="") as fh:
        for row in csv.DictReader(fh):
            keys = {k.strip().lower(): v for k, v in row.items() if k}
            val = keys.get(column.lower())
            if val in (None, ""):
                continue
            r = float(val)
            rates[parse_date(keys["date"])] = r / 100.0 if percent else r
    if not rates:
        raise ValueError(f"{path}: no usable rows (column {column!r})")
    return RateSeries(rates=rates, haircut=haircut)
