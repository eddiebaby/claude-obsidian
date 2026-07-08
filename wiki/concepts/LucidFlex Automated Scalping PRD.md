---
type: concept
title: "LucidFlex Automated Scalping PRD"
domain: quantitative-finance
complexity: intermediate
created: 2026-07-06
updated: 2026-07-06
tags:
  - strategy
  - quantitative-finance
  - futures
  - intraday
  - prop-firm
  - prd
status: seed
aliases:
  - "Lucid Flex Scalping Plan"
  - "Prop-Firm Scalping Bot PRD"
related:
  - "[[Retail Alpha Strategy Roadmap]]"
  - "[[Micro-Futures Trend Strategy]]"
  - "[[Short-Term Mean Reversion Strategy]]"
  - "[[Tick-Size-Microstructure]]"
  - "[[Overnight-Drift]]"
  - "[[Prop-Firm-Eval-Sizing]]"
  - "[[Research - Intraday Futures Strategies Under Prop-Firm Constraints]]"
  - "[[Research - Strengthening the LucidFlex Bot Plan]]"
  - "[[mesfin2026-mnq-intraday-falsification]]"
  - "[[baltussen2021-hedging-demand-intraday-momentum]]"
sources:
  - "[[kurth2026-trend-following-demise]]"
  - "[[baltussen2021-hedging-demand-intraday-momentum]]"
  - "[[busseti-ryu-boyd-2016-risk-constrained-kelly]]"
  - "[[cont2021-cross-impact-ofi]]"
  - "Gao, Han, Li & Zhou 2018 JFE — Market Intraday Momentum"
  - "Lou, Polk & Skouras 2019 JFE — A Tug of War: Overnight vs Intraday Expected Returns"
  - "Zarattini, Aziz & Barbon 2023 SSRN — Can Day Trading Really Be Profitable?"
  - "Lucca & Moench 2015 — The Pre-FOMC Announcement Drift"
  - "https://support.lucidtrading.com/en/articles/11404728-permitted-activities"
  - "https://saveonpropfirms.com/blog/lucid-trading-lucidflex-guide"
  - "https://damnpropfirms.com/prop-firms/lucid-trading-rules-payouts/"
---

# LucidFlex Automated Scalping PRD

Product requirements for an automated short-hold intraday strategy ("scalper") run on a Lucid Trading LucidFlex prop account. Track B alongside the [[Retail Alpha Strategy Roadmap]] build order — capped budget, hard gates, does not displace the sector-ETF momentum build.

## Honest Premise (read first)

**Pure tick-scalping for durable alpha at retail is a losing game.** The vault's own research says so: [[kurth2026-trend-following-demise]] shows fast strategies on small-tick, dense-order-book contracts (exactly MES/MNQ) stopped working post-2009 — queue position and latency belong to HFT firms. See [[Micro-Futures Trend Strategy]] ("build slow only") and [[Short-Term Mean Reversion Strategy]] (capacity-constrained by design).

**What makes this plan viable anyway is the payoff structure, not the alpha.** A LucidFlex eval costs $130 (50K tier). Passing yields a funded account with 90% profit split and downside capped at the eval fee. The bot does not need institutional-grade edge — it needs *modest positive expectancy after costs* plus risk management tuned precisely to Lucid's rule set. The eval fee is an option premium; the strategy is the exercise mechanism.

**Definition discipline:** "scalping" (tier 1) here means short-hold intraday trading — holds of 1–30 minutes, targets of 8–16 ticks — NOT sub-minute tick-scalping. Sub-2-tick systems die to costs (see Cost Model) and risk Lucid's HFT-detection ban. The menu also carries a tier 2 of higher-timeframe intraday families (hours-long holds, still flat by close) — slower is *better* under the cost model and the vault's turnover thesis.

## LucidFlex Rules That Drive the Design

Verified 2026-07-06 from third-party guides + Lucid help center. **Phase 0 must re-verify every number against official docs — third-party sources already disagree (5 vs 6 payouts), and prop firms change rules without notice.**

| Rule | Value (50K tier) | Design consequence |
|---|---|---|
| Eval fee | $130/mo (discounts common) | Cheap option; budget N attempts |
| Profit target (eval) | $3,000 | ~15–20 green days at modest pace |
| Max Loss Limit (MLL) | $2,000, EOD trailing | This is the real account size. Risk budget = $2,000 |
| MLL mechanics | Updates only at 4:45pm ET close; locks at initial MLL + $100 once balance exceeds start + $100 | Intraday dips don't ratchet the trail; breach still fails (verify intraday-touch rule in Phase 0) |
| Daily loss limit | None | Must self-impose one — the bot's, not the firm's |
| Consistency (eval only) | Largest day ≤ 50% of total profit | Cap daily profit in eval; removed once funded |
| Contract cap (50K) | 2–4 minis / 20–40 micros, scales EOD | Sizing ceiling; start micros |
| Automation | Bots, EAs, API strategies, copiers explicitly allowed, no approval needed | The whole plan is permitted |
| HFT | Prohibited; automated detection; profits removable | Rate-limit the bot (see Guardrails) |
| Payouts | 90/10 split; 5 days ≥ $150 profit per cycle; min $500, max 50% of balance (capped); 5–6 payouts then moved live | Optimize for consistent small green days, extract early and often |
| Overnight / weekend holds | Prohibited — flat by 4:45pm ET; open positions auto-flattened (no breach) | Intraday-only strategy menu; all swing/multi-day families excluded until LucidLive |
| News events (NFP/FOMC/CPI) | Explicitly allowed, algos included, no blackout windows | Event sleeve is legal — but highest slippage, deploy last |
| Activation fee | $0 | — |
| Malfunctions | Trader owns all software errors | Kill-switch is a hard requirement |

**Recommended vehicle: $50K tier.** The $25K's $1,000 MLL is too thin for any statistical strategy to breathe; $100K+ raises fee burn without changing the game.

## Goals / Non-Goals

**Goals**
1. Backtest the full rule-compatible menu (tier 1 families 1–6, tier 2 families 9–12) in one harness; ship the top 1–2 sleeves with positive net expectancy after costs, verified out-of-sample before a single eval dollar is spent.
2. Pass one LucidFlex 50K eval inside 5 attempts.
3. Extract ≥ 2 funded payouts (≥ $1,000 net) — that is the success bar for the whole track.

**Non-Goals**
- Not building an HFT system. Not competing on latency, ever.
- Not a strategy intended to scale on own capital — this edge class is prop-structure-specific.
- Not a replacement for the [[Retail Alpha Strategy Roadmap]] build order.

## Rule-Compatible Strategy Menu

Every family that survives the rule set: intraday-only (flat by 4:45pm ET), non-HFT (holds ≥ 60s), gross target that clears the cost model, automatable with defined per-trade risk. All on MES/MNQ (micros; ES/NQ minis when funded). Two tiers: **tier 1** = short-hold (minutes), **tier 2** = higher-timeframe intraday (hours, up to full session).

| # | Family | Mechanism | Hold | Trades/day | Notes |
|---|---|---|---|---|---|
| 1 | **Opening-range breakout (ORB)** | Break of first 5–30 min range in trend direction, range-based stop | 5–60 min | 1–3 | Best-documented intraday edge (Zarattini/Aziz 2023); the momentum anchor |
| 2 | **VWAP-stretch mean reversion** | Fade extensions ≥ Nσ / N×ATR from VWAP, target VWAP | 5–30 min | 3–10 | Frequent small wins → ideal for payout-day cadence; hard stop mandatory (MR losers are fat-tailed). Cousin of [[Short-Term Mean Reversion Strategy]] |
| 3 | **Prior-level reactions** | Fade or break at overnight H/L, prior-day H/L/close, settlement, round numbers | 5–45 min | 2–6 | Clean invalidation (the level); rules fully mechanical |
| 4 | **Opening gap fade/continuation** | Trade gap-fill stats conditioned on gap size vs prior range | 15–120 min | 0–1 | One decision/day; very low frequency, strong consistency profile |
| 5 | **Intraday trend pullback** | Trend-day filter (price vs rising VWAP), buy pullbacks to EMA/VWAP, exit by close | 15–90 min | 1–4 | Complement to ORB; catches the day ORB misses |
| 6 | **Range-day midday fade** | Range-day detection (failed open drive) → fade Keltner/Bollinger extremes 12:00–14:30 | 10–45 min | 2–5 | Regime complement to 5: trend-day vs range-day playbooks |
| 7 | **Scheduled-news momentum (NFP/FOMC/CPI)** | Enter on 1-min post-release impulse direction, ride 5–30 min | 5–30 min | 0–2/mo | Explicitly permitted by Lucid, no blackout. Highest slippage (model 2–4 ticks) and single-day P&L spikes threaten the eval consistency cap — funded-phase only |
| 8 | **Time-of-day overlays** | Last-hour momentum (15:00–16:00 imbalance drift), lunch-chop block (12:00–13:30) | overlay | — | Not standalone; filters applied to families 1–6 |

**Tier 2 — higher-timeframe intraday.** The flat-by-4:45pm rule kills *overnight* holds, not *long* holds: anything opened and closed inside the trading day is legal, up to full-session (~6.5h RTH) positions. Fewer, bigger trades — cost drag shrinks relative to target (2–3 tick costs against a 50–150 tick session move), which is the vault's own turnover thesis working in our favor.

| # | Family | Mechanism | Hold | Trades/day | Notes |
|---|---|---|---|---|---|
| 9 | **Open-to-close session momentum** | Daily signal (prior-day return sign, gap direction, price vs 20/50-day MA) sets direction; enter near open, hold to 4:15pm flat | ~6.5 h | 0–1 | Intraday time-series momentum; the "slow" anchor of the book |
| 10 | **Intraday momentum (rest-of-day → last 30 min)** | Rest-of-day return predicts the last 30-min direction; trade the 15:15–15:45 window (before 4:15 hard-flat) | 30 min | 0–1 | Gao–Han–Li–Zhou 2018 pattern + **peer-reviewed mechanism** [[baltussen2021-hedging-demand-intraday-momentum]] (dealer gamma hedging + leveraged-ETF rebalancing, 60+ futures, 46 yrs). See #14 for the conditioned version |
| 14 | **Gamma-conditioned intraday momentum** | Family #10 filtered by a dealer-gamma-exposure proxy: take the signal only when dealers are short gamma (must hedge with the move) | 30 min | 0–1 | The Baltussen mechanism made explicit. Gamma exposure is NOT in OHLCV bars → outside [[mesfin2026-mnq-intraday-falsification]]'s falsification scope. The single most promising *new* sleeve from the 2026-07 sweep |
| 11 | **Trend-day capture** | Daily-bar setups (NR7, inside day, gap-and-go) flag trend days; ride with ATR trailing stop all session | 2–6.5 h | 0–1 | The higher-timeframe sibling of #5; one fat winner pays for several scratches |
| 12 | **Daily mean-reversion, expressed intraday** | Yesterday closed oversold (RSI(2)-style) → long at open, exit at close | ~6.5 h | 0–1 | HONEST CAVEAT: much of short-term MR payoff historically accrues overnight, which this structurally cannot capture — backtest before trusting, expect a weakened edge |
| 13 | **Globex overnight-session drift** ⚠ CONDITIONAL | Overnight equity premium: long 6pm → 9:30am (or → next 4:45pm close) | 15–22 h | 0–1 | The well-documented overnight-drift anomaly — but third-party sources contradict each other on whether a position opened 8pm can be held past midnight to the next day's close. **Phase 0 must get this in writing from Lucid support before this family exists** |

**Tier-2 sizing note:** session-length holds need ATR-scale stops (0.3–0.6× daily ATR ≈ 30–60 MES points = $150–300/contract), so tier-2 risk budget is ≤ $150/trade at 1–2 micros, ≤ 2 tier-2 entries/day. Tier-2 sleeves produce fewer but larger green days — fine for the $150 payout-day threshold, but in eval a trend-day winner can threaten the 50% consistency cap, so the profit-cap logic must also flatten tier-2 positions.

**Excluded by rule or by reality:**
- Swing / multi-day / slow trend — flat-by-4:45pm rule kills them; revisit on LucidLive after payout #5–6
- Sub-minute tick scalping, order-book/queue strategies — HFT ban + no retail queue edge (the Kurth result)
- Cross-market lead-lag latency plays (NQ→ES) — a latency game; HFT-detection risk for zero retail edge

## Evidence Ranking — what actually has documented edge

Rule-legal is not the same as works. Grading the menu by the quality of evidence that the edge exists at all, because the build order should follow evidence, not convenience:

| Grade | Family | Evidence | Post-publication caveat |
|---|---|---|---|
| **A (mechanism-backed)** | #10 / #14 Intraday momentum, rest-of-day → last 30 min | Gao-Han-Li-Zhou 2018 JFE (pattern) **+ [[baltussen2021-hedging-demand-intraday-momentum]] JFE 2021 (mechanism: dealer gamma + leveraged-ETF hedging, 60+ futures, 1974–2020)** | Upgraded from "fragile": the mechanism explains why Mesfin's *unconditioned* OHLCV momentum failed while the flow-conditioned version can survive (gamma exposure isn't in OHLCV). #14 tests the conditioned form. Residual risk: LucidFlex 4:15 hard-flat truncates the last-30-min window — may need the 3:15–3:45 window |
| **A (conditional)** | #13 Globex overnight drift | [[Overnight-Drift]]: Cooper-Cliff-Gulen 2008; Lou-Polk-Skouras 2019 JFE; [[glasserman2025-overnight-news]] (30 yrs, news-linked); [[boyarchenko-larsen-whelan-overnight-drift]] (ES-specific dealer-inventory mechanism — drift concentrates around the European open, so a partial-night hold may capture most of it) | Only exists if Phase 0 confirms the hold is legal; index-level version robust, cross-sectional version decaying post-2015; post-2020 ES magnitude unverified — measure in Phase 1 |
| **A−** | #7 Scheduled-news momentum | Macro-announcement premia literature (Savor & Wilson 2013; Lucca & Moench 2015 pre-FOMC drift) — announcement days carry outsized, directionally persistent returns | Pre-FOMC drift specifically decayed post-publication; post-release surprise continuation holds up better; funded-only regardless (slippage + consistency cap) |
| **C (downgraded from B)** | #1 Opening-range breakout | Zarattini, Aziz & Barbon 2023/24 SSRN — QQQ net-positive; BUT [[mesfin2026-mnq-intraday-falsification]] falsifies ORB in every entry variant on 5-min MNQ 2021–25 with realistic costs | Direct falsification on our instrument outweighs the ETF-based positive; contradiction logged in [[Research - Intraday Futures Strategies Under Prop-Firm Constraints]]; Phase 1 adjudicates |
| **B** | #9 Open-to-close session momentum | Intraday time-series momentum literature (extensions of Moskowitz-Ooi-Pedersen to intraday horizons) | Regime-dependent; needs the trend-day filter to avoid chop bleed |
| **C− (presumed dead)** | #2 VWAP-stretch MR, #3 prior-level reactions, #4 gap fade, #5 trend pullback, #6 range-day fade, #11 trend-day capture | Practitioner folklore — and [[mesfin2026-mnq-intraday-falsification]] tested the gap, volume, level/liquidity-grab, and volatility-conditioned families on MNQ 2021–25: all fail net of costs (gross edge 0.07–1.5 pts vs ~2-pt costs) | No longer merely unevidenced — falsified as a class on this instrument. Harness time only to confirm the null cheaply |

**Build order consequence:** Phase 1 pre-registers and tests in evidence order — #13 overnight drift (if Phase 0 clears it) and #10 first-half-hour momentum first, then #9 session momentum (the sole surviving B), #7 for the funded phase. ORB and all other tier-1 OHLCV families are now confirm-the-null work only. The 2026-07 arXiv sweep ([[Research - Intraday Futures Strategies Under Prop-Firm Constraints]]) hardened this: four independent falsifications of fast bar-level edges post-2009 (Kurth, Byrd-Balch, Mesfin, decay literature), while the only robust documented effects are the slow structural ones — overnight decomposition and announcement-day dynamics. The evidence says the durable edges are slow; the eval-fee asymmetry remains the only reason to run intraday at all.

**Portfolio logic:** the payout rule (5 separate green days ≥ $150) and eval consistency cap reward *smooth daily P&L over big days*. So the target state is 2–3 uncorrelated sleeves — one tier-1 momentum (1 or 5), one tier-1 mean-reversion (2, 3, or 6), one tier-2 slow sleeve (9–12) for the low-turnover ballast, optionally the event sleeve (7) once funded — on one harness with a shared risk supervisor, daily stop, and profit cap. Tier-1 and tier-2 sleeves are natural diversifiers: minutes-scale and session-scale P&L are nearly uncorrelated by construction. Eval runs the best 1–2 only; sleeves get added funded, one at a time.

## Common Spec (applies to every sleeve)

| Parameter | Value |
|---|---|
| Instruments | MES, MNQ (micros; graduate to ES/NQ minis when funded — minis cost ~0.3 ticks RT vs ~1 tick on micros, per unit exposure) |
| Session | 9:30–16:00 ET per-sleeve windows; hard flat by 4:15pm ET (30-min buffer before Lucid's 4:45 cutoff) |
| Hold time | Per sleeve table — tier 1: 1–120 min; tier 2: up to full session, hard flat 4:15pm |
| Stop | Hard stop every trade, in the engine AND resting at the exchange — tier 1: 6–10 ticks; tier 2: 0.3–0.6× daily ATR |
| Target | Tier 1: 8–16 ticks or time-stop, R:R ≥ 1.2; tier 2: trail or session close |
| Risk per trade | **Risk-constrained Kelly** ([[Prop-Firm-Eval-Sizing]]): solve max growth s.t. P(hit MLL) < β from the backtested per-trade distribution. Caps below are the pre-Phase-1 placeholders until that distribution exists — tier 1 ≤ $100 (5% of MLL); tier 2 ≤ $150 (7.5% of MLL), ≤ 2 tier-2 entries/day |
| Self-imposed daily stop | −$300 (15% of MLL) → all sleeves flat + disabled until next session |
| Daily profit cap (eval only) | +$600 → stop trading (keeps largest day ≤ 50% rule safe at 20% of target) |
| Trade frequency | ≤ 20 trades/day across all sleeves |

## Guardrails (HFT-ban + malfunction safety)

- Minimum hold ≥ 60s, minimum 30s between entries, no order-spam (cancel/replace ≤ 1/sec). Stays far from any HFT-detection boundary.
- Independent risk-supervisor process (separate from signal engine): monitors position vs. expected state, P&L vs. daily stop, and connectivity; any mismatch → flatten + halt + alert.
- Distance-to-MLL throttle: when equity − MLL < $600, cut size 50%; < $400, halt for the day.
- Every order and fill logged; daily reconciliation vs. platform statement.
- **OFI execution layer** (optional, Phase 4+): once a sleeve has triggered, use order-flow-imbalance from the L2 feed to time the actual entry/exit within seconds and shave slippage. OFI decays too fast to be a *signal* at 1–30 min ([[cont2021-cross-impact-ofi]]) but recovering ~½ tick/side directly improves net expectancy against the cost model. Requires Rithmic/Tradovate depth data — Phase 0 platform question.

## Cost Model (the gate everything hangs on)

| Item | MES (per RT) | In ticks ($1.25) |
|---|---|---|
| Commission + exchange + NFA | ~$1.00–1.40 | ~1 tick |
| Spread/slippage (market or marketable-limit, liquid hours) | 1–2 ticks | 1–2 ticks |
| **All-in cost per round turn** | | **~2–3 ticks** |

Therefore: **gross edge must be ≥ 4–5 ticks/trade for net ≥ 2 ticks.** Any backtest showing profits on sub-4-tick average wins is measuring noise. This single number is why "scalping" must mean 8–16 tick targets, not 1–2.

## Build Phases & Gates

**Phase 0 — Verify (3–5 days, $0)**
Re-verify all rules on official Lucid docs/support: intraday MLL touch, current pricing, payout count, max accounts per trader, copier policy, **supported platforms/API path** (NinjaTrader ATS vs Tradovate API vs Rithmic R|API — this decides the execution stack), and **in writing from support: can a Globex position opened after 6pm ET be held through the night to the next day's 4:45pm close?** (Third-party sources contradict each other; the answer gates family #13.) GATE: rules still compatible with this PRD.

**Phase 1 — Data + Backtest (2–4 weeks, ~$100–200)**
Databento 1-min + tick MES/MNQ, 4+ years. Backtest in EVIDENCE ORDER (see Evidence Ranking): A-grades first (#14 gamma-conditioned intraday momentum + #10 base; #13 overnight drift if Phase 0 clears it), then B (#9 session momentum), C families only if A/B yields fewer than 2 shippable sleeves. ONE event-driven harness (Python) with the full cost model — pre-registered parameter grid per family, walk-forward, deflated Sharpe across ALL families tested (every family tried adds trials; the DSR haircut applies to the menu, not each family alone — [[Deflated-Sharpe-Ratio]]). Rank by net expectancy × out-of-sample robustness; ship the top 1–2 with pairwise daily-P&L correlation < 0.3. GATE (per shipped sleeve): net expectancy ≥ 2 ticks/trade AND profit factor ≥ 1.3 out-of-sample AND combined max sim drawdown ≤ 60% of MLL under eval sizing. The backtest also produces the per-trade return distribution that feeds risk-constrained Kelly sizing ([[Prop-Firm-Eval-Sizing]]). No family passes → kill the track, spend $0 on evals.

**Phase 2 — Sim (4 weeks, $0)**
Run the bot live-sim on the execution platform with eval rules simulated (MLL, daily stop, profit cap). GATE: ≥ 20 trading days, positive P&L, slippage within 1 tick of backtest assumption, zero guardrail breaches.

**Phase 3 — Eval (budget: 5 × $130 = $650 max)**
Same bot, zero parameter changes. Expected pass pace: $150–300/day → target in 3–5 weeks. GATE: pass within 5 attempts; 3 attempts failed by MLL breach (not variance at breakeven) → halt and return to Phase 1.

**Phase 4 — Funded**
First 10 days at half size until MLL locks at breakeven + $100 — after the lock, downside to Lucid is gone and size normalizes. Request payout the moment 5 × $150 days + $500 min are met. Extract every cycle; never bank a balance with a prop firm (counterparty risk).

**Phase 5 — Scale (only after 2 payouts)**
Copier to additional LucidFlex accounts (permitted; verify account cap), minis instead of micros, add the next-ranked menu sleeve (including the event sleeve #7, funded-only), or park the strategy and feed profits to the main roadmap. LucidLive (post payout 5–6) reopens overnight holds → the excluded swing families become legal there.

## Budget & Timebox

Total cap **$1,000** (data ~$200 + eval fees ≤ $650 + buffer) and **16 weeks** Phase 0 → first payout. Hit either cap without a payout → track closes, post-mortem filed, capital and attention return to [[Sector-ETF Momentum Strategy]].

**Eval-as-sizing decision (the go/no-go math).** Before Phase 3, Monte Carlo the full eval as a system (target + MLL + consistency cap + daily stop) using the Phase 1 distribution to get per-attempt pass probability `p`. Expected eval spend to funding = $130 / p. If that exceeds the value of ~2 payouts (~$1,000), the strategy is not worth running *even if its edge is real* — a genuine-but-small edge with p ≈ 0.15 costs ~$870 in expected fees before the first funded dollar. This is the number that decides whether to spend eval money at all, and it only exists after Phase 1.

## Risks & Failure Modes

- **The edge doesn't exist.** Most likely outcome; that is what the Phase 1 gate is for. The eval fee asymmetry only pays if the bot is genuinely +EV — a −EV bot on 5 evals just donates $650.
- **Rule changes / firm risk.** Prop firms alter rules retroactively and can fail entirely (industry precedent: multiple 2024–25 firm collapses). Mitigation: extract payouts immediately, never treat the funded balance as savings.
- **HFT false-positive.** Automated detection could flag a legitimate bot; frequency guardrails are set well inside the boundary, but keep logs to contest.
- **Sim-to-live slippage gap.** Rithmic/Tradovate fills ≠ backtest fills; Phase 2 exists to measure this before it costs eval fees.
- **Consistency-rule breach by a runaway winner day** in eval — the profit cap must be enforced in code, not discipline.
- **Attention drain.** This is the lottery-ticket track. The roadmap strategies are the compounding track. Timebox is a hard rule.

## Related Strategies / Concepts

- [[Retail Alpha Strategy Roadmap]] — build order this slots under (Track B)
- [[Micro-Futures Trend Strategy]] — the slow-only constraint this PRD deliberately works around via prop structure
- [[Short-Term Mean Reversion Strategy]] — signal-family cousin (VWAP-stretch variant)
- [[Tick-Size-Microstructure]] — why sub-4-tick edges are noise
- [[Overnight-Drift]] — the structural basis for family #13
- [[Prop-Firm-Eval-Sizing]] — risk-constrained Kelly + the eval-as-sizing go/no-go math
- [[Research - Intraday Futures Strategies Under Prop-Firm Constraints]] — what was falsified
- [[Research - Strengthening the LucidFlex Bot Plan]] — what upgrades survived (this sweep)

## Status

- [ ] Phase 0: rules + platform verified against official docs
- [ ] Phase 1: backtest clears expectancy gate
- [ ] Phase 2: 20-day sim clears
- [ ] Phase 3: eval passed
- [ ] Phase 4: first payout
- [ ] Phase 5: scaled or closed
