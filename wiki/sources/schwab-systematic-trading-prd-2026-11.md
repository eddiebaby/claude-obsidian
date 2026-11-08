---
type: source
title: "PRD: Systematic Trading Program on Charles Schwab"
created: 2026-11-08
updated: 2026-11-08
domain: quantitative-finance
address: c-000163
tags:
  - source
  - quantitative-finance
  - prd
  - schwab
  - etf
  - options
  - tax
status: ingested
source_type: research-report
source_file: ".raw/articles/schwab-systematic-trading-prd-2026-11-07.md"
url: "https://claude.ai/artifact/71ts2uKTPXF9Wp1t9YiQRT"
author: "Claude deep-research (Claude Doc), owner Scott"
date_published: 2026-11-07
confidence: medium
key_claims:
  - "Run four sleeves at Schwab: E1 cross-asset ETF trend and E5 ETF mean reversion in an IRA; E8 intraday SPY/QQQ momentum (quarter risk) and O1 XSP put spreads in a taxable margin account; target net Sharpe 0.5-0.8 at 8-10% vol"
  - "The Schwab Trader API places orders for stocks, ETFs and listed options only; futures orders return HTTP 400, so futures sleeves are replicated in ETFs or kept at IBKR"
  - "Schwab stopped counting day trades on 8 June 2026 and added real-time intraday buying power on 13 July 2026; FINRA phase-in for other brokers runs to 20 October 2027"
  - "A one-cent SPY spread is about 0.15 bp per round trip vs about 0.7 bp for MES, so intraday index exposure is 4-5x cheaper as ETFs than as micros at Schwab"
  - "Tax design: ETF sleeves in the IRA, XSP for Section 1256 60/40, ticker partition by index so taxable losses never become permanent IRA wash sales"
  - "About $1-2.5k a year to run the MVP; first one-unit live trades about 4-5 months out"
related:
  - "[[Schwab-Trader-API]]"
  - "[[Pattern-Day-Trader-Rule]]"
  - "[[Section-1256-Contracts]]"
  - "[[Wash-Sale-Rule]]"
  - "[[Trend-Following]]"
  - "[[Short-Term Mean Reversion Strategy]]"
  - "[[Volatility Risk Premium Strategy]]"
  - "[[Gamma Closing Reversal Strategy]]"
  - "[[Micro-Futures Trend Strategy]]"
  - "[[Post-Earnings Announcement Drift Strategy]]"
  - "[[Cross-Sectional-Momentum]]"
  - "[[Retail Alpha Strategy Roadmap]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[Combinatorial-Purged-Cross-Validation]]"
  - "[[Walk-Forward-Analysis]]"
  - "[[Backtest-Overfitting]]"
  - "[[Databento]]"
  - "[[Norgate-Data]]"
  - "[[compass2026-unified-backtester-prd-brief]]"
---

# PRD: Systematic Trading Program on Charles Schwab

Claude Doc, rev 21, dated 2026-11-07, sources checked the same day. **It picks four sleeves Schwab can run unattended, with a target net Sharpe of 0.5–0.8 at 8–10% vol and a −15% hard stop.** It extends a companion CME micro-futures PRD (IBKR/Tradovate) that is **not in the vault** (see Gaps). Live doc: [Claude Doc](https://claude.ai/artifact/71ts2uKTPXF9Wp1t9YiQRT).

## The MVP: four sleeves

| Sleeve | Instrument | Evidence | Account | Risk share | Build order |
|---|---|---|---|---|---|
| E1 cross-asset trend, long/flat | VTI, IWM, EFA, EEM, IEF, TLT, GLD, PDBC, UUP, IBIT | A | IRA | 40% | MVP 1 |
| E5 short-horizon mean reversion | IWM, DIA, 11 sector SPDRs | C | IRA | 20% | MVP 2 |
| E8 intraday momentum | SPY, QQQ | B− (OOS Sharpe 0.39) | Taxable margin | 10% at launch, 20% target | MVP 3, small risk |
| O1 defined-risk put-write | XSP put spreads | A (premium exists) | Taxable (§1256) | 20% | MVP 4 |

The remaining 10% is reserve/research. Research tracks: E6 pairs/stat-arb and O4 earnings straddles (both need t > 3.0), plus E3 cross-sectional momentum after a Norgate purchase. **Bench or exclude:** post-earnings drift (E7), overnight SPY (E9), calendar effects (E10), 0DTE (O3), covered calls (O2), tail hedges (O5), vol ETPs and the wheel (O6). Factor ETFs are bought, not built (E4). TAA variants are E1 robustness checks only (E2).

## Sleeve specs (condensed)

- **E1** → [[Trend-Following]]. Blend of EWMA crossovers (16/64, 32/128, 64/256) on total-return closes ÷ 36-day EWMA σ. Long/flat, inverse-vol, gross ≤ 1.0×. Rebalances weekly via MOC with a 20% no-trade buffer. Benchmark: DBMF/KMLM; if E1 can't beat them after costs, buy the ETF.
- **E5** → [[Short-Term Mean Reversion Strategy]]. Filter: close > 200-day SMA. Entry: RSI(2) < 10 or IBS < 0.2, evaluated at 15:40 ET on live prices, filled MOC. Exit: close > 5-day SMA, RSI(2) > 70, or 5 sessions. GTC stop at 3× ATR(10); 0.5% risk; ≤ 4 positions.
- **E8**. Last-30-minute variant (Gao-Han-Li-Zhou): read the rest-of-day return at 15:30 ET, enter with a marketable limit, exit MOC. Noise-area breakout (Zarattini) per companion FR-S3. Risks 0.25–0.5% of equity per trade. **Contradicted by the vault's own backtest (below).**
- **O1** → [[Volatility Risk Premium Strategy]]. Weekly 30–45 DTE XSP put spread: short leg at 20–25Δ, long leg 1–5% lower, max loss ≤ 1% of equity. Enter only when VIX/VIX3M < 1.0. Exit at 50% profit, 21 DTE, or a 2× credit mark. Summed open max loss ≤ 6%; a −20% gap must cost ≤ 8%.
- **F1/F2**: futures stay at IBKR or are replicated in ETFs ([[Micro-Futures Trend Strategy]]). Crypto enters E1 as IBIT/ETHA, capped at 10% of E1 risk.

## What changes the vault's picture

1. **No PDT limit at Schwab.** Day-trade counting ended 2026-06-08, and real-time intraday buying power arrived 2026-07-13 → [[Pattern-Day-Trader-Rule]]. That removes the old reason to run intraday index ideas through futures or a prop firm in a small account.
2. **The API cannot automate futures.** Orders return HTTP 400 "Unsupported instrument". thinkorswim conditional orders can't take external signals → [[Schwab-Trader-API]].
3. **Costs favor ETFs.** MES round trip ≈ $5.24 at Schwab (≈ 1.05 index points) vs ≈ $1.24 at IBKR. The vault's `futures_costs.py` already models Schwab at $2.62/side, so the numbers agree.
4. **No sandbox.** Paper trading becomes a shadow simulator on live Schwab quotes, then one-unit live trades.
5. **Tax placement is a design input**, not an afterthought → [[Section-1256-Contracts]], [[Wash-Sale-Rule]].

## Risk layer

- One vol-targeting layer, no financed leverage (Schwab margin ≈ 10%). Kelly capped at 0.25. Overnight net beta ≤ 0.8.
- Daily loss: −2% for the program, −1% per sleeve. Weekly −4% halves next week's sizes.
- Drawdown ladder: −10% halves sizes; −15% flattens E1/E5/E8 and stops new O1 spreads; −20% shuts the program down.
- Kill switch: API cancel-all, the mobile app, and a watchdog on a second host (90 s heartbeat). O1 spreads are not force-closed in a crisis.
- Stress test: a −7% gap costs ≤ 6% of equity across E1+E5+O1.

## Validation gates

Inherits the companion PRD's stack: trial ledger → [[Deflated-Sharpe-Ratio]] ≥ 0.95, PBO ≤ 0.20 ([[Backtest-Overfitting]]), [[Walk-Forward-Analysis]] with a 3y/6m split, [[Combinatorial-Purged-Cross-Validation]], and a single-touch holdout (Nov 2024–Oct 2026). New rules cover survivorship, auction fills (signal at 15:40, fill at the official close), OPRA option fills, borrow costs, and after-tax reporting.

| Gate | Pass condition |
|---|---|
| G1 backtest → shadow | OOS net Sharpe ≥ 0.6 at 1.5× costs (E1 ≥ 0.4); DSR ≥ 0.95; PBO ≤ 0.20; holdout ≥ 50% of WF |
| G2 shadow → one unit | ≥ 40 sessions (E8) or ≥ 3 months (daily); zero risk-check violations |
| G3 one unit → scaled | 6 mo/100 trades (E8) or 12 mo; slippage ≤ 1.25× model; tracking error ≤ ⅓ sleeve vol |
| G4 continuation | CUSUM on daily P&L: one breach halves, two halt |

Rejecting a zero Sharpe takes (1.645/SR)² years of live data, 10.8 years at SR 0.5. So G2/G3 test implementation fidelity, not whether the edge exists.

## Roadmap and cost

| Phase | Duration | Exit test |
|---|---|---|
| 0 Accounts + plumbing | 4–6 wk | Place/cancel/reconcile 1 share, an MOC, a GTC stop, and a 1-lot XSP vertical through the API; survive one 7-day token cycle |
| 1 Research | 6–10 wk | Each sleeve passes G1 or is dropped |
| 2 Shadow | 2–3 mo | G2 + two failure drills |
| 3 One-unit live | 6–12 mo | E1/E5 first, E8 after 1 clean month, O1 after 3 months |
| 4 Expansion | ongoing | Scale ≤ 2×/quarter; E6/E3; 475(f) decision |

The MVP runs ≈ $1–2.5k/yr, about a third of the futures program. That is a 2–5% hurdle at $50k and 1–2.5% at $100k. Live CME data ($199/mo) roughly doubles it, so drop ES/NQ features from E8 unless they pay.

## Contradictions with the vault

> [!contradiction] E8 is the signal the vault already killed. See [[Gamma Closing Reversal Strategy]].
> The PRD's E8 last-30-minute variant is unconditional Gao-Han-Li-Zhou momentum on SPY/QQQ. The vault's 2026-09-18 round killed it: **SPY 3 yrs −1.4 bps/trade, PF 0.82**. Low-gamma momentum also died (SPY −3.1, QQQ −3.3 bps). The one survivor runs the **opposite direction**: on high-GEX days it fades the 15:30 move (QQQ +1.8 bps, t 1.65). It still needs pre-2023 data. [[mesfin2026-mnq-intraday-falsification]] also found every OHLCV-only intraday family dead on MNQ. **Implication:** do not port E8 as written. The slot in the taxable account suits the gamma reversal traded in QQQ at Schwab's $0 commission, conditioned on GEX. It goes through G1 like any other trial.

> [!contradiction] Schwab futures history. See [[Schwab-Trader-API]].
> NFR-API-4 and FR-DATA-S2 say Schwab price history "covers equities only." The vault pulled ~7 months of /MES 5m from Schwab (2025-12 → 2026-07). It is the same stale claim flagged in [[compass2026-unified-backtester-prd-brief]]. It doesn't change the design, since research data comes from Databento anyway.

> [!contradiction] PEAD and the build order. See [[Retail Alpha Strategy Roadmap]].
> The July roadmap ranks PEAD (and LLM filings in the same small-cap universe) as build #2 and Sector-ETF momentum as build #1. The PRD benches PEAD: Martineau (2022) finds the drift gone from non-microcaps after 2001. It also grades dual-momentum/TAA rotation C (E2, variants only). The two can coexist, because the PRD excludes microcaps and the roadmap targets the under-covered small caps. **But for capital this year the PRD's order (trend, mean reversion, put spreads) has the stronger evidence and needs no fundamentals data.**

> [!contradiction] Databento "already in use"
> §9.1 lists Databento CME Standard as "already in use." As of 2026-10-13 the vault still had `DATABENTO_API_KEY` unset ([[hot]]). That key gates both the gamma-reversal validation and this PRD's Phase 1 research data.

**Internal inconsistency:** §3 E8 says "No PDT limit since June 4, 2026"; the summary and §10.1 say day-trade counting stopped on **8 June**. Use 8 June (§10.1 cites Schwab).

## Gaps

- The **companion CME micro-futures PRD** (sleeves S1–S6, FR-S3, its §4 validation stack) lives in another claude.ai conversation and is not in the vault. Ingest it next so the S-references resolve.
- Open questions from §13.3 (resolve in Phase 0 with 1-lot tests):
  - Schwab's API MOC cutoff.
  - Whether an XSP vertical goes in as one complex order.
  - Whether a refresh rolls the 7-day token window.
  - VIX/VIX3M streamer symbols.
  - The IRA/taxable capital split.
  - Keep IBKR futures in parallel, or go Schwab-only?
  - For the CPA: 475(f), VTI vs SPY "substantially identical", Hawaii treatment of 60/40, Schwab Crypto.

> [!key-insight] Start now
> The Schwab developer-app approval takes days and gates Phase 0. Applying costs nothing, so start it today. Phase 0's acceptance test (1 share, 1 MOC, 1 GTC stop, 1-lot XSP vertical, one token cycle) is the first money-path deliverable. It needs no research decisions.
