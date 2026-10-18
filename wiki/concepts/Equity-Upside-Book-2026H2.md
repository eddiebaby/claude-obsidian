---
type: concept
title: "Equity Upside Book — 2026 H2 (SPX + R2000 + Nasdaq)"
created: 2026-07-08
updated: 2026-10-13
domain: quantitative-finance
address: c-000029
complexity: intermediate
tags:
  - strategy
  - quantitative-finance
  - equity
  - position
  - idea-book
status: seed
related:
  - "[[Retail Alpha Strategy Roadmap]]"
  - "[[Index Rebalance and Event-Driven Strategy]]"
  - "[[Deflated-Sharpe-Ratio]]"
  - "[[ClaudeDevs-Getting-Started-with-Loops]]"
  - "[[Upside-Screen-2026-07]]"
  - "[[Equity-Book-Sweep-2026-10-13]]"
sources:
  - "web research 2026-07-08 (Schwab/Fidelity mid-year outlooks, MarketWatch H1 losers, TIKR, William Blair, Motley Fool bank M&A, company 8-Ks)"
---

# Equity Upside Book — 2026 H2 (SPX + R2000 + Nasdaq)

Hedge-fund-analyst exercise, 2026-07-08. Question: highest 12-24 month upside in the S&P 500 and Russell 2000. All price targets are sourced consensus/analyst figures from web research, **not verified against a terminal** — verify before any position.

Broad candidate layer (20 tickers per universe, tiered A/B/C): [[Upside-Screen-2026-07]] (2026-07-09).

## Market frame (as of 2026-07-08)

- SPX ~7,537 (ATH 7,621). Earnings-driven bull, but leadership narrow: AI + energy. FY26 SPX EPS growth estimate 25%, concentrated in a handful of names. Strategist warnings of "extreme speculation" in high-multiple names; one YE target at 7,100 (below market).
- Fed at 3.50-3.75%; further cuts fading on sticky inflation.
- R2000 +21% YTD — best start since 1991. Small-cap FY26 EPS growth consensus rose 23% → 38%. Bank M&A at 7-year high ($15.1B H1); biotech M&A $106B by June (strongest since 2019).
- Key R2000 risk: interest expense = 31% of EBITDA (6-yr high). Favor low-leverage names; the floating-rate trap is real if cuts stall.

> [!contradiction] Fed pivot vs the small-cap tailwind (updated 2026-07-29)
> Original callout: on **2026-06-17 the Fed held at 3.50-3.75% but signalled a likely 2026 HIKE** (first meeting under new Chair Kevin Warsh — dot plot flipped, 9 of 18 participants projecting a 2026 hike, easing bias stripped from the statement). **July 29 FOMC: held again at 3.50-3.75% (5th straight hold), but 3 of 12 voters (Hammack, Kashkari, Logan) dissented FOR a 25bp hike** — statement language essentially unchanged, no new SEP/dot plot at this meeting, Warsh's tone read as "hawkish-hold" but not an escalation beyond June's signal. **Verdict: signal held steady, did not escalate further** — the 2026-hike threat from June is confirmed live (3 hawkish dissents is unusually high) but not intensified today. Book-level threat to the R2000 sleeve stands unchanged: at 31% interest/EBITDA, BofA estimates every 25bp hike costs ~2% R2000 operating earnings. Market reaction was not read-through-negative for small caps: Dow -1,100pts (-2.2%), SPX -1.5%, Nasdaq -1.7% on the broad hawkish reaction, but **IWM/R2000 was flat/slightly green (+0.08%)** — relative resilience vs large caps, not confirmation the rate threat is defused. Standing response unchanged: R2000 picks must stay M&A/idiosyncratic-catalyst driven (SFNC takeout, OMCL bookings, biotech basket), never rate-beta. **Flag all four R2000 names (OMCL, SFNC, XENE, FRPT) for re-review at the next weekly sweep** given the elevated dissent count.

## Core insight

The most asymmetric 12-24mo upside is NOT in the AI-momentum winners (that's where snapback risk lives — MU +242% YTD). It's in two pockets:

1. **The AI-roadkill derating (SPX).** H1's worst performers weren't earnings misses — they were quality software derated on AI-disruption *narrative* while fundamentals grew (Intuit -51% with EPS +12%). Double engine if fear proves early: EPS growth × multiple re-rate. JPM private bank: full agentic replacement of enterprise software is "post-2028 at the earliest."
2. **M&A gravity (R2000).** Bank consolidation at 7-yr highs plus the biggest biotech M&A year since 2019 puts a takeout floor + call option under quality small-caps in those sectors.

## S&P 500 book

| # | Name | Setup | 12-24mo upside (sourced) | Falsifier |
|---|------|-------|--------------------------|-----------|
| 1 | ~~**INTU** Intuit~~ **REMOVED (2026-09-21 sweep)** | -51% YTD, worst in SPX; 15.9x P/E vs 30-40x historical; FY26 EPS +12% to $17.23; TT Live rev +36%, QBO accounting +22% | Falsifier fired: FY27 guide (8/25) = TurboTax +2-3% vs Street 6.8%, share erosion to AI tax rivals; stock -11% to ~$318; JPM/BofA/Goldman downgrades. Post-mortem: derating was not purely narrative — TurboTax was the real exposure. Re-entry: TurboTax growth back >5% or evidence share loss stopped (Q2 FY27 / 2027 tax season) | TurboTax unit declines or FY27 guide showing real share loss to AI-native competitors |
| 2 | **ADBE** Adobe | Same derating trade, second unit; ~cut in half; fair-value upside ~57% cited | ~+50-57% | Creative Cloud net-adds turning negative; Firefly failing to monetize |
| 3 | **CMCSA** Comcast | Deep value, Buy consensus; churn stabilization + margin stabilization scenario | +50% scenario cited | Broadband sub losses accelerating past current run-rate |
| 4 | **NVDA** Nvidia | The "cheap quality" AI leg: 30.6x P/E = less than half its 10-yr average; EPS growth expected 2026 + 2027 | Moderate (consensus, not a re-rate story) | AI capex cycle rolling over (hyperscaler capex guides) |
| 5 | **NEM** Newmont | Book hedge: gold miner, ~48% fair-value upside cited; pairs against the AI-snapback tail | +48% cited | Gold breaking down / cost inflation resuming |

## Russell 2000 book

| # | Name | Setup | 12-24mo upside (sourced) | Falsifier |
|---|------|-------|--------------------------|-----------|
| 1 | ~~**SPRY** ARS Pharma~~ **REMOVED (loop 2)** | neffy ramp was real (Q1 product rev $17.5M vs $7.8M) BUT the CVS Caremark catalyst **failed**: zero new commercial formulary adds in the 7/1 cycle, disclosed 6/24, stock −23% AH to ~$8; securities-fraud investigations opened into management's coverage claims | Kill switch fired | — |
| 2 | **OMCL** Omnicell | Titan XT + OmniSphere upgrade cycle; bookings H2-weighted; FY26 EPS guide raised 8.6% to $1.80-2.00 | Consensus PT $54 = +16%; BofA bull $70 = +77% | Titan XT bookings not converting by Q4 (capital-approval cycle stalling) |
| 3 | **SFNC** Simmons First | Regional-bank consolidation at 7-yr high; named next-in-line takeout candidate; middle-market lending franchise | Takeout premium + sector re-rate | Regulatory window closing after midterms with no bid |
| 4 | **XENE** Xenon Pharma | William Blair 2026 top-5 biotech pick; epilepsy program (azetukalner) with late-stage readouts; buyout optionality | Binary-heavy; basket with KRYS/~~TERN~~/SPRY (TERN acquired by Merck 2026-05-05 — see 10/13 sweep) | Trial miss — this is the tail-risk leg of the basket |
| 5 | **FRPT** Freshpet **— not an R2000 member (Russell 1000 per iShares holdings 10/12; reclassify, 10/13 sweep)** | TD Cowen $80 PT = +50%; premium pet-food volume share 2.7% and growing; growth-at-a-reasonable-price after derating | +50% (single-analyst) | Volume share stalling; **verify current R2000 membership** (borderline small/mid) |

## Loop 2 — Re-underwriting from primary sources (2026-07-08, same session)

Goal-based loop: re-underwrite top-3 conviction names from filings; stop when each has a unit-economics read and a yes/no verdict.

### INTU — verdict: YES (thesis survives primary contact)

Q3 FY26 8-K/press release (5/20): rev $8.56B **+10.4%** (beat), non-GAAP EPS $12.80 vs $11.65; FY26 guide **raised** to $21.34-21.37B (+13-14%), non-GAAP op income +16%; segment guides raised (GBS ~+16%, Consumer ~+10%); QBO accounting +22%. Cash+investments $6.8B vs debt $6.2B ≈ neutral. At $388 ≈ **~17x forward non-GAAP** vs 30-40x historical. The falsifier (unit declines / share loss) is NOT visible in primary data — every segment growing double digits with a raised guide. Next test: FY27 guide at the late-Aug FY26 report. 17% workforce cut = margin lever if revenue holds.

### SPRY — verdict: NO (kill switch fired; remove to watchlist)

Q1 8-K (5/15): product rev $17.5M vs $7.8M (+125%) — the ramp was real. But: SG&A $72.2M/qtr vs $17.5M product revenue; net loss $60.6M/qtr; cash+ST investments **$201.0M** (down ~$44M in Q1) vs term loans $96.5M + financing liability $74.7M; equity down to $61M. Management's "funded through cash-flow break-even" claim depended on the CVS Caremark formulary win. **On 6/24 the company disclosed zero new commercial formulary additions for the 7/1 cycle — stock −23% AH to ~$8 (52-wk range $6.66-18.63), and Levi & Korsinsky / Schall opened securities investigations** into the CEO's prior "80% coverage by early summer" statements. Without formulary access, the burn math implies a raise (~4-5 quarters of cash at Q1 consumption) → dilution risk on impaired credibility. Watchlist triggers to re-enter: Q2 script trend without formulary support, a real payor win, or the Q4 2026 CSU Phase 2b interim.

### OMCL — verdict: YES, qualified (thesis intact, upside case more modest than the bull PT)

Q1 8-K (4/28): rev $309.9M **+15%** (product +20%), GAAP net income $11M vs −$7M y/y, non-GAAP EPS $0.55 vs $0.26, EBITDA $45M vs $24M, OCF $55M. FY26 guide **raised**: EBITDA $153-168M, EPS $1.80-2.00; bookings $510-560M; ARR $680-700M. Balance sheet: $239M cash vs $168M debt = net cash. At ~$45 ≈ **~23-25x forward EPS, ~12-13x EV/EBITDA**. First Titan XT orders booked on plan; hardware ships H2, OmniSphere H1-27. Wrinkle from the call: internal contradiction on whether Titan XT is cannibalizing XTExtend interest — watch the bookings number, not the EPS. Consensus +16% is the base case; BofA's $70 (+77%) requires the H2 bookings inflection to print.

**Loop lesson (encoded per [[Claude Code Loop Taxonomy]] rule 4):** the SPRY entry was filed with a *stale* catalyst — the "CVS eff. 7/1" line came from a May article; the rejection had already been disclosed on 6/24, two weeks before filing. **New standing rule for this book: any catalyst with a date already in the past at filing/review time must be re-verified against primary/latest news before it counts.**

## Nasdaq extension (added 2026-07-08, same session)

Universe: all Nasdaq-listed. Carryovers from the books above that are Nasdaq-listed: INTU, ADBE, NVDA, SPRY, XENE, OMCL, FRPT. Context: Composite +11% YTD but pulling back since 6/5 on the chip selloff; memory is parabolic (MU +248%, SNDK +736% YTD) — that is the snapback pocket, not the upside pocket. New dislocation: even Mag-7 quality has derated on AI-capex skepticism + the hawkish Fed.

| # | Name | Setup | 12-24mo upside (sourced) | Falsifier |
|---|------|-------|--------------------------|-----------|
| 1 | **MSFT** Microsoft | Down ~19% YTD, ~30% below 52-wk high; consensus PT $561 | **+44%** | Azure AI revenue decelerating two straight quarters |
| 2 | **META** Meta | Widest consensus gap in big tech: PT $841 | **+44%** | Ad market rollover or capex guide up w/o revenue |
| 3 | **MELI** MercadoLibre | ~47% EPS growth next 12mo; LatAm e-comm/fintech compounder; PT $2,255 | **+28%** | Take-rate compression, credit-book deterioration |
| 4 | **PLTR** Palantir | -20-27% YTD after multiyear run; $143 vs median PT $200; rev growth ~85%, Rule of 40 ≈ 145%; still expensive — speculative leg | **+40%** to median | US gov/commercial bookings decelerating; multiple still un-anchored |
| 5 | **INTC** Intel | Deep turnaround: ~$110 after -21% week; server CPU estimates RAISED (25% '26, 30% '27); Druckenmiller new position Q1; HSBC $200 vs BofA "bubble"; 18A yields the swing factor; catalyst 7/23 earnings | Bull ~**+80%** (HSBC); wide distribution | 18A external yield slip to 2027+; foundry losses widening past $2.4B/qtr run-rate |
| 6 | **S** SentinelOne | Cybersecurity mid-cap; median PT $20.50 | **+48%** | Net-new ARR decel vs CRWD/PANW consolidation |

Anti-pick: MU/SNDK memory parabola — up 248%/736% YTD; the article's own framing ("speculation extreme, snapback precedent") applies here first.

## Construction & discipline

- Barbell: 60% derated-quality (INTU/ADBE/MSFT/META/CMCSA/OMCL) / 25% M&A-optionality + turnarounds (SFNC, biotech basket ex-SPRY, INTC small) / 15% hedge (NEM). NVDA as core beta only if net exposure needs it. PLTR and INTC are the speculative sleeve — size both together below any single quality name. SPRY removed to watchlist (loop 2).
- Biotech = basket, never single-name sized (binary risk). SPRY the largest of the basket because it's commercial-stage, not binary.
- Everything here is a *hypothesis* — per [[Deflated-Sharpe-Ratio]] discipline, sourced analyst PTs are marketing until re-underwritten. Next step per name: pull filings, build the unit-economics model, check short interest / positioning.
- Falsifiers are pre-committed above. If the falsifier fires, the position exits — no thesis drift.

## Loop log

### 2026-09-21 sweep (web-sourced, unverified; PTs not terminal-checked)

**Macro:** the Fed **HIKED 25bp on 2026-09-16** (unanimous, Warsh; another hike signalled). The June/July "hike threat" contradiction callout has now materialised. R2000 -1.29% on the day. R2000 sleeve rule (catalyst-driven, never rate-beta) stands; every R2000 name is exposed to the 31% interest/EBITDA trap.

- **INTU — KILLED.** FY27 guide 8/25: rev +9-10% (Street 10.8%), TurboTax +2-3% vs 6.8% expected, AI tax rivals (Perplexity Tax, Chime Tax etc.) named; -11%, JPM ($605→$331)/BofA/Goldman downgrades. Pre-committed falsifier ("FY27 guide showing real share loss to AI-native competitors") counted as fired. Judgment call: company-wide EPS guide still +23% (methodology change now includes SBC), so this is a borderline kill; rule = no thesis drift. Moved to watchlist.
- ADBE — intact. Q3 rev $6.76B +13%, FY guide raised, ARR $27.5B; Q4 guide below consensus; CEO transition 12/1 (Chakravarthy). Falsifier not fired.
- CMCSA — intact/soft. Q2 beat, broadband losses -167k (improved y/y), wireless record, Peacock profitable; stock -5% on outlook.
- NVDA — intact. FQ2 (8/26): next-qtr guide $108B vs $104B expected, hyperscaler capex $1.3T next yr; no China DC in outlook. Capex falsifier not close.
- NEM — intact. Record Q2 FCF $2.2B, realised gold $4,414/oz; gold dipped on the 9/16 hike then recovered ~$4,300; PTs raised (UBS/RBC $155).
- OMCL — weakened. Q2 EPS beat (aided by one-time $15M tariff refund) but FY product bookings guide cut to a wide $425-560M (was $510-560M), decision cycles lengthening — exactly the falsifier's direction; falsifier's Q4 test date not yet reached. Watch closely.
- SFNC — weakened. No takeout bid; Q2 EPS $0.50 adj vs $0.53 est. Falsifier (regulatory window post-midterms) still pending; rate hike adds pressure.
- XENE — mixed. X-TOLE2 positive (March), NDA filed 9/17 (epilepsy thesis strengthened) BUT voluntary enrollment pause in MDD/bipolar trials over neuropsychiatric AEs. Tail-risk leg of the basket; size accordingly.
- FRPT — intact/strengthened. Q2 sales +15.5%, GM highest since 2020, guide raised, +8% to ~$67 (vs $80 TD Cowen PT). R2000 membership still unverified.
- MSFT — strengthened. FQ4 Azure +43%, RPO +84%, stock +~17% next day; falsifier (Azure decel) opposite. Note ~part of the upside already realised.
- META — weakened. Q2 EPS $6.18 vs $7.14, FCF $784M, capex guide $130-145B (floor raised), stock ~-8-10%. Falsifier "capex guide up w/o revenue" is borderline (revenue $60.8B slightly beat). Re-check next quarter.
- MELI — intact/soft. Rev +50%, credit book +75%, NPLs near lows; op margin -550bp to 6.7% (margin compression, not yet take-rate/credit falsifier); stock -4% AH.
- PLTR — strengthened. Q2 rev +93%, US commercial +149%, guide raised; +~12-30% move. Valuation risk remains.
- INTC — strengthened. Q2 rev $16.1B, foundry loss $2.1B (under $2.4B falsifier), 18A output above target; stock ~$121 (9/21) — above the book's ~$110 reference and above the average PT ($116). Upside case now mostly HSBC-bull-dependent.
- S — intact, low confidence. Search returned FY27-Q2 (7/31/26) rev +21%, ARR +22%, NNARR $56M (+4%), guide raised; figures look identical to the prior-year quarter, so verify against the 8/27 press release.

**Stale-catalyst check:** INTC 7/23, FOMC 7/29, INTU FY27 guide all resolved (above). Open: OMCL Q4 bookings, SFNC post-midterm window, XENE FDA acceptance/psych pause, INTU watchlist re-entry.

### 2026-10-13 sweep (pre-Q3 earnings; 3 parallel sleeve agents; web-sourced, not terminal-checked)

Full evidence, proposed kill lines, data-conflict notes and all sources: [[Equity-Book-Sweep-2026-10-13]]. The Monday `weekly-upside-book-sweep` loop did not log 9/28, 10/5 or 10/12. This sweep covers the gap.

**Macro:**
- No FOMC since the 9/16 hike (12-0 to 3.75-4.00%). The statement had no explicit forward guidance. "Another hike" comes from the SEP median of 4.1% for YE-26 and the 10/7 minutes ("most participants").
- Sept payrolls +29k vs ~90k expected.
- 10y: 4.96% → **5.21%**, with a 5.31% peak on 10/5.
- Hike pricing: a December hike ~75%; October ~17-19% (unverified).
- SPX 7,805: +0.5% since 9/21, +14.0% YTD.
- **R2000 2,783: −3.2% since 9/21, ~0.8% above correction territory.** Every input to the R2000 interest-expense trap moved the wrong way.
- CPI is 10/14; FOMC is 10/27-28.

| Name | Verdict | 10/13 px (vs 9/21) | Falsifier | Next test |
|---|---|---|---|---|
| ADBE | **TRIM** | $236 (−5%) | closer: Q3 net new ARR ~$0.40B (−36% y/y); Wells Fargo cut to UW 10/12 | ~12/9: Q4 NNARR. Proposed KILL if below Q3 |
| CMCSA | **TRIM** | $20.88 (−9%) | closer: CFO pre-guided Q3 broadband losses worse than −104k; buybacks paused since the 6/29 NBCU/Sky spin | **10/22**: losses above Q2's 167k = KILL |
| NVDA | KEEP | $228.52 (flat) | unchanged. AI-funding wobbles (OpenAI revenue gap, Broadcom capital warning) | late-Oct hyperscaler capex; ~11/18 |
| NEM | KEEP | $115.59 (−6%) | marginally closer. Gold ~$4,170; proposed "breakdown" = close below $4,000 | 10/22 |
| INTU (watch) | no re-entry | $301 | further away. Investor Day confirmed DIY share loss on price | IRS filing stats Feb-Apr 2027 |
| OMCL | KEEP | $36.87 (+14%) | unchanged | **10/29**: proposed KILL if FY bookings midpoint < ~$490M or Titan XT slips to 2027 |
| SFNC | **TRIM** | $22.34 (−1%) | **mis-specified**: midterms don't change bank regulators. No bid; the 9/3 branch cuts are self-help | 10/15 AMC. Re-specify the falsifier |
| XENE | KEEP | $35.81 (−8%) | unchanged. CEO+CFO bought 45k shares ~$37.35 (9/30 Form 4s) | NDA acceptance ~11/16-30. Refuse-to-file = KILL |
| FRPT | KEEP; **moved out of R2000** (it's R1000) | $65.26 (+6%) | unchanged | ~11/3 |
| KRYS | KEEP | $332 (flat) | none written. Proposed: VYJUVEK q/q revenue flat-to-down 2 straight quarters | ~11/2. Russell prelim list 11/13: risk of moving to R1000 |
| TERN | **KILL** | — | acquired by Merck at $53 cash, closed 5/5/26, delisted | — |
| SPRY (watch) | no re-entry | $4.18 | trigger 1 technically hit (Q2 neffy $26.2M) but overridden by cash: $143.8M vs $171.6M debt + liability. CSU interim slipped to Q1-27 | ~mid-Nov |
| MSFT | **TRIM** | $543 (+8%) | further away (Azure +43%, guided ~45%). ~90% of the +44% realised | **10/28**: Azure cc below 43% = first decel |
| META | KEEP, no adds | $762.50 (+3%) | unchanged, skewed closer | **10/21** (not 10/28): 2027 capex vs revenue guide |
| MELI | KEEP | $1,876 (+3%) | take-rate leg closer: Brazil seller discounts per the Q2 letter; credit clean | ~10/29: op margin vs 6.7% |
| PLTR | **TRIM** | $208.67 (+14%) | further away. Past the $200 median PT | 11/2 |
| INTC | KEEP small | $102.81 (−16%) | closer: no named external 18A customer, externals steered to 14A, Terafab talking to TSMC. Upside now HSBC-$200-only | **10/29**: foundry loss vs $2.4B |
| S | **TRIM** | $24.01 (+1%) | closer: NNARR +4% y/y. Past the $20.50 PT | ~12/3: negative NNARR y/y = fires |
| MU/SNDK | anti-pick holds | MU −13%, SNDK −21% from highs | snapback started (CXMT DRAM news); MU still guides up | stay out both ways |

**Corrections to the 9/21 entry:**
- (a) The Fed "another hike signalled" came from the SEP and minutes, not the statement.
- (b) META's "$7.14" was Q2-2025 actual EPS, not consensus. The sweep also missed the 8/26 29-state settlement (~$16.7-18B over 10 years; reported ~$10B Q3 charge outside the expense guide; unverified, no 8-K found).
- (c) FRPT's "~$67" ≠ the 9/21 close of $61.37.
- (d) S's FY27-Q2 figures are verified real, not recycled (rev $291.98M vs $242.18M). The FY EPS guide was cut on share count.
- (e) Missed: CMCSA's 6/29 spin and buyback pause, and SFNC's 9/3 branch-closure 8-K.
- (f) **TERN was already acquired when the book was created (7/8).** That was a stale-catalyst violation from day one. The rule now needs a "still listed?" check at filing.

**Book-level reads:**
1. **Winners have hit target.** MSFT, PLTR and S have realised the book's upside, so trim. The derated-quality sleeve is now cracking at *leading* indicators (ADBE NNARR, CMCSA pre-announced losses). That is the same pattern INTU showed before its kill.
2. **The R2000 sleeve is thin.** It is OMCL, SFNC (trimmed), XENE and KRYS. It needs 1-2 catalyst-driven adds from [[Upside-Screen-2026-07]], and nothing rate-sensitive before CPI or the FOMC.
3. **NEM isn't hedging.** It is −6% vs SPX +0.5%, trading as real-rate beta. That is correlated with the book's main risk (a hawkish Fed), not with the AI-snapback tail it was bought for. Revisit its role under Construction & discipline.
4. **Decisions for Scott:**
   - adopt or reject the proposed kill lines (ADBE, CMCSA, OMCL, KRYS);
   - re-specify SFNC's falsifier (e.g. no bid by YE-2027);
   - set SPRY's override thresholds (proposed: Q3 neffy ≥ ~$30M with burn ≤ ~$30M/qtr, or a 1/1/27 formulary add).

## Status

- [x] Hypothesis formed (2026-07-08, web-sourced)
- [x] Top-3 conviction names re-underwritten from filings (2026-07-08 loop 2: INTU yes / SPRY killed / OMCL qualified yes) — remaining names still marketing-grade
- [ ] Entry levels / sizing set
- [ ] Positions live

Next dated catalysts (as of the 10/13 sweep):
- **10/14** CPI
- **10/15** SFNC
- **10/21** META
- **10/22** CMCSA, NEM
- **10/27-28** FOMC
- **10/28** MSFT
- **10/29** OMCL, INTC (MELI ~10/29, estimated)
- **11/2** PLTR (KRYS ~11/2, estimated)
- **11/13** Russell prelim list (KRYS)
- **~11/16-30** XENE NDA acceptance
- **~11/18** NVDA
- **~12/3** S
- **~12/9** ADBE

Calendar: [[Equity-Book-Sweep-2026-10-13]].

## Loop infrastructure (armed 2026-07-08)

This book is now maintained by scheduled loops ([[Claude Code Loop Taxonomy]] — time-based, trigger handed off). Tasks live in `C:\Users\scott\.claude\scheduled-tasks\`; they run while the Claude desktop app is open (missed runs fire on next launch):

- `weekly-upside-book-sweep` — Mondays 6:00 HST: re-verify all names' catalysts/falsifiers under the stale-catalyst rule; append to **Loop log** below
- `intc-earnings-check-jul23` — one-shot 7/23 14:00 HST: Q2 print vs the two INTC falsifiers
- `fomc-check-jul29` — one-shot 7/29 10:00 HST: decision vs the small-cap-sleeve contradiction callout
- `intu-fy27-guide-check` — one-shot 8/25 14:00 HST: FY27 guide vs the INTU falsifier

Loop runs append dated entries under a "## Loop log" section (created on first run, above Status).
