---
type: concept
title: "Equity Upside Book — 2026 H2 (SPX + R2000 + Nasdaq)"
created: 2026-07-08
updated: 2026-07-08
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
sources:
  - "web research 2026-07-08 (Schwab/Fidelity mid-year outlooks, MarketWatch H1 losers, TIKR, William Blair, Motley Fool bank M&A, company 8-Ks)"
---

# Equity Upside Book — 2026 H2 (SPX + R2000 + Nasdaq)

Hedge-fund-analyst exercise, 2026-07-08. Question: highest 12-24 month upside in the S&P 500 and Russell 2000. All price targets are sourced consensus/analyst figures from web research, **not verified against a terminal** — verify before any position.

## Market frame (as of 2026-07-08)

- SPX ~7,537 (ATH 7,621). Earnings-driven bull, but leadership narrow: AI + energy. FY26 SPX EPS growth estimate 25%, concentrated in a handful of names. Strategist warnings of "extreme speculation" in high-multiple names; one YE target at 7,100 (below market).
- Fed at 3.50-3.75%; further cuts fading on sticky inflation.
- R2000 +21% YTD — best start since 1991. Small-cap FY26 EPS growth consensus rose 23% → 38%. Bank M&A at 7-year high ($15.1B H1); biotech M&A $106B by June (strongest since 2019).
- Key R2000 risk: interest expense = 31% of EBITDA (6-yr high). Favor low-leverage names; the floating-rate trap is real if cuts stall.

> [!contradiction] Fed pivot vs the small-cap tailwind (added same day)
> Later same-day research (Nasdaq sweep): on **2026-06-17 the Fed held at 3.50-3.75% but signalled a likely 2026 HIKE** — the earlier "cuts fading" framing understates it. This directly weakens the R2000 rate-tailwind leg: at 31% interest/EBITDA, a hike is a book-level threat to the small-cap sleeve. Response: R2000 picks must be M&A/idiosyncratic-catalyst driven (SPRY formulary, SFNC takeout, OMCL bookings), never rate-beta. Watch July FOMC.

## Core insight

The most asymmetric 12-24mo upside is NOT in the AI-momentum winners (that's where snapback risk lives — MU +242% YTD). It's in two pockets:

1. **The AI-roadkill derating (SPX).** H1's worst performers weren't earnings misses — they were quality software derated on AI-disruption *narrative* while fundamentals grew (Intuit -51% with EPS +12%). Double engine if fear proves early: EPS growth × multiple re-rate. JPM private bank: full agentic replacement of enterprise software is "post-2028 at the earliest."
2. **M&A gravity (R2000).** Bank consolidation at 7-yr highs plus the biggest biotech M&A year since 2019 puts a takeout floor + call option under quality small-caps in those sectors.

## S&P 500 book

| # | Name | Setup | 12-24mo upside (sourced) | Falsifier |
|---|------|-------|--------------------------|-----------|
| 1 | **INTU** Intuit | -51% YTD, worst in SPX; 15.9x P/E vs 30-40x historical; FY26 EPS +12% to $17.23; TT Live rev +36%, QBO accounting +22% | Consensus PT ~$553 = +42%; some services cite +62% | TurboTax unit declines or FY27 guide showing real share loss to AI-native competitors |
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
| 4 | **XENE** Xenon Pharma | William Blair 2026 top-5 biotech pick; epilepsy program (azetukalner) with late-stage readouts; buyout optionality | Binary-heavy; basket with KRYS/TERN/SPRY | Trial miss — this is the tail-risk leg of the basket |
| 5 | **FRPT** Freshpet | TD Cowen $80 PT = +50%; premium pet-food volume share 2.7% and growing; growth-at-a-reasonable-price after derating | +50% (single-analyst) | Volume share stalling; **verify current R2000 membership** (borderline small/mid) |

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

## Status

- [x] Hypothesis formed (2026-07-08, web-sourced)
- [x] Top-3 conviction names re-underwritten from filings (2026-07-08 loop 2: INTU yes / SPRY killed / OMCL qualified yes) — remaining names still marketing-grade
- [ ] Entry levels / sizing set
- [ ] Positions live

Next dated catalysts: INTC earnings 7/23; July FOMC 7/29; INTU FY27 guide late Aug; OMCL H2 bookings; SPRY watchlist re-entry triggers above.

## Loop infrastructure (armed 2026-07-08)

This book is now maintained by scheduled loops ([[Claude Code Loop Taxonomy]] — time-based, trigger handed off). Tasks live in `C:\Users\scott\.claude\scheduled-tasks\`; they run while the Claude desktop app is open (missed runs fire on next launch):

- `weekly-upside-book-sweep` — Mondays 6:00 HST: re-verify all names' catalysts/falsifiers under the stale-catalyst rule; append to **Loop log** below
- `intc-earnings-check-jul23` — one-shot 7/23 14:00 HST: Q2 print vs the two INTC falsifiers
- `fomc-check-jul29` — one-shot 7/29 10:00 HST: decision vs the small-cap-sleeve contradiction callout
- `intu-fy27-guide-check` — one-shot 8/25 14:00 HST: FY27 guide vs the INTU falsifier

Loop runs append dated entries under a "## Loop log" section (created on first run, above Status).
