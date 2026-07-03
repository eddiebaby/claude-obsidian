---
type: source
address: c-000003
title: "Is Trend Still Your Friend? A Microstructural Account of the Demise of Short-Term Trend-Following"
domain: quantitative-finance
status: complete
created: 2026-07-02
updated: 2026-07-02
tags:
  - source
  - paper
  - quantitative-finance
  - trend-following
  - market-microstructure
  - high-frequency-trading
related:
  - "[[quantitative-finance]]"
  - "[[Trend-Following]]"
  - "[[Tick-Size-Microstructure]]"
  - "[[Jean-Philippe Bouchaud]]"
  - "[[Capital Fund Management]]"
source_type: paper
author: "Jutta G. Kurth, Zoltan Eisler, Adam Rej, Jean-Philippe Bouchaud"
date_published: 2026-07-03
url: "https://arxiv.org/abs/2607.01550"
confidence: high
key_claims:
  - "Short-term trend-following (horizons of days to weeks) ceased to deliver reliable returns starting ~2009, while slow trend signals remain approximately intact."
  - "The volatility-normalised tick size, not asset class or liquidity, is the cross-sectional variable that cleanly separates degraded from surviving trend strategies."
  - "Trend profitability and persistence are two faces of a self-fulfilling impact feedback loop; the loop broke on small-tick contracts because HFT market-making withdraws liquidity in front of predictable directional flow in sparse order books."
  - "Capacity constraints, electronification, and order-flow regime shift (H1-H3) are each rejected as sole explanations on grounds of timing, magnitude, or cross-sectional heterogeneity."
---

# Is Trend Still Your Friend? A Microstructural Account of the Demise of Short-Term Trend-Following

Navigation: [[quantitative-finance]]

---

## Bibliographic Record

| Field | Detail |
|-------|--------|
| Authors | Jutta G. Kurth (Institut Louis Bachelier / École polytechnique), Zoltan Eisler (Imperial College London), Adam Rej ([[Capital Fund Management]]), [[Jean-Philippe Bouchaud]] (CFM / Institut Louis Bachelier / Académie des Sciences) |
| Submitted | July 2, 2026 (paper dated July 3, 2026) |
| arXiv | [2607.01550](https://arxiv.org/abs/2607.01550) [q-fin.TR] |
| PDF | https://arxiv.org/pdf/2607.01550 |
| Keywords | Trend following, CTA, market microstructure, tick size, high-frequency trading, market making, price impact |
| Source | PDF directly read via pdftotext extraction (pages 1-22, main text, all tables/figures described in text; Appendix A data catalogue and Appendix B capacity-drag derivation read; Appendices C-F not extracted in detail) |

---

## Abstract (verbatim)

"Systematic trend following has, on average, been profitable for at least two centuries; yet since approximately 2009, short-term trends have ceased to deliver reliable returns. Using a cross-section of roughly 100 liquid futures contracts spanning 1995–2025, together with an industry-representative CTA proxy, we document the break and characterise its dependence on signal speed and asset class. We evaluate four candidate explanations — capacity constraints, market electronification, a regime change in CTA-versus-order-flow interactions, and a microstructural mechanism — and find that the first three fail on grounds of timing, magnitude, or cross-sectional heterogeneity.

Our central empirical finding is that the cross-sectional variable distinguishing degraded from surviving trends is the volatility-normalised tick size: post-2008 trend PnL has collapsed on small-tick contracts across all signal horizons, while remaining essentially intact on large-tick contracts. Neither asset class nor liquidity replicates this dichotomy.

We interpret this result through the lens of a self-fulfilling feedback loop that, in our view, lies at the heart of the trend anomaly itself: Trend signals trigger directional trades, whose market impact reinforces the very price moves that generated the signal. The profitability and the persistence of trend are therefore both sustained by the same impact channel. This loop, however, requires that trend followers can actually execute aggressively at reasonable cost. We argue that the post-crisis transition to HFT-dominated market making, whose liquidity-withdrawal behaviour in the face of predictable directional flow has sharply contrasting consequences for sparse (small-tick) and dense (large-tick) limit order books, has broken this loop on small-tick contracts. On large-tick contracts, where residual depth remains sufficient, the loop continues to operate and trend continues to deliver. A complementary price-impact analysis shows that passive execution offers no escape, since it forfeits the self-reinforcement channel while incurring adverse opportunity costs."

---

## Section Structure (7 sections + appendices)

1. Introduction (self-fulfilling impact loop, four candidate hypotheses H1-H4)
2. Trend Portfolios and a CTA Industry Proxy
3. Empirical Decay of Trend PnL (aggregate, speed dependence, asset-class heterogeneity)
4. Assessing Capacity, Electronification, and Order Flow (H1-H3)
5. Tick Size as a Discriminant Factor
6. HFT Liquidity, the Self-Fulfilling Loop, and the Sparse-vs-Dense Asymmetry (H4, mechanism)
7. Discussion and Conclusion
- Appendix A: Data catalogue (101 futures contracts, daily; 53 contracts, 5-min bars)
- Appendix B: Capacity drag calculation (square-root impact model)
- Appendix C: Intraday volume-clock decomposition
- Appendix D: Volatility/return-magnitude decompositions; anticipatory trading evidence
- Appendix E: Liquidity-tick size correlation; robustness
- Appendix F: Within-asset-class tick-size tiering

---

## Dataset

**Daily universe**: ~100 (101 listed) of the most liquid futures contracts, daily settlement, 1995-2025, four sectors: commodities (CMD), equity indices (IDX), currencies (FXR), government bonds/yields (YLD). Full ticker list in Appendix A (e.g., BUND, GOLD0, EUR, NIKKEI, TBOND, WTICRUDE0).

**Intraday bar data**: proprietary 5-minute bars from Capital Fund Management, 53 contracts with coverage starting no later than 2004 (ensures 5+ years pre-break data). Reports total volume, buyer/seller-initiated volume, and end-of-interval bid/ask resting volume snapshots per contract per bar.

**CTA proxy**: liquidity-weighted trend portfolio rescaled to industry-wide AUM (BarclayHedge data) at 12% annualised risk (inferred from SG CTA Index). Resulting median daily participation rate: 0.9% of traded volume — cross-validated against independent estimates from Quantica Capital (2022) and Lorenzen et al. (Morgan Stanley, 2025) that CTAs represent under 1% of futures volume.

---

## Signal and Portfolio Construction

**Signal**: EWM-τ-4τ — difference of fast (τ) and 4×-slower EWMA of close prices, normalised by a 16τ EWM standard deviation, clipped at ±2 SD. Tested horizons: τ ∈ {5, 10, 20, 50} days.

**Two portfolio types**:
- Type 1 (equal-risk): position ∝ signal / own volatility.
- Type 2 (liquidity-weighted): position further scaled by contract's share of aggregate portfolio liquidity — needed to model industry-scale CTA capacity, since illiquid products can't scale like liquid ones.

---

## Key Results

### Aggregate decay (Section 3)

- Fast trend portfolio (EWM-5-20) cumulative PnL: essentially flat 1950-2025 sample from 2009 onward (some weakening detectable from ~2000).
- 5-year rolling Sharpe collapses from historical 1-2.5 range to statistically indistinguishable from zero post-2010.
- Consistent with SG CTA Index performance: strong 2000-2008, flat/negative 2009-2025 except two macro punctuations (2014, Covid).

### Table 1: Sharpe ratios by signal horizon, two sub-periods

| τ (days) | Sharpe 1995-2009 | Sharpe 2009-2025 |
|----------|-------------------|--------------------|
| 5  | 0.84 ± 0.27 | 0.12 ± 0.24 |
| 10 | 0.83 ± 0.27 | 0.22 ± 0.24 |
| 20 | 0.79 ± 0.27 | 0.27 ± 0.26 |
| 50 | 0.70 ± 0.27 | 0.40 ± 0.26 |

Pre-2009: Sharpe monotonically *decreasing* in τ (fast signals best). Post-2008: ordering *reverses* — fastest signal collapses to 0.12, slowest still delivers 0.40. **Signal horizons that still work: slow trend (τ=50 days and slower) retains roughly 55-60% of its pre-break Sharpe; τ=5-10 day signals lose 71-85% of theirs.**

### Asset-class heterogeneity (Section 3.3)

Trend effectively vanished for IDX (equity indices) and FXR (currencies); YLD (yields) and CMD (commodities) show no appreciable degradation.

### Rejected hypotheses (Section 4)

**H1 — Capacity constraints**: rejected on four grounds. (1) Reverse causality — CTA AUM grew through the 2000s, plateaued ~2012, peaked 2022, years *after* PnL went flat. (2) No post-2018 recovery despite sharply rising futures liquidity from 2018 onward reducing participation rates. (3) Square-root impact model at 1% participation, 9% daily turnover implies only ~0.1 annualised Sharpe drag — too small to explain a 0.7→0 collapse even with 3× model-uncertainty margin. (4) **Most telling**: recomputing PnL with zero-lag (same-day close) execution still produces flat post-2008 returns even with costs fully removed — meaning the *signal itself* degraded, not merely the cost of harvesting it.

**H2 — Electronification**: rejected. Transition was gradual; PnL break was abrupt. Sectoral timing mismatches (equities electronified 5+ years before break; FX contemporaneously; interest-rate futures electronified early but did not degrade).

**H3 — Order-flow / CTA-book-imbalance regime shift**: initially promising at aggregate level — Corr(CTA, book imbalance) flips sign around 2010 for short-term signals specifically, paralleling the PnL break. But fails cross-sectionally: commodities show a sharp correlation regime change with *no* PnL degradation; yields show no correlation change and no degradation; indices show a reverse correlation pattern but similar degradation. No monotonic mapping between correlation change and PnL outcome at the asset-class level. (H3's diagnostic value resurfaces in Section 6 disaggregated by tick-size tier instead.)

### Table: Capacity drag calculation (Appendix B derivation)

Under square-root impact (Q^(3/2) slippage scaling), unit trading cost at 1% participation rate ≈ 2/30 of daily volatility; annualised Sharpe drag ≈ 0.1 — an order of magnitude too small to explain the observed 0.7→0 Sharpe collapse.

### Tick size as the discriminant (Section 5) — CENTRAL FINDING

**Tiering procedure**: monthly, causal ranking of each contract's average tick-to-volatility ratio (tick size ÷ daily volatility), split into two equal-sized tiers: small tick (ST, bottom 50%) vs large tick (LT, top 50%). Contracts rarely migrate tiers.

**Result**: 
- Pre-break Sharpes cluster ~0.8 (ST) and ~1.4 (LT) for equal-risk portfolio, across all four signal horizons.
- Post-break: ST Sharpes collapse to ~zero (mildly negative for fastest signals) — **100% relative degradation**.
- LT Sharpes remain 1.0-1.2 — **0-30% relative degradation**.
- Holds with and without liquidity weighting.
- Holds when tiering is performed *within* asset class (Appendix F) — rules out the dichotomy being just a relabeled asset-class effect. Asset-class heterogeneity (IDX/FXR degraded, YLD/CMD intact) is explained as a downstream symptom of IDX/FXR clustering in the small-tick tier and YLD/most CMD clustering in the large-tick tier.

**Liquidity does NOT replicate the dichotomy**: liquidity and tick size are negatively correlated (log-log Pearson r = -0.35 ± 0.08) but liquidity-tiered decomposition is inconsistent across signal horizons — no clean high/low-liquidity ordering. Tick size, not liquidity, asset class, or electronification timing, is the operative cross-sectional variable.

**Within-contract confirmations** (Section 5, Appendix D):
- Low-volatility regimes on small-tick contracts continue accruing PnL post-break — small-tick products behave like large-tick contracts when volatility drops (tick/volatility ratio rises), confirming τ/σ (not tick size τ alone) is the operative variable.
- Trend break is a large-return-day phenomenon only: PnL contribution from sub-1σ days is essentially invariant to the regime change across all horizons/tiers. What collapsed is specifically the ability to profit from large directional moves on small-tick contracts.

### The mechanism (Section 6)

**Liquidity provision rotated against trend flow** (6.1): Corr(CTA trade, book imbalance) for fast signals on large-tick contracts flipped from ≈-3%/yr pre-2010 to ≈+4%/yr post-2010 — the book rotated against trend followers in both tiers. But consequences are asymmetric.

**Two-part mechanism** (6.2):
1. Post-2008 transition from bank-affiliated/proprietary-desk market making (inventory horizons of hours-days) to HFT-dominated market making (intraday flat-inventory, tight spread-capture economics) that is structurally incompatible with absorbing predictable, persistent directional CTA flow.
2. Structural LOB differences: small-tick books are intrinsically **sparse** (better-price priority requirements make posted depth thin, gaps between filled levels common); large-tick books are intrinsically **dense** (wide spread relative to adverse-selection cost supports deep multi-level resting volume).

**Combined consequence**: on sparse small-tick books, HFT liquidity withdrawal removes the residual depth trend followers need to execute at reasonable cost, forcing them to "walk the book" or retreat — breaking the loop on its input side (impact-mediated reinforcement disappears with the flow that created it). On dense large-tick books, residual depth at multiple levels remains sufficient; loop continues to operate.

**Price-impact evidence** (6.3): normalised 5-min return vs. book imbalance relationship. Pre-2011 small-tick: clear adverse selection (negative correlation, peak at intermediate imbalance ~0.1). Post-2011: correlation flattens to near zero — the mechanical signature of liquidity withdrawal (depth that would have been "run over" no longer rests long enough to register). Large-tick correlation stays persistently negative pre- and post-2011 (spreads wide enough to absorb adverse selection). Return-vs-trade-imbalance relationship (the loop's "generative" leg) is stable over time and similar across tiers — evidence the reinforcement mechanism itself (not just the LOB shape) persists on large ticks.

**Limit orders are no remedy** (6.4): two independent reasons. (a) Passive trend orders are penalised by missed-opportunity cost (informative signal guarantees adverse fill timing), not classic adverse selection — re-labels cost, doesn't remove it. (b) Passive execution forfeits the self-reinforcing impact channel entirely, since only aggressive (buyer/seller-initiated) flow generates the trade-imbalance impact that sustains the signal.

---

## The Self-Fulfilling Impact Loop (organizing framework)

> "Trend signals trigger directional trades, whose market impact reinforces the very price moves that produced the signal, which in turn sustains the signal for the next trader to act on."

Trend's profitability and its very existence are two faces of the same coin — both depend on aggressive directional flow being absorbable at reasonable cost. The loop has two preconditions: (1) trend followers can execute aggressively at reasonable cost, (2) the impact function (flow → price) remains intact. Both held until ~2010 across the futures universe; both have since been compromised on small-tick contracts, preserved on large-tick contracts.

The paper explicitly does not claim this loop is the sole origin of trend — behavioural underreaction (Hong and Stein 1999; Daniel et al. 1998), slow information diffusion (Hong et al. 2000), and anticipatory staggered accumulation are cited as coexisting, non-exclusive mechanisms. The authors find direct evidence (Appendix D, Fig. 18) that anticipatory trading has also decayed over the same period, alongside the impact-loop component.

---

## Conclusion and Practical Implications

- The break is judged structural, with no plausible reversion scenario absent a structural change in liquidity provision (regulation, entry of inventory-tolerant intermediaries, or market-making rent re-tariffing).
- Passive execution is not a workaround (Section 6.4).
- Capacity estimation for trend portfolios should be done at the **tick-size-tier level**, not the asset-class level — aggregate participation rates can look comfortably low while binding within the small-tick subset specifically.
- Open questions: direct HFT-inventory-data tests around large CTA rebalances; possibility of trend surviving in microstructural niches (sub-HFT-threshold contracts, different market-maker mandates, shifted tick regimes); whether the same liquidity-withdrawal mechanism disadvantages other strategies generating predictable directional flow, and whether counter-flow strategies have benefited from a complementary tailwind.

---

## Key Citations

- Moskowitz, Ooi, Pedersen (2012) — "Time series momentum," the canonical TSM reference across 58 instruments, 3.5 decades
- Lempérière, Deremble, Seager, Potters, Bouchaud (2014) — "Two centuries of trend following"; Hurst, Ooi, Pedersen (2017) — "A century of evidence on trend-following investing"
- De Long, Shleifer, Summers, Waldmann (1990) — positive feedback investment strategies (origin of the self-fulfilling loop framing)
- Van der Beck, Bouchaud, Villamaina (2024) — "Ponzi funds" (arXiv 2405.12768), the ETF-context precedent for the impact-loop mechanism
- Tóth, Lemperiere, Deremble, De Lataillade, Kockelkoren, Bouchaud (2011) — square-root impact law (Physical Review X)
- Bouchaud, Bonart, Donier, Gould (2018) — *Trades, Quotes and Prices: Financial Markets Under the Microscope* (Cambridge UP)
- Volpati, Benzaquen, Eisler, Mastromatteo, Tóth, Bouchaud (2020) — "Zooming in on equity factor crowding" (order-flow imbalance methodology, Eq. 5 of this paper)
- Korajczyk and Murphy (2019) — HFT market making to large institutional trades; Van Kervel and Menkveld (2019) — HFT around large institutional orders
- Kirilenko, Kyle, Samadi, Tuzun (2017) — the Flash Crash; Menkveld (2013) — HFT and new market makers
- Quantica Capital (2022, 2025) — cross-sectional capacity/diversification analysis, cited and partially rebutted as H1's strongest form (footnote: they find no relationship between per-instrument Sharpe and liquidity after costs, and don't claim industry-wide capacity saturation — the paper treats this as a secondary effect, not the driver)
- Dayri and Rosenbaum (2015) — large tick assets, implicit spread, optimal tick size
- Schmidhuber (2021) — "Trends, reversion, and critical phenomena in financial markets"

---

## Provenance Note

PDF text extracted via `pdftotext -layout` (pages 1-22 of 23+; poppler's pdftoppm/image rendering unavailable in this environment, so the Read tool's native PDF path could not be used — text extraction substituted). All main-text sections (1-7), Table 1, the Appendix A data catalogue, and the Appendix B capacity-drag derivation were directly read. Figures (2-14, 18) were read via their captions and in-text descriptions, not visually rendered — numeric callouts embedded in figure captions/axis labels were extracted where legible in the text layer. Appendices C, D (beyond the text-described results), E, and F were not extracted in full detail; only the summary claims referenced in the main text are captured above.

---

## See Also

- [[quantitative-finance]] — domain page
- [[Trend-Following]] — concept page: TSM as a strategy class
- [[Tick-Size-Microstructure]] — concept page: volatility-normalised tick size and LOB density
- [[Jean-Philippe Bouchaud]] — senior author, CFM chairman
- [[Capital Fund Management]] — authors' affiliation, proprietary bar-data source
- [[zhang2026-benchmarking-deep-ts-equity]] — parallel equity forecasting benchmark; both papers converge on "no single approach dominates; costs and constraints are decisive"
- [[das2026-chronos-multivariate-forecasting]] — parallel time-series forecasting paper in the vault
