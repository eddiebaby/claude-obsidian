from datetime import date

from eqr.rsa import (classify_rounding, extract_ratio, first_split_day, hit_meta, merge_events, normalize,
                     prev_trading_day, window_status, words_to_int)


def n(s):
    return normalize(s)


def test_words_to_int():
    assert words_to_int(["forty"]) == 40
    assert words_to_int(["twenty", "five", "Reverse"]) == 25
    assert words_to_int("two hundred fifty".split()) == 250
    assert words_to_int(["Reverse"]) is None


def test_ratio_numeric_word_and_ordinal():
    assert extract_ratio(n("authorizing a 1-for-58 reverse stock split"))[0] == 58
    assert extract_ratio(n("Charter Amendments for One-for-Six Reverse Stock Split"))[0] == 6
    assert extract_ratio(n("to effect a one‑for‑forty (1-for-40) reverse stock split"))[0] == 40
    assert extract_ratio(n("ANNOUNCES 1-FOR-20 SHARE CONSOLIDATION"))[0] == 20
    assert extract_ratio(n("will be reduced to one-tenth of the Common Shares outstanding on November 5"))[0] == 10
    assert extract_ratio(n("every two (2) shares of issued Common Stock will be combined into one (1) share"))[0] == 2


def test_ratio_range_is_not_the_ratio():
    t = n("the Board may effect a reverse stock split at a ratio ranging from 1-for-5 to 1-for-50, as determined later.")
    assert extract_ratio(t) == (None, (5, 50))
    t = n("Company Announces 1-for-25 Reverse Stock Split. The Board was authorized at a ratio ranging from "
          "1-for-20 to 1-for-25.")
    assert extract_ratio(t) == (25, (20, 25))
    assert extract_ratio(n("one or more reverse splits at an aggregate ratio not to exceed 1-for-30."))[1] == (None, 30)
    assert extract_ratio(n("at a ratio of not less than 1-for-2 and not more than 1-for-20, with the exact ratio")) == \
        (None, (2, 20))
    assert extract_ratio(n("at a ratio in the range of 1-for-2 to 1-for-20with the exact ratio")) == (None, (2, 20))
    assert extract_ratio(n("at a ratio ranging from one-for-two (1-for-2) to one-for-fifty (1-for-50), with")) == \
        (None, (2, 50))
    assert extract_ratio(n("ranging from one-for-two (1:2) to one-for-49 (1:49), with the exact ratio")) == \
        (None, (2, 49))
    assert extract_ratio(n("at a ratio of not less than 1-for-12.48 and not more than 1-for-50, with")) == \
        (None, (12, 50))
    assert extract_ratio(n("at an exchange ratio of either one-for-three hundred (1:300) or one-for-two hundred "
                           "(1:200) in the aggregate")) == (None, (200, 300))
    assert extract_ratio(n("at a ratio of not less than two (2)-for-one (1) and not more than five-hundred (500)-for-one "
                           "(1) aggregately")) == (None, (2, 500))
    t = n("whereby every two (2) to every four hundred (400) issued and unissued shares be consolidated into one share")
    assert extract_ratio(t) == (None, (2, 400))
    t = n("(a) every two (2) to every four hundred (400) issued and unissued shares, subject to a cumulative "
          "consolidation ratio cap of five hundred (500) to one (1) in the aggregate. The Share Consolidation, within "
          "the Range that every eight (8) issued and unissued shares of the Company be consolidated into one (1) share")
    assert extract_ratio(t) == (8, (2, 400))


def test_ratio_consolidation_forms():
    assert extract_ratio(n("at a ratio of five (5)-for-one (1), such that every five (5) Class A Ordinary Shares of a "
                           "par value of US$0.00005 each be consolidated into one"))[0] == 5
    assert extract_ratio(n("at a ratio of eight (8)-to-one (1), such that every eight (8) Ordinary Shares"))[0] == 8
    assert extract_ratio(n("every one hundred (100) Class B Ordinary Shares of a par value of US$0.008 each be "
                           "consolidated into one share"))[0] == 100
    assert extract_ratio(n("re-designated on a one-for-one basis for newly issued shares")) == (None, None)
    assert extract_ratio(n("Every intermediary (broker) has its own mailing procedure")) == (None, None)


def test_split_day_prefers_trading_cue():
    t = n("effective at 12:01 a.m. Eastern Time on October 28, 2026. The Class A common stock is expected to begin "
          "trading on a split-adjusted basis on the New York Stock Exchange at the opening of trading on "
          "October 29, 2026, under the existing symbol.")
    assert first_split_day(t) == (date(2026, 10, 29), "trading")


def test_split_day_from_effective_date():
    assert first_split_day(n("The Reverse Stock Split will become effective at 12:01 a.m. Eastern Time on "
                             "November 5, 2026.")) == (date(2026, 11, 5), "effective")
    # effective after the close -> split-adjusted from the next session (Thursday -> Friday)
    assert first_split_day(n("a one-for-six Reverse Stock Split, to be effective at 5:00 p.m. Eastern Time on "
                             "October 29, 2026.")) == (date(2026, 10, 30), "effective")
    assert first_split_day(n("Split-adjusted trading began Oct. 20, 2026, under the symbol NGTFD")) == \
        (date(2026, 10, 20), "trading")


def test_split_day_ignores_old_history():
    t = n("On August 28, 2026, the Company began trading on a split-adjusted basis. The new split will be "
          "effective as of the opening of trading on October 26, 2026.")
    assert first_split_day(t, not_before=date(2026, 10, 15)) == (date(2026, 10, 26), "trading")


def test_split_day_needs_split_wording_nearby():
    t = n("The 1-for-25 reverse share split became effective on July 6, 2026. In other news, the new accounting "
          "updates are effective for annual periods beginning after December 15, 2026, and the Company does not "
          "expect a material impact.")
    assert first_split_day(t, not_before=date(2026, 10, 16)) == (date(2026, 7, 6), "past")   # not Dec 15
    t = n("The Reverse Stock Split will become effective at 12:01 a.m. Eastern Time on November 5, 2026, and will be "
          "reflected in the marketplace at the open of business on November 5, 2026, whereupon the shares will "
          "begin trading on a split-adjusted basis.")
    assert first_split_day(t) == (date(2026, 11, 5), "trading")


def test_split_day_skips_deadlines_and_reports_past_splits():
    t = n("authorize a share consolidation within a range of 10 to 30, at any time prior to October 29, 2027.")
    assert first_split_day(t) == (None, None)
    t = n("The Reverse Stock Split became effective on September 23, 2026, at 12:01 A.M. EST.")
    assert first_split_day(t, not_before=date(2026, 10, 2)) == (date(2026, 9, 23), "past")
    t = n("the rounding up of any fractional shares resulting from the Share Consolidation, which shall take effect "
          "on December 2, 2026")
    assert first_split_day(t, not_before=date(2026, 10, 23)) == (date(2026, 12, 2), "effective")
    t = n("The reverse stock split will become effective on May 3, 2027.")
    assert first_split_day(t, not_after=date(2027, 1, 28)) == (None, None)


def test_round_up_variants():
    ups = [
        "No fractional shares will be issued. Stockholders who would otherwise be entitled to receive fractional "
        "shares will have such fractional shares rounded up to the nearest whole share.",
        "No fractional shares will be issued, and no cash or other consideration will be paid. Instead, the Company "
        "will issue one whole share of the post-Reverse Stock Split common stock to any stockholder who otherwise "
        "would have received a fractional share.",
        "No fractional shares will be issued. Shareholders who would otherwise be entitled to receive fractional "
        "shares will receive one full share.",
        "Shareholders otherwise entitled to a fractional ordinary share will receive a full ordinary share in lieu.",
        "Instead, stockholders entitled to fractional shares will automatically be entitled to receive an "
        "additional fraction of a share of Common Stock to round up to the next whole share.",
    ]
    for t in ups:
        assert classify_rounding(n(t))[0] == "UP", t


def test_participant_level_round_up_is_flagged():
    t = n("Any fractional share that would otherwise result will be rounded up to the nearest whole share. For "
          "shares held through The Depository Trust Company, fractional share interests will be determined, and "
          "rounding will be effected, at the DTC-participant level.")
    cls, flags, excerpt = classify_rounding(t)
    assert cls == "UP_PARTICIPANT"
    assert "participant-level rounding" in flags
    assert "DTC-participant level" in excerpt


def test_participant_wording_variants():
    t = n("No fractional shares will be issued. Instead, the fractional share totals as to which shareholders who "
          "are DTC participants become entitled will be rounded up to the nearest whole number of shares.")
    assert classify_rounding(t)[0] == "UP_PARTICIPANT"
    t = n("Any fractional shares resulting from the Reverse Share Split will be rounded up at the beneficial holder "
          "level.")
    assert classify_rounding(t)[0] == "UP"


def test_cash_in_lieu_and_negation():
    t = n("No fractional shares will be issued; rather, stockholders who would have otherwise been issued a fractional "
          "share will instead receive a cash payment in lieu of such fractional share.")
    assert classify_rounding(t)[0] == "CASH"
    t = n("No fractional shares will be issued. In lieu of any fractional share, the Corporation shall pay to each "
          "such holder an amount in cash. The Reverse Stock Split shall be effected on a record holder-by-record "
          "holder basis, such that any fractional shares held by a single record holder shall be aggregated.")
    cls, flags, _ = classify_rounding(t)
    assert cls == "CASH" and "record-holder aggregation" in flags
    t = n("Fractional shares will be rounded up to the nearest whole share; no cash payment will be made.")
    assert classify_rounding(t)[0] == "UP"


def test_round_up_and_cash_is_mixed_and_anti_arb_flagged():
    t = n("Fractional shares will be rounded up to the nearest whole share, provided that the Company reserves the "
          "right to pay cash in lieu of fractional shares to holders who acquired shares after the record date.")
    cls, flags, _ = classify_rounding(t)
    assert cls == "MIXED" and "anti-arb wording" in flags


def test_boilerplate_cash_is_not_the_split_treatment():
    # JOB DEF 14A: real round-up, generic tax section mentions cash in lieu
    t = n("Fractional Shares Fractional shares will be rounded up to the next whole share. " + "x " * 300 +
          "Stockholders who acquired Common Stock on different dates should consult their tax advisors regarding the "
          "allocation of the tax basis. A U.S. Holder that receives cash in lieu of a fractional share of our Common "
          "Stock pursuant to the Reverse Stock Split should recognize capital gain or loss. " + "y " * 100 +
          "A U.S. Holder (other than corporations and certain other exempt recipients) may be subject to information "
          "reporting and backup withholding when such holder receives cash in lieu of a fractional share.")
    assert classify_rounding(t)[0] == "UP"
    # SGRX articles: asset-distribution clause, not the consolidation
    t = n("the rounding up of any fractional shares to the nearest whole ordinary share. " + "x " * 300 +
          "may issue fractional certificates and fix the value for distribution of such specific assets or any part "
          "thereof and may determine that cash payments shall be made to any Members")
    assert classify_rounding(t)[0] == "UP"
    # a real cash-in-lieu sentence still counts even with a tax section nearby
    t = n("No fractional shares will be issued. Stockholders will receive a cash payment in lieu of any fractional "
          "share. A U.S. Holder that receives cash in lieu of a fractional share should recognize capital gain.")
    assert classify_rounding(t)[0] == "CASH"


def test_up_with_down_in_one_doc_is_mixed():
    t = n("Fractional shares of common stock will be rounded up to the nearest whole share. Fractional shares "
          "underlying outstanding awards will be rounded down to the nearest whole share.")
    assert classify_rounding(t)[0] == "MIXED"


def test_appraisal_and_trailing_tax_wording_is_boilerplate():
    # ARAI DEF 14C: a real round-up plus DGCL appraisal text and IRS reporting sentences
    t = n("No fractional shares will be issued; instead, stockholders who would otherwise receive a fractional share "
          "will receive a whole share in lieu of any fractional share. " + "x " * 200 +
          "Appraisal is not available if holders receive shares of a corporation listed on a national securities "
          "exchange, cash in lieu of fractional shares or fractional depositary receipts described above or any "
          "combination of the foregoing. " + "y " * 200 +
          "In addition, payments of cash in lieu of a fractional share made pursuant to the Reverse Stock Split may "
          "be subject to backup withholding.")
    assert classify_rounding(t)[0] == "UP"


def test_tax_sentence_does_not_hide_the_next_cash_sentence():
    t = n("Fractional shares will be rounded up for holders of record. This summary addresses U.S. federal income "
          "tax consequences. Stockholders holding through a broker will receive cash in lieu of any fractional share.")
    assert classify_rounding(t)[0] == "MIXED"


def test_participant_flag_in_proxy_applies_to_the_announcement():
    today = date(2026, 11, 3)
    proxy = _doc(9, "DEF 14A", "2026-09-01", "UP")
    proxy["flags"] = ["participant-level rounding"]
    ev = merge_events([_doc(9, "8-K", "2026-11-02", "UP", 15, date(2026, 11, 10)), proxy], today)[0]
    assert ev["rounding"] == "UP_PARTICIPANT"


def test_no_fraction_language_is_unknown():
    assert classify_rounding(n("The Company received a Nasdaq deficiency notice."))[0] == "UNKNOWN"


def test_trading_calendar():
    assert prev_trading_day(date(2026, 11, 9)) == date(2026, 11, 6)      # Monday -> Friday
    assert prev_trading_day(date(2026, 11, 27)) == date(2026, 11, 25)    # skips Thanksgiving


def test_window_status():
    today = date(2026, 11, 3)
    assert window_status(date(2026, 11, 5), today) == ("OPEN", date(2026, 11, 4))
    assert window_status(date(2026, 11, 4), today) == ("TODAY", date(2026, 11, 3))
    assert window_status(date(2026, 11, 3), today)[0] == "DONE"
    assert window_status(None, today) == ("NO_DATE", None)
    assert window_status(date(2026, 11, 9), date(2026, 11, 7))[0] == "MISSED"  # Saturday before a Monday split


def test_hit_meta():
    hit = {"_id": "0001493152-26-049743:form8-k.htm", "_source": {
        "ciks": ["0001347858"], "display_names": ["22nd Century Group, Inc.  (XXII)  (CIK 0001347858)"],
        "form": "8-K", "file_type": "8-K", "file_date": "2026-11-03"}}
    m = hit_meta(hit)
    assert (m["cik"], m["ticker"], m["name"]) == (1347858, "XXII", "22nd Century Group, Inc.")
    assert m["url"] == "https://www.sec.gov/Archives/edgar/data/1347858/000149315226049743/form8-k.htm"
    hit["_source"]["display_names"] = ["Foo (Holdings) Ltd  (CIK 0000000001)"]
    assert hit_meta(hit)["ticker"] is None


VIXM_8K = ("FORM 8-K ProShares Trust II Securities registered pursuant to Section 12(b) of the Act. Title of each "
           "class Trading Symbol(s) Name of each exchange on which registered ProShares VIX Mid-Term Futures ETF "
           "VIXM Cboe BZX Check the appropriate box below Emerging growth company Item 8.01. Other Events On "
           "November 3, 2026, ProShare Capital Management LLC, on behalf of ProShares Trust II, issued a press "
           "release announcing a reverse share split on ProShares VIX Mid-Term Futures ETF (Cboe BZX Exchange ticker "
           "symbol \"VIXM\"). Post-Reverse Split fractional shares will be redeemed for cash and sent to the "
           "shareholder's broker of record.")
TRUST = ["AGQ", "UVXY", "SVXY", "VIXM", "VIXY", "UCO"]


def test_named_ticker_fund_trust():
    from eqr.rsa import named_ticker
    assert named_ticker(TRUST, VIXM_8K) == "VIXM"
    assert classify_rounding(n(VIXM_8K))[0] == "CASH"
    cover_all = VIXM_8K.replace("ProShares VIX Mid-Term Futures ETF VIXM Cboe BZX",
                                "Ultra Silver AGQ NYSE Arca Ultra VIX UVXY Cboe BZX VIX Mid-Term VIXM Cboe BZX")
    assert named_ticker(TRUST, cover_all) == "VIXM"             # the body decides, not the cover's list
    two = VIXM_8K.replace('symbol \"VIXM\")', 'symbols \"VIXM\" and \"UVXY\")')
    assert named_ticker(TRUST, two) is None                     # combined 8-K: don't pick one
    assert named_ticker(TRUST, "Item 8.01 a reverse split of one of our funds") is None    # never guess AGQ


def test_named_ticker_ordinary_company():
    from eqr.rsa import named_ticker
    spac = ("Title of each class Trading Symbol(s) Units ABCU Class A common stock ABC Warrants ABCW "
            "Item 5.03 The Company effected a 1-for-10 reverse split of its Class A common stock (Nasdaq: ABC).")
    assert named_ticker(["ABC", "ABCW", "ABCU"], spac) == "ABC"
    reit = ("Trading Symbol(s) Series A Preferred XYZ-PA Series B Preferred XYZ-PB Common Stock XYZ "
            "Item 8.01 The board approved a 1-for-5 reverse split; the preferred stock (XYZ-PA, XYZ-PB) is unaffected "
            "and the common stock XYZ will trade split-adjusted.")
    assert named_ticker(["XYZ", "XYZ-PA", "XYZ-PB"], reit) == "XYZ"       # several named: keep the common
    assert named_ticker(["ABC", "ABCW"], "no symbol named") == "ABC"
    assert named_ticker(["A", "AB"], "Item 8.01 A reverse split of AB shares") == "A"   # both named: keep the first
    assert named_ticker(["ABC", "ABCW"], "Item 8.01 its warrants (ABCW) are adjusted") == "ABCW"   # the one named
    assert named_ticker([], "x") is None


def test_fund_trust_events_split_by_fund():
    today = date(2026, 11, 5)
    a = {**_doc(1415311, "8-K", "2026-11-04", "CASH", 2, date(2026, 11, 19)), "ticker": "VIXM", "tickers": ["A"] * 6}
    b = {**_doc(1415311, "8-K", "2026-11-04", "UP", 4, date(2026, 11, 20)), "ticker": "UVXY", "tickers": ["A"] * 6,
         "url": "u/other"}
    ev = {e["ticker"]: e for e in merge_events([a, b], today)}
    assert (ev["VIXM"]["rounding"], ev["UVXY"]["rounding"], ev["UVXY"]["ratio"]) == ("CASH", "UP", 4)


def _doc(cik, form, filed, rounding, ratio=None, split_day=None, flags=(), rng=None):
    return {"cik": cik, "ticker": "ABC", "name": "Abc Inc", "form": form, "filed": filed, "url": f"u/{form}/{filed}",
            "ratio": ratio, "ratio_range": rng, "split_day": split_day, "date_kind": None, "rounding": rounding,
            "flags": list(flags), "excerpt": rounding.lower()}


def test_merge_events():
    today = date(2026, 11, 3)
    docs = [_doc(1, "8-K", "2026-11-02", "UP", 20, date(2026, 11, 6)),
            _doc(1, "8-K", "2026-10-30", "UNKNOWN"),
            _doc(1, "DEF 14A", "2026-08-01", "CASH", rng=(5, 50)),
            _doc(2, "8-K", "2026-11-01", "UP", 10, date(2026, 11, 5)),
            _doc(2, "8-K", "2026-10-31", "UP_PARTICIPANT", flags=["participant-level rounding"]),
            _doc(3, "8-K", "2026-11-02", "UNKNOWN", 15, date(2026, 11, 10)),
            _doc(3, "PRE 14A", "2026-09-01", "UP"),
            _doc(4, "DEF 14C", "2026-10-01", "UP", rng=(2, 30))]
    ev = {e["cik"]: e for e in merge_events(docs, today)}
    assert (ev[1]["rounding"], ev[1]["ratio"], ev[1]["status"], ev[1]["buy_by"]) == ("UP", 20, "OPEN", date(2026, 11, 5))
    assert ev[1]["ratio_range"] == (5, 50)
    assert ev[2]["rounding"] == "UP_PARTICIPANT" and "participant-level rounding" in ev[2]["flags"]
    assert ev[3]["rounding"] == "UP" and "rounding from PRE 14A filed 2026-09-01" in ev[3]["flags"]
    assert (ev[4]["stage"], ev[4]["status"], ev[4]["split_day"]) == ("proxy", "NO_DATE", None)


def test_newest_treatment_wins():
    today = date(2026, 11, 3)
    announce = _doc(1, "6-K", "2026-10-16", "UP", 25, date(2026, 11, 6))
    results = _doc(1, "6-K", "2026-10-27", "DOWN")
    e = merge_events([announce, results], today)[0]
    assert e["rounding"] == "DOWN" and "treatment changed: earlier filing said UP" in e["flags"]


def test_merge_drops_docs_that_barely_mention_a_split():
    today = date(2026, 11, 3)
    real = {**_doc(1, "8-K", "2026-10-30", "UP", 10, date(2026, 10, 30)), "mentions": 16}
    preferred = {**_doc(1, "8-K", "2026-11-02", "UP", 10, date(2026, 12, 28)), "mentions": 2}
    plan = {**_doc(2, "DEF 14A", "2026-10-01", "UP", 4), "mentions": 2}
    merger = {**_doc(3, "8-K", "2026-11-01", "UP", 10, date(2026, 12, 31)), "mentions": 9, "file_type": "EX-2.1"}
    financials = {**_doc(4, "6-K", "2026-11-02", "UP", 16), "mentions": 6, "financials": True}
    ev = merge_events([real, preferred, plan, merger, financials], today)
    assert len(ev) == 1 and ev[0]["status"] == "DONE" and ev[0]["split_day"] == date(2026, 10, 30)
    short_results = {**_doc(5, "6-K", "2026-10-27", "DOWN"), "mentions": 2,
                     "excerpt": "All fractional shares resulting from the reverse stock split will be disregarded"}
    assert merge_events([short_results], today)[0]["rounding"] == "DOWN"


def test_foreign_meeting_notices():
    today = date(2026, 11, 3)
    undated = {**_doc(1, "6-K", "2026-10-29", "UP", rng=(200, 300)), "mentions": 12, "meeting": True}
    dated = {**_doc(2, "6-K", "2026-10-30", "UP", 5, date(2026, 12, 2)), "mentions": 12, "meeting": True,
             "meeting_day": date(2026, 11, 20)}
    voted = {**_doc(3, "6-K", "2026-10-30", "UP", 5, date(2026, 11, 9)), "mentions": 9, "approved": True}
    voted_notice = {**_doc(3, "6-K", "2026-10-20", "UP", 5, date(2026, 11, 9)), "mentions": 9, "meeting": True,
                    "meeting_day": date(2026, 10, 29)}
    ev = {e["cik"]: e for e in merge_events([undated, dated, voted, voted_notice], today)}
    assert (ev[1]["stage"], ev[1]["status"], ev[1]["ratio_range"]) == ("proxy", "NO_DATE", (200, 300))
    assert (ev[2]["stage"], ev[2]["status"], ev[2]["vote"]) == ("announced", "OPEN", date(2026, 11, 20))
    assert ev[3]["vote"] is None


def test_approval_is_past_tense_only():
    from eqr.rsa import _APPROVED
    assert not _APPROVED.search("today announced that, subject to shareholder approval, the Company will")
    assert _APPROVED.search("Alps Group Inc Announces Shareholder Approval for a Share Consolidation")
    assert _APPROVED.search("all resolutions were duly passed at the EGM")
    assert _APPROVED.search("All matters voted on at the Extraordinary General Meeting were approved.")
    from eqr.rsa import approved
    assert not approved("For the purpose of determining whether the shareholders have approved Proposal One")
    assert approved("Robo.ai announced that each of the resolutions has been adopted; the shareholders approved the "
                    "share consolidation")


def test_meeting_day():
    from eqr.rsa import meeting_day
    assert meeting_day(n("PROXY Solicited on Behalf of the Board for the Extraordinary General Meeting of "
                         "Shareholders To be held on November 9, 2026 at 10 p.m.")) == date(2026, 11, 9)
    assert meeting_day(n("ANNOUNCES REVERSE STOCK SPLIT AND EXTRAORDINARY GENERAL MEETING ON OCTOBER 26, 2026")) == \
        date(2026, 10, 26)


def test_mark_round_up():
    from eqr.rsa import mark_round_up
    assert mark_round_up("fractional shares will be rounded up to the nearest whole share") == \
        "fractional shares will be **rounded up** to the nearest whole share"
    assert "**receive one full share**" in mark_round_up("holders will instead receive one full share of common stock")


def test_round_up_clause():
    from eqr.rsa import _sentence, mark_round_up, round_up_clause
    w = "dinary Share of a par value of US$0.0024 each, and the rounding up of any fractional shares to the nearest " \
        "whole ordinary share, which shall take effect on November 13, 2026. Next sentence."
    s = _sentence(w, w.index("rounding"))
    assert s.startswith("…Share of a par") and s.endswith("November 13, 2026.")
    q = 'such holder will be rounded up to the next whole Share." 4. Other items follow.'
    assert _sentence(q, q.index("rounded")).endswith('whole Share.')
    long = "x " * 200 + "all fractional shares will be rounded up to the next whole share" + " y" * 200
    c = round_up_clause(long, back=40, ahead=40)
    assert c.startswith("…") and c.endswith("…") and "**rounded up**" in c and len(c) < 160
    same = "All fractional shares will be rounded up, at the DTC participant level."
    assert round_up_clause(f"{same} … {same}") == mark_round_up(same)
