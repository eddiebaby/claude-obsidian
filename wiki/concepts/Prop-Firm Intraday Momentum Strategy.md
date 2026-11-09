---
type: concept
title: "Prop-Firm Intraday Momentum Strategy"
domain: quantitative-finance
complexity: intermediate
created: 2026-11-09
updated: 2026-11-09
tags:
  - strategy
  - quantitative-finance
  - futures
  - intraday
  - prop-firm
status: seed
aliases:
  - "Prop-Firm Day Trading Strategy"
  - "Futures Program on a Prop Account"
related:
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[Prop-Firm-Eval-Sizing]]"
  - "[[Gamma Closing Reversal Strategy]]"
  - "[[Research - Intraday Futures Strategies Under Prop-Firm Constraints]]"
  - "[[Research - Strengthening the LucidFlex Bot Plan]]"
  - "[[mesfin2026-mnq-intraday-falsification]]"
  - "[[baltussen2021-hedging-demand-intraday-momentum]]"
  - "[[Micro-Futures Trend Strategy]]"
  - "[[Walk-Forward-Analysis]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[Execution-Realism]]"
  - "[[Databento]]"
sources:
  - "Personal Systematic Futures Trading Program PRD (CME equity-index core, micros), pasted 2026-11-08; not yet in .raw/"
  - "prop-eval-sim/README.md (Monte Carlo results, 2026-11-09)"
  - "[[mesfin2026-mnq-intraday-falsification]]"
  - "[[baltussen2021-hedging-demand-intraday-momentum]]"
  - "[[busseti-ryu-boyd-2016-risk-constrained-kelly]]"
---

# Prop-Firm Intraday Momentum Strategy

This page covers two things:
- How the November 2026 *Personal Systematic Futures Trading Program* PRD maps onto a futures prop-firm account.
- What the evaluation Monte Carlo (`prop-eval-sim/`) says about position size and expected value.

It builds on [[LucidFlex Automated Scalping PRD]] (the rule research) and [[Prop-Firm-Eval-Sizing]] (the sizing frame) and replaces neither.

## Thesis

A prop evaluation is a race with capped downside: reach the profit target before the trailing drawdown, and the most you can lose is the fee. The strategy's job is to run that race. The candidates are the futures program's intraday sleeves that already end flat at the close:
- **Last-30-minute momentum (S2), conditioned on dealer gamma.** The vault's version is [[Gamma Closing Reversal Strategy]]: fade the day's move on high-GEX days.
- **Noise-area breakout (S3), long-only on NQ.**

## What carries over from the futures program PRD

| PRD element | On a prop account | Why |
|---|---|---|
| Validation stack (trial ledger, walk-forward, CPCV, DSR/PBO, cost model) | Keep all of it | Passing an evaluation is weak evidence of edge, so pre-live validation carries all the weight |
| S2 last-30-min momentum (gamma-conditioned) | **Primary** | Flat by the close, one trade a day, 10:30–11:00 HST in winter |
| S3 noise-area breakout (+ ORB trigger) | Secondary; shares a risk budget with S2 | Decayed: Paz (SSRN 7290621) out-of-sample Sharpe 0.39 vs 1.33 in-sample. Test only the long-only NQ arm |
| S1 trend, S6 RSI(2), S5 overnight drift | Drop | They hold overnight, which the flat-by-cutoff rule forbids |
| S9a vol targeting | Keep, re-based | Size against the distance left to the drawdown floor, not against equity |
| Risk ladder, account tiers, margin | Replace | The firm's drawdown, daily loss limit and contract cap govern |
| IBKR execution | Replace | You trade on the firm's platform |
| §1256 60/40 tax | Does not apply | Payouts are normally contractor income (1099): ordinary rates plus self-employment tax. Confirm with a CPA |

The prop route also fixes the PRD's own economics problem. At under ~$50–100k of own capital, the fixed cost base is a 5–20% hurdle; a prop account replaces that capital requirement with a capped fee.

## Setup Conditions

- **Entry trigger:** at 15:30 ET (10:30 HST winter, 09:30 HST in US summer), take the sign of the prior-close → 15:30 return. Fade it on high-GEX days. Follow it on short-gamma days only if that arm ever validates; it did not in 2023–26 data.
- **Market context required:** the GEX tercile (prior day). The VIX/VIX3M ratio as a regime overlay (PRD FR-S9a).
- **Filters / confirmation:** skip entries within ±2 minutes of scheduled releases. Respect the firm's flatten cutoff (LucidFlex: 16:45 ET).

## Execution

| Parameter | Value |
|-----------|-------|
| Asset class | MNQ (MES secondary); minis only once funded and size ≥ 10 micros |
| Timeframe | Intraday, 15:30 → 15:59:30 ET, about 110 trades a year at the high-GEX filter |
| Position size | Set by `propsim` expected value, not by Sharpe. LucidFlex as modeled: ~4 MNQ maximizes P(net > 0); ~8 MNQ maximizes EV |
| Entry | Marketable limit at 15:30 |
| Stop | None inside the 30-minute hold; own daily stop well inside the floor |
| Target | Time exit |
| R:R | N/A |

## Evaluation economics (propsim, synthetic paths, LucidFlex rules as modeled)

Assumptions:
- Unit = 1 MNQ. Per-trade SD is $125 (~20 bps, the gamma-reversal test's dispersion). A trade happens on 44% of days.
- Each campaign covers 252 trading days with up to 5 evaluation attempts, and is simulated 3,000 times.
- Rules: $130 fee per attempt; $3k target; $2k EOD trailing drawdown that locks at start + $100; 50% consistency rule. Funded: 90% split; 5 days of at least $150 per payout; withdraw 50% of profit; at most 5 payouts.

| Edge per MNQ trade | Size | Pass/attempt | P(funded) | Days to funded | EV / yr | P(net>0) | Funded breach |
|---|---|---|---|---|---|---|---|
| −$3 (dead after costs) | 4 | 22% | 70% | 81 | +$77 | 29% | 94% |
| −$3 | 8 | 20% | 67% | 33 | +$170 | 22% | 99% |
| $0 | 4 | 26% | 76% | 80 | +$227 | 35% | 94% |
| $0 | 8 | 23% | 72% | 33 | +$324 | 25% | 98% |
| +$4.75 (50% haircut) | 4 | 32% | 84% | 75 | +$519 | 45% | 92% |
| +$4.75 | 8 | 26% | 78% | 32 | +$614 | 30% | 97% |
| +$9.50 (in-sample) | 4 | 39% | 90% | 70 | +$897 | 54% | 89% |
| +$9.50 | 8 | 30% | 83% | 32 | +$993 | 36% | 96% |

Sensitivity at zero edge, size 8:

| Variant | Pass/attempt | EV / yr |
|---|---|---|
| EOD trailing, bar-level paths (base case) | 23% | $324 |
| Same paths, intraday trailing drawdown | 19% | $144 |
| End-of-day data only (the old compliance check) | 27% | $619 |

Other sensitivities, at +$4.75 edge:
- A $1,400 daily profit cap in the evaluation lifts size-8 EV from $614 to $690.
- A monthly fee instead of a one-off fee cuts size-4 EV from $519 to $66.

### Key findings

1. **A zero-edge strategy passes 19–26% of attempts.** This matches the 2026-10-13 cost rerun (~25%). Passing is not evidence of edge.
2. **Under these rules, EV comes mostly from the payoff structure.** The trader keeps withdrawals and the firm absorbs losses, so EV stays positive even at zero or slightly negative edge. Moving edge from −$3 to +$9.50 raises EV at size 8 from $170 to $993 a year.
3. **EV is a right tail.** Most campaigns lose their fees (P(net > 0) is at most 54%), and funded accounts are consumables: 89–99% are liquidated within the year. Withdraw at every eligible cycle.
4. **Rule details swing EV more than edge does.** Fee schedule, drawdown type and payout terms each move EV by 2–8×.
5. **The 2026-10-13 HIGH code-review finding is now quantified.** Checking only end-of-day balances overstates EV by ~90%.

### Money implication

The next action is to verify four rule numbers in writing with Lucid, not more signal research:
1. Is the $130 fee one-off or monthly?
2. Is there a funded payout cap?
3. What level does the drawdown floor lock at?
4. Are funded payouts paid from a simulated account?

If all four verify as modeled, a $130 evaluation at 4–8 MNQ is positive EV even with the current marginal sleeve. If the fee is monthly or payouts are capped low, it is not. Re-run `propsim` on the real gamma-reversal out-of-sample bar paths before buying.

## Execution path

- Tradovate's API excludes prop and evaluation accounts (futures program PRD §5.4). The LucidFlex PRD records that Lucid allows bots, API strategies and copiers; confirm which platform/API route Lucid actually exposes.
- Routes, cheapest first:
  - A manual click on a Python alert. Viable at one trade a day at 10:30 HST.
  - A NinjaTrader strategy in C#, with research staying in Python.
  - A webhook bridge (TradersPost, PickMyTrade, CrossTrade).
- Data: if signals run on the platform feed, Databento live ($199/mo) is unnecessary and pay-as-you-go historical data covers research. If Python generates signals live, it is needed. Ask [[Databento]] whether prop trading counts as non-professional use.

## Evidence

- [[Gamma Closing Reversal Strategy]]:
  - QQQ +1.8 bps per trade, t = 1.65 over 327 high-GEX days.
  - MNQ +3.7 bps over 38 days.
  - About $9.50 per MNQ per trade.
  - Not significant after ~40 tests in the round.
- Unconditional Gao-Han-Li-Zhou momentum is dead in 2023–26 (SPY −1.4 bps per trade). Low-gamma momentum is negative.
- [[mesfin2026-mnq-intraday-falsification]]: OHLCV-only intraday families fail on MNQ net of costs. The gamma state is the one non-OHLCV input, which is why the gamma sleeve is the candidate.
- [[baltussen2021-hedging-demand-intraday-momentum]]: the peer-reviewed mechanism (dealer gamma hedging, leveraged-ETF rebalancing).
- 2026-10-13 cost rerun: no prop-firm strategy is ALIVE. The gamma high-GEX reversal is MARGINAL but best supported, and gated on Databento 2018+ history at t > 2.

## Risks & Failure Modes

- **The rules are unverified.** Third-party sources already disagree, and firms change rules without notice.
- **Counterparty risk.** Funded accounts are usually simulated and payouts come from fee revenue. Firms fail.
- **Consistency rules vs positive skew.** Momentum P&L arrives in a few big days, which can block passing or payouts.
- **Synthetic paths are Gaussian.** Real out-of-sample paths have fatter tails and will lower pass rates.
- **The edge is still unproven.** t = 1.65 before multiple-testing correction. Treat the +$4.75 haircut row as optimistic and the $0 row as the planning case.
- **Behavior.** EV-optimal size (~8 MNQ, about $1,000 per-trade SD, half the drawdown) feels reckless and invites overriding. Decide the size in advance and let the code place it.

## Related Strategies / Concepts

- [[LucidFlex Automated Scalping PRD]]: rule table, strategy menu, phased gates
- [[Prop-Firm-Eval-Sizing]]: risk-constrained Kelly frame; design rule 4 is what `propsim` implements
- [[Gamma Closing Reversal Strategy]]: the sleeve to feed into the simulator
- [[Micro-Futures Trend Strategy]]: the own-capital trend sleeve this account type cannot hold

## Sources

- Personal Systematic Futures Trading Program PRD, pasted in session 2026-11-08. Ingest to `.raw/` to keep it.
- `prop-eval-sim/` code and README: [[Prop-Firm-Eval-Sizing]] design rule 4, implemented
- [[mesfin2026-mnq-intraday-falsification]]
- [[baltussen2021-hedging-demand-intraday-momentum]]
- [[busseti-ryu-boyd-2016-risk-constrained-kelly]]

## Status

- [x] Hypothesis formed
- [x] Evaluation simulator built (`prop-eval-sim/`, 15 tests, bar-by-bar reference check)
- [ ] Lucid rules verified in writing (fee period, payout cap, floor lock level, sim payouts)
- [ ] Gamma reversal validated on Databento 2018+ (t > 2)
- [ ] Out-of-sample bar paths run through `propsim`; size chosen
- [ ] Paper traded
- [ ] Evaluation bought
