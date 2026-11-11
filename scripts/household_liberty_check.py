"""Slice 1 of the household evolution run: liberty v2 next to the hand-made freedom score and plain empowerment, for the existing
household rule sets. DESCRIPTIVE check run (no prediction, no verdict). Output: runs/household-liberty/rows.json and a markdown table.

  uv run python scripts/household_liberty_check.py [--seeds 1] [--md docs/results/household-liberty-table.md]

57 pairings (15 hand-persona pairs + 42 ordered pairs with a pressing persona), seed 0, 156 weeks, liberty and plain empowerment at weeks
0, 52, 104 with k = 2 (min over the two partners, mean over snapshots). Imposed rule sets (no negotiation). No model calls.
Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.
"""
import argparse
import json
import sys
import time
from itertools import permutations
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import household_oracle as O  # noqa: E402
from mar import liberty as L  # noqa: E402
from mar import personas as P  # noqa: E402
from mar.worlds import household as H  # noqa: E402

PRESSING = ("p-controller", "p-freerider", "p-overasker")
VARIANTS = ("baseline", "needs_duty", "share_duty", "no_pressure_wall", "no_pressure_sanctioned", "free_chaotic", "exit_half",
            "veto_consent", "author_seed", "author_seed_nocontrol", "author_seed_v2_bindable", "author_seed_v2_free_exit",
            "author_seed_v2_nocommit", "trap", "contact_free")
SNAPSHOTS = (0, 52, 104)
OUT = ROOT / "runs" / "household-liberty"
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


def task(args):
    variant, a, b, seed, cohort = args
    ps = personas()
    r = L.household_run_liberty(H.load_variant(variant), (ps[a], ps[b]), seed, snapshots=SNAPSHOTS)
    out = r["run"].outcomes
    sc, hs = O.score(out), O.hedonic_summary(out)
    return {"variant": variant, "a": a, "b": b, "cohort": cohort, "seed": seed, "freedom": sc["freedom"], "cooperation": sc["cooperation"],
            "pleasure": hs["pleasure"], "fail": hs["fail"], "liberty": r["liberty_min"], "bits": r["bits_min"], "d": r["d_mean"],
            "ado": r["ado_mean"], "n_open": r["n_open"]}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def table(rows):
    lines = ["| rule set | hand-made freedom | plain empowerment (bits, min partner, k=2) | liberty v2 (bits, min partner, k=2) | domination exposure d | agreement-dependent options | cooperation | pleasure | fail share |",
             "|---|---|---|---|---|---|---|---|---|"]
    for v in VARIANTS:
        rs = [r for r in rows if r["variant"] == v]
        lines.append(f"| {v} | {mean(r['freedom'] for r in rs):.3f} | {mean(r['bits'] for r in rs):.2f} | {mean(r['liberty'] for r in rs):.2f} | "
                     f"{mean(r['d'] for r in rs):.2f} | {mean(r['ado'] for r in rs):.2f} | {mean(r['cooperation'] for r in rs):.3f} | "
                     f"{mean(r['pleasure'] for r in rs):.3f} | {mean(float(r['fail']) for r in rs):.2f} |")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--md", default=None)
    a = ap.parse_args(argv)
    tasks = [(v, x, y, s, c) for v in VARIANTS for x, y, c in pairings() for s in range(a.seeds)]
    t0, rows = time.time(), []
    with Pool(8) as pool:
        for i, r in enumerate(pool.imap_unordered(task, tasks, chunksize=2), 1):
            rows.append(r)
            if i % 100 == 0:
                print(f"  {i}/{len(tasks)} {time.time() - t0:.0f}s", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "rows.json").write_text(json.dumps(rows))
    t = table(rows)
    print(t)
    print(f"{len(rows)} runs in {time.time() - t0:.0f}s")
    if a.md:
        Path(a.md).write_text(t + "\n")


if __name__ == "__main__":
    main()
