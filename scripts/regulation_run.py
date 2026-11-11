"""Attuning versus appeasing: partner regulation policies against pressing personas. Prereg: docs/results/regulation-prereg.md.
Results: docs/results/regulation.md. Scripted agents, no model calls, $0.

  uv run python scripts/regulation_run.py --pilot      # EXPLORATORY: seeds 1000..1002; prints effect and spread for the power check
  uv run python scripts/regulation_run.py --run        # the confirmatory run (seeds 0..N-1), writes runs/regulation/results.json
  uv run python scripts/regulation_run.py --analyze    # re-print every number from runs/regulation/results.json
"""
import argparse
import json
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from mar import regulation as R  # noqa: E402
from mar import stats as S  # noqa: E402

OUT = ROOT / "runs" / "regulation"
SEEDS = tuple(range(10))                 # set by the power check in the prereg (amended there if the pilot says otherwise)
PILOT_SEEDS = (1000, 1001, 1002)         # EXPLORATORY, never used in the confirmatory data
PRIMARY = "author_seed_v2_free_exit"
ALPHA = 0.05


def _task(a):
    return R.run_pair(*a)


def run_all(seeds, rulesets=R.RULESETS, modes=R.MODES, workers=8):
    ts = [(rs, f, o, role, sd, m) for rs in rulesets for (f, o, role) in R.pairings() for sd in seeds for m in modes]
    with Pool(workers) as pool:
        return pool.map(_task, ts, chunksize=8)


def table(rows, ruleset, mode, key):
    """{pairing: mean over seeds of `key`}: the pairing (presser, partner, role) is the unit of resampling."""
    by = {}
    for r in rows:
        if r["ruleset"] == ruleset and r["mode"] == mode:
            by.setdefault((r["presser"], r["partner"], r["role"]), []).append(float(r[key]))
    return {k: sum(v) / len(v) for k, v in by.items()}


def paired(rows, ruleset, key, m1="appease", m0="attune"):
    """-> (pairings, m1 values, m0 values) aligned by pairing."""
    a, b = table(rows, ruleset, m1, key), table(rows, ruleset, m0, key)
    ks = sorted(set(a) & set(b))
    return ks, [a[k] for k in ks], [b[k] for k in ks]


def _perm(x, y, alt):
    return S.permutation_test(x, y, paired=True, alternative=alt, n_perm=20000, seed=0).p


def _ci(x, y):
    return S.mean_difference(x, y, paired=True, seed=0)


def predictions(rows, ruleset):
    """The four predictions for one rule set. -> {id: dict(p, effect interval, detail)}. All paired over pairings (seeds averaged within)."""
    out = {}
    # R1: presser's gain over partner is larger against APPEASE than against ATTUNE
    _, g1, g0 = paired(rows, ruleset, "gain")
    out["R1"] = {"p": _perm(g1, g0, "greater"), "ci": _ci(g1, g0), "mean_appease": sum(g1) / len(g1), "mean_attune": sum(g0) / len(g0)}
    # R2: partner lifetime pleasure lower under APPEASE (a) AND fewer refusal weeks under APPEASE (b); both reported
    _, a1, a0 = paired(rows, ruleset, "partner_pleasure")
    _, c1, c0 = paired(rows, ruleset, "refusal_weeks")
    _, k1, k0 = paired(rows, ruleset, "conflict_weeks")
    pa, pb = _perm(a1, a0, "less"), _perm(c1, c0, "less")
    out["R2"] = {"p": max(pa, pb), "p_pleasure": pa, "p_refusals": pb, "ci_pleasure": _ci(a1, a0), "ci_refusals": _ci(c1, c0),
                 "ci_pressing_weeks": _ci(k1, k0), "mean_pleasure": (sum(a1) / len(a1), sum(a0) / len(a0))}
    # R3: presser's own lifetime pleasure LOWER against ATTUNE than against APPEASE (H01 direction: pressing backfires under free exit)
    _, p1, p0 = paired(rows, ruleset, "presser_pleasure")
    out["R3"] = {"p": _perm(p0, p1, "less"), "ci": _ci(p0, p1), "mean_appease": sum(p1) / len(p1), "mean_attune": sum(p0) / len(p0)}
    # R4: pressing acts borne by the partner (executed requests, vetoes, takes by the presser) higher under APPEASE
    _, r1, r0 = paired(rows, ruleset, "pressing_acts")
    out["R4"] = {"p": _perm(r1, r0, "greater"), "ci": _ci(r1, r0), "mean_appease": sum(r1) / len(r1), "mean_attune": sum(r0) / len(r0)}
    return out


def analyze(rows, out=print):
    res = {}
    for rs in R.RULESETS:
        res[rs] = predictions(rows, rs)
    fam = ["R1", "R2", "R3", "R4"]
    adj = S.holm([res[PRIMARY][k]["p"] for k in fam])
    out(f"seeds {sorted({r['seed'] for r in rows})}  runs {len(rows)}")
    for rs in R.RULESETS:
        out(f"== {rs}")
        for k in fam:
            v = res[rs][k]
            extra = {kk: (str(vv) if not isinstance(vv, float) else round(vv, 4)) for kk, vv in v.items() if kk != "p"}
            out(f"  {k}: p={v['p']:.4g}  {extra}")
    out("Holm over R1..R4 at the primary rule set:", {k: round(a, 4) for k, a in zip(fam, adj)})
    for rs in R.RULESETS:
        out(f"-- descriptive means, {rs}")
        for mode in R.MODES:
            sel = [r for r in rows if r["ruleset"] == rs and r["mode"] == mode]
            n = len(sel)
            m = lambda k: sum(float(r[k]) for r in sel) / n
            out(f"  {mode:9s} presser {m('presser_pleasure'):7.2f} partner {m('partner_pleasure'):7.2f} gain {m('gain'):7.2f} "
                f"acts {m('pressing_acts'):6.1f} conflict_wks {m('conflict_weeks'):6.1f} refusal_wks {m('refusal_weeks'):5.1f} "
                f"yield_wks {m('yield_weeks'):5.1f} partner_left {m('partner_left'):.2f} presser_left {m('presser_left'):.2f} together {m('weeks_together'):6.1f}")
    return res, {k: a for k, a in zip(fam, adj)}


def pilot_numbers(rows, out=print):
    """EXPLORATORY: effect and sd of the paired pairing-level differences, for the power check."""
    spec = {"R1": ("gain", "appease", "attune", +1), "R2": ("partner_pleasure", "appease", "attune", -1),
            "R3": ("presser_pleasure", "attune", "appease", -1), "R4": ("pressing_acts", "appease", "attune", +1)}
    import numpy as np
    for rs in R.RULESETS:
        for k, (key, m1, m0, sign) in spec.items():
            _, x, y = paired(rows, rs, key, m1, m0)
            d = np.array(x) - np.array(y)
            out(f"  {rs:26s} {k} {key:17s} effect {d.mean():8.3f}  sd {d.std(ddof=1):8.3f}  n_pairings {len(d)}")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pilot", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--analyze", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.pilot:
        rows = run_all(PILOT_SEEDS, workers=a.workers)
        (OUT / "pilot.json").write_text(json.dumps(rows))
        print("EXPLORATORY pilot (seeds 1000..1002); not a result")
        pilot_numbers(rows)
        analyze(rows)
    elif a.run:
        rows = run_all(SEEDS, workers=a.workers)
        (OUT / "results.json").write_text(json.dumps(rows))
        analyze(rows)
    else:
        analyze(json.loads((OUT / "results.json").read_text()))


if __name__ == "__main__":
    main()
