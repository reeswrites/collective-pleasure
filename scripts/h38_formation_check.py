"""H38 formation check (docs/results/h38-formation-check-prereg.md): does H38's gain from pairing pressure survive when agents decide to
form and stay on the verdict's own yardstick (each member's own clipped pleasure, 52-week rollouts) instead of 26 weeks of net wellbeing?
Same world, pairings and seeds as H38 (scripts/h38_pairing_run.py). Scripted persona agents, no model calls.
Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

  uv run python scripts/h38_formation_check.py --diagnose   the rule inputs under each yardstick vs the realized lives (L0, old rule)
  uv run python scripts/h38_formation_check.py --run        the confirmatory arms under the corrected rule (at most 3 workers)
  uv run python scripts/h38_formation_check.py --analyze    prereg vs actual; writes runs/h38-formation/analysis.json
  add --v2 to --run / --analyze: Amendment 1, the recalibrated agents and bills that hurt. The G arms and the old-rule arms O-L0, O-L4,
  O-W4 (H38's L0, L4, W4) all rerun under them; rows in runs/h38-formation-v2/.
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
import h38_pairing_run as H38  # noqa: E402
from mar import exit_fallback as EF  # noqa: E402
from mar import exit_items as EI  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "h38-formation"
OLD_ROWS = ROOT / "runs" / "h38-pairing" / "rows.jsonl"
WORKERS = 3
GOOD = {"decide_on": "pleasure", "decide_weeks": 52}          # the corrected rule
# Decomposition (descriptive, L0 only): yardstick alone, window alone.
RULES = {"good": GOOD, "pl26": {"decide_on": "pleasure", "decide_weeks": 26}, "net52": {"decide_on": "net", "decide_weeks": 52}}
# Arm name -> (pairing config, rule name). Confirmatory: G-L0, G-L4, G-W4. Descriptive: G-L1, the dial's middle. (The yardstick-alone
# and window-alone rules are compared at week-0 formation only, in --diagnose.)
ARMS = {"G-L0": (PR.dial(0), "good"), "G-L4": (PR.dial(4), "good"), "G-W4": (PR.dial(4, parts=("withdraw",)), "good"),
        "G-L1": (PR.dial(1), "good")}
OLD_ARMS = {"O-L0": "L0", "O-L4": "L4", "O-W4": "W4"}    # Amendment 1 (v2): H38's own arms, old rule, rerun under the new agents
V2 = {"agent_values": "v2", "bills_hurt": True}
V2B = {"agent_values": "v2b", "bills_hurt": True}         # Amendment 2: the bill horizon (docs/results/agent-bill-horizon-prereg.md)
FORCED = "F-L0"     # descriptive: old rule, formation forced at week 0 (decline=False), for the diagnosis
MARGIN = 0.007      # prereg: the L4 gain "falls to within the margin" if G-L4 minus G-L0 is below this (a third of H38's +0.021)


def task(args):
    arm, a, b, seeds = args[:4]
    fix = args[4] if len(args) > 4 else None
    t0 = time.time()
    out = []
    for s in seeds:
        if arm == FORCED:
            run, lived, rd = H38.play(PR.dial(0), a, b, s, stay=False, decline=False)
        elif arm in OLD_ARMS:
            run, lived, rd = H38.play(H38.ARMS[OLD_ARMS[arm]], a, b, s, stay=True, rule=fix)
        elif fix:
            pc, rule = ARMS[arm]
            run, lived, rd = H38.play(pc, a, b, s, stay=True, rule={**RULES[rule], **fix})
        else:
            pc, rule = ARMS[arm]
            run, lived, rd = H38.play(pc, a, b, s, stay=True, rule=RULES[rule])
        out.append(H38.record(run, lived, rd, arm, a, b, s))
    return out, time.time() - t0


def run(arms, f, workers=WORKERS, fix=None):
    workers = min(workers, 3)
    OUT.mkdir(parents=True, exist_ok=True)
    done = set()
    if f.exists():
        done = {(r["arm"], r["a"], r["b"]) for r in H38.load(f)}
    tasks = [(arm, a, b, H38.CONFIRM["seeds"], fix) for (a, b) in H38.pairings(H38.CONFIRM) for arm in arms if (arm, a, b) not in done]
    print(f"{len(tasks)} tasks, {workers} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, f.open("a") as fh:
        for i, (rows, dt) in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            fh.write("\n".join(json.dumps(r) for r in rows) + "\n")
            fh.flush()
            if i % 25 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {dt:.1f}s wall {time.time() - t0:.0f}s", flush=True)


# ---- diagnosis: what the week-0 rule sees under each yardstick ------------------------------------------------------------------

def _inputs(args):
    """Week-0 rule inputs (together W, outside O, per member) for one pair-seed under each yardstick, in the H38 L0 world."""
    a, b, seed = args
    ps = RT.personas()
    pa, pb = ps[a], ps[b]
    cards = H.load_variant("baseline")
    out = {"a": a, "b": b, "seed": seed}
    for name, rule in {"old": {}, **RULES}.items():
        for c in (NG._RC, NG._PC, NG._BC):
            c.clear()
        fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **rule)
        with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[H38.CELL]):
            W = NG.baseline_value(pa, pb, seed, cards)
            O = {r: NG.outside_value(p, r, NG.START_HOLDINGS[0] + NG.START_HOLDINGS[1], seed)[0] for r, p in zip("AB", (pa, pb))}
        out[name] = {"W": W, "O": O, "form": all(W[r] >= O[r] for r in "AB")}
    return out


def diagnose():
    """Writes runs/h38-formation/diagnose.json: rule inputs under each yardstick; forced-formation lives vs the H38 L0 lives."""
    OUT.mkdir(parents=True, exist_ok=True)
    keys = [(a, b, s) for (a, b) in H38.pairings(H38.CONFIRM) for s in H38.CONFIRM["seeds"]]
    with Pool(WORKERS) as p:
        inp = p.map(_inputs, keys, chunksize=4)
    (OUT / "inputs.jsonl").write_text("\n".join(json.dumps(x) for x in inp) + "\n")
    run([FORCED], OUT / "forced.jsonl")


def diag_report():
    inp = {(x["a"], x["b"], x["seed"]): x for x in H38.load(OUT / "inputs.jsonl")}
    old = {(r["a"], r["b"], r["seed"]): r for r in H38.load(OLD_ROWS) if r["arm"] == "L0"}
    forced = {(r["a"], r["b"], r["seed"]): r for r in H38.load(OUT / "forced.jsonl")}
    res = {"n": len(inp), "form_share": {k: float(np.mean([x[k]["form"] for x in inp.values()])) for k in ("old", *RULES)},
           "L0_formed0": float(np.mean([r["formed0"] for r in old.values()]))}
    # Which members block formation, and on which margin, under the old rule
    gaps = {k: [] for k in ("old", *RULES)}
    for x in inp.values():
        for k in gaps:
            for r in "AB":
                gaps[k].append(x[k]["W"][r] - x[k]["O"][r])
    res["W_minus_O_mean"] = {k: float(np.mean(v)) for k, v in gaps.items()}
    res["W_mean"] = {k: float(np.mean([x[k]["W"][r] for x in inp.values() for r in "AB"])) for k in gaps}
    res["O_mean"] = {k: float(np.mean([x[k]["O"][r] for x in inp.values() for r in "AB"])) for k in gaps}
    # The realized counterfactual: declined pair-seeds at L0, forced to form vs as lived (old rule)
    dec = [k for k, r in old.items() if not r["formed0"] and k in forced]
    d_pl = np.array([forced[k]["pl"] - old[k]["pl"] for k in dec])
    d_net = np.array([forced[k]["net"] - old[k]["net"] for k in dec])
    both = np.array([all(forced[k][r]["pl"] > old[k][r]["pl"] for r in "AB") for k in dec])
    res["declined"] = {"n": len(dec), "d_pl_forced_minus_lived": float(d_pl.mean()), "share_pl_better": float(np.mean(d_pl > 0)),
                       "share_both_members_pl_better": float(both.mean()), "d_net": float(d_net.mean()),
                       "share_net_better": float(np.mean(d_net > 0))}
    frm = [k for k, r in old.items() if r["formed0"] and k in forced]
    res["formed"] = {"n": len(frm), "d_pl_forced_minus_lived": float(np.mean([forced[k]["pl"] - old[k]["pl"] for k in frm]))}
    # Agreement of each rule's week-0 call with the realized per-member pleasure comparison over 156 weeks (declined pairs only have
    # both lives; formed pairs' lived = forced, so they carry no counterfactual)
    agree = {}
    for k in ("old", *RULES):
        hits = [x for x in dec if inp[x][k]["form"] == bool(all(forced[x][r]["pl"] > old[x][r]["pl"] for r in "AB"))]
        agree[k] = {"declined_now_formed": float(np.mean([inp[x][k]["form"] for x in dec])), "agree_with_realized": len(hits) / len(dec)}
    res["rule_on_declined"] = agree
    # Where the old rule's gap comes from: per member at decline, net vs pleasure, 26 vs 156 realized
    print(json.dumps(res, indent=1))
    (OUT / "diagnose.json").write_text(json.dumps(res, indent=1))
    return res


# ---- analysis ------------------------------------------------------------------------------------------------------------------

def analyze(new=None, write=True, old=None):
    """old: rows for the old-rule arms L0, L1, L4, W4 (default: H38's own rows). Amendment 1 passes the v2 reruns, relabelled."""
    new = H38.load(OUT / "rows.jsonl") if new is None else new
    old = [r for r in H38.load(OLD_ROWS) if r["arm"] in ("L0", "L1", "L4", "W4")] if old is None else old
    rows = new + old
    K = H38.KEYS
    have = {r["arm"] for r in rows}
    res = {"table": H38.table(rows, [x for x in ["L0", "L1", "L4", "W4", *ARMS] if x in have]), "diffs": {}}

    def diff(hi, lo, key="pleasure", alt=None):
        d, ks = H38.paired(rows, hi, lo, K[key])
        o = {"est": float(d.mean()), "ci": H38.boot_ci(d), "n": len(ks)}
        if alt:
            o["p"] = H38.signflip_p(d, alt)
        return o
    for name, hi, lo, alt in (("C1 G-L4 - G-L0", "G-L4", "G-L0", "greater"), ("C2 G-W4 - G-L0", "G-W4", "G-L0", "less"),
                              ("C3 G-L0 - L0", "G-L0", "L0", "greater"), ("old L4 - L0", "L4", "L0", None),
                              ("old W4 - L0", "W4", "L0", None), ("G-L1 - G-L0", "G-L1", "G-L0", None)):
        if hi not in have or lo not in have:
            continue
        res["diffs"][name] = {k: diff(hi, lo, k, alt if k == "pleasure" else None)
                              for k in ("pleasure", "net", "together_share", "formed0", "pleasure_wo_direct", "p_raw")}
    # C1's gain relative to the old L4 gain, paired by pairing (difference in differences)
    a, ka = H38.paired(rows, "G-L4", "G-L0", K["pleasure"])
    b, kb = H38.paired(rows, "L4", "L0", K["pleasure"])
    bi = dict(zip(kb, b))
    dd = np.array([x - bi[k] for x, k in zip(a, ka) if k in bi])
    res["diffs"]["G-gain minus old gain"] = {"est": float(dd.mean()), "ci": H38.boot_ci(dd)}
    res["pushed_in_G"] = H38.pushed_in(rows, "G-L4", "G-L0")
    if "C2 G-W4 - G-L0" not in res["diffs"]:          # the descriptive v2-without-bills arm set has no G-W4: no verdicts
        if write:
            (OUT / "analysis.json").write_text(json.dumps(res, indent=1))
        return res
    c1 = res["diffs"]["C1 G-L4 - G-L0"]["pleasure"]
    c2 = res["diffs"]["C2 G-W4 - G-L0"]["pleasure"]
    c3 = res["diffs"]["C3 G-L0 - L0"]["pleasure"]
    fs = res["diffs"]["C3 G-L0 - L0"]["formed0"]
    adj = H38.holm([c1["p"], c2["p"], c3["p"]])
    res["holm"] = {"C1": adj[0], "C2": adj[1], "C3": adj[2]}
    res["verdicts"] = {
        "C1": ("survives" if (c1["est"] >= MARGIN and c1["ci"][0] > 0 and adj[0] < 0.05) else
               "within margin" if c1["est"] < MARGIN else "weak"),
        "C2": "holds" if (c2["est"] < 0 and c2["ci"][1] < 0 and adj[1] < 0.05) else "fails",
        "C3": "holds" if (c3["est"] > 0 and c3["ci"][0] > 0 and adj[2] < 0.05 and fs["est"] > 0 and fs["ci"][0] > 0) else "fails",
    }
    if write:
        print(json.dumps(res, indent=1))
        (OUT / "analysis.json").write_text(json.dumps(res, indent=1))
    return res


def reach():
    """Prereg "Can every verdict happen?": the analysis run on H38's own rows relabelled as G arms (no new runs)."""
    old = H38.load(OLD_ROWS)

    def as_g(m):
        return [{**r, "arm": g} for g, src in m.items() for r in old if r["arm"] == src]
    cases = {"C1 survives (G = old L0, L4)": {"G-L0": "L0", "G-L4": "L4", "G-W4": "W4", "G-L1": "L1"},
             "C1 within margin (G-L4 = old L0.5)": {"G-L0": "L0", "G-L4": "L0.5", "G-W4": "W4", "G-L1": "L1"},
             "C1 within margin, negative (G-L4 = old W4)": {"G-L0": "L0", "G-L4": "W4", "G-W4": "W4", "G-L1": "L1"},
             "C2 fails, C3 fails (G-W4 = old R4, G-L0 = old W4)": {"G-L0": "W4", "G-L4": "L4", "G-W4": "R4", "G-L1": "L1"},
             "C3 holds (G-L0 = old L1)": {"G-L0": "L1", "G-L4": "L4", "G-W4": "W4", "G-L1": "L1"}}
    noise = {}

    def noisy():         # synthetic: G-L4 = old L0 + 0.008 + alternating +-0.08 per pairing, so the estimate clears the margin but the CI does not
        rows = as_g({"G-L0": "L0", "G-W4": "W4", "G-L1": "L1"})
        for r in old:
            if r["arm"] == "L0":
                e = noise.setdefault((r["a"], r["b"]), 0.08 * (1 if len(noise) % 2 else -1))
                rows.append({**r, "arm": "G-L4", "pl": r["pl"] + 0.008 + e})
        return rows
    out = {}
    for name, m in [*cases.items(), ("C1 weak (synthetic: +0.008 with pairing noise)", None)]:
        r = analyze(as_g(m) if m else noisy(), write=False)
        out[name] = {"verdicts": r["verdicts"], "C1": r["diffs"]["C1 G-L4 - G-L0"]["pleasure"]}
        print(name, json.dumps(out[name]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--diagnose", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--reach", action="store_true")
    ap.add_argument("--v2", action="store_true", help="Amendment 1: agent_values v2 and bills_hurt; runs/h38-formation-v2/")
    ap.add_argument("--v2nobills", action="store_true", help="descriptive: v2 with bills off; G-L0, G-L4, O-L0, O-L4")
    ap.add_argument("--v2b", action="store_true", help="Amendment 2: agent_values v2b and bills_hurt; runs/h38-formation-v2b/")
    ap.add_argument("--v2bnobills", action="store_true", help="descriptive: v2b with bills off; G-L0, G-L4, O-L0, O-L4")
    a = ap.parse_args()
    global OUT
    if a.v2 or a.v2nobills or a.v2b or a.v2bnobills:
        OUT = ROOT / "runs" / ("h38-formation-v2" if a.v2 else "h38-formation-v2-nobills" if a.v2nobills else
                               "h38-formation-v2b" if a.v2b else "h38-formation-v2b-nobills")
        if a.run:
            if a.v2 or a.v2b:
                run([*ARMS, *OLD_ARMS], OUT / "rows.jsonl", fix=V2 if a.v2 else V2B)
            else:
                run(["G-L0", "G-L4", "O-L0", "O-L4"], OUT / "rows.jsonl", fix={"agent_values": "v2" if a.v2nobills else "v2b"})
        if a.analyze:
            rows = H38.load(OUT / "rows.jsonl")
            new = [r for r in rows if r["arm"] in ARMS]
            old = [{**r, "arm": OLD_ARMS[r["arm"]]} for r in rows if r["arm"] in OLD_ARMS]
            analyze(new, old=old)
        return
    if a.reach:
        reach()
    if a.diagnose:
        diagnose()
    if a.diagnose or a.report:
        diag_report()
    if a.run:
        run(list(ARMS), OUT / "rows.jsonl")
    if a.analyze:
        analyze()


if __name__ == "__main__":
    main()
