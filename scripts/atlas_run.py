"""Pattern atlas (ADR 0008 item 8; docs/results/pattern-atlas.md). EXPLORATORY and DESCRIPTIVE: no prereg, no prediction tested.
Re-runs a stratified sample of existing household designs with a week-by-week recorder (src/mar/atlas.py), then clusters the runs.
Scripted persona agents, no model calls. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

  uv run python scripts/atlas_run.py --time        time one run of each family
  uv run python scripts/atlas_run.py --run         record the sample (at most 3 workers) -> runs/atlas/records.jsonl.gz
  uv run python scripts/atlas_run.py --cluster     features, k by silhouette, stability, medoid stories -> runs/atlas/atlas.json

The sample (each family replays its source design exactly, reading those modules, changing none):
  h38   H38 pairing norms, arms L0 (no pressure) and L4 (the preregistered top of the dial); the first 50 confirmatory pairings
        (scripts/h38_pairing_run.py CONFIRM sample), seed 0; with the stay readings every 13 weeks.
  ef    Exit fallbacks slice 2 (items on, cell V2-split-loves), arms F0, F4, F5, the author's seeds v2.2 and v2.3 (bindable),
        household evolution run 2's 30 validation runs (scripts/exit_fallbacks_run.py play_items).
  v2    Seed v2 retest arms BASE-F and V23-F, the 40-pairing cohort RT.sample(25, 20261111), seed 0 (retest.play_cell).
"""
import argparse
import dataclasses
import gzip
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from mar import atlas as AT  # noqa: E402

OUT = ROOT / "runs" / "atlas"
WORKERS = 3
H38_ARMS, H38_N, H38_SEEDS = ("L0", "L4"), 50, (0, 1)
EF_ARMS, EF_CANDS, EF_CELL = ("F0", "F4", "F5"), ("author_seed_v2_bindable", "author_seed_v23_bindable"), "V2-split-loves"
V2_ARMS, V2_SAMPLE, V2_SEEDS = ("BASE-F", "V23-F"), (25, 20261111), (0,)


def persona_meta(p, role):
    from mar import pairing as PR
    return {"id": p.id, "style": p.negotiation_style, "v": PR.values_pairing(p), "source": p.source,
            "weights": {k: float(v) for k, v in p.weights.items()}, "role": role}


# ---- the three families -------------------------------------------------------------------------------------------------------

def play_h38(arm, a, b, seed):
    """= h38_pairing_run.play (stay=True), plus the recorder."""
    import h38_pairing_run as P
    from mar import exit_fallback as EF
    from mar import exit_items as EI
    from mar import hedonic as HD
    from mar import negotiation as NG
    from mar import pairing as PR
    from mar import retest as RT
    from mar.worlds import household as H
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=P.ARMS[arm])
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[P.CELL]):
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=H.WEEKS, decline=True)
        world = lived.world
        rec = AT.Recorder(world)
        last = {"busy": {"A": False, "B": False}}
        for w in range(world.weeks):
            if w and w % NG.REVIEW_EVERY == 0:
                if lived.apart and lived.decline:
                    lived.retry(w, last)
                elif all(world.p[r]["in"] for r in "AB"):
                    rec.stay(w, PR.stay_reading(world, w, last))
                    lived.reading(w, last)
            if world.early_review:
                world.ladder_reviewed(w)
            last = {"busy": world.step_week(w, last)}
        rec.finish().lived(lived)
    return rec, (ps[a], ps[b]), {"pressure": arm, "formed0": not bool(lived.week0 and any(
        lived.week0["O"][r] > lived.week0["W"][r] for r in "AB")) if getattr(lived, "week0", None) else True}


def play_v2(arm, a, b, seed):
    """= retest.play_cell (stay=False), plus the recorder (attached before the first week)."""
    from mar import hedonic as HD
    from mar import negotiation as NG
    from mar import retest as RT
    from mar.worlds import household as H
    rules, fx, decline = RT.ALL_ARMS[arm]
    ps = RT.personas()
    pa, pb = ps[a], ps[b]
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        if rules == "baseline":
            lived = NG.BaselineLived(pa, pb, seed, H.load_variant("baseline"), decline=bool(decline))
        else:
            base = NG.base_cards(rules)
            res = NG.week0(pa, pb, "fair_default", seed, base, floor=True)
            lived = NG.Lived(pa, pb, "fair_default", seed, base, res, floor=True, apart=True)
        lived.world.count_menus = True
        rec = AT.Recorder(lived.world)
        lived.play()
        rec.finish().lived(lived)
    return rec, (pa, pb), {}


def play_ef(arm, cand, i):
    """= exit_fallbacks_run.play_items for validation run i, plus the recorder."""
    import exit_fallbacks_run as X
    from mar import exit_fallback as EF
    from mar import exit_items as EI
    from mar import hedonic as HD
    from mar import world_api as W
    from mar.cards import load_cards
    from mar.worlds import household as H
    hr = X.ctx("val").runs[i]
    ps = W.hh_personas()
    cfg = dataclasses.replace(HD.DEFAULT, job_loss_rate=hr.rates[0], illness_rate=hr.rates[1], move_rate=hr.rates[2],
                              new_connection_rate=hr.rates[3], start=hr.start)
    box = {}
    with EF.use_exit_fallback(arm, strip_split=True), EI.use_items(EI.GRID[EF_CELL]):
        gate = H.PyGate(load_cards(str(H.RULES / cand)))

        def go():
            with HD.use_levers(X.LEVERS):
                wk = H.WeeklyWorld(gate, (ps[hr.a], ps[hr.b]), hr.seed, hr.weeks, cfg)
                box["rec"] = AT.Recorder(wk)
                wk.play()
            return wk
        W._with_rates(hr.rates, go)
        box["rec"].finish()
    return box["rec"], (ps[hr.a], ps[hr.b]), {"cand": cand, "run": i}


def tasks():
    from mar import retest as RT
    import h38_pairing_run as P
    out = []
    for a, b in RT.sample(P.CONFIRM["n_other"], P.CONFIRM["sample_seed"])[:H38_N]:
        for arm in H38_ARMS:
            for s in H38_SEEDS:
                out.append(("h38", arm, a, b, s))
    for cand in EF_CANDS:
        for arm in EF_ARMS:
            for i in range(30):
                out.append(("ef", arm, cand, i, 0))
    for a, b in RT.sample(*V2_SAMPLE):
        for arm in V2_ARMS:
            for s in V2_SEEDS:
                out.append(("v2", arm, a, b, s))
    return out


def task(t):
    fam, arm, x, y, s = t
    t0 = time.time()
    if fam == "h38":
        rec, ps, extra = play_h38(arm, x, y, s)
    elif fam == "v2":
        rec, ps, extra = play_v2(arm, x, y, s)
    else:
        rec, ps, extra = play_ef(arm, x, y)
    pa, pb = ps
    meta = {"family": fam, "arm": arm, "seed": s, "a": pa.id, "b": pb.id, **extra,
            "personas": {"A": persona_meta(pa, "A"), "B": persona_meta(pb, "B")}, **rec.meta}
    key = f"{fam}|{arm}|{x}|{y}|{s}"
    return {"key": key, "meta": meta, "rows": rec.rows, "secs": round(time.time() - t0, 2)}


def run(workers=WORKERS):
    workers = min(workers, 3)
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / "records.jsonl.gz"
    done = set()
    if f.exists():
        with gzip.open(f, "rt") as fh:
            done = {json.loads(x)["key"] for x in fh if x.strip()}
    todo = [t for t in tasks() if "|".join(map(str, t)) not in done]
    print(f"{len(todo)} runs to record, {workers} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, gzip.open(f, "at") as fh:
        for i, r in enumerate(pool.imap_unordered(task, todo, chunksize=1), 1):
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            if i % 20 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)} last {r['secs']}s wall {time.time() - t0:.0f}s", flush=True)


def load():
    with gzip.open(OUT / "records.jsonl.gz", "rt") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def timing():
    ts = tasks()
    for fam in ("h38", "ef", "v2"):
        t = next(x for x in ts if x[0] == fam and x[1] in ("L4", "F4", "V23-F"))
        r = task(t)
        print(fam, t, r["secs"], "s;", len(r["rows"]), "weeks;", AT.features(r["rows"], r["meta"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--time", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--cluster", action="store_true")
    ap.add_argument("--workers", type=int, default=WORKERS)
    a = ap.parse_args()
    if a.time:
        timing()
    if a.run:
        run(a.workers)
    if a.cluster:
        import atlas_cluster
        atlas_cluster.main()


if __name__ == "__main__":
    main()
