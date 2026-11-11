"""Household evolution run 2 (docs/results/household-evolve-2-prereg.md): run 1's loop with (a) liberty counting normative powers,
(b) a fixed lifetime horizon (156 weeks) and (c) the four pleasure levers ON for every run. Scripted agents, no model calls.

  uv run python scripts/household_evolve2_run.py --pilot      EXPLORATORY timing: one line, 1 generation (never cited)
  uv run python scripts/household_evolve2_run.py --run        the confirmatory run: LINES lines, validation (at most 4 workers)
  uv run python scripts/household_evolve2_run.py --analyze    prereg vs actual
  uv run python scripts/household_evolve2_run.py --report     loss report and plain-English cards for every elite
  uv run python scripts/household_evolve2_run.py --freeze     writes the elites under docs/results/household-evolve-2-elites/

Exam 2 (docs/results/household-exam-2-prereg.md) is not used or read here; the only item taken from it is its six-id persona denylist
(world_api.DENYLIST2, recomputed from its SHA-256 rule in a test). Wording rule: agents feel nothing; "pleasure" is a gloss.
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
from mar import hedonic as HD  # noqa: E402
from mar import loss_report as LR  # noqa: E402
from mar import stats as S  # noqa: E402
from mar import world_api as W  # noqa: E402
from mar.cards import load_cards, make_card  # noqa: E402

W.use_extra_deny(W.DENYLIST2)          # at import, so every spawned worker does it too

OUT = ROOT / "runs" / "household-evolve-2"
ELITES = ROOT / "docs" / "results" / "household-evolve-2-elites"
ELITES1 = ROOT / "docs" / "results" / "household-evolve-elites"
LINES, WORKERS = 16, 4
LIFETIME = 156
LEVERS = HD.LeverConfig(adapt=True, ritual=True, commit=True, network=True)
CFG = EV.HConfig(pop=8, offspring=6, generations=6, runs=6, k=3, max_rules=16, weeks=LIFETIME)
SEED_NAMES = ("author_seed_v2_bindable", "author_seed_v2_free_exit", "baseline", "needs_duty", "no_pressure_wall")
AUTHOR = "author_seed_v2_bindable"
VAL_SEED, VAL_RUNS = 777, 30
MARGINS = {"pleasure": 0.02, "no_fail": 0.05, "liberty": 0.25, "cooperation": 0.02}
POWERS = ("commit_stay", "commit_request", "give")
OBJ = W.HouseholdEvolveWorld.objectives


def new_world():
    return W.HouseholdEvolveWorld(levers=LEVERS, powers=True)


def card_dicts(spec):
    return [dataclasses.asdict(c) for c in spec]


def cards_from(dicts):
    return tuple(make_card(d) for d in dicts)


def val_ctx():
    return W.make_context(VAL_SEED, 0, VAL_RUNS, split="val", tag="val", weeks=LIFETIME)


def keeps(spec, power):
    """The elite keeps a power iff a `may` card names it (the world switches the mechanic on only then)."""
    return any(c.aim == power and c.deontic == "may" for c in spec)


def seed_task(name):
    w = new_world()
    return name, w.score_runs(w.load_spec(name), val_ctx())[0]


def line_task(line):
    t0 = time.time()
    w = new_world()
    res = EV.evolve_household(w, {n: w.load_spec(n) for n in SEED_NAMES}, line, CFG, log_path=OUT / f"line-{line:02d}.jsonl")
    vc = val_ctx()
    rows = []
    for i in [i for i in res["pop"] if i.rank == 0]:
        v, _ = w.score_runs(i.spec, vc)
        rows.append({"cards": card_dicts(i.spec), "train": i.scores, "val": v, "n_rules": i.n_rules, "op": i.op, "elite": i is res["elite"],
                     "protections": W.hh_protections(i.spec), "redundant": W.hh_redundant_cards(i.spec),
                     "powers": {p: keeps(i.spec, p) for p in POWERS}})
    return {"line": line, "front": rows, "log": res["log"], "seconds": time.time() - t0}


def run(lines=LINES, workers=WORKERS):
    OUT.mkdir(parents=True, exist_ok=True)
    workers = min(workers, 4)
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


def pilot():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    w = new_world()
    res = EV.evolve_household(w, {n: w.load_spec(n) for n in SEED_NAMES}, 501, dataclasses.replace(CFG, generations=1), log_path=OUT / "pilot.jsonl")
    for g in res["log"]:
        print(g["gen"], g["proposed"], g["filter_rejected"], g["accepted"], g["front_size"], g["elite"]["ids"])
    print(f"pilot {time.time() - t0:.0f}s")


# ---- the prereg's counting functions (pure, so the free check can run them on synthetic and run-1 inputs) ------------------------------

def p1_count(specs):
    """P1: elites keeping at least one of the three mechanic powers."""
    return sum(any(keeps(s, p) for p in POWERS) for s in specs)


def p2_counts(specs):
    """P2: per power, elites keeping it."""
    return {p: sum(keeps(s, p) for s in specs) for p in POWERS}


def p3_line(front, seed):
    """P3: a final-front member beats the author's seed on the validation context by >= the margin on >= 1 objective, losing none beyond it."""
    for m in front:
        d = {o: m["val"][o] - seed[o] for o in OBJ}
        if any(d[o] >= MARGINS[o] for o in OBJ) and all(d[o] >= -MARGINS[o] for o in OBJ):
            return True
    return False


def p5_count(specs):
    return sum(W.hh_protections(s)["no_veto"] and W.hh_protections(s)["free_exit"] for s in specs)


def verdicts(p1, p2, p3, p4_mean, p4_p, p5, rej, prop, n=16):
    """The prereg's verdict labels from the counts (Holm over P1, P2 a-c, P3, P4, P5)."""
    ps = {"P1": S.sign_test(p1, n), "P3": S.sign_test(p3, n), "P5": S.sign_test(p5, n), "P4": p4_p}
    for k, v in p2.items():
        ps["P2." + k] = S.fisher_exact_p(v, n, 0, n, "greater")
    names = sorted(ps)
    adj = dict(zip(names, S.holm([ps[k] for k in names])))
    ci = S.clopper_pearson(rej, prop)
    lab = {}
    lab["P1"] = "holds (descriptive)" if p1 >= 12 and adj["P1"] < 0.05 else ("meets threshold, not significant" if p1 >= 12 else "miss (descriptive)")
    ok2 = all(v >= 8 for v in p2.values())
    lab["P2"] = "holds" if ok2 and all(adj["P2." + k] < 0.05 for k in p2) else ("meets threshold, not significant" if ok2 else "miss")
    lab["P3"] = "holds (descriptive)" if p3 >= 12 and adj["P3"] < 0.05 else ("meets threshold, not significant" if p3 >= 12 else "miss (descriptive)")
    lab["P4"] = "holds (descriptive)" if p4_mean >= 0.01 and adj["P4"] < 0.05 else "miss (descriptive)"
    lab["P5"] = "holds (descriptive)" if p5 >= 12 and adj["P5"] < 0.05 else ("meets threshold, not significant" if p5 >= 12 else "miss (descriptive)")
    lab["P6"] = "holds robustly" if 0.05 <= ci.lo and ci.hi <= 0.40 else ("holds but CI crosses" if 0.05 <= rej / prop <= 0.40 else "miss")
    return lab, adj


def analyze():
    R = json.loads((OUT / "results.json").read_text())
    L = R["lines"]
    n = len(L)
    seed = R["seeds_val"][AUTHOR]
    el = [next(m for m in l["front"] if m["elite"]) for l in L]
    specs = [cards_from(e["cards"]) for e in el]
    p1, p2, p5 = p1_count(specs), p2_counts(specs), p5_count(specs)
    p3 = sum(p3_line(l["front"], seed) for l in L)
    d = np.array([e["val"]["pleasure"] - seed["pleasure"] for e in el])
    t = S.permutation_test(d, np.zeros(n), paired=True, alternative="greater", n_perm=20000, seed=1)
    rej = sum(g["filter_rejected"] for l in L for g in l["log"])
    prop = rej + sum(g["accepted"] for l in L for g in l["log"])
    lab, adj = verdicts(p1, p2, p3, float(d.mean()), t.p, p5, rej, prop, n)
    r1 = [load_cards(d_) for d_ in sorted(ELITES1.glob("line-*"))]
    r1c = {"any": p1_count(r1), **p2_counts(r1)}
    print(f"lines {n}")
    print(f"P1 elites keeping >=1 mechanic power: {p1}/{n} (run 1: {r1c['any']}/16) -> {lab['P1']} (Holm p {adj['P1']:.4f})")
    print(f"P2 per power: {p2} (run 1: { {k: r1c[k] for k in POWERS} }) -> {lab['P2']}; Holm p {[round(adj['P2.' + k], 4) for k in POWERS]}")
    print(f"P3 front member beats author's seed on validation: {p3}/{n} -> {lab['P3']}")
    print(f"P4 mean elite-minus-seed validation pleasure {d.mean():+.4f} (p {t.p:.4f}) -> {lab['P4']}")
    print(f"P5 elites keeping no-veto and free exit: {p5}/{n} (no_veto {sum(W.hh_protections(s)['no_veto'] for s in specs)}, free_exit {sum(W.hh_protections(s)['free_exit'] for s in specs)}) -> {lab['P5']}")
    ci = S.clopper_pearson(rej, prop)
    print(f"P6 filter rejected {rej}/{prop} = {rej / prop:.3f} CP [{ci.lo:.3f}, {ci.hi:.3f}] -> {lab['P6']}")
    print("seed val:", {k: round(v, 3) for k, v in seed.items() if k in OBJ})
    for o in OBJ:
        dd = [e["val"][o] - seed[o] for e in el]
        print(f"  elite - seed {o}: median {np.median(dd):+.3f} range {min(dd):+.3f} {max(dd):+.3f}")
    return R


def report():
    R = json.loads((OUT / "results.json").read_text())
    seed_spec = new_world().load_spec(AUTHOR)
    for l in R["lines"]:
        e = next(m for m in l["front"] if m["elite"])
        spec = cards_from(e["cards"])
        print(f"\nLINE {l['line']}: {len(spec)} cards, powers kept {[p for p in POWERS if keeps(spec, p)]}, protections {e['protections']}")
        print("  val " + ", ".join(f"{o} {e['val'][o]:.3f}" for o in OBJ))
        for c in spec:
            print("   - " + c.id + ": " + LR._plain(c))
        for x in LR.render(LR.loss_report(seed_spec, spec)):
            print("   * " + x)


def freeze():
    R = json.loads((OUT / "results.json").read_text())
    ELITES.mkdir(parents=True, exist_ok=True)
    man = {"selection_rule": "mar.evolve.pick_elite_h (rank-0, highest mean of the four normalized objectives, ties by fewer cards)", "lines": {}}
    for l in R["lines"]:
        e = next(m for m in l["front"] if m["elite"])
        d = ELITES / f"line-{l['line']:02d}"
        d.mkdir(exist_ok=True)
        for old in d.glob("*.yaml"):
            old.unlink()
        for c in cards_from(e["cards"]):
            (d / f"{c.id}.yaml").write_text(c.to_yaml())
        man["lines"][f"line-{l['line']:02d}"] = {"cards": [c["id"] for c in e["cards"]], "train": e["train"], "val": e["val"], "powers": e["powers"]}
    man["seeds_val"], man["cfg"] = R["seeds_val"], R["cfg"]
    (ELITES / "manifest.json").write_text(json.dumps(man, indent=1))
    keep = ("gen", "proposed", "duplicates", "inapplicable", "filter_rejected", "accepted", "rejected_by_reason", "accepted_by_op", "rejected_by_op",
            "front_size", "hv", "pop_rules_mean", "elite")
    (ELITES / "generation-log.json").write_text(json.dumps({f"line-{l['line']:02d}": [{k: g[k] for k in keep} for g in l["log"]] for l in R["lines"]}))
    print(f"froze {len(R['lines'])} elites to {ELITES}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("pilot", "run", "analyze", "report", "freeze"):
        ap.add_argument(f"--{k}", action="store_true")
    a = ap.parse_args()
    if a.pilot:
        pilot()
    if a.run:
        run()
    if a.analyze:
        analyze()
    if a.report:
        report()
    if a.freeze:
        freeze()
