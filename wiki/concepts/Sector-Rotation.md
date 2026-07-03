---
type: concept
title: "Sector Rotation"
domain: quantitative-finance
complexity: intermediate
status: developing
created: 2026-07-02
updated: 2026-07-02
aliases:
  - "sector-based tactical allocation"
  - "industry rotation"
tags:
  - concept
  - quantitative-finance
  - portfolio-construction
  - machine-learning
related:
  - "[[quantitative-finance]]"
  - "[[miao-polak-online-ensemble-sector-rotation]]"
  - "[[Online-Ensemble-Learning]]"
  - "[[zhang2026-benchmarking-deep-ts-equity]]"
  - "[[karatas2021-two-stage-sector-rotation]]"
  - "[[Echo-State-Networks]]"
sources:
  - "[[miao-polak-online-ensemble-sector-rotation]]"
  - "[[karatas2021-two-stage-sector-rotation]]"
---

# Sector Rotation

Navigation: [[quantitative-finance]]

---

## Definition

Sector rotation is a tactical asset allocation strategy that reallocates capital among industry sectors (rather than among individual securities) based on expected relative performance. It exploits the premise that different sectors outperform at different points in the business cycle, driven by cyclical shifts in growth, sentiment, monetary/fiscal policy, and sector-specific technological or regulatory forces.

Sectors are typically defined by classification schemes such as SIC (Standard Industrial Classification, first two digits) or GICS (Global Industry Classification Standard). [[miao-polak-online-ensemble-sector-rotation]] uses SIC specifically because it provides consistent historical coverage and avoids classification drift from periodic GICS revisions.

---

## Why Sector-Level Returns Are More Predictable Than Single-Name Returns

This is the structural bet underlying every ML-based sector rotation paper in this vault. The argument, as formalized in [[miao-polak-online-ensemble-sector-rotation]]:

1. **Noise cancellation**: Aggregating firm-level returns into a sector-level return (equally weighted or capitalization weighted) averages out idiosyncratic, firm-specific noise (regulatory shocks, one-off earnings surprises, individual mismanagement) while preserving the systematic component shared across firms in a sector.
2. **Common macro exposure**: Firms in a sector face coordinated demand, technological, and regulatory forces and align with business-cycle dynamics — this generates cross-sectional structure that a model can actually learn, versus single-stock idiosyncratic variance which is largely unforecastable.
3. **Leading-indicator property**: Firm-level accounting/market data (valuation ratios, profitability, investment behavior) adjust faster to changing economic conditions than macro aggregates, which are published with lag and subject to revision. Sector-level aggregates of these firm signals can therefore act as leading indicators for cyclical turning points, while remaining more stable than the raw firm-level series.
4. **Empirical confirmation**: [[miao-polak-online-ensemble-sector-rotation]] finds ensemble out-of-sample R² of ~1.19% (equal-weighted sectors) versus the individual-stock-level R² values reported in Gu, Kelly & Xiu (2020) — sector aggregation measurably improves the signal-to-noise ratio for the same firm characteristics and same model classes.

---

## Classic (Macro-Indicator) Approach

Traditional sector rotation strategies rely on **macroeconomic indicators** — business-cycle stage classification, yield curve shape, leading economic indicators, sentiment surveys — to time entry/exit into cyclical vs. defensive sectors. This is the approach [[miao-polak-online-ensemble-sector-rotation]] explicitly contrasts itself against (citing Karatas [13] for the macro-indicator tradition — i.e. [[karatas2021-two-stage-sector-rotation]] itself), preferring firm-characteristic aggregation instead because macro data is infrequent, lagged, and subject to revision, limiting usefulness for short-horizon or high-frequency allocation decisions.

[[karatas2021-two-stage-sector-rotation]] is the macro-indicator-driven exemplar in this vault: US business cycles (11 identified by NBER since 1945) are the motivating frame, but instead of the simple two-factor Investment Clock (growth + inflation), the paper selects a bespoke macro feature set per sector via Recursive Feature Elimination — a middle path between the coarse two-factor Investment Clock and the fully data-driven firm-characteristic-aggregation approach of Miao & Polak.

Classic **momentum-based** sector rotation (a distinct, older lineage not covered in depth by the sources in this vault yet) ranks sectors by trailing relative return (e.g., 6-12 month momentum) and rotates into recent winners — a direct sector-level analog of cross-sectional stock momentum. It requires no ML and no firm-level feature aggregation, but is more exposed to momentum crashes and regime turns than model-based approaches.

---

## ML Approaches (in vault)

| Paper | Approach | Signal construction | Combination method |
|-------|----------|---------------------|---------------------|
| [[miao-polak-online-ensemble-sector-rotation]] (Miao & Polak) | 16-model ensemble (OLS, PCR, LASSO, RF, GBRT, NN1-NN12) forecasting sector excess returns from PPCA-reduced firm-characteristic aggregates | Firm-level characteristics (94, following Gu-Kelly-Xiu) aggregated to sector level via first-PC-per-characteristic PPCA | Gradient-free online reweighting (see [[Online-Ensemble-Learning]]) by rolling out-of-sample R² |
| [[karatas2021-two-stage-sector-rotation]] (Karatas & Hirsa, 2021) | Two-stage predict-then-rank methodology: (1) predict each sector ETF's future price from sector-specific macro indicators via RFE-selected features, (2) rank sectors by predicted return and hold the top 4 equal-weighted | 8 iShares sector ETFs (IYH, IYE, IDU, IYG, IYW, IYM, IYJ, IYK); common macro indicators (GDP, unemployment, CPI, mortgage rate, fed funds rate) + sector-specific indicators (e.g., R&D/import for tech, LIBOR/TED spread for finance) selected via Recursive Feature Elimination | Compares Ridge Regression, LSTM, GRU, and Echo State Networks per sector; no ensemble — best single model/lookback combination selected per prediction horizon by balancing annualized return, Sharpe, and Calmar ratio |

Portfolio construction in [[miao-polak-online-ensemble-sector-rotation]]: monthly quintile sort of the 50 SIC sectors into Bottom 5 / 41-55 / 21-40 / 6-20 / Top 5 by predicted return; stocks within each sector held equal- or cap-weighted. The Top 5 minus Bottom 5 long-short spread portfolio is used as a market-neutral test of the ranking signal's robustness, delivering statistically significant Fama-French/Carhart alphas comparable to the long-only Top 5 leg.

Portfolio construction in [[karatas2021-two-stage-sector-rotation]] is simpler: rank all 8 sector ETFs by predicted return, hold the top 4 equal-weighted, long-only, benchmarked against the equal-weight-all-8-sectors portfolio. No long-short leg, no ensemble weighting — a direct macro-indicator-to-price-forecast pipeline per sector, contrasting with Miao & Polak's firm-characteristic-aggregation-to-excess-return pipeline. Both papers report the strategy beating its respective benchmark: Karatas & Hirsa show the two-stage methodology beats the equal-weight-all-sectors benchmark at every tested horizon out to 24 months ahead, with **Echo State Networks** ([[Echo-State-Networks]]) delivering the best annualized return and Calmar ratio at nearly every lookback window while training faster than LSTM/GRU (no backpropagation-through-time; only the linear readout is trained).

> [!note] Regime behavior
> In [[miao-polak-online-ensemble-sector-rotation]], the sector rotation strategy's edge does *not* decay during acute stress — Sortino ratio for the Top 5 portfolio rises from 1.14 (full sample 1987-2021) to 2.40 (COVID period 2020-2021), driven by the ensemble correctly identifying the rotation into technology/healthcare/consumer staples and out of energy/industrials/financials during the 2020 crash.

---

## Open Questions / Gaps in Vault Coverage

- Momentum-based (non-ML) sector rotation not yet given its own source treatment — only referenced here as contrast.
- No direct head-to-head comparison yet exists in the vault between [[miao-polak-online-ensemble-sector-rotation]]'s sector-level approach and [[zhang2026-benchmarking-deep-ts-equity]]'s firm-level daily approach on the same universe/period.
- No direct comparison yet between [[karatas2021-two-stage-sector-rotation]] and [[miao-polak-online-ensemble-sector-rotation]] on the same universe/period (8 iShares ETFs 2000-2019 vs. 50 SIC sectors 1987-2021).
- [[zhang2026-benchmarking-deep-ts-equity]]'s 15-architecture benchmark omits Echo State Networks despite ESN being the standout performer in [[karatas2021-two-stage-sector-rotation]].

---

## See Also

- [[quantitative-finance]] — domain page
- [[Online-Ensemble-Learning]] — the model-combination mechanism used in the leading vault example
- [[miao-polak-online-ensemble-sector-rotation]] — source page
- [[karatas2021-two-stage-sector-rotation]] — companion sector rotation source
- [[zhang2026-benchmarking-deep-ts-equity]] — contrasting firm-level (non-sector) benchmark
