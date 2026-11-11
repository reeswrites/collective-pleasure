"""H01: when exit is free, does a controlling persona who presses lower its own lifetime pleasure, compared with the same persona playing
cooperatively? Prereg: docs/results/h01-prereg.md. Results: docs/results/h01.md. Scripted agents, no model calls, $0.

  uv run python scripts/h01_control_run.py --pilot      # EXPLORATORY: seeds 1000..1002, free_exit and no_exit only; prints effect and spread for the power check
  uv run python scripts/h01_control_run.py --run        # the confirmatory run (seeds 0..N-1), writes runs/h01/results.json
  uv run python scripts/h01_control_run.py --analyze    # re-print every number from runs/h01/results.json

Matched twins: the same pairing (a pressing persona as focal member with one of the six non-pressing personas, both seat orders), the same seed and the
same rules; the focal member plays its pressing script (`press=True`) or the same persona with the pressing candidates removed (`press=False`, the
cooperative policy; the partner is unchanged in both). Measure: the focal member's lifetime pleasure = the sum over the 156 weeks of its weekly
`pleasure` from the hedonic model with the pleasure levers OFF (the present-weighted special case of ADR 0017; no memory or anticipation term).
Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.
"""
import argparse
import json
import sys
from itertools import product
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from mar import stats as S  # noqa: E402
from mar.cards import make_card  # noqa: E402
from mar.worlds import household as H  # noqa: E402
import household_run as HR  # noqa: E402  (a script module: its work is behind __main__ guards)

OUT = ROOT / "runs" / "h01"
PRESSERS = HR.PRESSING_IDS                                   # controller, freerider, overasker
RULESETS = ("author_seed_v2_free_exit", "baseline", "no_exit")
SEEDS = tuple(range(10))                                     # set by the power check in the prereg
PILOT_SEEDS = (1000, 1001, 1002)                             # EXPLORATORY, never used in the confirmatory data
LOADS = (0.2, 0.3, 0.4)                                      # exploratory sweep of the partner's non-offsettable leave load (0.2 is the world's)
ALPHA = 0.05
P1_MARGIN = 0.02 * H.WEEKS                                   # at least 0.02 mean weekly pleasure lower = 3.12 pleasure-weeks over 156 weeks (set before the confirmatory run)

NO_EXIT_CARD = {"id": "H01-no-exit", "attribute": "partner", "deontic": "must_not", "aim": "leave", "conditions": [], "or_else": None,
                "gloss": "A partner may never leave.",
                "source": "H01 control (docs/results/h01-prereg.md): the free_exit cards plus one unconditional hard prohibition on leaving, so that pressing cannot make the partner leave."}


def cards_for(ruleset):
    if ruleset == "no_exit":
        return H.load_variant("author_seed_v2_free_exit") + [make_card(NO_EXIT_CARD)]
    return H.load_variant(ruleset)


def pairings():
    """(focal persona, partner persona, focal role): 3 pressers x 6 non-pressers x 2 seatings = 36."""
    ps = HR._personas()
    others = sorted(i for i in ps if i not in PRESSERS)
    return [(f, o, role) for f, o, role in product(PRESSERS, others, "AB")]


def _with_load(agent, load):
    """Exploratory: the partner leaves on a non-offsettable load of at least `load` instead of 0.2: a leave candidate that exists only because
    h.N >= 0.2 (no 4 low weeks, trust fine) is dropped while h.N < load. The world's own leave rule is untouched at load 0.2."""
    orig = agent.propose

    def propose(o):
        out = orig(o)
        if o["in_hh"] and o["low_weeks"] < 4 and o.get("trust", 1.0) >= H.TRUST["leave_below"] and o["hed"].N < load:
            out = [(u, c) for u, c in out if c["a"] != "leave"]
        return out
    agent.propose = propose


def run_one(ruleset, focal, partner, role, seed, press, load=0.2, cards=None):
    ps = HR._personas()
    pa, pb = (ps[focal], ps[partner]) if role == "A" else (ps[partner], ps[focal])
    w = H.WeeklyWorld(cards if cards is not None else cards_for(ruleset), (pa, pb), seed)
    w.agents[role].press = press
    if load != 0.2:
        for r in "AB":
            _with_load(w.agents[r], load)
    run = w.play()
    out = run.outcomes
    other = "B" if role == "A" else "A"
    hr = lambda r, k: sum(o["hedonic"][r][k] for o in out)
    left = {r: not out[-1]["partners"][r]["in"] for r in "AB"}
    leave_week = {r: next((t["week"] for t in run.trace if t["role"] == r and t["action"] == "leave" and t["executed"]), None) for r in "AB"}
    return {"ruleset": ruleset, "focal": focal, "partner": partner, "role": role, "seed": seed, "press": press, "load": load,
            "pleasure": hr(role, "pleasure"), "wellbeing": hr(role, "pleasure") - hr(role, "s_off") - hr(role, "s_non"),
            "partner_pleasure": hr(other, "pleasure"), "partner_left": left[other], "focal_left": left[role],
            "partner_leave_week": leave_week[other], "focal_leave_week": leave_week[role],
            "dissolved": any(left.values())}


def _task(a):
    return run_one(*a)


def tasks(rulesets, seeds, loads=(0.2,)):
    return [(rs, f, o, role, sd, press, ld) for rs in rulesets for (f, o, role) in pairings() for sd in seeds for press in (True, False) for ld in loads]


def run_all(rulesets, seeds, loads=(0.2,), workers=8):
    ts = tasks(rulesets, seeds, loads)
    with Pool(workers) as pool:
        return pool.map(_task, ts, chunksize=8)


def pairing_table(rows, ruleset, load=0.2, key="pleasure"):
    """{pairing: (mean over seeds of the pressing twin, mean of the cooperative twin)} for one rule set. The pairing (focal, partner, role) is the unit."""
    by = {}
    for r in rows:
        if r["ruleset"] == ruleset and r["load"] == load:
            by.setdefault((r["focal"], r["partner"], r["role"]), {True: [], False: []})[r["press"]].append(r[key])
    return {k: (sum(v[True]) / len(v[True]), sum(v[False]) / len(v[False])) for k, v in by.items() if v[True] and v[False]}


def gaps(rows, ruleset, load=0.2, key="pleasure"):
    """-> (keys, array of gap = pressing minus cooperative per pairing)."""
    t = pairing_table(rows, ruleset, load, key)
    ks = sorted(t)
    return ks, [t[k][0] - t[k][1] for k in ks]


def _m(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def analyze(rows, out=print, confirmatory=True):
    def pr(*a):
        out(" ".join(str(x) for x in a))
    res = {}
    n_seeds = len({r["seed"] for r in rows})
    pr(f"== {len(rows)} runs, {n_seeds} seeds, {len(pairings())} pairings, rule sets {sorted({r['ruleset'] for r in rows})}")
    for rs in RULESETS:
        sub = [r for r in rows if r["ruleset"] == rs and r["load"] == 0.2]
        if not sub:
            continue
        ks, g = gaps(rows, rs)
        pt = pairing_table(rows, rs)
        pre, coop = _m(v[0] for v in pt.values()), _m(v[1] for v in pt.values())
        pl = S.permutation_test(g, [0.0] * len(g), paired=True, alternative="less")
        ci = S.mean_difference([v[0] for v in pt.values()], [v[1] for v in pt.values()], paired=True)
        dz = S.cohens_d([v[0] for v in pt.values()], [v[1] for v in pt.values()], paired=True)
        cd = S.cliffs_delta([v[0] for v in pt.values()], [v[1] for v in pt.values()])
        left_p = _m(r["partner_left"] for r in sub if r["press"])
        left_c = _m(r["partner_left"] for r in sub if not r["press"])
        diss_p = _m(r["dissolved"] for r in sub if r["press"])
        diss_c = _m(r["dissolved"] for r in sub if not r["press"])
        pr(f"== {rs}: lifetime pleasure (sum of 156 weekly values), pressing {pre:.2f} vs cooperative {coop:.2f}; gap (press - coop) {ci} over {len(g)} pairings;"
           f" paired permutation one-sided (press < coop) p = {pl.p:.4g}; d_z {dz:.2f}; Cliff's delta {cd:.2f}")
        pr(f"   partner left by week 156: pressing {left_p:.3f} vs cooperative {left_c:.3f}; household dissolved: {diss_p:.3f} vs {diss_c:.3f}; focal left: "
           f"{_m(r['focal_left'] for r in sub if r['press']):.3f} vs {_m(r['focal_left'] for r in sub if not r['press']):.3f}")
        _, gw = gaps(rows, rs, key="wellbeing")
        pr(f"   wellbeing (pleasure less suffering, summed) gap: {_m(gw):+.2f}; partner's lifetime pleasure, press - coop: "
           f"{_m(r['partner_pleasure'] for r in sub if r['press']) - _m(r['partner_pleasure'] for r in sub if not r['press']):+.2f}")
        by = {}
        for (f, o, role), gg in zip(ks, g):
            by.setdefault(f, []).append(gg)
        pr("   gap by focal persona (descriptive):", {f[2:]: round(_m(v), 2) for f, v in by.items()})
        res[rs] = {"gap": ci, "p": pl.p, "dz": dz, "cliff": cd, "g": g, "keys": ks, "pre": pre, "coop": coop, "partner_left": (left_p, left_c)}
    if "author_seed_v2_free_exit" in res and "baseline" in res and "no_exit" in res:
        ks = res["no_exit"]["keys"]
        d = [a - b for a, b in zip(res["no_exit"]["g"], res["author_seed_v2_free_exit"]["g"])]
        p3 = S.permutation_test(d, [0.0] * len(d), paired=True, alternative="greater")
        ci3 = S.mean_difference(res["no_exit"]["g"], res["author_seed_v2_free_exit"]["g"], paired=True)
        ph = S.holm([res["author_seed_v2_free_exit"]["p"], res["baseline"]["p"], p3.p])
        r1, r2 = res["author_seed_v2_free_exit"], res["baseline"]
        hold1 = ph[0] < ALPHA and r1["gap"].hi < 0 and r1["gap"].estimate <= -P1_MARGIN
        hold2 = ph[1] < ALPHA and r2["gap"].hi < 0 and r2["gap"].estimate <= -P1_MARGIN
        hold3 = ph[2] < ALPHA and ci3.lo > 0
        pr(f"== P1 free_exit gap {r1['gap']} (needs estimate <= {-P1_MARGIN:.2f} and upper bound < 0), Holm p = {ph[0]:.4g}: holds = {hold1}")
        pr(f"== P2 baseline gap {r2['gap']}, Holm p = {ph[1]:.4g}: holds = {hold2}")
        pr(f"== P3 contrast, gap(no_exit) - gap(free_exit) {ci3} (needs lower bound > 0), one-sided permutation p = {p3.p:.4g}, Holm {ph[2]:.4g}: holds = {hold3}")
        verdict = hold1 and hold2 and hold3
        pr(f"== VERDICT ({'confirmatory' if confirmatory else 'EXPLORATORY, no verdict'}): H01 supported = {verdict}")
        res.update({"p1": hold1, "p2": hold2, "p3": hold3, "ci3": ci3, "holm": ph, "supported": verdict})
    # exploratory sweep of the leave load
    loads = sorted({r["load"] for r in rows})
    if len(loads) > 1:
        for ld in loads:
            sub = [r for r in rows if r["load"] == ld and r["ruleset"] == "author_seed_v2_free_exit"]
            ks, g = gaps(rows, "author_seed_v2_free_exit", ld)
            ci = S.mean_difference([v[0] for v in pairing_table(rows, "author_seed_v2_free_exit", ld).values()],
                                   [v[1] for v in pairing_table(rows, "author_seed_v2_free_exit", ld).values()], paired=True)
            pr(f"== EXPLORATORY leave load {ld}: gap {ci}; partner left press {_m(r['partner_left'] for r in sub if r['press']):.3f} vs coop "
               f"{_m(r['partner_left'] for r in sub if not r['press']):.3f}")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--sweep", action="store_true", help="exploratory leave-load sweep (free_exit only, confirmatory seeds)")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--seeds", type=int, default=len(SEEDS))
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.pilot:
        rows = run_all(("author_seed_v2_free_exit", "no_exit"), PILOT_SEEDS)
        (out / "pilot.json").write_text(json.dumps(rows))
        analyze(rows, confirmatory=False)
        return 0
    if a.run:
        rows = run_all(RULESETS, tuple(range(a.seeds)))
        (out / "results.json").write_text(json.dumps(rows))
        analyze(rows)
        return 0
    if a.sweep:
        rows = run_all(("author_seed_v2_free_exit",), tuple(range(a.seeds)), LOADS)
        (out / "sweep.json").write_text(json.dumps(rows))
        analyze(rows, confirmatory=False)
        return 0
    if a.analyze:
        analyze(json.loads((out / "results.json").read_text()))
        return 0
    ap.error("give --pilot, --run, --sweep or --analyze")


if __name__ == "__main__":
    sys.exit(main())
