"""Newswire press releases on reverse splits, for dates that never reach EDGAR (JOB's Nov 10, 2026 date was only in an
ACCESS Newswire release; NXTS's Nov 9 split was on GlobeNewswire a day before any 8-K). Two public feeds:
GlobeNewswire's search feed (JSON, with release text) and Google News search RSS (headlines from every wire, ACCESS
included). Release pages themselves are not fetched: GlobeNewswire and ACCESS Newswire refuse scripts."""
import json
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from email.utils import parsedate_to_datetime

import requests

from eqr.rsa import _MONTHS, MAX_LEAD_DAYS, normalize, parse_doc

UA = {"User-Agent": "eqr-rsa-scanner/0.1 (personal research script)"}   # the contact email is for SEC only
GNW = "https://rss.globenewswire.com/WpFeed/search/{q}"
GNEWS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
GNW_QUERIES = ('"reverse stock split"', '"reverse split"', '"share consolidation"')
GNEWS_QUERIES = ('"reverse stock split"', '"reverse split" effective', '"share consolidation" effective')
PAUSE = 1.0     # seconds between feed requests
FOLLOWUP_MAX = 30   # per-company headline searches per run

_SPLIT_TITLE = re.compile(r"reverse (?:stock |share )?split|share consolidation|consolidation of (?:its )?(?:\w+ )?"
                          r"shares", re.I)
_TICKER = re.compile(r"\((?:(?:NASDAQ|Nasdaq|NYSE(?: American| Arca)?|OTC\w*|CBOE)\s*:\s*)?([A-Z]{1,5})\)")
_SUFFIX = {"inc", "corp", "corporation", "co", "company", "ltd", "limited", "plc", "lp", "llc", "sa", "nv", "ag", "the"}
_HEAD_DAY = re.compile(r"effective\s+(?:on\s+)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+"
                       r"(\d{1,2})\b(?!,?\s*20\d\d)", re.I)


def _get(url, fetch):
    try:
        return fetch(url)
    except Exception as e:  # a feed outage shouldn't sink the EDGAR scan; the run says what it missed
        print(f"  wire feed failed: {url} ({e})")
        return None


def _requests_text(url):
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    time.sleep(PAUSE)
    return r.text


def norm_name(s):
    words = re.sub(r"[^a-z0-9]+", " ", s.lower().replace("&", " and ")).split()
    return " ".join(w for w in words if w not in _SUFFIX)


class Names:
    """SEC's ticker/exchange list, to tie a release to a company: by ticker, else by the company name it opens with."""

    def __init__(self, rows):
        """rows: (cik, name, ticker) from company_tickers_exchange.json."""
        self.by_ticker, self.by_name = {}, {}
        for cik, name, ticker in rows:
            self.by_ticker.setdefault(ticker, (cik, name, ticker))
            n = norm_name(name)
            if len(n) >= 5 or " " in n:
                self.by_name.setdefault(n, (cik, name, ticker))

    def ticker(self, t):
        return self.by_ticker.get((t or "").upper())

    def lead(self, text):
        """The longest known company name that `text` starts with."""
        n = norm_name(text) + " "
        best = None
        for i in [m.start() for m in re.finditer(" ", n)]:
            hit = self.by_name.get(n[:i])
            if hit:
                best = hit
        return best


def headline_day(title, published):
    """'… Reverse Stock Split Effective Nov. 10' -> the next Nov 10 on or after a month before publication, if it is
    within MAX_LEAD_DAYS of it (the window parse_doc uses for filings)."""
    m = _HEAD_DAY.search(title)
    if not m:
        return None
    for year in (published.year, published.year + 1):
        try:
            d = date(year, _MONTHS[m.group(1)[:3].lower()], int(m.group(2)))
        except ValueError:
            return None
        if d >= published - timedelta(30):
            return d if d <= published + timedelta(MAX_LEAD_DAYS) else None
    return None


def _doc(company, filed, url, text, source):
    cik, name, ticker = company
    return {"cik": cik, "name": name, "ticker": ticker, "form": "PR", "file_type": "PR", "filed": filed.isoformat(),
            "url": url, "wire": source, **parse_doc(text, filed.isoformat())}


def gnw_docs(items, names):
    """GlobeNewswire search items -> docs. The feed carries the release's opening paragraphs, sometimes all of it."""
    out = []
    for it in items:
        if not _SPLIT_TITLE.search(it.get("Title", "")):
            continue
        tickers = re.findall(r"[A-Za-z ]+:\s*([A-Z.]{1,6})", str(it.get("StockTickers") or ""))   # a list, live
        company = next((names.ticker(t) for t in tickers if names.ticker(t)), None) or names.lead(it.get("OrgName", ""))
        if not company:
            continue
        body = re.sub(r"<[^>]+>", " ", " ".join(it.get(k) or "" for k in ("Title", "Summary", "Content")))
        filed = date.fromisoformat(it["ReleaseDateTime"][:10])
        out.append(_doc(company, filed, it["Url"], normalize(body), "GlobeNewswire"))
    return out


def gnews_docs(rss, names):
    """Google News search RSS -> one doc per split headline. Headline only: ratio and date when the title gives them,
    rounding comes from the company's filings."""
    out = []
    for item in ET.fromstring(rss).iter("item"):
        source = item.findtext("source") or "news"
        title = item.findtext("title") or ""
        if title.endswith(f" - {source}"):
            title = title[:-len(source) - 3]
        if not _SPLIT_TITLE.search(title):
            continue
        m = _TICKER.search(title)
        company = (names.ticker(m.group(1)) if m else None) or names.lead(title)
        if not company:
            continue
        published = parsedate_to_datetime(item.findtext("pubDate")).date()
        d = _doc(company, published, item.findtext("link"), normalize(title), source)
        if not d["split_day"]:
            d["split_day"] = headline_day(title, published)
            d["date_kind"] = "trading" if d["split_day"] else None
            if d["split_day"]:
                d["flags"].append(f"date from a {source} headline")
        out.append(d)
    return out


def short_name(name):
    """'GEE Group Inc.' -> 'GEE Group', for a news search."""
    return " ".join(w for w in re.sub(r"[^\w&.' -]+", " ", name).split() if w.lower().strip(".,") not in _SUFFIX)


def _gnews(q, days, fetch):
    return _get(GNEWS.format(q=urllib.parse.quote_plus(f"{q} when:{days}d")), fetch)


def wire_docs(names, today, days, dated=(), fetch=_requests_text):
    """Split releases from the last `days` days, deduped by URL. Companies with a release but no date anywhere (not
    in `dated`, the CIKs EDGAR already dates) get one more headline search by name: a broad search returns one
    headline per story, often the undated one."""
    docs = []
    for q in GNW_QUERIES:
        items = _get(GNW.format(q=urllib.parse.quote(q)), fetch)
        if items:
            docs += gnw_docs(json.loads(items), names)
    for q in GNEWS_QUERIES:
        rss = _gnews(q, days, fetch)
        if rss:
            docs += gnews_docs(rss, names)
    cutoff = (today - timedelta(days)).isoformat()
    docs = [d for d in docs if d["filed"] >= cutoff]
    undated = {d["cik"] for d in docs} - {d["cik"] for d in docs if d["split_day"]} - set(dated)
    for cik in sorted(undated)[:FOLLOWUP_MAX]:
        name = next(d["name"] for d in docs if d["cik"] == cik)
        rss = _gnews(f'"{short_name(name)}" reverse split', days, fetch)
        if rss:
            docs += [d for d in gnews_docs(rss, names) if d["cik"] == cik and d["filed"] >= cutoff]
    return list({d["url"]: d for d in docs}.values())
