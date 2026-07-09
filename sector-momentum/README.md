# sector-momentum

Backtest of the baseline **Sector-ETF Momentum Strategy** from the wiki
([[Sector-ETF Momentum Strategy]]). Built 2026-07-07. Zero paid dependencies —
pandas + numpy only, data pulled free from the Yahoo chart API.

## What it does

- **Universe**: 11 SPDR sector ETFs (XLK…XLC), treated as a growing set (XLRE
  from 2015, XLC from 2018 — ranked only once each has 252 days of history).
- **Signal**: 12-1 momentum (return from t-252 to t-21, skipping the last
  month), cross-sectional rank, hold top-N equal weight.
- **Overlay**: absolute-momentum filter — any selected ETF whose trailing
  12-month return is below the T-bill return (`^IRX`) rotates to cash. This is
  the crash-avoidance leg.
- **Turnover control**: optional tolerance band (hold a name until it drops out
  of the top-4 or top-5).
- **Costs**: 5 bps per side on turnover, monthly rebalance, market-on-close.
- **Validation**: benchmarks vs SPY / equal-weight / plain-momentum; Deflated
  Sharpe (Bailey & López de Prado 2014); walk-forward split at 2016.

## Run it

```bash
python data.py          # download + cache the universe (once)
python run.py           # full variant table + deflated Sharpe
python walkforward.py   # in-sample-pick -> out-of-sample-read discipline check
```

Outputs land in `results/` (equity curves + summary CSV).

## Headline result (2000–2026, net of costs)

| Strategy | CAGR | Sharpe | MaxDD |
|---|---|---|---|
| Top-3 + overlay + band(5) | 10.3% | 0.57 | −30.3% |
| SPY buy & hold | 8.2% | 0.41 | −55.2% |

Full-sample it beats SPY on every axis (13.2x vs 8.1x). **But the entire edge
is crash avoidance** — in the walk-forward out-of-sample window (2016–2026, no
sustained bear) SPY edges it on Sharpe (0.75 vs 0.71). Conclusion: this is a
*defensive equity sleeve*, not standalone bull-market alpha. Exactly what the
momentum literature predicts. Treat the modest Sharpe as honest, not a miss.

## Files

- `data.py` — Yahoo chart API fetch + CSV cache
- `strategy.py` — momentum, ranking, overlay, band
- `backtest.py` — monthly rebalance engine (drift, costs, cash leg) + benchmarks
- `metrics.py` — CAGR / vol / Sharpe / drawdown / Deflated Sharpe (no scipy)
- `run.py` — variant comparison + DSR
- `walkforward.py` — IS/OOS discipline check

## Known limitations / next

- DSR trial variance is tiny because the 6 configs are near-identical; the
  honest breadth of the search is wider (whole roadmap) — DSR here understates
  the multiple-testing haircut.
- No expansion hooks yet (ranking model, regime gate, joint TSM+CSM).
- Signal and execution share the rebalance close (standard, but a same-bar
  assumption).
