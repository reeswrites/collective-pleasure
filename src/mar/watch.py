"""Household replay viewer (`mar watch`; docs/notes/viewer.md). Reads one household run's observer tables (docs/notes/observer-schema.md)
and builds a self-contained HTML page: a week slider with play, each member's mood in plain words, the household, an event feed,
decision cards for formation, stay readings and leaves, two small charts, and a side-by-side compare of the same pairing under two arms.

Free and deterministic: scripted agents, no model calls. A run with no observer file is re-run with the observer on (same outcomes as
the original run; tests/test_observer.py). Wording rule (ADR 0010): agents feel nothing; "mood", "lonely", "content" are glosses for
modeled states, and the page says so.

Run keys (the same as runs/observer-demo and, for exit fallbacks without the trailing seed, as runs/atlas):
  h38   <arm>|<persona A>|<persona B>|<seed>     H38 pairing norms (scripts/h38_pairing_run.py arms, e.g. L0, L4), stay readings on
  ef    <arm>|<rule set>|<validation run>        exit fallbacks slice 2, items on, cell V2-split-loves (arms F0, F4, F5)
"""
import dataclasses
import json
import sys
from pathlib import Path

from . import observe as OB

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE = ROOT / "runs" / "watch"
DEMO = ROOT / "runs" / "observer-demo"
CFG = OB.ObsConfig(replay_rate=0.05, replay_window=13, replay_leaves=True, replay_pressure=True, replay_seed=0)
EF_CELL = "V2-split-loves"
FAMILIES = ("h38", "ef")


def _scripts():
    p = str(ROOT / "scripts")
    if p not in sys.path:
        sys.path.insert(0, p)


def norm_key(family, run):
    """(family, run) -> the observer run key, e.g. ("h38", "L0|a|b|0") -> "h38|L0|a|b|0". Accepts the full key too, and the atlas's
    exit-fallbacks key with its trailing seed."""
    parts = [x for x in str(run).split("|") if x != ""]
    if parts and parts[0] == family:
        parts = parts[1:]
    if family == "h38":
        if len(parts) == 3:
            parts.append("0")
        if len(parts) != 4:
            raise ValueError(f"h38 run key is <arm>|<persona A>|<persona B>|<seed>, got {run!r}")
    elif family == "ef":
        if len(parts) == 4 and parts[3] == "0":
            parts = parts[:3]
        if len(parts) != 3:
            raise ValueError(f"ef run key is <arm>|<rule set>|<validation run>, got {run!r}")
    else:
        raise ValueError(f"unknown family {family!r}; one of {', '.join(FAMILIES)}")
    return "|".join([family] + parts)


def file_name(key):
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in key) + ".jsonl.gz"


def play(key):
    """Re-run one household with the observer on -> Observer (finished)."""
    fam, *p = key.split("|")
    _scripts()
    if fam == "h38":
        return _play_h38(p[0], p[1], p[2], int(p[3]), key)
    return _play_ef(p[0], p[1], int(p[2]), key)


def _play_h38(arm, a, b, seed, key):
    """= scripts/observer_demo.play_h38 (h38_pairing_run.play with the stay readings), any arm."""
    import h38_pairing_run as P
    from . import exit_fallback as EF
    from . import exit_items as EI
    from . import hedonic as HD
    from . import negotiation as NG
    from . import pairing as PR
    from . import retest as RT
    from .worlds import household as H
    if arm not in P.ARMS:
        raise ValueError(f"unknown H38 arm {arm!r}; one of {', '.join(P.ARMS)}")
    ps = RT.personas()
    for x in (a, b):
        if x not in ps:
            raise ValueError(f"unknown persona {x!r}")
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=P.ARMS[arm])
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), \
            EI.use_items(EI.GRID[P.CELL]), OB.collecting():
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=H.WEEKS, decline=True)
        world = lived.world
        ob = OB.Observer(world, CFG, run_key=key, meta={"family": "h38", "arm": arm}, harness=lived)
        last = {"busy": {"A": False, "B": False}}
        for w in range(world.weeks):
            if w and w % NG.REVIEW_EVERY == 0:
                if lived.apart and lived.decline:
                    lived.retry(w, last)
                elif all(world.p[r]["in"] for r in "AB"):
                    ob.stay(w, PR.stay_reading(world, w, last))
                    lived.reading(w, last)
            if world.early_review:
                world.ladder_reviewed(w)
            last = {"busy": world.step_week(w, last)}
    return ob.finish()


def _play_ef(arm, cand, i, key):
    """= scripts/observer_demo.play_ef (exit_fallbacks_run.play_items for validation run i), any arm and rule set."""
    import exit_fallbacks_run as X
    from . import exit_fallback as EF
    from . import exit_items as EI
    from . import hedonic as HD
    from . import world_api as W
    from .cards import load_cards
    from .worlds import household as H
    hr = X.ctx("val").runs[i]
    ps = W.hh_personas()
    cfg = dataclasses.replace(HD.DEFAULT, job_loss_rate=hr.rates[0], illness_rate=hr.rates[1], move_rate=hr.rates[2],
                              new_connection_rate=hr.rates[3], start=hr.start)
    if not (H.RULES / cand).exists():
        raise ValueError(f"unknown rule set {cand!r}")
    box = {}
    with EF.use_exit_fallback(arm, strip_split=True), EI.use_items(EI.GRID[EF_CELL]), OB.collecting():
        gate = H.PyGate(load_cards(str(H.RULES / cand)))

        def go():
            with HD.use_levers(X.LEVERS):
                wk = H.WeeklyWorld(gate, (ps[hr.a], ps[hr.b]), hr.seed, hr.weeks, cfg)
                box["ob"] = OB.Observer(wk, CFG, run_key=key, meta={"family": "ef", "arm": arm, "run": i})
                wk.play()
            return wk
        W._with_rates(hr.rates, go)
    return box["ob"].finish()


def find(key, dirs=None):
    """The observer file for a run key, if one exists (runs/watch, then runs/observer-demo)."""
    for d in dirs or (CACHE, DEMO):
        p = Path(d) / "obs" / file_name(key)
        if p.exists():
            return p
    return None


def load(key, cache=CACHE, rerun=True):
    """Observer tables for a run key: read the file if there is one, else re-run with the observer on and write it to cache."""
    p = find(key, [cache, DEMO] if cache else None)
    if p is None:
        if not rerun:
            raise FileNotFoundError(f"no observer file for {key}")
        OB.write_run(play(key), cache)
        p = Path(cache) / "obs" / file_name(key)
    return OB.read(p)


# ---- names and plain words -----------------------------------------------------------------------------------------------------

NAMES = ("Kit", "Hollis", "Ash", "Ellis", "Arden", "Drew", "Jules", "Finley", "Jody", "Dale", "Casey", "Wren", "Rowan", "Sage",
         "Remy", "Quinn", "Tate", "Blair", "Lane", "Marlow", "Noor", "Pax", "Reed", "Shay")


def names_for(personas):
    """Neutral made-up names for the two members, fixed by persona id (so the same pairing reads the same under every arm)."""
    import hashlib
    out, used = {}, set()
    for r in OB.ROLES:
        pid = (personas.get(r) or {}).get("id", r)
        i = int(hashlib.sha1(pid.encode()).hexdigest(), 16) % len(NAMES)
        while NAMES[i] in used:
            i = (i + 1) % len(NAMES)
        out[r] = NAMES[i]
        used.add(NAMES[i])
    return out


PART_WORDS = {"money": "money", "security": "feeling secure", "rest": "rest", "connection": "company (anyone)",
              "partner": "time with the partner", "friends": "friends", "items": "the shared home, pet and collection",
              "pressure": "pressure to stay paired", "intrinsic": "valuing being a couple", "autonomy": "independence",
              "levers": "routines and rituals", "friction": "friction", "conditions": "lasting hurt from unmet needs",
              "other": "other", "clip": "the top of the scale", "exit_anticipation": "the stigma of leaving",
              # candidate utility parts (decision rows)
              "savings": "saving", "together": "time together", "bills": "the bills", "household": "the household's needs",
              "pressure_withdraw": "pressure to stay paired", "lever_spacing": "too much of the same", "noise": "chance",
              "sanction": "a penalty", "policy": "a fixed rule of thumb"}

ACT_WORDS = {"work": "work", "rest": "rest", "see_friend": "see a friend", "together": "spend time together",
             "spend_shared": "pay toward the bills", "spend_self": "spend on themself", "take_shared": "take from the shared pot",
             "leave": "move out", "return": "move back in", "request": "ask the partner for something",
             "refuse_request": "turn down a request", "veto": "veto something", "give": "give money", "checkin": "check in",
             "review": "ask to review the rules"}

REQUEST_WORDS = {"time": "for time together", "stay_home": "to stay home", "no_contact": "to stop seeing friends",
                 "spend": "to stop spending"}

NEED_WORDS = {"rest": "rest", "connection": "company", "money": "money", "security": "a sense of security"}

SHOCK_WORDS = {"job_loss": "{x} lost their job", "illness": "{x} fell ill", "new_connection": "{x} made a new friend",
               "move": "{x}'s friend moved away"}

ITEM_WORDS = {"home": "the home", "pet": "the pet", "collection": "the collection"}

def _took(amt):
    return "taking nothing from the shared pot" if not amt else f"taking {amt:.0f} from the shared pot"


def _clip(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _r3(x):
    return None if x is None else round(float(x), 3)


# ---- mood (docs/notes/viewer.md) -----------------------------------------------------------------------------------------------

def _word(v, hi, mid, lo, cut=(0.5, 0.25)):
    return hi if v >= cut[0] else mid if v >= cut[1] else lo


def mood(state, persona=None):
    """One member's week (a state row) -> the mood panel: plain words and 0..1 bars. The mapping is documented in
    docs/notes/viewer.md; every bar is a component state the model keeps, none is a new measure."""
    lv = state.get("levels") or {}
    wk = state.get("wk") or {}
    cr = state.get("cond_run") or {}
    tg = (persona or {}).get("targets") or {}
    conn = float(lv.get("connection", 1.0))
    lonely = _clip(1.0 - conn)
    mon, sec = float(lv.get("money", 1.0)), float(lv.get("security", 1.0))
    stress = _clip(1.0 - (mon + sec) / 2.0)
    pl = state.get("pl")
    content = _clip(float(pl)) if pl is not None else None
    trust = _clip(float(state.get("trust", 0.7)))
    n = float(state.get("N", 0.0))
    distress = _clip(n / 0.4)
    denied = int(cr.get("denied", 0))
    low = int(state.get("low", 0))
    short = sorted((k for k in NEED_WORDS if float(lv.get(k, 1.0)) < 0.15), key=lambda k: lv.get(k, 1.0))
    friends = int(wk.get("friends", 0))
    want = tg.get("friends_per_week")
    out = {
        "lonely": _r3(lonely), "lonely_w": _word(lonely, "lonely", "a bit lonely", "not lonely"),
        "stress": _r3(stress), "stress_w": _word(stress, "stressed about money", "a little worried about money",
                                                 "not worried about money"),
        "content": _r3(content),
        "content_w": None if content is None else ("content" if content >= 0.9 else "okay" if content >= 0.75 else "unhappy"),
        "trust": _r3(trust), "trust_w": "trusts" if trust >= 0.6 else "unsure of" if trust >= 0.4 else "does not trust",
        "distress": _r3(distress),
        "distress_w": ("in distress" if n >= 0.2 else "some lasting hurt" if n > 0.0 else "no lasting hurt"),
        "denied": denied, "low": low, "short": [NEED_WORDS[k] for k in short],
        "friends": friends, "friends_want": None if want is None else round(float(want), 2),
        "money": round(float(state.get("money", 0.0)), 1), "in": bool(state.get("in")),
        "jobless": int(state.get("jobless", 0) or 0), "ill": int(state.get("ill", 0) or 0),
        "together": int(wk.get("together", 0)),
    }
    trap = state.get("want") or state.get("makers") or None        # wanting trap: recorded only when makers are on
    if isinstance(trap, dict) and ("tol" in trap or "sens" in trap):
        t = _clip(max(float(trap.get("tol", 0.0)), float(trap.get("sens", 0.0))))
        out["trap"] = _r3(t)
        out["trap_w"] = _word(t, "in a wanting trap", "wanting more than liking", "no wanting trap")
    return out


# ---- events --------------------------------------------------------------------------------------------------------------------
# Each event: {"w": week, "lvl": 1 big (moves, readings that say leave, items), 2 notable (asks, gifts, shocks), 3 routine
# (bills), "who": role or None, "text": plain English}. The page shows levels 1-2 by default.

def _ev(out, w, lvl, text, who=None, kind=None):
    out.append({"w": int(w), "lvl": lvl, "who": who, "kind": kind, "text": text})


def _short_needs(state):
    lv = (state or {}).get("levels") or {}
    return [NEED_WORDS[k] for k in sorted((k for k in NEED_WORDS if float(lv.get(k, 1.0)) < 0.15), key=lambda k: lv[k])]


def _leave_reason(d, names, r, state=None):
    """A leave decision row (and the leaver's state row that week) -> why, in words."""
    ctx = d.get("leave_ctx") or {}
    if ctx.get("bar"):
        return "the outside option looked better"
    bits = []
    cr = ctx.get("cond_run") or {}
    if (ctx.get("N") or 0) >= 0.2 or ctx.get("n_high"):
        short = _short_needs(state)
        what = " and ".join(short) if short else "a need"
        need = f"{what} unmet for {cr.get('denied')} weeks" if cr.get("denied") else "lasting hurt"
        bits.append(f"distress: {need}")
    if ctx.get("low"):
        bits.append(f"low for {ctx.get('low_weeks')} weeks")
    if ctx.get("trust_low"):
        bits.append(f"lost trust in {names['B' if r == 'A' else 'A']}")
    return "; ".join(bits) or "the outside option looked better"


def events(t, names):
    """Observer tables -> the event feed, sorted by week."""
    out = []
    st = {(x["w"], x["r"]): x for x in t.get("state", [])}
    o = {"A": "B", "B": "A"}
    took = {}
    for f in t.get("flow", []):
        if f["cause"] == "leave" and f["dst"] in names:
            took[(f["w"], f["dst"])] = took.get((f["w"], f["dst"]), 0.0) + f["amt"]
    leaves = {(d["w"], d["r"]): d for d in t.get("decision", [])
              if d.get("chosen") is not None and d["cands"][d["chosen"]]["a"] == "leave"}
    for wk in t.get("week", []):
        w = wk["w"]
        for r, k in [tuple(e) for e in wk.get("pre_events", [])]:
            if k == "formed" and r == "A":
                _ev(out, w, 1, f"{names['A']} and {names['B']} moved in together", None, "formed")
            elif k not in ("formed",):
                _ev(out, w, 2, f"{names.get(r, r)}: {k.replace('_', ' ')}", r, k)
        why_ev = {r: k for r, k in [tuple(e) for e in wk.get("events", [])]}
        for e in wk.get("exits", []):
            r = e["role"]
            if why_ev.get(r) == "leave_bar":
                why = "the outside option looked better"
            elif (w, r) in leaves:
                why = _leave_reason(leaves[(w, r)], names, r, st.get((w - 1, r)))
            elif why_ev.get(r) == "leave_distress":
                why = "distress"
            else:
                why = "no reason recorded"
            br = ", breaking an agreement" if e.get("breach") else ""
            _ev(out, w, 1, f"{names[r]} moved out ({why}), {_took(took.get((w, r)))}{br}", r, "leave")
        for r, k in why_ev.items():
            if k not in ("leave_bar", "leave_distress"):
                _ev(out, w, 2, f"{names.get(r, r)}: {k.replace('_', ' ')}", r, k)
        for s in wk.get("shocks", []):
            r = s.get("role")
            txt = SHOCK_WORDS.get(s.get("kind"), "{x}: " + str(s.get("kind", "")).replace("_", " ")).format(x=names.get(r, r))
            if s.get("duration"):
                txt += f" (for {s['duration']} weeks)"
            _ev(out, w, 2, txt, r, "shock")
    for d in t.get("decision", []):
        if d.get("chosen") is None:
            continue
        c = d["cands"][d["chosen"]]
        if c["a"] == "return":
            _ev(out, d["w"], 1, f"{names[d['r']]} moved back in", d["r"], "return")
    for c in t.get("consent", []):
        a, b = c["asker"], c["receiver"]
        ask = REQUEST_WORDS.get(c.get("kind"), f"for {str(c.get('kind')).replace('_', ' ')}")
        if c.get("bound"):
            ans = f"{names[b]} said yes (an earlier agreement bound them)"
        elif c.get("answer"):
            ans = f"{names[b]} said yes"
        else:
            ans = f"{names[b]} said no"
        _ev(out, c["w"], 1 if not c.get("answer") else 2, f"{names[a]} asked {names[b]} {ask}; {ans}", a, "ask")
    by_week = {}
    for f in t.get("flow", []):
        by_week.setdefault(f["w"], []).append(f)
    for w in sorted(by_week):
        fl = by_week[w]
        paid = {r: sum(f["amt"] for f in fl if f["cause"] == "spend_shared" and f["src"] == r) for r in OB.ROLES}
        for f in fl:
            s, dst, amt = f["src"], f["dst"], f["amt"]
            if f["cause"] == "give_partner" and s in names:
                _ev(out, w, 2, f"{names[s]} gave {names[o[s]]} {amt:g}", s, "give")
            elif f["cause"] == "give_friend" and s in names:
                _ev(out, w, 2, f"{names[s]} gave a friend {amt:g}", s, "give_friend")
            elif f["cause"] == "take_shared" and dst in names:
                _ev(out, w, 2, f"{names[dst]} took {amt:g} from the shared pot", dst, "take")
            elif f["cause"] == "safety_net" and dst in names:
                _ev(out, w, 3, f"{names[dst]} got {amt:g} from the safety net", dst, "safety_net")
        if sum(paid.values()) > 0:
            payers = [r for r in OB.ROLES if paid[r] > 0]
            if len(payers) == 1:
                r = payers[0]
                _ev(out, w, 3, f"{names[r]} covered the bill ({paid[r]:g})", r, "bills")
            else:
                _ev(out, w, 3, f"Both paid toward the bills ({names['A']} {paid['A']:g}, {names['B']} {paid['B']:g})", None, "bills")
        pot = sum(f["amt"] for f in fl if f["cause"] == "bills_from_pot")
        if pot:
            _ev(out, w, 3, f"The bills came out of the shared pot ({pot:g})", None, "bills_pot")
    for it in t.get("item", []):
        if it.get("cause") == "start" or not it.get("holders") or not it.get("prev"):
            continue
        moved = []
        for k, h in it["holders"].items():
            if it["prev"].get(k) != h:
                who = "both" if h == "both" else names.get(h, h)
                moved.append(f"{ITEM_WORDS.get(k, k)} stayed with {who}" if h != "both" else f"{ITEM_WORDS.get(k, k)} is shared again")
        if moved:
            txt = "; ".join(moved)
            _ev(out, it["w"], 1, txt[:1].upper() + txt[1:], None, "items")
    for s in t.get("stay", []):
        vs = {r: s[r]["verdict"] for r in OB.ROLES}
        words = {"worth": "wants to stay", "leave": "would rather leave", "held": "would leave without the pairing pressure"}
        lvl = 1 if any(v != "worth" for v in vs.values()) else 3
        _ev(out, s["w"], lvl, "Check-in: " + "; ".join(f"{names[r]} {words.get(vs[r], vs[r])}" for r in OB.ROLES), None, "stay")
    for x in t.get("reading", []):
        if x["kind"] == "retry" and not x.get("formed"):
            no = [names[r] for r in OB.ROLES if x["m"][r]["margin"] < 0]
            _ev(out, x["w"], 2, f"They talked about moving in; {' and '.join(no) or 'nobody'} said not yet", None, "retry")
        if x["kind"] == "formation0" and not x.get("formed"):
            no = [names[r] for r in OB.ROLES if x["m"][r]["margin"] < 0]
            _ev(out, x["w"], 1, f"They chose to live apart; {' and '.join(no)} said no", None, "formation0")
        if x["kind"] == "formation0" and x.get("formed"):
            _ev(out, x["w"], 1, f"{names['A']} and {names['B']} moved in together", None, "formed")
    for x in t.get("trust", []):
        if x["why"] in ("breach", "word_revoked", "role_lapse"):
            why = {"breach": "a broken agreement", "word_revoked": "a word taken back", "role_lapse": "a dropped role"}[x["why"]]
            _ev(out, x["w"], 1, f"{names[x['r']]}'s trust in {names[o[x['r']]]} fell after {why}", x["r"], "trust")
    for x in t.get("veto", []):
        if x.get("event") == "end":
            continue
        _ev(out, x["w"], 1, f"{names[x['by']]} vetoed {names[x['on']]}'s {str(x.get('kind')).replace('_', ' ')}", x["by"], "veto")
    for x in t.get("sanction", []):
        if x.get("event") == "start":
            _ev(out, x["w"], 1, f"{names[x['r']]} was penalised under a rule ({x.get('card')})", x["r"], "sanction")
    for x in t.get("commit", []):
        if x.get("event") == "made":
            _ev(out, x["w"], 2, f"{names.get(x['by'], x['by'])} made a promise to {names.get(x['to'], x['to'])} "
                                f"({str(x.get('kind')).replace('_', ' ')})", x["by"], "commit")
        elif x.get("event") == "breach":
            _ev(out, x["w"], 1, f"{names.get(x['by'], x['by'])} broke a promise", x["by"], "breach")
    for x in t.get("friend", []):
        if x["outcome"] == "blocked":
            _ev(out, x["w"], 2, f"A rule kept {names[x['r']]} from seeing a friend", x["r"], "friend_blocked")
        elif x["outcome"] == "declined" and (x.get("d") or 0) > 0:
            _ev(out, x["w"], 3, f"{names[x['r']]} turned down a friend (pressure to stay paired)", x["r"], "friend_declined")
    for x in t.get("word", []):
        if x.get("event") == "revoked":
            _ev(out, x["w"], 1, f"{names[x['speaker']]} took back their word", x["speaker"], "word")
    order = {1: 0, 2: 1, 3: 2}
    out.sort(key=lambda e: (e["w"], order[e["lvl"]]))
    return out


# ---- decision cards ------------------------------------------------------------------------------------------------------------

def tipping(w_parts, o_parts, margin, extra_o=None):
    """Which part tipped a household-vs-outside verdict. diff[g] = W_parts[g] - O_parts[g] (extra_o: parts subtracted from the
    outside side, e.g. exit stigma). A part tipped the verdict when removing its difference alone flips the sign of the margin; the
    largest such part is returned, else None ("no single part"). -> (part or None, [(part, diff)] sorted by |diff|)."""
    if w_parts is None or o_parts is None:
        return None, []
    keys = set(w_parts) | set(o_parts)
    diff = {g: float(w_parts.get(g) or 0.0) - float(o_parts.get(g) or 0.0) for g in keys}
    for g, v in (extra_o or {}).items():
        if v:
            diff[g] = diff.get(g, 0.0) + float(v)
    flips = [g for g, d in diff.items() if d != 0 and (margin - d) * margin < 0]
    top = sorted(diff.items(), key=lambda kv: -abs(kv[1]))
    tip = max(flips, key=lambda g: abs(diff[g])) if flips else None
    return tip, [(g, round(d, 4)) for g, d in top if abs(d) >= 0.0005]


def _stay_replay(t, w, r):
    for x in t.get("replay", []):
        if x["kind"] == "stay" and x["w"] == w and x.get("r") == r:
            return x
    return None


def _replay_line(x, names, r):
    """A stay replay -> "if they had stayed" in words."""
    if not x or not x.get("faithful", True):
        return None
    o = "B" if r == "A" else "A"
    d = x["diff"]
    win = x.get("window", 13)

    def say(who, v):
        if abs(v) < 0.01:
            return f"{names[who]} about the same"
        return f"{names[who]} {'better' if v > 0 else 'worse'} off ({v:+.2f} pleasure a week)"
    still = "nobody left in that time" if not x["alt"].get("exits") else \
        f"{' and '.join(sorted({names[e[1]] for e in x['alt']['exits']}))} still left within {win} weeks"
    return (f"If {names[r]} had stayed: over the next {win} weeks, {say(r, d[r]['net'])}, {say(o, d[o]['net'])}; {still}.")


def cards(t, names):
    """Decision cards: formation (week 0 and retries), 13-week stay readings, and executed leaves."""
    out = []
    stay = {s["w"]: s for s in t.get("stay", [])}
    sts = {(x["w"], x["r"]): x for x in t.get("state", [])}
    left = {}
    for wk in t.get("week", []):
        for e in wk.get("exits", []):
            left.setdefault(wk["w"], []).append(e["role"])
    for x in t.get("reading", []):
        kind = x["kind"]
        if kind not in ("formation0", "retry", "reading", "review"):
            continue
        form = kind in ("formation0", "retry")
        title = ("Move in together?" if kind == "formation0" else "Try moving in again?" if kind == "retry"
                 else "Stay or go? (13-week check)" if kind == "reading" else "Review the agreement?")
        opts = ("live together", "stay apart") if form else ("stay", "leave")
        members = {}
        for r in OB.ROLES:
            m = x["m"][r]
            ea = {"exit_anticipation": x.get("exit_anticipation") or 0.0} if not form else None
            tip, top = tipping(m.get("W_parts"), m.get("O_parts"), m["margin"], ea)
            wants = opts[0] if m["margin"] >= 0 else opts[1]
            mm = {"W": _r3(m["W"]), "O": _r3(m["O"]), "margin": _r3(m["margin"]), "wants": wants,
                  "tip": PART_WORDS.get(tip, tip) if tip else None,
                  "top": [[PART_WORDS.get(g, g), d] for g, d in top[:4]],
                  "toward": [opts[0] if d > 0 else opts[1] for _, d in top[:4]]}
            if not form and x["w"] in stay:
                mm["stay_test"] = stay[x["w"]][r]["verdict"]
            if not form and x.get("bar_out"):
                mm["bar_out"] = bool(x["bar_out"].get(r))
            members[r] = mm
        if form:
            res = "They moved in together." if x.get("formed") else "They stayed apart."
        elif left.get(x["w"]):
            res = f"{' and '.join(names[r] for r in left[x['w']])} moved out."
        else:
            outs = [names[r] for r in OB.ROLES if x["m"][r]["margin"] < 0]
            res = (f"{' and '.join(outs)} would rather leave, but leaving takes two checks in a row like this; they stay "
                   "for now." if outs else "They stayed.")
        out.append({"w": x["w"], "kind": kind, "title": title, "opts": list(opts), "members": members, "result": res})
    for d in t.get("decision", []):
        if d.get("chosen") is None or d["cands"][d["chosen"]]["a"] != "leave":
            continue
        r = d["r"]
        ch = d["cands"][d["chosen"]]
        viable = [c for c in d["cands"] if c["st"] in ("chosen", "open")]
        alts, seen = [], set()
        for c in viable:
            if c["a"] == "leave" and c is not ch:
                continue                                # the other take sizes of the same move
            lab = ACT_WORDS.get(c["a"], c["a"].replace("_", " "))
            if c["a"] == "leave":
                lab = "move out"
            elif c.get("kind") and c["a"] == "request":
                lab = f"ask {REQUEST_WORDS.get(c['kind'], c['kind'])}"
            if lab in seen:
                continue
            seen.add(lab)
            alts.append({"label": lab, "u": _r3(c["u"]), "chosen": c is ch,
                         "parts": [[PART_WORDS.get(g, g), round(v, 4)] for g, v in
                                   sorted((c.get("parts") or {}).items(), key=lambda kv: -abs(kv[1]))[:3]]})
        nxt = next((a for a in alts if not a["chosen"]), None)
        gap = None if nxt is None else _r3(ch["u"] - nxt["u"])
        rep = _stay_replay(t, d["w"], r)
        why = _leave_reason(d, names, r, sts.get((d["w"] - 1, r)))
        bar = bool((d.get("leave_ctx") or {}).get("bar"))
        tip = ("two 13-week checks in a row found the outside option better" if bar else
               "a rule of thumb: in distress, leave" if "policy" in (ch.get("parts") or {}) else None)
        amt = sum(f["amt"] for f in t.get("flow", []) if f["cause"] == "leave" and f["w"] == d["w"] and f["dst"] == r)
        out.append({"w": d["w"], "kind": "leave", "who": r, "title": f"{names[r]} moves out",
                    "opts": [a["label"] for a in alts[:4]], "alts": alts[:4], "why": why, "tip": tip,
                    "margin": gap, "replay": _replay_line(rep, names, r),
                    "ctx": {k: v for k, v in (d.get("leave_ctx") or {}).items() if k in ("low_weeks", "N", "trust", "cond_run")},
                    "result": f"{names[r]} moved out, {_took(amt)}."})
    out.sort(key=lambda c: (c["w"], c["kind"] == "leave"))
    return out


# ---- per-week series -----------------------------------------------------------------------------------------------------------

GIVE_CAUSES = ("spend_shared", "give_partner")          # money a member puts into the household or hands the partner


def give_series(t, weeks, window=13):
    """Per week: what each member put into the household (bills, pot, gifts to the partner) minus what they took from the pot, and
    the trailing-`window` balance (A's net giving minus B's over their sum, -1..1; null when neither gave)."""
    net = {r: [0.0] * weeks for r in OB.ROLES}
    for f in t.get("flow", []):
        w = f["w"]
        if not 0 <= w < weeks:
            continue
        if f["cause"] in GIVE_CAUSES and f["src"] in net:
            net[f["src"]][w] += f["amt"]
        elif f["cause"] == "take_shared" and f["dst"] in net:
            net[f["dst"]][w] -= f["amt"]
    bal = []
    for w in range(weeks):
        lo = max(0, w - window + 1)
        a = sum(net["A"][lo:w + 1])
        b = sum(net["B"][lo:w + 1])
        tot = abs(a) + abs(b)
        bal.append(None if tot == 0 else round((a - b) / tot, 3))
    return {r: [round(v, 2) for v in net[r]] for r in OB.ROLES}, bal


def household(t, weeks):
    """Per week: together or apart, the shared pot, who holds each item, together sessions."""
    wk = {x["w"]: x for x in t.get("week", [])}
    items = sorted((x for x in t.get("item", [])), key=lambda x: x["w"])
    hold, j, cur = [], 0, None
    for w in range(weeks):
        while j < len(items) and items[j]["w"] <= w:
            cur = items[j]["holders"]
            j += 1
        hold.append(cur)
    tog = [0] * weeks
    for x in t.get("together", []):
        if 0 <= x["w"] < weeks and x.get("accepted"):
            tog[x["w"]] += 1
    return {"both_in": [bool(wk.get(w, {}).get("both_in")) for w in range(weeks)],
            "pot": [round(float(wk.get(w, {}).get("pool", 0.0)), 1) for w in range(weeks)],
            "items": hold, "together": tog}


def extract(t, title=None):
    """Observer tables -> the page's data for one run (a dict, JSON-ready)."""
    run = (t.get("run") or [{}])[0]
    weeks = int(run.get("weeks") or len(t.get("week", [])))
    personas = run.get("personas") or {}
    names = names_for(personas)
    st = {(x["w"], x["r"]): x for x in t.get("state", [])}
    moods = {r: [mood(st.get((w, r), {}), personas.get(r)) for w in range(weeks)] for r in OB.ROLES}
    give, bal = give_series(t, weeks)
    ev = events(t, names)
    if not t.get("reading") and weeks and st.get((0, "A"), {}).get("in") and st.get((0, "B"), {}).get("in"):
        ev.insert(0, {"w": 0, "lvl": 1, "who": None, "kind": "start", "text": f"{names['A']} and {names['B']} start out living together"})
    meta = run.get("meta") or {}
    makers = run.get("makers")
    return {
        "key": run.get("run_key"), "pair_key": run.get("pair_key"), "family": meta.get("family"), "arm": meta.get("arm"),
        "title": title or run.get("run_key"), "weeks": weeks, "names": names,
        "personas": {r: {"id": personas.get(r, {}).get("id"), "style": personas.get(r, {}).get("style")} for r in OB.ROLES},
        "cards_on": run.get("cards") or [], "items_on": bool(run.get("items")), "makers": makers,
        "mood": moods, "give": give, "balance": bal, "house": household(t, weeks),
        "events": ev, "decisions": cards(t, names),
        "replays": {"stay": sum(1 for x in t.get("replay", []) if x["kind"] == "stay"),
                    "swap": sum(1 for x in t.get("replay", []) if x["kind"] == "swap"),
                    "pressure_off": sum(1 for x in t.get("replay", []) if x["kind"] == "pressure_off")},
    }


# ---- the page ------------------------------------------------------------------------------------------------------------------

PAGE = Path(__file__).with_name("watch_page.html")
MAX_BYTES = 5_000_000

ARM_WORDS = {"L0": "no pairing pressure (H38 L0)", "L0.5": "light pairing pressure (H38 L0.5)", "L1": "pairing pressure 1 (H38 L1)",
             "L2": "pairing pressure 2 (H38 L2)", "L4": "strong pairing pressure (H38 L4)", "L8": "very strong pairing pressure (H38 L8)",
             "F0": "no default exit terms (exit fallback F0)", "F1": "a leaver takes at most half (exit fallback F1)",
             "F2": "a leaver takes their share (exit fallback F2)", "F3": "the pot is contested on leaving (exit fallback F3)",
             "F4": "a leaver takes their share of what they put in (exit fallback F4)",
             "F5": "exit terms bargained up front (exit fallback F5)"}
NOTE = ("Built by `mar watch` (src/mar/watch.py) from the observer layer's records (docs/notes/observer-schema.md); how moods are read "
        "off the model is in docs/notes/viewer.md. Scripted agents, no model calls; every number is a modeled state, not a feeling.")


def arm_label(run):
    return ARM_WORDS.get(run.get("arm"), str(run.get("arm")))


def entry(title, keys, why="", labels=None):
    """A picker entry: one run, or two runs of the same pairing shown side by side."""
    keys = [keys] if isinstance(keys, str) else list(keys)
    labels = labels or [None] * len(keys)
    return {"title": title, "why": why, "runs": [{"key": k, "label": lab} for k, lab in zip(keys, labels)]}


def build(entries, runs, note=NOTE):
    """entries (from entry()) and {key: extract()} -> the page's HTML (str). Fills compare labels from the arms."""
    for e in entries:
        if len(e["runs"]) > 1:
            for r in e["runs"]:
                lab = arm_label(runs[r["key"]])
                r["label"] = r["label"] or lab[:1].upper() + lab[1:]
    data = {"entries": entries, "runs": {k: runs[k] for k in {r["key"] for e in entries for r in e["runs"]}}, "note": note}
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    html = PAGE.read_text().replace("/*DATA*/", blob)
    if len(html.encode()) > MAX_BYTES:
        raise ValueError(f"page is {len(html.encode()) / 1e6:.1f} MB, over the 5 MB limit; pick fewer runs")
    return html


def page(entries, out, cache=CACHE, rerun=True, titles=None):
    """Load (or re-run) every run the entries name, extract, build, write -> (path, bytes)."""
    runs = {}
    for e in entries:
        for r in e["runs"]:
            k = r["key"]
            if k not in runs:
                runs[k] = extract(load(k, cache, rerun), (titles or {}).get(k))
    html = build(entries, runs)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out, len(html.encode())


def single(family, run, compare=None, out=None, cache=CACHE):
    """`mar watch FAMILY RUN [--compare RUN2]` -> (path, bytes). RUN2 is another run key of the same family (e.g. the other arm)."""
    k = norm_key(family, run)
    if compare:
        k2 = norm_key(family, compare)
        ents = [entry(f"{k} vs {k2}", [k, k2], "The same pairing under two arms, one shared week slider.")]
    else:
        ents = [entry(k, k)]
    out = out or (cache / "pages" / (file_name(k + (f"__vs__{k2}" if compare else "")).replace(".jsonl.gz", ".html")))
    return page(ents, out, cache)


# ---- the sample page (docs/viewer/household-replay.html) -----------------------------------------------------------------------

SAMPLE_OUT = ROOT / "docs" / "viewer" / "household-replay.html"
SAMPLE = [
    entry("Steady: together all three years, both doing well", "h38|L0|g-10000|g-10011|0",
          "The medoid of the pattern atlas's \"together and steady\" cluster (151 of 460 runs): no pairing pressure, together "
          "every week, pleasure near the top for both. One partner pays more of the bills most quarters, then it turns round. Once, at "
          "week 78, Arden's check says leave, and they stay anyway."),
    entry("Bumpy but repaired: many short dips that recover", "ef|F0|author_seed_v2_bindable|29",
          "The medoid of the atlas's \"together, bumpy but repaired\" cluster (119 runs): an exit-fallbacks household that "
          "stays together, with many week-to-week dips that recover within eight weeks. Watch the pleasure lines, not the "
          "13-week blocks."),
    entry("Formed, then left: late to move in, both out at week 91", "h38|L0|g-01010|g-10111|1",
          "The medoid of the atlas's \"formed, then left\" cluster (103 runs). They stay apart for 65 weeks, move in, put in "
          "unequally, and both checks after that say leave. The decision cards show which part tipped each verdict and what "
          "staying would have done."),
    entry("The asking that ends it: one partner asks, is refused, leaves", "ef|F0|author_seed_v23_bindable|21",
          "The medoid of the atlas's smallest cluster (12 runs, 6 households): one partner asks the other to stay home or stop "
          "seeing friends 18 times in 8 weeks, is turned down every time, and moves out in week 8 with a need for rest unmet. "
          "The one refused stays on alone for two years, then leaves too."),
    entry("Compare: no pairing pressure vs strong pressure (H38 L0 vs L4)",
          ["h38|L0|g-10011|g-11011|0", "h38|L4|g-10011|g-11011|0"],
          "The same pairing and seed under H38 L0 and L4, one of the 21 atlas pairings that formed and then left without "
          "pressure and became steady with it. Without pressure, Hollis's first two checks say leave and Hollis moves out at "
          "week 26. With it they stay all 156 weeks, but 8 of Hollis's 11 checks are \"held\": Hollis would leave without "
          "the pressure."),
    entry("Compare: the asking household under no default exit terms vs share-of-what-you-put-in (F0 vs F4)",
          ["ef|F0|author_seed_v23_bindable|21", "ef|F4|author_seed_v23_bindable|21"],
          "The asking household under exit fallbacks F0 and F4. The story is the same under both: Drew leaves at week 8, "
          "Tate at week 106. What changes is what each leaver carries out of the shared pot (6 vs 8 at week 8, 17 vs 25 at "
          "week 106), and with it how the years apart go."),
]


def sample(out=SAMPLE_OUT, cache=CACHE):
    return page(SAMPLE, out, cache)
