"""The engine: daily mark-to-market on the contract actually held.

What makes this a futures backtester rather than an equity one:

  * P&L is `contracts * multiplier * (settle_t - settle_t-1) * fx`, in integer
    contracts. No fractional shares, no `weight * return`.
  * Rolls are trades. On the roll date the held contract is sold and the next
    bought at that day's settles, and both legs pay commission and slippage.
  * Margin is posted, not spent. The balance earns the collateral rate, and the
    book is capped at a margin-to-equity ceiling instead of a leverage ratio.
  * Signals are lagged. A signal read at the close of day t-1 is filled at the
    close of day t (`execution_lag`), so no decision uses its own fill price.

Order of operations inside one day, which is where subtle lookahead usually
hides:

  1. mark existing positions to today's settle of the contract held,
  2. accrue collateral interest on yesterday's closing equity,
  3. rebalance (only on rebalance dates, using signals as of t - lag),
  4. roll any contract whose holding period ends today, at today's settles,
  5. enforce the margin ceiling; de-risk if breached,
  6. write the day's record.
"""
from __future__ import annotations

import bisect
import math
from dataclasses import dataclass, field
from datetime import date

import contracts as cx
import roll as rollmod
import sizing as sz
from data import MarketData, RateSeries, constant_rate

TRADING_DAYS = 252

DAILY, WEEKLY, MONTHLY = "daily", "weekly", "monthly"
REBALANCES = (DAILY, WEEKLY, MONTHLY)


@dataclass
class BacktestConfig:
    start: date | None = None
    end: date | None = None
    initial_equity: float = 100_000.0

    # risk
    vol_target: float = 0.10           # annualised portfolio vol target
    vol_span: int = 60                 # EWMA span for per-market vol
    vol_weight_recent: float = 0.7     # blend of EWMA vol vs long-run vol
    vol_lookback_cap: int = 1260       # bars fed to the vol estimator
    weights: dict[str, float] | None = None   # per-market risk weights
    idm: float | None = None           # None -> idm_for(n_markets, avg_corr)
    avg_corr: float = 0.15
    max_margin_to_equity: float = 0.25

    # trading
    rebalance: str = WEEKLY
    execution_lag: int = 1             # bars between signal and fill
    buffer_frac: float = 0.10          # no-trade band, in units of full size
    min_history: int = 260             # bars required before a market trades
    fixed_contracts: dict[str, int] | None = None
    """Bypass risk sizing and hold `signal * n` contracts per market.

    Two uses: a "long 1 contract" benchmark to compare a strategy against, and
    a test harness where the position is known exactly so engine P&L can be
    checked against hand arithmetic."""

    # market mechanics
    roll_method: str = rollmod.CALENDAR
    roll_offset_days: int | None = None
    adjust: str = rollmod.PANAMA
    slippage_ticks: float | None = None    # override every spec
    commission: float | None = None        # override every spec
    rates: RateSeries | None = None
    fx: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.rebalance not in REBALANCES:
            raise ValueError(f"rebalance must be one of {REBALANCES}")
        if self.execution_lag < 0:
            raise ValueError("execution_lag must be >= 0")
        if self.initial_equity <= 0:
            raise ValueError("initial_equity must be positive")
        if self.rates is None:
            self.rates = constant_rate(0.04)

    def cost_per_contract(self, spec: cx.ContractSpec) -> float:
        commission = spec.commission if self.commission is None else self.commission
        ticks = spec.slippage_ticks if self.slippage_ticks is None else self.slippage_ticks
        return commission + ticks * spec.tick_value


@dataclass
class Trade:
    date: date
    symbol: str
    code: str                  # the delivery month actually traded
    contracts: int             # signed change in position
    price: float
    cost: float
    reason: str                # signal | roll | margin | liquidation


@dataclass
class DailyRecord:
    date: date
    equity: float
    ret: float
    gross_pnl: float           # mark-to-market before costs and interest
    interest: float
    costs: float
    margin: float
    margin_to_equity: float
    gross_notional: float
    positions: dict[str, int]
    markets_held: int
    effective_markets: float


@dataclass
class BacktestResult:
    config: BacktestConfig
    symbols: list[str]
    records: list[DailyRecord]
    trades: list[Trade]
    pnl_by_market: dict[str, float]
    costs_by_reason: dict[str, float]
    contracts_traded: dict[str, int]
    roll_report: dict[str, list[dict]]
    warnings: list[str]
    blown_up: bool = False
    _multipliers: dict = field(default_factory=dict)
    capped_days: int = 0        # rebalances whose target hit the margin ceiling
    derisk_days: int = 0        # days the book was forcibly shrunk
    margin_calls: int = 0       # days maintenance margin exceeded equity

    @property
    def dates(self) -> list[date]:
        return [r.date for r in self.records]

    @property
    def returns(self) -> list[float]:
        return [r.ret for r in self.records]

    @property
    def equity_curve(self) -> list[float]:
        return [r.equity for r in self.records]

    @property
    def final_equity(self) -> float:
        return self.records[-1].equity if self.records else self.config.initial_equity

    def years(self) -> float:
        return len(self.records) / TRADING_DAYS

    def total_costs(self) -> float:
        return sum(self.costs_by_reason.values())

    def avg_equity(self) -> float:
        if not self.records:
            return self.config.initial_equity
        return sum(r.equity for r in self.records) / len(self.records)

    def cost_drag(self) -> float:
        """Annualised cost as a fraction of *average* equity — the number that
        decides whether a signal survives contact with the tape.

        Average, not starting, equity: on a compounding book the contract count
        grows with the account, so costs measured against day-one equity make a
        good run look expensive and a bad one look cheap.
        """
        y, base = self.years(), self.avg_equity()
        if y <= 0 or base <= 0:
            return 0.0
        return self.total_costs() / y / base

    def turnover_notional(self) -> float:
        """Notional traded per year divided by average equity — comparable
        across account sizes, unlike a raw contract count."""
        y, base = self.years(), self.avg_equity()
        if y <= 0 or base <= 0:
            return 0.0
        traded = sum(abs(t.contracts) * t.price * self.config_spec_multiplier(t.symbol)
                     for t in self.trades)
        return traded / y / base

    def config_spec_multiplier(self, symbol: str) -> float:
        return self._multipliers.get(symbol, 1.0)

    def turnover(self) -> float:
        """Contracts traded per year, all markets, all reasons."""
        y = self.years()
        return sum(self.contracts_traded.values()) / y if y > 0 else 0.0

    def avg_margin_to_equity(self) -> float:
        if not self.records:
            return 0.0
        return sum(r.margin_to_equity for r in self.records) / len(self.records)

    def peak_margin_to_equity(self) -> float:
        return max((r.margin_to_equity for r in self.records), default=0.0)


class Backtest:
    """One configuration, one universe, one run."""

    def __init__(self, markets: dict[str, MarketData], config: BacktestConfig,
                 strategy):
        if not markets:
            raise ValueError("no markets")
        self.markets = markets
        self.config = config
        self.strategy = strategy
        self.warnings: list[str] = []
        self.contracts_traded: dict[str, int] = {}
        self.costs_by_reason: dict[str, float] = {}
        self.capped_days = self.derisk_days = self.margin_calls = 0
        self._vol_cache: dict[tuple, float | None] = {}

        self.specs = {s: m.spec for s, m in markets.items()}
        self.segments: dict[str, list[rollmod.Segment]] = {}
        self.seg_of_day: dict[str, dict[date, rollmod.Segment]] = {}
        self.seg_index: dict[str, dict[str, int]] = {}
        self.adj_dates: dict[str, list[date]] = {}
        self.adj_vals: dict[str, list[float]] = {}
        self.raw_vals: dict[str, list[float]] = {}   # unadjusted, for % vol

        for sym, m in markets.items():
            segs = rollmod.roll_schedule(m, offset_days=config.roll_offset_days,
                                         method=config.roll_method,
                                         start=config.start, end=config.end)
            self.segments[sym] = segs
            self.seg_of_day[sym] = rollmod.held_contract(segs)
            self.seg_index[sym] = {id(s): i for i, s in enumerate(segs)}
            adj = rollmod.continuous(segs, method=config.adjust)
            ds = sorted(adj)
            self.adj_dates[sym] = ds
            self.adj_vals[sym] = [adj[d] for d in ds]
            self.raw_vals[sym] = [self.seg_of_day[sym][d].close(d) or adj[d]
                                  for d in ds]
            if any(v <= 0 for v in self.adj_vals[sym]):
                self.warnings.append(
                    f"{sym}: back-adjusted series goes non-positive — level-based "
                    "signals are meaningless here; difference-based ones are fine")
            gaps = [g for g in rollmod.roll_gaps(segs) if g["gap_roll"]]
            if gaps:
                self.warnings.append(
                    f"{sym}: {len(gaps)} roll(s) with no overlapping quote — "
                    "position carried across a data hole, gap not priced")

        self.calendar = self._build_calendar()
        self.rebalance_days = self._rebalance_days()

    # --- calendar ----------------------------------------------------------

    def _build_calendar(self) -> list[date]:
        days: set[date] = set()
        for sym in self.markets:
            days.update(self.seg_of_day[sym])
        cal = sorted(days)
        if self.config.start:
            cal = [d for d in cal if d >= self.config.start]
        if self.config.end:
            cal = [d for d in cal if d <= self.config.end]
        if len(cal) < 2:
            raise ValueError("fewer than 2 trading days in range")
        return cal

    def _rebalance_days(self) -> set[date]:
        cal = self.calendar
        if self.config.rebalance == DAILY:
            return set(cal)
        if self.config.rebalance == WEEKLY:
            key = lambda d: d.isocalendar()[:2]
        else:
            key = lambda d: (d.year, d.month)
        last: dict[tuple, date] = {}
        for d in cal:
            last[key(d)] = d
        return set(last.values())

    # --- helpers -----------------------------------------------------------

    def _fx(self, spec: cx.ContractSpec) -> float:
        return self.config.fx.get(spec.currency, 1.0)

    def _history(self, sym: str, as_of: date) -> list[float]:
        """Adjusted closes strictly up to and including `as_of` (no lookahead)."""
        k = bisect.bisect_right(self.adj_dates[sym], as_of)
        cap = self.config.vol_lookback_cap
        return self.adj_vals[sym][max(0, k - cap):k]

    def _raw_history(self, sym: str, as_of: date) -> list[float]:
        """Unadjusted closes over the same window — the denominator for % vol."""
        k = bisect.bisect_right(self.adj_dates[sym], as_of)
        cap = self.config.vol_lookback_cap
        return self.raw_vals[sym][max(0, k - cap):k]

    def _vol(self, sym: str, as_of: date) -> float | None:
        """Blended vol as of a date, memoised — the estimator walks up to five
        years of history, and the loop would otherwise redo that every day."""
        key = (sym, as_of)
        if key in self._vol_cache:
            return self._vol_cache[key]
        self._vol_cache[key] = v = self._compute_vol(sym, as_of)
        return v

    def _compute_vol(self, sym: str, as_of: date) -> float | None:
        spec = self.specs[sym]
        return sz.blended_vol(self._history(sym, as_of),
                             span=self.config.vol_span, basis=spec.vol_basis,
                             weight_recent=self.config.vol_weight_recent,
                             base=self._raw_history(sym, as_of))

    def _close_on(self, sym: str, d: date) -> float | None:
        seg = self.seg_of_day[sym].get(d)
        return None if seg is None else seg.close(d)

    def _trade(self, trades, d, sym, seg, delta: int, price: float, reason: str):
        if delta == 0:
            return 0.0
        spec = self.specs[sym]
        cost = abs(delta) * self.config.cost_per_contract(spec)
        trades.append(Trade(d, sym, seg.code, delta, price, cost, reason))
        self.contracts_traded[sym] = self.contracts_traded.get(sym, 0) + abs(delta)
        self.costs_by_reason[reason] = self.costs_by_reason.get(reason, 0.0) + cost
        return cost

    # --- the loop ----------------------------------------------------------

    def run(self) -> BacktestResult:
        cfg = self.config
        cal = self.calendar
        syms = sorted(self.markets)

        pos: dict[str, int] = {s: 0 for s in syms}
        cur_seg: dict[str, rollmod.Segment | None] = {s: None for s in syms}
        last_px: dict[str, float | None] = {s: None for s in syms}

        self.contracts_traded = {}
        self.costs_by_reason = {}
        self.capped_days = 0
        self.derisk_days = 0
        self.margin_calls = 0
        pnl_by_market: dict[str, float] = {s: 0.0 for s in syms}

        idm = cfg.idm if cfg.idm is not None else sz.idm_for(len(syms), cfg.avg_corr)
        weights = cfg.weights or {s: 1.0 / len(syms) for s in syms}

        equity = cfg.initial_equity
        risk_each: dict[str, float] = {}   # per-contract risk, refreshed on rebalances
        records: list[DailyRecord] = []
        trades: list[Trade] = []
        blown_up = False

        for i, d in enumerate(cal):
            prev_equity = equity
            gross_pnl = 0.0
            costs = 0.0

            # 1. mark to market on the contract held
            for s in syms:
                seg = self.seg_of_day[s].get(d)
                if seg is None:
                    continue
                if cur_seg[s] is None:
                    cur_seg[s], last_px[s] = seg, seg.close(d)
                    continue
                if seg.code != cur_seg[s].code:
                    # the roll happens at step 4 of the roll date; arriving here
                    # means the old contract stopped quoting first
                    cur_seg[s], last_px[s] = seg, seg.close(d)
                    continue
                px = seg.close(d)
                if px is None or last_px[s] is None:
                    continue
                if pos[s]:
                    spec = self.specs[s]
                    pnl = pos[s] * spec.multiplier * (px - last_px[s]) * self._fx(spec)
                    gross_pnl += pnl
                    pnl_by_market[s] += pnl
                last_px[s] = px

            # 2. collateral interest on yesterday's equity
            interest = prev_equity * cfg.rates.daily(d) if prev_equity > 0 else 0.0

            # 3. rebalance on schedule, from lagged signals
            if d in self.rebalance_days and i >= cfg.execution_lag:
                signal_date = cal[i - cfg.execution_lag]
                # Size on yesterday's closing equity: the order is placed before
                # today's settle is known.
                target, risk_each = self._targets(syms, d, signal_date, prev_equity,
                                                  weights, idm, pos)
                target, capped = sz.scale_to_margin_cap(
                    target, self._prices(syms, d), self.specs, prev_equity,
                    cfg.max_margin_to_equity)
                if capped:
                    self.capped_days += 1
                for s in syms:
                    seg = self.seg_of_day[s].get(d)
                    px = self._close_on(s, d)
                    if seg is None or px is None:
                        continue
                    delta = target[s] - pos[s]
                    if delta:
                        costs += self._trade(trades, d, s, seg, delta, px, "signal")
                        pos[s] = target[s]

            # 4. roll any holding period that ends today, at today's settles
            for s in syms:
                seg = cur_seg[s]
                if seg is None or seg.end != d or not seg.rolled:
                    continue
                idx = self.seg_index[s].get(id(seg))
                if idx is None or idx + 1 >= len(self.segments[s]):
                    continue
                nxt = self.segments[s][idx + 1]
                old_px = seg.close(d)
                new_px = nxt.contract.close(d)
                if pos[s]:
                    if old_px is not None:
                        costs += self._trade(trades, d, s, seg, -pos[s], old_px, "roll")
                    if new_px is not None:
                        costs += self._trade(trades, d, s, nxt, pos[s], new_px, "roll")
                    elif seg.gap_roll:
                        self.warnings.append(
                            f"{s}: re-entered {nxt.code} across a data gap on {d}")
                cur_seg[s] = nxt
                last_px[s] = new_px if new_px is not None else nxt.contract.close(
                    nxt.dates()[0] if nxt.dates() else d)

            # 5. margin ceiling, then solvency
            equity = prev_equity + gross_pnl + interest - costs
            prices = self._prices(syms, d)
            init_margin = sz.margin_required(pos, prices, self.specs)
            if equity > 0 and init_margin > equity * cfg.max_margin_to_equity:
                shrunk, _ = sz.scale_to_margin_cap(pos, prices, self.specs, equity,
                                                   cfg.max_margin_to_equity)
                for s in syms:
                    delta = shrunk[s] - pos[s]
                    seg, px = cur_seg[s], self._close_on(s, d)
                    if delta and seg is not None and px is not None:
                        c = self._trade(trades, d, s, seg, delta, px, "margin")
                        costs += c
                        equity -= c
                        pos[s] = shrunk[s]
                self.derisk_days += 1
            maint = sz.margin_required(pos, prices, self.specs, maintenance=True)
            if equity > 0 and maint > equity:
                self.margin_calls += 1
                self.warnings.append(
                    f"maintenance margin exceeded equity on {d} — a real broker "
                    "would have liquidated into the move")
            if equity <= 0:
                for s in syms:
                    seg, px = cur_seg[s], self._close_on(s, d)
                    if pos[s] and seg is not None and px is not None:
                        equity -= self._trade(trades, d, s, seg, -pos[s], px,
                                              "liquidation")
                        pos[s] = 0
                blown_up = True
                self.warnings.append(f"equity hit zero on {d} — run stopped")

            # 6. record
            margin = sz.margin_required(pos, prices, self.specs)
            notional_sum = sum(
                abs(sz.notional(self.specs[s], prices[s], pos[s], self._fx(self.specs[s])))
                for s in syms if pos[s] and prices.get(s))
            if not risk_each and any(pos.values()):
                risk_each = self._risk_each(syms, d, cal[max(0, i - cfg.execution_lag)])
            div = sz.diversification(pos, risk_each, intended=len(syms))
            records.append(DailyRecord(
                date=d, equity=equity,
                ret=(equity / prev_equity - 1.0) if prev_equity > 0 else 0.0,
                gross_pnl=gross_pnl, interest=interest, costs=costs,
                margin=margin,
                margin_to_equity=(margin / equity) if equity > 0 else float("inf"),
                gross_notional=notional_sum, positions=dict(pos),
                markets_held=div.held, effective_markets=div.effective))
            if blown_up:
                break

        return BacktestResult(
            config=cfg, symbols=syms, records=records, trades=trades,
            pnl_by_market=pnl_by_market, costs_by_reason=dict(self.costs_by_reason),
            contracts_traded=dict(self.contracts_traded),
            _multipliers={s: self.specs[s].multiplier for s in syms},
            roll_report={s: rollmod.roll_gaps(self.segments[s]) for s in syms},
            warnings=list(dict.fromkeys(self.warnings)), blown_up=blown_up,
            capped_days=self.capped_days, derisk_days=self.derisk_days,
            margin_calls=self.margin_calls)

    # --- sizing ------------------------------------------------------------

    def _prices(self, syms, d) -> dict[str, float]:
        out = {}
        for s in syms:
            px = self._close_on(s, d)
            if px is not None:
                out[s] = px
        return out

    def _risk_each(self, syms, d, signal_date) -> dict[str, float]:
        """Annualised dollar risk of one contract, per market, as of the lag date."""
        out = {}
        for s in syms:
            spec = self.specs[s]
            hist = self._history(s, signal_date)
            vol = self._vol(s, signal_date)
            px = self._close_on(s, d) or (hist[-1] if hist else None)
            if vol is None or px is None:
                continue
            r = sz.risk_per_contract(spec, px, vol, self._fx(spec))
            if r > 0:
                out[s] = r
        return out

    def _targets(self, syms, d, signal_date, equity, weights, idm, pos):
        """Target integer contracts per market, plus each market's unit risk."""
        cfg = self.config
        min_hist = max(cfg.min_history, getattr(self.strategy, "min_history", 0))
        target: dict[str, int] = {s: pos[s] for s in syms}
        risk_each: dict[str, float] = {}

        for s in syms:
            spec = self.specs[s]
            hist = self._history(s, signal_date)
            px_now = self._close_on(s, d)
            if px_now is None:                     # no quote: cannot trade today
                continue
            if cfg.fixed_contracts is not None:
                signal = self.strategy(hist) if hist else None
                n = cfg.fixed_contracts.get(s, 0)
                target[s] = 0 if signal is None else int(round(max(-1.0, min(1.0, signal)) * n))
                vol = self._vol(s, signal_date)
                if vol is not None:
                    risk_each[s] = sz.risk_per_contract(spec, px_now, vol, self._fx(spec))
                continue
            if len(hist) < min_hist:
                target[s] = 0
                continue
            vol = self._vol(s, signal_date)
            signal = self.strategy(hist)
            if vol is None or signal is None:
                target[s] = 0
                continue
            # Size off the lagged price, fill at today's close: the decision
            # never uses a price it could not have seen.
            size_px = self._close_on(s, signal_date) or px_now
            scale = sz.position_scale(equity, spec, size_px, vol, weights.get(s, 0.0),
                                      cfg.vol_target, idm, self._fx(spec))
            raw = max(-1.0, min(1.0, signal)) * scale
            target[s] = sz.buffered_target(pos[s], raw, scale, cfg.buffer_frac)
            risk_each[s] = sz.risk_per_contract(spec, px_now, vol, self._fx(spec))
        return target, risk_each


def run(markets: dict[str, MarketData], config: BacktestConfig, strategy) -> BacktestResult:
    return Backtest(markets, config, strategy).run()
