"""H39 makers (docs/results/h39-makers-prereg.md): six crediting rules for making, and negotiated protection of long projects, in the
H38 household (F4, items V2, pairing dial 0) with makers on and the per-persona suffering-weight decision rule. Scripted persona
agents, no model calls. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

  uv run python scripts/h39_makers_run.py --pilot      EXPLORATORY (pilot pairings, seeds 900-901; never cited as a result)
  uv run python scripts/h39_makers_run.py --power      the power check on the pilot rows
  uv run python scripts/h39_makers_run.py --reach      the free checks for "Can every verdict happen?"
  uv run python scripts/h39_makers_run.py --run        the confirmatory and descriptive arms (at most 3 workers)
  uv run python scripts/h39_makers_run.py --analyze    prereg vs actual; writes runs/h39-makers/analysis.json
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
from mar import makers as MK  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar import stats as ST  # noqa: E402

OUT = ROOT / "runs" / "h39-makers"
WORKERS = 3
RULE_W = {"decide_on": "weighted", "decide_weeks": 52}       # main: per-persona suffering weight w, 52 weeks
RULE_0 = {"decide_on": "pleasure", "decide_weeks": 52}       # sensitivity: w = 0 for everyone (the H38 corrected rule)
RULE_NET = None                                               # sensitivity: the old net rule (w = 1, 26 weeks)
CONFIRM_ARMS = {"Z": ("zero", "off"), "H": ("hours", "off"), "P": ("pleasure", "off"), "BP": ("bp", "off"), "G": ("gift", "off"),
                "A": ("agreed", "off"), "BP-PN": ("bp", "negotiated")}
DESC_ARMS = {"BP-PI": ("bp", "imposed"), "M0": None, "Z-w0": ("zero", "off"), "BP-w0": ("bp", "off"), "Z-net": ("zero", "off"),
             "BP-net": ("bp", "off")}
ARMS = {**CONFIRM_ARMS, **DESC_ARMS}
PILOT_ARMS = ("Z", "H", "P", "BP", "BP-PN")
MARGIN = 0.003
BASE_OVERRIDES = {}      # H39b (scripts/h39b_makers_rerun.py) sets the opportunity choice here for the main process; workers get it in task args


def arm_setup(arm, overrides=None):
    spec = ARMS[arm]
    rule = RULE_0 if arm.endswith("-w0") else RULE_NET if arm.endswith("-net") else RULE_W
    cfg = None if spec is None else MK.config(spec[0], protect=spec[1], **{**BASE_OVERRIDES, **(overrides or {})})
    return cfg, rule


def play(arm, a, b, seed, overrides=None, weeks=None, recorder=None, fix=None):
    """fix: extra FixConfig fields (agent recalibration: {"agent_values": "v2", "bills_hurt": True}); None is the run as preregistered."""
    cfg, rule = arm_setup(arm, overrides)
    if fix:
        rule = {**(rule or {}), **fix}
    with MK.use_makers(cfg):
        kw = {"weeks": weeks} if weeks else {}
        run, lived, rd = H38.play(PR.dial(0), a, b, seed, stay=False, rule=rule, **kw)
    return run, lived, rd


def record(run, lived, arm, a, b, seed):
    rec = H38.record(run, lived, [], arm, a, b, seed)
    rec["p_raw"] = float(np.mean([rec[r]["p_raw"] for r in "AB"]))
    rec["together"] = float(np.mean([o["both_in"] for o in run.outcomes]))
    w = lived.world
    st = w.makers
    if st is None:
        return rec
    tr = st["traits"]
    wt = st["weeks_together"]
    blocks = st["blocks"]
    tot = blocks["A"] + blocks["B"]
    cred = {r: MK.credit(w, r) for r in "AB"}
    ctot = cred["A"] + cred["B"]
    c52 = st["cum52"]
    big = max("AB", key=lambda r: blocks[r])
    from mar import exit_fallback as EF
    sh_with = EF.contribution_share(w, "A", "all")
    saved, w.makers = w.makers, None
    sh_without = EF.contribution_share(w, "A", "all")
    w.makers = saved
    works = st["works"]
    rec["mk"] = {
        "traits": {r: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in tr[r].items()} for r in "AB"},
        "rule": st["rule"], "agreed": st["agreed"]["pick"] if st["agreed"] else None,
        "weeks_together": wt, "blocks": dict(blocks),
        "bpw": tot / (2 * wt) if wt else None,                      # blocks per partner-week while together
        "e0_blocks": st["e0_blocks"], "by_kind": dict(st["by_kind"]),
        "credit": cred, "credit_share": {r: (cred[r] / ctot if ctot > 0 else None) for r in "AB"},
        "liking_given": dict(st["liking_given"]),
        "big": big, "share52": (c52[big] / (c52["A"] + c52["B"]) if c52 and (c52["A"] + c52["B"]) > 0 else None),
        "share_end": (blocks[big] / tot if tot else None),
        "proj": {k: v for k, v in st["proj"].items() if k != "log"}, "proj_log": st["proj"]["log"],
        "paid": sum(1 for x in works if (x["paid_count"] or 0) >= st["cfg"].paid_weeks),
        "f4_share_A": {"with": sh_with, "without": sh_without},
        "pleasure_got": dict(st["pleasure_got"]), "proc_got": dict(st["proc_got"]), "crave_got": dict(st["crave_got"]),
        # H39b measures (also recorded for H39's choice): liking lost to tolerance, wanting trap, liking and wanting received
        "lost_tol": dict(st["lost_tol"]), "like_got": dict(st["like_got"]), "want_got": dict(st["want_got"]),
        "trap_weeks": dict(st["trap_weeks"]), "tol_weeks": dict(st["tol_weeks"]), "weeks_seen": st["weeks_seen"],
        "dec": json.loads(json.dumps(st["dec"])), "choice": st["cfg"].choice,
    }
    return rec


def task(args):
    arm, a, b, seeds, overrides = args[:5]
    fix = args[5] if len(args) > 5 else None
    t0 = time.time()
    out = []
    for s in seeds:
        run, lived, _ = play(arm, a, b, s, overrides, fix=fix)
        out.append(record(run, lived, arm, a, b, s))
    return out, time.time() - t0


def run(arms, pairs, seeds, f, workers=WORKERS, overrides=None, fix=None):
    workers = min(workers, 3)
    OUT.mkdir(parents=True, exist_ok=True)
    done = set()
    if f.exists():
        done = {(r["arm"], r["a"], r["b"]) for r in H38.load(f)}
    tasks = [(arm, a, b, seeds, overrides, fix) for (a, b) in pairs for arm in arms if (arm, a, b) not in done]
    print(f"{len(tasks)} tasks, {workers} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, f.open("a") as fh:
        for i, (rows, dt) in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            fh.write("\n".join(json.dumps(r) for r in rows) + "\n")
            fh.flush()
            if i % 25 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {dt:.1f}s wall {time.time() - t0:.0f}s", flush=True)


# ---- analysis ------------------------------------------------------------------------------------------------------------------

def _mean(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def per_pair(rows, arm, key, keep=None):
    acc = {}
    for r in rows:
        if r["arm"] != arm or (keep and not keep(r)):
            continue
        v = key(r)
        if v is not None:
            acc.setdefault((r["a"], r["b"]), []).append(v)
    return {k: float(np.mean(v)) for k, v in acc.items()}


def paired(rows, hi, lo, key, keep=None):
    x, y = per_pair(rows, hi, key, keep), per_pair(rows, lo, key, keep)
    ks = sorted(set(x) & set(y))
    return np.array([x[k] - y[k] for k in ks]), ks, np.array([x[k] for k in ks]), np.array([y[k] for k in ks])


def comp(rows, hi, lo, key, alt=None, keep=None):
    d, ks, x, y = paired(rows, hi, lo, key, keep)
    if len(d) == 0:
        return {"est": None, "n": 0}
    o = {"est": float(d.mean()), "ci": H38.boot_ci(d), "n": len(ks), "sd": float(d.std(ddof=1)) if len(d) > 1 else None,
         "cliff": float(ST.cliffs_delta(list(x), list(y)))}
    if alt:
        o["p"] = H38.signflip_p(d, alt)
    return o


K = {
    "pleasure": lambda r: r["pl"], "p_raw": lambda r: r["p_raw"], "net": lambda r: r["net"], "formed0": lambda r: float(r["formed0"]),
    "together": lambda r: r["together"], "ended": lambda r: float(r["ended"]),
    "bpw": lambda r: r.get("mk", {}).get("bpw"),
    "e0_share": lambda r: (r["mk"]["e0_blocks"] / sum(r["mk"]["blocks"].values())) if r.get("mk") and sum(r["mk"]["blocks"].values()) else None,
    "started": lambda r: r["mk"]["proj"]["started"] if r.get("mk") else None,
    "completed": lambda r: r["mk"]["proj"]["completed"] if r.get("mk") else None,
    "paid": lambda r: r["mk"]["paid"] if r.get("mk") else None,
}


def _ext_role(r):
    t = r["mk"]["traits"]
    ex = [x for x in "AB" if t[x]["aim"] == "extractive"]
    return ex[0] if len(ex) == 1 else None


def ext_share(r):
    role = _ext_role(r) if r.get("mk") else None
    if role is None:
        return None
    return r["mk"]["credit_share"][role]


def has(pred):
    return lambda r: bool(r.get("mk")) and pred(r["mk"]["traits"])


ONE_EXT = has(lambda t: sum(t[x]["aim"] == "extractive" for x in "AB") == 1)
ANY_EXT = has(lambda t: any(t[x]["aim"] == "extractive" for x in "AB"))
ANY_ART = has(lambda t: any(t[x]["kind"] == "artist" for x in "AB"))
ANY_E0 = has(lambda t: any(t[x].get("e_rank", 0 if t[x]["e"] == 0.0 else 1) == 0 for x in "AB"))   # lowest-enjoyment third


def evens(rows, arm):
    xs = [r for r in rows if r["arm"] == arm and r.get("mk") and r["mk"]["weeks_together"] >= 104 and r["mk"]["share52"] is not None]
    ev = [r["mk"]["share_end"] <= r["mk"]["share52"] - 0.02 for r in xs]
    return {"n": len(xs), "share": float(np.mean(ev)) if ev else None, "k": int(sum(ev)),
            "lopsided_end": float(np.mean([r["mk"]["share_end"] > 0.6 for r in xs])) if xs else None}


def newcombe(k1, n1, k2, n2):
    """Newcombe (1998) hybrid Wilson interval for p1 - p2."""
    from math import sqrt
    z = 1.959964

    def wilson(k, n):
        p = k / n
        c = (p + z * z / (2 * n)) / (1 + z * z / n)
        h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        return c - h, c + h
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    d = p1 - p2
    return d, (d - sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2))


def analyze(rows, write=True, path=None):
    arms = sorted({r["arm"] for r in rows})
    res = {"arms": {}, "comps": {}, "verdicts": {}}
    for a in arms:
        xs = [r for r in rows if r["arm"] == a]
        res["arms"][a] = {k: _mean([f(r) for r in xs]) for k, f in K.items()}
        res["arms"][a]["n"] = len(xs)
        res["arms"][a]["evens"] = evens(rows, a)
        res["arms"][a]["ext_share"] = _mean([ext_share(r) for r in xs])
        mk = [r["mk"] for r in xs if r.get("mk")]
        if mk:
            res["arms"][a]["proj"] = {k: _mean([m["proj"][k] for m in mk]) for k in ("started", "protected", "asked", "agreed", "refused",
                                                                                     "completed", "abandoned", "comp_paid")}
            res["arms"][a]["by_kind"] = {k: _mean([m["by_kind"][k] for m in mk]) for k in MK.KINDS}
            res["arms"][a]["f4_shift"] = _mean([abs(m["f4_share_A"]["with"] - m["f4_share_A"]["without"]) for m in mk])
            res["arms"][a]["f4_shift_ge_005"] = _mean([float(abs(m["f4_share_A"]["with"] - m["f4_share_A"]["without"]) >= 0.05)
                                                       for m in mk])
            if a == "A":
                picks = [m["agreed"] for m in mk]
                res["arms"][a]["agreed_picks"] = {p: picks.count(p) for p in set(picks)}
    C = res["comps"]
    have = set(arms)

    def c(name, hi, lo, key, alt=None, keep=None):
        if hi in have and lo in have:
            C[name] = comp(rows, hi, lo, K[key] if isinstance(key, str) else key, alt, keep)
    for a in ("BP", "H", "P", "G", "A"):
        c(f"{a}-Z pleasure", a, "Z", "pleasure", "greater")
        c(f"{a}-Z p_raw", a, "Z", "p_raw")
        c(f"{a}-Z net", a, "Z", "net")
        c(f"{a}-Z bpw", a, "Z", "bpw", "greater")
        c(f"{a}-Z formed0", a, "Z", "formed0")
        c(f"{a}-Z together", a, "Z", "together")
    c("BP-G pleasure (motive)", "BP", "G", "pleasure")
    c("G-Z pleasure (exit split)", "G", "Z", "pleasure")
    c("H-Z e0_share", "H", "Z", "e0_share", "greater", ANY_E0)
    c("H-P ext_share", "H", "P", ext_share, "greater", ONE_EXT)
    c("P-H pleasure ext", "P", "H", "pleasure", "greater", ANY_EXT)
    c("P-H pleasure no-ext", "P", "H", "pleasure", None, lambda r: bool(r.get("mk")) and not ANY_EXT(r))
    for k in ("started", "completed", "paid", "pleasure", "p_raw", "together"):
        c(f"BP-PN-BP {k}", "BP-PN", "BP", k, "greater", ANY_ART)
        c(f"BP-PI-BP {k}", "BP-PI", "BP", k, None, ANY_ART)
    c("BP-BP-w0 formed0", "BP", "BP-w0", "formed0", "less")
    c("Z-Z-w0 formed0", "Z", "Z-w0", "formed0")
    c("BP-w0-Z-w0 pleasure", "BP-w0", "Z-w0", "pleasure")
    c("BP-net-Z-net pleasure", "BP-net", "Z-net", "pleasure")
    c("Z-M0 pleasure", "Z", "M0", "pleasure")
    c("BP-M0 pleasure", "BP", "M0", "pleasure")
    c("Z-M0 p_raw", "Z", "M0", "p_raw")
    no_ext = lambda r: bool(r.get("mk")) and not ANY_EXT(r)
    c("Z-M0 pleasure no-ext", "Z", "M0", "pleasure", None, lambda r: r["arm"] == "M0" or no_ext(r))
    c("Z-M0 pleasure ext", "Z", "M0", "pleasure", None, lambda r: r["arm"] == "M0" or ANY_EXT(r))
    c("BP-Z pleasure no-ext", "BP", "Z", "pleasure", None, no_ext)
    c("BP-Z pleasure ext", "BP", "Z", "pleasure", None, ANY_EXT)
    # Holm families
    fam1 = [f"{a}-Z pleasure" for a in ("BP", "H", "P", "G", "A") if f"{a}-Z pleasure" in C and C[f"{a}-Z pleasure"].get("p") is not None]
    if fam1:
        for n_, p in zip(fam1, ST.holm([C[n]["p"] for n in fam1])):
            C[n_]["holm"] = p
    fam2 = [n for n in ("H-Z bpw", "P-Z bpw", "BP-Z bpw") if n in C]
    for n_, p in zip(fam2, ST.holm([C[n]["p"] for n in fam2])):
        C[n_]["holm"] = p
    fam5 = [n for n in ("H-P ext_share", "P-H pleasure ext") if n in C]
    for n_, p in zip(fam5, ST.holm([C[n]["p"] for n in fam5])):
        C[n_]["holm"] = p
    fam6 = [n for n in ("BP-PN-BP started", "BP-PN-BP paid", "BP-PN-BP pleasure") if n in C]
    for n_, p in zip(fam6, ST.holm([C[n]["p"] for n in fam6])):
        C[n_]["holm"] = p
    res["verdicts"] = verdicts(res, rows)
    if write:
        (path or OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    return res


def _hold(o, thr, lower_ok=None):
    """Holds robustly: estimate >= thr, CI lower > 0 (or >= lower_ok), Holm p < 0.05. Weak: estimate >= thr only."""
    if not o or o.get("est") is None:
        return "not run"
    lo = o["ci"][0]
    p = o.get("holm", o.get("p", 0))
    ok_lo = lo > 0 if lower_ok is None else lo >= lower_ok
    if o["est"] >= thr and ok_lo and p < 0.05:
        return "holds"
    if o["est"] >= thr:
        return "weak"
    return "misses"


def verdicts(res, rows):
    C, V = res["comps"], {}
    p1 = C.get("BP-Z pleasure")
    if p1 and p1.get("est") is not None:
        rb = C.get("BP-Z p_raw", {})
        agree = rb.get("est") is not None and np.sign(rb["est"]) == np.sign(p1["est"])
        V["P1"] = _hold(p1, MARGIN)
        V["P1b"] = "holds" if agree else "misses"
        if V["P1"] == "holds" and agree:
            V["H39"] = "supported"
        elif p1["est"] <= 0 or (p1["est"] < MARGIN and p1["ci"][1] < 2 * MARGIN):
            V["H39"] = "not supported"
        else:
            V["H39"] = "inconclusive"
    for n in ("H-Z bpw", "P-Z bpw", "BP-Z bpw"):
        if n in C:
            V[f"P2 {n}"] = _hold(C[n], 0.10)
    if "H-Z e0_share" in C:
        V["P3"] = _hold(C["H-Z e0_share"], 0.03)
    if "BP" in res["arms"] and "Z" in res["arms"]:
        e1, e0 = res["arms"]["BP"]["evens"], res["arms"]["Z"]["evens"]
        if e1["n"] and e0["n"]:
            d, ci = newcombe(e1["k"], e1["n"], e0["k"], e0["n"])
            res["comps"]["P4 evens BP-Z"] = {"est": d, "ci": ci}
            V["P4"] = "holds" if (-0.10 < ci[0] and ci[1] < 0.10) else "misses"
    if "H-P ext_share" in C:
        V["P5"] = _hold(C["H-P ext_share"], 0.05)
    if "P-H pleasure ext" in C:
        V["P5b"] = _hold(C["P-H pleasure ext"], 1e-12)
    if "BP-PN-BP started" in C:
        V["P6a"] = _hold(C["BP-PN-BP started"], 0.20)
        V["P6b"] = _hold(C["BP-PN-BP paid"], 0.10)
        o = C["BP-PN-BP pleasure"]
        V["P6c"] = "holds" if (o["est"] > 0 and o["ci"][0] >= -0.002) else "misses"
        V["H20a"] = "supported" if all(V[k] == "holds" for k in ("P6a", "P6b", "P6c")) else "not supported"
    if "BP-BP-w0 formed0" in C:
        o = C["BP-BP-w0 formed0"]
        V["P7"] = "holds" if (o["est"] <= -0.10 and o["ci"][1] < 0 and o["p"] < 0.05) else ("weak" if o["est"] <= -0.10 else "misses")
    return V


# ---- pilot, power, reach --------------------------------------------------------------------------------------------------------

def pilot():
    run(PILOT_ARMS, H38.pairings(H38.PILOT), H38.PILOT["seeds"], OUT / "pilot.jsonl")
    res = analyze(H38.load(OUT / "pilot.jsonl"), path=OUT / "pilot-analysis.json")
    print(json.dumps({k: v for k, v in res["comps"].items()}, indent=1, default=str))


def power():
    rows = H38.load(OUT / "pilot.jsonl")
    out = {}
    for name, hi, lo, key, keep, eff in (("P1", "BP", "Z", "pleasure", None, MARGIN), ("P5b", "P", "H", "pleasure", ANY_EXT, None),
                                         ("P6c", "BP-PN", "BP", "pleasure", ANY_ART, None), ("P6a", "BP-PN", "BP", "started", ANY_ART, 0.20),
                                         ("P6b", "BP-PN", "BP", "paid", ANY_ART, 0.10)):
        d, ks, _, _ = paired(rows, hi, lo, K[key], keep)
        sd = float(d.std(ddof=1))
        e = eff if eff is not None else max(abs(float(d.mean())), 1e-4)
        out[name] = {"pilot_est": float(d.mean()), "pilot_sd": sd, "n_pilot": len(ks), "effect_used": e,
                     "units_80": ST.seeds_for_power(e, sd, target=0.8, alpha=0.05, paired=True)}
    print(json.dumps(out, indent=1))
    (OUT / "power.json").write_text(json.dumps(out, indent=1))
    return out


def reach():
    """Free checks: the analysis on synthetic and relabelled pilot rows, and two small parameter flips."""
    rows = H38.load(OUT / "pilot.jsonl")
    out = {}

    def relabel(m, add=None):
        new = []
        for r in rows:
            for tgt, src in m.items():
                if r["arm"] == src:
                    x = json.loads(json.dumps(r))
                    x["arm"] = tgt
                    if add and tgt in add:
                        add[tgt](x)
                    new.append(x)
        return new
    base = {"Z": "Z", "H": "H", "P": "P", "BP-PN": "BP-PN"}

    def plus(v):
        def f(x):
            x["pl"] += v
            x["p_raw"] += v
        return f
    alt = {}

    def noisy(x):
        k = (x["a"], x["b"])
        alt.setdefault(k, 0.08 * (1 if len(alt) % 2 else -1))
        x["pl"] += 0.004 + alt[k]
    cases = {"H39 supported (BP = Z + 0.01)": relabel({**base, "BP": "Z"}, {"BP": plus(0.01)}),
             "H39 not supported (BP = Z)": relabel({**base, "BP": "Z"}),
             "H39 inconclusive (BP = Z + 0.004 +- 0.08)": relabel({**base, "BP": "Z"}, {"BP": noisy}),
             "P5b fails (H and P swapped)": relabel({"Z": "Z", "BP": "BP", "H": "P", "P": "H", "BP-PN": "BP-PN"}),
             "P6 fails (BP-PN = BP)": relabel({"Z": "Z", "BP": "BP", "H": "H", "P": "P", "BP-PN": "BP"}),
             "P6 holds (synthetic: BP-PN = BP + projects)": relabel({**base, "BP": "BP", "BP-PN": "BP"},
                                                                   {"BP-PN": lambda x: (x["mk"]["proj"].__setitem__("started", x["mk"]["proj"]["started"] + 1),
                                                                                        x["mk"].__setitem__("paid", x["mk"]["paid"] + 1),
                                                                                        x.__setitem__("pl", x["pl"] + 0.003))})}
    for name, rs in cases.items():
        v = analyze(rs, write=False)["verdicts"]
        out[name] = {k: v.get(k) for k in ("H39", "P1", "P1b", "P5b", "P6a", "P6b", "P6c", "H20a")}
        print(name, out[name], flush=True)
    # parameter flips on a few pilot pairings (free runs)
    pairs = [p for p in H38.pairings(H38.PILOT)][:10]
    flip = {}
    for nm, arm, ov in (("P5 extractive = safe (cue 0, boost 0), H", "H", {"cue": 0.0, "boost": 0.0, "crave": 0.0}),
                        ("P5 extractive = safe (cue 0, boost 0), P", "P", {"cue": 0.0, "boost": 0.0, "crave": 0.0}),
                        ("P6 nobody agrees (trust_min 2), BP-PN", "BP-PN", {"trust_min": 2.0})):
        rs = []
        for a, b in pairs:
            run_, lived, _ = play(arm, a, b, 900, ov)
            rs.append(record(run_, lived, arm, a, b, 900))
        flip[nm] = {"ext_share": _mean([ext_share(r) for r in rs]), "agreed": _mean([r["mk"]["proj"]["agreed"] for r in rs]),
                    "started": _mean([r["mk"]["proj"]["started"] for r in rs])}
        print(nm, flip[nm], flush=True)
    out["flips"] = flip
    allrows = H38.load(OUT / "pilot.jsonl")
    out["open_cells_pilot"] = {"one_ext": len({(r["a"], r["b"]) for r in allrows if ONE_EXT(r)}),
                               "any_ext": len({(r["a"], r["b"]) for r in allrows if ANY_EXT(r)}),
                               "any_art": len({(r["a"], r["b"]) for r in allrows if ANY_ART(r)}),
                               "any_e0": len({(r["a"], r["b"]) for r in allrows if ANY_E0(r)})}
    ps = RT.personas()
    with MK.use_makers(MK.DEFAULT):
        cells = {"one_ext": 0, "any_ext": 0, "any_art": 0, "any_e0": 0}
        for a, b in H38.pairings(H38.CONFIRM):
            t = [MK.traits(ps[a]), MK.traits(ps[b])]
            cells["one_ext"] += sum(x["aim"] == "extractive" for x in t) == 1
            cells["any_ext"] += any(x["aim"] == "extractive" for x in t)
            cells["any_art"] += any(x["kind"] == "artist" for x in t)
            cells["any_e0"] += any(x["e"] == 0.0 for x in t)
    out["open_cells_confirm"] = cells
    print(json.dumps(out["open_cells_pilot"]), json.dumps(cells))
    (OUT / "reach.json").write_text(json.dumps(out, indent=1, default=str))
    return out


# ---- story spot-check (pattern-atlas recorder plus a makers line per 13-week block) ----------------------------------------------

def story_run(arm, a, b, seed):
    """Replays one run with the atlas Recorder attached (it only reads) and a weekly makers snapshot. -> (lines, row of record())."""
    import dataclasses
    from mar import atlas as AT
    from mar import exit_fallback as EF
    from mar import exit_items as EI
    from mar import hedonic as HD
    from mar import negotiation as NG
    from mar.worlds import household as H
    cfg, rule = arm_setup(arm)
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **(rule or {}))
    snaps = {}
    with MK.use_makers(cfg), HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), \
            EI.use_items(EI.GRID[H38.CELL]):
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=H.WEEKS, decline=True)
        world = lived.world

        def snap(wd, wk):
            if wd is world and wd.makers:
                st = wd.makers
                snaps[wk] = {"blocks": dict(st["blocks"]), "credit": {r: MK.credit(wd, r) for r in "AB"},
                             "proj": {r: (dict(st["project"][r]) if st["project"][r] else None) for r in "AB"},
                             "h": {r: st["recv"][r]["h"] for r in "AB"}, "s": {r: st["recv"][r]["s"] for r in "AB"},
                             "lost": dict(st["lost_tol"]), "trap": dict(st["trap_weeks"])}
        world.hook = snap
        rec = AT.Recorder(world)
        last = {"busy": {"A": False, "B": False}}
        for w in range(world.weeks):
            if w and w % NG.REVIEW_EVERY == 0:
                if lived.apart and lived.decline:
                    lived.retry(w, last)
                elif all(world.p[r]["in"] for r in "AB"):
                    lived.reading(w, last)
            if world.early_review:
                world.ladder_reviewed(w)
            last = {"busy": world.step_week(w, last)}
        world.run.final = {r: {**world.p[r], "pooled": world.pool, "put": world.put[r]} for r in "AB"}
        world.run.fix = world.fix_report()
        world.run.exits = list(world.exit_log)
        rec.lived(lived).finish()
    names = {"A": a, "B": b}
    lines = AT.story(rec.rows, rec.meta, names)
    out = []
    st = world.makers
    if st:
        t = st["traits"]
        out.append("Makers: " + "; ".join(f"{a if r == 'A' else b} {t[r]['kind']}, {t[r]['aim']}, enjoys {t[r]['e']}, w {t[r]['w']:.2f}"
                                           for r in "AB") + f". Rule: {st['rule']}.")
    for i, ln in enumerate(lines):
        out.append(ln)
        s0, s1 = snaps.get(13 * i), snaps.get(min(13 * i + 12, 155) + 1) or snaps.get(155)
        if st and s0 and s1:
            mk = [f"{names[r]} made {s1['blocks'][r] - s0['blocks'][r]}" for r in "AB"]
            ev = [f"{names[x['who']]} {x['event']} a project" + (" (protected)" if x.get("protected") else "")
                  for x in st["proj"]["log"] if 13 * i <= x["week"] < 13 * i + 13]
            out.append("    makers: " + ", ".join(mk) + f"; credit {s1['credit']['A']:.0f} vs {s1['credit']['B']:.0f}"
                       + f"; tolerance {s1['h']['A']}/{s1['h']['B']}, sensitization {s1['s']['A']}/{s1['s']['B']}"
                       + f"; liking lost {s1['lost']['A'] - s0['lost']['A']:.3f}/{s1['lost']['B'] - s0['lost']['B']:.3f}"
                       + f", trap weeks {s1['trap']['A'] - s0['trap']['A']}/{s1['trap']['B'] - s0['trap']['B']}"
                       + ("; " + "; ".join(ev) if ev else "") + ".")
    return out, record(world.run, lived, arm, a, b, seed)


def stories(picks):
    res = {}
    for arm, a, b, seed in picks:
        lines, rec = story_run(arm, a, b, seed)
        stored = [r for r in H38.load(OUT / "rows.jsonl") if (r["arm"], r["a"], r["b"], r["seed"]) == (arm, a, b, seed)]
        same = bool(stored) and abs(stored[0]["pl"] - rec["pl"]) < 1e-12
        res[f"{arm}|{a}|{b}|{seed}"] = {"lines": lines, "reproduces_stored_row": same, "pl": rec["pl"]}
        print(f"\n== {arm} {a} {b} seed {seed} (pleasure {rec['pl']:.3f}; reproduces stored row: {same})")
        print("\n".join(lines))
    (OUT / "stories.json").write_text(json.dumps(res, indent=1))
    return res


# ---- observer sample: what tipped formation (observer layer, src/mar/observe.py) ------------------------------------------------

def observe_run(arm, a, b, seed):
    import dataclasses
    from mar import exit_fallback as EF
    from mar import exit_items as EI
    from mar import hedonic as HD
    from mar import negotiation as NG
    from mar import observe as OB
    from mar.worlds import household as H
    cfg, rule = arm_setup(arm)
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **(rule or {}))
    with MK.use_makers(cfg), OB.collecting(), HD.use_levers(RT.LEVERS), HD.use_fixes(fx), \
            EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[H38.CELL]):
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=H.WEEKS, decline=True)
        world = lived.world
        ob = OB.Observer(world, OB.ObsConfig(), run_key=f"h39|{arm}|{a}|{b}|{seed}", meta={"family": "h39", "arm": arm}, harness=lived)
        last = {"busy": {"A": False, "B": False}}
        for w in range(world.weeks):
            if w and w % NG.REVIEW_EVERY == 0:
                if lived.apart and lived.decline:
                    lived.retry(w, last)
                elif all(world.p[r]["in"] for r in "AB"):
                    lived.reading(w, last)
            if world.early_review:
                world.ladder_reviewed(w)
            last = {"busy": world.step_week(w, last)}
    ob.finish()
    return [x for x in ob.rows if x.get("t") == "reading"], record(world.run, lived, arm, a, b, seed)


def observe_sample(arms=("M0", "Z", "BP"), n=20, seed=0):
    """Formation at week 0: per member, the household value minus the outside value, split into the observer's groups (net parts),
    for members who block formation and members who do not."""
    pairs = H38.pairings(H38.CONFIRM)[:n]
    out = {}
    for arm in arms:
        agg = {"block": {}, "ok": {}}
        cnt = {"block": 0, "ok": 0}
        same = 0
        for a, b in pairs:
            rd, rec = observe_run(arm, a, b, seed)
            stored = [r for r in H38.load(OUT / "rows.jsonl") if (r["arm"], r["a"], r["b"], r["seed"]) == (arm, a, b, seed)]
            same += bool(stored) and abs(stored[0]["pl"] - rec["pl"]) < 1e-12
            f0 = next((x for x in rd if x["kind"] == "formation0"), None)
            if f0 is None:
                continue
            for r in "AB":
                m = f0["m"][r]
                if not m.get("W_parts") or not m.get("O_parts"):
                    continue
                k = "block" if m["margin"] < 0 else "ok"
                cnt[k] += 1
                for g in m["W_parts"]:
                    agg[k][g] = agg[k].get(g, 0.0) + m["W_parts"][g] - m["O_parts"].get(g, 0.0)
        out[arm] = {"members": cnt, "reproduces_stored_rows": f"{same} of {len(pairs)}",
                    **{k: {g: round(v / cnt[k], 4) for g, v in sorted(agg[k].items(), key=lambda t: t[1]) if abs(v) > 1e-9}
                       for k in agg if cnt[k]}}
        print(arm, json.dumps(out[arm], indent=1), flush=True)
    (OUT / "observer-sample.json").write_text(json.dumps(out, indent=1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--power", action="store_true")
    ap.add_argument("--reach", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--observe", action="store_true")
    ap.add_argument("--stories", default="", help="arm|a|b|seed;... runs to tell as stories")
    a = ap.parse_args()
    if a.pilot:
        pilot()
    if a.power:
        power()
    if a.reach:
        reach()
    if a.run:
        run(a.arms.split(","), H38.pairings(H38.CONFIRM), tuple(range(a.seeds)), OUT / "rows.jsonl")
    if a.analyze:
        res = analyze(H38.load(OUT / "rows.jsonl"))
        print(json.dumps(res["verdicts"], indent=1))
    if a.observe:
        observe_sample()
    if a.stories:
        stories([(x.split("|")[0], x.split("|")[1], x.split("|")[2], int(x.split("|")[3])) for x in a.stories.split(";")])


if __name__ == "__main__":
    main()
