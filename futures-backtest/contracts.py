"""Contract specifications — the thing an equity backtester never needs.

A futures P&L is not `weight * pct_return`. It is
`contracts * multiplier * (settle_today - settle_yesterday) * fx`, in integer
contract units, against margin rather than cash. Every number that turns a
price move into dollars lives here.

The margin and commission figures are *plausible 2026 retail estimates*, not
quotes. They are inputs, not gospel: check the CME contract spec page and your
broker's margin table before sizing real money, then edit the registry. Tick
size and multiplier are contract-definitional and safe; margin moves with
volatility and commission moves with your broker.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

# CME month codes. Quarterly cycle = HMUZ; most financials use it.
MONTH_CODES = {1: "F", 2: "G", 3: "H", 4: "J", 5: "K", 6: "M",
               7: "N", 8: "Q", 9: "U", 10: "V", 11: "X", 12: "Z"}
CODE_MONTHS = {v: k for k, v in MONTH_CODES.items()}

QUARTERLY = (3, 6, 9, 12)
ALL_MONTHS = tuple(range(1, 13))


@dataclass(frozen=True)
class ContractSpec:
    """Everything needed to price, size, roll and cost one futures market."""

    symbol: str                 # root symbol, e.g. "MES"
    name: str
    asset_class: str            # equity | rates | fx | metal | energy | crypto
    exchange: str
    currency: str
    multiplier: float           # account currency per 1.00 of price
    tick_size: float            # minimum price increment
    commission: float           # per contract per side, all-in (broker + fees)
    initial_margin: float       # per contract, overnight
    maintenance_margin: float   # per contract
    slippage_ticks: float = 1.0     # modelled fill cost per side, in ticks
    roll_months: tuple = QUARTERLY  # delivery months actually traded
    roll_offset_days: int = 5       # trading days before expiry to roll
    vol_basis: str = "pct"          # "pct" = returns; "abs" = price diffs
    risk_weight: float = 1.0        # <1 to half-weight short-history markets
    notes: str = ""

    @property
    def tick_value(self) -> float:
        """Account currency per one tick of price movement, per contract."""
        return self.multiplier * self.tick_size

    def point_value(self, points: float = 1.0) -> float:
        return points * self.multiplier

    def cost_per_contract(self, slippage_ticks: float | None = None) -> float:
        """One-way cost of trading one contract: commission + modelled slippage."""
        ticks = self.slippage_ticks if slippage_ticks is None else slippage_ticks
        return self.commission + ticks * self.tick_value

    def round_price(self, price: float) -> float:
        """Snap a price to the contract's tick grid."""
        return round(price / self.tick_size) * self.tick_size


# --- CME micro universe (the retail-accessible diversified trend book) -------
# Sized so an 8-10 market vol-targeted book is feasible in the $25-50K range.
_SPECS: dict[str, ContractSpec] = {}


def _add(spec: ContractSpec) -> ContractSpec:
    _SPECS[spec.symbol] = spec
    return spec


_add(ContractSpec("MES", "Micro E-mini S&P 500", "equity", "CME", "USD",
                  multiplier=5.0, tick_size=0.25, commission=0.85,
                  initial_margin=2400.0, maintenance_margin=2200.0))
_add(ContractSpec("MNQ", "Micro E-mini Nasdaq 100", "equity", "CME", "USD",
                  multiplier=2.0, tick_size=0.25, commission=0.85,
                  initial_margin=2900.0, maintenance_margin=2650.0))
_add(ContractSpec("M2K", "Micro E-mini Russell 2000", "equity", "CME", "USD",
                  multiplier=5.0, tick_size=0.10, commission=0.85,
                  initial_margin=900.0, maintenance_margin=820.0))
_add(ContractSpec("MYM", "Micro E-mini Dow", "equity", "CME", "USD",
                  multiplier=0.5, tick_size=1.0, commission=0.85,
                  initial_margin=1100.0, maintenance_margin=1000.0))
_add(ContractSpec("MGC", "Micro Gold", "metal", "COMEX", "USD",
                  multiplier=10.0, tick_size=0.10, commission=0.85,
                  initial_margin=1150.0, maintenance_margin=1050.0))
_add(ContractSpec("SIL", "Micro Silver (1,000 oz)", "metal", "COMEX", "USD",
                  multiplier=1000.0, tick_size=0.005, commission=0.85,
                  initial_margin=2500.0, maintenance_margin=2250.0,
                  roll_months=(3, 5, 7, 9, 12)))
_add(ContractSpec("MCL", "Micro WTI Crude Oil", "energy", "NYMEX", "USD",
                  multiplier=100.0, tick_size=0.01, commission=0.85,
                  initial_margin=800.0, maintenance_margin=730.0,
                  roll_months=ALL_MONTHS, roll_offset_days=8,
                  notes="Monthly expiry; roll early, front month goes illiquid fast."))
_add(ContractSpec("M6E", "Micro EUR/USD", "fx", "CME", "USD",
                  multiplier=12500.0, tick_size=0.0001, commission=0.55,
                  initial_margin=280.0, maintenance_margin=255.0))
_add(ContractSpec("M6B", "Micro GBP/USD", "fx", "CME", "USD",
                  multiplier=6250.0, tick_size=0.0001, commission=0.55,
                  initial_margin=230.0, maintenance_margin=210.0))
_add(ContractSpec("MBT", "Micro Bitcoin (0.1 BTC)", "crypto", "CME", "USD",
                  multiplier=0.1, tick_size=5.0, commission=2.50,
                  initial_margin=3000.0, maintenance_margin=2700.0,
                  roll_months=ALL_MONTHS, risk_weight=0.5,
                  notes="Short history and regime-dependent — half risk weight."))
_add(ContractSpec("10Y", "Micro 10-Year Yield", "rates", "CBOT", "USD",
                  multiplier=1000.0, tick_size=0.001, commission=0.55,
                  initial_margin=330.0, maintenance_margin=300.0,
                  roll_months=ALL_MONTHS, vol_basis="abs",
                  notes="Quoted in yield: 4.250 = 4.25%. Long = long YIELD, "
                        "i.e. short duration. vol_basis='abs' because percent "
                        "vol of a yield is meaningless near zero."))

# --- full-size contracts, for when equity outgrows the micros ---------------
_add(ContractSpec("ES", "E-mini S&P 500", "equity", "CME", "USD",
                  multiplier=50.0, tick_size=0.25, commission=2.30,
                  initial_margin=24000.0, maintenance_margin=21800.0))
_add(ContractSpec("NQ", "E-mini Nasdaq 100", "equity", "CME", "USD",
                  multiplier=20.0, tick_size=0.25, commission=2.30,
                  initial_margin=29000.0, maintenance_margin=26400.0))
_add(ContractSpec("GC", "Gold (100 oz)", "metal", "COMEX", "USD",
                  multiplier=100.0, tick_size=0.10, commission=2.50,
                  initial_margin=11500.0, maintenance_margin=10450.0))
_add(ContractSpec("CL", "WTI Crude Oil (1,000 bbl)", "energy", "NYMEX", "USD",
                  multiplier=1000.0, tick_size=0.01, commission=2.50,
                  initial_margin=8000.0, maintenance_margin=7300.0,
                  roll_months=ALL_MONTHS, roll_offset_days=8))
_add(ContractSpec("ZN", "10-Year T-Note", "rates", "CBOT", "USD",
                  multiplier=1000.0, tick_size=0.015625, commission=2.10,
                  initial_margin=2100.0, maintenance_margin=1900.0,
                  vol_basis="abs",
                  notes="Priced in 32nds; tick is 1/64 of a point = $15.625."))

# The default book: 8 micros across 6 asset classes. Diversification across
# classes IS the strategy — equity-only trend is just slow beta timing.
MICRO_UNIVERSE = ("MES", "MNQ", "M2K", "MGC", "MCL", "M6E", "M6B", "10Y")


def get(symbol: str) -> ContractSpec:
    try:
        return _SPECS[symbol]
    except KeyError:
        raise KeyError(f"unknown contract {symbol!r}; known: {sorted(_SPECS)}") from None


def universe(symbols=MICRO_UNIVERSE) -> list[ContractSpec]:
    return [get(s) for s in symbols]


def register(spec: ContractSpec) -> ContractSpec:
    """Add or replace a spec at runtime (your broker's numbers beat these)."""
    return _add(spec)


def override(symbol: str, **fields) -> ContractSpec:
    """Return a copy of a spec with fields replaced, and register it."""
    return _add(replace(get(symbol), **fields))


def contract_code(symbol: str, year: int, month: int) -> str:
    """'MES', 2026, 3 -> 'MESH26' (the ticker you actually send to the broker)."""
    return f"{symbol}{MONTH_CODES[month]}{year % 100:02d}"


def all_symbols() -> list[str]:
    return sorted(_SPECS)
