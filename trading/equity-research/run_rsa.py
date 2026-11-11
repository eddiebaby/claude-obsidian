"""Reverse-split arbitrage scan. Research only: nothing here places orders.
Pulls 8-K/6-K reverse-split announcements (last --days) and round-up proxies (last --proxy-days) from EDGAR full-text
search, reads each filing's fractional-share treatment, and ranks per-holder round-ups by gain per account:
1 share bought at price p becomes 1 post-split share worth about ratio x p.
Usage: python run_rsa.py [--days 30] [--proxy-days 90] [--as-of YYYY-MM-DD] [--alert | --alert-all]
Writes reports/rsa-YYYY-MM-DD.md and data/rsa/YYYY-MM-DD.csv."""
import argparse
import csv
from datetime import date, timedelta
from pathlib import Path

import yfinance as yf

from eqr.rsa import (ANNOUNCE_FORMS, ANNOUNCE_QUERIES, PROXY_FORMS, PROXY_QUERIES, fts_url, hit_meta, merge_events,
                     named_ticker, parse_doc, round_up_clause)
from eqr.rsa_alert import alerts, load_sent, message, ntfy, push_text, save_sent, session_day, title
from eqr.wires import Names, wire_docs
from run_filings import text_of
from run_screen import client

EXCHANGES = "https://www.sec.gov/files/company_tickers_exchange.json"
DOC_EXT = (".htm", ".html", ".txt")
MAX_HITS_PER_QUERY = 1000
OPEN = ("OPEN", "TODAY")
BUYABLE = ("UP",)
CHECK = ("MIXED", "UNKNOWN", "UP_PARTICIPANT", "UP_EARLIER")
LISTED = ("Nasdaq", "NYSE", "CBOE")     # SEC's exchange labels; OTC names are mostly not tradable on Robinhood
WATCH_MAX = 15
SPLIT_SEEN_DAYS = 10    # a price-history split this close before the filing is the split the filing describes
BACKFILL_FORMS = ANNOUNCE_FORMS + "," + PROXY_FORMS
BACKFILL_DAYS = 365     # boards often split under a proxy approved months earlier
SENT = "data/rsa/alerts_sent.json"


def search(sec, queries, forms, start, end, ciks=None):
    hits = {}
    for q in queries:
        frm = 0
        while True:
            d = (sec.get_json(fts_url(q, forms, start, end, frm, ciks), max_age_hours=3) or {}).get("hits", {})
            page = d.get("hits", [])
            hits.update((h["_id"], h) for h in page)
            frm += len(page)
            if not page or frm >= min(d.get("total", {}).get("value", 0), MAX_HITS_PER_QUERY):
                break
    return list(hits.values())


def exchanges(sec):
    j = sec.get_json(EXCHANGES) or {}
    i_cik, i_ex = j.get("fields", []).index("cik"), j.get("fields", []).index("exchange")
    out = {}
    for row in j.get("data", []):
        out.setdefault(row[i_cik], row[i_ex])
    return out


def company_rows(sec):
    """(cik, name, ticker) for every listed company SEC knows."""
    j = sec.get_json(EXCHANGES) or {}
    f = j.get("fields", [])
    return [(r[f.index("cik")], r[f.index("name")], r[f.index("ticker")]) for r in j.get("data", [])]


def market(ticker):
    """-> (last close, [split dates in the last 6 months])."""
    try:
        h = yf.Ticker(ticker).history(period="6mo", auto_adjust=False)
    except Exception:  # yfinance raises a zoo of errors for delisted/foreign symbols
        return None, []
    if not len(h):
        return None, []
    return float(h["Close"].dropna().iloc[-1]), [i.date() for i, v in h["Stock Splits"].items() if v]


def read(sec, hits):
    metas = [m for m in (hit_meta(h) for h in hits) if m["url"].lower().endswith(DOC_EXT)]
    docs = []
    for i, m in enumerate(metas, 1):
        if i % 50 == 0:
            print(f"  read {i}/{len(metas)}")
        text = text_of(sec.get_text(m["url"], max_age_hours=float("inf")) or "")
        docs.append({**m, "ticker": named_ticker(m["tickers"], text), **parse_doc(text, m["filed"])})
    return docs


def backfill(sec, wires, docs, end):
    """Wire releases that don't say how fractions are handled: the company's own filings from the last year (the
    proxy that authorized the split, an earlier split's 8-K) give its policy. They only fill in the rounding."""
    known = {d["cik"] for d in docs if not d.get("wire") and d["rounding"] != "UNKNOWN"}
    seen = {d["url"] for d in docs}
    out = []
    for cik in sorted({d["cik"] for d in wires if d["rounding"] == "UNKNOWN"} - known):
        hits = search(sec, ANNOUNCE_QUERIES, BACKFILL_FORMS, end - timedelta(BACKFILL_DAYS), end, ciks=f"{cik:010d}")
        out += [{**d, "precedent": True} for d in read(sec, hits) if d["url"] not in seen]
    return out


def scan(sec, today, days, proxy_days):
    end = min(today, date.today())      # --as-of may be a future day; nothing is filed past today
    hits = (search(sec, ANNOUNCE_QUERIES, ANNOUNCE_FORMS, end - timedelta(days), end) +
            search(sec, PROXY_QUERIES, PROXY_FORMS, end - timedelta(proxy_days), end))
    docs = read(sec, hits)
    print(f"{len(hits)} search hits -> {len(docs)} documents from {len({d['cik'] for d in docs})} companies")
    wires = wire_docs(Names(company_rows(sec)), end, days, dated={d["cik"] for d in docs if d["split_day"]})
    print(f"{len(wires)} split releases on the wires from {len({d['cik'] for d in wires})} companies")
    docs += wires + backfill(sec, wires, docs, end)
    return merge_events(docs, today)


def enrich(sec, events):
    ex = exchanges(sec)
    for e in events:
        e["exchange"] = ex.get(e["cik"])
        if e["exchange"] == "OTC":
            e["flags"].append("OTC: Robinhood may not trade it")
        priced = e["ticker"] and e["status"] in OPEN + ("NO_DATE",) and e["rounding"] not in ("CASH", "DOWN")
        e["price"], splits = market(e["ticker"]) if priced else (None, [])
        since = date.fromisoformat(str(e["filed"])) - timedelta(SPLIT_SEEN_DAYS)
        if e["status"] == "NO_DATE" and any(d >= since for d in splits):
            e["status"] = "DONE"    # undated in the filings, but the price history shows it already happened
            e["flags"].append(f"already split {max(splits)} per price history")
        r = e["ratio"]
        e["gain_per_acct"] = round(e["price"] * (r - 1), 2) if e["price"] and r else None


def _ratio(e):
    if e["ratio"]:
        return f"1:{e['ratio']}"
    lo, hi = e["ratio_range"] or (None, None)
    return f"1:{lo or '?'}-{hi}" if hi else "?"


def _money(x):
    if x is None:
        return "?"
    return f"${x:,.3f}" if x < 1 else f"${x:,.2f}"


def _day(d):
    return f"{d:%a %b} {d.day}" if d else "TBD"


def sections(events):
    by_day = lambda e: (e["buy_by"] or date.max, -(e["gain_per_acct"] or 0))
    opened = [e for e in events if e["status"] in OPEN]
    act = sorted((e for e in opened if e["rounding"] in BUYABLE and not e.get("vote")), key=by_day)
    vote = sorted((e for e in opened if e["rounding"] in BUYABLE + CHECK and e.get("vote")), key=by_day)
    check = sorted((e for e in opened if e["rounding"] in CHECK and not e.get("vote")), key=by_day)
    watch = sorted((e for e in events if e["status"] == "NO_DATE" and e["rounding"] in BUYABLE
                    and e.get("exchange") in LISTED), key=lambda e: e["filed"], reverse=True)
    watch = sorted(watch, key=lambda e: -(e["gain_per_acct"] or 0))[:WATCH_MAX]   # biggest known profit first
    return act, vote, check, watch


def _vote_line(v, today):
    if v == date.max:
        return "⚠ needs shareholder vote (meeting date not found)"
    if v < today:
        return f"⚠ vote was {_day(v)}: confirm it passed before buying"
    return f"⚠ needs shareholder vote {_day(v)}: buy only after it passes"


def card(e, wording=True, today=None):
    """One event in the RSA-tracker layout: ticker/name/exchange, split, price, profit, then the dates, then the
    filing's fractional-share wording with the round-up phrase bolded."""
    lines = [f"**${e['ticker'] or '?'}** ({e['name']} @ {e.get('exchange') or '?'})",
             f"Split {_ratio(e)} · Price {_money(e['price'])} · Profit {_money(e['gain_per_acct'])}",
             f"Buy by {_day(e['buy_by'])} close · Splits {_day(e['split_day'])} · "
             f"[{'filing' if 'sec.gov' in e['urls'][0] else 'release'}]({e['urls'][0]})"]
    if e.get("vote"):
        lines.append(_vote_line(e["vote"], today or date.today()))
    if e["flags"]:
        lines.append(f"⚠ {'; '.join(e['flags'])}")
    if wording and e["excerpt"]:
        lines.append(f"Wording: \"{round_up_clause(e['excerpt'])}\"")
    return "  \n".join(lines)


def table(rows, today=None):
    return "\n\n".join(card(e, today=today) for e in rows) if rows else "_None._"


def report(events, today):
    act, vote, check, watch = sections(events)
    done = sum(e["status"] in ("DONE", "MISSED") for e in events)
    cash = sum(e["rounding"] in ("CASH", "DOWN") for e in events)
    return "\n\n".join([
        f"# Reverse-split scan {today}",
        f"Profit = price × ratio − price, for 1 share, before the post-split fade. Buy 1 whole share by "
        f"the close on the buy-by day. Robinhood posts round-ups about 3-4 weeks later. Research only, not orders.",
        f"## BUY: rounds up per holder ({len(act)})", table(act, today=today),
        f"## PENDING VOTE: dated round-up, shareholders still voting ({len(vote)})",
        table(vote, today=today),
        f"## CHECK by hand before buying ({len(check)})",
        "UP_PARTICIPANT = rounded at the broker, usually no extra share; MIXED = round-up and cash both mentioned; "
        "UNKNOWN = no fractional-share wording found; UP_EARLIER = round-up wording only in an earlier filing "
        "(a past split or an older proxy), not this split's.", table(check, today=today),
        f"## WATCH: round-up wording, no date yet (top {len(watch)} by profit, listed only)",
        "No date on EDGAR, GlobeNewswire, or Google News headlines yet. Wires with no feed (ACCESS, Business Wire) "
        "show up only when a headline carries the date.",
        "\n".join(f"- **${e['ticker'] or '?'}** {_ratio(e)} · {_money(e['price'])} · "
                  f"Profit {_money(e['gain_per_acct'])} · {e['exchange']} · "
                  + (f"vote pending, proposed {_day(e['proposed_day'])} · " if e.get("proposed_day") else "")
                  + f"{e['stage']} filed {e['filed']} · [filing]({e['urls'][0]})" for e in watch) or "_None._",
        f"_Skipped {done} splits already past their buy window and {cash} that pay cash or round down._",
    ]) + "\n"


def alert(events, today, remember=True, everything=False):
    """Prints 'ALERT ...' lines (a scheduled run greps for them), saves the push text to data/rsa/alert.txt, pushes
    via ntfy when configured, and remembers what was sent so each alert fires once. A failed push isn't remembered,
    so the next run retries it. remember=False (an --as-of run) leaves the sent-alerts file alone; everything=True
    sends the whole current picture as if nothing had been sent, and also leaves the file alone."""
    sent = set() if everything else load_sent(SENT)
    groups, keys = alerts(*sections(events), events, sent, today)
    text = message(groups)
    Path("data/rsa").mkdir(parents=True, exist_ok=True)
    Path("data/rsa/alert.txt").write_text(text + ("\n" if text else ""), encoding="utf-8")
    pushed, failed = False, False
    try:
        pushed = ntfy(groups)
    except Exception as e:  # the alert stays in the output and alert.txt, and is retried next run
        print(f"ntfy push failed: {e}")
        failed = True
    if remember and not everything and not failed:
        save_sent(SENT, sent | keys)
    if text:
        print(f"ALERT-TITLE {title(groups)}")
        print("\n".join(f"ALERT {line}" for line in text.split("\n")))
    print(f"ALERT-PUSH {push_text(groups)}" if text else "ALERT none")
    if pushed:
        print("pushed via ntfy")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--proxy-days", type=int, default=90)
    ap.add_argument("--as-of", type=date.fromisoformat, default=None,
                    help="judge buy windows as of this day (default: today, or the next session after the close)")
    ap.add_argument("--alert", action="store_true",
                    help="print new buys / last days / dropped buys once each; push via ntfy if NTFY_TOPIC is set")
    ap.add_argument("--alert-all", action="store_true",
                    help="push the whole current BUY / CHECK / WATCH picture, ignoring (and not updating) what was sent")
    a = ap.parse_args()
    sec, today = client(), a.as_of or session_day()
    events = scan(sec, today, a.days, a.proxy_days)
    enrich(sec, events)
    md = report(events, today)
    if a.alert or a.alert_all:
        alert(events, today, remember=a.as_of is None, everything=a.alert_all)
    Path("reports").mkdir(exist_ok=True)
    Path(f"reports/rsa-{today}.md").write_text(md, encoding="utf-8")
    Path("data/rsa").mkdir(parents=True, exist_ok=True)
    cols = ["ticker", "name", "cik", "exchange", "stage", "status", "rounding", "ratio", "ratio_range", "buy_by",
            "split_day", "price", "gain_per_acct", "flags", "filed", "excerpt", "urls"]
    with open(f"data/rsa/{today}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for e in sorted(events, key=lambda e: (e["status"], str(e["buy_by"]))):
            w.writerow({**e, "flags": "; ".join(e["flags"]), "urls": " ".join(e["urls"])})
    if not a.alert:
        print(md)
    print(f"\nwrote reports/rsa-{today}.md and data/rsa/{today}.csv ({len(events)} events)")


if __name__ == "__main__":
    main()
