"""First household evolution run (docs/results/household-evolve-prereg.md). Scripted agents, no model calls.

  uv run python scripts/household_evolve_run.py --pilot       EXPLORATORY: one line, 2 generations (sizing only; its numbers are never cited)
  uv run python scripts/household_evolve_run.py --run         the confirmatory run: LINES independent evolution lines, then validation
  uv run python scripts/household_evolve_run.py --analyze     prereg vs actual (prints the numbers docs/results/household-evolve.md quotes)
  uv run python scripts/household_evolve_run.py --freeze      writes each line's final elite as YAML cards under docs/results/household-evolve-elites/

Training set: the 35 non-denylisted personas (6 hand, 3 pressing, 26 grid), pairings and conditions redrawn every generation from the
training distribution in mar.world_api. The held-out exam (docs/results/household-exam-prereg.md) is NOT used or read here: the only item
taken from it is the six-id DENYLIST in mar.world_api. Validation (a fifth of the pairings, never selected on) gives the overfitting gap.
Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.
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
from mar import evolve as EV  # noqa: E402
from mar import stats as S  # noqa: E402
from mar import world_api as W  # noqa: E402
from mar.cards import make_card  # noqa: E402

OUT = ROOT / "runs" / "household-evolve"
ELITES = ROOT / "docs" / "results" / "household-evolve-elites"
LINES = 16
CFG = EV.HConfig(pop=8, offspring=6, generations=6, runs=6, k=3, max_rules=16)
SEED_NAMES = ("author_seed_v2_bindable", "author_seed_v2_free_exit", "baseline", "needs_duty", "no_pressure_wall")
AUTHOR = "author_seed_v2_bindable"
VAL_SEED, VAL_RUNS = 777, 30
MARGINS = {"pleasure": 0.02, "no_fail": 0.05, "liberty": 0.25, "cooperation": 0.02}      # P1 margins (prereg)
TRADE = 0.05                                                                              # P4: normalized objective difference
OBJ = W.HouseholdEvolveWorld.objectives


def card_dicts(spec):
    return [dataclasses.asdict(c) for c in spec]


def cards_from(dicts):
    return tuple(make_card(d) for d in dicts)


def val_ctx():
    return W.make_context(VAL_SEED, 0, VAL_RUNS, split="val", tag="val")


def seed_task(name):
    w = W.HouseholdEvolveWorld()
    sc, ev = w.score_runs(w.load_spec(name), val_ctx())
    return name, sc


def line_task(line):
    t0 = time.time()
    w = W.HouseholdEvolveWorld()
    seeds = {n: w.load_spec(n) for n in SEED_NAMES}
    res = EV.evolve_household(w, seeds, line, CFG, log_path=OUT / f"line-{line:02d}.jsonl")
    vc = val_ctx()
    front = [i for i in res["pop"] if i.rank == 0]
    rows = []
    for i in front:
        v, _ = w.score_runs(i.spec, vc)
        rows.append({"cards": card_dicts(i.spec), "train": i.scores, "val": v, "n_rules": i.n_rules, "op": i.op,
                     "protections": W.hh_protections(i.spec), "elite": i is res["elite"],
                     "redundant": W.hh_redundant_cards(i.spec)})
    return {"line": line, "front": rows, "log": res["log"], "seconds": time.time() - t0}


def run(lines=LINES, workers=8):
    # 8 worker processes: two waves of eight lines
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with Pool(workers) as pool:
        seeds = dict(pool.map(seed_task, SEED_NAMES))
        out = []
        for i, r in enumerate(pool.imap_unordered(line_task, range(1, lines + 1)), 1):
            out.append(r)
            print(f"  line {r['line']} done ({i}/{lines}) {r['seconds']:.0f}s, elapsed {time.time() - t0:.0f}s", flush=True)
    out.sort(key=lambda r: r["line"])
    (OUT / "results.json").write_text(json.dumps({"cfg": dataclasses.asdict(CFG), "seeds_val": seeds, "lines": out}))
    print(f"{lines} lines in {time.time() - t0:.0f}s")


def _pilot_line(seed):
    w = W.HouseholdEvolveWorld()
    t0 = time.time()
    res = EV.evolve_household(w, {n: w.load_spec(n) for n in SEED_NAMES}, seed, dataclasses.replace(CFG, generations=2),
                              log_path=OUT / f"pilot-{seed}.jsonl")
    return seed, time.time() - t0, [(g["proposed"], g["filter_rejected"], g["accepted"], g["front_size"]) for g in res["log"]]


def pilot():
    """EXPLORATORY sizing: 8 lines in parallel (pilot seeds 501 to 508, never used in the confirmatory run), 2 generations."""
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with Pool(8) as pool:
        for seed, sec, rows in pool.imap_unordered(_pilot_line, range(501, 509)):
            print(seed, f"{sec:.0f}s", rows, flush=True)
    print(f"pilot wall {time.time() - t0:.0f}s")


# ---- analysis -----------------------------------------------------------------------------------------------------------------

def norm(sc):
    return (sc["pleasure"], sc["no_fail"], min(1.0, sc["liberty"] / W.HH_NORM["liberty"]), sc["cooperation"])


def p1_line(front, seed):
    """Some final-front member beats the author's seed on the validation context by >= the margin on >= 1 objective and is not worse by
    more than the margin on any."""
    for m in front:
        d = {o: m["val"][o] - seed[o] for o in OBJ}
        if any(d[o] >= MARGINS[o] for o in OBJ) and all(d[o] >= -MARGINS[o] for o in OBJ):
            return True
    return False


def p4_line(front):
    pts = [norm(m["train"]) for m in front]
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            if any(x - y >= TRADE for x, y in zip(a, b)) and any(y - x >= TRADE for x, y in zip(a, b)):
                return True
    return False


def analyze():
    R = json.loads((OUT / "results.json").read_text())
    L = R["lines"]
    seed = R["seeds_val"][AUTHOR]
    n = len(L)
    elites = [next(m for m in l["front"] if m["elite"]) for l in L]
    p1 = [p1_line(l["front"], seed) for l in L]
    p1e = [p1_line([e], seed) for e in elites]
    p2 = [e["protections"]["no_veto"] and e["protections"]["free_exit"] for e in elites]
    prop = sum(g["accepted"] + g["filter_rejected"] for l in L for g in l["log"])
    rej = sum(g["filter_rejected"] for l in L for g in l["log"])
    p4 = [p4_line(l["front"]) for l in L]
    gap = np.array([np.mean(norm(e["train"])) - np.mean(norm(e["val"])) for e in elites])
    print(f"lines {n}; seconds mean {np.mean([l['seconds'] for l in L]):.0f}")
    print(f"P1 (any front member beats author's seed): {sum(p1)}/{n}; elite itself {sum(p1e)}/{n}; sign test p={S.sign_test(sum(p1), n):.4f}")
    print(f"P2 (elite keeps no-veto and free exit): {sum(p2)}/{n}; p={S.sign_test(sum(p2), n):.4f}; "
          f"no_veto {sum(e['protections']['no_veto'] for e in elites)}, free_exit {sum(e['protections']['free_exit'] for e in elites)}")
    ci = S.clopper_pearson(rej, prop)
    print(f"P3 (filter rejects): {rej}/{prop} = {rej / prop:.3f}, CP95 [{ci.lo:.3f}, {ci.hi:.3f}]")
    by = {}
    for l in L:
        for g in l["log"]:
            for k, v in g["rejected_by_reason"].items():
                by[k] = by.get(k, 0) + v
    print("   by reason:", by)
    print(f"P4 (front has a trade-off pair): {sum(p4)}/{n}; p={S.sign_test(sum(p4), n):.4f}")
    t = S.permutation_test(gap, np.zeros(n), paired=True, alternative="greater", n_perm=20000, seed=1)
    bc = S.bootstrap_ci(gap, n_boot=5000, seed=1)
    print(f"P5 (elite gap train-val, mean of normalized objectives): mean {gap.mean():.4f}, CI [{bc.lo:.4f}, {bc.hi:.4f}], p={t.p:.4f}")
    ps = [S.sign_test(sum(p1), n), S.sign_test(sum(p2), n), S.clopper_pearson(rej, prop).lo, S.sign_test(sum(p4), n), t.p]
    print("Holm over P1,P2,P4,P5:", [round(x, 4) for x in S.holm([ps[0], ps[1], ps[3], ps[4]])])
    return R


def freeze():
    R = json.loads((OUT / "results.json").read_text())
    ELITES.mkdir(parents=True, exist_ok=True)
    man = {"selection_rule": "rank-0 member of the final population with the highest mean of (pleasure, no_fail, min(1, liberty/6), cooperation); ties by fewer cards (mar.evolve.pick_elite_h)",
           "lines": {}}
    for l in R["lines"]:
        e = next(m for m in l["front"] if m["elite"])
        d = ELITES / f"line-{l['line']:02d}"
        d.mkdir(exist_ok=True)
        for old in d.glob("*.yaml"):
            old.unlink()
        for c in cards_from(e["cards"]):
            (d / f"{c.id}.yaml").write_text(c.to_yaml())
        man["lines"][f"line-{l['line']:02d}"] = {"cards": [c["id"] for c in e["cards"]], "train": e["train"], "val": e["val"]}
    (ELITES / "manifest.json").write_text(json.dumps(man, indent=1))
    print(f"froze {len(R['lines'])} elites to {ELITES}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--lines", type=int, default=LINES)
    a = ap.parse_args()
    if a.pilot:
        pilot()
    if a.run:
        run(a.lines)
    if a.analyze:
        analyze()
    if a.freeze:
        freeze()
