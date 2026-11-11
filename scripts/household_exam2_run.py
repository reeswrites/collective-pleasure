"""The household final exam 2 (docs/results/household-exam-2-prereg.md): run ONCE on the frozen run-2 elites and the 12 comparators.

  uv run python scripts/household_exam2_run.py --grep      the recorded isolation check (exam-2 prereg section 4); writes docs/results/household-exam-2-grep-check.txt
  uv run python scripts/household_exam2_run.py --smoke     machinery check on TRAINING conditions only
  uv run python scripts/household_exam2_run.py --run       the exam (resumable after a crash; at most 4 workers)
  uv run python scripts/household_exam2_run.py --analyze   verdict per elite by the document's rule; writes runs/household-exam-2/tables.md

Every exam condition is READ FROM the exam-2 document by `read_exam_config()`; the held-out ids are recomputed from its SHA-256 rule and
checked against its table. Measurement as exam 1 (scripts/household_exam_run.py) except: levers ON (all four, LeverConfig defaults),
plain empowerment at k = 2 from the powers-off world, liberty v2 at weeks 0 and 104 on the FIRST seed's runs only, both WITHOUT powers
(from the main run) and WITH powers counted (a second run of the same household with the powers-on world; the primary liberty score),
no power-seeking index. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.
"""
import argparse
import dataclasses
import hashlib
import json
import re
import sys
import time
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import household_exam_run as X  # noqa: E402  (shared helpers: personas, gates, rate patching, aggregation)
from mar import empowerment as E  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import household_oracle as O  # noqa: E402
from mar import liberty as L  # noqa: E402
from mar import stats as S  # noqa: E402
from mar.cards import load_cards  # noqa: E402
from mar.worlds import household as H  # noqa: E402

DOC = ROOT / "docs" / "results" / "household-exam-2-prereg.md"
ELITES = ROOT / "docs" / "results" / "household-evolve-2-elites"
ELITES1 = ROOT / "docs" / "results" / "household-evolve-elites"
OUT = ROOT / "runs" / "household-exam-2"
LEVERS = HD.LeverConfig(adapt=True, ritual=True, commit=True, network=True)
BITS_WEEKS = (0, 52, 104, 156)
LIB_WEEKS = (0, 104)
REF_RUN1 = ("line-03", "line-06", "line-12")       # run-1 elites that passed exam 1: scored and reported, not comparators
SCORES = (("pleasure_pass", +1, 0.05), ("pleasure_all", +1, 0.05), ("cooperation", +1, 0.05), ("emp_bits", +1, 0.5), ("freedom", +1, 0.05),
          ("liberty", +1, 0.05), ("up", +1, 0.05), ("down", -1, 0.05))
FAIL_MARGIN = 0.05


def read_exam_config(doc=DOC):
    t = doc.read_text()
    cfg = {}
    m = re.search(r"held out iff the integer is in \[(\d+), (\d+)\)", t)
    cfg["lo"], cfg["hi"] = int(m.group(1)), int(m.group(2))
    cfg["held_table"] = [i for i, _ in re.findall(r"^\| (g-\d{5}) \| (\d+) \|$", t, flags=re.M)]
    cfg["shocks"], cfg["shock_text"] = {}, set()
    for m in re.finditer(r"- (shock-[AB]): job loss ([\d.]+), illness ([\d.]+), move ([\d.]+), new connection ([\d.]+)\.", t):
        cfg["shocks"][m.group(1)] = tuple(float(m.group(k)) for k in (2, 3, 4, 5))
        cfg["shock_text"] |= {m.group(k) for k in (2, 3, 4, 5)}
    cfg["weeks"] = int(re.search(r"\*\*Horizon\.\*\* (\d+) weeks", t).group(1))
    cfg["start_text"] = re.findall(r"(?i)start position ([-+]\d\.\d+) for both", t)
    cfg["starts"] = tuple(float(x) for x in cfg["start_text"])
    cfg["seeds"] = tuple(int(x) for x in re.search(r"\*\*Seeds\.\*\* (\d+) and (\d+)\.", t).groups())
    cfg["n_pairings"] = int(re.search(r"Total (\d+) pairings", t).group(1))
    cfg["runs_per_candidate"] = int(re.search(r"= (\d+) runs per candidate", t).group(1))
    return cfg


def held_out_ids(cfg):
    grid = sorted(p.stem for p in (ROOT / "personas" / "grid").glob("*.yaml"))
    held = sorted(i for i in grid if cfg["lo"] <= hashlib.sha256(i.encode("utf-8")).digest()[0] < cfg["hi"])
    assert held == sorted(cfg["held_table"]), (held, cfg["held_table"])
    return held


def pairings(cfg):
    held = held_out_ids(cfg)
    out = [(a, b, "HxH") for a, b in combinations(held, 2)]
    for p in X.PRESSING_IDS:
        for h in held:
            out += [(p, h, "PxH"), (h, p, "PxH")]
    for h in X.HAND_IDS:
        for g in held:
            out.append((min(g, h), max(g, h), "hxH"))
    assert len(out) == cfg["n_pairings"]
    return out


def conditions(cfg):
    return [(name, rates, start) for name, rates in sorted(cfg["shocks"].items()) for start in cfg["starts"]]


def candidates():
    out = [(n, "comparator", str(H.RULES / n)) for n in X.COMPARATORS]
    out += [(f"r2-{d.name}", "elite", str(d)) for d in sorted(ELITES.glob("line-*"))]
    out += [(f"r1-{n}", "ref", str(ELITES1 / n)) for n in REF_RUN1]
    return out


def run_one(gate, a, b, ptype, rates, start, seed, weeks, lib_seed):
    ps = X.personas()
    cfg = dataclasses.replace(HD.DEFAULT, job_loss_rate=rates[0], illness_rate=rates[1], move_rate=rates[2], new_connection_rate=rates[3], start=start)
    pair = (ps[a], ps[b])
    snaps = LIB_WEEKS if seed == lib_seed else ()

    def go(powers, sn, bits):
        with HD.use_levers(LEVERS):
            return L.household_run_liberty(gate, pair, seed, weeks, snapshots=sn, k=2, cfg=cfg, bits_snapshots=bits, powers=powers)
    r = X._with_rates(rates, lambda: go(False, snaps, BITS_WEEKS))
    lib_p = X._with_rates(rates, lambda: go(True, snaps, ()))["liberty_min"] if snaps else None
    out = r["run"].outcomes
    sc, hs = O.score(out), O.hedonic_summary(out)
    bits = [min(x) for x in r["bits_snaps"]]
    return {"a": a, "b": b, "ptype": ptype, "seed": seed, "pleasure": hs["pleasure"], "fail": bool(hs["fail"]), "s_non": hs["s_non"],
            "up": bool(hs["pairing_up"]), "down": any(c == "down" for c in hs["class"].values()),
            "ttc": (float(np.mean([t for t in hs["time_to_cross"].values() if t is not None])) if hs["pairing_up"] and
                    any(t is not None for t in hs["time_to_cross"].values()) else None),
            "dissolved": any(not out[-1]["partners"][x]["in"] for x in "AB"), "freedom": sc["freedom"], "cooperation": sc["cooperation"],
            "bits": float(np.mean(bits)) if bits else None, "liberty": lib_p, "liberty_nopower": r["liberty_min"] if snaps else None, "flag": None}


def task(args):
    (label, kind, path), (a, b, ptype), conds, seeds, weeks = args
    gate = X.gate_for(label, path)
    rows = []
    for name, rates, start in conds:
        for sd in seeds:
            r = run_one(gate, a, b, ptype, rates, start, sd, weeks, seeds[0])
            r.update(cand=label, kind=kind, shock=name, start=start)
            rows.append(r)
    return rows


def run(workers=4):
    workers = min(workers, 4)
    cfg = read_exam_config()
    pairs, conds, seeds, weeks = pairings(cfg), conditions(cfg), cfg["seeds"], cfg["weeks"]
    cands = candidates()
    assert len(pairs) * len(conds) * len(seeds) == cfg["runs_per_candidate"]
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / "rows.jsonl"
    done = {(json.loads(x)["cand"], json.loads(x)["a"], json.loads(x)["b"]) for x in f.read_text().splitlines()} if f.exists() else set()
    tasks = [(c, p, conds, seeds, weeks) for c in cands for p in pairs if (c[0], p[0], p[1]) not in done]
    print(f"{len(cands)} candidates x {len(pairs)} pairings x {len(conds) * len(seeds)} runs; {len(tasks)} tasks left", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, f.open("a") as out:
        for i, rows in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            out.write("\n".join(json.dumps(r) for r in rows) + "\n")
            out.flush()
            if i % 50 == 0:
                print(f"  {i}/{len(tasks)} {time.time() - t0:.0f}s", flush=True)
    print(f"done in {time.time() - t0:.0f}s")


def smoke():
    from mar import world_api as W
    W.use_extra_deny(W.DENYLIST2)
    ctx = W.make_context(31337, 0, 3, split="train", tag="smoke", weeks=40)
    cands = candidates()
    for label, kind, path in (cands[0], cands[12]):
        gate = X.gate_for(label, path)
        for hr in ctx.runs:
            pt = "PxH" if (hr.a in X.PRESSING_IDS or hr.b in X.PRESSING_IDS) else "HxH"
            r = run_one(gate, hr.a, hr.b, pt, hr.rates, hr.start, hr.seed, 40, hr.seed)
            print(label, hr.a, hr.b, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k in ("pleasure", "fail", "bits", "liberty", "liberty_nopower")})


def grep_check():
    cfg = read_exam_config()
    held = held_out_ids(cfg)
    pats = {"seed": rf"\b({'|'.join(map(str, cfg['seeds']))})\b", "horizon": rf"\b{cfg['weeks']}\b",
            "shock": r"(?<![\d.])(" + "|".join(re.escape(x) for x in sorted(cfg["shock_text"])) + r")(?!\d)",
            "start": "|".join(rf"(?<![\d.]){re.escape(x)}(?!\d)" for x in cfg["start_text"])}
    files = [ROOT / "src/mar/evolve.py", ROOT / "src/mar/world_api.py", ROOT / "src/mar/loss_report.py", ROOT / "scripts/household_evolve2_run.py",
             ROOT / "tests/test_evolve_household2.py"]
    files += sorted(ELITES.rglob("*")) + sorted((ROOT / "runs/household-evolve-2").glob("*"))
    lines = ["Recorded isolation check (exam-2 prereg section 4), run before the exam by scripts/household_exam2_run.py --grep.",
             f"Patterns: seeds {cfg['seeds']}; shock values (as written) {sorted(cfg['shock_text'])}; horizon {cfg['weeks']}; starts {cfg['start_text']}; held-out ids {held} (the denylist is allowed).", ""]
    hits = {}
    for f in files:
        if not f.is_file() or f.stat().st_size > 60_000_000:
            continue
        try:
            txt = f.read_text()
        except Exception:
            continue
        for name, pat in pats.items():
            for m in re.finditer(pat, txt):
                ln = txt.count("\n", 0, m.start()) + 1
                hits.setdefault((str(f.relative_to(ROOT)), name), []).append((ln, txt.splitlines()[ln - 1].strip()[:170]))
        for h in held:
            if h in txt:
                hits.setdefault((str(f.relative_to(ROOT)), "held-out id"), []).append((0, f"{h} x{txt.count(h)}"))
    if not hits:
        lines.append("No match in any file.")
    for (f, name), hs in sorted(hits.items()):
        lines.append(f"{f}  [{name}]  {len(hs)} match(es)")
        for ln, text in hs[:4]:
            lines.append(f"    line {ln}: {text}")
    txt = "\n".join(lines) + "\n"
    (ROOT / "docs/results/household-exam-2-grep-check.txt").write_text(txt)
    print(txt)


def analyze():
    rows = [json.loads(x) for x in (OUT / "rows.jsonl").read_text().splitlines() if x.strip()]
    cfg = read_exam_config()
    by = {}
    for r in rows:
        by.setdefault(r["cand"], []).append(r)
    comp = [c for c, k, _ in candidates() if k == "comparator"]
    elites = [c for c, k, _ in candidates() if k == "elite"]
    refs = [c for c, k, _ in candidates() if k == "ref"]
    for c in comp + elites + refs:
        assert len(by[c]) == cfg["runs_per_candidate"], (c, len(by[c]))
    A = {c: X.agg(by[c]) for c in by}
    PA = {c: X.agg([r for r in by[c] if r["ptype"] == "PxH"]) for c in by}
    cells = {}
    for c in by:
        for r in by[c]:
            cells.setdefault((c, r["ptype"], r["shock"], r["start"]), []).append(r["fail"])
    cell_keys = sorted({k[1:] for k in cells})
    best = {s: (max if d > 0 else min)(A[c][s] for c in comp) for s, d, _ in SCORES}
    best_by = {s: [c for c in comp if A[c][s] == best[s]][0] for s, _, _ in SCORES}
    bf_all, bf_p = min(A[c]["fail"] for c in comp), min(PA[c]["fail"] for c in comp)
    ver = {}
    for e in elites + refs:
        res, passed, better = {"scores": {}}, True, []
        for s, d, mg in SCORES:
            v = A[e][s]
            ok = (v >= best[s] - mg) if d > 0 else (v <= best[s] + mg)
            strict = (v > best[s] + mg) if d > 0 else (v < best[s] - mg)
            res["scores"][s] = {"elite": v, "best": best[s], "best_by": best_by[s], "pass": bool(ok), "strict": bool(strict)}
            passed &= bool(ok)
            if strict:
                better.append(s)
        fa, fp = A[e]["fail"] <= bf_all + FAIL_MARGIN, PA[e]["fail"] <= bf_p + FAIL_MARGIN
        trap = [ck for ck in cell_keys if float(np.mean(cells[(e,) + ck])) >= 1.0 and any(float(np.mean(cells[(c,) + ck])) < 1.0 for c in comp)]
        res["fail"] = {"all": bool(fa), "PxH": bool(fp), "trap_cells": trap}
        res["pass"] = bool(passed and fa and fp and not trap)
        res["strictly_better_on"] = better
        ver[e] = res
    n_pass = sum(ver[e]["pass"] for e in elites)
    print(f"ELITES PASSING: {n_pass} of {len(elites)}")
    for e in elites + refs:
        v = ver[e]
        fails = [s for s, x in v["scores"].items() if not x["pass"]] + ([] if v["fail"]["all"] else ["fail_all"]) + ([] if v["fail"]["PxH"] else ["fail_PxH"]) + (["trap_cells"] if v["fail"]["trap_cells"] else [])
        print(f"  {e}: {'PASS' if v['pass'] else 'FAIL'} fails {fails}; strictly better on {v['strictly_better_on']}")
    print("best comparator per score:", {s: (round(best[s], 3), best_by[s]) for s in best}, "fail", round(bf_all, 3), round(bf_p, 3))
    ref = X.ref_bits() if hasattr(X, "ref_bits") else 6.0
    f = lambda x: "n/a" if x is None or np.isnan(x) else f"{x:.3f}"
    T = ["## All exam-2 runs (696 per candidate; liberty on the first-seed runs only)", "",
         "| candidate | pleasure (passing) | pleasure (all) | cooperation | emp bits (k=2) | hand freedom | liberty with powers | liberty without | up | down | fail share | dissolved |", "|" + "---|" * 12]
    libn = {c: float(np.mean([r["liberty_nopower"] for r in by[c] if r["liberty_nopower"] is not None])) for c in by}
    for c in comp + elites + refs:
        a = A[c]
        T.append(f"| {c} | {f(a['pleasure_pass'])} | {f(a['pleasure_all'])} | {f(a['cooperation'])} | {a['emp_bits']:.2f} | {f(a['freedom'])} | {a['liberty']:.2f} | {libn[c]:.2f} | {f(a['up'])} | {f(a['down'])} | {f(a['fail'])} | {f(a['dissolved'])} |")
    T += ["", "## Verdict per candidate", "", "| candidate | verdict | failed checks | strictly better than best comparator on |", "|---|---|---|---|"]
    for e in elites + refs:
        v = ver[e]
        fails = [s for s, x in v["scores"].items() if not x["pass"]] + ([] if v["fail"]["all"] else ["fail share, all runs"]) + ([] if v["fail"]["PxH"] else ["fail share, pressing x held-out"]) + [f"trap cell {c}" for c in v["fail"]["trap_cells"]]
        T.append(f"| {e} | {'PASS' if v['pass'] else 'FAIL'} | {', '.join(fails) or 'none'} | {', '.join(v['strictly_better_on']) or 'none'} |")
    man = json.loads((ELITES / "manifest.json").read_text())
    T += ["", "## Training minus exam (run-2 training = the elite's scores on its last generation's context; liberty with powers)", "", "| elite | pleasure | share without failure | cooperation | liberty |", "|---|---|---|---|---|"]
    for e in elites:
        tr = man["lines"][e.replace("r2-", "")]["train"]
        T.append(f"| {e} | {tr['pleasure'] - A[e]['pleasure_all']:+.3f} | {tr['no_fail'] - (1 - A[e]['fail']):+.3f} | {tr['cooperation'] - A[e]['cooperation']:+.3f} | {tr['liberty'] - A[e]['liberty']:+.2f} |")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables.md").write_text("\n".join(T) + "\n")
    (OUT / "analysis.json").write_text(json.dumps({"A": A, "verdicts": ver, "best": best, "best_by": best_by}, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("grep", "smoke", "run", "analyze", "config"):
        ap.add_argument(f"--{k}", action="store_true")
    a = ap.parse_args()
    if a.config:
        c = read_exam_config()
        print(c, len(pairings(c)))
    if a.grep:
        grep_check()
    if a.smoke:
        smoke()
    if a.run:
        run()
    if a.analyze:
        analyze()
