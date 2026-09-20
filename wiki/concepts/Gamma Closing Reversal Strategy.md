---
type: concept
title: "Gamma Closing Reversal Strategy"
domain: quantitative-finance
complexity: intermediate
created: 2026-09-18
updated: 2026-09-18
tags:
  - strategy
  - quantitative-finance
  - futures
  - intraday
status: seed
aliases:
  - "High-Gamma Last-Half-Hour Fade"
  - "Market Intraday Momentum (tested)"
related:
  - "[[Research - Intraday Futures Strategies Under Prop-Firm Constraints]]"
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[baltussen2021-hedging-demand-intraday-momentum]]"
  - "[[mesfin2026-mnq-intraday-falsification]]"
  - "[[Walk-Forward-Analysis]]"
  - "[[Execution-Realism]]"
  - "[[Micro-Futures Trend Strategy]]"
sources:
  - "[[baltussen2021-hedging-demand-intraday-momentum]]"
  - "[[mesfin2026-mnq-intraday-falsification]]"
---

# Gamma Closing Reversal Strategy

Candidate, pending validation. The one survivor of the 2026-09-18 intraday-momentum round. Code: `trading/propfirm/gamma_momentum.py`.

## Thesis

When options dealers are net **long** gamma, delta-hedging makes them sell strength and buy weakness into the close, so the day's move partly reverses in the last half hour. This is one half of [[baltussen2021-hedging-demand-intraday-momentum]]. The other half (short gamma leads to momentum) did **not** show up in 2023-26 data.

## Setup Conditions

- **Market context required:** prior-day SqueezeMetrics GEX in the top third of its trailing 252-day range.
- **Entry trigger:** at 15:30 ET, fade the sign of the prior-close → 15:30 return.
- **Filters / confirmation:** none yet. Adding filters before validation just adds degrees of freedom.

## Execution

| Parameter | Value |
|-----------|-------|
| Asset class | Index futures (MNQ preferred, MES secondary) |
| Timeframe | Intraday, one trade per day, 15:30 → 16:00 ET |
| Position size | 1 micro until validated |
| Entry | Market at 15:30 |
| Stop | None tested (30-minute hold) |
| Target | Exit at the 16:00 close |
| R:R | N/A, time exit |

## Evidence

Net of 2 ticks plus TOS commission per round trip, charged in bps.

| Data | Net bps/trade | t | PF | By year |
|---|---|---|---|---|
| QQQ 1h, 2023-10 → 2026-09 (327 high-GEX days) | +1.8 | 1.65 | 1.29 | +1.0 / +1.9 / +2.2 / +1.2 |
| SPY 1h, same span | +0.5 | 0.56 | 1.09 | +0.2 / +0.5 / +0.5 / +1.0 |
| MNQ 5m, 2026-02 → 09 (38 days) | +3.7 | 0.96 | 1.52 | — |
| MES 5m, same (38 days) | +1.7 | 0.70 | 1.38 | — |

- About $9.50 per MNQ contract per trade and about 110 trades a year, so roughly $1K a year per contract. Not significant after about 40 tests in the round.
- Killed in the same round: unconditional Gao-Han-Li-Zhou momentum (SPY 3 yrs −1.4 bps, PF 0.82), and low-gamma momentum (SPY −3.1, QQQ −3.3 bps).
- Consistent with [[mesfin2026-mnq-intraday-falsification]]: signals built only from price are dead; the gamma state is the only information here that isn't OHLCV.

## Risks & Failure Modes

- **Multiple testing.** The best cell of about 40 tests. It needs data from before 2023 to count.
- **Regime specificity.** The high-gamma, 0DTE era (2023+) may be what created it; it could invert in a short-gamma bear market.
- **GEX is a vendor model.** SqueezeMetrics can revise its methodology, and the free CSV could disappear.
- **The edge is only 1-2 ticks gross over cost.** Close-auction slippage on MNQ could eat it. Paper-trade the fills before sizing.

## Related Strategies / Concepts

- [[Research - Intraday Futures Strategies Under Prop-Firm Constraints]]
- [[LucidFlex Automated Scalping PRD]]: flat by 16:00, so it's prop-legal

## Sources

- [[baltussen2021-hedging-demand-intraday-momentum]]
- [[mesfin2026-mnq-intraday-falsification]]

## Status

- [x] Hypothesis formed
- [x] Backtested (2023-26, weak positive)
- [ ] Validated on 2018-2023 NQ (`python -m propfirm.pull_databento NQ --quote`, needs a Databento key)
- [ ] Paper traded
- [ ] Live (small size)
- [ ] Scaled
