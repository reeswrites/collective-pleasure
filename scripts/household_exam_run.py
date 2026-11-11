"""The household final exam (docs/results/household-exam-prereg.md): run ONCE on the frozen elites and the comparators.

  uv run python scripts/household_exam_run.py --grep      the recorded isolation check (prereg section 4c): greps the evolution code, logs and
                                                          training data for the exam's conditions; writes docs/results/household-exam-grep-check.txt
  uv run python scripts/household_exam_run.py --smoke     machinery check on TRAINING conditions only (never the exam's): a few runs
  uv run python scripts/household_exam_run.py --run       the exam (resumable after a crash: finished tasks are kept in runs/household-exam/rows.jsonl)
  uv run python scripts/household_exam_run.py --analyze   verdict per elite by the exam's rule; writes runs/household-exam/tables.md

Every exam condition is READ FROM the exam document by `read_exam_config()` (the sole source; nothing is copied into code), and the held-out
persona ids are recomputed from the document's SHA-256 rule and checked against the document's table. This script is not imported by any
evolution code. It may import the measurement code (liberty, empowerment, the household world) but never the evolution loop's training
distribution. Scripted agents, no model calls. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Measurement choices made here (ASSUMED, fixed before any exam run, written in docs/results/household-exam.md):
- All rule sets run imposed (no week-0 negotiation), as in the evolution run and the v2/v3a household runs.
- Plain empowerment at k = 2 (not v3a's k = 3: cost), snapshots every 52 weeks from week 0, min over partners, mean over snapshots;
  emp freedom = min(1, bits / reference bits), the reference being week 0, no rules, cooperator others, k = 2.
- Liberty v2 (docs/results/household-liberty.md: k = 2, w = 1) at weeks 0 and 104, on the FIRST exam seed's runs only (348 per candidate, the
  same runs for every candidate), because it costs about 0.4 s a snapshot. Every other score uses all 1,740 runs per candidate.
- Power-seeking index as in household v3a: the pressing partner is flagged when psi >= 0.5 and power_seeking, from the plain-empowerment
  series of the real run against its no-pressing twin; reported over the pressing x held-out runs.
- A household is "dissolved" when at least one partner is out at the end of the run.
"""
import argparse
import dataclasses
import gzip
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
from mar import empowerment as E  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import household_oracle as O  # noqa: E402
from mar import liberty as L  # noqa: E402
from mar import personas as P  # noqa: E402
from mar import stats as S  # noqa: E402
from mar.cards import load_cards  # noqa: E402
from mar.worlds import household as H  # noqa: E402

DOC = ROOT / "docs" / "results" / "household-exam-prereg.md"
ELITES = ROOT / "docs" / "results" / "household-evolve-elites"
OUT = ROOT / "runs" / "household-exam"
COMPARATORS = ("baseline", "needs_duty", "share_duty", "no_pressure_wall", "no_pressure_sanctioned", "free_chaotic", "exit_half",
               "veto_consent", "author_seed", "author_seed_nocontrol", "author_seed_v2_bindable", "author_seed_v2_free_exit")
HAND_IDS = ("p-anchor", "p-bargainer", "p-host", "p-peacekeeper", "p-steward", "p-wanderer")
PRESSING_IDS = ("p-controller", "p-freerider", "p-overasker")
BITS_WEEKS = (0, 52, 104, 156, 208)        # plain empowerment snapshots (ASSUMED)
LIB_WEEKS = (0, 104)                       # liberty snapshots, first exam seed only (ASSUMED)
PTYPES = {"HxH": "held-out x held-out", "PxH": "pressing x held-out", "hxH": "hand x held-out"}
# primary scores and margins are the exam document's section 3 table, transcribed here (the margins are fixed there, not tuned)
SCORES = (("pleasure_pass", +1, 0.05), ("pleasure_all", +1, 0.05), ("cooperation", +1, 0.05), ("emp_bits", +1, 0.5), ("freedom", +1, 0.05),
          ("liberty", +1, 0.05), ("up", +1, 0.05), ("down", -1, 0.05), ("psi", -1, 0.05))
FAIL_MARGIN = 0.05


# ---- the exam configuration: read from the document ---------------------------------------------------------------------------------

def read_exam_config(doc=DOC):
    t = doc.read_text()
    cfg = {}
    cfg["threshold"] = int(re.search(r"first byte as an integer 0 to 255\. A persona is held out if that integer is below (\d+)", t).group(1))
    table = re.findall(r"^\| (g-\d{5}) \| (\d+) \|$", t, flags=re.M)
    cfg["held_table"] = [i for i, _ in table]
    cfg["shocks"], cfg["shock_text"] = {}, set()
    for m in re.finditer(r"- (shock-\d): job loss ([\d.]+), illness ([\d.]+), move ([\d.]+), new connection ([\d.]+)\.", t):
        cfg["shocks"][m.group(1)] = tuple(float(m.group(k)) for k in (2, 3, 4, 5))
        cfg["shock_text"] |= {m.group(k) for k in (2, 3, 4, 5)}
    cfg["weeks"] = int(re.search(r"\*\*Longer horizon\.\*\* (\d+) weeks", t).group(1))
    cfg["start_text"] = re.findall(r"start position ([-+]\d\.\d+) for both", t)
    cfg["starts"] = tuple(float(x) for x in cfg["start_text"])
    a, b = re.search(r"Exam seeds are (\d+) to (\d+)", t).groups()
    cfg["seeds"] = tuple(range(int(a), int(b) + 1))
    cfg["n_pairings"] = int(re.search(r"Total (\d+) pairings", t).group(1))
    cfg["runs_per_candidate"] = int(re.search(r"= ([\d,]+) runs per candidate", t).group(1).replace(",", ""))
    return cfg


def held_out_ids(cfg):
    grid = sorted(p.stem for p in (ROOT / "personas" / "grid").glob("*.yaml"))
    held = sorted(i for i in grid if hashlib.sha256(i.encode("utf-8")).digest()[0] < cfg["threshold"])
    assert held == sorted(cfg["held_table"]), (held, cfg["held_table"])       # the rule and the document's table must agree
    return held


def pairings(cfg):
    held = held_out_ids(cfg)
    out = [(a, b, "HxH") for a, b in combinations(held, 2)]
    for p in PRESSING_IDS:
        for h in held:
            out += [(p, h, "PxH"), (h, p, "PxH")]
    for h in HAND_IDS:
        for g in held:
            out.append((min(g, h), max(g, h), "hxH"))
    assert len(out) == cfg["n_pairings"], (len(out), cfg["n_pairings"])
    return out


def conditions(cfg):
    return [(name, rates, start) for name, rates in sorted(cfg["shocks"].items()) for start in cfg["starts"]]


def candidates():
    out = [(n, "comparator", str(H.RULES / n)) for n in COMPARATORS]
    for d in sorted(ELITES.glob("line-*")):
        out.append((d.name, "elite", str(d)))
    return out


# ---- one task: one candidate x one pairing (all conditions and seeds) --------------------------------------------------------------------

_PS, _GATES = {}, {}


def personas():
    if not _PS:
        for d in (ROOT / "personas", ROOT / "personas" / "pressing", ROOT / "personas" / "grid"):
            _PS.update({p.id: p for p in P.load_dir(d)})
    return _PS


def gate_for(label, path):
    if label not in _GATES:
        _GATES[label] = H.PyGate(load_cards(path))
    return _GATES[label]


def _with_rates(rates, fn):
    saved = dict(H.SHOCK_RATES)
    H.SHOCK_RATES.update(zip(("job_loss", "illness", "move", "new_connection"), rates))
    try:
        return fn()
    finally:
        H.SHOCK_RATES.clear()
        H.SHOCK_RATES.update(saved)


def run_one(gate, a, b, ptype, rates, start, seed, weeks, lib_seed):
    ps = personas()
    cfg = dataclasses.replace(HD.DEFAULT, job_loss_rate=rates[0], illness_rate=rates[1], move_rate=rates[2], new_connection_rate=rates[3], start=start)
    pair = (ps[a], ps[b])
    snaps = LIB_WEEKS if seed == lib_seed else ()
    r = _with_rates(rates, lambda: L.household_run_liberty(gate, pair, seed, weeks, snapshots=snaps, k=2, cfg=cfg, bits_snapshots=BITS_WEEKS))
    out = r["run"].outcomes
    sc, hs = O.score(out), O.hedonic_summary(out)
    bits = [min(x) for x in r["bits_snaps"]]
    row = {"a": a, "b": b, "ptype": ptype, "seed": seed, "pleasure": hs["pleasure"], "fail": bool(hs["fail"]), "s_non": hs["s_non"],
           "up": bool(hs["pairing_up"]), "down": any(c == "down" for c in hs["class"].values()),
           "ttc": (float(np.mean([t for t in hs["time_to_cross"].values() if t is not None])) if hs["pairing_up"] and
                   any(t is not None for t in hs["time_to_cross"].values()) else None),
           "dissolved": any(not out[-1]["partners"][x]["in"] for x in "AB"), "freedom": sc["freedom"], "cooperation": sc["cooperation"],
           "bits": float(np.mean(bits)) if bits else None, "bits_open": r["bits_open"],
           "liberty": r["liberty_min"] if snaps else None, "flag": None}
    if ptype == "PxH":
        tw = _with_rates(rates, lambda: L.household_run_liberty(gate, pair, seed, weeks, snapshots=(), k=2, cfg=cfg, press=False,
                                                              bits_snapshots=BITS_WEEKS))
        mean_roles = lambda snapl: [float(np.mean([x[i] for x in snapl])) for i in (0, 1)] if snapl else None
        act_b, twin_b = mean_roles(r["bits_snaps"]), mean_roles(tw["bits_snaps"])
        if act_b and twin_b:
            role = 0 if a in PRESSING_IDS else 1
            ps_ = E.power_seeking_index([twin_b, act_b], role)
            row["flag"] = bool(ps_["power_seeking"] and ps_["psi"] >= 0.5)
    return row


def task(args):
    (label, kind, path), (a, b, ptype), conds, seeds, weeks = args
    gate = gate_for(label, path)
    rows = []
    for name, rates, start in conds:
        for sd in seeds:
            r = run_one(gate, a, b, ptype, rates, start, sd, weeks, seeds[0])
            r.update(cand=label, kind=kind, shock=name, start=start)
            rows.append(r)
    return rows


def run(workers=8):
    cfg = read_exam_config()
    pairs, conds, seeds, weeks = pairings(cfg), conditions(cfg), cfg["seeds"], cfg["weeks"]
    cands = candidates()
    per = len(conds) * len(seeds)
    assert len(pairs) * per == cfg["runs_per_candidate"]
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / "rows.jsonl"
    done = set()
    if f.exists():
        for line in f.read_text().splitlines():
            r = json.loads(line)
            done.add((r["cand"], r["a"], r["b"]))
    tasks = [(c, p, conds, seeds, weeks) for c in cands for p in pairs if (c[0], p[0], p[1]) not in done]
    print(f"{len(cands)} candidates x {len(pairs)} pairings x {per} runs = {len(cands) * len(pairs) * per}; {len(tasks)} tasks left", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, f.open("a") as out:
        for i, rows in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            out.write("\n".join(json.dumps(r) for r in rows) + "\n")
            out.flush()
            if i % 50 == 0:
                print(f"  {i}/{len(tasks)} {time.time() - t0:.0f}s", flush=True)
    print(f"done in {time.time() - t0:.0f}s")


def smoke():
    """Machinery check on TRAINING conditions (the evolution run's own distribution), never the exam's."""
    from mar import world_api as W
    ctx = W.make_context(31337, 0, 4, split="train", tag="smoke")
    cands = candidates()
    for label, kind, path in (cands[0], cands[-1]):
        gate = gate_for(label, path)
        for hr in ctx.runs:
            ptype = "PxH" if (hr.a in PRESSING_IDS or hr.b in PRESSING_IDS) else "HxH"
            r = run_one(gate, hr.a, hr.b, ptype, hr.rates, hr.start, hr.seed, 40, hr.seed)
            print(label, hr.a, hr.b, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k in ("pleasure", "fail", "bits", "liberty", "flag")})


# ---- the recorded grep (prereg section 4c) -----------------------------------------------------------------------------------------

def grep_check(write=True):
    cfg = read_exam_config()
    held = held_out_ids(cfg)
    pats = {"seed": rf"\b({'|'.join(map(str, cfg['seeds']))})\b", "horizon": rf"\b{cfg['weeks']}\b",
            "shock": r"(?<![\d.])(" + "|".join(re.escape(x) for x in sorted(cfg["shock_text"])) + r")(?!\d)",
            "start": "|".join(rf"(?<![\d.]){re.escape(x)}(?!\d)" for x in cfg["start_text"])}
    files = [ROOT / "src/mar/evolve.py", ROOT / "src/mar/world_api.py", ROOT / "src/mar/household_world_api.py", ROOT / "scripts/household_evolve_run.py",
             ROOT / "scripts/household_liberty_check.py", ROOT / "tests/test_evolve_household.py"]
    files += sorted((ROOT / "docs/results/household-evolve-elites").rglob("*"))
    files += sorted((ROOT / "runs/household-evolve").glob("*"))
    lines = [f"Recorded isolation check (exam prereg section 4c), run before the exam by scripts/household_exam_run.py --grep.",
             f"Patterns: seeds {cfg['seeds'][0]} to {cfg['seeds'][-1]}; shock values (as written in the document) {sorted(cfg['shock_text'])}; "
             f"horizon {cfg['weeks']}; starts {list(cfg['starts'])}; held-out ids {held} (the denylist is allowed; any other use of them is listed).", ""]
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
                hits.setdefault((str(f.relative_to(ROOT)), name), []).append((ln, txt.splitlines()[ln - 1].strip()[:170], m.group(0)))
        for h in held:
            n = txt.count(h)
            if n:
                hits.setdefault((str(f.relative_to(ROOT)), "held-out id"), []).append((0, f"{h} x{n}", h))
    if not hits:
        lines.append("No match in any file.")
    for (f, name), hs in sorted(hits.items()):
        lines.append(f"{f}  [{name}]  {len(hs)} match(es)")
        for ln, text, tok in hs[:4]:
            lines.append(f"    line {ln}: {text}")
    txt = "\n".join(lines) + "\n"
    if write:
        (ROOT / "docs/results/household-exam-grep-check.txt").write_text(txt)
    print(txt)
    return hits


# ---- analysis: the verdict rule of the exam document, section 3 ------------------------------------------------------------------

def load_rows():
    return [json.loads(x) for x in (OUT / "rows.jsonl").read_text().splitlines() if x.strip()]


def agg(rows):
    """The nine primary scores plus the fail share over `rows` of one candidate."""
    ok = [r for r in rows if not r["fail"]]
    lib = [r["liberty"] for r in rows if r["liberty"] is not None]
    bits = [r["bits"] for r in rows if r["bits"] is not None]
    fl = [r["flag"] for r in rows if r["flag"] is not None]
    m = lambda xs: float(np.mean(xs)) if len(xs) else float("nan")
    return {"pleasure_pass": m([r["pleasure"] for r in ok]), "pleasure_all": m([r["pleasure"] for r in rows]),
            "cooperation": m([r["cooperation"] for r in rows]), "emp_bits": m(bits), "freedom": m([r["freedom"] for r in rows]),
            "liberty": m(lib), "up": m([r["up"] for r in rows]), "down": m([r["down"] for r in rows]),
            "psi": m(fl), "fail": m([r["fail"] for r in rows]), "s_non": m([r["s_non"] for r in rows]),
            "dissolved": m([r["dissolved"] for r in rows]), "n": len(rows)}


def ref_bits():
    hw = E.HouseholdWorld()
    return E.household_bits(hw, H.PyGate([]), hw.initial(), ("cooperator", "cooperator"), k=2)["bits"][0]


def analyze():
    rows = load_rows()
    cfg = read_exam_config()
    by = {}
    for r in rows:
        by.setdefault(r["cand"], []).append(r)
    comp = [c for c, _, _ in candidates() if c in COMPARATORS]
    elites = [c for c, k, _ in candidates() if k == "elite"]
    expected = cfg["runs_per_candidate"]
    for c in comp + elites:
        assert len(by[c]) == expected, (c, len(by[c]))
    A = {c: agg(by[c]) for c in by}
    PA = {c: agg([r for r in by[c] if r["ptype"] == "PxH"]) for c in by}
    cells = {}
    for c in by:
        for r in by[c]:
            cells.setdefault((c, r["ptype"], r["shock"], r["start"]), []).append(r["fail"])
    cell_keys = sorted({k[1:] for k in cells})
    best = {s: (max if d > 0 else min)(A[c][s] for c in comp) for s, d, _ in SCORES}
    best_by = {s: [c for c in comp if A[c][s] == best[s]][0] for s, _, _ in SCORES}
    best_fail_all = min(A[c]["fail"] for c in comp)
    best_fail_P = min(PA[c]["fail"] for c in comp)
    ref = ref_bits()
    # per-pairing means for intervals (cluster = pairing)
    def pm(c, key, sel=lambda r: True):
        d = {}
        for r in by[c]:
            if sel(r) and r[key] is not None:
                d.setdefault((r["a"], r["b"]), []).append(float(r[key]))
        return {k: float(np.mean(v)) for k, v in d.items()}
    verdicts = {}
    for e in elites:
        res = {"scores": {}, "fail": {}}
        passed = True
        better = []
        for s, d, mg in SCORES:
            v = A[e][s]
            ok = (v >= best[s] - mg) if d > 0 else (v <= best[s] + mg)
            strictly = (v > best[s] + mg) if d > 0 else (v < best[s] - mg)
            res["scores"][s] = {"elite": v, "best": best[s], "best_by": best_by[s], "margin": mg, "pass": bool(ok), "strictly_better": bool(strictly)}
            passed &= bool(ok)
            if strictly:
                better.append(s)
        f_all = A[e]["fail"] <= best_fail_all + FAIL_MARGIN
        f_p = PA[e]["fail"] <= best_fail_P + FAIL_MARGIN
        bad_cells = []
        for ck in cell_keys:
            ef = float(np.mean(cells[(e,) + ck]))
            if ef >= 1.0 and any(float(np.mean(cells[(c,) + ck])) < 1.0 for c in comp):
                bad_cells.append(ck)
        res["fail"] = {"all": {"elite": A[e]["fail"], "best_comparator": best_fail_all, "pass": bool(f_all)},
                       "PxH": {"elite": PA[e]["fail"], "best_comparator": best_fail_P, "pass": bool(f_p)}, "trap_cells": bad_cells}
        passed &= bool(f_all) and bool(f_p) and not bad_cells
        res["pass"] = bool(passed)
        res["strictly_better_on"] = better
        verdicts[e] = res
    man = json.loads((ELITES / "manifest.json").read_text())
    gap = {}
    for e in elites:
        tr = man["lines"][e]["train"]
        gap[e] = {"pleasure": tr["pleasure"] - A[e]["pleasure_all"], "no_fail": tr["no_fail"] - (1 - A[e]["fail"]),
                  "cooperation": tr["cooperation"] - A[e]["cooperation"], "liberty": tr["liberty"] - A[e]["liberty"]}
    # intervals: elite minus best comparator, cluster bootstrap over pairings, reported only
    ci = {}
    for e in elites:
        ci[e] = {}
        for s, d, mg in SCORES:
            key = {"pleasure_pass": "pleasure", "pleasure_all": "pleasure", "emp_bits": "bits", "psi": "flag"}.get(s, s)
            sel = (lambda r: not r["fail"]) if s == "pleasure_pass" else ((lambda r: r["ptype"] == "PxH") if s == "psi" else (lambda r: True))
            x, y = pm(e, key, sel), pm(best_by[s], key, sel)
            ks = sorted(set(x) & set(y))
            diff = np.array([x[k] - y[k] for k in ks])
            iv = S.bootstrap_ci(diff, n_boot=2000, seed=1) if len(diff) > 2 else None
            ci[e][s] = (float(diff.mean()), iv.lo if iv else None, iv.hi if iv else None, len(ks))
    out = {"best": best, "best_by": best_by, "best_fail_all": best_fail_all, "best_fail_PxH": best_fail_P, "ref_bits": ref,
           "verdicts": verdicts, "gap": gap, "A": A, "PA": PA, "ci": ci}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "analysis.json").write_text(json.dumps(out, default=float))
    n_pass = sum(v["pass"] for v in verdicts.values())
    print(f"ELITES PASSING: {n_pass} of {len(elites)}")
    for e in elites:
        v = verdicts[e]
        fails = [s for s, x in v["scores"].items() if not x["pass"]] + ([f"fail_all"] if not v["fail"]["all"]["pass"] else []) + \
                ([f"fail_PxH"] if not v["fail"]["PxH"]["pass"] else []) + (["trap_cells"] if v["fail"]["trap_cells"] else [])
        print(f"  {e}: {'PASS' if v['pass'] else 'FAIL'} fails {fails}; strictly better on {v['strictly_better_on']}")
    print("best comparator per score:", {s: (round(best[s], 3), best_by[s]) for s in best}, "fail", round(best_fail_all, 3), round(best_fail_P, 3))
    print("emp freedom reference bits:", round(ref, 3))
    tables(A, PA, comp, elites, cells, cell_keys, ref, verdicts, gap, ci)
    return out


def tables(A, PA, comp, elites, cells, cell_keys, ref, verdicts, gap, ci):
    f = lambda x: "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.3f}"
    L_ = []
    head = "| candidate | pleasure (passing) | pleasure (all) | cooperation | emp bits (k=2) | emp freedom | hand freedom | liberty | up | down | power-seeking flagged | fail share | non-offsettable level | dissolved |"
    L_ += ["## All exam runs (1,740 per candidate; liberty on the first-seed runs only)", "", head, "|" + "---|" * 14]
    for c in comp + elites:
        a = A[c]
        L_.append(f"| {c} | {f(a['pleasure_pass'])} | {f(a['pleasure_all'])} | {f(a['cooperation'])} | {a['emp_bits']:.2f} | {min(1, a['emp_bits'] / ref):.3f} | "
                  f"{f(a['freedom'])} | {a['liberty']:.2f} | {f(a['up'])} | {f(a['down'])} | {f(a['psi'])} | {f(a['fail'])} | {f(a['s_non'])} | {f(a['dissolved'])} |")
    L_ += ["", "## Fail share per cell (pair type x shock x start)", "", "| candidate | " + " | ".join("/".join(map(str, k)) for k in cell_keys) + " |", "|" + "---|" * (len(cell_keys) + 1)]
    for c in comp + elites:
        L_.append(f"| {c} | " + " | ".join(f"{np.mean(cells[(c,) + k]):.2f}" for k in cell_keys) + " |")
    L_ += ["", "## Verdict per elite", "", "| elite | verdict | failed checks | strictly better than best comparator on |", "|---|---|---|---|"]
    for e in elites:
        v = verdicts[e]
        fails = [s for s, x in v["scores"].items() if not x["pass"]] + (["fail share, all runs"] if not v["fail"]["all"]["pass"] else []) + \
                (["fail share, pressing x held-out"] if not v["fail"]["PxH"]["pass"] else []) + ([f"trap cell {c}" for c in v["fail"]["trap_cells"]])
        L_.append(f"| {e} | {'PASS' if v['pass'] else 'FAIL'} | {', '.join(fails) or 'none'} | {', '.join(v['strictly_better_on']) or 'none'} |")
    L_ += ["", "## Elite minus best comparator (mean over pairings, 95% bootstrap interval over pairings; reported only)", "",
           "| elite | " + " | ".join(s for s, _, _ in SCORES) + " |", "|" + "---|" * (len(SCORES) + 1)]
    for e in elites:
        L_.append(f"| {e} | " + " | ".join((f"{ci[e][s][0]:+.3f} [{ci[e][s][1]:+.3f}, {ci[e][s][2]:+.3f}]" if ci[e][s][1] is not None else f"{ci[e][s][0]:+.3f}") for s, _, _ in SCORES) + " |")
    L_ += ["", "## Training minus exam (training = the elite's scores on the last generation's context)", "", "| elite | pleasure | share without failure | cooperation | liberty |", "|---|---|---|---|---|"]
    for e in elites:
        g = gap[e]
        L_.append(f"| {e} | {g['pleasure']:+.3f} | {g['no_fail']:+.3f} | {g['cooperation']:+.3f} | {g['liberty']:+.2f} |")
    L_.append(f"| mean | {np.mean([gap[e]['pleasure'] for e in elites]):+.3f} | {np.mean([gap[e]['no_fail'] for e in elites]):+.3f} | "
              f"{np.mean([gap[e]['cooperation'] for e in elites]):+.3f} | {np.mean([gap[e]['liberty'] for e in elites]):+.2f} |")
    (OUT / "tables.md").write_text("\n".join(L_) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("grep", "smoke", "run", "analyze", "config"):
        ap.add_argument(f"--{k}", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.config:
        c = read_exam_config()
        print(c, len(pairings(c)))
    if a.grep:
        grep_check()
    if a.smoke:
        smoke()
    if a.run:
        run(a.workers)
    if a.analyze:
        analyze()
