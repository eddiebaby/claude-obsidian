from datetime import date, datetime

from eqr.rsa_alert import ET, alerts, deadline, ntfy, push_text, session_day, title


def ev(ticker, buy_by, split_day, rounding="UP", status="OPEN", vote=None, stage="announced"):
    return {"ticker": ticker, "ratio": 5, "price": 0.53, "gain_per_acct": 2.12, "buy_by": buy_by,
            "split_day": split_day, "rounding": rounding, "status": status, "vote": vote, "stage": stage,
            "filed": "2026-11-04",
            "excerpt": "Any fractional shares will be rounded up to the nearest whole share."}


def run(act=(), vote=(), check=(), watch=(), sent=(), today=date(2026, 11, 5), events=None):
    rows = list(act) + list(vote) + list(check) + list(watch)
    return alerts(list(act), list(vote), list(check), list(watch), rows if events is None else events, set(sent),
                  today)


def test_session_day():
    assert session_day(datetime(2026, 11, 6, 10, 0, tzinfo=ET)) == date(2026, 11, 6)      # Fri before the close
    assert session_day(datetime(2026, 11, 6, 16, 5, tzinfo=ET)) == date(2026, 11, 9)      # Fri after -> Mon
    assert session_day(datetime(2026, 11, 7, 9, 0, tzinfo=ET)) == date(2026, 11, 9)       # Saturday
    assert session_day(datetime(2026, 11, 25, 17, 0, tzinfo=ET)) == date(2026, 11, 27)    # skips Thanksgiving


def test_deadline_in_hawaii_time():
    assert deadline(date(2026, 11, 13)) == "Fri Nov 13 close (11am HST)"
    assert deadline(date(2026, 7, 10)) == "Fri Jul 10 close (10am HST)"      # US daylight saving


def test_buy_entry_says_what_by_when_and_why():
    nxts = ev("NXTS", date(2026, 11, 6), date(2026, 11, 9))
    entries, keys = run(act=[nxts])
    assert entries == ["BUY NXTS · 1:5 · $0.530 → +$2.12/share\n"
                       "Buy 1 share by Fri Nov 6 close (11am HST)\n"
                       "\"Any fractional shares will be rounded up to the nearest whole share.\""]
    assert run(act=[nxts], sent=keys) == ([], set())
    entries, keys2 = run(act=[nxts], sent=keys, today=date(2026, 11, 6))
    assert entries[0].startswith("LAST DAY NXTS") and run(act=[nxts], sent=keys | keys2, today=date(2026, 11, 6))[0] == []


def test_check_entries_give_the_reason_and_last_day_fires_once():
    arai = ev("ARAI", date(2026, 11, 11), date(2026, 11, 12), rounding="UP_EARLIER")
    entries, keys = run(check=[arai])
    assert entries[0].split("\n")[:3] == ["CHECK ARAI · 1:5 · $0.530 → +$2.12/share",
                                          "Why: round-up wording is only in an earlier filing, not this split's",
                                          "If it checks out, buy 1 share by Wed Nov 11 close (11am HST)"]
    entries, keys2 = run(check=[arai], sent=keys, today=date(2026, 11, 11))
    assert entries[0].startswith("LAST DAY (CHECK) ARAI")
    assert run(check=[arai], sent=keys | keys2, today=date(2026, 11, 11))[0] == []


def test_dropped_buy_that_moved_to_check_is_one_entry():
    sos = ev("SOS", date(2026, 11, 18), date(2026, 11, 19), rounding="UP_EARLIER")
    entries, keys = run(check=[sos], sent={"SOS:2026-11-19"})
    assert entries == ["DROPPED SOS: moved to CHECK, round-up wording is only in an earlier filing, not this "
                       "split's. Recheck before buying."]
    assert run(check=[sos], sent={"SOS:2026-11-19"} | keys)[0] == []


def test_dropped_when_rounding_changes_or_vote_reappears():
    aiio = ev("AIIO", date(2026, 11, 9), date(2026, 11, 10), rounding="DOWN")
    licn = ev("LICN", date(2026, 11, 18), date(2026, 11, 19), vote=date(2026, 11, 9))
    done = ev("XXII", date(2026, 11, 4), date(2026, 11, 5), status="DONE")
    sent = {"AIIO:2026-11-10", "LICN:2026-11-19", "XXII:2026-11-05", "watch:LICN:2026-11"}
    entries, _ = run(events=[aiio, licn, done], sent=sent, today=date(2026, 11, 3))
    assert entries == ["DROPPED AIIO: now DOWN. Recheck before buying.",
                       "DROPPED LICN: a shareholder vote is pending again. Recheck before buying."]


def test_watch_entries_for_votes_and_undated_names_once():
    airi = {**ev("AIRI", date(2026, 11, 19), date(2026, 11, 20), vote=date(2026, 11, 18)), "gain_per_acct": 12.0,
            "price": 3.0}
    chsn = {**ev("CHSN", None, None, status="NO_DATE"), "ratio": 100}
    entries, keys = run(vote=[airi], watch=[chsn])
    assert entries == ["WATCH AIRI · 1:5 · $3.00 → +$12.00/share\n"
                       "shareholder vote Wed Nov 18; if it passes, buy by Thu Nov 19 close (11am HST)",
                       "WATCH CHSN · 1:100 · $0.530 → +$2.12/share\nround-up announced, no split date yet"]
    assert run(vote=[airi], watch=[chsn], sent=keys)[0] == []


def test_watch_vote_without_a_date_does_not_crash():
    rfil = {**ev("RFIL", None, None, status="NO_DATE", vote=date(2026, 11, 20)), "ratio": 10}
    entries, _ = run(watch=[rfil])
    assert entries == ["WATCH RFIL · 1:10 · $0.530 → +$2.12/share\nshareholder vote Fri Nov 20; no split date yet"]


def test_tickerless_skipped():
    anon = ev(None, date(2026, 11, 6), date(2026, 11, 9))
    assert run(act=[anon], check=[anon], watch=[anon]) == ([], set())


class Resp:
    def __init__(self, ok=True):
        self.ok = ok

    def raise_for_status(self):
        if not self.ok:
            raise RuntimeError("HTTP 503")


def test_push_text_title_and_ntfy():
    entries = ["LAST DAY A · 1:5\nBuy…", "BUY B · 1:8\nBuy…", "BUY C · 1:2\nBuy…", "WATCH D · 1:9\nvote"]
    assert push_text(entries[:1]) == "RSA: LAST DAY A · 1:5"
    assert len(push_text(["BUY " + "X" * 300])) == 200
    assert title(entries) == "RSA: 1 last day, 2 buy, 1 watch"
    calls = []

    def post(url, **kw):
        calls.append((url, kw))
        return Resp()
    assert ntfy(entries[:2], topic="t", post=post)
    assert calls[0][0] == "https://ntfy.sh/t" and calls[0][1]["data"] == "\n\n".join(entries[:2]).encode()
    assert calls[0][1]["headers"]["Title"] == "RSA: 1 last day, 1 buy"
    assert not ntfy([], topic="t", post=post)
    assert not ntfy(["BUY A"], topic="", post=post) and len(calls) == 1
    try:
        ntfy(["BUY A"], topic="t", post=lambda *a, **k: Resp(ok=False))
        raise AssertionError("an HTTP error must raise, so the alert isn't marked sent")
    except RuntimeError:
        pass


def test_save_sent_roundtrip(tmp_path):
    from eqr.rsa_alert import load_sent, save_sent
    p = tmp_path / "sent.json"
    save_sent(p, {"A:2026-11-09", "B:2026-11-10:last"})
    assert load_sent(p) == {"A:2026-11-09", "B:2026-11-10:last"} and not (tmp_path / "sent.json.tmp").exists()
    p.write_text("{corrupt", encoding="utf-8")
    assert load_sent(p) == set()
