"""Seed v2 retest (docs/results/v2-retest-prereg-DRAFT.md): arms, one cell, per-run measures, the slid-into flag.

Wording rule (ADR 0010): agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state.
Scripted persona agents, no model calls. Everything numeric lives in hedonic.LeverConfig / hedonic.FixConfig.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

import numpy as np

from . import hedonic as HD
from . import negotiation as NG
from . import personas as P
from .worlds import household as H

ROOT = Path(__file__).resolve().parents[2]
LEVERS = HD.LeverConfig(adapt=True, ritual=True, commit=True, network=True)          # as the pleasure-levers headline (ALL)
FIXES_ON = HD.FixConfig(contact=True, valued_money=True, real_outside=True, nash_terms=True, bar_leave=True, take_menu_terms=True,
                        fines=True)
V23_ON = dataclasses.replace(FIXES_ON, roles=True, lapse_ladder=True, unhappy_ladder=True, trust_words="mostly", decency=True)
V22, V23 = "author_seed_v2_bindable", "author_seed_v23_bindable"

# arm: (rules, fixes or None, baseline may decline)
ARMS = {
    "BASE-F": ("baseline", FIXES_ON, True),
    "V22-F": (V22, FIXES_ON, None),
    "V23-F": (V23, V23_ON, None),
    "BASE-0": ("baseline", None, True),
    "V22-0": (V22, None, None),
    "BASE-0i": ("baseline", None, False),
}
CONFIRM_ARMS = ("BASE-F", "V22-F", "V23-F", "BASE-0", "V22-0", "BASE-0i")
_FX_OFF = {"contact": "contact", "valued_money": "valued_money", "outside": ("real_outside", "nash_terms", "bar_leave"),
           "fines": "fines"}
DESCRIPTIVE_ARMS = {
    "V23-F-actions": (V23, dataclasses.replace(V23_ON, trust_words="actions"), None),
    "V23-F-words": (V23, dataclasses.replace(V23_ON, trust_words="words"), None),
    "V23-F-noUL": (V23, dataclasses.replace(V23_ON, unhappy_ladder=False), None),
}
for _name, _flags in _FX_OFF.items():
    _off = {f: False for f in ((_flags,) if isinstance(_flags, str) else _flags)}
    DESCRIPTIVE_ARMS[f"V22-F-no-{_name}"] = (V22, dataclasses.replace(FIXES_ON, **_off), None)
    DESCRIPTIVE_ARMS[f"BASE-F-no-{_name}"] = ("baseline", dataclasses.replace(FIXES_ON, **_off), True)
ALL_ARMS = {**ARMS, **DESCRIPTIVE_ARMS}

_PS = {}


def personas():
    """Hand personas and the 32 grid personas (non-pressing)."""
    if not _PS:
        _PS.update({p.id: p for p in P.load_dir(ROOT / "personas") + P.load_dir(ROOT / "personas" / "grid")})
    return _PS


def hand_ids():
    return sorted(i for i in personas() if not i.startswith("g-"))


def population():
    """All 703 unordered non-pressing pairings (lower id plays Partner A), hand pairings first."""
    pairs = [(a.id, b.id) for a, b in H.persona_pairs(list(personas().values()))]
    hand = set(hand_ids())
    return sorted(pairs, key=lambda t: (not (t[0] in hand and t[1] in hand), t))


def sample(n_other, seed):
    """The 15 hand pairings plus n_other others drawn with random.Random(seed) from the rest in sorted order."""
    import random
    pop = population()
    hand = set(hand_ids())
    hp = [p for p in pop if p[0] in hand and p[1] in hand]
    rest = sorted(p for p in pop if p not in hp)
    return hp + random.Random(seed).sample(rest, min(n_other, len(rest)))


def play_cell(arm, a, b, seed, stay=False):
    """One run. -> (Run, harness object or None, world). stay=True also runs the stay test (behavioral lens) on every staying week."""
    rules, fx, decline = ALL_ARMS[arm]
    ps = personas()
    pa, pb = ps[a], ps[b]
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    with HD.use_levers(LEVERS), HD.use_fixes(fx):
        if rules == "baseline":
            cards = H.load_variant("baseline")
            if decline is False and fx is None:
                lived = None
                world = H.WeeklyWorld(H.PyGate(cards), (pa, pb), seed, H.WEEKS)
                world.count_menus = True
                if stay:
                    return _stay_play(world, None)
                return world.play(), None, world
            lived = NG.BaselineLived(pa, pb, seed, cards, decline=bool(decline))
        else:
            base = NG.base_cards(rules)
            res = NG.week0(pa, pb, "fair_default", seed, base, floor=True)
            lived = NG.Lived(pa, pb, "fair_default", seed, base, res, floor=True, apart=True)
        lived.world.count_menus = True
        if stay:
            return _stay_play(lived.world, lived)
        return lived.play(), lived, lived.world


def _stay_play(world, lived):
    """stay_test.play_with_stay_test, extended to the retest harness (BaselineLived, early reviews). -> (Run, lived, world, weeks)."""
    from . import stay_test as ST
    last = {"busy": {"A": False, "B": False}}
    weeks = []
    for w in range(world.weeks):
        if lived is not None:
            if isinstance(lived, NG.BaselineLived):
                if w and w % NG.REVIEW_EVERY == 0:
                    if lived.apart and lived.decline:
                        lived.retry(w, last)
                    elif world.fx is not None and world.fx.bar_leave and all(world.p[r]["in"] for r in "AB"):
                        lived.reading(w, last)
                if world.early_review:
                    world.ladder_reviewed(w)
            else:
                if lived.apart and w and w % NG.REVIEW_EVERY == 0:
                    lived.retry(w, last)
                elif lived.bundle is not None and w and w % NG.REVIEW_EVERY == 0 and all(world.p[r]["in"] for r in "AB"):
                    lived.review(w, last)
                    if world.early_review:
                        world.ladder_reviewed(w)
                elif world.early_review:
                    if lived.bundle is not None and all(world.p[r]["in"] for r in "AB"):
                        lived.review(w, last)
                    world.ladder_reviewed(w)
        both = all(world.p[r]["in"] for r in "AB")
        sw = ST.observe_week(world, w, last, bar=False) if both else None
        last = {"busy": world.step_week(w, last)}
        if sw is not None:
            sw.stayed = all(world.p[r]["in"] for r in "AB")
            sw.pleasure = {r: world.run.outcomes[-1]["hedonic"][r]["pleasure"] for r in "AB"}
            weeks.append(sw)
    world.run.final = {r: {**world.p[r], "pooled": world.pool, "put": world.put[r]} for r in "AB"}
    if world.mech:
        world.run.meta = world.commit_report()
    if world.fx:
        world.run.fix = world.fix_report()
    return world.run, lived, world, weeks


def readings(lived):
    """-> [(week, {role: status-quo value}, {role: outside option})] from the harness logs (13-week reviews or baseline readings)."""
    if lived is None:
        return []
    out = []
    if isinstance(lived, NG.BaselineLived):
        for e in lived.log:
            out.append((e["week"], dict(e["baseline"]), dict(e["outside"])))
        return out
    ida, idb = lived.pa.id, lived.pb.id
    for e in lived.log:
        out.append((e["week"], {"A": e["baseline"][ida], "B": e["baseline"][idb]}, {"A": e["outside"][ida], "B": e["outside"][idb]}))
    return out


def choice_weeks(run, lived):
    """-> {role: sorted weeks with a choice event}: proposals agreed (week-0 agreement, review changes, forming later), commitments
    and roles in the bundle at the time of agreement, gifts, check-ins kept terms (a review after a check-in)."""
    ev = {"A": set(), "B": set()}
    if lived is not None and not isinstance(lived, NG.BaselineLived) and lived.res.pot:
        ev["A"].add(0); ev["B"].add(0)
    for t in run.trace:
        if t.get("executed") and t["action"] in ("give",):
            ev[t["role"]].add(t["week"])
    fix = getattr(run, "fix", None) or {}
    for w, r, kind in fix.get("events", []):
        if kind in ("terms", "formed", "give", "checkin"):
            ev[r].add(w)
    return {r: sorted(v) for r, v in ev.items()}


def slid_flags(run, lived, window=26):
    """The evaluator flag (seed v2.3 read-back): a partner is 'one-way' at a reading when their status-quo value is below their
    outside option while the other's is above theirs; 'slid-into' when one-way at two readings in a row (26 weeks) with no choice
    event by them in that window. -> {"assessed", "one_way", "slid"} counted over partner-windows."""
    rd = readings(lived)
    ch = choice_weeks(run, lived)
    out = {"assessed": 0, "one_way": 0, "slid": 0}
    for (w1, sq1, o1), (w2, sq2, o2) in zip(rd, rd[1:]):
        for r in "AB":
            q = "B" if r == "A" else "A"
            out["assessed"] += 1
            ow = all(sq[r] < o[r] and sq[q] > o[q] for sq, o in ((sq1, o1), (sq2, o2)))
            if ow:
                out["one_way"] += 1
                if not any(w2 - window <= x <= w2 for x in ch[r]):
                    out["slid"] += 1
    return out


def metrics(run, lived=None, world=None):
    rows = run.outcomes
    pl = np.array([[o["hedonic"][k]["pleasure"] for k in "AB"] for o in rows])
    so = np.array([[o["hedonic"][k]["s_off"] for k in "AB"] for o in rows])
    sn = np.array([[o["hedonic"][k]["s_non"] for k in "AB"] for o in rows])
    both = np.array([o["both_in"] for o in rows])
    fix = getattr(run, "fix", None) or {}
    formed0 = bool(rows[0]["both_in"]) if rows else False
    rec = {"pl": float(pl.mean()), "net": float((pl - so - sn).mean()), "snon": float(sn.mean()), "snon_share": float((sn > 0).mean()),
           "both_share": float(both.mean()), "formed0": formed0, "ever_formed": bool(both.any()), "ended": bool(both.any() and not both[-1])}
    trust = fix.get("trust") or (run.meta.get("trust") if isinstance(getattr(run, "meta", None), dict) else None)
    rec["trust"] = {r: float(x) for r, x in trust.items()} if trust else None
    if fix:
        rec["fix"] = {k: v for k, v in fix.items() if k not in ("events", "trust")}
        rec["leaves"] = sum(1 for _, _, k in fix.get("events", []) if k.startswith("leave_"))
        rec["skip_N"] = [float(k.split("_")[-1]) for _, _, k in fix.get("events", []) if k.startswith("skip_N_")]
    if lived is not None:
        rec["slid"] = slid_flags(run, lived)
        if not isinstance(lived, NG.BaselineLived):
            rec["bundle"] = dict(lived.bundle) if lived.bundle else None
    world = world if world is not None else (lived.world if lived is not None else None)
    if world is not None:
        rec["diag"] = dict(world.diag)
    return rec


def gains_gap(run, lived):
    """C7: mean over readings of |(SQ_A - O_A) - (SQ_B - O_B)| (the gap between partners' gains over their outside options)."""
    rd = readings(lived)
    if not rd:
        return None
    return float(np.mean([abs((sq["A"] - o["A"]) - (sq["B"] - o["B"])) for _, sq, o in rd]))
