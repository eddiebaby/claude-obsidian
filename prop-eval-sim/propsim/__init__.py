"""propsim: prop-firm evaluation and funded-account Monte Carlo.

Feeds a strategy's out-of-sample intraday P&L paths through a firm's exact
rules and reports pass rate, time to pass, fees, payouts and expected value per
position size.
"""
from .engine import Controls, open_account, play_day, run_eval, run_funded
from .montecarlo import run_campaign, simulate, sweep, to_markdown
from .paths import Day, compress, eod_only, load_bar_csv, load_daily_csv, synthetic_days
from .rules import PRESETS, EvalRules, FirmRules, FundedRules, PhaseRules

__all__ = [
    "Controls",
    "Day",
    "EvalRules",
    "FirmRules",
    "FundedRules",
    "PRESETS",
    "PhaseRules",
    "compress",
    "eod_only",
    "load_bar_csv",
    "load_daily_csv",
    "open_account",
    "play_day",
    "run_campaign",
    "run_eval",
    "run_funded",
    "simulate",
    "sweep",
    "synthetic_days",
    "to_markdown",
]
