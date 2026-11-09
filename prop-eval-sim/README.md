# prop-eval-sim

Monte Carlo of a prop-firm **evaluation + funded account** under the firm's exact
rules. Feed it a strategy's out-of-sample intraday P&L paths; it reports pass
rate, time to funded, fees, payouts and expected value **per position size**.

Wiki: [[Prop-Firm Intraday Momentum Strategy]] · [[Prop-Firm-Eval-Sizing]] ·
[[LucidFlex Automated Scalping PRD]]

## Why it exists

- An evaluation is a barrier race (profit target vs trailing drawdown). Size is
  chosen by expected value per fee dollar, not by Sharpe.
- The `trading/` code review of 2026-10-13 flagged the old prop-firm compliance
  check as **end-of-day only**. That makes pass rates optimistic: an intraday dip
  through the floor fails the account even if the day closes green. This engine
  checks every bar. On zero-edge MNQ paths the EOD-only view overstates EV by
  about 90% (see results below).

## Install / test

numpy only (no pandas, no network).

```bash
cd prop-eval-sim
python3 -m unittest discover -s tests -v
```

The suite includes a brute-force bar-by-bar reference simulator.
- The fast engine must match it, P&L and status, on more than 10,000 random days.
- Those days span over 600 independently drawn combinations of drawdown mode, lock, touch rule, daily loss limit, stop, cap and slippage.
- The check is mutation-tested: disabling the intraday floor ratchet, flipping event priority, or dropping stop slippage each fails it.
- A gambler's-ruin check confirms the driftless pass rate equals D/(D+T).

## Input

The P&L is for **one unit of size** (1 contract), net of costs, from
walk-forward / CPCV **out-of-sample** runs. Never use in-sample P&L.

| Flag | Format |
|---|---|
| `--bars FILE` | `date,pnl`, one row per bar in time order. `pnl` = cumulative MTM P&L since that day's open. Best option: exact intraday breach checks. |
| `--daily FILE` | `date,pnl[,mae,mfe,mfe_first]`. MAE/MFE give the intraday worst/best as **signed** P&L (mae ≤ 0; a positive mae is rejected). `mfe_first` defaults to 1: the worst case for trailing drawdowns, but the best case for a daily profit cap. Without MAE/MFE you get a warning and optimistic results. |
| `--synthetic MEAN:SD[:BARS[:TRADE_FRAC]]` | Gaussian what-if days, moment-matched to exactly MEAN/SD per trade. |

## Run

```bash
python3 -m propsim --preset lucidflex50k --bars oos_s2_mnq.csv --sizes 2,4,8,12 --sims 3000
python3 -m propsim --synthetic 4.75:125:30:0.44 --sizes 4,8 --profit-cap 1400      # consistency management
python3 -m propsim --synthetic 0:125:30:0.44 --sizes 8 --drawdown-mode intraday_trailing
python3 -m propsim --synthetic 0:125:30:0.44 --sizes 8 --eod-only                  # see the EOD-only bias
python3 -m propsim --synthetic 4.75:125:30:0.44 --sizes 4,8 --fee-period 21        # monthly subscription
python3 -m propsim --synthetic=-3:125:30:0.44 --sizes 4                            # negative mean needs '='
```

Other flags: `--horizon` (trading days per campaign, default 252), `--attempts`
(max evaluations bought, default 5), `--block` (stationary-bootstrap mean block
length, default 10 days), `--daily-stop`, `--funded-profit-cap`,
`--stop-slippage`, `--fee`, `--seed`.

### Output columns

- **Pass/attempt**: passes ÷ completed attempts.
- **P(funded)**: share of campaigns that pass within the attempt budget and horizon.
- **Days to funded**: trading days from the campaign start, failed attempts included.
- **Take**: payouts after the profit split.
- **EV**: take − fees, per campaign.
- **Funded breach**: share of funded accounts later liquidated inside the horizon.
- **Open at horizon**: share of campaigns that ended with an attempt still running. Those attempts are left out of Pass/attempt, but their fees count in EV.

## Presets (`propsim/rules.py`)

| Key | Source | Status |
|---|---|---|
| `lucidflex50k` | Vault's LucidFlex PRD (third-party guides, 2026-07-06) | **Re-verify every number.** Fee period, payout cap and the MLL lock level are uncertain |
| `generic-intraday50k` | Illustrative intraday-trailing structure | Not any specific firm |
| `generic-eod-dll50k` | Illustrative EOD-trailing + daily loss limit | Not any specific firm |

Build a firm-specific `FirmRules` from the firm's help center before buying an evaluation.

## Model assumptions

- **Fills.** Trader stops and firm daily-loss-limit flattens fill at the level minus `--stop-slippage` per unit. Profit caps fill exactly at the cap.
- **Bar resolution.** When a bar jumps across several levels, the highest level counts as crossed first. Breaches are checked on bar values; an intrabar spike is invisible below bar resolution.
- **Judging.** Profit target and payout eligibility use end-of-day balances.
- **Payouts.** Withdrawals do not move the floor or the high-water mark, and are capped so the balance stays above the floor. Payout size is a share of *total* profit above the starting balance, not of profit earned in the cycle; check this against the firm's rule.
- **Not modeled:**
  - contract-cap scaling with balance;
  - news blackouts;
  - firm-specific payout-cap tiers;
  - funded-phase monthly or data fees;
  - multiple simultaneous accounts.
- **Bootstrap.** The stationary bootstrap keeps autocorrelation up to about the block length, not longer regimes.

## Results so far (synthetic, LucidFlex preset as modeled)

Unit = 1 MNQ. Per-trade SD is $125 (~20 bps, from the vault's gamma-reversal
test). There is a trade on 44% of days. Each campaign runs 252 days with up to 5
attempts and 3,000 simulations.

| Edge per MNQ trade | Best-EV size | Pass/attempt | P(funded) | EV / yr | P(net>0) |
|---|---|---|---|---|---|
| −$3 (dead after costs) | 8 | 20% | 67% | +$170 | 22% |
| $0 | 8 | 23% | 72% | +$324 | 25% |
| +$4.75 (50% haircut) | 8 (12 ties) | 26% | 78% | +$614 | 30% |
| +$9.50 (in-sample) | 8 | 30% | 83% | +$993 | 36% |

At zero edge, size 8:

| Check | Pass/attempt | EV |
|---|---|---|
| EOD trailing (bar-level paths) | 23% | $324 |
| Intraday trailing (same paths) | 19% | $144 |
| EOD-only data (old check) | 27% | $619 |

Read: under these rules EV comes mostly from the payoff structure (capped
downside), not the edge. Most campaigns still lose their fees (P(net>0) ≤ 36%).
The EV is a few hundred to about $1k a year per account, and it is fragile to
the fee schedule: a monthly fee cuts size-4 EV from $519 to $66.
