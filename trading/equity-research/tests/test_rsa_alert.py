from datetime import date, datetime

from eqr.rsa_alert import ET, alerts, ntfy, push_text, session_day


def ev(ticker, buy_by, split_day, rounding="UP", status="OPEN", vote=None):
    return {"ticker": ticker, "ratio": 5, "price": 0.53, "gain_per_acct": 2.12, "buy_by": buy_by,
            "split_day": split_day, "rounding": rounding, "status": status, "vote": vote}


def test_session_day():
    assert session_day(datetime(2026, 11, 6, 10, 0, tzinfo=ET)) == date(2026, 11, 6)      # Fri before the close
    assert session_day(datetime(2026, 11, 6, 16, 5, tzinfo=ET)) == date(2026, 11, 9)      # Fri after -> Mon
    assert session_day(datetime(2026, 11, 7, 9, 0, tzinfo=ET)) == date(2026, 11, 9)       # Saturday
    assert session_day(datetime(2026, 11, 25, 17, 0, tzinfo=ET)) == date(2026, 11, 27)    # skips Thanksgiving


def test_new_then_last_day_then_quiet():
    today = date(2026, 11, 5)
    nxts = ev("NXTS", date(2026, 11, 6), date(2026, 11, 9))
    lines, keys = alerts([nxts], [nxts], set(), today)
    assert lines == ["NEW NXTS 1:5 $0.530 +$2.12 by Fri Nov 6"]
    sent = keys
    assert alerts([nxts], [nxts], sent, today) == ([], set())                      # same day, nothing new
    lines, keys = alerts([nxts], [nxts], sent, date(2026, 11, 6))
    assert lines == ["LAST DAY NXTS 1:5 $0.530 +$2.12 by TODAY"]
    assert alerts([nxts], [nxts], sent | keys, date(2026, 11, 6)) == ([], set())


def test_new_on_its_last_day_is_one_alert():
    today = date(2026, 11, 6)
    nxts = ev("NXTS", today, date(2026, 11, 9))
    lines, keys = alerts([nxts], [nxts], set(), today)
    assert lines == ["NEW NXTS 1:5 $0.530 +$2.12 by TODAY"]
    assert alerts([nxts], [nxts], keys, today) == ([], set())


def test_dropped_when_rounding_changes_or_vote_reappears():
    today = date(2026, 11, 3)
    sent = {"AIIO:2026-11-10", "LICN:2026-11-19"}
    aiio = ev("AIIO", date(2026, 11, 9), date(2026, 11, 10), rounding="DOWN")
    licn = ev("LICN", date(2026, 11, 18), date(2026, 11, 19), vote=date(2026, 11, 9))
    done = ev("XXII", date(2026, 11, 4), date(2026, 11, 5), status="DONE")
    lines, keys = alerts([], [aiio, licn, done], sent | {"XXII:2026-11-05"}, today)
    assert lines == ["DROPPED AIIO: now DOWN, recheck before buying",
                     "DROPPED LICN: vote pending, recheck before buying"]
    assert alerts([], [aiio, licn], sent | keys, today) == ([], set())


class Resp:
    def __init__(self, ok=True):
        self.ok = ok

    def raise_for_status(self):
        if not self.ok:
            raise RuntimeError("HTTP 503")


def test_push_text_and_ntfy():
    assert push_text(["NEW A"]) == "RSA: NEW A"
    assert len(push_text(["NEW " + "X" * 300])) == 200
    calls = []

    def post(url, **kw):
        calls.append((url, kw))
        return Resp()
    assert ntfy(["NEW A", "NEW B"], topic="t", post=post)
    assert calls[0][0] == "https://ntfy.sh/t" and calls[0][1]["data"] == b"NEW A\nNEW B"
    assert not ntfy([], topic="t", post=post)
    assert not ntfy(["NEW A"], topic="", post=post) and len(calls) == 1
    try:
        ntfy(["NEW A"], topic="t", post=lambda *a, **k: Resp(ok=False))
        raise AssertionError("an HTTP error must raise, so the alert isn't marked sent")
    except RuntimeError:
        pass


def test_tickerless_skipped_and_verify_tag():
    today = date(2026, 11, 5)
    anon = {**ev(None, date(2026, 11, 6), date(2026, 11, 9)), "ratio": None}
    early = {**ev("NXTS", date(2026, 11, 6), date(2026, 11, 9)), "rounding": "UP_EARLIER", "ratio": None}
    lines, _ = alerts([anon, early], [anon, early], set(), today)
    assert lines == ["NEW NXTS 1:? $0.530 +$2.12 by Fri Nov 6 VERIFY round-up (earlier filing)"]


def test_save_sent_roundtrip(tmp_path):
    from eqr.rsa_alert import load_sent, save_sent
    p = tmp_path / "sent.json"
    save_sent(p, {"A:2026-11-09", "B:2026-11-10:last"})
    assert load_sent(p) == {"A:2026-11-09", "B:2026-11-10:last"} and not (tmp_path / "sent.json.tmp").exists()
    p.write_text("{corrupt", encoding="utf-8")
    assert load_sent(p) == set()
