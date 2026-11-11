"""What's worth a phone push after a scan, each once: a new buy, a buy or check name on its last day, a buy that
stopped rounding up (AIIO switched to selling the fractions after it was announced as a round-up), a new name to
check by hand, and a new name to watch (no date yet, or a vote still pending). The keys already sent live in a small
JSON file."""
import json
import os
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from eqr.rsa import is_trading_day, next_trading_day, round_up_clause

ET = ZoneInfo("America/New_York")
HST = ZoneInfo("Pacific/Honolulu")
CLOSE = time(16, 0)
NTFY = "https://ntfy.sh/{topic}"
OPEN = ("OPEN", "TODAY")
REASON = {"UP_PARTICIPANT": "rounds up at the broker (DTC participant) level, usually no extra share for you",
          "MIXED": "the filing mentions both a round-up and cash or rounding down",
          "UNKNOWN": "no fractional-share wording found",
          "UP_EARLIER": "round-up wording is only in an earlier filing, not this split's"}


def session_day(now=None):
    """The trading day buy decisions are for: today until the 4pm ET close, then the next session."""
    now = (now or datetime.now(ET)).astimezone(ET)
    d = now.date()
    return d if is_trading_day(d) and now.time() < CLOSE else next_trading_day(d)


def _money(x):
    return "?" if x is None else (f"${x:.3f}" if x < 1 else f"${x:,.2f}")


def _day(d):
    return f"{d:%a %b} {d.day}"


def deadline(buy_by):
    """'Wed Nov 11 close (11am HST)': the clock time follows US daylight saving (10am HST in summer)."""
    h = datetime.combine(buy_by, CLOSE, ET).astimezone(HST).hour
    return f"{_day(buy_by)} close ({h % 12 or 12}{'am' if h < 12 else 'pm'} HST)"


def _head(e, last=False):
    return (f"{'LAST DAY: ' if last else ''}{e['ticker']} · 1:{e['ratio'] or '?'} · {_money(e['price'])} → "
            f"+{_money(e['gain_per_acct'])}/share")


def _entry(e, *lines, last=False):
    """A header line, the given lines, then the filing's round-up wording."""
    out = [_head(e, last), *lines]
    if e.get("excerpt"):
        out.append(f"\"{round_up_clause(e['excerpt'], back=70, ahead=110).replace('**', '')}\"")
    return "\n".join(out)


def _watch_line(e):
    if e.get("vote"):
        v = e["vote"]
        when = "vote date not found" if v == date.max else f"vote {_day(v)}"
        note = f"{when}, then buy by {_day(e['buy_by'])}" if e["buy_by"] else f"{when}, no split date yet"
    else:
        note = "no split date yet"
    return f"• {e['ticker']} 1:{e['ratio'] or '?'} · {_money(e['price'])} → +{_money(e['gain_per_acct'])} · {note}"


def alerts(act, vote, check, watch, events, sent, today):
    """The report's four sections, every event, and the keys already sent -> ({buy, check, watch}, keys to add).
    BUY and CHECK entries are a few lines each: what to do, by when, why (CHECK), and the filing's own wording,
    last-day names first. WATCH is a one-line-per-name list. A name's last-day reminder fires once whether it sits
    in BUY or CHECK. Names without a ticker are skipped: they can't be bought or keyed."""
    buy, buy_last, check_new, check_last, dropped, watching, keys = [], [], [], [], [], [], set()
    named = lambda rows: [e for e in rows if e["ticker"]]
    key = lambda e: f"{e['ticker']}:{e['split_day']}"
    for e in named(act):
        k, last = key(e), e["buy_by"] == today
        todo = f"Buy 1 share by {deadline(e['buy_by'])}"
        if k not in sent:
            (buy_last if last else buy).append(_entry(e, todo, last=last))
            keys |= {k} | ({f"{k}:last"} if last else set())
        elif last and f"{k}:last" not in sent:
            buy_last.append(_entry(e, todo, last=True))
            keys.add(f"{k}:last")
    checking = {key(e): e for e in named(check)}
    buying = {key(e) for e in act}
    for e in named(events):
        k = key(e)
        if k in sent and k not in buying and e["status"] in OPEN and f"{k}:dropped" not in sent:
            if k in checking:
                why = f"moved to CHECK, {REASON.get(e['rounding'], e['rounding'])}"
                keys.add(f"check:{k}")      # the DROPPED line says it all; no separate CHECK entry
            elif e.get("vote"):
                why = "a shareholder vote is pending again"
            else:
                why = f"now {e['rounding']}"
            dropped.append(f"DROPPED {e['ticker']}: {why}. Recheck before buying.")
            keys.add(f"{k}:dropped")
    for e in named(check):
        k, last = key(e), e["buy_by"] == today
        lines = [f"Why: {REASON.get(e['rounding'], e['rounding'])}",
                 f"If it checks out, buy 1 share by {deadline(e['buy_by'])}"]
        if f"check:{k}" not in sent | keys:
            (check_last if last else check_new).append(_entry(e, *lines, last=last))
            keys |= {f"check:{k}"} | ({f"{k}:last"} if last else set())
        elif last and f"{k}:last" not in sent:
            check_last.append(_entry(e, *lines, last=True))
            keys.add(f"{k}:last")
    for e in named(vote) + named(watch):
        k = f"watch:{e['ticker']}:{str(e['filed'])[:7]}"     # once a month per name: a later split alerts again
        if k not in sent:
            watching.append(_watch_line(e))
            keys.add(k)
    return {"buy": buy_last + buy, "check": check_last + check_new + dropped, "watch": watching}, keys


SECTIONS = (("buy", "BUY: rounds up per holder", "\n\n"),
            ("check", "CHECK: read the filing before buying", "\n\n"),
            ("watch", "WATCH: vote pending or no date yet", "\n"))


def message(groups):
    """The push body: BUY entries, then CHECK entries, then the WATCH list, each under a heading."""
    return "\n\n".join(f"{head}\n{sep.join(groups[k])}" for k, head, sep in SECTIONS if groups.get(k))


def load_sent(path):
    try:
        return set(json.loads(Path(path).read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return set()


def save_sent(path, sent):
    """Atomic: a half-written file would read back empty and re-fire every alert."""
    tmp = Path(f"{path}.tmp")
    tmp.write_text(json.dumps(sorted(sent), indent=0), encoding="utf-8")
    os.replace(tmp, path)


def push_text(groups):
    """One short line (mobile cuts around 200 characters): each BUY/CHECK header, then the WATCH count."""
    heads = [e.split("\n", 1)[0] for k in ("buy", "check") for e in groups.get(k, [])]
    heads += [f"{len(groups['watch'])} to watch"] if groups.get("watch") else []
    text = "RSA: " + "; ".join(heads)
    return text if len(text) <= 200 else text[:197] + "..."


def title(groups):
    """'RSA: LAST DAY · 2 buy, 1 check, 5 watch'."""
    last = any(e.startswith("LAST DAY") for k in ("buy", "check") for e in groups.get(k, []))
    counts = ", ".join(f"{len(groups[k])} {k}" for k, _, _ in SECTIONS if groups.get(k))
    return f"RSA: {'LAST DAY · ' if last else ''}{counts}"


def ntfy(groups, topic=None, post=requests.post):
    """Push through ntfy.sh when NTFY_TOPIC is set. -> True if sent."""
    topic = topic or os.environ.get("NTFY_TOPIC")
    if not topic or not any(groups.values()):
        return False
    r = post(NTFY.format(topic=topic), data=message(groups).encode("utf-8"),
             headers={"Title": title(groups), "Tags": "chart_with_upwards_trend"}, timeout=30)
    r.raise_for_status()
    return True
