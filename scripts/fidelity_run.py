"""Fidelity run (docs/results/fidelity-prereg.md). No model calls.

  uv run python scripts/fidelity_run.py          confirmatory run -> runs/fidelity/results.json, prints the numbers fidelity.md quotes
"""
from __future__ import annotations

import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import fidelity as F  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import stats as S  # noqa: E402

OUT = ROOT / "runs" / "fidelity"
SEEDS5 = range(5)
P2_SEEDS = range(12)


def _p2(args):
    return F.p2_run(*args)


def _p4(args):
    v, a, b, s = args
    r = F.weekly(v, a, b, s)
    return F.need_met_share(r)


def cluster(rows, pairs, ix):
    """{pairing index: mean over seeds of the counted rows}."""
    acc = {}
    for (i, _s), v in rows:
        if v is not None:
            acc.setdefault(i, []).append(v)
    return acc


def main():
    t0 = time.time()
    pairs = F.hand_pairs()
    base = NG.base_cards("author_seed_v2_bindable")
    res = {}

    # P1a and P3 (household negotiation)
    p1a, p3 = {}, {}
    for i, (a, b) in enumerate(pairs):
        for s in SEEDS5:
            r = F.p1a_one(a, b, s, base)
            if r is not None:
                p1a.setdefault(i, []).append(r)
            r = F.p3_one(a, b, s, base)
            if r is not None:
                p3.setdefault(i, []).append(r)
    res["P1a_n_pairings"] = len(p1a)
    res["P1a"] = {"raised": [float(np.mean([x[1] for x in v])) for v in p1a.values()], "base": [float(np.mean([x[0] for x in v])) for v in p1a.values()],
                  "pair_seeds": sum(len(v) for v in p1a.values()), "pair_seeds_total": len(pairs) * len(SEEDS5)}
    res["P3"] = {"d1": [float(np.mean([x[0] for x in v])) for v in p3.values()], "d2": [float(np.mean([x[1] for x in v])) for v in p3.values()],
                 "pair_seeds": sum(len(v) for v in p3.values()), "pair_seeds_total": len(pairs) * len(SEEDS5)}
    print(f"P1a/P3 done {time.time() - t0:.0f}s", flush=True)

    # P1b
    cells = F.p1b_cells()
    res["P1b"] = {"hi": [], "lo": [], "ctl_hi": [], "ctl_lo": []}
    for d, o1 in cells:
        hi, lo = F.p1b_cell("exit-allowed", d, o1)
        chi, clo = F.p1b_cell("no-exit", d, o1)
        res["P1b"]["hi"].append(hi); res["P1b"]["lo"].append(lo); res["P1b"]["ctl_hi"].append(chi); res["P1b"]["ctl_lo"].append(clo)

    with Pool(8) as pool:
        v = pool.map(_p2, [("voluntary", s) for s in P2_SEEDS] + [("compulsory", s) for s in P2_SEEDS])
        res["P2"] = {"voluntary": v[:len(P2_SEEDS)], "compulsory": v[len(P2_SEEDS):]}
        print(f"P2 done {time.time() - t0:.0f}s", flush=True)
        tasks = [(var, a, b, s) for var in ("needs_duty", "free_chaotic") for (a, b) in pairs for s in SEEDS5]
        out = pool.map(_p4, tasks, chunksize=5)
    n = len(pairs) * len(SEEDS5)
    nd = np.array(out[:n]).reshape(len(pairs), len(SEEDS5)).mean(1)
    fc = np.array(out[n:]).reshape(len(pairs), len(SEEDS5)).mean(1)
    res["P4"] = {"needs_duty": nd.tolist(), "free_chaotic": fc.tolist()}
    print(f"P4 done {time.time() - t0:.0f}s", flush=True)

    # P5 deterministic checks
    same = True
    E = D = Eh = Dh = 0
    for a, b in pairs:
        for s in range(3):
            tr = F.weekly("trap", a, b, s)
            same &= F.same_run(tr, F.weekly("contact_free", a, b, s))
            e, d = F.distress_exit(tr); E += e; D += d
            e, d = F.distress_exit(F.weekly("exit_half", a, b, s)); Eh += e; Dh += d
    res["P5"] = {"trap_equals_contact_free": bool(same), "trap_exits": E, "trap_distress_weeks": D, "half_exits": Eh, "half_distress_weeks": Dh}

    # P6
    pers = F.personas9()
    g = [F.p6_persona(p) for p in pers]
    res["P6"] = {"first": [x[0] for x in g], "last": [x[1] for x in g], "rel": [x[2] for x in g], "control": F.adaptation_control()}

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(res, indent=1))
    report(res)
    print(f"total {time.time() - t0:.0f}s")


def report(res):
    rows = []   # (id, est, ci, test, direction, threshold, d)
    a, b = np.array(res["P1a"]["raised"]), np.array(res["P1a"]["base"])
    rows.append(("P1a", a, b, True, +1, 0.02))
    hi, lo = np.array(res["P1b"]["hi"]), np.array(res["P1b"]["lo"])
    rows.append(("P1b", hi, lo, True, +1, 0.05))
    rows.append(("P2", np.array(res["P2"]["voluntary"]), np.array(res["P2"]["compulsory"]), False, +1, 0.10))
    rows.append(("P3", np.array(res["P3"]["d1"]), np.array(res["P3"]["d2"]), True, +1, 0.15))
    rows.append(("P4", np.array(res["P4"]["needs_duty"]), np.array(res["P4"]["free_chaotic"]), True, -1, 0.05))
    first, last = np.array(res["P6"]["first"]), np.array(res["P6"]["last"])
    rel = np.array(res["P6"]["rel"])
    tests = []
    for pid, x, y, paired, dr, thr in rows:
        t, ci = F.test_effect(x, y, paired=paired, direction=dr)
        tests.append((pid, x, y, paired, dr, thr, t, ci))
    t6 = S.permutation_test(first, last, paired=True, alternative="greater")
    ci6 = S.bootstrap_ci(rel)
    tests.append(("P6", rel, np.zeros_like(rel), True, +1, 0.10, t6, ci6))
    padj = S.holm([t[6].p for t in tests])
    print(f"{'id':5} {'n':>3} {'est':>8} {'95% CI':>20} {'p':>8} {'p_holm':>8} {'d':>7} verdict")
    for (pid, x, y, paired, dr, thr, t, ci), ph in zip(tests, padj):
        est = float(np.mean(x - y)) if paired else float(np.mean(x) - np.mean(y))
        d = S.cohens_d(x, y, paired=paired) if pid != "P6" else float("nan")
        print(f"{pid:5} {len(x):3d} {est:8.4f} {str(ci):>20} {t.p:8.4f} {ph:8.4f} {d:7.2f} {F.verdict(est, ci, ph, dr, thr)}")
    print("P1a pair-seeds counted", res["P1a"]["pair_seeds"], "/", res["P1a"]["pair_seeds_total"], "pairings", res["P1a_n_pairings"])
    print("P3 pair-seeds counted", res["P3"]["pair_seeds"], "/", res["P3"]["pair_seeds_total"], "pairings", len(res["P3"]["d1"]))
    print("P1b no-exit control, max |hi-lo|:", float(np.max(np.abs(np.array(res["P1b"]["ctl_hi"]) - np.array(res["P1b"]["ctl_lo"])))))
    print("P5", res["P5"]); print("P6 control (scale week1, week20):", res["P6"]["control"])


if __name__ == "__main__":
    if "--analyze" in sys.argv:
        report(json.loads((OUT / "results.json").read_text()))
    else:
        main()
