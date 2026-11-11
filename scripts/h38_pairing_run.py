"""H38 pairing norms (docs/results/h38-pairing-norms-prereg.md): a pairing-pressure dial and each part alone, on the v2-retest household
(baseline rules, may decline, fixes and levers on) with exit fallback F4 and items (cell V2). Scripted persona agents, no model calls.
Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

  uv run python scripts/h38_pairing_run.py --pilot      EXPLORATORY (sample seed 900, seeds 900-901; never cited as a result)
  uv run python scripts/h38_pairing_run.py --reach      the free reachability checks (prereg "Can every verdict happen?")
  uv run python scripts/h38_pairing_run.py --run        the confirmatory run (at most 3 workers)
  uv run python scripts/h38_pairing_run.py --analyze    prereg vs actual; writes runs/h38-pairing/analysis.json
"""
import argparse
import dataclasses
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import exit_fallback as EF  # noqa: E402
from mar import exit_items as EI  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "h38-pairing"
WORKERS = 3
LEVELS = (0, 0.5, 1, 2, 4)
DIAL = {f"L{lv:g}": PR.dial(lv) for lv in LEVELS}
PART_NAME = {"stigma": "S", "reward": "R", "withdraw": "W", "exit": "X"}
PARTS_ALONE = {f"{PART_NAME[p]}{lv}": PR.dial(lv, parts=(p,)) for lv in (4, 1) for p in PR.PARTS}
DESCRIPTIVE_DIAL = {"L8": PR.dial(8)}           # Amendment 1: past the preregistered top of the dial (descriptive)
ARMS = {**DIAL, **DESCRIPTIVE_DIAL, **PARTS_ALONE}
CONFIRM = {"sample_seed": 38, "n_other": 105, "seeds": (0, 1, 2, 3)}
PILOT = {"sample_seed": 900, "n_other": 30, "seeds": (900, 901)}
CELL = "V2-split-loves"


def pairings(cfg):
    if cfg["sample_seed"] == CONFIRM["sample_seed"]:
        return RT.sample(cfg["n_other"], cfg["sample_seed"])
    import random
    pop = RT.population()
    return random.Random(cfg["sample_seed"]).sample(pop, cfg["n_other"])        # pilot: any pairings, drawn with its own seed


def _liberty(world, w, memo):
    """Liberty with powers at week w (as household evolution run 2 scores it: the lower partner's liberty)."""
    from mar import empowerment as E
    from mar import liberty as L
    ps = (world.personas["A"], world.personas["B"])
    hw = E.HouseholdWorld(tuple(E.consent_for(p) for p in ps), powers=True)
    scripts = tuple(E.script_for(p) for p in ps)
    state = hw.snapshot(world, w)
    mk = (state, scripts, hw.consents)
    if mk not in memo:
        memo[mk] = L.household_liberty(hw, world.gate, state, scripts, L.HH_K, L.W_DEFAULT, E.HH_CAP, 2)
    return min(r["liberty"] for r in memo[mk])


def play(pc, a, b, seed, stay=True, weeks=H.WEEKS, liberty=None):
    """One lived run under pairing config pc. -> (Run, lived, stay readings [(week, reading)]). liberty: a memo dict to also measure
    liberty with powers at liberty.HH_SNAPSHOTS (stored on the run as run.liberty)."""
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=pc)
    readings = []
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[CELL]):
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=weeks, decline=True)
        world = lived.world
        if liberty is not None:                           # measured at the start of the week, as liberty.household_run_liberty does
            world.run.liberty = []

            def hook(wd, wk_):
                if wk_ in (0, 52):
                    wd.run.liberty.append(_liberty(wd, wk_, liberty))
            world.hook = hook
        last = {"busy": {"A": False, "B": False}}
        for w in range(world.weeks):                      # = BaselineLived.play, plus the stay lens before each reading
            if w and w % NG.REVIEW_EVERY == 0:
                if lived.apart and lived.decline:
                    lived.retry(w, last)
                elif all(world.p[r]["in"] for r in "AB"):
                    if stay:
                        readings.append((w, PR.stay_reading(world, w, last)))
                    lived.reading(w, last)
            if world.early_review:
                world.ladder_reviewed(w)
            last = {"busy": world.step_week(w, last)}
        world.run.final = {r: {**world.p[r], "pooled": world.pool, "put": world.put[r]} for r in "AB"}
        world.run.fix = world.fix_report()
        world.run.exits = list(world.exit_log)
    return world.run, lived, readings


def record(run, lived, readings, arm, a, b, seed):
    rows = run.outcomes
    m = RT.metrics(run, lived)
    ps = RT.personas()
    rec = {"arm": arm, "a": a, "b": b, "seed": seed, **{k: m[k] for k in ("pl", "net", "snon", "snon_share", "both_share", "formed0",
                                                                          "ever_formed", "ended")},
           "leaves": m.get("leaves", 0), "friend_declined": lived.world.pstats["friend_declined"]}
    for r, pid in (("A", a), ("B", b)):
        hs = [o["hedonic"][r] for o in rows]
        fx = [h["fix"] for h in hs]
        tog = [f["together_now"] for f in fx]
        fr = [f["friends"] for f in fx]
        rec[r] = {"v": PR.values_pairing(ps[pid]), "pl": float(np.mean([h["pleasure"] for h in hs])),
                  "net": float(np.mean([h["pleasure"] - h["s_off"] - h["s_non"] for h in hs])),
                  "snon": float(np.mean([h["s_non"] for h in hs])),
                  "together": float(np.mean(tog)), "friends": float(np.mean(fr)),
                  "friends_tog": float(np.mean([x for x, t in zip(fr, tog) if t])) if any(tog) else None,
                  "friends_apart": float(np.mean([x for x, t in zip(fr, tog) if not t])) if not all(tog) else None,
                  "c_friend": float(np.mean([f.get("c_friend", 0.0) for f in fx])),
                  "reward": float(np.mean([f["pr_reward"] for f in fx])), "stigma": float(np.mean([f["pr_stigma"] for f in fx])),
                  "exit": float(np.mean([f["pr_exit"] for f in fx])), "intrinsic": float(np.mean([f["pr_intrinsic"] for f in fx])),
                  "p_raw": float(np.mean([h["p_raw"] for h in hs])), "clipped": float(np.mean([h["p_raw"] > 1.0 for h in hs])),
                  # Amendment 1: the clipped pleasure the week would have had without the direct pressure terms (spiral ignored)
                  "p_nopress": float(np.mean([min(1.0, max(0.0, h["p_raw"] - (f["pr_reward"] - f["pr_stigma"] - f["pr_exit"])))
                                              for h, f in zip(hs, fx)]))}
    rec["stay"] = {c: sum(1 for _, rd in readings for r in "AB" if rd[r]["verdict"] == c) for c in PR.STAY_CLASSES}
    return rec


def task(args):
    arm, a, b, seeds, stay = args
    t0 = time.time()
    out = []
    for s in seeds:
        run, lived, rd = play(ARMS[arm], a, b, s, stay=stay)
        out.append(record(run, lived, rd, arm, a, b, s))
    return out, time.time() - t0


def run(cfg, f, arms, workers=WORKERS, stay=True):
    workers = min(workers, 3)
    OUT.mkdir(parents=True, exist_ok=True)
    done = set()
    if f.exists():
        for x in f.read_text().splitlines():
            r = json.loads(x)
            done.add((r["arm"], r["a"], r["b"]))
    tasks = [(arm, a, b, cfg["seeds"], stay) for (a, b) in pairings(cfg) for arm in arms if (arm, a, b) not in done]
    print(f"{len(tasks)} tasks, {workers} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, f.open("a") as fh:
        for i, (rows, dt) in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            fh.write("\n".join(json.dumps(r) for r in rows) + "\n")
            fh.flush()
            if i % 25 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {dt:.1f}s wall {time.time() - t0:.0f}s", flush=True)


# ---- analysis -----------------------------------------------------------------------------------------------------------------

def load(f):
    return [json.loads(x) for x in f.read_text().splitlines() if x.strip()]


def per_pair(rows, arm, key):
    """-> {(a, b): mean over seeds of key(rec)} for one arm; key is a callable; None values dropped."""
    acc = {}
    for r in rows:
        if r["arm"] != arm:
            continue
        v = key(r)
        if v is not None:
            acc.setdefault((r["a"], r["b"]), []).append(v)
    return {k: float(np.mean(v)) for k, v in acc.items()}


def paired(rows, arm, base, key):
    x, y = per_pair(rows, arm, key), per_pair(rows, base, key)
    ks = sorted(set(x) & set(y))
    return np.array([x[k] - y[k] for k in ks]), ks


def boot_ci(d, n=4000, seed=0):
    rng = np.random.default_rng(seed)
    bs = [np.mean(d[rng.integers(0, len(d), len(d))]) for _ in range(n)]
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def signflip_p(d, alternative, n=10000, seed=0):
    """One-sided paired sign-flip permutation p. alternative: "greater" (mean > 0) or "less"."""
    rng = np.random.default_rng(seed)
    obs = d.mean()
    flips = rng.choice([-1.0, 1.0], size=(n, len(d)))
    null = (flips * d).mean(axis=1)
    if alternative == "greater":
        return float((np.sum(null >= obs) + 1) / (n + 1))
    return float((np.sum(null <= obs) + 1) / (n + 1))


def role_values(rows, arm, field_, v=None):
    """-> {(a, b, role): mean over seeds of rec[role][field_]} for roles with values-pairing v (all if None)."""
    acc = {}
    for r in rows:
        if r["arm"] != arm:
            continue
        for role in "AB":
            if v is not None and r[role]["v"] != v:
                continue
            x = r[role][field_]
            if x is not None:
                acc.setdefault((r["a"], r["b"], role), []).append(x)
    return {k: float(np.mean(x)) for k, x in acc.items()}


def p4_stat(rows, hi="L4", lo="L0", field_="pl"):
    """Delta (hi - lo) pleasure for v=0 agents minus for v=1 agents; cluster bootstrap by pairing. -> (est, ci, p_less)."""
    def deltas(v):
        a, b = role_values(rows, hi, field_, v), role_values(rows, lo, field_, v)
        out = {}
        for k in set(a) & set(b):
            out.setdefault(k[:2], []).append(a[k] - b[k])
        return out
    d0, d1 = deltas(0.0), deltas(1.0)
    pairs = sorted(set(d0) | set(d1))

    def est(idx):
        x0 = [v for i in idx for v in d0.get(pairs[i], [])]
        x1 = [v for i in idx for v in d1.get(pairs[i], [])]
        return np.mean(x0) - np.mean(x1)
    e = est(range(len(pairs)))
    rng = np.random.default_rng(1)
    bs = np.array([est(rng.integers(0, len(pairs), len(pairs))) for _ in range(4000)])
    return float(e), (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))), float((np.sum(bs >= 0) + 1) / (len(bs) + 1))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run_max = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        run_max = max(run_max, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run_max
    return adj


def mean_of(rows, arm, key):
    return float(np.mean(list(per_pair(rows, arm, key).values())))


KEYS = {
    "pleasure": lambda r: r["pl"],
    "net": lambda r: r["net"],
    "s_non": lambda r: r["snon"],
    "together_share": lambda r: r["both_share"],
    "formed0": lambda r: float(r["formed0"]),
    "ever_formed": lambda r: float(r["ever_formed"]),
    "ended_if_formed": lambda r: float(r["ended"]) if r["ever_formed"] else None,
    "leaves": lambda r: r["leaves"],
    "friends_per_week": lambda r: np.mean([r[x]["friends"] for x in "AB"]),
    "friends_while_together": lambda r: (np.mean([r[x]["friends_tog"] for x in "AB" if r[x]["friends_tog"] is not None])
                                         if any(r[x]["friends_tog"] is not None for x in "AB") else None),
    "c_friend": lambda r: np.mean([r[x]["c_friend"] for x in "AB"]),
    "direct_terms": lambda r: np.mean([r[x]["reward"] - r[x]["stigma"] - r[x]["exit"] for x in "AB"]),
    "pleasure_wo_direct": lambda r: np.mean([r[x]["p_nopress"] for x in "AB"]),
    "p_raw": lambda r: np.mean([r[x]["p_raw"] for x in "AB"]),
    "clipped_share": lambda r: np.mean([r[x]["clipped"] for x in "AB"]),
    "held_share": lambda r: (r["stay"]["held"] / sum(r["stay"].values())) if sum(r["stay"].values()) else None,
    "worth_share": lambda r: (r["stay"]["worth"] / sum(r["stay"].values())) if sum(r["stay"].values()) else None,
}


def table(rows, arms):
    return {arm: {k: mean_of(rows, arm, f) for k, f in KEYS.items()} for arm in arms if any(r["arm"] == arm for r in rows)}


def verdicts(rows, key="pleasure"):
    """The prereg's primary family on `rows` (confirmatory or synthetic). key: the pleasure measure (Amendment 1: "p_raw", unclipped,
    as a sensitivity line). -> dict."""
    lv = [f"L{x:g}" for x in LEVELS]
    means = {a: mean_of(rows, a, KEYS[key]) for a in lv}
    star = max(lv, key=lambda a: means[a])
    out = {"means": means, "L_star": star}
    d1, _ = paired(rows, star, "L0", KEYS[key]) if star != "L0" else (np.zeros(2), None)
    p1 = signflip_p(d1, "greater") if star != "L0" else 1.0
    d2, _ = paired(rows, "L4", "L0", KEYS[key])
    d3a, _ = paired(rows, "L4", "L0", KEYS["together_share"])
    d3b, _ = paired(rows, "L4", "L0", KEYS["ended_if_formed"])
    p4e, p4ci, p4p = p4_stat(rows, field_="p_raw" if key == "p_raw" else "pl")
    raw = [p1, signflip_p(d2, "less"), max(signflip_p(d3a, "greater"), signflip_p(d3b, "less") if len(d3b) else 1.0), p4p]
    adj = holm(raw)
    out["P1"] = {"L_star_low": star in ("L0.5", "L1"), "est": float(d1.mean()), "ci": boot_ci(d1) if star != "L0" else None,
                 "p_holm": adj[0]}
    out["P2"] = {"est": float(d2.mean()), "ci": boot_ci(d2), "p_holm": adj[1]}
    out["P3"] = {"together": float(d3a.mean()), "together_ci": boot_ci(d3a), "ended": float(d3b.mean()) if len(d3b) else None,
                 "ended_ci": boot_ci(d3b) if len(d3b) else None, "n_ended_pairs": len(d3b), "p_holm": adj[2]}
    out["P4"] = {"est": p4e, "ci": p4ci, "p_holm": adj[3]}
    h = {
        "P1": out["P1"]["L_star_low"] and out["P1"]["est"] > 0 and out["P1"]["ci"] is not None and out["P1"]["ci"][0] > 0 and adj[0] < 0.05,
        "P2": out["P2"]["est"] < 0 and out["P2"]["ci"][1] < 0 and adj[1] < 0.05,
        "P3": (out["P3"]["together"] > 0 and out["P3"]["together_ci"][0] > 0 and out["P3"]["ended"] is not None and out["P3"]["ended"] < 0
               and out["P3"]["ended_ci"][1] < 0 and adj[2] < 0.05),
        "P4": out["P4"]["est"] < 0 and out["P4"]["ci"][1] < 0 and adj[3] < 0.05,
    }
    out["holds"] = h
    out["verdict"] = ("supported" if all(h.values()) else "partly supported" if (h["P2"] and (h["P3"] or h["P4"])) else "not supported")
    return out


def split_by_v(rows, arms):
    out = {}
    for arm in arms:
        if not any(r["arm"] == arm for r in rows):
            continue
        out[arm] = {}
        for v in PR.V_LEVELS:
            out[arm][str(v)] = {f: float(np.mean(list(role_values(rows, arm, f, v).values()))) for f in ("pl", "net", "together", "snon",
                                                                                                      "friends", "p_raw")}
    return out


def pushed_in(rows, hi="L4", lo="L0"):
    """S1: pair-seeds that decline at week 0 under lo but form at week 0 under hi: their pleasure hi minus lo."""
    idx = {(r["arm"], r["a"], r["b"], r["seed"]): r for r in rows}
    ds, ds_v = [], {str(v): [] for v in PR.V_LEVELS}
    for (arm, a, b, s), r in idx.items():
        if arm != lo or r["formed0"]:
            continue
        h = idx.get((hi, a, b, s))
        if h and h["formed0"]:
            ds.append(h["pl"] - r["pl"])
            for x in "AB":
                ds_v[str(h[x]["v"])].append(h[x]["pl"] - r[x]["pl"])
    n_lo = sum(1 for (arm, *_), r in idx.items() if arm == lo)
    return {"n": len(ds), "of": n_lo, "mean_delta": float(np.mean(ds)) if ds else None,
            "by_v": {k: (float(np.mean(v)) if v else None) for k, v in ds_v.items()}}


def analyze(f, label):
    rows = load(f)
    arms = [a for a in ARMS if any(r["arm"] == a for r in rows)]
    res = {"label": label, "n_rows": len(rows), "n_pairings": len({(r["a"], r["b"]) for r in rows}), "table": table(rows, arms),
           "by_v": split_by_v(rows, arms), "pushed_in": {hi: pushed_in(rows, hi) for hi in ("L1", "L2", "L4", "S4", "R4")
                                                         if any(r["arm"] == hi for r in rows)}}
    if all(any(r["arm"] == f"L{x:g}" for r in rows) for x in LEVELS):
        res["verdicts"] = verdicts(rows)
        res["verdicts_unclipped"] = verdicts(rows, key="p_raw")
    res["vs_L0"] = {}
    for arm in arms:
        if arm == "L0":
            continue
        res["vs_L0"][arm] = {}
        for k in ("pleasure", "net", "s_non", "together_share", "pleasure_wo_direct", "friends_per_week", "p_raw"):
            d, _ = paired(rows, arm, "L0", KEYS[k])
            if len(d):
                res["vs_L0"][arm][k] = {"est": float(d.mean()), "ci": boot_ci(d), "sd": float(d.std(ddof=1))}
    return res


def show(res):
    print(f"{res['label']}: {res['n_rows']} rows, {res['n_pairings']} pairings")
    cols = ("pleasure", "net", "s_non", "together_share", "formed0", "ended_if_formed", "leaves", "friends_per_week",
            "friends_while_together", "held_share", "worth_share", "pleasure_wo_direct", "p_raw", "clipped_share")
    print("arm    " + " ".join(f"{c[:10]:>10s}" for c in cols))
    for arm, t in res["table"].items():
        print(f"{arm:6s} " + " ".join(f"{t[c]:10.4f}" for c in cols))
    print("vs L0 (pleasure; net; pleasure without direct terms):")
    for arm, d in res["vs_L0"].items():
        print(f"  {arm:6s} " + "  ".join(f"{k} {v['est']:+.4f} [{v['ci'][0]:+.4f},{v['ci'][1]:+.4f}] sd {v['sd']:.4f}"
                                        for k, v in d.items() if k in ("pleasure", "net", "pleasure_wo_direct")))
    print("by v (pleasure):")
    for arm, d in res["by_v"].items():
        print(f"  {arm:6s} " + "  ".join(f"v{k} pl {x['pl']:.4f} tog {x['together']:.3f}" for k, x in d.items()))
    print("pushed in:", json.dumps(res["pushed_in"]))
    if "verdicts" in res:
        print("verdicts:", json.dumps(res["verdicts"], indent=1))


# ---- reachability (prereg "Can every verdict happen?") ------------------------------------------------------------------------

def synthetic(curve, n=40, sd=0.01, v_slope=0.0, together_up=True, ended_down=True, seed=0):
    """Synthetic records with a given mean pleasure per dial level (for the verdict function only)."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        base = rng.normal(0.85, 0.03)
        for j, lv in enumerate(LEVELS):
            arm = f"L{lv:g}"
            for s in (0, 1):
                pl = base + curve[j] + rng.normal(0, sd)
                rec = {"arm": arm, "a": f"a{i}", "b": f"b{i}", "seed": s, "pl": pl,
                       "both_share": 0.3 + (0.05 * j if together_up else -0.05 * j) + rng.normal(0, 0.01),
                       "ever_formed": True, "ended": bool(rng.random() < (0.5 - 0.08 * j if ended_down else 0.2 + 0.08 * j))}
                for x, v in (("A", 0.0), ("B", 1.0)):
                    rec[x] = {"v": v, "pl": pl + (v_slope * j if v == 0.0 else 0.0)}
                rows.append(rec)
    return rows


def reach():
    print("Reachability on synthetic records (verdict function):")
    cases = {
        "peak at L0.5, high hurts, low valuers bear it": dict(curve=[0, 0.01, 0.005, -0.01, -0.03], v_slope=-0.01),
        "negation: peak at L0 (monotone harm)": dict(curve=[0, -0.005, -0.01, -0.02, -0.04], v_slope=-0.01),
        "negation: peak at L4 (monotone help)": dict(curve=[0, 0.005, 0.01, 0.02, 0.04], v_slope=0.0),
        "P3 fails (together falls)": dict(curve=[0, 0.01, 0.005, -0.01, -0.03], v_slope=-0.01, together_up=False),
        "P3 fails (more endings)": dict(curve=[0, 0.01, 0.005, -0.01, -0.03], v_slope=-0.01, ended_down=False),
        "P4 fails (high valuers bear it)": dict(curve=[0, 0.01, 0.005, -0.01, -0.03], v_slope=+0.01),
    }
    out = {}
    for name, kw in cases.items():
        v = verdicts(synthetic(**kw))
        out[name] = {"L_star": v["L_star"], "holds": v["holds"], "verdict": v["verdict"]}
        print(f"  {name}: L* {v['L_star']}, holds {v['holds']}, verdict {v['verdict']}")
    return out


def liberty_sub():
    """S8: liberty with powers on the 15 hand pairings, seed 0, L0 and L4 (and each part alone at L4)."""
    memo, out = {}, {}
    hand = [p for p in RT.sample(0, 38)]
    for arm in ("L0", "L4", "S4", "R4", "W4", "X4"):
        vals = []
        for a, b in hand:
            run, _, _ = play(ARMS[arm], a, b, 0, stay=False, liberty=memo)
            vals.append(float(np.mean(run.liberty)))
        out[arm] = {"mean": float(np.mean(vals)), "per_pair": vals}
        print(f"  liberty {arm}: {out[arm]['mean']:.4f}", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "liberty.json").write_text(json.dumps(out, indent=1))
    return out


def _reach_comp(L):
    """A withdrawal-heavy composition (reward only, withdrawal 0.45 per level, cap 0.9): the free model-level check that a peak at a
    low level is reachable in this world, not only in the verdict function."""
    return dataclasses.replace(PR.dial(L, parts=("reward",)), withdraw=min(0.9, 0.45 * L))


def _reach_one(args):
    L, a, b = args
    run, _, _ = play(_reach_comp(L), a, b, 950, stay=False)
    return L, float(np.mean([[o["hedonic"][r]["pleasure"] for r in "AB"] for o in run.outcomes]))


def reach_model():
    import random
    pairs = random.Random(901).sample(RT.population(), 12)
    with Pool(3) as p:
        res = p.map(_reach_one, [(L, a, b) for L in (0, 0.5, 1, 2) for a, b in pairs])
    out = {L: float(np.mean([x for lv, x in res if lv == L])) for L in (0, 0.5, 1, 2)}
    print("model-level reachability (withdrawal-heavy composition, 12 pairings, seed 950):", out)
    return out


def extras(f=OUT / "rows.jsonl"):
    """Descriptive extras for the results file: per-agent change by values-pairing (losers), pushed-in pairs net and without the
    direct terms, households formed at L0, stay-lens class shares. -> dict (also printed)."""
    rows = load(f)
    idx = {(r["arm"], r["a"], r["b"], r["seed"]): r for r in rows}

    def agent(arm):
        d = {}
        for (a_, x, y, s), r in idx.items():
            if a_ == arm:
                for R, pid in (("A", x), ("B", y)):
                    d.setdefault((pid, x, y, R), []).append(r[R])
        return d
    out = {"by_v": {}, "pushed_in": {}, "stay": {}}
    L0 = agent("L0")
    for arm in [a for a in ARMS if a != "L0"]:
        H_ = agent(arm)
        out["by_v"][arm] = {}
        for v in PR.V_LEVELS:
            ks = [k for k in L0 if L0[k][0]["v"] == v]
            dl = np.array([np.mean([h["pl"] for h in H_[k]]) - np.mean([h["pl"] for h in L0[k]]) for k in ks])
            dn = np.array([np.mean([h["net"] for h in H_[k]]) - np.mean([h["net"] for h in L0[k]]) for k in ks])
            st = float(np.mean([np.mean([h["stigma"] + h["exit"] for h in H_[k]]) for k in ks]))
            out["by_v"][arm][str(v)] = {"d_pl": float(dl.mean()), "losers_0.01": float(np.mean(dl < -0.01)), "d_net": float(dn.mean()),
                                        "stigma_exit_paid": st, "n_agents": len(ks)}
    for hi in ("L0.5", "L1", "L2", "L4", "L8", "S4", "R4"):
        d, dn, dw = [], [], []
        for (arm, a, b, s), r in idx.items():
            if arm == "L0" and not r["formed0"]:
                h = idx[(hi, a, b, s)]
                if h["formed0"]:
                    d.append(h["pl"] - r["pl"]); dn.append(h["net"] - r["net"])
                    dw.append(np.mean([h[x]["p_nopress"] for x in "AB"]) - np.mean([r[x]["p_nopress"] for x in "AB"]))
        out["pushed_in"][hi] = {"n": len(d), "d_pl": float(np.mean(d)), "d_net": float(np.mean(dn)), "d_pl_wo_direct": float(np.mean(dw)),
                                "share_worse": float(np.mean(np.array(d) < 0))}
    d = [idx[("L4", a, b, s)]["pl"] - r["pl"] for (arm, a, b, s), r in idx.items() if arm == "L0" and r["formed0"]]
    out["formed_at_L0_L4_minus_L0"] = {"n": len(d), "d_pl": float(np.mean(d))}
    for arm in ARMS:
        t = {c: sum(r["stay"][c] for r in rows if r["arm"] == arm) for c in PR.STAY_CLASSES}
        n = sum(t.values())
        out["stay"][arm] = {**{c: v / n for c, v in t.items()}, "readings": n}
    print(json.dumps(out, indent=1))
    (OUT / "extras.json").write_text(json.dumps(out, indent=1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--reach", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--liberty", action="store_true")
    ap.add_argument("--extras", action="store_true")
    ap.add_argument("--workers", type=int, default=WORKERS)
    a = ap.parse_args()
    if a.reach:
        reach()
        reach_model()
    if a.pilot:
        f = OUT / "pilot.jsonl"
        run(PILOT, f, list(ARMS), a.workers)
        res = analyze(f, "PILOT (EXPLORATORY; not a result)")
        show(res)
        (OUT / "pilot_analysis.json").write_text(json.dumps(res, indent=1))
    if a.run:
        run(CONFIRM, OUT / "rows.jsonl", list(ARMS), a.workers)
    if a.extras:
        extras()
    if a.liberty:
        liberty_sub()
    if a.analyze:
        res = analyze(OUT / "rows.jsonl", "CONFIRMATORY")
        show(res)
        (OUT / "analysis.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
