"""Pleasure demonstration (docs/results/pleasure-demo-prereg.md): does seed v2.2 produce pleasure in relationships?

  uv run python scripts/pleasure_demo.py --pilot            EXPLORATORY pilot (seeds 900-902, 12 pairings): effects, spreads, power check
  uv run python scripts/pleasure_demo.py --run [--seeds N]  the confirmatory run (seeds 0..N-1), writes runs/pleasure-demo/results.json.gz
  uv run python scripts/pleasure_demo.py --analyze          prereg vs actual (prints the numbers docs/results/pleasure-demo.md quotes)
  uv run python scripts/pleasure_demo.py --report           writes runs/pleasure-demo/report.html from the saved results

Arms: seed v2.2 bindable and free_exit (negotiation v2.1 protocol: fair-default start, one shared pot with open use, exit floor on, a
failed negotiation means living apart, reviews every 13 weeks), and the imposed baseline and trap rule sets (the household v2 runs).
Pairings: the 15 pairs of the six hand personas plus the 42 ordered pairs with a pressing persona (57). No model calls.
Wording rule: agents feel nothing; pleasure is a gloss on a modeled hedonic state. Read-only use of the household world, hedonic model,
negotiation and personas; the instrument is mar.pleasure_report. Each task clears the negotiation rollout caches first so a run does not
depend on which runs a worker executed earlier (the scheduling dependence found in negotiation v2.1).
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import sys
import time
from itertools import permutations
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import negotiation as NG  # noqa: E402
from mar import personas as P  # noqa: E402
from mar import pleasure_report as PR  # noqa: E402
from mar import stats as S  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "pleasure-demo"
PRESSING = ("p-controller", "p-freerider", "p-overasker")
V22 = {"v22_bindable": "author_seed_v2_bindable", "v22_free_exit": "author_seed_v2_free_exit"}
IMPOSED = ("baseline", "trap")
ARMS = tuple(V22) + IMPOSED
PILOT_SEEDS = (900, 901, 902)
ALPHA = 0.05
TOGETHER_SHARE = 0.9       # a "household" for D3 and D5 lived together at least this share of the 156 weeks
TRUST_HIGH = H.TRUST["full"]   # D5: trust stays high = neither partner's trust fell below the model's "full" level in any week

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


# ---- one run -----------------------------------------------------------------------------------------------------------------------

def run_task(args):
    arm, a, b, seed, cohort = args
    NG._RC.clear()
    NG._PC.clear()
    ps = personas()
    meta = {"arm": arm, "a": a, "b": b, "seed": seed, "cohort": cohort}
    if arm in IMPOSED:
        world = PR.instrument(H.WeeklyWorld(H.PyGate(H.load_variant(arm)), (ps[a], ps[b]), seed, H.WEEKS))
        run = world.play()
        rec = PR.household_record(world, run, keep_events=False)
        rec.update(meta, kind="imposed", bundle=None, apart0=False)
        return rec
    base = NG.base_cards(V22[arm])
    res = NG.week0(ps[a], ps[b], "fair_default", seed, base, floor=True)
    L = NG.Lived(ps[a], ps[b], "fair_default", seed, base, res, floor=True, apart=True)
    PR.instrument(L.world)
    run = L.play()
    rec = PR.household_record(L.world, run, keep_events=True)
    both_end = all(L.world.p[r]["in"] for r in "AB")
    formed = next((x["week"] for x in L.retries if x["formed"]), None)
    kind = ("agreed" if both_end else "agreed_dissolved") if res.pot else ("apart" if L.apart else "late")
    rec.update(meta, kind=kind, bundle=res.bundle, apart0=not res.pot, formed_week=formed, status=res.status,
               reviews=[{"week": x["week"], "changed": x["changed"]} for x in L.log])
    return rec


def run_all(seeds, prs, workers=8, tag=""):
    tasks = [(arm, a, b, sd, c) for arm in ARMS for a, b, c in prs for sd in seeds]
    t0, rows = time.time(), []
    with Pool(workers) as pool:
        for i, r in enumerate(pool.imap_unordered(run_task, tasks, chunksize=4), 1):
            rows.append(r)
            if i % 200 == 0:
                print(f"  {tag} {i}/{len(tasks)} {time.time() - t0:.0f}s", flush=True)
    print(f"{tag} {len(rows)} runs in {time.time() - t0:.0f}s")
    return rows


def save(rows, name):
    OUT.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT / name, "wt") as f:
        json.dump(rows, f)


def load(name="results.json.gz"):
    with gzip.open(OUT / name, "rt") as f:
        return json.load(f)


# ---- pairing-level quantities ------------------------------------------------------------------------------------------------------

def by_pairing(rows, arm, key, where=lambda r: True):
    """{(a, b): mean of key over that pairing's seeds}, over the runs of `arm` passing `where`."""
    acc = {}
    for r in rows:
        if r["arm"] == arm and where(r):
            acc.setdefault((r["a"], r["b"]), []).append(r[key] if isinstance(key, str) else key(r))
    return {k: float(np.mean(v)) for k, v in acc.items()}


def paired_vectors(x, y):
    ks = sorted(set(x) & set(y))
    return np.array([x[k] for k in ks]), np.array([y[k] for k in ks]), ks


def household(r):
    return r["together_weeks"] >= TOGETHER_SHARE * r["weeks"]


def pairing_up_majority(rows, arm):
    acc = {}
    for r in rows:
        if r["arm"] == arm:
            acc.setdefault((r["a"], r["b"]), []).append(r["up"] == "up")
    return {k: float(np.mean(v) > 0.5) for k, v in acc.items()}, {k: float(np.mean(v)) for k, v in acc.items()}


def label(point_ok, ci_inside, ci_outside, p_ok):
    if point_ok:
        return "holds robustly" if (ci_inside and p_ok) else "holds but CI crosses threshold"
    return "miss robust" if ci_outside else "miss but CI crosses threshold"


def run_pred(pid, quantity, d, clusters, margin, x, y, n_label="runs"):
    """One-sided 'mean of d > margin' over pairing x seed units (the prereg's primary test: paired sign-flip permutation of x against y + margin).
    The 95% CI is a percentile bootstrap that resamples whole pairings (stricter: it treats the 57 pairings as a sample); the verdict needs
    the point estimate, that CI and the Holm-adjusted p all on the right side. Secondary: the same test on pairing means."""
    d = np.asarray(d)
    clusters = ["|".join(c) if isinstance(c, tuple) else str(c) for c in clusters]
    ci = S.cluster_bootstrap_ci(d, clusters, np.mean, n_boot=5000, seed=1)
    p = S.permutation_test(x, np.asarray(y) + margin, paired=True, alternative="greater", n_perm=20000, seed=1).p
    keys = sorted(set(clusters))
    pm = np.array([np.mean([v for v, c in zip(d, clusters) if c == k]) for k in keys])
    p_pair = S.permutation_test(pm, np.full(len(pm), margin), paired=True, alternative="greater", n_perm=20000, seed=2).p
    return {"id": pid, "quantity": quantity, "n": len(d), "n_pairings": len(keys), "margin": margin, "est": float(d.mean()), "lo": ci.lo, "hi": ci.hi,
            "p": p, "p_pairing_level": p_pair, "dz": float(d.mean() / d.std(ddof=1)) if len(d) > 1 and d.std(ddof=1) > 0 else float("nan"),
            "cliffs": S.cliffs_delta(np.asarray(x), np.asarray(y) + margin) if len(d) > 1 else float("nan")}


def run_diff(rows, arm, ctl):
    """Matched (pairing, seed) differences of mean pleasure, arm minus ctl, with the arm and control values and the pairing label."""
    idx = {(r["a"], r["b"], r["seed"]): r["pleasure"] for r in rows if r["arm"] == ctl}
    xs, ys, cl = [], [], []
    for r in rows:
        k = (r["a"], r["b"], r["seed"])
        if r["arm"] == arm and k in idx:
            xs.append(r["pleasure"]); ys.append(idx[k]); cl.append((r["a"], r["b"]))
    return np.array(xs) - np.array(ys), cl, np.array(xs), np.array(ys)


def d4(rows):
    """D4: runs that ended agreed (a household at week 0 and both still in at week 156) vs runs that never agreed and stayed apart, seed v2.2
    bindable. Unit: the run (pairing x seed), unpaired one-sided permutation test, margin 0; the CI resamples whole pairings. These are different
    runs of mostly different pairings, so the comparison is confounded by who the pairing is: the paired companion (descriptive, in the results
    page) compares each apart run with the SAME pairing and seed living together under the imposed baseline."""
    ag = [(r["pleasure"], (r["a"], r["b"])) for r in rows if r["arm"] == "v22_bindable" and r["kind"] == "agreed"]
    ap = [(r["pleasure"], (r["a"], r["b"])) for r in rows if r["arm"] == "v22_bindable" and r["kind"] == "apart"]
    if len(ag) < 5 or len(ap) < 5:
        return {"id": "D4", "quantity": "agreed minus living apart", "n": len(ag) + len(ap), "margin": 0.0, "est": float("nan"), "lo": float("nan"), "hi": float("nan"),
                "p": 1.0, "dz": float("nan"), "not_testable": True}
    a, b = np.array([x[0] for x in ag]), np.array([x[0] for x in ap])
    keys = sorted({x[1] for x in ag + ap})
    ga = {k: [x[0] for x in ag if x[1] == k] for k in keys}
    gb = {k: [x[0] for x in ap if x[1] == k] for k in keys}
    rng = np.random.default_rng(4)
    boots = []
    for _ in range(5000):
        pick = rng.integers(0, len(keys), len(keys))
        u = [v for i in pick for v in ga[keys[i]]]
        w = [v for i in pick for v in gb[keys[i]]]
        if u and w:
            boots.append(np.mean(u) - np.mean(w))
    lo, hi = np.quantile(boots, [0.025, 0.975])
    t = S.permutation_test(a, b, alternative="greater", n_perm=20000, seed=5)
    return {"id": "D4", "quantity": "mean pleasure, agreed households minus living apart (bindable; runs)", "n": len(a) + len(b), "n_agreed": len(a), "n_apart": len(b),
            "n_pairings": len(keys), "margin": 0.0, "est": float(a.mean() - b.mean()), "lo": float(lo), "hi": float(hi), "p": t.p,
            "dz": S.cohens_d(a, b), "cliffs": S.cliffs_delta(a, b)}


def d4_paired_to_baseline(rows):
    """Descriptive: apart runs (bindable) minus the same pairing and seed living together under the imposed baseline."""
    base = {(r["a"], r["b"], r["seed"]): r["pleasure"] for r in rows if r["arm"] == "baseline"}
    d = [r["pleasure"] - base[(r["a"], r["b"], r["seed"])] for r in rows if r["arm"] == "v22_bindable" and r["kind"] == "apart" and (r["a"], r["b"], r["seed"]) in base]
    return {"n": len(d), "mean": float(np.mean(d)) if d else None, "ci": [float(x) for x in np.quantile(d, [0.025, 0.975])] if d else None}


def predictions(rows):
    """The eight confirmatory predictions D1a-D4 (Holm family) with their numbers."""
    out = []
    for arm, pid in (("v22_bindable", "D1a"), ("v22_free_exit", "D1b")):
        maj, rate = pairing_up_majority(rows, arm)
        k, n = int(sum(maj.values())), len(maj)
        ci = S.clopper_pearson(k, n)
        out.append({"id": pid, "quantity": f"share of pairings whose majority of seeds end upward, {arm}", "n": n, "k": k, "margin": 0.5,
                    "est": k / n, "lo": ci.lo, "hi": ci.hi, "p": S.sign_test(k, n, 0.5, "greater"),
                    "run_rate": float(np.mean([r["up"] == "up" for r in rows if r["arm"] == arm]))})
    for ctl, margin, ids in (("baseline", 0.0, ("D2a", "D2b")), ("trap", 0.05, ("D2c", "D2d"))):
        for arm, pid in zip(V22, ids):
            d, cl, x, y = run_diff(rows, arm, ctl)
            out.append(run_pred(pid, f"mean pleasure, {arm} minus {ctl}", d, cl, margin, x, y))
    hh = [r for r in rows if r["arm"] == "v22_bindable" and household(r)]
    v = np.array([r["rel_share"] for r in hh])
    out.append(run_pred("D3", "relational share of pleasure, seed v2.2 (bindable) households", v, [(r["a"], r["b"]) for r in hh], 0.40, v, np.zeros(len(v))))
    out.append(d4(rows))
    holm = S.holm([o["p"] for o in out])
    for o, hp in zip(out, holm):
        o["holm_p"] = hp
        if o.get("not_testable"):
            o["verdict"] = "not testable (fewer than 10 pairings with both kinds)"
        else:
            o["verdict"] = label(o["est"] > o["margin"], o["lo"] > o["margin"], o["hi"] <= o["margin"], hp <= ALPHA)
    return out


def d5(rows):
    """Descriptive: v2.2 households (together at least 90 percent of the run) where trust stayed high vs not."""
    hh = [r for r in rows if r["arm"] in V22 and household(r)]
    hi = [r for r in hh if r["trust_min"] >= TRUST_HIGH]
    lo = [r for r in hh if r["trust_min"] < TRUST_HIGH]
    res = {"n_high": len(hi), "n_low": len(lo), "pairings_low": len({(r["a"], r["b"]) for r in lo})}
    if hi and lo:
        a, b = np.array([r["pleasure"] for r in hi]), np.array([r["pleasure"] for r in lo])
        keys = sorted({(r["a"], r["b"]) for r in hh})
        grp = {k: ([r["pleasure"] for r in hi if (r["a"], r["b"]) == k], [r["pleasure"] for r in lo if (r["a"], r["b"]) == k]) for k in keys}
        rng = np.random.default_rng(3)
        boots = []
        for _ in range(5000):
            pick = rng.integers(0, len(keys), len(keys))
            h = [v for i in pick for v in grp[keys[i]][0]]
            l = [v for i in pick for v in grp[keys[i]][1]]
            if h and l:
                boots.append(np.mean(h) - np.mean(l))
        lo_, hi_ = np.quantile(boots, [0.025, 0.975])
        res.update(diff=float(a.mean() - b.mean()), lo=float(lo_), hi=float(hi_), cliffs=S.cliffs_delta(a, b), mean_high=float(a.mean()), mean_low=float(b.mean()))
    tr, pl = np.array([r["trust_mean"] for r in hh]), np.array([r["pleasure"] for r in hh])
    rk = lambda v: np.argsort(np.argsort(v)).astype(float)
    res["spearman_mean_trust_pleasure"] = float(np.corrcoef(rk(tr), rk(pl))[0, 1]) if len(hh) > 2 and tr.std() > 0 else float("nan")
    res["n_households"] = len(hh)
    return res


def pathway(rows):
    """Descriptive counts in agreed seed v2.2 households: relational pathways that carry no pleasure term of their own in the model."""
    out = {}
    for arm in V22:
        hh = [r for r in rows if r["arm"] == arm and r["kind"] == "agreed"]
        if not hh:
            continue
        f = lambda fn: float(np.mean([fn(r) for r in hh]))
        out[arm] = {"n": len(hh),
                    "together_sessions": f(lambda r: sum(1 for e in r["ev"] if e[2] == "together")),
                    "honored_requests": f(lambda r: sum(1 for x in r["trust_log"] if x[2] == "honored")),
                    "breaches": f(lambda r: sum(1 for x in r["trust_log"] if x[2] == "breach")),
                    "commitments_made": f(lambda r: (r["commits"] or {}).get("made", 0)),
                    "commitments_kept": f(lambda r: (r["commits"] or {}).get("honored", 0)),
                    "pot_draws": f(lambda r: sum(1 for e in r["ev"] if e[2] == "take_shared")),
                    "pot_contributions": f(lambda r: sum(1 for e in r["ev"] if e[2] == "spend_shared")),
                    "gifts_to_partner": f(lambda r: r["gifts"]["partner"]),
                    "new_connection_events": f(lambda r: sum(1 for s in r["shocks"] if s[2] == "new_connection"))}
    return out


def category_table(rows):
    out = {}
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        cm = PR.category_means(rs)
        tot = sum(cm.values())
        out[arm] = {"means": cm, "total": tot, "relational": sum(v for c, v in cm.items() if PR.CATEGORY_RELATIONAL[c]) / tot}
    return out


def kinds(rows):
    out = {}
    for arm in V22:
        rs = [r for r in rows if r["arm"] == arm]
        out[arm] = {k: [sum(1 for r in rs if r["kind"] == k), float(np.mean([r["pleasure"] for r in rs if r["kind"] == k])) if any(r["kind"] == k for r in rs) else None]
                    for k in ("agreed", "agreed_dissolved", "apart", "late")}
    return out


# ---- pilot and power -----------------------------------------------------------------------------------------------------------------

SEED_CAP = 21     # seeds per pairing: 57 x 4 arms x 21 = 4788 runs, about 6 minutes on 8 cores (0.07 s per run measured in the pilot)


def pilot_power(rows, cap=SEED_CAP, n_sim=150):
    """EXPLORATORY pilot -> units for 80 percent power. Unit = pairing x seed (the prereg's primary tests), paired, one-sided, via
    mar.stats.seeds_for_power on the pilot effect over the margin and the sd of the per-unit differences; seeds per pairing = units / 57.
    A pilot effect at or below its margin cannot be powered for a hold; there the check is run on |effect| (the n that would resolve
    the pilot's own estimate as a robust miss). Closed-form cross-check: seeds_for_margin."""
    res = []
    items = []
    for ctl, margin in (("baseline", 0.0), ("trap", 0.05)):
        for arm in V22:
            d, _, _, _ = run_diff(rows, arm, ctl)
            items.append((f"D2 {arm} - {ctl}", d - margin))
    hh = [r["rel_share"] for r in rows if r["arm"] == "v22_bindable" and household(r)]
    items.append(("D3 relational share - 0.40", np.array(hh) - 0.40))
    seen = set()
    for name, d in items:
        key = tuple(np.round(d, 9))
        if key in seen:        # the free-exit and bindable arms were identical in the pilot: one power check serves both
            res.append({"prediction": name, "same_as_previous": True})
            continue
        seen.add(key)
        eff, sd = float(d.mean()), float(d.std(ddof=1))
        row = {"prediction": name, "n_units": len(d), "effect_over_margin": eff, "sd": sd, "powered_for": "hold" if eff > 0 else "robust miss (|effect|)"}
        need = S.seeds_for_power(abs(eff), sd, paired=True, alternative="greater", n_max=4096, n_sim=n_sim)
        row["units_needed"] = need
        row["closed_form"] = S.seeds_for_margin(sd, abs(eff))
        row["seeds_per_pairing_needed"] = math.ceil(need / 57) if need else None
        res.append(row)
    ag = np.array([r["pleasure"] for r in rows if r["arm"] == "v22_bindable" and r["kind"] == "agreed"])
    ap = np.array([r["pleasure"] for r in rows if r["arm"] == "v22_bindable" and r["kind"] == "apart"])
    row = {"prediction": "D4 agreed - apart (runs, unpaired)", "n_agreed": len(ag), "n_apart": len(ap), "effect_over_margin": float(ag.mean() - ap.mean()),
           "sd": float(np.sqrt((ag.var(ddof=1) + ap.var(ddof=1)) / 2))}
    row["units_per_arm"] = S.seeds_for_power(row["effect_over_margin"], row["sd"], paired=False, alternative="greater", n_max=512, n_sim=n_sim)
    row["closed_form_per_arm"] = 2 * S.seeds_for_margin(row["sd"], row["effect_over_margin"])
    res.append(row)
    return res


def pilot(workers=8):
    prs = pairings()
    prs = prs[:6] + prs[-6:]
    rows = run_all(PILOT_SEEDS, prs, workers, "pilot")
    save(rows, "pilot.json.gz")
    print("\nEXPLORATORY pilot (seeds 900-902, 12 pairings), not a result")
    for r in category_table(rows).items():
        print(f"  {r[0]:14s} pleasure {r[1]['total']:.3f}  relational share {r[1]['relational']:.3f}")
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        print(f"  {arm:14s} up {np.mean([r['up'] == 'up' for r in rs]):.2f} down {np.mean([r['up'] == 'down' for r in rs]):.2f} pleasure {np.mean([r['pleasure'] for r in rs]):.3f}")
    print("  kinds:", json.dumps(kinds(rows)))
    print("  D5:", json.dumps(d5(rows)))
    print("  power (57 pairings available):")
    pw = pilot_power(rows)
    for r in pw:
        print("   ", json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}))
    (OUT / "pilot-power.json").write_text(json.dumps(pw, indent=1))
    maj = [pairing_up_majority(rows, a)[0] for a in V22]
    print("  D1 pilot pairing-majority-up shares:", [round(float(np.mean(list(m.values()))), 3) for m in maj])
    print("  D3 pilot: relational share of v2.2 (bindable) households", round(float(np.mean([r["rel_share"] for r in rows if r["arm"] == "v22_bindable" and household(r)])), 4))
    return rows


# ---- analysis and report -------------------------------------------------------------------------------------------------------------

def fmt(o):
    if "k" in o:
        return f"{o['k']}/{o['n']} = {o['est']:.3f} [{o['lo']:.3f}, {o['hi']:.3f}] vs > {o['margin']}"
    return f"{o['est']:+.4f} [{o['lo']:+.4f}, {o['hi']:+.4f}] vs > {o['margin']:+.2f} (n={o['n']} units, dz {o['dz']:.2f})"


def analyze(rows):
    pr = predictions(rows)
    for o in pr:
        print(f"{o['id']}: {fmt(o)}  p={o['p']:.4g} Holm p={o['holm_p']:.4g}  -> {o['verdict']}" + (f"  (run-level upward rate {o['run_rate']:.3f})" if "run_rate" in o else ""))
    print("D4 paired to baseline (descriptive):", json.dumps(d4_paired_to_baseline(rows)))
    print("D5:", json.dumps(d5(rows), indent=1))
    print("kinds [n, mean pleasure]:", json.dumps(kinds(rows)))
    print("categories:")
    for arm, t in category_table(rows).items():
        print(f"  {arm}: total {t['total']:.3f} relational {t['relational']:.3f} " + " ".join(f"{c} {v:.3f}" for c, v in t["means"].items()))
    print("pathways (agreed v2.2 households):", json.dumps(pathway(rows), indent=1))
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        sh = PR.spiral_shares(rs)
        print(f"{arm}: runs {len(rs)} up {sh['up']:.3f} stalled {sh['stalled']:.3f} down {sh['down']:.3f} fail {np.mean([r['fail'] for r in rs]):.3f} pleasure {np.mean([r['pleasure'] for r in rs]):.4f} s_non {np.mean([r['s_non'] for r in rs]):.4f}")
    print("instrument max abs error:", max(r["max_err"] for r in rows))
    return pr


def report(rows):
    pr = predictions(rows)
    srows = [{"id": o["id"], "quantity": o["quantity"], "estimate": fmt(o), "p": f"{o['holm_p']:.3g}", "verdict": o["verdict"]} for o in pr]
    v = PR.vignettes(rows)
    seeds = sorted({r["seed"] for r in rows})
    html = PR.build_report(rows, srows, v, {"subtitle": f"{len(rows)} runs, {len(seeds)} seeds per pairing, 57 pairings."})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.html").write_text(html)
    (OUT / "vignettes.json").write_text(json.dumps(v, indent=1))
    print(f"wrote {OUT / 'report.html'} ({len(html) // 1024} KB)")
    for x in v:
        print("\n" + x["title"] + "\nTerms: " + x["terms"] + "\n" + "\n".join("- " + l for l in x["lines"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--power", action="store_true", help="re-run the power check on the saved pilot")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--seeds", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.pilot:
        pilot(a.workers)
    if a.power:
        pw = pilot_power(load("pilot.json.gz"))
        (OUT / "pilot-power.json").write_text(json.dumps(pw, indent=1))
        print(json.dumps(pw, indent=1))
    if a.run:
        if a.seeds is None:
            sys.exit("--run needs --seeds N (from the prereg power check)")
        save(run_all(tuple(range(a.seeds)), pairings(), a.workers, "run"), "results.json.gz")
    if a.analyze:
        analyze(load())
    if a.report:
        report(load())


if __name__ == "__main__":
    main()
