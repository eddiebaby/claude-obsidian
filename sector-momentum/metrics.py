"""Performance metrics, including the Deflated Sharpe Ratio.

No scipy dependency: the normal CDF is erf-based and its inverse uses Acklam's
rational approximation, so the repo runs on a bare pandas/numpy install.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

TRADING_DAYS = 252
MONTHS = 12
EULER_GAMMA = 0.5772156649015329


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    """Inverse normal CDF (Acklam's algorithm), accurate to ~1e-9."""
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


def _to_equity(returns: pd.Series) -> pd.Series:
    return (1 + returns.fillna(0)).cumprod()


def cagr(returns: pd.Series, periods: int = TRADING_DAYS) -> float:
    eq = _to_equity(returns)
    years = len(returns) / periods
    if years <= 0 or eq.iloc[-1] <= 0:
        return float("nan")
    return eq.iloc[-1] ** (1 / years) - 1


def ann_vol(returns: pd.Series, periods: int = TRADING_DAYS) -> float:
    return returns.std(ddof=1) * math.sqrt(periods)


def sharpe(returns: pd.Series, rf: pd.Series | float = 0.0, periods: int = TRADING_DAYS) -> float:
    excess = returns - rf if not np.isscalar(rf) else returns - rf / periods
    sd = excess.std(ddof=1)
    if sd == 0:
        return float("nan")
    return excess.mean() / sd * math.sqrt(periods)


def max_drawdown(returns: pd.Series) -> float:
    eq = _to_equity(returns)
    return (eq / eq.cummax() - 1).min()


def calmar(returns: pd.Series, periods: int = TRADING_DAYS) -> float:
    mdd = max_drawdown(returns)
    if mdd == 0:
        return float("nan")
    return cagr(returns, periods) / abs(mdd)


def deflated_sharpe(returns: pd.Series, n_trials: int, sharpe_variance: float,
                    periods: int = MONTHS) -> float:
    """Bailey & Lopez de Prado (2014) Deflated Sharpe Ratio.

    Probability the strategy's *per-period* Sharpe is truly > 0 after correcting
    for (a) the number of trials attempted and (b) non-normal returns.

    returns: series at the frequency you deflate on (monthly by default).
    n_trials: honest count of strategy configs evaluated.
    sharpe_variance: variance of the per-period Sharpe estimates across trials.
    """
    r = returns.dropna()
    n = len(r)
    if n < 4:
        return float("nan")
    sr = r.mean() / r.std(ddof=1)  # per-period (non-annualized) Sharpe
    skew = r.skew()
    kurt = r.kurtosis() + 3.0  # pandas gives excess kurtosis; DSR wants raw
    # Expected maximum Sharpe under the null of zero skill across n_trials trials.
    v = max(sharpe_variance, 1e-12)
    sr0 = math.sqrt(v) * (
        (1 - EULER_GAMMA) * norm_ppf(1 - 1.0 / n_trials)
        + EULER_GAMMA * norm_ppf(1 - 1.0 / (n_trials * math.e))
    )
    denom = math.sqrt(1 - skew * sr + (kurt - 1) / 4.0 * sr ** 2)
    if denom <= 0:
        return float("nan")
    z = (sr - sr0) * math.sqrt(n - 1) / denom
    return norm_cdf(z), sr, sr0


def summary(returns: pd.Series, rf_daily: pd.Series | None = None, name: str = "") -> dict:
    rf = rf_daily.reindex(returns.index).fillna(0) if rf_daily is not None else 0.0
    monthly = (1 + returns).resample("ME").prod() - 1
    return {
        "name": name,
        "CAGR": cagr(returns),
        "Vol": ann_vol(returns),
        "Sharpe": sharpe(returns, rf),
        "MaxDD": max_drawdown(returns),
        "Calmar": calmar(returns),
        "months": len(monthly),
        "_monthly": monthly,
    }
