#!/usr/bin/env python3
"""test_futures_engine.py — hermetic tests for futures-backtest/.

Covers the things a futures backtester gets wrong silently:

  * contract arithmetic (tick value, cost per contract)
  * roll schedules and back-adjustment (the adjusted series must reproduce the
    P&L of holding and rolling one contract, to the cent)
  * mark-to-market accounting, roll costs, collateral interest
  * no lookahead: the signal on day t never sees day t's price
  * integer contracts, the margin ceiling, and forced liquidation
  * volatility estimation on an adjusted series whose level is fictional
  * metrics, including the deflated Sharpe's response to more trials

No network, no pandas, no numpy. Pure stdlib.

Usage:
  python3 tests/test_futures_engine.py
"""
import math
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "futures-backtest"))

import contracts as cx          # noqa: E402
import data as datamod          # noqa: E402
import engine                   # noqa: E402
import metrics as mt            # noqa: E402
import roll as rollmod          # noqa: E402
import sizing as sz             # noqa: E402
import strategies as st         # noqa: E402
import synthetic as syn         # noqa: E402

EPS = 1e-9


class Fail(SystemExit):
    pass


def assert_eq(label, expected, actual):
    if expected != actual:
        raise Fail(f"FAIL {label}: expected {expected!r}, got {actual!r}")
    print(f"OK   {label}")


def assert_close(label, expected, actual, tol=1e-6):
    if expected != expected or actual != actual or abs(expected - actual) > tol:
        raise Fail(f"FAIL {label}: expected {expected!r}, got {actual!r} (tol {tol})")
    print(f"OK   {label}")


def assert_true(label, cond, hint=""):
    if not cond:
        raise Fail(f"FAIL {label}{(': ' + hint) if hint else ''}")
    print(f"OK   {label}")


def assert_raises(label, exc, fn, *a, **kw):
    try:
        fn(*a, **kw)
    except exc:
        print(f"OK   {label}")
        return
    raise Fail(f"FAIL {label}: expected {exc.__name__}")


# --- fixtures ---------------------------------------------------------------

TEST_SPEC = cx.ContractSpec(
    "TST", "Test Contract", "equity", "TEST", "USD",
    multiplier=10.0, tick_size=0.01, commission=0.0,
    initial_margin=1000.0, maintenance_margin=900.0, slippage_ticks=0.0,
    roll_months=cx.QUARTERLY, roll_offset_days=1)


def weekdays(start: date, n: int) -> list:
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def make_market(spec, series_prices, dates, expiries=None):
    """series_prices: list of (year, month, {date_index: price})."""
    contracts = []
    for n, (y, m, prices) in enumerate(series_prices):
        bars = {dates[i]: datamod.Bar(dates[i], p, p, p, p, 1000 + n, 1000)
                for i, p in prices.items()}
        exp = (expiries or {}).get((y, m))
        contracts.append(datamod.ContractSeries(spec.symbol, y, m, bars, expiry=exp))
    return datamod.MarketData(spec=spec, contracts=contracts)


def two_contract_market(spec=TEST_SPEC):
    """C1 runs d0..d5 at 100..105; C2 runs d3..d8 at 110..115.

    With roll_offset_days=1 the roll lands on d4 (one trading day before C1's
    last quote), where C1 = 104 and C2 = 111, a gap of +7.
    """
    ds = weekdays(date(2026, 1, 5), 9)
    c1 = {i: 100.0 + i for i in range(6)}                 # d0..d5 -> 100..105
    c2 = {i: 110.0 + (i - 3) for i in range(3, 9)}        # d3..d8 -> 110..115
    return make_market(spec, [(2026, 3, c1), (2026, 6, c2)], ds), ds


def flat_config(**kw):
    base = dict(initial_equity=100_000.0, rebalance=engine.DAILY, execution_lag=1,
                min_history=1, buffer_frac=0.0, roll_offset_days=1,
                rates=datamod.constant_rate(0.0, haircut=0.0))
    base.update(kw)
    return engine.BacktestConfig(**base)


# --- contract specs ---------------------------------------------------------

def test_tick_value_and_costs():
    mes = cx.get("MES")
    assert_close("MES tick value = multiplier x tick size", 1.25, mes.tick_value)
    assert_close("MES one-way cost = commission + 1 tick",
                 mes.commission + 1.25, mes.cost_per_contract())
    assert_close("MES cost with 2 ticks slippage",
                 mes.commission + 2.5, mes.cost_per_contract(slippage_ticks=2.0))
    assert_eq("contract code", "MESH26", cx.contract_code("MES", 2026, 3))
    assert_close("price snaps to the tick grid", 5900.25, mes.round_price(5900.3))
    assert_raises("unknown symbol raises", KeyError, cx.get, "NOPE")


def test_yield_contract_uses_absolute_vol_basis():
    assert_eq("10Y vol basis", "abs", cx.get("10Y").vol_basis)
    assert_eq("MES vol basis", "pct", cx.get("MES").vol_basis)


# --- rolls ------------------------------------------------------------------

def test_roll_schedule_is_contiguous():
    market, ds = two_contract_market()
    segs = rollmod.roll_schedule(market)
    assert_eq("two segments", 2, len(segs))
    assert_eq("first segment ends on the roll date", ds[4], segs[0].end)
    assert_eq("second segment starts the next day", ds[5], segs[1].start)
    held = rollmod.held_contract(segs)
    assert_eq("held contract before roll", "TSTH26", held[ds[4]].code)
    assert_eq("held contract after roll", "TSTM26", held[ds[5]].code)
    assert_true("no day is held twice", len(held) == len(set(held)))


def test_panama_removes_the_roll_gap():
    market, ds = two_contract_market()
    segs = rollmod.roll_schedule(market)
    adj = rollmod.continuous(segs, rollmod.PANAMA)
    assert_close("panama: newest segment is unadjusted", 115.0, adj[ds[8]])
    assert_close("panama: history shifted by the +7 gap", 107.0, adj[ds[0]])
    diffs = [adj[b] - adj[a] for a, b in zip(ds, ds[1:])]
    assert_true("panama: every daily step is +1, roll day included",
                all(abs(x - 1.0) < EPS for x in diffs), f"{diffs}")


def test_ratio_adjustment_preserves_returns():
    market, ds = two_contract_market()
    segs = rollmod.roll_schedule(market)
    adj = rollmod.continuous(segs, rollmod.RATIO)
    r_roll = adj[ds[5]] / adj[ds[4]] - 1.0
    assert_close("ratio: roll-day return is the new contract's own return",
                 112.0 / 111.0 - 1.0, r_roll)
    assert_close("ratio: last price is the real price", 115.0, adj[ds[8]])


def test_unadjusted_keeps_the_jump():
    market, ds = two_contract_market()
    segs = rollmod.roll_schedule(market)
    raw = rollmod.continuous(segs, rollmod.UNADJUSTED)
    assert_close("unadjusted: roll day shows the fictional +7 jump",
                 8.0, raw[ds[5]] - raw[ds[4]])
    assert_true("unadjusted levels are real prices", raw[ds[0]] == 100.0)


def test_roll_gap_report():
    market, ds = two_contract_market()
    rows = rollmod.roll_gaps(rollmod.roll_schedule(market))
    assert_eq("one roll reported", 1, len(rows))
    assert_close("gap = new close - old close on the roll date", 7.0, rows[0]["gap"])
    assert_eq("roll date", ds[4], rows[0]["date"])


def test_volume_roll_never_later_than_calendar():
    market = syn.synthetic_market(cx.get("MES"), date(2020, 1, 1), date(2023, 12, 29),
                                  seed=3)
    cal = rollmod.roll_schedule(market, method=rollmod.CALENDAR)
    vol = rollmod.roll_schedule(market, method=rollmod.VOLUME)
    cal_dates = {s.code: s.end for s in cal}
    late = [c for c, d in {s.code: s.end for s in vol}.items()
            if c in cal_dates and d > cal_dates[c]]
    assert_true("volume roll never rolls later than the calendar rule", not late,
                f"late: {late}")
    assert_true("volume roll does move at least one roll earlier",
                any({s.code: s.end for s in vol}[c] < cal_dates[c]
                    for c in cal_dates if c in {s.code: s.end for s in vol}))


def test_unknown_methods_rejected():
    market, _ = two_contract_market()
    assert_raises("bad roll method", ValueError, rollmod.roll_schedule, market,
                  method="psychic")
    assert_raises("bad adjustment", ValueError, rollmod.continuous,
                  rollmod.roll_schedule(market), "vibes")


# --- engine accounting ------------------------------------------------------

def test_pnl_equals_adjusted_move_times_multiplier():
    """The invariant the whole design exists to satisfy.

    Holding one contract and rolling it must earn exactly
    multiplier x (adjusted price change), with no roll gap leaking into P&L.
    """
    market, ds = two_contract_market()
    cfg = flat_config(fixed_contracts={"TST": 1})
    res = engine.run({"TST": market}, cfg, st.Constant(1.0))
    entry = res.trades[0]
    assert_eq("entered on the first day after the signal date", ds[1], entry.date)
    assert_eq("entered one contract", 1, entry.contracts)
    adj = rollmod.continuous(rollmod.roll_schedule(market, offset_days=1))
    expected = TEST_SPEC.multiplier * (adj[ds[8]] - adj[ds[1]])
    assert_close("P&L = multiplier x adjusted move", expected,
                 res.final_equity - cfg.initial_equity, tol=1e-6)
    assert_close("attributed P&L matches", expected, res.pnl_by_market["TST"], tol=1e-6)
    raw = rollmod.continuous(rollmod.roll_schedule(market, offset_days=1),
                             rollmod.UNADJUSTED)
    naive = TEST_SPEC.multiplier * (raw[ds[8]] - raw[ds[1]])
    assert_close("the naive unadjusted stitch would have over-counted by the gap",
                 expected + TEST_SPEC.multiplier * 7.0, naive)
    assert_true("engine did not book the roll gap as profit",
                abs((res.final_equity - cfg.initial_equity) - naive) > 1.0)


def test_roll_is_a_real_trade_with_real_costs():
    spec = cx.ContractSpec(**{**TEST_SPEC.__dict__, "commission": 1.0,
                              "slippage_ticks": 2.0})   # 1.0 + 2 x (10 x 0.01) = 1.20
    market, ds = two_contract_market(spec)
    cfg = flat_config(fixed_contracts={"TST": 1})
    res = engine.run({"TST": market}, cfg, st.Constant(1.0))
    per = spec.cost_per_contract()
    assert_close("cost per contract", 1.20, per)
    assert_eq("three fills: entry + two roll legs", 3, len(res.trades))
    assert_eq("roll legs are labelled", 2,
              sum(1 for t in res.trades if t.reason == "roll"))
    assert_close("total cost = 3 fills", 3 * per, res.total_costs())
    adj = rollmod.continuous(rollmod.roll_schedule(market, offset_days=1))
    gross = spec.multiplier * (adj[ds[8]] - adj[ds[1]])
    assert_close("equity = gross P&L - costs", gross - 3 * per,
                 res.final_equity - cfg.initial_equity, tol=1e-6)


def test_roll_legs_price_both_contracts():
    market, _ = two_contract_market()
    res = engine.run({"TST": market}, flat_config(fixed_contracts={"TST": 1}),
                     st.Constant(1.0))
    legs = [t for t in res.trades if t.reason == "roll"]
    assert_close("sold the old contract at its own close", 104.0, legs[0].price)
    assert_eq("sold the front month", "TSTH26", legs[0].code)
    assert_close("bought the new contract at its own close", 111.0, legs[1].price)
    assert_eq("bought the back month", "TSTM26", legs[1].code)
    assert_eq("net position unchanged across the roll", 0,
              legs[0].contracts + legs[1].contracts)


def test_short_position_pnl_sign():
    market, ds = two_contract_market()
    res = engine.run({"TST": market}, flat_config(fixed_contracts={"TST": 1}),
                     st.Constant(-1.0))
    adj = rollmod.continuous(rollmod.roll_schedule(market, offset_days=1))
    expected = -TEST_SPEC.multiplier * (adj[ds[8]] - adj[ds[1]])
    assert_close("short earns the negative of the move", expected,
                 res.final_equity - 100_000.0, tol=1e-6)


def test_collateral_interest_compounds_on_a_flat_book():
    market, _ = two_contract_market()
    rate = datamod.constant_rate(0.04, haircut=0.0)
    cfg = flat_config(rates=rate, fixed_contracts={"TST": 0})
    res = engine.run({"TST": market}, cfg, st.Constant(0.0))
    daily = (1.04) ** (1 / 252) - 1
    expected = 100_000.0 * (1 + daily) ** len(res.records)
    assert_eq("no trades on a flat book", 0, len(res.trades))
    assert_close("equity compounds at the collateral rate", expected,
                 res.final_equity, tol=1e-6)
    assert_true("interest is reported", res.records[-1].interest > 0)


def test_rate_haircut_is_applied():
    r = datamod.RateSeries(default=0.05, haircut=0.005)
    assert_close("broker spread comes off the bill rate", 0.045, r.annual(date(2026, 1, 1)))
    floor = datamod.RateSeries(default=0.002, haircut=0.005)
    assert_close("rate floors at zero, never negative", 0.0,
                 floor.annual(date(2026, 1, 1)))


def test_no_lookahead_in_signals():
    """The strategy must never be handed the bar it is about to trade on."""
    market, ds = two_contract_market()
    adj = rollmod.continuous(rollmod.roll_schedule(market, offset_days=1))
    seen = []

    class Spy:
        min_history = 1
        label = "spy"

        def __call__(self, values):
            seen.append(values[-1] if values else None)
            return 1.0

    cfg = flat_config(fixed_contracts={"TST": 1})
    engine.run({"TST": market}, cfg, Spy())
    # rebalance happens every day from index 1; the value seen on day i must be
    # the adjusted close of day i-1.
    expected = [adj[d] for d in ds[:-1]]
    assert_eq("one signal call per tradable day", len(expected), len(seen))
    assert_eq("signal sees only the prior close", expected, seen)


def test_execution_lag_zero_uses_same_bar():
    market, ds = two_contract_market()
    adj = rollmod.continuous(rollmod.roll_schedule(market, offset_days=1))
    seen = []

    class Spy:
        min_history = 1
        label = "spy"

        def __call__(self, values):
            seen.append(values[-1])
            return 1.0

    engine.run({"TST": market}, flat_config(execution_lag=0,
                                            fixed_contracts={"TST": 1}), Spy())
    assert_eq("lag 0 sees today's close (opt in knowingly)", adj[ds[0]], seen[0])


def test_positions_are_always_whole_contracts():
    book = syn.synthetic_book(("MES", "MGC"), date(2015, 1, 2), date(2020, 12, 31))
    res = engine.run(book, engine.BacktestConfig(initial_equity=250_000),
                     st.TimeSeriesMomentum())
    bad = [(r.date, r.positions) for r in res.records
           if any(not isinstance(q, int) for q in r.positions.values())]
    assert_true("every position is an integer number of contracts", not bad)
    assert_true("fills are integers",
                all(isinstance(t.contracts, int) for t in res.trades))


def test_margin_ceiling_is_never_breached():
    book = syn.synthetic_book(("MES", "MGC", "MCL"), date(2016, 1, 4), date(2020, 12, 31))
    cfg = engine.BacktestConfig(initial_equity=100_000, vol_target=3.0,
                                max_margin_to_equity=0.25)
    res = engine.run(book, cfg, st.TimeSeriesMomentum())
    breaches = [(r.date, r.margin_to_equity) for r in res.records
                if r.equity > 0 and r.margin_to_equity > 0.25 + 1e-9]
    assert_true("margin/equity respects the cap on every day", not breaches,
                f"{breaches[:3]}")
    assert_true("an absurd vol target actually binds the cap",
                res.capped_days > 0 or res.derisk_days > 0)


def test_blow_up_liquidates_and_stops():
    """A gap larger than equity must end the run, not print a negative curve."""
    spec = cx.ContractSpec("CRSH", "Crash Test", "equity", "TEST", "USD",
                           multiplier=1.0, tick_size=0.01, commission=0.0,
                           initial_margin=100.0, maintenance_margin=90.0,
                           slippage_ticks=0.0, roll_months=cx.QUARTERLY,
                           roll_offset_days=1)
    ds = weekdays(date(2026, 1, 5), 6)
    prices = {0: 1000.0, 1: 1000.0, 2: 1000.0, 3: 1000.0, 4: 100.0, 5: 100.0}
    market = make_market(spec, [(2026, 3, prices)], ds)
    cfg = flat_config(initial_equity=10_000.0, fixed_contracts={"CRSH": 25},
                      max_margin_to_equity=0.25)
    res = engine.run({"CRSH": market}, cfg, st.Constant(1.0))
    assert_true("run is flagged as blown up", res.blown_up)
    assert_true("everything is liquidated", all(q == 0 for q in res.records[-1].positions.values()))
    assert_true("run stops on the day of ruin", res.records[-1].date == ds[4])
    assert_true("a warning explains it", any("equity hit zero" in w for w in res.warnings))


def test_buffer_suppresses_churn():
    book = syn.synthetic_book(("MES", "MGC", "M6E"), date(2014, 1, 2), date(2019, 12, 31))
    cfg_a = engine.BacktestConfig(initial_equity=500_000, buffer_frac=0.0)
    cfg_b = engine.BacktestConfig(initial_equity=500_000, buffer_frac=0.20)
    traded_a = sum(engine.run(book, cfg_a, st.TimeSeriesMomentum()).contracts_traded.values())
    traded_b = sum(engine.run(book, cfg_b, st.TimeSeriesMomentum()).contracts_traded.values())
    assert_true("a no-trade band cuts contracts traded", traded_b < traded_a,
                f"{traded_b} !< {traded_a}")


def test_run_is_deterministic():
    a = syn.synthetic_book(("MES", "MGC"), date(2016, 1, 4), date(2020, 12, 31), seed=42)
    b = syn.synthetic_book(("MES", "MGC"), date(2016, 1, 4), date(2020, 12, 31), seed=42)
    cfg = engine.BacktestConfig(initial_equity=300_000)
    ra = engine.run(a, cfg, st.TimeSeriesMomentum())
    rb = engine.run(b, cfg, st.TimeSeriesMomentum())
    assert_eq("same seed, same equity curve", ra.equity_curve, rb.equity_curve)


# --- sizing -----------------------------------------------------------------

def test_vol_target_is_approximately_hit_when_capital_allows():
    book = syn.synthetic_book(("MES", "MGC", "MCL", "M6E"), date(2012, 1, 3),
                              date(2020, 12, 31))
    cfg = engine.BacktestConfig(initial_equity=5_000_000, vol_target=0.10,
                                rates=datamod.constant_rate(0.0, haircut=0.0))
    res = engine.run(book, cfg, st.TimeSeriesMomentum())
    realised = mt.ann_vol(res.returns)
    assert_true("realised vol lands near the target when rounding is not binding",
                0.06 <= realised <= 0.16, f"realised {realised:.3f}")


def test_small_account_undershoots_the_vol_target():
    """The rounding problem, made visible instead of hidden."""
    book = syn.synthetic_book(("MES", "MGC", "MCL", "M6E"), date(2012, 1, 3),
                              date(2020, 12, 31))
    small = engine.run(book, engine.BacktestConfig(initial_equity=50_000),
                       st.TimeSeriesMomentum())
    big = engine.run(book, engine.BacktestConfig(initial_equity=5_000_000),
                     st.TimeSeriesMomentum())
    assert_true("a small account cannot express the risk target",
                mt.ann_vol(small.returns) < mt.ann_vol(big.returns))
    small_eff = mt.mean([r.effective_markets for r in small.records])
    big_eff = mt.mean([r.effective_markets for r in big.records])
    assert_true("and holds fewer markets in effect", small_eff < big_eff,
                f"{small_eff:.2f} !< {big_eff:.2f}")


def test_risk_per_contract_by_basis():
    mes = cx.get("MES")
    assert_close("percent basis scales by price x multiplier",
                 0.17 * 5900 * 5, sz.risk_per_contract(mes, 5900, 0.17))
    ten = cx.get("10Y")
    assert_close("absolute basis ignores the price level",
                 0.6 * 1000, sz.risk_per_contract(ten, 4.25, 0.6))


def test_percent_vol_uses_the_unadjusted_price_as_base():
    """A back-adjusted series' level is fictional; its differences are not."""
    adj = [100.0 + i for i in range(60)]        # +1 per day, level drifts
    raw = [1000.0] * 60                        # the tradable price, constant
    v_base = sz.ewma_vol(adj, span=10, basis="pct", base=raw)
    v_self = sz.ewma_vol(adj, span=10, basis="pct")
    assert_close("percent vol against the real price is exact",
                 (1.0 / 1000.0) * math.sqrt(252), v_base, tol=1e-12)
    assert_true("using the fictional adjusted level instead gives a different answer",
                abs(v_self - v_base) > 1e-6, f"{v_self} vs {v_base}")
    negative = [10.0 - 0.5 * i for i in range(60)]     # crosses zero, as crude does
    ok = sz.ewma_vol(negative, span=10, basis="pct", base=[100.0] * 60)
    assert_true("vol is finite even when the adjusted level goes negative",
                ok is not None and ok == ok and ok > 0)


def test_ewma_vol_on_a_known_series():
    vals = [100.0]
    for i in range(300):
        vals.append(vals[-1] * (1.01 if i % 2 == 0 else 1 / 1.01))
    v = sz.ewma_vol(vals, span=20, basis="pct")
    per_day = abs(vals[2] / vals[1] - 1.0)
    assert_true("EWMA vol of an alternating series ~ step x sqrt(252)",
                abs(v - per_day * math.sqrt(252)) < 0.02, f"{v}")
    assert_true("too little history returns None", sz.ewma_vol([1.0, 2.0]) is None)


def test_buffered_target_band():
    assert_eq("inside the band: no trade", 3, sz.buffered_target(3, 3.3, 10.0, 0.10))
    assert_eq("above the band: sell to the edge", 4, sz.buffered_target(9, 3.3, 10.0, 0.10))
    assert_eq("below the band: buy to the edge", 2, sz.buffered_target(0, 3.3, 10.0, 0.10))
    assert_eq("no buffer: round to target", 3, sz.buffered_target(0, 3.3, 10.0, 0.0))


def test_margin_scaling_keeps_book_shape():
    specs = {"MES": cx.get("MES"), "MGC": cx.get("MGC")}
    prices = {"MES": 5900.0, "MGC": 3350.0}
    pos = {"MES": 20, "MGC": 10}
    out, scaled = sz.scale_to_margin_cap(pos, prices, specs, 100_000, 0.25)
    assert_true("scaling happened", scaled)
    assert_true("margin now under the cap",
                sz.margin_required(out, prices, specs) <= 25_000 + EPS)
    assert_true("both markets kept (proportional, not sequential)",
                out["MES"] > 0 and out["MGC"] > 0)
    assert_true("shorts stay short",
                sz.scale_to_margin_cap({"MES": -20}, prices, specs, 10_000, 0.25)[0]["MES"] <= 0)


def test_idm_and_effective_markets():
    assert_close("IDM of one market is one", 1.0, sz.idm_for(1))
    assert_true("IDM rises with market count", sz.idm_for(8) > sz.idm_for(4))
    assert_true("IDM is capped", sz.idm_for(100, 0.0, cap=2.5) == 2.5)
    even = sz.diversification({"a": 1, "b": 1, "c": 1, "d": 1},
                              {"a": 1.0, "b": 1.0, "c": 1.0, "d": 1.0})
    assert_close("four equal risks = four effective markets", 4.0, even.effective, 1e-6)
    lopsided = sz.diversification({"a": 100, "b": 1}, {"a": 1.0, "b": 1.0})
    assert_true("one dominant market collapses the effective count",
                lopsided.effective < 1.2, f"{lopsided.effective}")
    zeroed = sz.diversification({"a": 1, "b": 0}, {"a": 1.0, "b": 1.0})
    assert_eq("markets rounded to zero are named", ("b",), zeroed.zeroed)


def test_min_equity_for_one_contract():
    mes = cx.get("MES")
    need = sz.min_equity_for_one(mes, 5900, 0.17, weight=1 / 8, vol_target=0.10,
                                 idm=sz.idm_for(8))
    got = sz.position_scale(need, mes, 5900, 0.17, 1 / 8, 0.10, sz.idm_for(8))
    assert_close("at min equity the full position is exactly one contract", 1.0, got)


# --- data layer -------------------------------------------------------------

def test_contract_csv_round_trip():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "MESH26.csv"
        p.write_text("date,open,high,low,close,volume,open_interest\n"
                     "2026-01-02,5901.25,5930,5895.5,5925.75,182340,1204553\n"
                     "2026-01-05,5925.75,5950,5920,5940.00,171002,1210441\n")
        cs = datamod.load_contract_csv(p)
        assert_eq("symbol parsed from filename", "MES", cs.symbol)
        assert_eq("delivery month parsed", (2026, 3), cs.delivery)
        assert_eq("code round-trips", "MESH26", cs.code)
        assert_close("close read", 5940.0, cs.close(date(2026, 1, 5)))
        assert_eq("expiry falls back to the last quote", date(2026, 1, 5),
                  cs.expiry_date())
        junk = Path(tmp) / "whatever.csv"
        junk.write_text("date,close\n2026-01-02,1.0\n")
        assert_raises("a filename with no delivery month is rejected", ValueError,
                      datamod.load_contract_csv, junk)
        assert_raises("an impossible delivery month is rejected", ValueError,
                      datamod.load_contract_csv, p, symbol="MES", year=2026, month=13)


def test_load_market_requires_files():
    with tempfile.TemporaryDirectory() as tmp:
        assert_raises("missing contract files raise", FileNotFoundError,
                      datamod.load_market, tmp, cx.get("MES"))


def test_continuous_mode_wrapper_runs():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "MES_continuous.csv"
        ds = weekdays(date(2020, 1, 6), 400)
        lines = ["date,close"] + [f"{d},{100 + i * 0.1:.2f}" for i, d in enumerate(ds)]
        p.write_text("\n".join(lines) + "\n")
        md = datamod.load_continuous(p, cx.get("MES"), rolls_per_year=4)
        assert_true("segments created", len(md.contracts) >= 4)
        segs = rollmod.roll_schedule(md, offset_days=0)
        adj = rollmod.continuous(segs)
        assert_close("a pre-adjusted file has zero roll gaps",
                     0.0, sum(abs(r["gap"]) for r in rollmod.roll_gaps(segs)
                              if r["gap"] is not None), tol=1e-6)
        assert_eq("adjusted series covers the file", len(ds), len(adj))


def test_rates_from_csv():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "irx.csv"
        p.write_text("date,close\n2026-01-02,4.25\n2026-02-02,4.00\n")
        r = datamod.load_rates(p, haircut=0.0)
        assert_close("percent quotes become decimals", 0.0425, r.annual(date(2026, 1, 2)))
        assert_close("values carry forward", 0.0425, r.annual(date(2026, 1, 20)))
        assert_close("and update", 0.04, r.annual(date(2026, 3, 1)))


# --- strategies -------------------------------------------------------------

def test_signals_are_bounded_and_lagged_safe():
    rising = [100.0 + i for i in range(400)]
    falling = [500.0 - i for i in range(400)]
    for name in ("tsm", "ma", "multi", "volmom", "breakout"):
        s = st.build(name)
        up, down = s(rising), s(falling)
        assert_true(f"{s.label}: long in an uptrend", up is not None and up > 0)
        assert_true(f"{s.label}: short in a downtrend", down is not None and down < 0)
        assert_true(f"{s.label}: bounded to [-1, 1]", -1.0 <= up <= 1.0 and -1.0 <= down <= 1.0)
        assert_true(f"{s.label}: stands aside without history", s(rising[:5]) is None)


def test_long_only_variant_never_shorts():
    falling = [500.0 - i for i in range(400)]
    for s in (st.TimeSeriesMomentum(allow_short=False),
              st.MovingAverageCross(allow_short=False),
              st.MultiSpeedMomentum(allow_short=False),
              st.Breakout(allow_short=False)):
        assert_eq(f"{s.label}: flat instead of short", 0.0, s(falling))


def test_scaled_signal_survives_a_negative_adjusted_level():
    series = [50.0 - 0.3 * i for i in range(400)]      # crosses zero like crude
    v = st.VolAdjustedMomentum()(series)
    assert_true("scaled momentum is finite below zero", v is not None and v == v)
    assert_true("and points short", v < 0)


# --- metrics ----------------------------------------------------------------

def test_return_statistics():
    r = [0.001] * 252
    assert_close("CAGR of 0.1%/day", (1.001 ** 252) - 1, mt.cagr(r), tol=1e-9)
    assert_close("zero vol on a constant series", 0.0, mt.ann_vol(r), tol=1e-12)
    eq = mt.equity_from_returns([0.1, -0.5, 0.2])
    assert_close("max drawdown", -0.5, mt.max_drawdown(eq), tol=1e-12)
    d = mt.drawdown_detail(mt.equity_from_returns([0.1, -0.5, 0.2]))
    assert_true("unrecovered drawdown is reported as such", not d["recovered"])


def test_sharpe_subtracts_the_cash_leg():
    r = [0.0004] * 300
    raw = mt.sharpe(r, 0.0)
    net = mt.sharpe(r, 0.0002)
    assert_true("a constant series has undefined Sharpe", raw != raw and net != net)
    noisy = [0.001 if i % 2 else -0.0002 for i in range(400)]
    assert_true("subtracting the risk-free rate lowers Sharpe",
                mt.sharpe(noisy, 0.0002) < mt.sharpe(noisy, 0.0))


def test_deflated_sharpe_penalises_more_trials():
    monthly = [0.02, 0.01, -0.01, 0.03, 0.005, 0.015, -0.02, 0.018, 0.004,
               0.009, 0.011, -0.003, 0.02, 0.006, -0.008, 0.012, 0.004, 0.01,
               0.015, -0.005, 0.008, 0.013, 0.002, 0.009]
    few = mt.deflated_sharpe(monthly, n_trials=2, sharpe_variance=0.02)
    many = mt.deflated_sharpe(monthly, n_trials=200, sharpe_variance=0.02)
    assert_true("more trials -> lower probability of real skill",
                many["dsr"] < few["dsr"], f"{many['dsr']} !< {few['dsr']}")
    assert_true("threshold rises with the size of the search",
                many["threshold"] > few["threshold"])
    assert_true("short samples return nan, not a number",
                mt.deflated_sharpe([0.01, 0.02], 10, 0.02)["dsr"] != 
                mt.deflated_sharpe([0.01, 0.02], 10, 0.02)["dsr"])


def test_summary_reports_futures_mechanics():
    book = syn.synthetic_book(("MES", "MGC"), date(2016, 1, 4), date(2020, 12, 31))
    res = engine.run(book, engine.BacktestConfig(initial_equity=500_000),
                     st.TimeSeriesMomentum())
    s = mt.summary(res, name="t")
    for key in ("cost_drag", "roll_costs", "avg_margin_to_equity", "interest_earned",
                "effective_markets", "vol_realised_ratio", "turnover_x_equity"):
        assert_true(f"summary reports {key}", key in s and s[key] == s[key])
    assert_close("roll + signal costs reconcile to the total",
                 s["costs"], s["roll_costs"] + s["signal_costs"]
                 + res.costs_by_reason.get("margin", 0.0)
                 + res.costs_by_reason.get("liquidation", 0.0), tol=1e-6)


# --- config guards ----------------------------------------------------------

def test_config_validation():
    assert_raises("bad rebalance rejected", ValueError,
                  engine.BacktestConfig, rebalance="hourly")
    assert_raises("negative lag rejected", ValueError,
                  engine.BacktestConfig, execution_lag=-1)
    assert_raises("zero equity rejected", ValueError,
                  engine.BacktestConfig, initial_equity=0)
    assert_raises("empty universe rejected", ValueError,
                  engine.run, {}, engine.BacktestConfig(), st.Constant(1.0))


def main():
    test_tick_value_and_costs()
    test_yield_contract_uses_absolute_vol_basis()
    test_roll_schedule_is_contiguous()
    test_panama_removes_the_roll_gap()
    test_ratio_adjustment_preserves_returns()
    test_unadjusted_keeps_the_jump()
    test_roll_gap_report()
    test_volume_roll_never_later_than_calendar()
    test_unknown_methods_rejected()
    test_pnl_equals_adjusted_move_times_multiplier()
    test_roll_is_a_real_trade_with_real_costs()
    test_roll_legs_price_both_contracts()
    test_short_position_pnl_sign()
    test_collateral_interest_compounds_on_a_flat_book()
    test_rate_haircut_is_applied()
    test_no_lookahead_in_signals()
    test_execution_lag_zero_uses_same_bar()
    test_positions_are_always_whole_contracts()
    test_margin_ceiling_is_never_breached()
    test_blow_up_liquidates_and_stops()
    test_buffer_suppresses_churn()
    test_run_is_deterministic()
    test_vol_target_is_approximately_hit_when_capital_allows()
    test_small_account_undershoots_the_vol_target()
    test_risk_per_contract_by_basis()
    test_percent_vol_uses_the_unadjusted_price_as_base()
    test_ewma_vol_on_a_known_series()
    test_buffered_target_band()
    test_margin_scaling_keeps_book_shape()
    test_idm_and_effective_markets()
    test_min_equity_for_one_contract()
    test_contract_csv_round_trip()
    test_load_market_requires_files()
    test_continuous_mode_wrapper_runs()
    test_rates_from_csv()
    test_signals_are_bounded_and_lagged_safe()
    test_long_only_variant_never_shorts()
    test_scaled_signal_survives_a_negative_adjusted_level()
    test_return_statistics()
    test_sharpe_subtracts_the_cash_leg()
    test_deflated_sharpe_penalises_more_trials()
    test_summary_reports_futures_mechanics()
    test_config_validation()
    print("\nAll futures-engine tests passed.")


if __name__ == "__main__":
    main()
