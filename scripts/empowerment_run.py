"""Empowerment vs the hand-made freedom score, judged against docs/results/empowerment-prereg.md.

  uv run python scripts/empowerment_run.py [--out runs/empowerment]

Deterministic (no seeds, no model calls). Writes summary.json and prints the prediction table.
Thresholds are copied from the committed prereg; do not tune them.
"""
import argparse
import itertools
import json
from pathlib import Path

from mar import empowerment as E
from mar.cards import load_cards
from mar.fishery import run_fishery
from mar.gate import Gate
from mar.games import vpgg as V
from mar.mocks import Compliant, Exploiter
from mar.patcher import propose_patch

ROOT = Path(__file__).parent.parent
K = 3
ROLES = ["exploiter", "exploiter", "compliant", "compliant"]
MONTHS = range(0, 5)
SUBROUNDS = 12


def mocks():
    return [Exploiter(), Exploiter(), Compliant(), Compliant()]


def vpgg_part():
    w = E.VPGGWorld()
    gates = {n: V.VPGate(V.load_regime(n, str(ROOT / "rules" / "vpgg"))) for n in ("voluntary", "compulsory")}
    rows = []
    for comp in itertools.combinations_with_replacement("CDL", 4):
        pol = lambda s, i, comp=comp: comp[i - 1]  # noqa: E731
        r = {n: E.empowerment(w, g, w.initial(), 0, K, pol) for n, g in gates.items()}
        rows.append({"others": "".join(comp), "vol": r["voluntary"]["reachable"], "comp": r["compulsory"]["reachable"],
                     "vol_bits": r["voluntary"]["bits"], "comp_bits": r["compulsory"]["bits"],
                     "open": r["voluntary"]["bound_hit"] or r["compulsory"]["bound_hit"]})
    hand = {n: E.vpgg_hand_freedom(g) for n, g in gates.items()}
    return rows, hand


def fishery_part():
    seamed_cards = load_cards(ROOT / "rules" / "fishery")
    seamed = Gate(seamed_cards)
    failing = run_fishery(mocks(), seamed, seed=0)
    patch = propose_patch(failing.trace, seamed_cards)
    specs = {"seamed": seamed, "patched": Gate(seamed_cards + patch)}
    w = E.FisheryWorld(n_agents=4)
    pol = E.mock_policy(mocks())
    out = {}
    for name, spec in specs.items():
        traj = E.rollout(w, spec, pol)
        res = {"month_start": {}, "month0": [], "pool_end": [traj[SUBROUNDS * (m + 1)].pool for m in range(6)]}
        for m in MONTHS:
            s = traj[SUBROUNDS * m]
            res["month_start"][m] = [{**E.empowerment(w, spec, s, a, K, pol), "opt": E.option_fraction(w, spec, s)}
                                     for a in range(4)]
        for t in range(SUBROUNDS):
            s = traj[t]
            res["month0"].append([E.empowerment(w, spec, s, a, K, pol) for a in range(4)])
        res["series"] = [[res["month_start"][m][a]["bits"] for a in range(4)] for m in MONTHS]
        res["psi"] = [E.power_seeking_index(res["series"], a) for a in range(4)]
        res["collective"] = [E.collective_empowerment(row) for row in res["series"]]
        out[name] = res
    return out, [c.id for c in patch]


def judge(vrows, hand, fish):
    out = {}
    strict = sum(r["vol"] > r["comp"] for r in vrows)
    worse = [r["others"] for r in vrows if r["vol"] < r["comp"]]
    ties = [r["others"] for r in vrows if r["vol"] == r["comp"]]
    mean_diff = sum(r["vol_bits"] - r["comp_bits"] for r in vrows) / len(vrows)
    out["1"] = (not worse and strict >= 13 and mean_diff >= 0.5,
                f"strict {strict}/15, ties {ties}, compulsory higher in {worse}, mean diff {mean_diff:.3f} bits (need strict >= 13, none worse, mean >= 0.5)")
    S, P = fish["seamed"]["month_start"], fish["patched"]["month_start"]
    later = [1, 2, 3, 4]
    b = lambda d, m, a: d[m][a]["bits"]  # noqa: E731
    c_ok = all(b(P, m, a) > b(S, m, a) for m in later for a in (2, 3))
    c_min = min(b(P, m, a) for m in later for a in (2, 3))
    c_seam = max(b(S, m, a) for m in later for a in (2, 3))
    out["2b"] = (c_ok and c_seam == 0.0 and c_min >= 3.0,
                 f"compliant patched min {c_min:.3f} bits, seamed max {c_seam:.3f} (need patched > seamed, seamed 0, patched >= 3.0)")
    e_ok = all(b(P, m, a) < b(S, m, a) for m in later for a in (0, 1))
    out["2a"] = (e_ok, f"exploiter patched bits by month {[[round(b(P, m, a), 3) for a in (0, 1)] for m in later]} vs seamed "
                       f"{[[round(b(S, m, a), 3) for a in (0, 1)] for m in later]}; patched < seamed in every cell: {e_ok} (predicted fail)")
    mean0 = lambda d, a: sum(r[a]["bits"] for r in d["month0"]) / SUBROUNDS  # noqa: E731
    d0 = [mean0(fish["seamed"], a) - mean0(fish["patched"], a) for a in (0, 1)]
    out["2a'"] = (all(x >= 0.3 for x in d0), f"month-0 mean12 bits exploiters seamed minus patched {[round(x, 3) for x in d0]} (need >= 0.3 each)")
    # 3: agreement
    vd_emp = sum(r["vol_bits"] for r in vrows) - sum(r["comp_bits"] for r in vrows)
    vd_hand = hand["voluntary"] - hand["compulsory"]
    out["3a"] = (vd_emp * vd_hand > 0, f"hand-made voluntary minus compulsory {vd_hand:+.2f}; empowerment sum over compositions {vd_emp:+.3f} bits")
    agree = {}
    for a in range(4):
        de = sum(b(P, m, a) - b(S, m, a) for m in later)
        dh = sum(P[m][a]["opt"] - S[m][a]["opt"] for m in later)
        agree[a] = (ROLES[a], round(de, 3), round(dh, 3), "agree" if de * dh > 0 else ("uninformative" if de == 0 or dh == 0 else "DISAGREE"))
    out["3b"] = (all(v[3] == "agree" for v in agree.values()), f"(role, d bits, d option fraction, verdict) per agent, patched minus seamed, months 1-4: {agree}")
    seats = [(round(b(P, m, 0), 3), round(b(P, m, 3), 3), round(P[m][0]["opt"], 3), round(P[m][3]["opt"], 3)) for m in later]
    n_more = sum(b(P, m, 0) > b(P, m, 3) for m in later)
    same_opt = all(P[m][0]["opt"] == P[m][3]["opt"] for m in later)
    out["3c"] = (n_more >= 3 and same_opt, f"patched, month start: (E0 bits, C3 bits, E0 opt, C3 opt) {seats}; E0 > C3 in {n_more}/4 months; options equal {same_opt}")
    # 4
    sp = fish["seamed"]["psi"]
    pp = fish["patched"]["psi"]
    ok4 = all(r["gain"] <= 0 for r in sp) and not any(r["power_seeking"] for r in sp + pp) and all(abs(r["psi"]) <= 1.0 for r in sp)
    out["4"] = (ok4, f"seamed psi {[round(r['psi'], 3) for r in sp]} gains {[round(r['gain'], 3) for r in sp]}; patched psi {[round(r['psi'], 3) for r in pp]} "
                     f"flags seamed {[r['power_seeking'] for r in sp]} patched {[r['power_seeking'] for r in pp]}")
    allres = [vrows] + [fish[n]["month_start"][m] for n in fish for m in MONTHS]
    hit = any(r["open"] for r in vrows) or any(x["bound_hit"] for n in fish for m in MONTHS for x in fish[n]["month_start"][m]) \
        or any(x["bound_hit"] for n in fish for row in fish[n]["month0"] for x in row)
    mx = max(x["expanded"] for n in fish for m in MONTHS for x in fish[n]["month_start"][m])
    out["5"] = (not hit, f"any bound_hit: {hit}; largest fishery expansion count {mx}")
    return out, agree


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="runs/empowerment")
    a = ap.parse_args()
    vrows, hand = vpgg_part()
    fish, patch_ids = fishery_part()
    res, agree = judge(vrows, hand, fish)
    print(f"k={K} rounds; patch {patch_ids}\n")
    print("VPGG others  vol  comp  (reachable, k=3)")
    for r in vrows:
        print(f"  {r['others']}   {r['vol']:4d} {r['comp']:5d}   bits {r['vol_bits']:.3f} vs {r['comp_bits']:.3f}")
    print(f"hand-made freedom {hand}\n")
    for name in fish:
        print(name, "pool_end", fish[name]["pool_end"])
        for m in MONTHS:
            print(f"  month {m} start bits", [round(x["bits"], 3) for x in fish[name]["month_start"][m]],
                  "reach", [x["reachable"] for x in fish[name]["month_start"][m]],
                  "opt", [round(x["opt"], 3) for x in fish[name]["month_start"][m]])
        print("  month0 mean12", [round(sum(r[i]["bits"] for r in fish[name]["month0"]) / SUBROUNDS, 3) for i in range(4)])
        print("  psi", [round(r["psi"], 3) for r in fish[name]["psi"]], "collective", [{k: round(v, 2) for k, v in c.items()} for c in fish[name]["collective"]])
    print()
    for k, (ok, d) in res.items():
        print(f"{k:4} {'PASS' if ok else 'FAIL'}  {d}")
    Path(a.out).mkdir(parents=True, exist_ok=True)
    Path(a.out, "summary.json").write_text(json.dumps({"vpgg": vrows, "hand": hand, "fishery": fish,
        "judge": {k: {"pass": ok, "detail": d} for k, (ok, d) in res.items()}}, indent=1, default=str))


if __name__ == "__main__":
    main()
