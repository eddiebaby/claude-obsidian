"""What's worth a phone push after a scan: a new buy, a buy whose last day is today, and a buy that stopped rounding
up (AIIO switched to selling the fractions after it was announced as a round-up). Each alert fires once; the keys
already sent live in a small JSON file."""
import json
import os
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from eqr.rsa import is_trading_day, next_trading_day

ET = ZoneInfo("America/New_York")
CLOSE = time(16, 0)
NTFY = "https://ntfy.sh/{topic}"


def session_day(now=None):
    """The trading day buy decisions are for: today until the 4pm ET close, then the next session."""
    now = (now or datetime.now(ET)).astimezone(ET)
    d = now.date()
    return d if is_trading_day(d) and now.time() < CLOSE else next_trading_day(d)


def _money(x):
    return "?" if x is None else (f"${x:.3f}" if x < 1 else f"${x:,.2f}")


def _by(buy_by, today):
    return "TODAY" if buy_by == today else f"{buy_by:%a %b} {buy_by.day}"


def _line(e, today):
    verify = " VERIFY round-up (earlier filing)" if e["rounding"] == "UP_EARLIER" else ""
    return (f"{e['ticker']} 1:{e['ratio'] or '?'} {_money(e['price'])} +{_money(e['gain_per_acct'])} "
            f"by {_by(e['buy_by'], today)}{verify}")


def alerts(buys, events, sent, today):
    """buys: the report's BUY section plus UP_EARLIER names; events: every event; sent: keys already alerted.
    -> (lines, keys to add to sent). Names without a ticker are skipped: they can't be bought or keyed."""
    lines, keys = [], set()
    for e in (e for e in buys if e["ticker"]):
        key = f"{e['ticker']}:{e['split_day']}"
        last = e["buy_by"] == today and f"{key}:last" not in sent
        if key not in sent:
            lines.append(f"NEW {_line(e, today)}")
            keys |= {key} | ({f"{key}:last"} if last else set())
        elif last:
            lines.append(f"LAST DAY {_line(e, today)}")
            keys.add(f"{key}:last")
    buying = {f"{e['ticker']}:{e['split_day']}" for e in buys}
    for e in events:
        key = f"{e['ticker']}:{e['split_day']}"
        if key in sent and key not in buying and e["status"] in ("OPEN", "TODAY") and f"{key}:dropped" not in sent:
            reason = "vote pending" if e.get("vote") else f"now {e['rounding']}"
            lines.append(f"DROPPED {e['ticker']}: {reason}, recheck before buying")
            keys.add(f"{key}:dropped")
    return lines, keys


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


def push_text(lines):
    """One short line for a phone notification (mobile cuts around 200 characters)."""
    text = "RSA: " + "; ".join(lines)
    return text if len(text) <= 200 else text[:197] + "..."


def ntfy(lines, topic=None, post=requests.post):
    """Push through ntfy.sh when NTFY_TOPIC is set. -> True if sent."""
    topic = topic or os.environ.get("NTFY_TOPIC")
    if not topic or not lines:
        return False
    r = post(NTFY.format(topic=topic), data="\n".join(lines).encode("utf-8"),
             headers={"Title": f"RSA: {len(lines)} alert{'s' * (len(lines) > 1)}", "Tags": "chart_with_upwards_trend"},
             timeout=30)
    r.raise_for_status()
    return True
