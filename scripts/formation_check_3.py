"""Formation check, third run (docs/results/formation-check-3-prereg.md): H38's pairing pressure in the formation check's household with
bills that hurt, the saturating pleasure scale and the corrected rule, under four agent sets side by side (v1, v2, v2b, hybrid). Held share
and liberty lead; then pleasure, lived pleasure (reward and stigma taken out), withdrawal, the worse-off partner, weeks near the top, and
the old capped line. A sign that differs across agent sets is reported as agent-dependent (the stop rule) and nothing is patched.
Scripted persona agents, no model calls. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

  uv run python scripts/formation_check_3.py --reach      "Can every verdict happen?": synthetic verdicts and stop rule, the P2 probe
                                                          and the stay test's trap (free; pilot pairings, no confirmatory rows)
  uv run python scripts/formation_check_3.py --run        the confirmatory run (at most 4 workers); rows in runs/formation-check-3/
  uv run python scripts/formation_check_3.py --analyze    prereg vs actual; writes runs/formation-check-3/analysis.json

Time together is valued at the world's satiety (satiety_expect="world") under v2, v2b and the hybrid (hybrid-agent-prereg.md,
Amendment 2; formation-check-3-prereg.md, Amendment 1). v1 keeps its own heuristics and does not read the flag.
"""
import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import h38_pairing_run as H38  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import pairing as PR  # noqa: E402

OUT = ROOT / "runs" / "formation-check-3"
WORKERS = 4
WORLD = {"decide_on": "pleasure", "decide_weeks": 52, "bills_hurt": True, "pleasure_scale": "sat", "satiety_expect": "world"}
SETS = {"v1": {}, "v2": {"agent_values": "v2"}, "v2b": {"agent_values": "v2b"}, "hybrid": {"agent_values": "hybrid"}}
ARMS = {"G-L0": PR.dial(0), "G-L4": PR.dial(4), "G-W4": PR.dial(4, parts=("withdraw",))}
KNEE = 0.8
TOP = 0.95             # ADR 0019: "near the top" on the new scale
MARGIN = 0.007         # P3, carried over from the formation check
BLOCK = 13             # a reading decides the next 13 weeks: the suffering read beside each held / worth reading


def rule(agent_set):
    return {**WORLD, **SETS[agent_set]}


# ---- one run ---------------------------------------------------------------------------------------------------------------------

def record(run, lived, readings, agent_set, arm, a, b, seed):
    """H38's record plus what this prereg reads: liberty, lived pleasure on the new scale, near the top, the worse-off partner, the old
    capped line, suffering, and each stay reading's verdict with the suffering of the block it decides."""
    rec = H38.record(run, lived, readings, f"{agent_set}:{arm}", a, b, seed)
    rec.update(set=agent_set, g=arm)
    outs = run.outcomes
    per = {}
    for r in "AB":
        hs = [o["hedonic"][r] for o in outs]
        fx = [h["fix"] for h in hs]
        direct = [f["pr_reward"] - f["pr_stigma"] - f["pr_exit"] for f in fx]
        per[r] = {"pl": float(np.mean([h["pleasure"] for h in hs])),
                  "lived": float(np.mean([HD.saturate(h["p_raw"] - d, KNEE) for h, d in zip(hs, direct)])),
                  "top": float(np.mean([h["pleasure"] >= TOP for h in hs])),
                  "pclip": float(np.mean([h["p_clip"] for h in hs])),
                  "suff": float(np.mean([h["s_off"] + h["s_non"] for h in hs]))}
        rec[r].update(lived=per[r]["lived"], top=per[r]["top"], pclip=per[r]["pclip"], suff=per[r]["suff"])
    rec["lived"] = float(np.mean([per[r]["lived"] for r in "AB"]))
    rec["top"] = float(np.mean([per[r]["top"] for r in "AB"]))
    rec["pclip"] = float(np.mean([per[r]["pclip"] for r in "AB"]))
    rec["suff"] = float(np.mean([per[r]["suff"] for r in "AB"]))
    rec["worse_off"] = min(per[r]["pl"] for r in "AB")
    rec["liberty"] = list(getattr(run, "liberty", []) or [])
    rec["lib"] = float(np.mean(rec["liberty"])) if rec["liberty"] else None
    rec["readings"] = [{"w": w, "r": r, "v": rd[r]["verdict"],
                        "suff": float(np.mean([o["hedonic"][r]["s_off"] + o["hedonic"][r]["s_non"] for o in outs[w:w + BLOCK]]))}
                       for w, rd in readings for r in "AB"]
    return rec


_LIB = {}             # liberty memo, per worker process


def task(args):
    agent_set, arm, a, b, seeds = args
    t0 = time.time()
    out = []
    for s in seeds:
        run, lived, rd = H38.play(ARMS[arm], a, b, s, stay=True, liberty=_LIB, rule=rule(agent_set))
        out.append(record(run, lived, rd, agent_set, arm, a, b, s))
    return out, time.time() - t0


def run_all(sets, f, workers=WORKERS, pairs=None, seeds=None, arms=None):
    workers = min(workers, 4)
    f.parent.mkdir(parents=True, exist_ok=True)
    done = {(r["set"], r["g"], r["a"], r["b"]) for r in load(f)} if f.exists() else set()
    pairs = pairs if pairs is not None else H38.pairings(H38.CONFIRM)
    seeds = seeds if seeds is not None else H38.CONFIRM["seeds"]
    tasks = [(st, arm, a, b, seeds) for st in sets for (a, b) in pairs for arm in (arms or ARMS) if (st, arm, a, b) not in done]
    print(f"{len(tasks)} tasks, {workers} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, f.open("a") as fh:
        for i, (rows, dt) in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            fh.write("\n".join(json.dumps(r) for r in rows) + "\n")
            fh.flush()
            if i % 25 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {dt:.1f}s wall {time.time() - t0:.0f}s", flush=True)


def load(f):
    return [json.loads(x) for x in Path(f).read_text().splitlines() if x.strip()]


# ---- analysis ----------------------------------------------------------------------------------------------------------------------

def per_pair(rows, arm, key):
    """-> {(a, b): mean over seeds of key(rec)}; None values dropped."""
    acc = {}
    for r in rows:
        if r["g"] == arm:
            v = key(r)
            if v is not None:
                acc.setdefault((r["a"], r["b"]), []).append(v)
    return {k: float(np.mean(v)) for k, v in acc.items()}


def paired(rows, hi, lo, key):
    x, y = per_pair(rows, hi, key), per_pair(rows, lo, key)
    ks = sorted(set(x) & set(y))
    return np.array([x[k] - y[k] for k in ks])


KEYS = {
    "pleasure": lambda r: r["pl"],
    "lived": lambda r: r["lived"],
    "top": lambda r: r["top"],
    "worse_off": lambda r: r["worse_off"],
    "old_line": lambda r: r["pclip"],
    "liberty": lambda r: r["lib"],
    "net": lambda r: r["net"],
    "suffering": lambda r: r["suff"],
    "formed0": lambda r: float(r["formed0"]),
    "together": lambda r: r["both_share"],
    "ended_if_formed": lambda r: float(r["ended"]) if r["ever_formed"] else None,
}
DESCRIPTIVE = ("formed0", "together", "ended_if_formed", "suffering")


def held_share(rows, arm="G-L4", n_boot=4000, seed=0):
    """P1: of all stay readings at the arm (both members, every reading while both are in), the share classed held. Ratio of sums,
    95% percentile bootstrap resampling pairings; p = bootstrap share at or below 0.05 (one-sided, against the interval bar)."""
    acc = {}
    for r in rows:
        if r["g"] == arm:
            n = sum(r["stay"].values())
            h = r["stay"]["held"]
            x = acc.setdefault((r["a"], r["b"]), [0, 0])
            x[0] += h
            x[1] += n
    ks = sorted(acc)
    h = np.array([acc[k][0] for k in ks], float)
    n = np.array([acc[k][1] for k in ks], float)
    if n.sum() == 0:
        return {"est": None, "ci": None, "readings": 0, "p": 1.0}
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(ks), len(ks))
        bs.append(h[i].sum() / n[i].sum() if n[i].sum() else 0.0)
    bs = np.array(bs)
    return {"est": float(h.sum() / n.sum()), "ci": (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))),
            "readings": int(n.sum()), "pairings_with_readings": int((n > 0).sum()), "p": float((np.sum(bs <= 0.05) + 1) / (n_boot + 1))}


def diff(rows, hi, lo, key, alt=None):
    d = paired(rows, hi, lo, KEYS[key])
    if not len(d):
        return {"est": None, "ci": None, "n": 0}
    o = {"est": float(d.mean()), "ci": H38.boot_ci(d), "n": int(len(d))}
    if alt == "two":
        o["p"] = min(1.0, 2 * min(H38.signflip_p(d, "greater"), H38.signflip_p(d, "less")))
    elif alt:
        o["p"] = H38.signflip_p(d, alt)
    return o


def sign_class(x):
    """The stop rule's class: + (interval above 0), - (interval below 0), 0 (interval includes 0)."""
    if x["ci"] is None:
        return "n/a"
    return "+" if x["ci"][0] > 0 else "-" if x["ci"][1] < 0 else "0"


def p3_outcome(x, p_adj):
    e, (lo, hi) = x["est"], x["ci"]
    if e >= MARGIN and lo > 0 and p_adj < 0.05:
        return "raises"
    if e <= -MARGIN and hi < 0 and p_adj < 0.05:
        return "lowers"
    if abs(e) < MARGIN and lo > -0.015 and hi < 0.015:
        return "within margin"
    return "unclear"


def verdict(p1, p2, p3):
    """The evaluator's rule: pleasure AND freedom. Pressure that holds people in or narrows liberty is at best a trade-off."""
    dom = p1 or p2
    if dom and p3 == "raises":
        return "trade-off"
    if dom and p3 == "lowers":
        return "harm"
    if dom:
        return "not a win"
    if p3 == "raises":
        return "win"
    return "not a win (pleasure not raised)"


def claims(rows):
    """P1 to P4 for one agent set's rows, Holm across the four, classes for the stop rule, and the verdict."""
    p1 = held_share(rows)
    p2 = diff(rows, "G-L4", "G-L0", "liberty", "less")
    p3 = diff(rows, "G-L4", "G-L0", "pleasure", "two")
    p4 = diff(rows, "G-W4", "G-L0", "pleasure", "less")
    ps = [p1["p"], p2.get("p", 1.0), p3.get("p", 1.0), p4.get("p", 1.0)]
    adj = H38.holm(ps)
    hold = {"P1": p1["est"] is not None and p1["est"] >= 0.10 and p1["ci"][0] > 0.05 and adj[0] < 0.05,
            "P2": p2["est"] is not None and p2["est"] < 0 and p2["ci"][1] < 0 and adj[1] < 0.05,
            "P4": p4["est"] is not None and p4["est"] < 0 and p4["ci"][1] < 0 and adj[3] < 0.05}
    out3 = p3_outcome(p3, adj[2]) if p3["est"] is not None else "n/a"
    p2_moves = any(abs(x) > 1e-12 for x in paired(rows, "G-L4", "G-L0", KEYS["liberty"]))
    return {"P1": {**p1, "p_holm": adj[0], "holds": hold["P1"], "class": "n/a" if p1["ci"] is None else
                   ("+" if p1["ci"][0] > 0 else "0")},
            "P2": {**p2, "p_holm": adj[1], "holds": hold["P2"], "class": sign_class(p2), "moves": p2_moves},
            "P3": {**p3, "p_holm": adj[2], "outcome": out3, "class": out3},
            "P4": {**p4, "p_holm": adj[3], "holds": hold["P4"], "class": sign_class(p4)},
            "verdict": verdict(hold["P1"], hold["P2"], out3)}


def stop_rule(per_set):
    """Each claim: 'holds across the agent sets' in one class if every set is in the same class, else 'agent-dependent'."""
    out = {}
    for c in ("P1", "P2", "P3", "P4"):
        cls = {s: per_set[s][c]["class"] for s in per_set}
        same = len(set(cls.values())) == 1
        out[c] = {"classes": cls, "reading": f"holds across the {len(cls)} agent sets ({next(iter(cls.values()))})" if same
                  else "agent-dependent"}
    vs = {s: per_set[s]["verdict"] for s in per_set}
    out["verdict"] = {"by_set": vs, "reading": f"the same under every set ({next(iter(vs.values()))})" if len(set(vs.values())) == 1
                      else "agent-dependent"}
    return out


# The exact model (docs/results/h38-exact-model.md): the corrected chooser's week-0 formation at each household worth, and its sign map
# on the saturating scale (L4 - L0 pleasure, held share). Used to place each set and read the expected sign; nothing here is fitted.
EXACT_FORM = ((0.80, 0.0), (0.40, -0.10), (0.20, -0.15), (0.00, -0.20))
EXACT_SAT = {-0.20: (-0.028, 0.35), -0.15: (-0.017, 0.40), -0.10: (-0.004, 0.42), -0.05: (0.006, 0.35), 0.0: (0.011, 0.19),
             0.05: (0.010, 0.07)}


def place(formed0):
    """Household worth from the no-pressure week-0 formation share, by linear interpolation of the exact chooser's formation; at or
    above 0.80 it is 'worth 0 or more' (the exact model's formation does not rise past 0.80 in the reported cells)."""
    if formed0 >= EXACT_FORM[0][0]:
        return 0.0
    for (f1, w1), (f0, w0) in zip(EXACT_FORM, EXACT_FORM[1:]):
        if f0 <= formed0 <= f1:
            return w0 + (w1 - w0) * (formed0 - f0) / (f1 - f0)
    return -0.20


def expected(formed0):
    """The prereg's expected answer for a set placed by its G-L0 formation share."""
    w = place(formed0)
    ws = sorted(EXACT_SAT)
    lo = max(x for x in ws if x <= w)
    hi = min(x for x in ws if x >= w)
    t = 0.0 if hi == lo else (w - lo) / (hi - lo)
    d = EXACT_SAT[lo][0] + t * (EXACT_SAT[hi][0] - EXACT_SAT[lo][0])
    held = EXACT_SAT[lo][1] + t * (EXACT_SAT[hi][1] - EXACT_SAT[lo][1])
    p3 = ("within margin or raises" if formed0 >= 0.6 else "within margin or lowers" if formed0 <= 0.4 else
          "within margin (the crossing)")
    return {"worth": round(w, 3), "exact_L4_minus_L0": round(d, 4), "exact_held": round(held, 3), "P3": p3, "P1": "held above 0",
            "P4": "withdrawal lowers pleasure", "lived": "lived pleasure lower under pressure"}


def agrees(exp, cl, lived):
    p3 = cl["P3"]["outcome"]
    return {"P1 held above 0": cl["P1"]["class"] == "+",
            "P3 in the expected set": p3 in exp["P3"] or (exp["P3"].startswith("within margin (") and p3 == "within margin"),
            "P4 lowers": cl["P4"]["class"] == "-",
            "lived lower": lived["ci"] is not None and lived["ci"][1] < 0}


def analyze_rows(rows):
    sets = [s for s in SETS if any(r["set"] == s for r in rows)]
    res = {"n_rows": len(rows), "sets": {}}
    for s in sets:
        sr = [r for r in rows if r["set"] == s]
        cl = claims(sr)
        d = {"L4": {k: diff(sr, "G-L4", "G-L0", k) for k in ("pleasure", "lived", "top", "worse_off", "old_line", "net", "suffering",
                                                            "together", "formed0", "liberty")},
             "W4": {k: diff(sr, "G-W4", "G-L0", k) for k in ("pleasure", "lived", "top", "worse_off", "old_line", "together")}}
        means = {arm: {k: float(np.mean(list(per_pair(sr, arm, f).values()))) if per_pair(sr, arm, f) else None for k, f in KEYS.items()}
                 for arm in ARMS}
        susp = {v: [x["suff"] for r in sr if r["g"] == "G-L4" for x in r["readings"] if x["v"] == v] for v in ("held", "worth")}
        f0 = means["G-L0"]["formed0"]
        exp = expected(f0)
        res["sets"][s] = {"claims": cl, "diffs": d, "means": means, "exact": {**exp, "agrees": agrees(exp, cl, d["L4"]["lived"])},
                          "suffering_by_reading": {v: {"n": len(x), "mean": float(np.mean(x)) if x else None} for v, x in susp.items()},
                          "pushed_in": H38.pushed_in([{**r, "arm": r["g"]} for r in sr], "G-L4", "G-L0")}
    res["stop_rule"] = stop_rule({s: res["sets"][s]["claims"] for s in sets})
    return res


def show(res):
    for s, x in res["sets"].items():
        c = x["claims"]
        f = lambda o: "n/a" if o.get("est") is None else f"{o['est']:+.4f} [{o['ci'][0]:+.4f}, {o['ci'][1]:+.4f}]"  # noqa: E731
        print(f"== {s}: formed0 {x['means']['G-L0']['formed0']:.3f}  verdict {c['verdict']}")
        print(f"  P1 held {f(c['P1'])} readings {c['P1']['readings']} holds {c['P1']['holds']}")
        print(f"  P2 liberty {f(c['P2'])} holds {c['P2']['holds']} moves {c['P2']['moves']}")
        print(f"  P3 pleasure {f(c['P3'])} {c['P3']['outcome']}")
        print(f"  lived {f(x['diffs']['L4']['lived'])}  P4 W4 {f(c['P4'])} holds {c['P4']['holds']}")
        print(f"  worse-off {f(x['diffs']['L4']['worse_off'])}  top {f(x['diffs']['L4']['top'])}  old line {f(x['diffs']['L4']['old_line'])}")
        print(f"  exact {x['exact']}")
    print(json.dumps(res["stop_rule"], indent=1))


def analyze(f=OUT / "rows.jsonl"):
    res = analyze_rows(load(f))
    show(res)
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    return res


# ---- "Can every verdict happen?" (free; no confirmatory rows) -----------------------------------------------------------------------

def synthetic(spec, n=40, seed=0):
    """Rows for one agent set with given effects: spec = {held, lib, pl, w4} (L4 held share, liberty L4 - L0, pleasure L4 - L0,
    pleasure W4 - L0); pairing noise sd 0.01."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        base = rng.normal(0.85, 0.03)
        for arm in ARMS:
            for s in (0, 1):
                pl = base + (spec["pl"] if arm == "G-L4" else spec["w4"] if arm == "G-W4" else 0.0) + rng.normal(0, 0.01)
                lib = 0.6 + (spec["lib"] if arm == "G-L4" else 0.0) + rng.normal(0, 0.005)
                h = int(round(8 * spec["held"])) if arm == "G-L4" else 0
                rows.append({"set": "syn", "g": arm, "a": f"a{i}", "b": f"b{i}", "seed": s, "pl": pl, "lived": pl, "top": 0.5,
                             "worse_off": pl, "pclip": pl, "lib": lib, "net": pl, "suff": 0.1, "formed0": True, "both_share": 0.9,
                             "ended": False, "ever_formed": True, "readings": [],
                             "stay": {"worth": 8 - h, "held": h, "pushed_out": 0, "leave": 0}})
    return rows


def reach_verdicts():
    cases = {"trade-off (held, pleasure up)": {"held": 0.3, "lib": 0.0, "pl": 0.02, "w4": -0.01},
             "harm (held, pleasure down)": {"held": 0.3, "lib": 0.0, "pl": -0.02, "w4": -0.01},
             "not a win (held, pleasure flat)": {"held": 0.3, "lib": 0.0, "pl": 0.0, "w4": -0.01},
             "not a win (liberty narrowed only)": {"held": 0.0, "lib": -0.02, "pl": 0.0, "w4": -0.01},
             "win (nobody held, liberty kept, pleasure up)": {"held": 0.0, "lib": 0.0, "pl": 0.02, "w4": 0.0},
             "P3 unclear (estimate past the margin, wide interval)": {"held": 0.0, "lib": 0.0, "pl": 0.008, "w4": 0.0}}
    out = {}
    for name, spec in cases.items():
        rows = synthetic(spec)
        if "unclear" in name:
            for r in rows:
                if r["g"] == "G-L4":
                    r["pl"] += 0.06 * (1 if int(r["a"][1:]) % 2 else -1)
        cl = claims(rows)
        out[name] = {"verdict": cl["verdict"], "P1": cl["P1"]["holds"], "P2": cl["P2"]["holds"], "P3": cl["P3"]["outcome"],
                     "P4": cl["P4"]["holds"]}
        print(f"  {name}: {out[name]}")
    same = {s: claims(synthetic({"held": 0.3, "lib": 0.0, "pl": 0.02, "w4": -0.01}, seed=i)) for i, s in enumerate(SETS)}
    opp = dict(same)
    opp["v2"] = claims(synthetic({"held": 0.3, "lib": 0.0, "pl": -0.02, "w4": -0.01}, seed=9))
    out["stop rule, matching classes"] = stop_rule(same)
    out["stop rule, one set opposite on pleasure"] = stop_rule(opp)
    print("  stop rule, matching:", json.dumps(out["stop rule, matching classes"]["P3"]))
    print("  stop rule, opposite:", json.dumps(out["stop rule, one set opposite on pleasure"]["P3"]))
    return out


PROBE = {"sample_seed": 900, "n_other": 30, "seeds": (900,)}      # H38's pilot pairings and seed: never confirmatory


def reach_probe(workers=WORKERS):
    """The P2 probe (prereg: count the open cells on a 10-pairing free probe) and P1's failing case (G-L0's lens read as if it were L4),
    under every agent set, on 10 pilot pairings at seed 900. Writes runs/formation-check-3/probe.jsonl. Only liberty and the stay
    classes are read here."""
    f = OUT / "probe.jsonl"
    pairs = H38.pairings(PROBE)[:10]
    run_all(list(SETS), f, workers, pairs=pairs, seeds=PROBE["seeds"], arms=("G-L0", "G-L4"))
    rows = load(f)
    out = {}
    for s in SETS:
        sr = [r for r in rows if r["set"] == s]
        d = paired(sr, "G-L4", "G-L0", KEYS["liberty"])
        lib = {arm: [r["liberty"] for r in sr if r["g"] == arm] for arm in ("G-L0", "G-L4")}
        out[s] = {"liberty_cells_differ": int(np.sum(np.abs(d) > 1e-12)), "pairings": int(len(d)),
                  "liberty_values_L0": sorted({round(x, 4) for v in lib["G-L0"] for x in v}),
                  "liberty_values_L4": sorted({round(x, 4) for v in lib["G-L4"] for x in v}),
                  "held_at_G-L0_read_as_L4": held_share(sr, "G-L0")["est"],
                  "secs": None}
        print(f"  {s}: {out[s]}")
    return out


def _trap_one(args):
    """The stay test's built trap (and its baseline) on the new world under one agent set: imposed household, no negotiation."""
    import dataclasses
    from mar import exit_fallback as EF  # noqa: F401
    from mar import retest as RT
    from mar import stay_test as ST
    from mar.worlds import household as H
    sys.path.insert(0, str(ROOT / "scripts"))
    import stay_test_run as STR
    agent_set, arm, a, b, seed = args
    ps = STR.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **rule(agent_set))
    try:
        with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
            world = H.WeeklyWorld(H.PyGate(H.load_variant(arm)), (ps[a], ps[b]), seed, H.WEEKS)
            _, weeks = ST.play_with_stay_test(world, bar=False)
    except Exception as e:                                          # noqa: BLE001
        return {"set": agent_set, "arm": arm, "a": a, "b": b, "error": f"{type(e).__name__}: {e}"}
    rec = STR.compact(weeks)
    flags = STR.held_week_flags(rec)
    return {"set": agent_set, "arm": arm, "a": a, "b": b, "staying": len(flags), "held": int(sum(flags))}


def reach_trap(workers=WORKERS, n_pairs=12):
    """Known-answer case: held-by-cost share in the trap against the baseline fixture, per agent set (12 hand pairings, seed 900)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import stay_test_run as STR
    pairs = [(a, b) for a, b, c in STR.pairings() if c == "ctl"][:n_pairs]
    tasks = [(s, arm, a, b, 900) for s in SETS for arm in ("trap", "baseline") for a, b in pairs]
    with Pool(min(workers, 4)) as p:
        recs = p.map(_trap_one, tasks, chunksize=1)
    out = {}
    for s in SETS:
        out[s] = {}
        for arm in ("trap", "baseline"):
            xs = [r for r in recs if r["set"] == s and r["arm"] == arm]
            err = [r["error"] for r in xs if "error" in r]
            ok = [r for r in xs if "error" not in r]
            n, h = sum(r["staying"] for r in ok), sum(r["held"] for r in ok)
            out[s][arm] = {"held_share": (h / n) if n else None, "staying_weeks": n, "runs": len(ok), "errors": err[:2]}
        print(f"  {s}: {out[s]}")
    return out


LENS_DIAL = 20         # exit stigma alone at 0.02 x 20 = 0.40 a week for 26 weeks: a wall no household's gain clears (ASSUMED)


def _lens_one(args):
    agent_set, arm, a, b, seed = args
    pc = PR.dial(LENS_DIAL, parts=("exit",)) if arm == "X20" else PR.dial(0)
    run, lived, rd = H38.play(pc, a, b, seed, stay=True, decline=False, rule=rule(agent_set))
    return {"set": agent_set, "arm": arm, "a": a, "b": b, "stay": {c: sum(1 for _, x in rd for r in "AB" if x[r]["verdict"] == c)
                                                                    for c in PR.STAY_CLASSES}}


def reach_lens(workers=WORKERS):
    """Supplementary known answer for the stay lens itself (formation-check-3-prereg.md, Amendment 1): formation forced at week 0, exit
    stigma alone at dial 20 against no pressure, 10 pilot pairings, seed 900, every agent set. Held must be well above 0 with the wall
    and 0 without it."""
    pairs = H38.pairings(PROBE)[:10]
    tasks = [(s, arm, a, b, 900) for s in SETS for arm in ("X20", "L0") for a, b in pairs]
    with Pool(min(workers, 4)) as p:
        recs = p.map(_lens_one, tasks, chunksize=1)
    out = {}
    for s in SETS:
        out[s] = {}
        for arm in ("X20", "L0"):
            t = {c: sum(r["stay"][c] for r in recs if r["set"] == s and r["arm"] == arm) for c in PR.STAY_CLASSES}
            n = sum(t.values())
            out[s][arm] = {"held_share": (t["held"] / n) if n else None, "readings": n}
        print(f"  {s}: {out[s]}")
    return out


def reach(workers=WORKERS):
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    print("Synthetic verdicts and stop rule:")
    res = {"verdicts": reach_verdicts()}
    print("P2 probe and P1's failing case (10 pilot pairings, seed 900):")
    res["probe"] = reach_probe(workers)
    print("Known answer: the stay test's trap on the new world:")
    res["trap"] = reach_trap(workers)
    print("Supplementary known answer for the stay lens (exit stigma wall, formation forced):")
    res["lens"] = reach_lens(workers)
    res["secs"] = round(time.time() - t0)
    (OUT / "reach.json").write_text(json.dumps(res, indent=1, default=str))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reach", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--sets", default=",".join(SETS), help="agent sets to run, in order (default: all four)")
    ap.add_argument("--workers", type=int, default=WORKERS)
    a = ap.parse_args()
    if a.reach:
        reach(a.workers)
    if a.run:
        run_all([s for s in a.sets.split(",") if s], OUT / "rows.jsonl", a.workers)
    if a.analyze:
        analyze()


if __name__ == "__main__":
    main()
