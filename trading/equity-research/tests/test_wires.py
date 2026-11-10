import re
from datetime import date

from eqr.rsa import merge_events, parse_doc
from eqr.wires import Names, gnews_docs, gnw_docs, headline_day, norm_name, wire_docs

NAMES = Names([(40570, "GEE Group Inc.", "JOB"), (1789192, "Nexentis Technologies Inc.", "NXTS"),
               (1951067, "C3is Inc.", "CISS"), (111, "UK Wisdom Ltd", "UK")])

NXTS = {"Title": "Nexentis Announces Reverse Stock Split", "ReleaseDateTime": "2026-11-05T14:00:00Z",
        "Url": "https://www.globenewswire.com/news-release/2026/11/05/3396505/0/en/nexentis-announces-reverse-stock-split.html",
        "OrgName": "Nexentis Technologies Inc.", "StockTickers": ["Nasdaq:NXTS"], "Summary": "",
        "Content": "Ness Ziona, Israel, Nov. 05, 2026 (GLOBE NEWSWIRE) -- Nexentis Technologies Inc. (NASDAQ: NXTS) "
                   "announced that its Board of Directors has approved a one-for-five (1-for-5) reverse stock split "
                   "of its common stock that is scheduled to become effective for Nasdaq purposes on November 9, 2026. "
                   "Beginning on November 9, 2026, the Company's common stock will trade on the Nasdaq Capital Market "
                   "on a split adjusted basis under a new CUSIP number 80512Q709."}
NOISE = {"Title": "Fluence Energy, Inc. (FLNC) Class Action Lawsuit Seeks Recovery for Investors",
         "ReleaseDateTime": "2026-11-06T18:02:04Z", "Url": "https://x", "OrgName": "Kessler Topaz",
         "StockTickers": "[]", "Content": "Did you buy FLNC securities?"}

RSS = """<?xml version="1.0"?><rss><channel>
<item><title>GEE Group Inc. (JOB) Sets 1-for-30 Reverse Stock Split Effective Nov. 10 - TradingView</title>
<link>https://news.google.com/rss/articles/abc</link><pubDate>Wed, 28 Oct 2026 21:10:00 GMT</pubDate>
<source url="https://www.tradingview.com">TradingView</source></item>
<item><title>GEE Group Inc. Announces Effective Date of Previously Approved Reverse Stock Split - Bergen Record</title>
<link>https://news.google.com/rss/articles/def</link><pubDate>Thu, 29 Oct 2026 05:21:17 GMT</pubDate>
<source url="https://www.northjersey.com">Bergen Record</source></item>
<item><title>GEE Group Announces Filing of a Universal Shelf Registration - Yahoo Finance</title>
<link>https://news.google.com/rss/articles/ghi</link><pubDate>Thu, 14 May 2026 07:00:00 GMT</pubDate>
<source url="https://finance.yahoo.com">Yahoo Finance</source></item>
</channel></rss>"""


def test_names():
    assert norm_name("GEE Group Inc.") == "gee group"
    assert NAMES.ticker("job")[0] == 40570
    assert NAMES.lead("GEE Group Inc. Announces Effective Date")[0] == 40570
    assert NAMES.lead("Geely Motors announces") is None


def test_headline_day():
    assert headline_day("Sets 1-for-30 Reverse Stock Split Effective Nov. 10", date(2026, 10, 28)) == date(2026, 11, 10)
    assert headline_day("Reverse Split Effective January 5", date(2026, 12, 20)) == date(2027, 1, 5)
    assert headline_day("Announces Reverse Stock Split", date(2026, 10, 28)) is None


def test_gnw_docs():
    docs = gnw_docs([NXTS, NOISE], NAMES)
    assert len(docs) == 1
    d = docs[0]
    assert (d["cik"], d["ticker"], d["ratio"], d["split_day"], d["filed"]) == \
        (1789192, "NXTS", 5, date(2026, 11, 9), "2026-11-05")
    assert d["rounding"] == "UNKNOWN" and d["wire"] == "GlobeNewswire"


def test_gnews_docs():
    docs = gnews_docs(RSS, NAMES)
    assert [d["filed"] for d in docs] == ["2026-10-28", "2026-10-29"]     # the shelf filing isn't a split headline
    assert (docs[0]["ratio"], docs[0]["split_day"], docs[0]["wire"]) == (30, date(2026, 11, 10), "TradingView")
    assert docs[1]["cik"] == 40570 and docs[1]["split_day"] is None     # matched by the name it opens with


def test_wire_docs_survives_a_feed_outage():
    def fetch(url):
        if "globenewswire" in url:
            raise OSError("down")
        return RSS
    docs = wire_docs(NAMES, date(2026, 11, 6), 30, fetch=fetch)
    assert {d["cik"] for d in docs} == {40570}


def test_undated_company_gets_a_name_search():
    dated, undated = re.findall(r"<item>.*?</item>", RSS, re.S)[:2]
    wrap = lambda items: f"<rss><channel>{items}</channel></rss>"
    asked = []

    def fetch(url):
        asked.append(url)
        if "globenewswire" in url:
            return "[]"
        return wrap(dated) if "GEE+Group" in url else wrap(undated)
    docs = wire_docs(NAMES, date(2026, 11, 6), 30, fetch=fetch)
    assert any("%22GEE+Group%22+reverse+split" in u for u in asked)
    assert {d["split_day"] for d in docs} == {None, date(2026, 11, 10)}
    asked.clear()
    wire_docs(NAMES, date(2026, 11, 6), 30, dated={40570}, fetch=fetch)    # EDGAR already has its date
    assert not any("GEE+Group" in u for u in asked)


def test_wire_date_with_proxy_rounding_makes_a_buy():
    today = date(2026, 11, 6)
    proxy = {"cik": 40570, "name": "GEE Group Inc.", "ticker": "JOB", "form": "DEF 14A", "file_type": "DEF 14A",
             "filed": "2026-08-31", "url": "https://www.sec.gov/def14a.htm",
             **parse_doc("Approve a one-for-thirty (1-for-30) reverse stock split. " * 8 +
                         "Fractional Shares Fractional shares will be rounded up to the next whole share.",
                         "2026-08-31")}
    ev = merge_events(gnews_docs(RSS, NAMES) + [proxy], today)[0]
    assert (ev["rounding"], ev["ratio"], ev["split_day"], ev["buy_by"], ev["status"]) == \
        ("UP", 30, date(2026, 11, 10), date(2026, 11, 9), "OPEN")
    assert "rounding from DEF 14A filed 2026-08-31" in ev["flags"] and "date from a TradingView headline" in ev["flags"]


def test_earlier_split_filing_fills_rounding():
    today = date(2026, 11, 6)
    prior = {"cik": 1789192, "name": "Nexentis Technologies Inc.", "ticker": "NXTS", "form": "8-K",
             "file_type": "8-K", "filed": "2026-04-06", "url": "https://www.sec.gov/8k.htm", "precedent": True,
             **parse_doc("The Company effected a one-for-seven reverse stock split. The reverse stock split was "
                         "approved. No fractional shares will be issued as a result of the Reverse Stock Split. Any "
                         "fractional shares that would otherwise have resulted from the Reverse Stock Split will be "
                         "rounded up to the next whole number.", "2026-04-06")}
    ev = merge_events(gnw_docs([NXTS], NAMES) + [prior], today)[0]
    # another split's filing is evidence, not this split's terms: CHECK, not BUY
    assert (ev["rounding"], ev["ratio"], ev["buy_by"], ev["status"]) == ("UP_EARLIER", 5, date(2026, 11, 6), "TODAY")
    assert "rounding from 8-K filed 2026-04-06" in ev["flags"] and "rounded up" in ev["excerpt"]


def test_headline_day_too_far_out():
    assert headline_day("Reverse Split Effective Mar. 20", date(2026, 11, 6)) is None    # 2027-03-20: >90 days
