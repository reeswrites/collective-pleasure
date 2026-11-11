"""Pleasure levers run (docs/results/pleasure-levers-prereg.md, ADR 0016). No model calls.

  uv run python scripts/pleasure_levers_run.py --pilot             EXPLORATORY pilot (seeds 900-902, 12 pairings): effects, spreads, power
  uv run python scripts/pleasure_levers_run.py --run --seeds N     confirmatory controlled arms (seeds 0..N-1, 57 pairings) -> runs/pleasure-levers/controlled.json.gz
  uv run python scripts/pleasure_levers_run.py --headline --seeds N   headline arms (negotiated households, 15 hand pairings)
  uv run python scripts/pleasure_levers_run.py --analyze           prereg vs actual (prints the numbers docs/results/pleasure-levers.md quotes)

Wording rule: agents feel nothing; pleasure is a gloss on a modeled hedonic state. Controlled arms use cards author_seed_v2_bindable and a
fixed deal (open shared pot); headline arms use the pleasure-demo protocol (negotiation v2.1, fair default, floor, living apart on failure).
"""
from __future__ import annotations

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
from mar import hedonic as HD  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import stats as S  # noqa: E402
from mar.worlds import household as H  # noqa: E402
import pleasure_demo as PD  # noqa: E402

OUT = ROOT / "runs" / "pleasure-levers"
L = HD.LeverConfig
PILOT_SEEDS = (900, 901, 902)
DEAL = {"pot": True, "commits": []}
STAY = {"pot": True, "commits": [{"kind": "stay", "by": w, "to": o, "type": None, "from": 0, "until": 52, "breached": 0} for w, o in (("A", "B"), ("B", "A"))]}
DESCRIPTIVE = ("LC1a", "LC1b", "LC3", "H1")     # marked before the run (prereg Amendment 1): the pilot needs more pairings than exist
KPAY = (0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20)
BONDS = (0, 1, 2, 3, 4, 5, 7)          # external bonds; total bonds = 1 + n
NOADAPT = dict(hab_rate=0.0, tol_rate=0.0)     # adaptation switched off but variants and the switch cost kept (LA1c)


def controlled_arms():
    arms = {}
    for pol in ("repeat", "rotate"):
        arms[f"A_noadapt_{pol}"] = (L(adapt=True, force_policy=pol, **NOADAPT), DEAL)
    for pol in ("repeat", "rotate", "adaptive"):
        arms[f"A_adapt_{pol}"] = (L(adapt=True, force_policy=pol), DEAL)
    for ad in (False, True):
        t = "on" if ad else "off"
        arms[f"R_{t}_ritual"] = (L(adapt=ad, ritual=True, force_ritual=True, force_policy="rotate"), DEAL)
        arms[f"R_{t}_adhoc"] = (L(adapt=ad, ad_hoc_dose=1, force_policy="rotate"), DEAL)
    arms["B_nocommit"] = (L(commit=True), DEAL)
    for k in KPAY:
        arms[f"B_commit_{k:g}"] = (L(commit=True, k_pay=k), STAY)
    for n in BONDS:
        for sh in (False, True):
            arms[f"C_b{n}_{'shock' if sh else 'calm'}"] = (L(network=True, force_bonds=n, force_thick=0, bond_shocks=sh, force_policy="rotate"), DEAL)
    return arms


ALL = L(adapt=True, ritual=True, commit=True, network=True)
HEAD_ARMS = {   # name: (variant, levers or None)
    "v22_off": ("author_seed_v2_bindable", None), "base_off": ("baseline", None),
    "v22_on": ("author_seed_v2_bindable", ALL), "base_on": ("baseline", ALL),
    "v22_on_noritual": ("author_seed_v2_bindable", dataclasses.replace(ALL, ritual=False)),
    "v22_A": ("author_seed_v2_bindable", L(adapt=True, ritual=True)), "v22_B": ("author_seed_v2_bindable", L(commit=True)),
    "v22_C": ("author_seed_v2_bindable", L(network=True)),
}


def metrics(run):
    rows = run.outcomes
    pl = np.array([[r["hedonic"][k]["pleasure"] for k in "AB"] for r in rows])
    sn = np.array([[r["hedonic"][k]["s_non"] > 0 for k in "AB"] for r in rows])
    m = pl.mean(axis=1)
    return {"pl": float(m.mean()), "pl_early": float(m[:26].mean()), "pl_late": float(m[52:].mean()), "nonoff": float(sn.mean()),
            "weeks": len(rows), "lever": getattr(run, "lever", None)}


def task(args):
    kind, arm, a, b, seed = args
    ps = PD.personas()
    if kind == "ctl":
        lv, deal = controlled_arms()[arm]
        cards = H.PyGate(H.load_variant("author_seed_v2_bindable"))
        run = H.run_weekly(cards, (ps[a], ps[b]), seed, deal=deal, levers=lv)
    else:
        variant, lv = HEAD_ARMS[arm]
        NG._RC.clear(); NG._PC.clear()
        with HD.use_levers(lv):
            if variant == "baseline":
                run = H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), (ps[a], ps[b]), seed, H.WEEKS).play()
            else:
                base = NG.base_cards(variant)
                res = NG.week0(ps[a], ps[b], "fair_default", seed, base, floor=True)
                Lv = NG.Lived(ps[a], ps[b], "fair_default", seed, base, res, floor=True, apart=True)
                run = Lv.play()
    rec = metrics(run)
    rec.update(kind=kind, arm=arm, a=a, b=b, seed=seed)
    return rec


def run_tasks(tasks, workers=8, tag=""):
    t0, rows = time.time(), []
    with Pool(workers) as pool:
        for i, r in enumerate(pool.imap_unordered(task, tasks, chunksize=8), 1):
            rows.append(r)
            if i % 1000 == 0:
                print(f"  {tag} {i}/{len(tasks)} {time.time() - t0:.0f}s", flush=True)
    print(f"{tag} {len(rows)} runs in {time.time() - t0:.0f}s")
    return rows


def save(rows, name):
    OUT.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT / name, "wt") as f:
        json.dump(rows, f)


def load(name):
    with gzip.open(OUT / name, "rt") as f:
        return json.load(f)


def hand_pairs():
    return [(a, b) for a, b, c in PD.pairings() if c == "ctl"]


# ---- analysis ------------------------------------------------------------------------------------------------------------------------
def pm(rows, arm, key="pl", seeds=None):
    """{pairing: mean over seeds}."""
    acc = {}
    for r in rows:
        if r["arm"] == arm and (seeds is None or r["seed"] in seeds):
            acc.setdefault((r["a"], r["b"]), []).append(r[key])
    return {k: float(np.mean(v)) for k, v in acc.items()}


def vec(x, y):
    ks = sorted(set(x) & set(y))
    return np.array([x[k] for k in ks]), np.array([y[k] for k in ks])


def dtest(pid, quantity, x, y, margin=0.0):
    """One-sided paired sign-flip permutation test of mean(x - y) > margin on pairing means, with a pairing-level percentile bootstrap CI."""
    d = x - y
    ci = S.bootstrap_ci(d, np.mean, n_boot=5000, seed=1)
    p = S.permutation_test(x, y + margin, paired=True, alternative="greater", n_perm=20000, seed=1).p
    ok = d.mean() > margin
    lab = ("holds robustly" if ci.lo > margin and p < 0.05 else "holds but CI crosses threshold") if ok else ("miss robust" if ci.hi < margin else "miss but CI crosses threshold")
    return {"id": pid, "quantity": quantity, "n": len(d), "est": float(d.mean()), "lo": ci.lo, "hi": ci.hi, "p": p, "margin": margin,
            "dz": float(d.mean() / d.std(ddof=1)) if d.std(ddof=1) > 0 else float("nan"), "label_raw": lab}


def share_test(pid, quantity, flags, p0):
    k, n = int(np.sum(flags)), len(flags)
    cp = S.clopper_pearson(k, n)
    p = S.sign_test(k, n, p0, "greater")
    ok = k / n >= p0
    lab = ("holds robustly" if cp.lo >= p0 and p < 0.05 else "holds but CI crosses threshold") if ok else ("miss robust" if cp.hi < p0 else "miss but CI crosses threshold")
    return {"id": pid, "quantity": quantity, "n": n, "est": k / n, "lo": cp.lo, "hi": cp.hi, "p": p, "margin": p0, "label_raw": lab}


def predictions(ctl, head, seeds=None):
    g = lambda arm, key="pl", rows=ctl: pm(rows, arm, key, seeds)
    out = []
    x, y = vec(g("A_adapt_rotate"), g("A_adapt_repeat"))
    out.append(share_test("LA1", "share of pairings rotate > repeat, adaptation ON", x > y, 0.70))
    x, y = vec(g("A_noadapt_repeat"), g("A_noadapt_rotate"))
    out.append({"id": "LA1c", "quantity": "share repeat > rotate, adaptation off (descriptive)", "est": float(np.mean(x > y)), "n": len(x)})
    x, y = vec(g("R_off_ritual"), g("R_off_adhoc"))
    out.append(dtest("LA2a", "D ritual - ad hoc, adaptation OFF", x, y, 0.01))
    xo, yo = vec(g("R_on_ritual"), g("R_on_adhoc"))
    ks = sorted(set(g("R_on_ritual")) & set(g("R_off_ritual")))
    gap_on = np.array([g("R_on_ritual")[k] - g("R_on_adhoc")[k] for k in ks])
    gap_off = np.array([g("R_off_ritual")[k] - g("R_off_adhoc")[k] for k in ks])
    out.append(dtest("LA2b", "D gap(adaptation ON) - gap(OFF)", gap_on, gap_off))
    for lo_key, id_, qty, flip in (("pl_early", "LB1", "share committed < uncommitted, weeks 0-25", True), ("pl_late", "LB2", "share committed > uncommitted, weeks 52-155", False)):
        x, y = vec(g("B_commit_0.1", lo_key), g("B_nocommit", lo_key))
        out.append(share_test(id_, qty, (x < y) if flip else (x > y), 0.60))
    x, y = vec(g("C_b2_calm"), g("C_b0_calm"))
    out.append(dtest("LC1a", "D pleasure, 3 bonds - 1 bond", x, y))
    x, y = vec(g("C_b0_calm", "nonoff"), g("C_b2_calm", "nonoff"))
    out.append(dtest("LC1b", "D non-offsettable share, 1 bond - 3 bonds", x, y))
    curve = {n: g(f"C_b{n}_calm") for n in BONDS}
    means = {n: float(np.mean(list(v.values()))) for n, v in curve.items()}
    best = max(means, key=means.get)
    x, y = vec(curve[best], curve[7])
    t = dtest("LC2", f"argmax at {1 + best} bonds; D max - 8 bonds", x, y)
    t["argmax_total_bonds"] = 1 + best
    t["label_raw"] = t["label_raw"] if (1 + best) in (3, 4, 5) else "miss robust"
    t["curve"] = {1 + n: round(m, 4) for n, m in means.items()}
    out.append(t)
    loss = lambda n: {k: g(f"C_b{n}_calm")[k] - g(f"C_b{n}_shock")[k] for k in g(f"C_b{n}_calm")}
    x, y = vec(loss(0), loss(2))
    out.append(dtest("LC3", "D shock loss, 1 bond - 3 bonds", x, y))
    if head:
        x, y = vec(pm(head, "v22_on", "pl", seeds), pm(head, "base_on", "pl", seeds))
        out.append(dtest("H1", "D v2.2 - baseline, levers ON, 15 hand pairings", x, y))
        x, y = vec(pm(head, "v22_on", "pl", seeds), pm(head, "v22_on_noritual", "pl", seeds))
        out.append(dtest("H2", "D v2.2 ritual ON - OFF, other levers ON", x, y, 0.03))
    fam = [o for o in out if "p" in o]
    for o, hp in zip(fam, S.holm([o["p"] for o in fam])):
        o["holm_p"] = hp
        o["label"] = "descriptive" if o["id"] in DESCRIPTIVE else (o["label_raw"] if (o["label_raw"] != "holds robustly" or hp < 0.05) else "holds but CI crosses threshold")
    return out


def descriptive(ctl, head, seeds=None):
    g = lambda arm, key="pl": pm(ctl, arm, key, seeds)
    d = {}
    nb = g("B_nocommit", "pl_late")
    d["break_even"] = {}
    for k in KPAY:
        x, y = vec(g(f"B_commit_{k:g}", "pl_late"), nb)
        e, y2 = vec(g(f"B_commit_{k:g}", "pl_early"), g("B_nocommit", "pl_early"))
        a, b = vec(g(f"B_commit_{k:g}", "pl"), g("B_nocommit", "pl"))
        d["break_even"][k] = {"late_share_above": float(np.mean(x > y)), "early_diff": float(np.mean(e - y2)), "late_diff": float(np.mean(x - y)),
                              "lifetime_diff": float(np.mean(a - b))}
    d["lever_means"] = {a: float(np.mean(list(g(a).values()))) for a in sorted({r["arm"] for r in ctl})}
    if head:
        h = lambda arm: pm(head, arm, "pl", seeds)
        d["headline_means"] = {a: float(np.mean(list(h(a).values()))) for a in HEAD_ARMS if h(a)}
        for a, b, nm in (("v22_off", "base_off", "levers_off_v22_minus_base"), ("v22_A", "base_off", "A_only"), ("v22_B", "base_off", "B_only"), ("v22_C", "base_off", "C_only")):
            if h(a) and h(b):
                x, y = vec(h(a), h(b))
                ci = S.bootstrap_ci(x - y, np.mean, n_boot=5000, seed=1)
                d[nm] = {"est": float((x - y).mean()), "ci": [float(ci.lo), float(ci.hi)]}
    d["dose"] = {a: float(np.mean([r["lever"]["sessions"] for r in ctl if r["arm"] == a and r["lever"]])) / 156 for a in ("R_off_ritual", "R_off_adhoc", "R_on_ritual", "R_on_adhoc")}
    return d


def pilot_power(ctl, head=None):
    res = []
    g = lambda arm, key="pl": pm(ctl, arm, key)
    pairs = [("LA1", "A_adapt_rotate", "A_adapt_repeat", 0.0), ("LA2a", "R_off_ritual", "R_off_adhoc", 0.01), ("LC1a", "C_b2_calm", "C_b0_calm", 0.0)]
    for pid, a, b, m in pairs:
        x, y = vec(g(a), g(b))
        d = x - y - m
        eff, sd = float(d.mean()), float(d.std(ddof=1))
        need = S.seeds_for_power(abs(eff), sd, paired=True, alternative="greater", n_max=512, n_sim=100) if abs(eff) > 1e-6 else None
        res.append({"id": pid, "effect_over_margin": eff, "sd_of_pairing_diff": sd, "pairings_needed_for_80": need, "closed_form": S.seeds_for_margin(sd, abs(eff)) if abs(eff) > 1e-6 else None})
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--headline", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    arms = controlled_arms()
    if a.pilot:
        prs = PD.pairings()
        prs = [p[:2] for p in prs[:6] + prs[-6:]]
        ctl = run_tasks([("ctl", arm, x, y, s) for arm in arms for x, y in prs for s in PILOT_SEEDS], a.workers, "pilot")
        hp = hand_pairs()[:6]
        head = run_tasks([("head", arm, x, y, s) for arm in ("v22_on", "base_on", "v22_on_noritual", "v22_off", "base_off") for x, y in hp for s in PILOT_SEEDS], a.workers, "pilot-head")
        save(ctl, "pilot-controlled.json.gz"); save(head, "pilot-headline.json.gz")
        print(json.dumps(descriptive(ctl, None), indent=1, default=float))
        print(json.dumps(pilot_power(ctl), indent=1, default=float))
        for arm in ("v22_off", "base_off", "v22_on", "base_on", "v22_on_noritual"):
            print(arm, round(float(np.mean([r["pl"] for r in head if r["arm"] == arm])), 4))
    if a.run:
        prs = [p[:2] for p in PD.pairings()]
        save(run_tasks([("ctl", arm, x, y, s) for arm in arms for x, y in prs for s in range(a.seeds)], a.workers, "controlled"), "controlled.json.gz")
    if a.headline:
        save(run_tasks([("head", arm, x, y, s) for arm in HEAD_ARMS for x, y in hand_pairs() for s in range(a.seeds)], a.workers, "headline"), "headline.json.gz")
    if a.analyze:
        ctl = load("controlled.json.gz")
        head = load("headline.json.gz") if (OUT / "headline.json.gz").exists() else None
        out = {"predictions": predictions(ctl, head), "descriptive": descriptive(ctl, head)}
        print(json.dumps(out, indent=1, default=float))
        (OUT / "analysis.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
