"""How the hybrid decides to leave (docs/results/hybrid-leaving-prereg.md; hybrid prereg Amendment 5). Scripted persona agents, no model
calls. Wording rule: agents feel nothing; "pleasure", "suffering", "tally" and "forecast" are glosses for modeled numbers.

  uv run python scripts/hybrid_leaving.py --paths            slice (b): lived exit paths and the outside-forecast error (A4 on B, trial,
                                                             P2; old on B); runs/hybrid-leaving/paths-<version>.jsonl
  uv run python scripts/hybrid_leaving.py --paths-analyze    slice (b) tables -> runs/hybrid-leaving/paths.json
  uv run python scripts/hybrid_leaving.py --reach            "Can every verdict happen?" (synthetic exits, three-version labels, P-AUTH)
  uv run python scripts/hybrid_leaving.py --kx2 [--flags a4|a5]   KX2 with a pure exit cost (exit_fixed 0.04 vs 0, exit option off/on)
  uv run python scripts/hybrid_leaving.py --story            KL2 under A5 (story 4), with the outside forecast against the life lived
  uv run python scripts/hybrid_leaving.py --run CFG [--arms B,..] [--every k]   H41's harness under a configuration (CFGS); rows in
                                                             runs/hybrid-leaving/<CFG>.jsonl (a5: rows.jsonl)
  uv run python scripts/hybrid_leaving.py --analyze          three versions, the stop rule, KO1, P-AUTH, sweeps -> analysis.json
  uv run python scripts/hybrid_leaving.py --life ARM A B [--version a5]   one life, 13-week blocks (story check)
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
sys.path.insert(0, str(ROOT / "scripts"))
import h41_choice_aids as A  # noqa: E402
import hybrid_exit_option as XO  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import hybrid as HY  # noqa: E402
from mar import makers as MK  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "hybrid-leaving"
WORKERS = 4
WIN = 13            # the two windows a path compares (weeks)
FLAT = 0.25         # quiet path: weighted suffering moved by at most this share of the pleasure fall (ASSUMED, prereg)
POST_MAX, POST_MIN = 52, 13

# Amendment 5's version and the arms around it (hybrid-leaving-prereg.md). A4's flags are hybrid_exit_option.VERSIONS["new"].
A5 = {"hybrid_lone": True, "hybrid_exit": True, "hybrid_tally": "level", "tally_half": 13.0, "tally_line": 0.02, "exit_grow": 0.04,
      "hybrid_outside": "lived"}
CFGS = {"a5": A5, "a5_noexit": {**A5, "hybrid_exit": False},
        "half4": {**A5, "tally_half": 4.0}, "half26": {**A5, "tally_half": 26.0},
        "line0": {**A5, "tally_line": 0.0}, "line05": {**A5, "tally_line": 0.05},
        "slope": {**A5, "hybrid_tally": "slope"}, "both": {**A5, "hybrid_tally": "both"},
        "grow0": {**A5, "exit_grow": 0.0}, "grow02": {**A5, "exit_grow": 0.02}, "grow08": {**A5, "exit_grow": 0.08},
        "solo": {**A5, "hybrid_outside": "solo"}, "bias02": {**A5, "leave_bias": 0.02}, "bias05": {**A5, "leave_bias": 0.05}}
SWEEPS = ("half4", "half26", "line0", "line05", "slope", "both", "grow0", "grow02", "grow08", "solo", "bias02", "bias05")
XO.VERSIONS.update(CFGS)
OLD_ROWS = ROOT / "runs" / "h41-choice-aids" / "rows.jsonl"
A4_ROWS = ROOT / "runs" / "h41-exit-option" / "rows.jsonl"
KX2_COST = 0.04          # the exact model's exit cost: 0.04 a week for one 13-week block (h41_exact, ASSUMED there)


# ---- slice (b): how lived exits come about ------------------------------------------------------------------------------------

def in_flags(run, lone):
    """Per week, the set of roles in the household: both (both_in), the one alone (lone), or none."""
    out = []
    for o, x in zip(run.outcomes, lone):
        out.append({"A", "B"} if o["both_in"] else ({x[0]} if x is not None else set()))
    return out


def ys(run, role, w):
    """The leaver's weekly yardstick, pleasure and suffering (both kinds)."""
    h = [o["hedonic"][role] for o in run.outcomes]
    p = [x["pleasure"] for x in h]
    s = [x["s_off"] + x["s_non"] for x in h]
    so = [x["s_off"] for x in h]
    sn = [x["s_non"] for x in h]
    return p, s, so, sn, [a - w * b for a, b in zip(p, s)]


def classify(p, s, w, early, late):
    """slice (b)'s classes from mean pleasure and suffering in two windows (lists of week indices)."""
    dp = float(np.mean([p[i] for i in late]) - np.mean([p[i] for i in early]))
    ds = float(np.mean([s[i] for i in late]) - np.mean([s[i] for i in early]))
    cp, cs = -dp, w * ds
    if cp + cs <= 0:
        c = "no_fall"
    elif cs >= cp:
        c = "suffering"
    elif abs(cs) <= FLAT * cp:
        c = "quiet"
    else:
        c = "mixed"
    return c, {"dp": round(dp, 6), "ds": round(ds, 6), "cp": round(cp, 6), "cs": round(cs, 6)}


def exit_paths(run, lived, lone, events, weights):
    """One record per lived exit: classes under both window pairs, the partner's class, the outside-forecast error."""
    flags = in_flags(run, lone)
    n = len(run.outcomes)
    why = {}
    for wk, r, ev in events:
        if isinstance(ev, str) and ev.startswith("leave_"):
            why[(wk, r)] = ev[6:]
    pair_log = list(lived.log)
    lone_log = list(getattr(lived.world, "lone_log", []))
    out = []
    for e in run.exits:
        wk, r = e["week"], e["role"]
        q = "B" if r == "A" else "A"
        start = wk
        while start > 0 and r in flags[start - 1]:
            start -= 1
        rec = {"week": wk, "role": r, "why": why.get((wk, r)), "spell_start": start, "spell": wk - start, "w": weights[r]}
        p, s, so, sn, y = ys(run, r, weights[r])
        late = list(range(wk - WIN, wk))
        if wk - start >= 2 * WIN:
            rec["primary"], rec["primary_d"] = classify(p, s, weights[r], list(range(start, start + WIN)), late)
            rec["second"], rec["second_d"] = classify(p, s, weights[r], list(range(wk - 2 * WIN, wk - WIN)), late)
            rec["kinds"] = {"s_off": round(float(np.mean([so[i] for i in late]) - np.mean([so[i] for i in range(start, start + WIN)])), 6),
                            "s_non": round(float(np.mean([sn[i] for i in late]) - np.mean([sn[i] for i in range(start, start + WIN)])), 6)}
            pp, ps_, _, _, _ = ys(run, q, weights[q])
            rec["partner"], _ = classify(pp, ps_, weights[q], list(range(start, start + WIN)), late)
        else:
            rec["primary"] = rec["second"] = "short_spell"
        # outside-forecast error: the deciding reading's O against the life lived after the exit
        cands = [(x["week"], x["outside"][r]) for x in pair_log if x["week"] <= wk] + \
                [(x["week"], x["out"]) for x in lone_log if x["role"] == r and x["week"] <= wk]
        if cands:
            rw, O = max(cands, key=lambda t: t[0])
            post = list(range(wk + 1, min(n, wk + 1 + POST_MAX)))
            rec["reading_week"], rec["O"] = rw, round(O, 6)
            if len(post) >= POST_MIN:
                L = float(np.mean([y[i] for i in post]))
                rec["L"], rec["err"], rec["post_weeks"] = round(L, 6), round(L - O, 6), len(post)
        out.append(rec)
    return out


def path_task(args):
    arm, a, b, seed, version = args
    t0 = time.time()
    run, lived, rd, ex = XO.play(arm, a, b, seed, version)
    ps = RT.personas()
    weights = {"A": MK.suffering_weight(ps[a]), "B": MK.suffering_weight(ps[b])}
    events = run.fix.get("events", []) if isinstance(run.fix, dict) else []
    return {"g": arm, "a": a, "b": b, "seed": seed, "version": version, "exits": exit_paths(run, lived, ex["lone"], events, weights),
            "both_share": float(np.mean([o["both_in"] for o in run.outcomes])), "secs": round(time.time() - t0, 1)}


PATH_RUNS = (("new", ("B", "trial", "P2")), ("old", ("B",)))      # "new" is A4 here (hybrid_exit_option.VERSIONS)


def paths(workers=WORKERS):
    OUT.mkdir(parents=True, exist_ok=True)
    for version, arms in PATH_RUNS:
        f = OUT / f"paths-{'a4' if version == 'new' else version}.jsonl"
        done = {(r["g"], r["a"], r["b"]) for r in A.load(f)} if f.exists() else set()
        tasks = [(arm, a, b, s, version) for (a, b) in A.pairings(A.CONFIRM) for arm in arms for s in A.CONFIRM["seeds"]
                 if (arm, a, b) not in done]
        print(f"{version}: {len(tasks)} tasks -> {f}", flush=True)
        t0 = time.time()
        with Pool(min(workers, 4)) as pool, f.open("a") as fh:
            for i, rec in enumerate(pool.imap_unordered(path_task, tasks, chunksize=1), 1):
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                if i % 40 == 0 or i == len(tasks):
                    print(f"  {i}/{len(tasks)} wall {time.time() - t0:.0f}s", flush=True)


CLASSES = ("suffering", "quiet", "mixed", "no_fall", "short_spell")


def boot_mean(vals, groups, n=2000, seed=0):
    """Mean and a 95% bootstrap interval resampling groups (pairings)."""
    if not vals:
        return None
    by = {}
    for v, g in zip(vals, groups):
        by.setdefault(g, []).append(v)
    keys = list(by)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n):
        pick = [keys[i] for i in rng.integers(0, len(keys), len(keys))]
        xs = [v for k in pick for v in by[k]]
        bs.append(float(np.mean(xs)))
    return {"mean": float(np.mean(vals)), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "n": len(vals)}


def path_table(rows):
    ex = [(r, e) for r in rows for e in r["exits"]]
    t = {"runs": len(rows), "exits": len(ex), "by_why": {}}
    for key in ("primary", "second"):
        t[key] = {c: sum(1 for _, e in ex if e[key] == c) for c in CLASSES}
    for _, e in ex:
        t["by_why"][str(e["why"])] = t["by_why"].get(str(e["why"]), 0) + 1
    t["partner"] = {c: sum(1 for _, e in ex if e.get("partner") == c) for c in CLASSES}
    suf = [e for _, e in ex if e["primary"] == "suffering"]
    t["suffering_kinds"] = {"s_off_up": sum(1 for e in suf if e["kinds"]["s_off"] > 0), "s_non_up": sum(1 for e in suf if e["kinds"]["s_non"] > 0),
                            "n": len(suf)}
    err = [(e["err"], (r["a"], r["b"])) for r, e in ex if "err" in e and e["why"] == "bar"]
    t["outside_error_bar"] = boot_mean([x for x, _ in err], [g for _, g in err])
    err_all = [(e["err"], (r["a"], r["b"])) for r, e in ex if "err" in e]
    t["outside_error_all"] = boot_mean([x for x, _ in err_all], [g for _, g in err_all])
    t["worst_errors"] = sorted(([round(e["err"], 3), r["g"], r["a"], r["b"], e["week"], e["role"], e["why"]] for r, e in ex if "err" in e),
                               key=lambda x: x[0])[:5]
    return t


def paths_analyze():
    res = {}
    for f in sorted(OUT.glob("paths-*.jsonl")):
        rows = A.load(f)
        v = f.stem.split("-", 1)[1]
        for arm in sorted({r["g"] for r in rows}):
            res[f"{v}:{arm}"] = path_table([r for r in rows if r["g"] == arm])
    (OUT / "paths.json").write_text(json.dumps(res, indent=1))
    for k, t in res.items():
        print(k, "exits", t["exits"], "why", t["by_why"])
        print("   primary", t["primary"])
        print("   second ", t["second"])
        print("   partner", t["partner"], "suffering kinds", t["suffering_kinds"])
        print("   outside error (bar exits)", t["outside_error_bar"], " all", t["outside_error_all"])
        print("   worst", t["worst_errors"])
    return res


# ---- slice (c): KX2 with a pure exit cost --------------------------------------------------------------------------------------

KX2_FLAGS = {"a4": {"hybrid_lone": True}, "a5": {k: v for k, v in A5.items() if k != "hybrid_exit"}}


def _kx2_one(args):
    import formation_check_3 as FC3
    import stay_test_run as STR
    flags, exit_on, cost, a, b, seed = args
    ps = STR.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **FC3.rule("hybrid"), hybrid_w="persona", hybrid_readings="world",
                             **KX2_FLAGS[flags], hybrid_exit=exit_on, exit_fixed=cost)
    last = {"busy": {"A": False, "B": False}}
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        world = H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), (ps[a], ps[b]), seed, H.WEEKS)
        HY._FLOG[0] = []
        try:
            V = HY.forecast(world, 0, last, NG.decide_weeks(NG.FORWARD_WEEKS))
            fut = HY._FLOG[0]
        finally:
            HY._FLOG[0] = None
        O = {r: NG.outside_value(world.personas[r], r, world.p[r]["money"], seed, world.hed[r], cx=NG._cx(world, r))[0] for r in "AB"}
    return {"flags": flags, "exit": exit_on, "cost": cost, "a": a, "b": b, "V": V, "O": O,
            "futures_with_exit": sum(1 for f in fut if f), "futures": len(fut), "exit_weeks": fut}


def kx2(flags="a4", workers=WORKERS, n_pairs=12, seed=900):
    """KX2 (prereg slice c): the stay test's baseline fixture with a pure exit cost (exit_fixed) against none, exit option off and on."""
    import stay_test_run as STR
    pairs = [(a, b) for a, b, c in STR.pairings() if c == "ctl"][:n_pairs]
    tasks = [(flags, e, c, a, b, seed) for e in (False, True) for c in (0.0, KX2_COST) for a, b in pairs]
    t0 = time.time()
    with Pool(min(workers, 4)) as p:
        recs = p.map(_kx2_one, tasks, chunksize=1)
    get = {(r["exit"], r["cost"], r["a"], r["b"]): r for r in recs}
    did, D = {}, {False: [], True: []}
    for a, b in pairs:
        dd = []
        for r in "AB":
            d = {e: get[(e, 0.0, a, b)]["V"][r] - get[(e, KX2_COST, a, b)]["V"][r] for e in (False, True)}
            D[False].append(d[False])
            D[True].append(d[True])
            dd.append(d[True] - d[False])
        did[(a, b)] = float(np.mean(dd))
    vals = np.array(list(did.values()))
    rng = np.random.default_rng(0)
    bs = [float(np.mean(vals[rng.integers(0, len(vals), len(vals))])) for _ in range(4000)]
    ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    forms = {f"{'on' if e else 'off'}:{c}": float(np.mean([get[(e, c, a, b)]["V"][r] > get[(e, c, a, b)]["O"][r]
                                                         for a, b in pairs for r in "AB"])) for e in (False, True) for c in (0.0, KX2_COST)}
    fut = {c: sum(get[(True, c, a, b)]["futures_with_exit"] for a, b in pairs) for c in (0.0, KX2_COST)}
    fut_off = {c: sum(get[(False, c, a, b)]["futures_with_exit"] for a, b in pairs) for c in (0.0, KX2_COST)}
    first = {c: [min(f) for a, b in pairs for f in get[(True, c, a, b)]["exit_weeks"] if f] for c in (0.0, KX2_COST)}
    c1 = float(np.mean(vals)) > 0 and ci[0] > 0
    c2 = forms[f"on:0.0"] >= forms[f"on:{KX2_COST}"]
    c3 = all(v >= 1 for v in fut.values())
    out = {"flags": flags, "pairs": pairs, "D_off": float(np.mean(D[False])), "D_on": float(np.mean(D[True])), "DiD": float(np.mean(vals)),
           "DiD_ci": ci, "DiD_by_pair": list(vals), "beats_outside": forms, "futures_with_exit_on": {str(k): v for k, v in fut.items()},
           "futures_with_exit_off": {str(k): v for k, v in fut_off.items()},
           "first_exit_week_mean": {str(k): (float(np.mean(v)) if v else None) for k, v in first.items()},
           "clauses": {"i": c1, "ii": c2, "iii": c3},
           "KX2": "PASS" if (c1 and c2 and c3) else ("FAIL" if c3 else "CANNOT FAIL (no in-future exits)"),
           "rows": recs, "secs": round(time.time() - t0)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"kx2-{flags}.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, default=str))
    return out


# ---- slice (g): H41's harness under a configuration -------------------------------------------------------------------------

_TLOG = []


def _instrument():
    """Keep each lived week's tally flags (for rethink spells), without changing what the world does."""
    if getattr(HY.tally_step, "_wrapped", False):
        return
    real = HY.tally_step

    def wrapped(world, row):
        real(world, row)
        if HY.lived(world):
            _TLOG.append((row["week"], dict(world.tally_due), {r: (None if v is None else round(v, 5)) for r, v in world.tally.items()}))
    wrapped._wrapped = True
    HY.tally_step = wrapped


_instrument()


def spells(tlog, exits):
    """Rethink spells per member: runs of weeks its tally calls a rethink. Left: it left within the spell or 13 weeks after its start;
    came back: the spell ended and it did not leave."""
    out = {"spells": 0, "left": 0, "back": 0, "open": 0}
    for r in "AB":
        cur = None
        seq = [(wk, bool(d.get(r))) for wk, d, _ in tlog]
        for i, (wk, on) in enumerate(seq):
            if on and cur is None:
                cur = wk
            if (not on or i == len(seq) - 1) and cur is not None:
                end = wk
                out["spells"] += 1
                if any(e["role"] == r and cur <= e["week"] <= max(end, cur + 13) for e in exits):
                    out["left"] += 1
                elif not on:
                    out["back"] += 1
                else:
                    out["open"] += 1
                cur = None
    return out


def cfg_task(args):
    arm, a, b, seed, version = args
    t0 = time.time()
    _TLOG.clear()
    run, lived, rd, ex = XO.play(arm, a, b, seed, version, liberty=XO._LIB)
    rec = XO.record(run, lived, rd, ex, arm, a, b, seed, version, time.time() - t0)
    ps = RT.personas()
    weights = {"A": MK.suffering_weight(ps[a]), "B": MK.suffering_weight(ps[b])}
    events = run.fix.get("events", []) if isinstance(run.fix, dict) else []
    rec["paths"] = exit_paths(run, lived, ex["lone"], events, weights)
    rec["tally_log"] = list(getattr(lived.world, "tally_log", []))
    rec["spells"] = spells(_TLOG, run.exits)
    rec["xcost_paid"] = round(sum(o["hedonic"][r].get("fix", {}).get("exit_cost", 0.0) for o in run.outcomes for r in "AB"), 6)
    rec["future_exits"] = HY.STATS.get("future_exits", 0)
    rec["lived_outside"] = HY.STATS.get("lived_outside", 0)
    return rec


def cfg_file(name):
    return OUT / ("rows.jsonl" if name == "a5" else f"{name}.jsonl")


def run_cfg(name, arms, every=1, workers=WORKERS):
    f = cfg_file(name)
    f.parent.mkdir(parents=True, exist_ok=True)
    done = {(r["g"], r["a"], r["b"]) for r in A.load(f)} if f.exists() else set()
    pairs = A.pairings(A.CONFIRM)[::every]
    tasks = [(arm, a, b, s, name) for (a, b) in pairs for arm in arms for s in A.CONFIRM["seeds"] if (arm, a, b) not in done]
    print(f"{name}: {len(tasks)} tasks, {min(workers, 4)} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(min(workers, 4)) as pool, f.open("a") as fh:
        for i, rec in enumerate(pool.imap_unordered(cfg_task, tasks, chunksize=1), 1):
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            if i % 20 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {rec['secs']:.0f}s wall {time.time() - t0:.0f}s", flush=True)


# ---- KL2 under A5 ----------------------------------------------------------------------------------------------------------------

def story():
    arm, a, b, seed = XO.STORY
    a, b = next(((x, y) for x, y in A.pairings(A.CONFIRM) if {x, y} == {a, b}))
    t0 = time.time()
    _TLOG.clear()
    run, lived, rd, ex = XO.play(arm, a, b, seed, "a5")
    log = ex["lone_log"]
    m = 0.02
    stuck = False
    beyond = [x["out"] > x["stay"] + m for x in log]
    for i in range(1, len(log)):
        if beyond[i - 1] and beyond[i]:
            start = log[i - 1]["week"]
            stuck = sum(1 for wk, x in enumerate(ex["lone"]) if wk >= start and x is not None) > 26
            break
    ps = RT.personas()
    weights = {"A": MK.suffering_weight(ps[a]), "B": MK.suffering_weight(ps[b])}
    events = run.fix.get("events", []) if isinstance(run.fix, dict) else []
    out = {"pair": [a, b], "exits": [{"week": e["week"], "role": e["role"]} for e in run.exits], "lone_readings": log,
           "stuck": stuck, "KL2": "FAIL" if stuck else "PASS", **XO.lone_stats(ex["lone"]),
           "paths": exit_paths(run, lived, ex["lone"], events, weights), "tally_log": list(getattr(lived.world, "tally_log", [])),
           "suff_blocks": {r: [round(float(np.mean([o["hedonic"][r]["s_off"] + o["hedonic"][r]["s_non"] for o in run.outcomes[k:k + 13]])), 3)
                               for k in range(0, len(run.outcomes), 13)] for r in "AB"},
           "secs": round(time.time() - t0)}
    (OUT / "story-a5.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))
    return out


# ---- analysis --------------------------------------------------------------------------------------------------------------------

def three_way(vs):
    """vs: {version: {arm: {key: {"class": ...}}}} -> per arm and key, the classes and the label over all versions present."""
    out = {}
    arms = set.intersection(*[set(v) for v in vs.values()])
    for arm in sorted(arms):
        out[arm] = {}
        for k in vs["a5"][arm]:
            cls = {v: vs[v][arm][k]["class"] for v in vs}
            same = len(set(cls.values())) == 1
            out[arm][k] = {**cls, "label": f"holds across versions ({len(cls)})" if same else
                           "version-dependent (" + ", ".join(f"{v} {c}" for v, c in cls.items()) + ")"}
    return out


def ko1(rows, arm="B"):
    err = [(e["err"], (r["a"], r["b"])) for r in rows if r["g"] == arm for e in r.get("paths", []) if "err" in e and e["why"] == "bar"]
    m = boot_mean([x for x, _ in err], [g for _, g in err])
    if m is None:
        return {"KO1": "NO EXITS", "n": 0}
    ok = abs(m["mean"]) <= 0.02 and -0.04 <= m["ci"][0] and m["ci"][1] <= 0.04
    return {**m, "KO1": "PASS" if ok else "FAIL"}


def paired_diff(rows_x, rows_y, arm, key, pairs=None, n=2000):
    px, py = A.per_pair(rows_x, arm, key), A.per_pair(rows_y, arm, key)
    ks = sorted(set(px) & set(py) & (set(pairs) if pairs else set(px)))
    if not ks:
        return None
    d = np.array([px[k] - py[k] for k in ks])
    rng = np.random.default_rng(0)
    bs = [float(np.mean(d[rng.integers(0, len(d), len(d))])) for _ in range(n)]
    ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    return {"d": float(np.mean(d)), "ci": ci, "n": len(ks)}


def p_auth(a5, noexit):
    res = {}
    for k in ("formed0", "together"):
        d = paired_diff(a5, noexit, "B", k)
        if d:
            d["class"] = A.classify(d["d"], d["ci"], 0.01)
        res[k] = d
    res["P-AUTH"] = (None if res["formed0"] is None else ("missed" if res["formed0"]["class"] == "+" else "held"))
    return res


def run_summary(rows, arm="B"):
    xs = [r for r in rows if r["g"] == arm]
    if not xs:
        return None
    pairs = [(r["a"], r["b"]) for r in xs]
    keys = ("together", "formed0", "liberty", "pleasure", "lived", "snon", "ended")
    m = A.arm_means(rows, arm, keys)
    sm = XO.second_measure(rows, arm)
    sp = {k: sum(r.get("spells", {}).get(k, 0) for r in xs) for k in ("spells", "left", "back", "open")}
    paths_ = path_table([{"exits": r.get("paths", []), "a": r["a"], "b": r["b"], "g": arm} for r in xs]) if any("paths" in r for r in xs) else None
    return {"n": len(xs), **{k: m[k] for k in keys}, "exits_per_run": float(np.mean([len(r["exits"]) for r in xs])),
            "tally_readings_per_run": float(np.mean([len(r.get("tally_log", [])) for r in xs])),
            "secs": float(np.mean([r["secs"] for r in xs])), "second": sm, "spells": sp,
            "ko1": ko1(rows, arm) if paths_ else None,
            "paths": {k: paths_[k] for k in ("primary", "second", "by_why")} if paths_ else None, "pairs": pairs}


def analyze():
    old, a4, a5 = A.load(OLD_ROWS), A.load(A4_ROWS), A.load(cfg_file("a5"))
    res = {"h41_a5": A.analyze_rows(a5)}
    arms = [x for x in A.ARMS if x != "B" and any(r["g"] == x for r in a5)]
    vs = {v: {arm: XO.vs_b(rows, arm) for arm in arms} for v, rows in (("old", old), ("a4", a4), ("a5", a5))}
    res["vsB"] = vs
    res["stop_rule"] = three_way(vs)
    res["arms"] = {v: {arm: A.arm_means(rows, arm, A.KEYS) for arm in A.ARMS} for v, rows in (("old", old), ("a4", a4), ("a5", a5))}
    res["held_pooled"] = {v: {arm: A.pooled_held(rows, arm) for arm in A.ARMS} for v, rows in (("old", old), ("a4", a4), ("a5", a5))}
    res["paired_a5_minus_a4"] = {arm: {k: paired_diff(a5, a4, arm, k) for k in ("together", "formed0", "liberty", "pleasure", "lived", "snon")}
                                 for arm in A.ARMS}
    res["paired_a5_minus_old"] = {arm: {k: paired_diff(a5, old, arm, k) for k in ("together", "formed0", "liberty", "pleasure", "lived", "snon")}
                                  for arm in A.ARMS}
    res["second_measure"] = {arm: XO.second_measure(a5, arm) for arm in ("B", "P1", "trial", "prenup")}
    res["lone"] = {arm: XO.lone_summary(a5, arm) for arm in A.ARMS}
    res["KO1"] = ko1(a5, "B")
    res["summary_B"] = run_summary(a5, "B")
    res["summary_P2"] = run_summary(a5, "P2")
    if cfg_file("a5_noexit").exists():
        res["P_AUTH"] = p_auth(a5, A.load(cfg_file("a5_noexit")))
        res["P_AUTH_a4"] = {k: paired_diff(A.load(A4_ROWS), A.load(XO.OUT / "lone.jsonl"), "B", k) for k in ("formed0", "together")} \
            if (XO.OUT / "lone.jsonl").exists() else None
    centre = run_summary(a5, "B")
    res["sweeps"] = {}
    for name in SWEEPS:
        f = cfg_file(name)
        if not f.exists():
            continue
        rows = A.load(f)
        s = run_summary(rows, "B")
        pairs = set(s["pairs"])
        c = run_summary([r for r in a5 if (r["a"], r["b"]) in pairs], "B")
        s.pop("pairs", None)
        c.pop("pairs", None)
        res["sweeps"][name] = {"cfg": {k: v for k, v in CFGS[name].items() if A5.get(k) != v}, "sweep": s, "centre_same_pairs": c,
                               "d_together": paired_diff(rows, a5, "B", "together", pairs),
                               "d_formed0": paired_diff(rows, a5, "B", "formed0", pairs),
                               "d_pleasure": paired_diff(rows, a5, "B", "pleasure", pairs),
                               "d_liberty": paired_diff(rows, a5, "B", "liberty", pairs)}
    if centre:
        centre.pop("pairs", None)
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    show(res)
    return res


def show(res):
    print(f"{'arm':<7}" + "".join(f"{k:>26}" for k in ("together", "formed0", "liberty", "pleasure", "lived")))
    for arm in A.ARMS:
        vals = [res["arms"][v][arm] for v in ("old", "a4", "a5")]
        print(f"{arm:<7}" + "".join("  " + ">".join(f"{x[k]:.4f}" if x[k] is not None else "  nan " for x in vals) for k in
                                    ("together", "formed0", "liberty", "pleasure", "lived")))
    for arm, d in res["stop_rule"].items():
        vd = {k: v["label"] for k, v in d.items() if not v["label"].startswith("holds")}
        print(f"{arm:<7} {vd}")
    for aid, v in res["h41_a5"]["aids"].items():
        print(f"== {aid}: {v['verdict']}")
    print("H41 a5:", res["h41_a5"]["H41"])
    print("KO1:", res["KO1"])
    print("P-AUTH:", res.get("P_AUTH"), res.get("P_AUTH_a4"))
    print("second:", json.dumps(res["second_measure"]))
    print("summary B:", json.dumps({k: v for k, v in (res["summary_B"] or {}).items() if k != "pairs"}, default=str))
    for k, v in res["sweeps"].items():
        s, c = v["sweep"], v["centre_same_pairs"]
        print(f"sweep {k:<7} {v['cfg']}: together {s['together']:.3f} (c {c['together']:.3f}) formed0 {s['formed0']:.3f} (c {c['formed0']:.3f}) "
              f"exits/run {s['exits_per_run']:.2f} (c {c['exits_per_run']:.2f}) rethinks/run {s['tally_readings_per_run']:.2f} "
              f"f13 {s['second']['forecast13'] if s['second'] else None} l13 {s['second']['lived13'] if s['second'] else None} "
              f"KO1 {(s['ko1'] or {}).get('mean')} paths {s['paths']['primary'] if s['paths'] else None}")


def life(arm, a, b, version="a5", seed=0):
    _TLOG.clear()
    run, lived, rd, ex = XO.play(arm, a, b, seed, version)
    outs = run.outcomes
    print(f"{arm} {a} x {b} ({version}): week0 {lived.week0.get('term')} formed {lived.week0.get('formed')}; exits {run.exits}; "
          f"retries {[(x['week'], x['formed']) for x in lived.retries]}; trials {getattr(lived, 'trials', [])}")
    print("pair readings:", [(x["week"], {r: round(v, 3) for r, v in x["outside"].items()}, {r: round(v, 3) for r, v in x["baseline"].items()})
                             for x in lived.log])
    print("lone readings:", ex["lone_log"])
    print("tally rethinks:", getattr(lived.world, "tally_log", []))
    ps = RT.personas()
    wts = {"A": MK.suffering_weight(ps[a]), "B": MK.suffering_weight(ps[b])}
    events = run.fix.get("events", []) if isinstance(run.fix, dict) else []
    print("paths:", exit_paths(run, lived, ex["lone"], events, wts))
    tl = {wk: t for wk, _, t in _TLOG}
    for k in range(0, len(outs), 13):
        blk = outs[k:k + 13]
        s = " ".join(f"{r}: pl {np.mean([o['hedonic'][r]['pleasure'] for o in blk]):.3f} su {np.mean([o['hedonic'][r]['s_off'] + o['hedonic'][r]['s_non'] for o in blk]):.3f} "
                     f"tally {tl.get(k + 12, {}).get(r)}" for r in "AB")
        print(f"  wk {k:>3}: both-in {np.mean([o['both_in'] for o in blk]):.2f}  {s}")


# ---- can every verdict happen? -------------------------------------------------------------------------------------------------

def reach():
    res = {}
    # step-5 classes: a planted suffering rise, a planted pleasure fade at flat suffering, a flat life
    p = [0.9] * 26 + [0.9] * 13
    s_up = [0.0] * 26 + [0.2] * 13
    res["suffering"] = classify(p, s_up, 1.0, list(range(13)), list(range(26, 39)))[0]
    p_fade = [0.9] * 26 + [0.8] * 13
    res["quiet"] = classify(p_fade, [0.0] * 39, 1.0, list(range(13)), list(range(26, 39)))[0]
    res["mixed"] = classify(p_fade, [0.0] * 26 + [0.05] * 13, 1.0, list(range(13)), list(range(26, 39)))[0]
    res["no_fall"] = classify(p, [0.0] * 39, 1.0, list(range(13)), list(range(26, 39)))[0]
    assert res == {"suffering": "suffering", "quiet": "quiet", "mixed": "mixed", "no_fall": "no_fall"}, res
    print("step-5 classes reachable:", res)
    # three-version labels: a planted flip in one of three versions reads version-dependent; none reads holds
    rs = {v: {"X": {"together": {"class": c}}} for v, c in (("old", "+"), ("a4", "+"), ("a5", "+"))}
    res["three_same"] = three_way(rs)["X"]["together"]["label"]
    rs["a4"]["X"]["together"]["class"] = "0"
    res["three_flip"] = three_way(rs)["X"]["together"]["label"]
    assert res["three_same"].startswith("holds") and res["three_flip"].startswith("version-dependent"), res
    # P-AUTH: a planted +0.10 formation gain reads missed, 0 reads held
    def rows(shift):
        rng = np.random.default_rng(3)
        out = []
        for i in range(120):
            base = bool(rng.random() < 0.7)
            out.append({"g": "B", "a": f"s{i}", "b": f"t{i}", "formed0": base or (shift > 0 and rng.random() < shift / 0.3),
                        "both_share": 0.8})
        return out
    base = rows(0.0)
    res["pauth_gain"] = p_auth(rows(0.10), base)["P-AUTH"]
    res["pauth_none"] = p_auth(base, base)["P-AUTH"]
    assert res["pauth_gain"] == "missed" and res["pauth_none"] == "held", res
    print("three-version and P-AUTH labels reachable:", {k: res[k] for k in ("three_same", "three_flip", "pauth_gain", "pauth_none")})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "reach.json").write_text(json.dumps(res))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", action="store_true")
    ap.add_argument("--paths-analyze", action="store_true")
    ap.add_argument("--reach", action="store_true")
    ap.add_argument("--kx2", action="store_true")
    ap.add_argument("--flags", default="a4")
    ap.add_argument("--story", action="store_true")
    ap.add_argument("--run")
    ap.add_argument("--arms", default=",".join(A.ARMS))
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--life", nargs=3)
    ap.add_argument("--version", default="a5")
    ap.add_argument("--workers", type=int, default=WORKERS)
    a = ap.parse_args()
    if a.kx2:
        kx2(a.flags, a.workers)
    if a.story:
        story()
    if a.run:
        for name in a.run.split(","):
            run_cfg(name, [x for x in a.arms.split(",") if x], a.every, a.workers)
    if a.analyze:
        analyze()
    if a.life:
        life(*a.life, version=a.version)
    if a.reach:
        reach()
    if a.paths:
        paths(a.workers)
    if a.paths_analyze:
        paths_analyze()


if __name__ == "__main__":
    main()
