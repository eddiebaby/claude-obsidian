from datetime import date, datetime

from eqr.rsa_alert import ET, alerts, deadline, message, ntfy, push_text, session_day, title

EMPTY = {"buy": [], "check": [], "watch": []}


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
    groups, keys = run(act=[nxts])
    assert groups["buy"] == ["NXTS · 1:5 · $0.530 → +$2.12/share\n"
                             "Buy 1 share by Fri Nov 6 close (11am HST)\n"
                             "\"Any fractional shares will be rounded up to the nearest whole share.\""]
    assert run(act=[nxts], sent=keys) == (EMPTY, set())
    groups, keys2 = run(act=[nxts], sent=keys, today=date(2026, 11, 6))
    assert groups["buy"][0].startswith("LAST DAY: NXTS")
    assert run(act=[nxts], sent=keys | keys2, today=date(2026, 11, 6)) == (EMPTY, set())


def test_last_day_names_lead_their_section():
    a = ev("AAA", date(2026, 11, 9), date(2026, 11, 10))
    b = ev("BBB", date(2026, 11, 5), date(2026, 11, 6))
    groups, _ = run(act=[a, b])
    assert [e.split(" ·")[0] for e in groups["buy"]] == ["LAST DAY: BBB", "AAA"]


def test_check_entries_give_the_reason_and_last_day_fires_once():
    arai = ev("ARAI", date(2026, 11, 11), date(2026, 11, 12), rounding="UP_EARLIER")
    groups, keys = run(check=[arai])
    assert groups["check"][0].split("\n")[:3] == ["ARAI · 1:5 · $0.530 → +$2.12/share",
                                                  "Why: round-up wording is only in an earlier filing, not this "
                                                  "split's",
                                                  "If it checks out, buy 1 share by Wed Nov 11 close (11am HST)"]
    groups, keys2 = run(check=[arai], sent=keys, today=date(2026, 11, 11))
    assert groups["check"][0].startswith("LAST DAY: ARAI")
    assert run(check=[arai], sent=keys | keys2, today=date(2026, 11, 11)) == (EMPTY, set())


def test_dropped_buy_that_moved_to_check_is_one_entry():
    sos = ev("SOS", date(2026, 11, 18), date(2026, 11, 19), rounding="UP_EARLIER")
    groups, keys = run(check=[sos], sent={"SOS:2026-11-19"})
    assert groups["check"] == ["DROPPED SOS: moved to CHECK, round-up wording is only in an earlier filing, not "
                               "this split's. Recheck before buying."]
    assert run(check=[sos], sent={"SOS:2026-11-19"} | keys) == (EMPTY, set())


def test_dropped_when_rounding_changes_or_vote_reappears():
    aiio = ev("AIIO", date(2026, 11, 9), date(2026, 11, 10), rounding="DOWN")
    licn = ev("LICN", date(2026, 11, 18), date(2026, 11, 19), vote=date(2026, 11, 9))
    done = ev("XXII", date(2026, 11, 4), date(2026, 11, 5), status="DONE")
    sent = {"AIIO:2026-11-10", "LICN:2026-11-19", "XXII:2026-11-05", "watch:LICN:2026-11"}
    groups, _ = run(events=[aiio, licn, done], sent=sent, today=date(2026, 11, 3))
    assert groups["check"] == ["DROPPED AIIO: now DOWN. Recheck before buying.",
                               "DROPPED LICN: a shareholder vote is pending again. Recheck before buying."]


def test_watch_is_a_one_line_list_once():
    airi = {**ev("AIRI", date(2026, 11, 19), date(2026, 11, 20), vote=date(2026, 11, 18)), "gain_per_acct": 12.0,
            "price": 3.0}
    chsn = {**ev("CHSN", None, None, status="NO_DATE"), "ratio": 100}
    rfil = {**ev("RFIL", None, None, status="NO_DATE", vote=date(2026, 11, 20)), "ratio": 10}     # no crash
    groups, keys = run(vote=[airi], watch=[chsn, rfil])
    assert groups["watch"] == ["• AIRI 1:5 · $3.00 → +$12.00 · vote Wed Nov 18, then buy by Thu Nov 19",
                               "• CHSN 1:100 · $0.530 → +$2.12 · no split date yet",
                               "• RFIL 1:10 · $0.530 → +$2.12 · vote Fri Nov 20, no split date yet"]
    assert run(vote=[airi], watch=[chsn, rfil], sent=keys) == (EMPTY, set())


def test_tickerless_skipped():
    anon = ev(None, date(2026, 11, 6), date(2026, 11, 9))
    assert run(act=[anon], check=[anon], watch=[anon]) == (EMPTY, set())


GROUPS = {"buy": ["LAST DAY: A · 1:5\nBuy…", "B · 1:8\nBuy…"], "check": ["C · 1:2\nWhy…"],
          "watch": ["• D 1:9 · no split date yet", "• E 1:3 · no split date yet"]}


def test_message_order_buy_check_watch():
    assert message(GROUPS) == ("BUY: rounds up per holder\nLAST DAY: A · 1:5\nBuy…\n\nB · 1:8\nBuy…\n\n"
                               "CHECK: read the filing before buying\nC · 1:2\nWhy…\n\n"
                               "WATCH: vote pending or no date yet\n• D 1:9 · no split date yet\n"
                               "• E 1:3 · no split date yet")
    assert message({**EMPTY, "watch": ["• D"]}) == "WATCH: vote pending or no date yet\n• D"
    assert message(EMPTY) == ""


class Resp:
    def __init__(self, ok=True):
        self.ok = ok

    def raise_for_status(self):
        if not self.ok:
            raise RuntimeError("HTTP 503")


def test_push_text_title_and_ntfy():
    assert push_text(GROUPS) == "RSA: LAST DAY: A · 1:5; B · 1:8; C · 1:2; 2 to watch"
    assert len(push_text({**EMPTY, "buy": ["X" * 300]})) == 200
    assert title(GROUPS) == "RSA: LAST DAY · 2 buy, 1 check, 2 watch"
    assert title({**EMPTY, "watch": ["• D"]}) == "RSA: 1 watch"
    calls = []

    def post(url, **kw):
        calls.append((url, kw))
        return Resp()
    assert ntfy(GROUPS, topic="t", post=post)
    assert calls[0][0] == "https://ntfy.sh/t" and calls[0][1]["data"] == message(GROUPS).encode()
    assert calls[0][1]["headers"]["Title"] == "RSA: LAST DAY · 2 buy, 1 check, 2 watch"
    assert not ntfy(EMPTY, topic="t", post=post)
    assert not ntfy(GROUPS, topic="", post=post) and len(calls) == 1
    try:
        ntfy(GROUPS, topic="t", post=lambda *a, **k: Resp(ok=False))
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
