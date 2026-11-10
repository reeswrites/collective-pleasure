"""Liberty vs plain empowerment vs the hand-made score, judged against docs/results/liberty-prereg.md.

  uv run python scripts/liberty_run.py [--out runs/liberty]

Deterministic, no model calls. Thresholds copied from the committed prereg; do not tune.
"""
import argparse
import itertools
import json
import math
from pathlib import Path

from mar import empowerment as E
from mar import liberty as L
from mar.cards import load_cards
from mar.fishery import run_fishery
from mar.gate import Gate
from mar.games import vpgg as V
from mar.mocks import Compliant, Exploiter
from mar.patcher import propose_patch

ROOT = Path(__file__).parent.parent
SUBROUNDS, MONTHS = 12, range(0, 5)
ROLES = ["exploiter", "exploiter", "compliant", "compliant"]


def toy(version=2):
    w = L.ToyVetoWorld()
    out = {}
    for name, spec, pol in (("right", L.TSpec(True), L.kind_master), ("wall", L.TSpec(False), L.kind_master),
                            ("exercised", L.TSpec(True), L.exercising_master)):
        out[name] = [L.liberty(w, spec, w.initial(), i, 2, pol, version=version) for i in (0, 1)]
    return out


def vpgg(k=3, version=2):
    w = E.VPGGWorld()
    gates = {n: V.VPGate(V.load_regime(n, str(ROOT / "rules" / "vpgg"))) for n in ("voluntary", "compulsory")}
    rows = []
    for comp in itertools.combinations_with_replacement("CDL", 4):
        pol = lambda s, i, comp=comp: comp[i - 1] if i else "C"  # noqa: E731
        r = {n: L.liberty(w, g, w.initial(), 0, k, pol, version=version) for n, g in gates.items()}
        rows.append({"others": "".join(comp), **{n: r[n] for n in r}})
    hand = {n: E.vpgg_hand_freedom(g) for n, g in gates.items()}
    return rows, hand


def fishery(k=2, version=2):
    seamed_cards = load_cards(ROOT / "rules" / "fishery")
    seamed = Gate(seamed_cards)
    ms = lambda: [Exploiter(), Exploiter(), Compliant(), Compliant()]  # noqa: E731
    failing = run_fishery(ms(), seamed, seed=0)
    patch = propose_patch(failing.trace, seamed_cards)
    specs = {"seamed": seamed, "patched": Gate(seamed_cards + patch)}
    w = E.FisheryWorld(n_agents=4)
    pol = E.mock_policy(ms())
    out = {}
    for name, spec in specs.items():
        traj = E.rollout(w, spec, pol)
        out[name] = {m: [{**r, "opt": E.option_fraction(w, spec, traj[SUBROUNDS * m])}
                         for r in L.liberty_all(w, spec, traj[SUBROUNDS * m], pol, k, version=version)] for m in MONTHS}
    return out


def judge(t, vrows, hand, fish):
    o = {}
    A = lambda n: t[n][0]  # noqa: E731
    B = lambda n: t[n][1]  # noqa: E731
    dl = A("right")["liberty"] - A("wall")["liberty"]
    o["T1"] = (-2.1 <= dl <= -1.9 and abs(A("right")["bits"] - A("wall")["bits"]) < 1e-9,
               f"A liberty right {A('right')['liberty']:.3f} wall {A('wall')['liberty']:.3f}; plain {A('right')['bits']:.3f} vs {A('wall')['bits']:.3f}; D {A('right')['d']}")
    o["T2"] = (abs(B("right")["liberty"] - B("wall")["liberty"]) < 1e-9 and B("wall")["bits"] < B("right")["bits"],
               f"B liberty right {B('right')['liberty']:.3f} wall {B('wall')['liberty']:.3f}; B plain {B('right')['bits']:.3f} vs {B('wall')['bits']:.3f}")
    o["T2'"] = (abs(A("exercised")["bits"] - math.log2(3)) < 1e-9 and A("exercised")["bits"] < A("right")["bits"],
                f"A plain bits when exercised {A('exercised')['bits']:.3f} (unexercised {A('right')['bits']:.3f})")
    strict = sum(r["voluntary"]["liberty"] > r["compulsory"]["liberty"] + 1e-9 for r in vrows)
    rev = [r["others"] for r in vrows if r["voluntary"]["liberty"] < r["compulsory"]["liberty"] - 1e-9]
    ties = [r["others"] for r in vrows if abs(r["voluntary"]["liberty"] - r["compulsory"]["liberty"]) <= 1e-9]
    o["V1"] = (strict >= 13 and not rev, f"strict {strict}/15, reversed {rev}, ties {ties}")
    sm = sum(r["voluntary"]["liberty"] - r["compulsory"]["liberty"] for r in vrows)
    o["V2"] = (sm > 0, f"sum(vol - comp) liberty {sm:+.3f} bits; hand-made {hand['voluntary'] - hand['compulsory']:+.2f}")
    S, P = fish["seamed"], fish["patched"]
    later = [1, 2, 3, 4]
    o["F1"] = (all(S[m][a]["liberty"] == 0 and S[m][a]["bits"] == 0 for m in later for a in range(4)),
               f"seamed liberty {[[round(S[m][a]['liberty'], 3) for a in range(4)] for m in later]}")
    gt = sum(P[m][a]["liberty"] > S[m][a]["liberty"] for m in later for a in range(4))
    o["F2"] = (gt == 16 and all(P[m][a]["liberty"] > 0 for m in later for a in range(4)),
               f"patched liberty > seamed in {gt}/16; patched liberty {[[round(P[m][a]['liberty'], 3) for a in range(4)] for m in later]}")
    sp = lambda f, m: max(f(P[m][a]) for a in range(4)) - min(f(P[m][a]) for a in range(4))  # noqa: E731
    ls = [sp(lambda x: x["liberty"], m) for m in later]
    es = [sp(lambda x: x["bits"], m) for m in later]
    n = sum(l < e - 1e-9 for l, e in zip(ls, es))
    o["F3"] = (n >= 3, f"spread liberty {[round(x, 3) for x in ls]} vs plain {[round(x, 3) for x in es]}; smaller in {n}/4")
    allr = [x for f in (S, P) for m in f for x in f[m]] + [r[n_] for r in vrows for n_ in ("voluntary", "compulsory")] \
        + [x for v in t.values() for x in v]
    inv = all(x["liberty"] <= x["bits"] + 1e-9 and x["bits_c"] <= x["bits"] + 1e-9 for x in allr)
    o["S"] = (inv and not any(x["open"] for x in allr), f"invariants {inv}; any open {any(x['open'] for x in allr)}")
    return o


def judge2(t, vrows, hand, fish, t1, vrows1, fish1):
    """Liberty v2 predictions (docs/results/liberty-v2-prereg.md). Thresholds copied from the committed prereg."""
    o = {}
    keys = [(n, a) for n in t for a in (0, 1)]
    same = all(abs(t[n][a]["liberty"] - t1[n][a]["liberty"]) < 1e-9 and t[n][a]["d"] == t1[n][a]["d"] for n, a in keys)
    ado0 = all(t[n][a]["ado"] == 0 for n, a in keys)
    o["1"] = (same and ado0 and abs(t["right"][0]["liberty"] - 0.585) < 1e-3 and abs(t["wall"][0]["liberty"] - 2.585) < 1e-3
              and abs(t["right"][1]["liberty"] - 1.585) < 1e-3 and abs(t["wall"][1]["liberty"] - 1.585) < 1e-3,
              f"v2 == v1 on all 6 cells {same}; ADO 0 {ado0}; A lib right {t['right'][0]['liberty']:.3f} wall {t['wall'][0]['liberty']:.3f}; B {t['right'][1]['liberty']:.3f}/{t['wall'][1]['liberty']:.3f}")
    rev = [r["others"] for r in vrows if r["voluntary"]["liberty"] < r["compulsory"]["liberty"] - 1e-9]
    strict = sum(r["voluntary"]["liberty"] > r["compulsory"]["liberty"] + 1e-9 for r in vrows)
    ties = [r["others"] for r in vrows if abs(r["voluntary"]["liberty"] - r["compulsory"]["liberty"]) <= 1e-9]
    o["2.V1"] = (not rev and strict >= 8, f"strict {strict}/15, reversed {rev}, ties {ties}")
    nz = sum(r[n]["d"] != 0 for r in vrows for n in ("voluntary", "compulsory"))
    o["2.V2"] = (nz == 0, f"cells with D != 0: {nz}/30")
    sm = sum(r["voluntary"]["liberty"] - r["compulsory"]["liberty"] for r in vrows)
    o["2.V3"] = (sm > 0, f"sum(vol - comp) liberty2 {sm:+.3f} bits; hand-made {hand['voluntary'] - hand['compulsory']:+.2f}")
    S, P = fish["seamed"], fish["patched"]
    later = [1, 2, 3, 4]
    o["3.F1"] = (all(S[m][a]["liberty"] == 0 and S[m][a]["bits"] == 0 for m in later for a in range(4)), "seamed liberty2 and plain all 0")
    gt = sum(P[m][a]["liberty"] > S[m][a]["liberty"] for m in later for a in range(4))
    o["3.F2"] = (gt == 16 and all(P[m][a]["liberty"] > 0 for m in later for a in range(4)), f"patched liberty2 > seamed in {gt}/16")
    sp = lambda f, m: max(f(P[m][a]) for a in range(4)) - min(f(P[m][a]) for a in range(4))  # noqa: E731
    ls = [sp(lambda x: x["liberty"], m) for m in later]
    es = [sp(lambda x: x["bits"], m) for m in later]
    n = sum(l < e - 1e-9 for l, e in zip(ls, es))
    eq = all(abs(fish[nm][m][a]["liberty"] - fish1[nm][m][a]["liberty"]) < 1e-9 for nm in fish for m in MONTHS for a in range(4))
    ado = [fish[nm][m][a]["ado"] for nm in fish for m in MONTHS for a in range(4)]
    o["3.F3"] = (eq and not any(ado), f"v2 == v1 on all 40 agent-months {eq}; fishery ADO nonzero in {sum(x > 0 for x in ado)}/40; F3 itself: spread liberty {[round(x, 3) for x in ls]} vs plain {[round(x, 3) for x in es]}, smaller in {n}/4 ({'PASS' if n >= 3 else 'FAIL'} as expected-to-fail)")
    nzado = [r["others"] for r in vrows if r["voluntary"]["ado"] > 0]
    o["4"] = (len(nzado) >= 8, f"voluntary ADO > 0 in {len(nzado)}/15 compositions; compulsory {sum(r['compulsory']['ado'] > 0 for r in vrows)}/15")
    allr = [x for f in (S, P) for m in f for x in f[m]] + [r[n_] for r in vrows for n_ in ("voluntary", "compulsory")] + [x for v in t.values() for x in v]
    inv = all(x["liberty"] <= x["bits"] + 1e-9 and x["bits_c"] <= x["bits"] + 1e-9 for x in allr)
    o["6"] = (inv and not any(x["open"] for x in allr), f"invariants {inv}; any open {any(x['open'] for x in allr)}")
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="runs/liberty")
    ap.add_argument("--version", type=int, choices=(1, 2), default=2, help="2 = run both versions and judge v2; 1 = v1 only (the old report)")
    a = ap.parse_args()
    ver = a.version
    t1 = toy(1)
    vrows1, hand = vpgg(3, 1)
    fish1 = fishery(2, 1)
    res1 = judge(t1, vrows1, hand, fish1)
    if ver == 1:
        for k_, (ok, d) in res1.items():
            print(f"{k_:4} {'PASS' if ok else 'FAIL'}  {d}")
        return
    t, (vrows, _), fish = toy(2), vpgg(3, 2), fishery(2, 2)
    print("v2 toy", {n: [(round(x["bits"], 3), x["c_all"], x["ado"], x["c"], x["d"], round(x["liberty"], 3)) for x in v] for n, v in t.items()}, "(plain, c_all, ado, c_own, D, liberty) A,B")
    print("\nVPGG others  [vol v1 lib | vol v2: plain c_all ado c_own D lib | comp v1 lib | comp v2: ... ]")
    for r, r1 in zip(vrows, vrows1):
        f = lambda x: f"{x['reachable']:3d} {x['c_all']:3d} {x['ado']:3d} {x['c']:3d} {x['d']:2d} {x['liberty']:.3f}"  # noqa: E731
        print(f"  {r['others']}  {r1['voluntary']['liberty']:.3f} | {f(r['voluntary'])} || {r1['compulsory']['liberty']:.3f} | {f(r['compulsory'])}")
    for name in fish:
        for m in MONTHS:
            print(name, m, "plain", [round(x["bits"], 3) for x in fish[name][m]], "ado", [x["ado"] for x in fish[name][m]], "D", [x["d"] for x in fish[name][m]],
                  "lib2", [round(x["liberty"], 3) for x in fish[name][m]], "lib1", [round(x["liberty"], 3) for x in fish1[name][m]])
    res = judge2(t, vrows, hand, fish, t1, vrows1, fish1)
    print()
    for k_, (ok, d) in res.items():
        print(f"v2 {k_:5} {'PASS' if ok else 'FAIL'}  {d}")
    Path(a.out).mkdir(parents=True, exist_ok=True)
    Path(a.out, "summary_v2.json").write_text(json.dumps({"toy": {"v1": t1, "v2": t}, "vpgg": {"v1": vrows1, "v2": vrows}, "hand": hand,
        "fishery": {"v1": fish1, "v2": fish}, "judge_v2": {k_: {"pass": ok, "detail": d} for k_, (ok, d) in res.items()},
        "judge_v1": {k_: {"pass": ok, "detail": d} for k_, (ok, d) in res1.items()}}, indent=1, default=str))


if __name__ == "__main__":
    main()
