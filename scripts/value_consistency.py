"""Value consistency check (docs/results/value-consistency.md): the agents' own action values against the hedonic model's known
answer, in makers-off worlds. Measurement only; no model behaviour changes (src/mar/valuecheck.py).

World: H39b's M0 arm, which is the H38 baseline at L0 (pairing dial 0), exit fallback F4 with items (V2-split-loves), the per-persona
suffering-weight rule over 52 weeks, makers off. Pairings: H38's 120 confirmatory pairings. Scripted agents, no model calls.

At sampled weeks, for each partner, at the week's last decision call (the third pass), every action the agent scores is forced in
turn in an isolated copy, and compared with a copy in which the agent does nothing at that call. The rest of the week up to that call is
the same in every copy, so the difference is one unit of that action against idle. Later weeks use common random numbers.

  uv run python scripts/value_consistency.py --run          the main sample (world-only branches; at most 3 workers)
  uv run python scripts/value_consistency.py --harness      a smaller sample with the formation retries and stay readings inside the branches
  uv run python scripts/value_consistency.py --first        a smaller sample at the week's first call (the rest of the week re-plans)
  uv run python scripts/value_consistency.py --analyze      runs/value-consistency/analysis.json and the tables for the write-up

Agent recalibration (docs/results/agent-recalibration-prereg.md): add --v2 to run the same check with FixConfig(agent_values="v2",
bills_hurt=True); rows and analysis go to runs/value-consistency-v2/. --passtest prints the preregistered T1-T6 verdict for the rows in
the chosen directory; --reach the free checks that every verdict can happen (on the v1 rows).

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.
"""
import argparse
import copy
import dataclasses
import json
import random
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import h38_pairing_run as H38  # noqa: E402
from mar import exit_fallback as EF  # noqa: E402
from mar import exit_items as EI  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar import valuecheck as VC  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "value-consistency"
WORKERS = 3
RULE = {"decide_on": "weighted", "decide_weeks": 52}          # H39b's main rule (M0 arm)
LAST_START = H.WEEKS - max(VC.HORIZONS)                         # a sampled week leaves room for the 52-week horizon
MAIN = {"pairs_every": 1, "seeds": (0, 1, 2, 3), "weeks": 6, "k": 2, "harness": False}
HARNESS = {"pairs_every": 3, "seeds": (0,), "weeks": 3, "k": 2, "harness": True}
FIRST = {"pairs_every": 3, "seeds": (0,), "weeks": 4, "k": 0, "harness": False}
NOBILLS = {"pairs_every": 3, "seeds": (0, 1), "weeks": 6, "k": 2, "harness": False}     # recalibration Amendment 2 (descriptive)


def sample_weeks(a, b, seed, n):
    rng = random.Random(f"vc-weeks|{a}|{b}|{seed}")
    return sorted(rng.sample(range(1, LAST_START + 1), n))


V2 = {"agent_values": "v2", "bills_hurt": True}              # the recalibrated agents and bills that hurt (off by default)
# Bill horizon (docs/results/agent-bill-horizon-prereg.md): the 4-week horizon added, so a payment is measured through the settlement it feeds
HORIZONS4 = (1, 4, 13, 52)
V2B = {"agent_values": "v2b", "bills_hurt": True}
# Saturating pleasure scale (docs/decisions/0019-saturating-pleasure-scale.md): v2 and bills on the new scale; rows in runs/value-consistency-v2-sat/
V2SAT = {**V2, "pleasure_scale": "sat"}
# The hybrid agent's routine pass test (docs/results/hybrid-agent-prereg.md, PT-R): a third of the pairings, seed 0; runs/value-consistency-hybrid/
HYBRID = {"agent_values": "hybrid", "bills_hurt": True, "pleasure_scale": "sat"}
HSAMPLE = {"pairs_every": 3, "seeds": (0,), "weeks": 6, "k": 2, "harness": False}


def _ctx(extra=None):
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **RULE, **(extra or {}))
    return fx


def _lived_snapshot(lived):
    world = lived.world
    run, hook = world.run, world.hook
    world.run, world.hook = H.Run(), None
    try:
        return copy.deepcopy(lived)
    finally:
        world.run, world.hook = run, hook


def run_pair(a, b, seed, n_weeks, k, harness, extra=None, horizons=VC.HORIZONS):
    """Play one makers-off life as H39b's M0 arm does and measure the sampled decisions. -> list of decision records."""
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    weeks = set(sample_weeks(a, b, seed, n_weeks))
    out = []
    with HD.use_levers(RT.LEVERS), HD.use_fixes(_ctx(extra)), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[H38.CELL]):
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=H.WEEKS, decline=True)
        world = lived.world
        last = {"busy": {"A": False, "B": False}}
        hyb = world.fx is not None and world.fx.agent_values == "hybrid"
        for w in range(max(weeks) + 1):
            if w and w % NG.REVIEW_EVERY == 0:
                if lived.apart and lived.decline:
                    lived.retry(w, last)
                elif all(world.p[r]["in"] for r in "AB"):
                    lived.reading(w, last)
                elif hyb and any(world.p[r]["in"] for r in "AB"):
                    from mar import hybrid as HY
                    HY.return_reading(lived, w, last)
            elif hyb:
                lived.hybrid_week(w, last)
            world = lived.world
            if world.early_review:
                world.ladder_reviewed(w)
            if w in weeks:
                snap = VC.snapshot(world)
                sl = _lived_snapshot(lived) if harness else None
                for r in "AB":
                    rec = VC.measure_decision(snap, dict(last), w, r, k, horizons=horizons, lived=sl)
                    if rec is not None:
                        rec.update(a=a, b=b, seed=seed, persona=a if r == "A" else b,
                                   both_in=all(world.p[x]["in"] for x in "AB"))
                        out.append(rec)
            last = {"busy": world.step_week(w, last)}
    return out


def task(args):
    a, b, seed, n_weeks, k, harness, extra = args[:7]
    hz = args[7] if len(args) > 7 else VC.HORIZONS
    t0 = time.time()
    recs = run_pair(a, b, seed, n_weeks, k, harness, extra, hz)
    return recs, time.time() - t0


def collect(cfg, f, workers=WORKERS, extra=None, horizons=None):
    workers = min(workers, 3)
    OUT.mkdir(parents=True, exist_ok=True)
    pairs = H38.pairings(H38.CONFIRM)[::cfg["pairs_every"]]
    done = set()
    if f.exists():
        done = {(r["a"], r["b"], r["seed"]) for r in load(f)}
    tasks = [(a, b, s, cfg["weeks"], cfg["k"], cfg["harness"], extra, *([horizons] if horizons else []))
             for (a, b) in pairs for s in cfg["seeds"] if (a, b, s) not in done]
    print(f"{len(tasks)} tasks, {workers} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, f.open("a") as fh:
        for i, (recs, dt) in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            if recs:
                fh.write("\n".join(json.dumps(r) for r in recs) + "\n")
                fh.flush()
            if i % 20 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {dt:.1f}s wall {time.time() - t0:.0f}s", flush=True)


def load(f):
    return [json.loads(x) for x in Path(f).read_text().splitlines() if x.strip()]


# ---- analysis ----------------------------------------------------------------------------------------------------------------

def items(recs, applied=True):
    """Flatten to one row per (decision, action): perceived, actual per horizon and measure (own and partner), the decision's key."""
    out = []
    for d in recs:
        dk = (d["a"], d["b"], d["seed"], d["w"], d["r"])
        for it in d["items"]:
            if applied and not it["applied"]:
                continue
            out.append({"dk": dk, "w": d["w"], "run": (d["a"], d["b"], d["seed"]), "a": it["a"], "kind": it.get("kind"), "rule": it.get("rule", "ok"),
                        "persona": d.get("persona"),
                        "p": it["perceived"], "listed": it.get("listed", True), "in": d["ctx"]["in_hh"] and d["ctx"]["other_in"],
                        "act": {int(h): v for h, v in it["actual"].items()}, "g": {int(h): v for h, v in it["groups"].items()},
                        "levels": d["ctx"]["levels"]})
    return out


def _ranks(x):
    """Ranks with ties averaged (as scipy.stats.rankdata)."""
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    xs = x[order]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return None
    rx, ry = _ranks(x), _ranks(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def boot_mean(rows, f, n=1000, seed=0):
    """Mean of f over rows with a 95% bootstrap interval, resampling runs (a run's decisions are not independent)."""
    by = {}
    for r in rows:
        by.setdefault(r["run"], []).append(f(r))
    keys = list(by)
    if not keys:
        return None
    est = float(np.mean([v for k in keys for v in by[k]]))
    rng = np.random.default_rng(seed)
    sums = np.array([sum(by[k]) for k in keys])
    cnts = np.array([len(by[k]) for k in keys])
    bs = []
    for _ in range(n):
        idx = rng.integers(0, len(keys), len(keys))
        bs.append(sums[idx].sum() / cnts[idx].sum())
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"est": round(est, 5), "lo": round(float(lo), 5), "hi": round(float(hi), 5), "n": int(cnts.sum())}


def act_of(r, h, m="net", who="own"):
    return r["act"][h][who][m]


def analyze(recs, horizons=VC.HORIZONS, measures=("net", "pl", "raw", "wnet")):
    rows = items(recs)
    res = {"decisions": len(recs), "items": len(rows), "applied_share": None, "per_action": {}, "overall": {}, "idle": {},
           "groups": {}, "top_agree": {}}
    allit = [it for d in recs for it in d["items"]]
    res["applied_share"] = round(sum(it["applied"] for it in allit) / max(1, len(allit)), 4)
    acts = sorted({r["a"] for r in rows}, key=lambda a: -sum(1 for r in rows if r["a"] == a))
    for a in acts:
        xs = [r for r in rows if r["a"] == a]
        e = {"n": len(xs), "listed_share": round(float(np.mean([r["listed"] for r in xs])), 3),
             "perceived": boot_mean(xs, lambda r: r["p"])}
        for h in horizons:
            for m in measures:
                e[f"actual_{m}_{h}"] = boot_mean(xs, lambda r, h=h, m=m: act_of(r, h, m))
            e[f"partner_net_{h}"] = boot_mean(xs, lambda r, h=h: act_of(r, h, "net", "partner"))
            e[f"rho_net_{h}"] = spearman([r["p"] for r in xs], [act_of(r, h) for r in xs])
            e[f"gap_net_{h}"] = boot_mean(xs, lambda r, h=h: act_of(r, h) - r["p"])
            e[f"sign_disagree_{h}"] = round(float(np.mean([(r["p"] > 0.003) != (act_of(r, h) > 0) for r in xs])), 3)
        e["in_hh_share"] = round(float(np.mean([r["in"] for r in xs])), 3)
        res["per_action"][a] = e
        res["groups"][a] = {h: {g: round(float(np.mean([r["g"][h].get(g, 0.0) for r in xs])), 5)
                                for g in sorted({g for r in xs for g in r["g"][h]})} for h in horizons}
    for h in horizons:
        for m in measures:
            p = np.array([r["p"] for r in rows])
            y = np.array([act_of(r, h, m) for r in rows])
            slope = float((p @ y) / (p @ p)) if p @ p > 0 else None
            # within-decision rank agreement (decisions with 3 or more measured actions)
            byd = {}
            for r in rows:
                byd.setdefault(r["dk"], []).append(r)
            wr = [spearman([r["p"] for r in v], [act_of(r, h, m) for r in v]) for v in byd.values() if len(v) >= 3]
            wr = [x for x in wr if x is not None]
            res["overall"][f"{m}_{h}"] = {"rho_pooled": spearman(list(p), list(y)), "rho_within_mean": round(float(np.mean(wr)), 4) if wr else None,
                                          "n_within": len(wr), "slope_through_0": round(slope, 4) if slope is not None else None,
                                          "mean_perceived": round(float(p.mean()), 5), "mean_actual": round(float(y.mean()), 5)}
            # top choice: does the agent's own best action (or idle when nothing clears the floor) match the best by actual?
            agree = n = 0
            for v in byd.values():
                if len(v) < 2:
                    continue
                n += 1
                best_p = max(v, key=lambda r: r["p"])
                own = best_p["a"] if best_p["p"] > 0.003 else "idle"
                best_a = max(v, key=lambda r: act_of(r, h, m))
                act = best_a["a"] if act_of(best_a, h, m) > 0 else "idle"
                agree += own == act
            res["top_agree"][f"{m}_{h}"] = {"share": round(agree / max(1, n), 4), "n": n}
    # the swap the task names: the agent's own best action against its next best (idle when nothing else clears the floor)
    byd = {}
    for r in rows:
        byd.setdefault(r["dk"], []).append(r)
    sw = []
    for v in byd.values():
        v = sorted(v, key=lambda r: -r["p"])
        if v[0]["p"] <= 0.003:
            continue
        nxt = v[1] if len(v) > 1 and v[1]["p"] > 0.003 else None
        sw.append((v[0], nxt))
    res["swap"] = {"n": len(sw), "next_is_idle": round(float(np.mean([n is None for _, n in sw])), 4) if sw else None,
                   "perceived_margin": round(float(np.mean([t["p"] - (n["p"] if n else 0.0) for t, n in sw])), 5) if sw else None}
    for h in horizons:
        m = [act_of(t, h) - (act_of(n, h) if n else 0.0) for t, n in sw]
        res["swap"][f"actual_margin_net_{h}"] = round(float(np.mean(m)), 5) if m else None
        res["swap"][f"right_order_{h}"] = round(float(np.mean([x > 0 for x in m])), 4) if m else None
    # in the household against apart
    res["by_in"] = {}
    for a in acts:
        for tag, keep in (("in", True), ("apart", False)):
            xs = [r for r in rows if r["a"] == a and r["in"] == keep]
            if len(xs) >= 20:
                res["by_in"][f"{a}|{tag}"] = {"n": len(xs), "perceived": round(float(np.mean([r["p"] for r in xs])), 5),
                                              **{f"net_{h}": round(float(np.mean([act_of(r, h) for r in xs])), 5) for h in horizons}}
    # idle units: decisions where nothing clears the agent's floor (the agent leaves the call idle)
    byd = {}
    for r in rows:
        byd.setdefault(r["dk"], []).append(r)
    idle = [v for v in byd.values() if max(r["p"] for r in v) <= 0.003]
    res["idle"]["decisions"] = len(idle)
    res["idle"]["share_of_decisions"] = round(len(idle) / max(1, len(byd)), 4)
    for h in horizons:
        best = [max(act_of(r, h) for r in v) for v in idle]
        res["idle"][f"best_actual_net_{h}"] = round(float(np.mean(best)), 5) if best else None
        res["idle"][f"share_best_positive_{h}"] = round(float(np.mean([b > 0 for b in best])), 4) if best else None
        for a in ("rest", "see_friend", "work", "together", "spend_self"):
            xs = [r for v in idle for r in v if r["a"] == a]
            res["idle"][f"{a}_net_{h}"] = boot_mean(xs, lambda r, h=h: act_of(r, h)) if xs else None
    return res


# ---- the preregistered pass test (docs/results/agent-recalibration-prereg.md) ---------------------------------------------------

PASS_ACTIONS = ("work", "rest", "see_friend", "together", "spend_shared", "spend_self")
T_BARS = {"T1": 0.70, "T2": 0.60, "T3": 0.60, "T4": 0.60, "T5": (0.8, 1.25)}


def _prosocial():
    from mar.worlds.household import PersonaAgent
    return {pid: PersonaAgent(p).prosocial for pid, p in RT.personas().items()}


def target_fn(kind="net"):
    """The 'actual' a row is held to. net: own net (the main line). social: own + prosocial x partner net (the utility's own
    definition). unclipped: own unclipped pleasure - suffering."""
    if kind == "net":
        return lambda r, h: act_of(r, h)
    if kind == "oldline":            # ADR 0019: the same rows held to the old capped line (clipped pleasure - suffering)
        return lambda r, h: r["act"][h]["own"]["pcnet"]
    if kind == "unclipped":
        return lambda r, h: r["act"][h]["own"]["raw"] - (r["act"][h]["own"]["pl"] - r["act"][h]["own"]["net"])
    pro = _prosocial()
    return lambda r, h: act_of(r, h) + pro.get(r["persona"], 0.0) * act_of(r, h, "net", "partner")


def passtest(recs, kind="net", perceived=None, horizon=1, actions=PASS_ACTIONS, keep=None):
    """T1-T6 at the 1-week horizon. perceived: optional f(row) replacing the agent's number (the --reach checks). horizon: the horizon
    a row without a soft rule is held to (the bill horizon's pass test uses 4); actions: the actions T6 bars; keep: a row filter."""
    rows = [r for r in items(recs) if keep is None or keep(r)]
    tf = target_fn(kind)
    P = perceived or (lambda r: r["p"])
    pv = np.array([P(r) for r in rows])
    av = np.array([tf(r, 13 if r["rule"] == "soft" else horizon) for r in rows])   # Amendment 1: a soft-rule row is held to 13 weeks throughout
    byd = {}
    for r, p_, a_ in zip(rows, pv, av):
        byd.setdefault(r["dk"], []).append((r, p_, a_))
    within = [spearman([x[1] for x in v], [x[2] for x in v]) for v in byd.values() if len(v) >= 3]
    within = [x for x in within if x is not None]
    top = n = 0
    sw = []
    for v in byd.values():
        if len(v) < 2:
            continue
        n += 1
        bp = max(v, key=lambda x: x[1])
        own = bp[0]["a"] if bp[1] > 0.003 else "idle"
        ba = max(v, key=lambda x: x[2])
        top += own == (ba[0]["a"] if ba[2] > 0 else "idle")
        vs = sorted(v, key=lambda x: -x[1])
        if vs[0][1] > 0.003:
            nxt = vs[1] if vs[1][1] > 0.003 else None
            sw.append(vs[0][2] - (nxt[2] if nxt else 0.0) > 0)
    out = {"T1": spearman(list(pv), list(av)), "T2": float(np.mean(within)) if within else None, "T3": top / max(1, n),
           "T4": float(np.mean(sw)) if sw else None, "T5": float((pv @ av) / (pv @ pv)) if pv @ pv > 0 else None, "T6": {}}
    for a in actions:
        ok = [(r, p_) for r, p_ in zip(rows, pv) if r["a"] == a and r["rule"] != "soft"]
        soft = [(r, p_) for r, p_ in zip(rows, pv) if r["a"] == a and r["rule"] == "soft"]
        e = {}
        for tag, xs, h in (("ok", ok, horizon), ("soft", soft, 13)):
            if len(xs) >= 100:
                ma, mp = float(np.mean([tf(r, h) for r, _ in xs])), float(np.mean([p_ for _, p_ in xs]))
                bar = max(0.015, 0.25 * abs(ma))
                e[tag] = {"n": len(xs), "actual": round(ma, 5), "perceived": round(mp, 5), "gap": round(mp - ma, 5),
                          "bar": round(bar, 5), "holds": abs(mp - ma) <= bar, "horizon": h}
            elif xs:
                e[tag] = {"n": len(xs), "note": "n < 100, no bar"}
        out["T6"][a] = e
    hold = {"T1": out["T1"] is not None and out["T1"] >= T_BARS["T1"], "T2": out["T2"] is not None and out["T2"] >= T_BARS["T2"],
            "T3": out["T3"] >= T_BARS["T3"], "T4": out["T4"] is not None and out["T4"] >= T_BARS["T4"],
            "T5": out["T5"] is not None and T_BARS["T5"][0] <= out["T5"] <= T_BARS["T5"][1],
            "T6": all(x.get("holds", True) for e in out["T6"].values() for x in e.values())}
    out["holds"] = hold
    out["verdict"] = "PASS" if all(hold.values()) else "FAIL"
    return out


# ---- the bill horizon's pass test (docs/results/agent-bill-horizon-prereg.md) ---------------------------------------------------

V2_ONE_WEEK = {"T1": 0.9931, "T2": 0.9919, "T3": 0.9766, "T4": 0.9204}      # v2 + bills, rows of the five other actions (runs/value-consistency-v2-h4)
ONE_WEEK_TOL = 0.05                                                         # how far each may fall (T3, T4: 5 points)
OTHER_ACTIONS = tuple(a for a in PASS_ACTIONS if a != "spend_shared")


def passtest4(recs, kind="net", perceived=None):
    """U1-U5: T1-T5 with every row held to its 4-week actual (a soft-rule row to 13 weeks, as before); U6: paying a shared bill, mean
    perceived within max(0.015, 0.25 x |mean actual|) of its 4-week actual; U6b: the same on payments made before the settlement week.
    O1-O6: the one-week line must not get worse: on the rows of the five other actions (paying a bill is valued past the week on
    purpose), T1-T4 at 1 week no more than ONE_WEEK_TOL below v2's on the same rows, T5 in [0.8, 1.25], T6 at 1 week for each."""
    four = passtest(recs, kind, perceived, horizon=4, actions=("spend_shared",))
    pre = passtest(recs, kind, perceived, horizon=4, actions=("spend_shared",), keep=lambda r: r["w"] % H.MONTH_WEEKS != H.MONTH_WEEKS - 1)
    one = passtest(recs, kind, perceived, horizon=1, actions=OTHER_ACTIONS, keep=lambda r: r["a"] != "spend_shared")
    one_all = passtest(recs, kind, perceived, horizon=1, actions=())
    ok6 = lambda t: t["T6"].get("spend_shared", {}).get("ok", {}).get("holds", False)      # noqa: E731
    hold = {**{f"U{i}": four["holds"][f"T{i}"] for i in range(1, 6)}, "U6": ok6(four), "U6b": ok6(pre),
            **{f"O{i}": one[f"T{i}"] is not None and one[f"T{i}"] >= V2_ONE_WEEK[f"T{i}"] - ONE_WEEK_TOL for i in range(1, 5)},
            "O5": one["holds"]["T5"], "O6": one["holds"]["T6"]}
    return {"four_weeks": four, "four_weeks_before_settlement": {"T6": pre["T6"]}, "one_week": one,
            "one_week_all_rows": {k: one_all[k] for k in ("T1", "T2", "T3", "T4", "T5")}, "holds": hold,
            "verdict": "PASS" if all(hold.values()) else "FAIL"}


def reach4(recs):
    """Bill horizon prereg, "Can every verdict happen?", on the v2 rows with the 4-week horizon (no v2b runs)."""
    o4 = lambda r: act_of(r, 13 if r["rule"] == "soft" else 4)              # noqa: E731
    o1 = lambda r: act_of(r, 13 if r["rule"] == "soft" else 1)              # noqa: E731
    bills4 = lambda r: o4(r) if r["a"] == "spend_shared" else r["p"]        # noqa: E731
    cases = {"v2 as it is": None, "oracle at 4 weeks for every action": o4, "v2, bills at their 4-week actual": bills4,
             "oracle at 1 week (bills at 1 week)": o1, "v2, bills at twice their 4-week actual": lambda r: 2 * o4(r) if r["a"] == "spend_shared" else r["p"],
             "v2 halved (U5, O5 fail)": lambda r: 0.5 * r["p"],
             "v2 with noise (+-0.03, every row)": lambda r: r["p"] + 0.03 * (1 if zlib.crc32(repr((r["dk"], r["a"])).encode()) % 2 else -1)}
    out = {}
    for name, f in cases.items():
        res = passtest4(recs, perceived=f)
        out[name] = {"verdict": res["verdict"], "holds": res["holds"],
                     "U": {k: res["four_weeks"][k] for k in ("T1", "T2", "T3", "T4", "T5")},
                     "U6": res["four_weeks"]["T6"]["spend_shared"], "U6b": res["four_weeks_before_settlement"]["T6"]["spend_shared"],
                     "O": {k: res["one_week"][k] for k in ("T1", "T2", "T3", "T4", "T5")}}
    return out


def reach(recs):
    """Prereg "Can every verdict happen?" on the v1 rows: an oracle agent (perceived = the 1-week actual; the 13-week actual where a soft
    rule binds, as T6 holds those rows) passes; the v1 agents fail T1-T4 and T6; doubling the oracle's numbers fails T5 (and T6)."""
    oracle = lambda r: act_of(r, 13 if r["rule"] == "soft" else 1)          # noqa: E731
    return {"oracle (PASS reachable)": passtest(recs, perceived=oracle), "v1 agents as they are": passtest(recs),
            "oracle doubled (T5 fails)": passtest(recs, perceived=lambda r: 2 * oracle(r))}


# ---- carry-over terms (docs/results/agent-bill-horizon-prereg.md, step 2) --------------------------------------------------------

# The model's carry-over stocks and the observer groups that carry them into the agent's own net. "pot" is the shared pot as the model
# feels it: the security level (lost buffer, the pot's share in assets) and friction (bill stress and eviction; warnings and presses also
# land there, and are reported apart by the rule column). Trust is not a hedonic term: it moves net only through behaviour, so it shows
# up in the other groups.
TERMS = {"money": ("money",), "pot (security)": ("security",), "pot (bill friction)": ("friction",), "rest": ("rest",),
         "connection": ("connection",), "partner": ("partner",), "friends": ("friends",), "bonds": ("levers",),
         "conditions": ("conditions",), "clip": ("clip",), "other": ("items", "pressure", "intrinsic", "autonomy", "other")}


def gaps(recs, horizons=HORIZONS4):
    """Per action (applied, no soft rule): the k-week own-net effect of each carry-over term, and its gap to the 1-week effect, which is
    what a one-week valuer sees. -> {action: {"n", "perceived", "net": {h: x}, "terms": {term: {h: x}}, "gap": {term: {h: x - x_1}}}}"""
    rows = [r for r in items(recs) if r["rule"] != "soft"]
    out = {}
    for a in PASS_ACTIONS:
        xs = [r for r in rows if r["a"] == a]
        if not xs:
            continue
        e = {"n": len(xs), "in_hh_share": round(float(np.mean([r["in"] for r in xs])), 3),
             "perceived": round(float(np.mean([r["p"] for r in xs])), 5),
             "net": {h: boot_mean(xs, lambda r, h=h: act_of(r, h)) for h in horizons}, "terms": {}, "gap": {}}
        for t, gs in TERMS.items():
            e["terms"][t] = {h: round(float(np.mean([sum(r["g"][h].get(g, 0.0) for g in gs) for r in xs])), 5) for h in horizons}
            e["gap"][t] = {h: round(e["terms"][t][h] - e["terms"][t][horizons[0]], 5) for h in horizons}
        out[a] = e
    return out


def gaps_table(g, horizons=HORIZONS4):
    lines = []
    for a, e in g.items():
        lines.append(f"\n{a} (n {e['n']}, in a household {e['in_hh_share']:.0%}, perceived {e['perceived']:+.4f}); net "
                     + ", ".join(f"{h}w {e['net'][h]['est']:+.4f}" for h in horizons))
        lines.append("| term | " + " | ".join(f"{h}w" for h in horizons) + " | " + " | ".join(f"gap {h}w" for h in horizons[1:]) + " |")
        lines.append("|---" * (2 * len(horizons)) + "|")
        for t in TERMS:
            x, d = e["terms"][t], e["gap"][t]
            if max(abs(v) for v in x.values()) < 5e-4:
                continue
            lines.append(f"| {t} | " + " | ".join(f"{x[h]:+.4f}" for h in horizons) + " | "
                         + " | ".join(f"{d[h]:+.4f}" for h in horizons[1:]) + " |")
    return "\n".join(lines)


def table(res, h=1, m="net"):
    lines = [f"| action | n | perceived | actual {m} {h}w | gap | rho | sign disagree |", "|---|---|---|---|---|---|---|"]
    for a, e in res["per_action"].items():
        p, y, g = e["perceived"], e[f"actual_{m}_{h}"], e[f"gap_net_{h}"]
        lines.append(f"| {a} | {e['n']} | {p['est']:+.4f} | {y['est']:+.4f} [{y['lo']:+.4f}, {y['hi']:+.4f}] | {g['est']:+.4f} | "
                     f"{e[f'rho_net_{h}'] if e[f'rho_net_{h}'] is None else round(e[f'rho_net_{h}'], 3)} | {e[f'sign_disagree_{h}']} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--harness", action="store_true")
    ap.add_argument("--first", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--v2", action="store_true", help="agent values v2 and bills that hurt; rows in runs/value-consistency-v2/")
    ap.add_argument("--v2nobills", action="store_true", help="descriptive: v2 with bills off, a smaller sample (Amendment 2)")
    ap.add_argument("--v2h4", action="store_true", help="bill horizon prereg: v2 and bills, horizons 1/4/13/52; runs/value-consistency-v2-h4/")
    ap.add_argument("--v2b", action="store_true", help="bill horizon: agent_values v2b and bills, horizons 1/4/13/52; runs/value-consistency-v2b/")
    ap.add_argument("--v2sat", action="store_true", help="ADR 0019: v2 and bills on the saturating scale; runs/value-consistency-v2-sat/")
    ap.add_argument("--hybrid", action="store_true", help="the hybrid agent's routine pass test (PT-R); runs/value-consistency-hybrid/")
    ap.add_argument("--world", action="store_true", help="hybrid prereg Amendment 2: with --v2sat or --hybrid, satiety_expect='world'; "
                    "rows in the same directory name with -world")
    ap.add_argument("--a3", action="store_true", help="hybrid prereg Amendment 3: with --hybrid --world, hybrid_w='persona' and "
                    "hybrid_readings='world'; rows in runs/value-consistency-hybrid-world-a3/")
    ap.add_argument("--a4", action="store_true", help="hybrid prereg Amendment 4 (hybrid-exit-option-prereg.md): with --hybrid --world, "
                    "Amendment 3's flags plus hybrid_lone and hybrid_exit; rows in runs/value-consistency-hybrid-world-a4/")
    ap.add_argument("--a5", action="store_true", help="hybrid prereg Amendment 5 (hybrid-leaving-prereg.md): with --hybrid --world, "
                    "Amendment 4's flags plus the tally, the growing exit cost and the lived outside option; runs/value-consistency-hybrid-world-a5/")
    ap.add_argument("--gaps", action="store_true", help="carry-over terms: per action, per group, the k-week effect minus the 1-week effect")
    ap.add_argument("--passtest", action="store_true")
    ap.add_argument("--reach", action="store_true")
    a = ap.parse_args()
    global OUT
    extra = None
    if a.v2:
        OUT, extra = ROOT / "runs" / "value-consistency-v2", V2
    hz = None
    if a.v2h4:
        OUT, extra, hz = ROOT / "runs" / "value-consistency-v2-h4", V2, HORIZONS4
    if a.v2b:
        OUT, extra, hz = ROOT / "runs" / "value-consistency-v2b", V2B, HORIZONS4
    if a.v2sat:
        OUT, extra = ROOT / "runs" / "value-consistency-v2-sat", V2SAT
    if a.hybrid:
        OUT, extra = ROOT / "runs" / "value-consistency-hybrid", HYBRID
    if a.world and (a.v2sat or a.hybrid):          # Amendment 2: time together at the world's satiety
        OUT, extra = OUT.parent / (OUT.name + "-world"), {**extra, "satiety_expect": "world"}
    if a.a3 and a.hybrid and a.world:              # Amendment 3: the suffering weight and readings run by the world
        OUT, extra = OUT.parent / (OUT.name + "-a3"), {**extra, "hybrid_w": "persona", "hybrid_readings": "world"}
    if a.a4 and a.hybrid and a.world:              # Amendment 4: the lone member's reading and forecasts with the option to leave
        OUT, extra = OUT.parent / (OUT.name + "-a4"), {**extra, "hybrid_w": "persona", "hybrid_readings": "world", "hybrid_lone": True,
                                                       "hybrid_exit": True}
    if a.a5 and a.hybrid and a.world:              # Amendment 5: how the hybrid decides to leave
        OUT, extra = OUT.parent / (OUT.name + "-a5"), {**extra, "hybrid_w": "persona", "hybrid_readings": "world", "hybrid_lone": True,
                                                       "hybrid_exit": True, "hybrid_tally": "level", "tally_half": 13.0, "tally_line": 0.02, "exit_grow": 0.04, "hybrid_outside": "lived"}
    if a.hybrid:
        if a.run:
            collect(HSAMPLE, OUT / "rows.jsonl", a.workers, extra)
            a.run = False
    if a.v2nobills:
        OUT, extra = ROOT / "runs" / "value-consistency-v2-nobills", {"agent_values": "v2"}
        if a.run:
            collect(NOBILLS, OUT / "rows.jsonl", a.workers, extra)
            a.run = False
    if a.reach and not hz:
        res = reach(load(ROOT / "runs" / "value-consistency" / "rows.jsonl"))
        print(json.dumps(res, indent=1, default=str))
        (ROOT / "runs" / "value-consistency" / "reach.json").write_text(json.dumps(res, indent=1, default=str))
    if a.run:
        collect(MAIN, OUT / "rows.jsonl", a.workers, extra, hz)
    if a.harness:
        collect(HARNESS, OUT / "harness.jsonl", a.workers, extra)
    if a.first:
        collect(FIRST, OUT / "first.jsonl", a.workers, extra)
    if a.gaps:
        recs = load(OUT / "rows.jsonl")
        hzs = tuple(int(h) for h in recs[0]["items"][0]["actual"])
        g = gaps(recs, hzs)
        print(gaps_table(g, hzs))
        (OUT / "gaps.json").write_text(json.dumps(g, indent=1, default=str))
    if a.passtest and hz:
        recs = load(OUT / "rows.jsonl")
        res = {k: passtest4(recs, k) for k in ("net", "social", "unclipped")}
        print(json.dumps(res, indent=1, default=str))
        (OUT / "passtest4.json").write_text(json.dumps(res, indent=1, default=str))
        a.passtest = False
    if a.reach and hz:
        res = reach4(load(OUT / "rows.jsonl"))
        print(json.dumps(res, indent=1, default=str))
        (OUT / "reach4.json").write_text(json.dumps(res, indent=1, default=str))
        a.reach = False
    if a.passtest:
        recs = load(OUT / "rows.jsonl")
        kinds = ("net", "social", "unclipped") + (("oldline",) if "pcnet" in recs[0]["items"][0]["actual"]["1"]["own"] else ())
        res = {k: passtest(recs, k) for k in kinds}
        print(json.dumps(res, indent=1, default=str))
        (OUT / "passtest.json").write_text(json.dumps(res, indent=1, default=str))
    if a.analyze:
        res = {}
        for name in ("rows", "harness", "first"):
            f = OUT / f"{name}.jsonl"
            if f.exists():
                res[name] = analyze(load(f))
                print(f"== {name}: {res[name]['decisions']} decisions, {res[name]['items']} items, applied {res[name]['applied_share']}")
                for h in VC.HORIZONS:
                    print(table(res[name], h))
                print(json.dumps({k: res[name][k] for k in ("overall", "top_agree", "idle", "swap", "by_in")}, indent=1))
        (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
