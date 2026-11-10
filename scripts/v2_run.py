"""V2: instrument calibration with scripted mock agents. Prints a pass/fail table."""
import itertools
import time
from pathlib import Path

from mar.cards import load_cards, make_card
from mar.gate import Gate
from mar.fishery import run_fishery
from mar.mocks import Compliant, Exploiter, Explorer
from mar.patcher import propose_patch
from mar.patch_check import check_patch
from mar.miner import mine, diff
from mar import oracle

RULES = Path(__file__).parent.parent / "rules" / "fishery"
N, SEEDS = 4, range(50)


def reference(pool, mt, catch, month_cap=None):
    """Independent plain-Python statement of the written spec."""
    ok = 0 <= catch <= 10 and catch <= pool
    if month_cap is not None and catch > 0:
        ok = ok and mt + catch <= month_cap
    return ok


def check1_gate(seamed, patched):
    mism, total = 0, 0
    for cards, cap in ((seamed, None), (patched, 40)):
        g = Gate(cards)
        for pool, mt, catch in itertools.product(range(0, 13), range(0, 13), range(-2, 15)):
            total += 1
            mism += g.check_action({"pool": pool, "month_total": mt}, {"catch": catch})[0] != reference(pool, mt, catch, cap)
        for pool, mt, catch in [(100, 0, 10), (100, 35, 6), (100, 35, 5), (60, 40, 0), (60, 40, 1)]:
            total += 1
            mism += g.check_action({"pool": pool, "month_total": mt}, {"catch": catch})[0] != reference(pool, mt, catch, cap)
    return mism == 0, f"{total} grid points, {mism} mismatches vs plain-Python reference"


def check2_seam(seamed):
    run = run_fishery([Exploiter() for _ in range(N)], Gate(seamed), seed=0)
    v = oracle.judge(run.outcomes)
    good = run_fishery([Compliant() for _ in range(N)], Gate(seamed), seed=0)
    ok = oracle.is_seam(run.trace, run.outcomes) and oracle.judge(good.outcomes)["ok"]
    kinds = [(f["kind"], f["month"]) for f in v["findings"]]
    return ok, f"exploiter findings {kinds}; compliant oracle ok={oracle.judge(good.outcomes)['ok']}", run


def conflicting():
    return make_card({"id": "C1", "attribute": "fisher", "deontic": "must", "aim": "harvest",
                      "conditions": [{"expr": "catch", "op": "ge", "value": 20}], "or_else": None,
                      "gloss": "Every fisher must take at least 20 fish per harvest action.",
                      "source": "V2 fixture (deliberately conflicting patch)"})


def check3_patch(seamed, failing_run):
    patch = propose_patch(failing_run.trace, seamed)
    rep = check_patch(seamed, patch)
    rerun = run_fishery([Exploiter() for _ in range(N)], Gate(seamed + patch), seed=0)
    closed = oracle.judge(rerun.outcomes)["ok"]
    bad = check_patch(seamed, [conflicting()])
    rejected = not bad["accepted"]
    named = sorted({i for v in bad["verdicts"] if v["verdict"] == "fail" for i in v["cards"]})
    ok = rep["accepted"] and closed and rejected and {"C1", "F1"} <= set(named)
    verdicts = {v["check"]: v["verdict"] for v in rep["verdicts"]}
    return ok, (f"patch {rep['patch_ids']} checks {verdicts}; seam closed={closed}; "
                f"conflicting patch rejected={rejected}, ids {named}; bound: {rep['bound']}"), patch, bad


def explore(cards):
    rows = []
    for s in SEEDS:
        rows += run_fishery([Explorer() for _ in range(N)], Gate(cards), seed=s).trace
    return mine(rows)


def check4_mining(seamed, patched):
    parts, ok = [], True
    for name, cards in (("seamed", seamed), ("patched", patched)):
        m = explore(cards)
        d = diff(cards, m)
        ok &= d["bounds_equal"] and not d["edges_mined_not_jure"]
        b = {r["bound"]: (r["written"], r["mined"]) for r in d["bounds"]}
        parts.append(f"{name}: written/mined {b}; edges mined={d['n_mined']} jure={d['n_jure']} "
                     f"mined-not-jure={len(d['edges_mined_not_jure'])} jure-not-mined={len(d['edges_jure_not_mined'])}")
    return ok, " | ".join(parts)


def main():
    t0 = time.time()
    seamed = load_cards(RULES)
    ok2, d2, failing = check2_seam(seamed)
    ok3, d3, patch, _ = check3_patch(seamed, failing)
    patched = seamed + patch
    rows = [("1 gate correctness", *check1_gate(seamed, patched)),
            ("2 oracle flags planted seam", ok2, d2),
            ("3 patch closes seam; conflicting rejected", ok3, d3),
            ("4 mined rules equal written", *check4_mining(seamed, patched))]
    print(f"{'check':45} result  detail")
    for name, ok, detail in rows:
        print(f"{name:45} {'PASS' if ok else 'FAIL':6}  {detail}")
    print(f"\nscripted patch card:\n{patch[0].to_yaml() if patch else '(none)'}")
    print(f"wall time {time.time() - t0:.1f}s")
    raise SystemExit(0 if all(r[1] for r in rows) else 1)


if __name__ == "__main__":
    main()
