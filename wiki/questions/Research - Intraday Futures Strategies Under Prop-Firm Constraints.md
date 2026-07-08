---
type: synthesis
title: "Research: Intraday Futures Strategies Under Prop-Firm Constraints"
domain: quantitative-finance
created: 2026-07-07
updated: 2026-07-07
tags:
  - research
  - quantitative-finance
  - futures
  - intraday
  - prop-firm
status: developing
question: "What does arXiv (and adjacent literature) say actually works for intraday index-futures trading under LucidFlex prop-firm constraints?"
answer_quality: solid
related:
  - "[[LucidFlex Automated Scalping PRD]]"
  - "[[Overnight-Drift]]"
  - "[[mesfin2026-mnq-intraday-falsification]]"
  - "[[glasserman2025-overnight-news]]"
  - "[[boyarchenko-larsen-whelan-overnight-drift]]"
  - "[[byrd-balch-2019-intraday-ml-market-efficiency]]"
  - "[[knuteson2020-overnight-intraday-returns]]"
sources:
  - "[[mesfin2026-mnq-intraday-falsification]]"
  - "[[glasserman2025-overnight-news]]"
  - "[[boyarchenko-larsen-whelan-overnight-drift]]"
  - "[[byrd-balch-2019-intraday-ml-market-efficiency]]"
  - "[[knuteson2020-overnight-intraday-returns]]"
---

# Research: Intraday Futures Strategies Under Prop-Firm Constraints

## Overview

Two-round arXiv sweep (q-fin, stat.ML) for strategies usable under LucidFlex constraints (intraday-only, non-HFT, MES/MNQ, net-of-cost). The literature converges on a sharp asymmetry: **bar-level intraday signals on index futures are falsified; the overnight/announcement structure of returns is the only robustly documented edge class** — and it sits exactly on the boundary of what the prop rules allow.

## Key Findings

1. **OHLCV intraday signals on MNQ are dead, tested directly.** 14 signal families (ORB, gaps, volume, cross-session momentum, liquidity grabs) fail walk-forward validation with 2-point costs on 2021–2025 5-min MNQ; gross edge 0.07–1.50 points vs ~2-point costs (Source: [[mesfin2026-mnq-intraday-falsification]], confidence: high).
2. **The post-2009 death of fast edges is now confirmed four independent ways**: tick-size microstructure ([[kurth2026-trend-following-demise]]), intraday ML on equities ([[byrd-balch-2019-intraday-ml-market-efficiency]]), OHLCV falsification on MNQ ([[mesfin2026-mnq-intraday-falsification]]), and the practitioner decay literature. Confidence: high.
3. **The overnight drift is the strongest documented effect available to this account class.** Nearly all index gains accrue overnight over 30 years (Source: [[glasserman2025-overnight-news]], confidence: high); on ES futures the drift concentrates around the European open via a dealer-inventory mechanism (Source: [[boyarchenko-larsen-whelan-overnight-drift]], confidence: medium — primary unfetched).
4. **Announcement-time dynamics are real but are microstructure, not a retail strategy paper.** Macro releases sharply raise price impact and volatility on ES at 1-second resolution (arXiv 2508.06788); pre-FOMC drift is attributed by some work to leakage and has decayed post-publication. Confidence: medium.
5. **Intraday RL/DL trading papers (DeepScalper etc.) do not establish retail-usable edge** — cost modeling opaque, tick-level execution assumptions unrealistic for a Rithmic retail feed. Considered and set aside. Confidence: medium.

## Contradictions

- [[mesfin2026-mnq-intraday-falsification]] (nothing works on MNQ 2021–25, net) vs Zarattini-Aziz-Barbon SSRN results (ORB and intraday momentum on QQQ/SPY strongly net-positive 2016–24). Differences: instrument (ETF vs futures), leverage assumptions, cost model, signal definitions. Mesfin's walk-forward design with positive controls is methodologically stronger; Zarattini's results have not survived independent replication on futures. **Resolution path: the PRD's Phase 1 harness on MES/MNQ is the adjudicator.**
- Elm Wealth reports the cross-sectional overnight effect **waning post-2015**, while [[glasserman2025-overnight-news]] finds the aggregate premium robust over 30 years. The decaying version is the stock-picking long-short; the index-level decomposition is the durable one.

## Consequences for [[LucidFlex Automated Scalping PRD]]

- ORB downgraded B → C (falsified on MNQ; contradiction logged). Tier-1 C-grade families (VWAP stretch, levels, liquidity grabs): now *presumed dead*, not merely unevidenced — they only earn harness time to confirm the null cheaply.
- Build order inverts decisively toward: #13 overnight drift (if Phase 0 clears legality — now with a partial-night timing refinement from the dealer-inventory mechanism), #10 first-half-hour momentum (JFE-grade but adjacent families failed on MNQ — treat as fragile), #7 announcement momentum (funded-only).
- The PRD's core premise is strengthened: the payoff asymmetry of the eval structure is the *only* reason to attempt this; the literature offers no durable fast-intraday alpha to a retail bot.

## Open Questions

- Boyarchenko staff report primary (SSRN + NY Fed both 403): exact overnight accrual hours and post-2020 ES magnitude unverified — fetch the PDF another way or measure directly in Phase 1 data.
- Whether Gao-Han-Li-Zhou first-half-hour momentum survives on MES/MNQ 2020–2026 specifically — Mesfin's "cross-session momentum" family failed, but his family definitions may not include the exact 9:30–10:00 → 15:30–16:00 formulation.
- Lucid's ruling on holding a Globex position through the night (gates the entire overnight-drift sleeve) — Phase 0, in writing.
- DeepScalper and DRL-intraday papers unread beyond abstracts; low expected value, revisit only if Phase 1 A/B families all fail.

## Sources

- [[mesfin2026-mnq-intraday-falsification]] — Mesfin, 2026-05
- [[glasserman2025-overnight-news]] — Glasserman, Krstovski, Laliberte, Mamaysky, 2025-07
- [[boyarchenko-larsen-whelan-overnight-drift]] — Boyarchenko, Larsen, Whelan (NY Fed SR 917)
- [[byrd-balch-2019-intraday-ml-market-efficiency]] — Byrd & Balch, 2019-08
- [[knuteson2020-overnight-intraday-returns]] — Knuteson, 2020-10
