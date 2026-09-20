# Getting real data into the engine

Everything the engine prints on synthetic bars is plumbing validation. This is
the checklist that turns it into a result you can act on. Work top to bottom;
step 1 is free and may end the exercise.

## 1. Check capacity before you spend a dollar (free, 10 seconds)

```bash
python3 capacity.py --equity 100000
```

If the account cannot hold the book, no data purchase fixes that. As of the
reference prices in `contracts.py`:

| Equity | Book the account can actually hold |
|---|---|
| $25–50K | `MCL, M6E, M6B, 10Y` (4 markets) |
| $100–150K | `M2K, MGC, MCL, M6E, M6B, 10Y` (6 markets) |
| $250K+ | the full 8 micros, MES and MNQ included |

MES needs $203K of equity to justify one contract at 1/8 weight; MNQ needs
$340K. A $100K account running the 8-market list is a 5-market book with three
permanently flat lines in it, at 0.66x its stated risk.

## 2. The history trap — read this before choosing a vendor

**The micros do not have the history the strategy needs.** MES and MNQ launched
May 2019; M2K, M6E and M6B later; Micro 10-Year Yield in 2021. Seven years is
not a sample for a strategy whose entire value shows up in rare years (2008,
2020, 2022).

So: **backtest the parent, trade the micro.** The contracts track the same
underlying at a different multiplier, so the price history is the parent's and
the contract arithmetic is the micro's. The engine does this for you — put the
parent's files in the micro's directory and `data.load_market` picks them up,
keeping the micro's multiplier, tick and margin:

| Trade | Backtest on | Years available |
|---|---|---|
| MES | ES | 1997– |
| MNQ | NQ | 1999– |
| M2K | RTY | 2017– (use it knowing it is short) |
| MGC | GC | 1975– |
| SIL | SI | 1975– |
| MCL | CL | 1983– |
| M6E | 6E | 1999– |
| M6B | 6B | 1975– |
| 10Y | **nothing** | Micro 10Y Yield is quoted in *yield*; ZN is quoted in *dollars*. Different instruments — never substitute. Either trade 10Y on its short history at half risk weight, or use ZN as its own market. |

Half-weight anything whose history is short (`risk_weight=0.5` on the spec),
which the registry already does for MBT.

## 3. Buy the data

The engine needs **individual delivery-month bars** (not a vendor's
back-adjusted continuous file — that cannot price a roll) plus a short rate.

| Source | Gives you | Watch out |
|---|---|---|
| **Norgate Data** (Futures package) | Individual contracts + continuous, deep history, clean | Updater is Windows-native; fine under Parallels/a cheap VM. Check current pricing — do not trust a number from me. |
| **Databento** (GLBX.MDP3) | Pay-per-use API, individual contracts, cross-platform, scriptable | Daily bars are cheap; intraday is not. Budget the query before running it. |
| **CME DataMine** | Official settlements, authoritative | Priciest route, heaviest to reshape. |
| **IBKR API** | Free with an account | Limited history (years, not decades). Good for a pipeline smoke test, useless for judging the strategy. |

Verify pricing and platform requirements at purchase time. Start with one
market's full history, run step 5, then buy the rest — a pipeline bug is cheaper
to find on one symbol.

## 4. Reshape into the expected layout

One CSV per delivery month, named `<ROOT><MONTHCODE><YY>.csv`:

```
data/MES/ESH19.csv          <- parent bars are fine, see step 2
data/MES/ESM19.csv
data/MGC/GCG05.csv
data/irx.csv

date,open,high,low,close,volume,open_interest
2019-01-02,2476.25,2519.75,2467.00,2510.00,1842301,2904553
```

- `open/high/low` are optional (they default to the close); `close` must be the
  **settlement** price, which is what P&L marks against.
- `volume` / `open_interest` are optional; supply them to enable
  `--roll-method volume`.
- Month codes: F G H J K M N Q U V X Z = Jan…Dec.
- The rate file is any CSV with `date` and a percent-quoted annual yield;
  `^IRX` (13-week T-bill) works and is free from the same place
  `sector-momentum/data.py` already pulls it.

`make_sample_data.py --out ./data-demo` writes exactly this layout, so you can
diff your reshaping against a known-good tree. `data*/` is gitignored.

## 5. Run it, in this order

```bash
python3 capacity.py --equity 100000                    # the book to use
python3 run.py --data ./data --rates ./data/irx.csv \
               --equity 100000 --start 2000-01-01      # headline + rolls + costs
python3 walkforward.py --data ./data --rates ./data/irx.csv --equity 100000
python3 run.py --data ./data --rates ./data/irx.csv --compare   # roll sensitivity
```

## 6. Check these before believing any of it

In the order they are printed:

1. **Roll report** — does each market show roughly the expected number of rolls
   (4/yr quarterly, 12/yr monthly) and no cluster in the final fortnight? A
   cluster means the chain is rolling off truncated contracts.
2. **Realised vs target vol** — under 0.8x means the account cannot express the
   book, and the Sharpe describes positions you would not have held.
3. **Effective markets** — well below the number held means rounding has
   collapsed the diversification that is the entire thesis.
4. **Cost drag** — a slow trend book should be well under 1%/yr of equity. Above
   that, check the rebalance cadence and the roll schedule before blaming the
   signal.
5. **`--compare` roll sensitivity** — if Sharpe moves materially across
   calendar/volume × panama/ratio, the result is measuring the roll convention.
6. **Walk-forward verdict** — the config chosen on in-sample Sharpe, read
   out-of-sample. Expect degradation; expect a standalone net Sharpe of 0.4–0.7.
   If it prints much more than that, look for the bug before celebrating.
7. **Deflated Sharpe** — pass `--trials` the honest number of configurations you
   tried, including the abandoned ones and everything on the wiki roadmap. Six
   is almost always a lie.

## 7. Then stop and decide

A passing walk-forward is a licence to **paper trade**, not to fund. The failure
mode for this strategy is not a bad backtest, it is abandoning the sleeve in year
three of chop right before the year it pays for itself. Size it so you can sit in
it, and write down the kill criteria from
`wiki/concepts/Micro-Futures Trend Strategy.md` before the first order.
