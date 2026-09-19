"""Performance metrics, pure stdlib (no numpy, no scipy — the test suite is hermetic).

Includes the Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014), because the
honest question about any trend backtest is not "what was the Sharpe" but "what
is the chance this Sharpe survives the number of configurations I tried".

Futures-specific additions at the bottom: cost drag, contract turnover, margin
utilisation and effective market count. A trend book that looks good on returns
and runs at 60% margin-to-equity is not the same strategy the backtest describes.
"""
from __future__ import annotations

import math
from datetime import date

TRADING_DAYS = 252
MONTHS = 12
EULER_GAMMA = 0.5772156649015329


# --- distributions ----------------------------------------------------------

def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    """Inverse normal CDF (Acklam), accurate to ~1e-9. Same routine the
    sector-momentum engine uses, kept dependency-free."""
    if p <= 0.0:
        return -math.inf
    if p >= 1.0:
        return math.inf
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


# --- moments ----------------------------------------------------------------

def mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def stdev(xs, ddof: int = 1) -> float:
    xs = list(xs)
    n = len(xs)
    if n - ddof <= 0:
        return float("nan")
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - ddof))


def skewness(xs) -> float:
    xs = list(xs)
    n = len(xs)
    sd = stdev(xs, ddof=0)
    if n < 3 or sd == 0 or math.isnan(sd):
        return float("nan")
    m = mean(xs)
    return sum(((x - m) / sd) ** 3 for x in xs) / n


def kurtosis(xs, excess: bool = True) -> float:
    xs = list(xs)
    n = len(xs)
    sd = stdev(xs, ddof=0)
    if n < 4 or sd == 0 or math.isnan(sd):
        return float("nan")
    m = mean(xs)
    k = sum(((x - m) / sd) ** 4 for x in xs) / n
    return k - 3.0 if excess else k


# --- return statistics ------------------------------------------------------

def equity_from_returns(returns, initial: float = 1.0) -> list[float]:
    eq, out = initial, []
    for r in returns:
        eq *= (1.0 + r)
        out.append(eq)
    return out


def cagr(returns, periods: int = TRADING_DAYS) -> float:
    returns = list(returns)
    if not returns:
        return float("nan")
    total = 1.0
    for r in returns:
        total *= (1.0 + r)
    years = len(returns) / periods
    if years <= 0 or total <= 0:
        return float("nan")
    return total ** (1.0 / years) - 1.0


def ann_vol(returns, periods: int = TRADING_DAYS) -> float:
    return stdev(returns) * math.sqrt(periods)


def sharpe(returns, rf_daily=0.0, periods: int = TRADING_DAYS) -> float:
    """Excess-return Sharpe. For a futures book the risk-free leg is *earned*
    (collateral interest is inside the returns), so it must be subtracted here
    or the ratio flatters the strategy by the whole cash rate."""
    returns = list(returns)
    if isinstance(rf_daily, (int, float)):
        excess = [r - rf_daily for r in returns]
    else:
        rf = list(rf_daily)
        excess = [r - (rf[i] if i < len(rf) else 0.0) for i, r in enumerate(returns)]
    sd = stdev(excess)
    # A flat (or floating-point-flat) series has no Sharpe. Without the epsilon
    # a 1e-19 rounding residue in the denominator prints a Sharpe of 10^15.
    if math.isnan(sd) or sd < 1e-12:
        return float("nan")
    return mean(excess) / sd * math.sqrt(periods)


def sortino(returns, target: float = 0.0, periods: int = TRADING_DAYS) -> float:
    returns = list(returns)
    downside = [min(0.0, r - target) for r in returns]
    dd = math.sqrt(sum(x * x for x in downside) / len(downside)) if downside else 0.0
    if dd == 0:
        return float("nan")
    return (mean(returns) - target) / dd * math.sqrt(periods)


def drawdown_curve(equity) -> list[float]:
    peak, out = -math.inf, []
    for e in equity:
        peak = max(peak, e)
        out.append(e / peak - 1.0 if peak > 0 else 0.0)
    return out


def max_drawdown(equity) -> float:
    dd = drawdown_curve(equity)
    return min(dd) if dd else 0.0


def drawdown_detail(equity, dates=None) -> dict:
    """Worst drawdown plus how long it lasted and whether it recovered.

    Trend books are held through multi-year drawdowns; the duration is the number
    that decides whether a real person can actually sit in the position.
    """
    dd = drawdown_curve(equity)
    if not dd:
        return {"max_dd": 0.0, "trough_i": None, "length_days": 0, "recovered": True}
    trough = min(range(len(dd)), key=lambda i: dd[i])
    peak_i = max((i for i in range(trough + 1) if dd[i] == 0.0), default=0)
    recovery = next((i for i in range(trough, len(dd)) if dd[i] >= -1e-12), None)
    out = {
        "max_dd": dd[trough],
        "trough_i": trough,
        "peak_i": peak_i,
        "length_days": (recovery if recovery is not None else len(dd) - 1) - peak_i,
        "recovered": recovery is not None,
    }
    if dates:
        out["peak_date"] = dates[peak_i]
        out["trough_date"] = dates[trough]
        out["recovery_date"] = dates[recovery] if recovery is not None else None
    return out


def calmar(returns, equity=None, periods: int = TRADING_DAYS) -> float:
    eq = equity if equity is not None else equity_from_returns(returns)
    mdd = max_drawdown(eq)
    if mdd == 0:
        return float("nan")
    return cagr(returns, periods) / abs(mdd)


def monthly_returns(dates: list[date], returns: list[float]) -> dict[tuple, float]:
    out: dict[tuple, float] = {}
    for d, r in zip(dates, returns):
        k = (d.year, d.month)
        out[k] = (1.0 + out.get(k, 0.0)) * (1.0 + r) - 1.0
    return out


def annual_returns(dates: list[date], returns: list[float]) -> dict[int, float]:
    out: dict[int, float] = {}
    for d, r in zip(dates, returns):
        out[d.year] = (1.0 + out.get(d.year, 0.0)) * (1.0 + r) - 1.0
    return out


def hit_rate(returns) -> float:
    returns = [r for r in returns if r == r]
    if not returns:
        return float("nan")
    return sum(1 for r in returns if r > 0) / len(returns)


# --- multiple-testing correction --------------------------------------------

def deflated_sharpe(returns, n_trials: int, sharpe_variance: float,
                    periods: int = MONTHS) -> dict:
    """Probability the true Sharpe is > 0 after correcting for the search.

    returns: the series at the frequency you deflate on (monthly by default).
    n_trials: honest count of configurations tried — including the ones you
        abandoned, and the ones your reading of other people's results implies.
    sharpe_variance: variance of per-period Sharpe estimates across those trials.
    """
    r = [x for x in returns if x == x]
    n = len(r)
    if n < 4 or n_trials < 2:
        return {"dsr": float("nan"), "sharpe": float("nan"), "threshold": float("nan"),
                "n": n}
    sd = stdev(r)
    if not sd or math.isnan(sd):
        return {"dsr": float("nan"), "sharpe": float("nan"), "threshold": float("nan"),
                "n": n}
    sr = mean(r) / sd                       # per-period, not annualised
    sk = skewness(r)
    ku = kurtosis(r, excess=False)
    v = max(sharpe_variance, 1e-12)
    sr0 = math.sqrt(v) * ((1 - EULER_GAMMA) * norm_ppf(1 - 1.0 / n_trials)
                          + EULER_GAMMA * norm_ppf(1 - 1.0 / (n_trials * math.e)))
    denom = 1 - sk * sr + (ku - 1) / 4.0 * sr ** 2
    if denom <= 0:
        return {"dsr": float("nan"), "sharpe": sr, "threshold": sr0, "n": n}
    z = (sr - sr0) * math.sqrt(n - 1) / math.sqrt(denom)
    return {"dsr": norm_cdf(z), "sharpe": sr, "threshold": sr0, "n": n,
            "sharpe_ann": sr * math.sqrt(periods),
            "threshold_ann": sr0 * math.sqrt(periods)}


# --- the futures-aware summary ----------------------------------------------

def summary(result, rf_annual: float | None = None, name: str = "") -> dict:
    """Fold a BacktestResult into one row, including the mechanics that decide
    whether the return stream is reproducible in a real account."""
    dates, rets = result.dates, result.returns
    eq = result.equity_curve
    if rf_annual is None:
        rf_annual = result.config.rates.annual(dates[-1]) if dates else 0.0
    rf_daily = (1.0 + rf_annual) ** (1.0 / TRADING_DAYS) - 1.0
    dd = drawdown_detail(eq, dates)
    ann = annual_returns(dates, rets)
    interest = sum(r.interest for r in result.records)

    return {
        "name": name or getattr(result.config, "label", "") or "run",
        "start": dates[0] if dates else None,
        "end": dates[-1] if dates else None,
        "years": result.years(),
        "final_equity": result.final_equity,
        "CAGR": cagr(rets),
        "Vol": ann_vol(rets),
        "Sharpe": sharpe(rets, rf_daily),
        "Sortino": sortino(rets),
        "MaxDD": dd["max_dd"],
        "DD_days": dd["length_days"],
        "DD_recovered": dd["recovered"],
        "Calmar": calmar(rets, eq),
        "Skew": skewness(rets),
        "Kurtosis": kurtosis(rets),
        "HitRate": hit_rate(rets),
        "best_year": max(ann.values()) if ann else float("nan"),
        "worst_year": min(ann.values()) if ann else float("nan"),
        # futures mechanics
        "vol_target": result.config.vol_target,
        "vol_realised_ratio": (ann_vol(rets) / result.config.vol_target
                               if result.config.vol_target else float("nan")),
        "interest_earned": interest,
        "interest_share": (interest / (result.final_equity - result.config.initial_equity)
                           if result.final_equity != result.config.initial_equity
                           else float("nan")),
        "costs": result.total_costs(),
        "cost_drag": result.cost_drag(),
        "roll_costs": result.costs_by_reason.get("roll", 0.0),
        "signal_costs": result.costs_by_reason.get("signal", 0.0),
        "contracts_per_year": result.turnover(),
        "turnover_x_equity": result.turnover_notional(),
        "avg_margin_to_equity": result.avg_margin_to_equity(),
        "peak_margin_to_equity": result.peak_margin_to_equity(),
        "effective_markets": mean([r.effective_markets for r in result.records])
                             if result.records else float("nan"),
        "markets": len(result.symbols),
        "margin_calls": result.margin_calls,
        "derisk_days": result.derisk_days,
        "blown_up": result.blown_up,
        "_annual": ann,
        "_monthly": monthly_returns(dates, rets),
    }
