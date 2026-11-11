"""Stay test (ADR 0018 test 2, "worth it vs hard to leave"; docs/results/stay-test-prereg.md).

  uv run python scripts/stay_test_run.py --pilot             EXPLORATORY pilot (seeds 900, 901): spreads for the power check
  uv run python scripts/stay_test_run.py --run [--seeds N]   the confirmatory run (seeds 0..N-1), writes runs/stay-test/results.json.gz
  uv run python scripts/stay_test_run.py --analyze           prereg vs actual; writes runs/stay-test/analysis.json and the kept report

Arms (57 pairings each, the pleasure demonstration's grid):
  v22_bindable      seed v2.2 bindable (the author's confirmed seed), negotiation v2.1 protocol (fair default start, exit floor,
                    a failed negotiation means living apart, reviews and retries every 13 weeks)
  v22_free_exit     seed v2.2 free-exit variant, same protocol
  v22_locked        STRONGER EXIT COST: bindable negotiation at week 0, then a mutual stay commitment for the whole run with the full
                    breach forfeit imposed on top, terms frozen (no reviews; partners living apart may still form a pot, then locked)
  v22_locked_hard   v22_locked plus a breach load of 0.5 instead of 0.2 (ASSUMED): a bound partner breaks the commitment only at a
                    non-offsettable load of 0.5
  trap              imposed household fixture (T1 forfeit wall, contact and stay-home vetoes, no refusal); no negotiation
  baseline          imposed household fixture with an even exit split and no wall on leaving (exit-cost control); no negotiation
The author's seed files are read, never written. The locked arms change the deal and the breach load in this script only.
No model calls. Wording rule: agents feel nothing; pleasure is a gloss on a modeled hedonic state.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from itertools import permutations
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import negotiation as NG  # noqa: E402
from mar import personas as P  # noqa: E402
from mar import stay_test as ST  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "stay-test"
PRESSING = ("p-controller", "p-freerider", "p-overasker")
V22 = {"v22_bindable": "author_seed_v2_bindable", "v22_free_exit": "author_seed_v2_free_exit"}
LOCKED = ("v22_locked", "v22_locked_hard")
IMPOSED = ("trap", "baseline")
ARMS = tuple(V22) + LOCKED + IMPOSED
PILOT_SEEDS = (900, 901)
HARD_BREACH_N = 0.5        # ASSUMED, v22_locked_hard only

_PS = {}


def personas():
    if not _PS:
        _PS.update({p.id: p for p in P.load_dir(ROOT / "personas") + P.load_dir(ROOT / "personas" / "pressing")})
    return _PS


def pairings():
    ps = personas()
    hand = [p for i, p in ps.items() if i not in PRESSING]
    out = [(a.id, b.id, "ctl") for a, b in H.persona_pairs(hand)]
    out += [(a, b, "prs") for a, b in permutations(sorted(ps), 2) if a in PRESSING or b in PRESSING]
    return out


# ---- the stronger-exit-cost arms ---------------------------------------------------------------------------------------------

class HardBreachWorld(H.WeeklyWorld):
    """The household world with a higher breach load (a bound partner breaks a stay commitment only at N >= breach_n)."""
    breach_n = HARD_BREACH_N

    def breaks(self, r):
        return self.hed[r].N >= self.breach_n


def lock(L, w):
    """Impose a mutual stay commitment from week w to the end of the run, with the full breach forfeit, on a Lived household."""
    world = L.world
    L.bundle = dict(L.bundle, stay=world.weeks, breach=1.0)
    world.breach_forfeit = 1.0
    world.commits = [c for c in world.commits if c["kind"] != "stay"]
    for who, to in (("A", "B"), ("B", "A")):
        world.commits.append({"kind": "stay", "by": who, "to": to, "type": None, "from": w, "until": world.weeks + 1, "breached": 0})
    world.mech = True


class LockedLived(NG.Lived):
    """Terms frozen after week 0 (no reviews); a pot formed later by a retry is locked when it forms."""

    def review(self, w, last):
        return None

    def retry(self, w, last):
        super().retry(w, last)
        if not self.apart:
            lock(self, w)


# ---- one run -----------------------------------------------------------------------------------------------------------------

def run_task(args):
    arm, a, b, seed, cohort = args
    NG._RC.clear()
    NG._PC.clear()
    ps = personas()
    t0 = time.time()
    meta = {"arm": arm, "a": a, "b": b, "seed": seed, "cohort": cohort}
    if arm in IMPOSED:
        world = H.WeeklyWorld(H.PyGate(H.load_variant(arm)), (ps[a], ps[b]), seed, H.WEEKS)
        run, weeks = ST.play_with_stay_test(world)
        kind, bundle = "imposed", None
    else:
        base = NG.base_cards(V22.get(arm, "author_seed_v2_bindable"))
        res = NG.week0(ps[a], ps[b], "fair_default", seed, base, floor=True)
        cls = LockedLived if arm in LOCKED else NG.Lived
        L = cls(ps[a], ps[b], "fair_default", seed, base, res, floor=True, apart=True)
        if arm == "v22_locked_hard":
            L.world.__class__ = HardBreachWorld
        if arm in LOCKED and res.pot:
            lock(L, 0)
        world = L.world
        run, weeks = ST.play_with_stay_test(world, lived=L)
        kind, bundle = ("agreed" if res.pot else "apart"), (L.bundle if L.bundle else None)
    rec = compact(weeks)
    rec.update(meta, kind=kind, bundle=bundle, exits=len(world.exit_log), secs=round(time.time() - t0, 2),
               breaches=sum(1 for c in world.commits if c["kind"] == "stay" and c["breached"]))
    return rec


def compact(weeks):
    """A run's StayWeek list -> JSON-able per-run record (pleasure and held flags over staying weeks, causes where held)."""
    st = [s for s in weeks if s.stayed]
    rec = {"staying_weeks": len(st), "exit_weeks": len([s for s in weeks if not s.stayed]),
           "week": [s.week for s in st],
           "p": {r: [s.pleasure[r] for s in st] for r in "AB"},
           "held": {r: [int(bool(s.held[r])) for s in st] for r in "AB"},
           "causes": {r: {str(i): ST.cause_label(s.causes.get(r)) for i, s in enumerate(st) if s.held[r]} for r in "AB"},
           "bar": [{"week": s.week, "pair": ST.pair_bar_verdict(s.bar), **{r: s.bar[r] for r in "AB"}} for s in weeks if s.bar is not None]}
    return rec


def run_all(seeds, prs, arms=ARMS, workers=8, tag=""):
    tasks = [(arm, a, b, sd, c) for sd in seeds for a, b, c in prs for arm in arms]
    t0, rows = time.time(), []
    with Pool(workers) as pool:
        for i, r in enumerate(pool.imap_unordered(run_task, tasks, chunksize=2), 1):
            rows.append(r)
            if i % 100 == 0:
                print(f"  {tag} {i}/{len(tasks)} {time.time() - t0:.0f}s", flush=True)
    print(f"{tag} {len(rows)} runs in {time.time() - t0:.0f}s")
    return rows


def save(rows, name):
    OUT.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT / name, "wt") as f:
        json.dump(rows, f)


def load(name="results.json.gz"):
    with gzip.open(OUT / name, "rt") as f:
        return json.load(f)


# ---- per-arm description (pilot and confirmatory) -----------------------------------------------------------------------------

def pair_key(r):
    return f"{r['a']}|{r['b']}"


def held_week_flags(r):
    """Pair-week held flags: 1 if either partner is held by cost in that staying week."""
    return [int(x or y) for x, y in zip(r["held"]["A"], r["held"]["B"])]


def pair_pleasure(r):
    return [(x + y) / 2 for x, y in zip(r["p"]["A"], r["p"]["B"])]


def arm_counts(rows, arm):
    """Per-run (staying weeks, held weeks, pleasure sums) for one arm, with pairing clusters."""
    out = []
    for r in rows:
        if r["arm"] != arm:
            continue
        hf, pp = held_week_flags(r), pair_pleasure(r)
        out.append({"key": pair_key(r), "n": len(hf), "h": sum(hf), "p_held": sum(p for p, h in zip(pp, hf) if h),
                    "p_worth": sum(p for p, h in zip(pp, hf) if not h), "seed": r["seed"]})
    return out


def low_threshold(rows, arm="v22_bindable"):
    """The "low" cut: the LOW_Q quantile of all staying partner-week pleasures of the confirmed arm."""
    xs = [p for r in rows if r["arm"] == arm for x in "AB" for p in r["p"][x]]
    return float(np.quantile(xs, ST.LOW_Q)) if xs else float("nan")


def dissolution(rows, arm, low):
    """Low-or-falling partner-weeks in staying weeks: how many are held by cost, and by which cost."""
    per, causes = [], {}
    for r in rows:
        if r["arm"] != arm:
            continue
        n = h = 0
        for x in "AB":
            ser = r["p"][x]
            for i, p in enumerate(ser):
                if p < low or ST.falling(ser, i):
                    n += 1
                    if r["held"][x][i]:
                        h += 1
                        c = r["causes"][x].get(str(i)) or "joint"
                        causes[c] = causes.get(c, 0) + 1
        per.append({"key": pair_key(r), "n": n, "h": h})
    return per, causes


def bar_counts(rows, arm):
    per = []
    for r in rows:
        if r["arm"] != arm:
            continue
        v = [b["pair"] for b in r["bar"]]
        per.append({"key": pair_key(r), "n": len(v), "worth": v.count("worth"), "held": v.count("held"), "bar_leave": v.count("bar_leave")})
    return per


def describe(rows, arms=ARMS):
    low = low_threshold(rows)
    out = {"low_threshold": low, "arms": {}}
    for arm in arms:
        c = arm_counts(rows, arm)
        if not c:
            continue
        keys = [x["key"] for x in c]
        n = np.array([x["n"] for x in c]); h = np.array([x["h"] for x in c])
        d = {"runs": len(c), "staying_weeks": int(n.sum()), "held_weeks": int(h.sum()),
             "held_share": ST.ratio_ci(h, n, keys), "worth_share": ST.ratio_ci(n - h, n, keys),
             "p_worth": ST.ratio_ci([x["p_worth"] for x in c], n - h, keys),
             "p_held": ST.ratio_ci([x["p_held"] for x in c], h, keys)}
        per, causes = dissolution(rows, arm, low)
        dn = np.array([x["n"] for x in per]); dh = np.array([x["h"] for x in per])
        d["lowfall_weeks"] = int(dn.sum())
        d["lowfall_held_share"] = ST.ratio_ci(dh, dn, [x["key"] for x in per])
        d["lowfall_causes"] = causes
        bc = bar_counts(rows, arm)
        bn = np.array([x["n"] for x in bc])
        bk = [x["key"] for x in bc]
        d["bar_weeks"] = int(bn.sum())
        for v in ("worth", "held", "bar_leave"):
            d[f"bar_{v}_share"] = ST.ratio_ci([x[v] for x in bc], bn, bk)
        # pairing-level held shares (for paired comparisons and the power check)
        acc = {}
        for x in c:
            acc.setdefault(x["key"], [0, 0])
            acc[x["key"]][0] += x["h"]; acc[x["key"]][1] += x["n"]
        d["pairing_held"] = {k: (v[0] / v[1] if v[1] else None) for k, v in acc.items()}
        d["kinds"] = {k: sum(1 for r in rows if r["arm"] == arm and r["kind"] == k) for k in ("agreed", "apart", "imposed")}
        d["exits"] = sum(r["exits"] for r in rows if r["arm"] == arm)
        d["breaches"] = sum(r["breaches"] for r in rows if r["arm"] == arm)
        d["secs"] = float(np.mean([r["secs"] for r in rows if r["arm"] == arm]))
        out["arms"][arm] = d
    return out


def print_describe(d):
    print(f"low threshold (q{ST.LOW_Q} of v22_bindable staying partner-weeks): {d['low_threshold']:.4f}")
    for arm, x in d["arms"].items():
        print(f"\n== {arm}: runs {x['runs']} kinds {x['kinds']} exits {x['exits']} breaches {x['breaches']} mean secs {x['secs']:.1f}")
        print(f"  staying weeks {x['staying_weeks']}, held {x['held_weeks']}")
        print(f"  held share {ST.fmt_ci(x['held_share'])}   worth share {ST.fmt_ci(x['worth_share'])}")
        print(f"  pleasure worth {ST.fmt_ci(x['p_worth'])}   held {ST.fmt_ci(x['p_held'])}")
        print(f"  low/falling partner-weeks {x['lowfall_weeks']}, held share {ST.fmt_ci(x['lowfall_held_share'])}, causes {x['lowfall_causes']}")
        print(f"  bar lens ({x['bar_weeks']} weeks): worth {ST.fmt_ci(x['bar_worth_share'])} held {ST.fmt_ci(x['bar_held_share'])} "
              f"bar_leave {ST.fmt_ci(x['bar_bar_leave_share'])}")


# ---- confirmatory analysis (the prereg's predictions) -------------------------------------------------------------------------

KEPT = ROOT / "experiments" / "kept" / "stay-test-2026-11-10"
HOLM = ("P2", "P3", "P4", "P5", "P6", "P7", "P9a", "P9b")


def _paired(d, a, b):
    ks = [k for k in sorted(d["arms"][a]["pairing_held"]) if d["arms"][a]["pairing_held"][k] is not None
          and d["arms"][b]["pairing_held"].get(k) is not None]
    return (np.array([d["arms"][a]["pairing_held"][k] for k in ks]), np.array([d["arms"][b]["pairing_held"][k] for k in ks]))


def _shares(d, a):
    return np.array([v for v in d["arms"][a]["pairing_held"].values() if v is not None])


def _label(point_ok, lo_ok, p):
    if point_ok:
        return "holds robustly" if (lo_ok and p <= 0.05) else "holds but CI crosses threshold"
    return "miss robust" if not lo_ok else "miss but CI crosses threshold"


def _cmp(pid, q, x, y, margin, side):
    """Paired pairing-level test of mean(x - y) against margin. side 'greater' or 'less'."""
    from mar import stats as S
    dd = x - y
    ci = S.bootstrap_ci(dd, n_boot=10000, seed=7)
    t = S.permutation_test(x, y + margin, paired=True, alternative=side, n_perm=20000, seed=7)
    pt = dd.mean() >= margin if side == "greater" else dd.mean() <= margin
    inside = ci.lo >= margin if side == "greater" else ci.hi <= margin
    outside = ci.hi < margin if side == "greater" else ci.lo > margin
    return {"id": pid, "quantity": q, "n_pairings": len(dd), "est": float(dd.mean()), "lo": ci.lo, "hi": ci.hi, "margin": margin,
            "side": side, "p": t.p, "cliffs": S.cliffs_delta(x, y + margin) if len(dd) > 1 else None,
            "_pt": bool(pt), "_in": bool(inside), "_out": bool(outside)}


def _boot_ratio_p(num, den, keys, margin, side, n_boot=10000, seed=11):
    """Ratio of sums with a pairing bootstrap; p = share of draws on the wrong side of the margin."""
    num, den = np.asarray(num, float), np.asarray(den, float)
    ks = list(dict.fromkeys(keys)); ix = {k: i for i, k in enumerate(ks)}
    cn, cd = np.zeros(len(ks)), np.zeros(len(ks))
    for n_, d_, k in zip(num, den, keys):
        cn[ix[k]] += n_; cd[ix[k]] += d_
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(ks), len(ks))
        if cd[pick].sum() > 0:
            bs.append(cn[pick].sum() / cd[pick].sum())
    bs = np.array(bs)
    p = float(np.mean(bs <= margin) if side == "greater" else np.mean(bs >= margin))
    return bs, max(p, 1 / len(bs))


def _ratio_pred(pid, q, num, den, keys, margin, side):
    est = float(np.sum(num) / np.sum(den))
    bs, p = _boot_ratio_p(num, den, keys, margin, side)
    lo, hi = (float(x) for x in np.quantile(bs, [0.025, 0.975]))
    pt = est >= margin if side == "greater" else est <= margin
    inside = lo >= margin if side == "greater" else hi <= margin
    outside = hi < margin if side == "greater" else lo > margin
    return {"id": pid, "quantity": q, "n_pairings": len(set(keys)), "est": est, "lo": lo, "hi": hi, "margin": margin, "side": side, "p": p,
            "_pt": bool(pt), "_in": bool(inside), "_out": bool(outside)}


def _trap_pleasure_gap(rows):
    num_w, den_w, num_h, den_h, keys, within = [], [], [], [], [], {}
    for r in rows:
        if r["arm"] != "trap":
            continue
        hf, pp = held_week_flags(r), pair_pleasure(r)
        k = pair_key(r)
        keys.append(k)
        num_w.append(sum(p for p, h in zip(pp, hf) if not h)); den_w.append(sum(1 for h in hf if not h))
        num_h.append(sum(p for p, h in zip(pp, hf) if h)); den_h.append(sum(hf))
        w = within.setdefault(k, [[], []])
        w[0] += [p for p, h in zip(pp, hf) if not h]; w[1] += [p for p, h in zip(pp, hf) if h]
    num_w, den_w, num_h, den_h = map(np.array, (num_w, den_w, num_h, den_h))
    ks = list(dict.fromkeys(keys)); ix = {k: i for i, k in enumerate(ks)}
    agg = np.zeros((len(ks), 4))
    for i, k in enumerate(keys):
        agg[ix[k]] += (num_w[i], den_w[i], num_h[i], den_h[i])
    est = agg[:, 0].sum() / agg[:, 1].sum() - agg[:, 2].sum() / agg[:, 3].sum()
    rng = np.random.default_rng(13)
    bs = []
    for _ in range(10000):
        a = agg[rng.integers(0, len(ks), len(ks))]
        if a[:, 1].sum() > 0 and a[:, 3].sum() > 0:
            bs.append(a[:, 0].sum() / a[:, 1].sum() - a[:, 2].sum() / a[:, 3].sum())
    bs = np.array(bs)
    lo, hi = (float(x) for x in np.quantile(bs, [0.025, 0.975]))
    wd = np.array([np.mean(v[0]) - np.mean(v[1]) for v in within.values() if v[0] and v[1]])
    from mar import stats as S
    wci = S.bootstrap_ci(wd, n_boot=10000, seed=13)
    return ({"id": "P7", "quantity": "trap pair pleasure, worth-it weeks minus held weeks (pooled)", "n_pairings": len(ks), "est": float(est),
             "lo": lo, "hi": hi, "margin": 0.02, "side": "greater", "p": max(float(np.mean(bs <= 0.02)), 1 / len(bs)),
             "_pt": bool(est >= 0.02), "_in": bool(lo >= 0.02), "_out": bool(hi < 0.02)},
            {"within_pairing_mean": float(wd.mean()), "lo": wci.lo, "hi": wci.hi, "n_pairings": len(wd)})


def _cause_pred(pid, rows, arm, low, want, margin):
    """Share of held low-or-falling partner-weeks whose cause label contains `want` (pairing bootstrap)."""
    num, den, keys = [], [], []
    for r in rows:
        if r["arm"] != arm:
            continue
        n = h = 0
        for x in "AB":
            ser = r["p"][x]
            for i, p in enumerate(ser):
                if (p < low or ST.falling(ser, i)) and r["held"][x][i]:
                    n += 1
                    c = r["causes"][x].get(str(i)) or "joint"
                    h += want in c.split("+")
        num.append(h); den.append(n); keys.append(pair_key(r))
    if sum(den) == 0:
        return {"id": pid, "quantity": f"{arm}: share of held low/falling partner-weeks caused by {want}", "est": None, "not_measurable": True,
                "margin": margin, "side": "greater"}
    out = _ratio_pred(pid, f"{arm}: share of held low/falling partner-weeks caused by {want}", num, den, keys, margin, "greater")
    out["held_lowfall_weeks"] = int(sum(den))
    out.pop("p")
    return out


def analyze(rows):
    from mar import log as LOG
    from mar import stats as S
    d = describe(rows)
    low = d["low_threshold"]
    P = []
    base_held = d["arms"]["baseline"]["held_weeks"]
    P.append({"id": "P1", "quantity": "held weeks, baseline (sanity control)", "est": base_held, "margin": 0, "verdict": "pass" if base_held == 0 else "FAIL",
              "label": "not testable (deterministic)"})
    tr = _shares(d, "trap")
    t = S.permutation_test(tr, np.full(len(tr), 0.5), paired=True, alternative="greater", n_perm=20000, seed=7)
    hs = d["arms"]["trap"]["held_share"]
    P.append({"id": "P2", "quantity": "held share, trap", "n_pairings": len(tr), "est": hs[0], "lo": hs[1], "hi": hs[2], "margin": 0.5, "side": "greater",
              "p": t.p, "_pt": hs[0] >= 0.5, "_in": hs[1] >= 0.5, "_out": hs[2] < 0.5})
    x, y = _paired(d, "trap", "v22_bindable")
    P.append(_cmp("P3", "held share, trap minus v22_bindable (paired pairings)", x, y, 0.40, "greater"))
    b = _shares(d, "v22_bindable")
    t = S.permutation_test(b, np.full(len(b), 0.02), paired=True, alternative="less", n_perm=20000, seed=7)
    hs = d["arms"]["v22_bindable"]["held_share"]
    P.append({"id": "P4", "quantity": "held share, v22_bindable", "n_pairings": len(b), "est": hs[0], "lo": hs[1], "hi": hs[2], "margin": 0.02, "side": "less",
              "p": t.p, "_pt": hs[0] <= 0.02, "_in": hs[2] <= 0.02, "_out": hs[1] > 0.02})
    x, y = _paired(d, "v22_locked_hard", "v22_bindable")
    p5 = _cmp("P5", "held share, v22_locked_hard minus v22_bindable", x, y, 0.001, "greater")
    p5["descriptive"] = len(x) < 38
    P.append(p5)
    x, y = _paired(d, "v22_locked", "v22_bindable")
    P.append(_cmp("P6", "held share, v22_locked minus v22_bindable", x, y, 0.005, "less"))
    p7, within = _trap_pleasure_gap(rows)
    P.append(p7)
    P.append(_cause_pred("P8a", rows, "trap", low, "rule", 0.95))
    P.append(_cause_pred("P8b", rows, "v22_locked_hard", low, "bind", 0.80))
    for pid, arm, m, side in (("P9a", "v22_bindable", 0.5, "greater"), ("P9b", "trap", 0.25, "less")):
        bc = bar_counts(rows, arm)
        P.append(_ratio_pred(pid, f"bar lens worth share, {arm}", [z["worth"] for z in bc], [z["n"] for z in bc], [z["key"] for z in bc], m, side))
    adj = dict(zip(HOLM, S.holm([next(q["p"] for q in P if q["id"] == h) for h in HOLM])))
    for q in P:
        if q["id"] == "P1":
            continue
        if q.get("not_measurable"):
            q["label"] = ST.NOT_MEASURABLE
            continue
        q["p_holm"] = adj.get(q["id"])
        pv = q["p_holm"] if q["p_holm"] is not None else 0.0
        q["label"] = _label(q["_pt"], q["_in"], pv) if q["_pt"] else ("miss robust" if q["_out"] else "miss but CI crosses threshold")
        if q.get("descriptive"):
            q["label"] = "DESCRIPTIVE (underpowered): " + q["label"]
    d["predictions"] = [{k: v for k, v in q.items() if not k.startswith("_")} for q in P]
    d["p7_within_pairing"] = within
    for a in d["arms"].values():
        a.pop("pairing_held", None)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "analysis.json").write_text(json.dumps(d, indent=1))
    KEPT.mkdir(parents=True, exist_ok=True)
    (KEPT / "results.json").write_text(json.dumps(d, indent=1))
    print_describe(d)
    print()
    for q in d["predictions"]:
        print(q["id"], q["quantity"], "est", q.get("est"), "CI", q.get("lo"), q.get("hi"), "p_holm", q.get("p_holm"), "->", q["label"])
    print("P7 within-pairing:", within)
    LOG._append(ROOT / "experiments" / LOG.LOG_NAME, {
        "run_id": "stay-test-2026-11-10", "kind": "stay_test", "timestamp": LOG.now_utc(), "git_commit": LOG.git_commit(),
        "spec": "scripts/stay_test_run.py --run --seeds 10", "agents": "persona agents (57 pairings)", "months": None,
        "seed": "0-9", "model": None, "cost_usd": 0.0, "arms": list(ARMS), "runs": len(rows),
        "verdict": "; ".join(f"{q['id']} {q['label']}" for q in d["predictions"]),
        "report": "docs/results/stay-test.md", "trace": "runs/stay-test/results.json.gz (git-ignored)",
        "note": "ADR 0018 test 2; prereg docs/results/stay-test-prereg.md (commit c8bef76)"})
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--seeds", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.pilot:
        rows = run_all(PILOT_SEEDS, pairings(), workers=a.workers, tag="pilot")
        save(rows, "pilot.json.gz")
        print_describe(describe(rows))
    if a.run:
        rows = run_all(range(a.seeds), pairings(), workers=a.workers, tag="run")
        save(rows, "results.json.gz")
    if a.analyze:
        analyze(load())


if __name__ == "__main__":
    main()
