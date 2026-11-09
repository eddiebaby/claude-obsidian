#!/usr/bin/env python3
"""Hermetic tests for propsim. Stdlib unittest + numpy, no network.

Usage (from prop-eval-sim/):
  python3 -m unittest discover -s tests -v
"""
import math
import os
import sys
import tempfile
import unittest
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from propsim import (  # noqa: E402
    Controls,
    EvalRules,
    FirmRules,
    FundedRules,
    PhaseRules,
    compress,
    eod_only,
    load_daily_csv,
    open_account,
    play_day,
    run_eval,
    run_funded,
    simulate,
    synthetic_days,
)
from propsim.paths import stationary_bootstrap_indices  # noqa: E402


# --------------------------------------------------------------------------
# Reference: naive bar-by-bar day, written independently of the engine
# --------------------------------------------------------------------------

def reference_day(state, path, size, phase, ctl):
    """state = dict(start, balance, peak, floor). Returns (pnl, status), mutates state."""
    lock = math.inf if phase.lock_floor_offset is None else state["start"] + phase.lock_floor_offset

    def raise_floor():
        if phase.drawdown_mode != "static":
            state["floor"] = max(state["floor"], min(state["peak"] - phase.max_loss, lock))

    intraday = phase.drawdown_mode == "intraday_trailing"
    touch = phase.breach_on_intraday_touch or intraday
    b0 = state["balance"]
    lo = -ctl.daily_stop if ctl.daily_stop is not None else -math.inf
    fail_lvl = -math.inf
    if phase.daily_loss_limit is not None:
        if phase.dll_action == "flatten":
            lo = max(lo, -phase.daily_loss_limit)
        else:
            fail_lvl = -phase.daily_loss_limit
    hi = ctl.daily_profit_cap if ctl.daily_profit_cap is not None else math.inf

    pnl = None
    for v in [0.0] + [x * size for x in path]:
        if v >= hi:
            pnl = hi
            if intraday and b0 + hi > state["peak"]:
                state["peak"] = b0 + hi
                raise_floor()
            break
        if intraday and b0 + v > state["peak"]:
            state["peak"] = b0 + v
            raise_floor()
        # crossing order between bars is unknowable; when one bar crosses several
        # levels, the highest level is the one crossed first
        hits = []
        if touch and b0 + v <= state["floor"]:
            hits.append((state["floor"] - b0, 3, "breach"))
        if v <= fail_lvl:
            hits.append((fail_lvl, 2, "dll_fail"))
        if v <= lo:
            hits.append((lo, 1, "stop"))
        if hits:
            lvl, _, ev = max(hits)
            if ev != "stop":
                return lvl, ev
            pnl, status = lo - ctl.stop_slippage * size, "stop"
            break
    else:
        status = "ok"
    if pnl is None:
        pnl = path[-1] * size if len(path) else 0.0
    elif v >= hi:
        status = "cap"
    bal = b0 + pnl
    if bal <= state["floor"]:
        return pnl, "breach"
    state["balance"] = bal
    if bal > state["peak"]:
        state["peak"] = bal
        raise_floor()
    return pnl, status


class TestCompression(unittest.TestCase):
    def test_records_and_segment_mins(self):
        d = compress([1, -2, 3, 2, 5, -4, 0])
        # path with open: 0,1,-2,3,2,5,-4,0 -> records 0,1,3,5
        self.assertEqual(d.segments, ((0.0, 0.0), (1.0, -2.0), (3.0, 2.0), (5.0, -4.0)))
        self.assertEqual(d.close, 0.0)
        self.assertTrue(d.traded)

    def test_flat_day(self):
        d = compress([0.0])
        self.assertFalse(d.traded)
        self.assertEqual(d.close, 0.0)

    def test_engine_matches_bar_by_bar_reference(self):
        rng = np.random.default_rng(7)
        modes = ["eod_trailing", "intraday_trailing", "static"]
        n_checked = 0
        seen = set()
        statuses = set()
        for trial in range(3000):
            pick = lambda xs: xs[int(rng.integers(len(xs)))]  # noqa: E731
            combo = (
                pick(modes),
                pick([None, 0.0, 100.0]),
                pick([True, False]),
                pick([None, 400.0]),
                pick(["flatten", "fail"]),
                pick([None, 250.0, 600.0]),
                pick([None, 300.0, 900.0]),
                pick([0.0, 5.0]),
            )
            seen.add(combo)
            mode, lock, touch, dll, dll_action, stop, cap, slip = combo
            phase = PhaseRules(
                max_loss=float(rng.choice([300, 800, 2000])),
                drawdown_mode=mode,
                lock_floor_offset=lock,
                breach_on_intraday_touch=touch,
                daily_loss_limit=dll,
                dll_action=dll_action,
            )
            ctl = Controls(daily_stop=stop, daily_profit_cap=cap, stop_slippage=slip)
            size = float(rng.choice([1, 2, 3]))
            acct = open_account(50_000.0, phase)
            ref = dict(start=acct.start, balance=acct.balance, peak=acct.peak, floor=acct.floor)
            for _ in range(15):
                path = list(np.cumsum(rng.normal(0, 60, size=int(rng.integers(1, 40)))))
                day = compress(path)
                got = play_day(acct, day, size, phase, ctl)
                exp = reference_day(ref, path, size, phase, ctl)
                self.assertAlmostEqual(got[0], exp[0], places=6, msg=f"trial {trial} {combo}")
                self.assertEqual(got[1], exp[1], msg=f"trial {trial} {combo}")
                statuses.add(got[1])
                n_checked += 1
                if got[1] in ("breach", "dll_fail"):
                    break
                self.assertAlmostEqual(acct.balance, ref["balance"], places=6)
                self.assertAlmostEqual(acct.peak, ref["peak"], places=6)
                self.assertAlmostEqual(acct.floor, ref["floor"], places=6)
        self.assertGreater(n_checked, 10000)
        self.assertGreater(len(seen), 600)  # of 864 parameter combinations
        self.assertEqual(statuses, {"ok", "stop", "cap", "breach", "dll_fail"})


def _eval_firm(mode="static", target=3000.0, max_loss=2000.0, lock=None, consistency=None, fee=100.0, period=None):
    return FirmRules(
        name="test",
        start_balance=50_000.0,
        eval=EvalRules(
            profit_target=target,
            phase=PhaseRules(max_loss=max_loss, drawdown_mode=mode, lock_floor_offset=lock),
            consistency_max_day_frac=consistency,
            fee=fee,
            fee_period_days=period,
        ),
        funded=FundedRules(
            phase=PhaseRules(max_loss=max_loss, drawdown_mode="eod_trailing", lock_floor_offset=0.0),
            profit_split=0.9,
            payout_min_days=5,
            payout_day_min_profit=150.0,
            payout_min=500.0,
            payout_frac_of_profit=0.5,
        ),
    )


class TestEval(unittest.TestCase):
    def test_gamblers_ruin_driftless(self):
        """Static barrier, zero drift: P(hit +T before -D) ~= D / (D + T)."""
        bank = synthetic_days(5000, 0.0, 300.0, bars=40, seed=1)
        firm = _eval_firm(mode="static")
        s = simulate(bank, firm, 1, sims=1500, seed=2, horizon_days=2000, max_attempts=1, block=1.0)
        self.assertAlmostEqual(s.pass_rate, 2000 / 5000, delta=0.05)

    def test_intraday_trailing_never_easier_than_eod(self):
        bank = synthetic_days(2000, 0.0, 400.0, bars=60, seed=3)
        eod = simulate(bank, _eval_firm(mode="eod_trailing", lock=0.0), 1, sims=800, seed=4, max_attempts=1)
        intr = simulate(bank, _eval_firm(mode="intraday_trailing", lock=0.0), 1, sims=800, seed=4, max_attempts=1)
        self.assertLess(intr.pass_rate, eod.pass_rate)

    def test_eod_only_data_is_optimistic(self):
        bank = synthetic_days(2000, 0.0, 400.0, bars=60, seed=5)
        firm = _eval_firm(mode="eod_trailing", lock=0.0)
        full = simulate(bank, firm, 1, sims=800, seed=6, max_attempts=1)
        eod = simulate(eod_only(bank), firm, 1, sims=800, seed=6, max_attempts=1)
        self.assertGreater(eod.pass_rate, full.pass_rate)

    def test_consistency_rule_delays_pass(self):
        big = compress([3000.0])
        small = compress([200.0])
        firm = _eval_firm(consistency=0.5)
        res = run_eval(iter([big] + [small] * 20), firm, 1, Controls())
        # need total >= 6000 so the 3000 day is <= 50%: 3000 + 15 * 200
        self.assertEqual(res.outcome, "passed")
        self.assertEqual(res.days, 16)
        res2 = run_eval(iter([big]), _eval_firm(), 1, Controls())
        self.assertEqual((res2.outcome, res2.days), ("passed", 1))

    def test_profit_cap_and_stop(self):
        firm = _eval_firm(max_loss=5000.0)
        acct = open_account(50_000.0, firm.eval.phase)
        pnl, st = play_day(acct, compress([100, 700, 1200]), 1, firm.eval.phase, Controls(daily_profit_cap=500))
        self.assertEqual((pnl, st), (500, "cap"))
        pnl, st = play_day(acct, compress([-100, -400, 900]), 1, firm.eval.phase, Controls(daily_stop=300, stop_slippage=5))
        self.assertEqual((pnl, st), (-305, "stop"))

    def test_lock_caps_the_floor(self):
        phase = PhaseRules(max_loss=2000.0, drawdown_mode="eod_trailing", lock_floor_offset=100.0)
        acct = open_account(50_000.0, phase)
        for _ in range(10):
            play_day(acct, compress([1000.0]), 1, phase, Controls())
        self.assertEqual(acct.floor, 50_100.0)

    def test_intraday_trailing_breaches_on_giveback(self):
        """+1500 unrealized then back to -100 at the close: breach intraday, survive EOD."""
        path = [1500.0, -100.0]
        for mode, expect in (("intraday_trailing", "breach"), ("eod_trailing", "ok")):
            phase = PhaseRules(max_loss=1500.0, drawdown_mode=mode, lock_floor_offset=None)
            acct = open_account(50_000.0, phase)
            _, st = play_day(acct, compress(path), 1, phase, Controls())
            self.assertEqual(st, expect, mode)

    def test_fees_one_off_vs_recurring(self):
        flat = [compress([0.0])] * 50
        one = run_eval(iter(flat), _eval_firm(fee=100.0), 1, Controls())
        rec = run_eval(iter(flat), _eval_firm(fee=100.0, period=21), 1, Controls())
        self.assertEqual(one.fees, 100.0)
        self.assertEqual(rec.fees, 300.0)  # days 1, 22, 43


class TestFunded(unittest.TestCase):
    def test_payout_cycle(self):
        firm = _eval_firm()
        days = [compress([200.0])] * 5  # five qualifying days, profit 1000
        res = run_funded(iter(days), firm, 1, Controls())
        self.assertEqual(res.payouts, 1)
        self.assertAlmostEqual(res.withdrawn, 500.0)
        self.assertAlmostEqual(res.trader_take, 450.0)

    def test_payout_never_breaches_floor(self):
        firm = FirmRules(
            name="t",
            start_balance=50_000.0,
            eval=_eval_firm().eval,
            funded=FundedRules(
                phase=PhaseRules(max_loss=500.0, drawdown_mode="eod_trailing", lock_floor_offset=0.0),
                payout_min_days=1,
                payout_frac_of_profit=1.0,
            ),
        )
        res = run_funded(iter([compress([1000.0]), compress([0.0])]), firm, 1, Controls())
        self.assertNotEqual(res.outcome, "breach")
        self.assertLess(res.withdrawn, 1000.0)


class TestIO(unittest.TestCase):
    def test_daily_csv_with_and_without_excursions(self):
        with tempfile.TemporaryDirectory() as tmp:
            p1 = os.path.join(tmp, "a.csv")
            with open(p1, "w") as fh:
                fh.write("date,pnl,mae,mfe\n2026-01-02,100,-300,400\n")
            (d,) = load_daily_csv(p1)
            self.assertEqual(d.segments, ((0.0, 0.0), (400.0, -300.0)))
            self.assertEqual(d.close, 100.0)
            p2 = os.path.join(tmp, "b.csv")
            with open(p2, "w") as fh:
                fh.write("date,pnl\n2026-01-02,100\n")
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                load_daily_csv(p2)
            self.assertTrue(any("optimistic" in str(x.message) for x in w))
            p3 = os.path.join(tmp, "c.csv")
            with open(p3, "w") as fh:
                fh.write("date,pnl,mae,mfe\n2026-01-02,100,300,400\n")  # mae stored as a magnitude
            with self.assertRaisesRegex(ValueError, "mae must be <= 0"):
                load_daily_csv(p3)

    def test_bootstrap_indices(self):
        idx = stationary_bootstrap_indices(10, 1000, 5.0, np.random.default_rng(0))
        self.assertEqual(len(idx), 1000)
        self.assertTrue(((idx >= 0) & (idx < 10)).all())
        runs = np.mean(np.diff(idx) % 10 == 1)
        self.assertGreater(runs, 0.7)  # mostly contiguous with block 5


if __name__ == "__main__":
    unittest.main()
