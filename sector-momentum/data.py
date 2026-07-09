"""Data layer: adjusted daily closes from the Yahoo chart API (no key required).

One endpoint carries the whole strategy: the 11 SPDR sector ETFs, SPY (benchmark),
and ^IRX (13-week T-bill yield, the absolute-momentum hurdle / cash-leg rate).
Everything is cached to CSV in data/ so a re-run is offline and reproducible.
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

# 11 SPDR sector ETFs (spec universe). XLRE (2015) and XLC (2018) come in late;
# the backtest treats the universe as growing and only ranks ETFs with enough history.
SECTOR_ETFS = ["XLK", "XLF", "XLV", "XLE", "XLI", "XLY", "XLP", "XLB", "XLU", "XLRE", "XLC"]
BENCHMARK = "SPY"
TBILL = "^IRX"  # 13-week T-bill discount yield, annualized percent

DATA_DIR = Path(__file__).parent / "data"
_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=0&period2=9999999999&interval=1d"


def _fetch_one(symbol: str) -> pd.Series:
    """Return a date-indexed Series of adjusted close for one symbol."""
    sym = symbol.replace("^", "%5E")
    url = _CHART.format(sym=sym)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=30).read().decode()
    res = json.loads(raw)["chart"]["result"][0]
    ts = res["timestamp"]
    ind = res["indicators"]
    # ^IRX has no adjclose block; fall back to raw close.
    if "adjclose" in ind and ind["adjclose"][0].get("adjclose"):
        vals = ind["adjclose"][0]["adjclose"]
    else:
        vals = ind["quote"][0]["close"]
    idx = pd.to_datetime(ts, unit="s").normalize()
    s = pd.Series(vals, index=idx, name=symbol).dropna()
    s = s[~s.index.duplicated(keep="last")]
    return s


def load(symbols=None, refresh: bool = False) -> pd.DataFrame:
    """Load adjusted closes for all symbols into one wide DataFrame (cached)."""
    if symbols is None:
        symbols = SECTOR_ETFS + [BENCHMARK, TBILL]
    DATA_DIR.mkdir(exist_ok=True)
    series = {}
    for sym in symbols:
        cache = DATA_DIR / f"{sym.replace('^', '_')}.csv"
        if cache.exists() and not refresh:
            s = pd.read_csv(cache, index_col=0, parse_dates=True).iloc[:, 0]
            s.name = sym
        else:
            s = _fetch_one(sym)
            s.to_frame().to_csv(cache)
            time.sleep(0.3)  # be polite to the endpoint
            print(f"  fetched {sym:6s} {len(s):5d} rows  {s.index[0].date()} -> {s.index[-1].date()}")
        series[sym] = s
    df = pd.DataFrame(series).sort_index()
    return df


if __name__ == "__main__":
    print("Downloading full history for the sector-momentum universe...")
    df = load(refresh=True)
    print(f"\nUniverse matrix: {df.shape[0]} days x {df.shape[1]} symbols")
    print(f"Range: {df.index[0].date()} -> {df.index[-1].date()}")
    print("\nFirst valid date per symbol:")
    print(df.apply(lambda c: c.first_valid_index()).sort_values().to_string())
