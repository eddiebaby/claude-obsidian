"""Reverse-split arbitrage: turn EDGAR full-text-search hits into split events (ratio, first split-adjusted
trading day, fractional-share treatment). Only a per-holder round-up pays: 1 pre-split share becomes 1 post-split
share worth about ratio x price. Rounding "at the DTC-participant level" happens at the broker, not per account."""
import re
import urllib.parse
from collections import defaultdict
from datetime import date, timedelta

FTS = "https://efts.sec.gov/LATEST/search-index"
ANNOUNCE_FORMS = "8-K,6-K"   # adding "/A" forms makes EDGAR return only amendments
PROXY_FORMS = "PRE 14A,DEF 14A,PRE 14C,DEF 14C"
ANNOUNCE_QUERIES = ('"reverse stock split" fractional', '"reverse split" fractional', '"share consolidation" fractional')
PROXY_QUERIES = ('"reverse stock split" "rounded up"', '"reverse split" "rounded up"', '"reverse stock split" "round up"')
CLUSTER_DAYS = 21      # announcement filings this close to the newest one describe the same split

NYSE_HOLIDAYS = frozenset(date.fromisoformat(d) for d in (
    "2026-01-01 2026-01-19 2026-02-16 2026-04-03 2026-05-25 2026-06-19 2026-07-03 2026-09-07 2026-11-26 2026-12-25 "
    "2027-01-01 2027-01-18 2027-02-15 2027-03-26 2027-05-31 2027-06-18 2027-07-05 2027-09-06 2027-11-25 2027-12-24"
).split())


def is_trading_day(d):
    return d.weekday() < 5 and d not in NYSE_HOLIDAYS


def prev_trading_day(d):
    d -= timedelta(1)
    while not is_trading_day(d):
        d -= timedelta(1)
    return d


def next_trading_day(d):
    d += timedelta(1)
    while not is_trading_day(d):
        d += timedelta(1)
    return d


def on_or_after(d):
    return d if is_trading_day(d) else next_trading_day(d)


def fts_url(q, forms, start, end, frm=0, ciks=None):
    """ciks: one 10-digit CIK to search a single company's filings."""
    params = {"q": q, "forms": forms, "dateRange": "custom", "startdt": start.isoformat(), "enddt": end.isoformat(),
              "from": frm}
    return FTS + "?" + urllib.parse.urlencode({**params, **({"ciks": ciks} if ciks else {})})


def hit_meta(hit):
    s = hit["_source"]
    adsh, fname = hit["_id"].split(":", 1)
    cik = int(s["ciks"][0])
    shown = s["display_names"][0]
    m = re.match(r"\s*(.*?)\s+\(([^()]*)\)\s+\(CIK \d+\)", shown)
    tickers = [t.strip() for t in m.group(2).split(",")] if m else []
    if m and all(re.fullmatch(r"[A-Z0-9.\-]{1,7}", t) for t in tickers):
        name = m.group(1)
    else:
        name, tickers = re.sub(r"\s*\(CIK \d+\)", "", shown).strip(), []
    return {"cik": cik, "name": name, "ticker": tickers[0] if tickers else None, "tickers": tickers,
            "form": s["form"], "file_type": s.get("file_type"), "filed": s["file_date"],
            "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fname}"}


MULTI_FUND = 4      # a filer with this many tickers is a fund trust (ProShares Trust II), not one company


_ITEM = re.compile(r"\bItem\s+\d\.\d\d\b")     # where an 8-K's body starts, after the cover's securities table


def _named(tickers, text):
    return [t for t in tickers if re.search(rf"(?<![A-Za-z0-9.\-/]){re.escape(t)}(?![A-Za-z0-9\-/])", text)]


def named_ticker(tickers, text):
    """The filer's ticker the document is about. The body (after the 8-K cover, whose table can list every security)
    decides when it names exactly one of the filer's tickers. Otherwise an ordinary company keeps its first ticker,
    the common stock as SEC lists it; a fund trust (ProShares Trust II: VIXM's split, not AGQ's) needs exactly one
    fund named in the body or, failing that, the cover, or gets no ticker rather than a guess."""
    if len(tickers) <= 1:
        return tickers[0] if tickers else None
    m = _ITEM.search(text)
    named = _named(tickers, text[m.start():] if m else text)
    if len(named) == 1:
        return named[0]
    if len(tickers) < MULTI_FUND:
        return tickers[0]
    cover = _named(tickers, text[:m.start()]) if m and not named else []
    return cover[0] if len(cover) == 1 else None


def normalize(text):
    t = re.sub(r"[‐-―−]", "-", text)
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", t.replace("\xa0", " ").replace("�", " "))


_UNITS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                     "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
_TENS = {w: 10 * i for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"}
_ORDINALS = {"first": "one", "second": "two", "third": "three", "fifth": "five", "eighth": "eight", "ninth": "nine",
             "twelfth": "twelve"}


def words_to_int(tokens):
    """Leading run of number words -> value ('two hundred fifty' -> 250), or None."""
    total, cur, used = 0, 0, 0
    for t in (x.lower() for x in tokens):
        if t in _UNITS:
            cur += _UNITS[t]
        elif t in _TENS:
            cur += _TENS[t]
        elif t == "hundred":
            cur = (cur or 1) * 100
        elif t == "thousand":
            total, cur = total + (cur or 1) * 1000, 0
        elif t == "and" and used:
            continue
        else:
            break
        used += 1
    return total + cur if used else None


def _val(s):
    s = s.strip()
    return int(s) if s.isdigit() else words_to_int(re.split(r"[\s-]+", s))


def _cardinal(ordinal):
    *head, last = ordinal.lower().split("-")
    last = _ORDINALS.get(last) or (last[:-4] + "y" if last.endswith("ieth") else last[:-2])
    return words_to_int(head + [last])


_NW = "(?:" + "|".join(sorted(list(_UNITS) + list(_TENS) + ["hundred", "thousand"], key=len, reverse=True)) + ")"
_N = rf"(?P<w>\d{{1,4}}(?:\.\d+)?(?!\d)|{_NW}(?:[\s-]+{_NW}){{0,3}}\b)"
_P = r"(?:\s*\((?P<p>[^)]{1,14})\))?"
_FOR = r"\s*-?\s*for\s*-?\s*"
_MENTIONS = (   # (pattern, is a share-consolidation 'every N' form)
    (re.compile(r"\b(?:1|one)" + _FOR + _N + _P, re.I), False),                          # 1-for-10, one-for-forty (1-for-40)
    (re.compile(r"\b" + _N + _P + r"\s*-?\s*(?:for|to)\s*-?\s*(?:one|1)\b(?:\s*\(1\))?", re.I), False),  # five (5)-for-one (1)
    (re.compile(r"\bratio of\s+1\s*:\s*(?P<w>\d{1,4})\b", re.I), False),
    (re.compile(r"\b(?:each|every)\s+" + _N + _P, re.I), True),                           # every ten (10) shares ... into one
)
_JOIN = re.compile(r"\s*,?\s*(?:to|and|through|or)\s+(?:not more than\s+|a maximum of\s+|up to\s+)?", re.I)
_CAP_BEFORE = re.compile(r"(?:not to exceed|up to|maximum of|no (?:more|greater) than|not more than|cap of|"
                         r"capped at)\s+(?:a\s+)?(?:ratio\s+of\s+)?$", re.I)
_COMBINE = re.compile(r"consolidat|combined|reclassif|converted", re.I)
_ORD_OF = re.compile(r"\bone[\s-]+((?:[a-z]+-)?[a-z]+?(?:th|ieth))\s+of\s+the\s+(?:[\w'-]+\s+){0,4}?shares", re.I)


def _mentions(t):
    """Every ratio mention as (start, end, value, kind), left to right, overlaps dropped. kind: 'for' (1-for-N,
    N-for-1), 'every' ('every N shares ... consolidated into one'), or 'loose' (an 'every N' with no consolidation
    nearby, which only counts as the far end of a range)."""
    out = []
    for pat, every in _MENTIONS:
        for m in pat.finditer(t):
            p = re.findall(r"\d{1,4}", m.groupdict().get("p") or "")
            v = int(p[-1]) if p else _val(m.group("w").split(".")[0])
            kind = "for" if not every else "every" if _COMBINE.search(t, m.end(), m.end() + 300) else "loose"
            if v:
                out.append((m.start(), m.end(), v, kind))
    out.sort(key=lambda x: (x[0], -x[1]))
    kept = []
    for x in out:
        if not kept or x[0] >= kept[-1][1]:
            kept.append(x)
    return kept


def extract_ratio(t):
    """-> (ratio, (lo, hi) or None). Two mentions joined by to/and/or ('not less than 1-for-2 and not more than
    1-for-20') are a range: the board hasn't picked a ratio. The ratio is the first mention outside any range."""
    ms, rng, in_range = _mentions(t), None, set()
    for i, (a, b, v, _) in enumerate(ms):
        if i + 1 < len(ms) and _JOIN.fullmatch(t[b:ms[i + 1][0]]):
            lo, hi = sorted((v, ms[i + 1][2]))
            rng = rng or (lo, hi)
            in_range |= {i, i + 1}
        elif _CAP_BEFORE.search(t[max(0, a - 40):a]):
            rng = rng or (None, v)
            in_range.add(i)
    for kind in ("for", "every"):
        for i, (a, b, v, k) in enumerate(ms):
            if k == kind and i not in in_range and v >= 2:
                return v, rng
    for m in _ORD_OF.finditer(t):
        v = _cardinal(m.group(1))
        if v and v >= 2:
            return v, rng
    return None, rng


_MONTHS = {m: i + 1 for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}
_DATE = re.compile(r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept?(?:ember)?|"
                   r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d\d)\b", re.I)
_TRADE_CUE = re.compile(r"split[\s-]adjusted|open(?:ing)? of (?:trading|business|the market)|market opens|"
                        r"market open\b|begins? trading|commences? trading", re.I)
_EFFECTIVE_CUE = re.compile(r"\beffective|\btakes? effect", re.I)
_DEADLINE = re.compile(r"(?:prior to|no later than|not later than|until|on or before|before|after|ended|ending|"
                       r"beginning)\s+$", re.I)
_AFTER_CLOSE = re.compile(r"\b(?:[4-9]|1[01]):\d\d\s*p\.?\s*m|after (?:the )?(?:market )?close", re.I)
_SPLIT_CTX = re.compile(r"split|consolidat|effective time|certificate of (?:amendment|change)|articles of amendment",
                        re.I)
DATE_WINDOW, AFTER_WINDOW = 250, 150


def _to_date(m):
    try:
        return date(int(m.group(3)), _MONTHS[m.group(1)[:3].lower()], int(m.group(2)))
    except ValueError:
        return None


def first_split_day(t, not_before=None, not_after=None):
    """-> (first split-adjusted trading day, 'trading' | 'effective' | 'past') or (None, None). Prefers a date right
    after a trading cue ('split-adjusted basis', 'opening of trading'); otherwise the effective date, moved to the
    next session when the split takes effect after the close. The date must sit next to split wording, and deadlines
    ('prior to October 29, 2027', 'periods beginning after December 15') don't count. A split dated before
    not_before already happened: returned as 'past' only when the text names no newer one."""
    prev_end, effective, past = 0, None, None
    for m in _DATE.finditer(t):
        d, window = _to_date(m), t[max(prev_end, m.start() - DATE_WINDOW):m.start()]
        prev_end = m.end()
        if d is None or (not_after and d > not_after) or _DEADLINE.search(t[max(0, m.start() - 25):m.start()]):
            continue
        if not _SPLIT_CTX.search(window + t[m.end():m.end() + AFTER_WINDOW]):
            continue
        cue = "trading" if _TRADE_CUE.search(window) else "effective" if _EFFECTIVE_CUE.search(window) else None
        if cue and not_before and d < not_before:
            past = max(past or d, d)
        elif cue == "trading":
            return on_or_after(d), "trading"
        elif cue and effective is None:
            effective = next_trading_day(d) if _AFTER_CLOSE.search(window) else on_or_after(d)
    if effective:
        return effective, "effective"
    return (past, "past") if past else (None, None)


_UP = re.compile(r"round(?:ed|ing|s)?\s+up|(?:receive|issue|issued|hold|entitled to)\s+(?:\w+\s+){0,6}?"
                 r"(?:one|1|a|an)\s+(?:\(1\)\s+)?(?:full|whole|additional)\s+(?:[\w'-]+\s+){0,6}?share", re.I)
_NOT = re.compile(r"\b(?:no|not|nor|without)\b", re.I)
_CASH = re.compile(r"\bcash\s+(?:payment|payments|in lieu|equal|amount|value)|\bamount in cash|"
                   r"\b(?:receive|pay|paid)\s+(?:\w+\s+){0,4}?cash\b|"
                   r"\bredeemed (?:for|in) cash", re.I)   # VIXM: 'fractional shares will be redeemed for cash'
_BOILERPLATE = re.compile(r"U\.S\. Holder|tax basis|capital (?:gain|loss)|federal income tax|backup withholding|"
                          r"information reporting|information returns|\bIRS\b|specific assets|in specie|"
                          r"Section 262|appraisal rights|\bDGCL\b|fractional depositary receipts",
                          re.I)   # ARAI: Delaware appraisal-rights text   # tax sections and articles' asset-distribution clauses, not the split
_DOWN = re.compile(r"round(?:ed|ing)?\s+down|\bdisregarded\b", re.I)
_PARTICIPANT = re.compile(r"participant[\s-]+level|participant[\s-]+by[\s-]+participant|"
                          r"level of (?:each |the )?(?:dtc )?participant|"
                          r"(?:share|stock)?holders? (?:who|that) are (?:dtc |direct )?participants|"
                          r"participants? become entitled", re.I)   # SLXN: 'shareholders who are DTC participants'
_RECORD_LEVEL = re.compile(r"record[\s-]+holder[\s-]+by[\s-]+record[\s-]+holder|holder[\s-]+of[\s-]+record[\s-]+level",
                           re.I)
_ANTI = re.compile(r"reserves? the right|arbitrage|\babus|manipulat|limited to one|in excess of one|"
                   r"(?:acquired|purchased)\s+(?:\w+\s+){0,3}?(?:after|following|on or after)", re.I)


def _fraction_windows(t, before=300, after=400):
    spans = []
    for m in re.finditer(r"fraction", t, re.I):
        a, b = max(0, m.start() - before), m.end() + after
        if spans and a <= spans[-1][1]:
            spans[-1][1] = b
        else:
            spans.append([a, b])
    return [t[a:b] for a, b in spans]


_STOP = re.compile(r"\.[\")]?\s")


def _sentence(w, pos, back=250, ahead=350):
    """The sentence around pos. Where no sentence break is in reach, cut at a word break and mark the cut with '…'."""
    stops = [m.end() for m in _STOP.finditer(w, max(0, pos - back), pos)]
    a = stops[-1] if stops else w.find(" ", max(0, pos - back)) + 1
    lead = "" if stops or a == 0 else "…"
    end = _STOP.search(w, pos)
    if end and end.start() < pos + ahead:
        return lead + w[a:end.start() + 1].strip()
    b = w.rfind(" ", pos, pos + ahead) if pos + ahead < len(w) else len(w)
    return lead + w[a:b].strip() + ("…" if b < len(w) else "")


_SENTENCE_END = re.compile(r"(?<![A-Z])\.[\")]?\s")     # not 'U.S. Holder'


def _same_sentence(w, pos, back=150, ahead=200):
    """The sentence around pos (at most `back` chars before it and `ahead` after): tax wording can come after the
    cash phrase ('payments of cash in lieu … may be subject to backup withholding')."""
    seg = w[max(0, pos - back):pos]
    stops = list(_SENTENCE_END.finditer(seg))
    rest = w[pos:pos + ahead]
    end = _SENTENCE_END.search(rest)
    return (seg[stops[-1].end():] if stops else seg) + (rest[:end.start()] if end else rest)


def classify_rounding(t):
    """-> (UP | UP_PARTICIPANT | CASH | MIXED | DOWN | UNKNOWN, flags, excerpt). Read near 'fraction' only, so the
    ratio sentence ('one share for every ten') isn't mistaken for a round-up."""
    up, cash, down, anti = [], [], [], []
    for w in _fraction_windows(t):
        up += [(w, m.start()) for m in _UP.finditer(w) if not _NOT.search(w[max(0, m.start() - 15):m.start()])]
        cash += [(w, m.start()) for m in _CASH.finditer(w) if not _NOT.search(w[max(0, m.start() - 20):m.start()])
                 and not _BOILERPLATE.search(_same_sentence(w, m.start()))]
        down += [(w, m.start()) for m in _DOWN.finditer(w)]
        anti += [(w, m.start()) for m in _ANTI.finditer(w)]
    participant = _PARTICIPANT.search(t)
    flags = []
    if participant:
        flags.append("participant-level rounding")
    if _RECORD_LEVEL.search(t):
        flags.append("record-holder aggregation")
    if anti:
        flags.append("anti-arb wording")
    if up and (cash or down):   # e.g. shares rounded up but award fractions 'rounded down': read it by hand
        cls, hit = "MIXED", up[0]
    elif up:
        cls, hit = ("UP_PARTICIPANT" if participant else "UP"), up[0]
    elif cash:
        cls, hit = "CASH", cash[0]
    elif down:
        cls, hit = "DOWN", down[0]
    else:
        return "UNKNOWN", flags, ""
    excerpt = _sentence(*hit)
    if participant:
        excerpt += " … " + _sentence(t, participant.start())
    for w, pos in anti[:1]:
        excerpt += " … " + _sentence(w, pos)
    return cls, flags, excerpt


def mark_round_up(text):
    """Bold the round-up phrase so the report shows why a name was classed UP."""
    return _UP.sub(lambda m: f"**{m.group(0)}**", text)


def round_up_clause(excerpt, back=100, ahead=160):
    """The excerpt for the report: each part cut to `back`/`ahead` chars around its round-up phrase (on word
    breaks), repeats dropped, the phrase bolded."""
    parts = []
    for part in excerpt.split(" … "):
        m = _UP.search(part)
        a, b = (max(0, m.start() - back), m.end() + ahead) if m else (0, back + ahead)
        if a:
            a = part.find(" ", a) + 1
        if b < len(part):
            b = part.rfind(" ", a, b) if part.rfind(" ", a, b) > a else b
        cut = ("…" if a else "") + part[a:b].strip() + ("…" if b < len(part) else "")
        if cut.strip("…") not in (p.strip("…") for p in parts):
            parts.append(cut)
    return mark_round_up(" … ".join(parts))


def parse_doc(text, filed):
    t = normalize(text)
    ratio, rng = extract_ratio(t)
    f = date.fromisoformat(filed)
    day, kind = first_split_day(t, not_before=f - timedelta(7), not_after=f + timedelta(MAX_LEAD_DAYS))
    rounding, flags, excerpt = classify_rounding(t)
    return {"ratio": ratio, "ratio_range": rng, "split_day": day, "date_kind": kind, "mentions": len(_MENTION.findall(t)),
            "meeting": bool(_MEETING.search(t)), "meeting_day": meeting_day(t), "approved": approved(t),
            "financials": len(_FINANCIALS.findall(t)) >= 3, "rounding": rounding, "flags": flags, "excerpt": excerpt}


def approved(t):
    """Shareholders already approved it: past-tense wording not inside 'whether/if the shareholders have approved'."""
    return any(not _CONDITIONAL.search(t[max(0, m.start() - 25):m.start()]) for m in _APPROVED.finditer(t))


def meeting_day(t):
    """Date of the shareholder meeting that votes on the split ('Extraordinary General Meeting ... to be held on
    November 9, 2026'), or None."""
    for m in _DATE.finditer(t):
        if _MEETING_BEFORE.search(t[max(0, m.start() - 110):m.start()]):
            return _to_date(m)
    return None


MAX_LEAD_DAYS = 90     # splits are announced days to weeks ahead; a later date is a deadline or a closing date
_MENTION = re.compile(r"reverse (?:stock |share )?split|share consolidation|stock consolidation", re.I)
_MEETING = re.compile(r"notice of (?:an? |the )?(?:extraordinary |annual |special )*(?:general )?meeting|"
                      r"proxy solicited|meeting of (?:share|stock)holders,? (?:to be|will be) held|"
                      r"general meeting to be held|will hold an? (?:extraordinary |annual |special )*(?:general )?meeting",
                      re.I)
_MEETING_BEFORE = re.compile(r"meeting\b[^.;]{0,90}?\b(?:on|held on)\s+$", re.I)
_APPROVED = re.compile(r"(?:were|was|have been|has been) (?:duly )?(?:approved|passed|adopted) by (?:the )?"
                       r"(?:share|stock)holders|(?:share|stock)holders (?:have )?approved|(?:received|obtained|"
                       r"announces?) (?:the )?(?:share|stock)holder approval|results of (?:the )?"
                       r"(?:extraordinary|annual|special)|(?:resolutions?|proposals?) (?:were|was) (?:duly )?"
                       r"(?:approved|passed)|matters (?:voted on|submitted)[\w\s]{0,80}? were (?:duly )?"
                       r"(?:approved|passed)", re.I)   # past tense only: 'subject to shareholder approval' is pending
_CONDITIONAL = re.compile(r"\b(?:whether|if|once|when|until|unless)\b", re.I)
_FINANCIALS = re.compile(r"balance sheets?|statements? of operations|statements? of cash flows", re.I)
MIN_MENTIONS = {"announce": 3, "proxy": 8}   # preferred designations and equity plans mention a split once or twice
_AGREEMENT = ("EX-2", "EX-4", "EX-10")       # merger agreements, warrants, contracts
_SPLIT_WORD = re.compile(r"reverse (?:stock |share )?split|consolidation", re.I)


def is_proxy(form):
    return form.startswith(("PRE", "DEF"))


def is_notice(doc):
    """A proxy, or a foreign issuer's undated meeting notice filed as a 6-K exhibit. A dated meeting notice stays an
    announcement and the event carries vote_pending instead."""
    return (is_proxy(doc["form"]) or doc.get("precedent", False)
            or (doc.get("meeting", False) and not doc.get("split_day")))


def is_relevant(doc):
    """Drops agreements, financial statements, and documents that barely mention a split, except a short
    announcement whose fractional-share sentence is itself about the split ('fractional shares resulting from the
    reverse stock split will be disregarded')."""
    if doc.get("wire"):
        return True     # picked by a split headline; a headline or feed excerpt is too short to count mentions
    if doc.get("financials") or (doc.get("file_type") or "").startswith(_AGREEMENT):
        return False
    n = doc.get("mentions", MIN_MENTIONS["proxy"])
    if is_notice(doc) and not doc.get("precedent"):
        return n >= MIN_MENTIONS["proxy"]
    return n >= MIN_MENTIONS["announce"] or (n >= 1 and bool(_SPLIT_WORD.search(doc.get("excerpt", ""))))


def vote_pending(core):
    """None, or the meeting date (possibly already past) when the cluster has a meeting notice and no approval."""
    if any(d.get("approved") for d in core) or not any(d.get("meeting") for d in core):
        return None
    return next((d["meeting_day"] for d in core if d.get("meeting_day")), date.max)


_ORDER = ("UP_PARTICIPANT", "MIXED", "UP", "CASH", "DOWN")


def _combine(classes):
    if "UP" in classes and classes & {"CASH", "DOWN"}:
        return "MIXED"
    return next((c for c in _ORDER if c in classes), "UNKNOWN")


def _treatment(docs):
    """docs newest first -> (rounding, changed_from). The newest filing date that states a treatment wins: a company
    can announce a round-up and then switch to selling the fractions in its meeting-results release."""
    known = [d for d in docs if d["rounding"] != "UNKNOWN"]
    if not known:
        return "UNKNOWN", None
    latest = _combine({d["rounding"] for d in known if d["filed"] == known[0]["filed"]})
    older = _combine({d["rounding"] for d in known if d["filed"] != known[0]["filed"]})
    return latest, (older if older not in ("UNKNOWN", latest) else None)


def window_status(split_day, today):
    """-> (status, buy_by). buy_by is the last pre-split session; holding at its close is what earns the round-up."""
    if split_day is None:
        return "NO_DATE", None
    buy_by = prev_trading_day(split_day)
    if split_day <= today:
        return "DONE", buy_by
    if buy_by < today:
        return "MISSED", buy_by
    return ("TODAY" if buy_by == today else "OPEN"), buy_by


def merge_events(docs, today):
    """docs: hit_meta + parse_doc dicts. One event per company: announcement filings (8-K/6-K) within CLUSTER_DAYS
    of the newest one; proxies only fill in the rounding when no announcement states it. Documents that barely
    mention a split are dropped. A fund trust whose documents name different funds gets one event per fund."""
    by_cik = defaultdict(list)
    for d in filter(is_relevant, docs):
        by_cik[d["cik"]].append(d)
    groups = []
    for cik, ds in by_cik.items():
        funds = {d["ticker"] for d in ds if d["ticker"] and len(d.get("tickers") or ()) >= MULTI_FUND}
        groups += [(cik, [d for d in ds if d["ticker"] == f]) for f in sorted(funds)] if len(funds) > 1 else [(cik, ds)]
    events = []
    for cik, ds in groups:
        ds.sort(key=lambda d: d["filed"], reverse=True)
        ann = [d for d in ds if not is_notice(d)]
        proxies = [d for d in ds if is_notice(d)]
        newest = date.fromisoformat((ann or proxies)[0]["filed"])
        core = [d for d in (ann or proxies) if (newest - date.fromisoformat(d["filed"])).days <= CLUSTER_DAYS]
        flags = list(dict.fromkeys(f for d in core for f in d["flags"]))
        source = core
        rounding, changed = _treatment(core)
        if rounding == "UNKNOWN" and ann and proxies:
            source = proxies
            rounding, changed = _treatment(proxies)
            src = next((d for d in proxies if d["rounding"] == rounding), None)
            if src:
                flags.append(f"rounding from {src['form']} filed {src['filed']}")
        stated = rounding
        excerpt = next((d["excerpt"] for d in source if d["rounding"] == stated and d["excerpt"]),
                       next((d["excerpt"] for d in source if d["excerpt"]), ""))
        if source is proxies and rounding == "UP" and src.get("precedent"):
            rounding = "UP_EARLIER"     # another split's filing: a guess about this one, read it by hand
        if rounding in ("UP", "UP_EARLIER") and any("participant-level rounding" in d["flags"] for d in ds):
            rounding = "UP_PARTICIPANT"     # stated once, in any of the company's split filings, it still applies
            flags = list(dict.fromkeys(flags + ["participant-level rounding"]))
        if changed:
            flags.append(f"treatment changed: earlier filing said {changed}")
        split_day = next((d["split_day"] for d in core if d["split_day"]), None) if ann else None
        status, buy_by = window_status(split_day, today)
        ratio_range = next((d["ratio_range"] for d in core + proxies if d["ratio_range"]), None)
        ratio = next((d["ratio"] for d in core if d["ratio"]), None)
        if not ann and ratio_range:
            ratio = None        # a proxy's lone 1-for-N is usually an illustration; the range is what's proposed
        if ann and not ratio and not ratio_range:
            ratio = next((d["ratio"] for d in proxies if d["ratio"]), None)   # a release that names no ratio
        events.append({
            "cik": cik, "ticker": next((d["ticker"] for d in ds if d["ticker"]), None), "name": core[0]["name"],
            "stage": "announced" if ann else "proxy", "filed": core[0]["filed"],
            "ratio": ratio, "ratio_range": ratio_range,
            "proposed_day": None if ann else next((d["split_day"] for d in core
                                                   if d["split_day"] and d["date_kind"] != "past"), None),
            "split_day": split_day, "buy_by": buy_by, "status": status, "vote": vote_pending(core) if ann else None,
            "rounding": rounding, "flags": flags, "excerpt": excerpt,
            "urls": list(dict.fromkeys(d["url"] for d in core)),
        })
    return events
