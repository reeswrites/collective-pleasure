"""V2b: English-like surface over ADICO cards. Prints a pass/fail table and example stories."""
import itertools
import time
from pathlib import Path

from mar.cards import load_cards, make_card
from mar.english import (render, parse, parse_all, load_english, explain, FORBIDDEN_IN_STORIES)
from mar.fishery import run_fishery
from mar.gate import Gate
from mar.mocks import Exploiter
from mar.patch_check import check_patch
from mar.patcher import propose_patch

ROOT = Path(__file__).parent.parent
YAML, EN = ROOT / "rules" / "fishery", ROOT / "rules" / "fishery-en"
N = 4


def conflicting():
    return make_card({"id": "C1", "attribute": "fisher", "deontic": "must", "aim": "harvest",
                      "conditions": [{"expr": "catch", "op": "ge", "value": 20}], "or_else": None,
                      "gloss": "Every fisher must take at least 20 fish per harvest action.",
                      "source": "V2 fixture (deliberately conflicting patch)"})


def naive_cap():
    """The V2 first-run failure: month cap written without `catch > 0` (deadlocks)."""
    return make_card({"id": "N1", "attribute": "fisher", "deontic": "must_not", "aim": "harvest",
                      "conditions": [{"expr": "month_total + catch", "op": "gt", "value": 40}],
                      "or_else": {"kind": "suspend", "duration_months": 1, "sanctioner": "monitor"},
                      "gloss": "Together, fishers may take no more than 40 fish in one month.",
                      "source": "V2 fixture (naive patch, first-run failure)"})


def grid():
    pts = [(p, m, c) for p, m, c in itertools.product(range(0, 13), range(0, 13), range(-2, 15))]
    return pts + [(100, 0, 10), (100, 35, 6), (100, 35, 5), (60, 40, 0), (60, 40, 1)]


def check1(cards):
    bad = [c.id for c in cards if parse(render(c)) != c]
    return not bad, f"{len(cards) - len(bad)} of {len(cards)} cards round trip exactly; failures {bad}"


def check2(seamed, patched, seamed_en, patched_en):
    mism, total = 0, 0
    for a, b in ((seamed, seamed_en), (patched, patched_en)):
        ga, gb = Gate(a), Gate(b)
        for p, m, c in grid():
            total += 1
            mism += ga.check_action({"pool": p, "month_total": m}, {"catch": c}) != \
                gb.check_action({"pool": p, "month_total": m}, {"catch": c})
    return mism == 0, f"{total} grid points (both specs), {mism} mismatches (allowed flag and reason ids)"


def key(report):
    return [(v["check"], v["verdict"], v["cards"]) for v in report["verdicts"]]


def check3(seamed, seamed_en, p1_en, c1_en):
    yaml_bad = check_patch(seamed, [conflicting()])
    en_bad = check_patch(seamed_en, c1_en)
    en_good = check_patch(seamed_en, p1_en)
    failed = {v["check"]: v["cards"] for v in en_bad["verdicts"] if v["verdict"] == "fail"}
    same = key(yaml_bad) == key(en_bad)
    ok = same and not en_bad["accepted"] and {"C1", "F1", "F2"} <= set(failed.get("a_no_conflict", [])) \
        and "b_no_deadlock" in failed and en_good["accepted"]
    return ok, (f"English-authored C1 set fails {failed}; identical to YAML-authored verdicts: {same}; "
                f"English P1 accepted: {en_good['accepted']}; bound: {en_bad['bound']}")


def stories(seamed, patch):
    out, ids = {}, {}
    cm = {c.id: c for c in seamed}
    run = run_fishery([Exploiter() for _ in range(N)], Gate(seamed), seed=0)
    out["seam trace (exploiters, seamed spec)"] = explain(run, seamed)
    run2 = run_fishery([Exploiter() for _ in range(N)], Gate(seamed + patch), seed=0)
    out["exploiters under seamed + P1"] = explain(run2, seamed + patch)
    for label, extra in (("C1", [conflicting()]), ("N1 (naive cap)", [naive_cap()])):
        cards = seamed + extra
        rep = check_patch(seamed, extra)
        for v in rep["verdicts"]:
            if v["verdict"] == "fail":
                out[f"{label}: {v['check']}"] = explain(v, cards)
                ids[f"{label}: {v['check']}"] = v["cards"]
    return out, ids


def check4(story_map, failing_ids):
    bad, notes = [], []
    for name, s in story_map.items():
        leaks = [t for t in FORBIDDEN_IN_STORIES if t in s]
        if leaks:
            bad.append(f"{name}: code tokens {leaks}")
        if name.startswith("seam trace") and not ("seam" in s and "collapses" in s and "passed the gate" in s):
            bad.append(f"{name}: missing oracle finding or seam statement")
        if name.startswith(("C1", "N1")):
            fail_ids = failing_ids.get(name, [])
            if not fail_ids or not all(i in s for i in fail_ids):
                bad.append(f"{name}: failing card ids {fail_ids} not all named")
    return not bad, f"{len(story_map)} stories; problems {bad}"


def main():
    t0 = time.time()
    seamed = load_cards(YAML)
    seamed_en = load_english(EN)
    p1_en = parse_all((EN / "patch" / "P1.txt").read_text())
    c1_en = parse_all((EN / "patch" / "C1.txt").read_text())
    trace = run_fishery([Exploiter() for _ in range(N)], Gate(seamed), seed=0).trace
    patch = propose_patch(trace, seamed)
    cards6 = seamed + patch + [conflicting()]
    story_map, failing_ids = stories(seamed, patch)
    rows = [("1 round trip, all V2 cards", *check1(cards6)),
            ("2 gate agrees on full V2 grid", *check2(seamed, seamed + patch, seamed_en, seamed_en + p1_en)),
            ("3 conflict still caught (English)", *check3(seamed, seamed_en, p1_en, c1_en)),
            ("4 stories pass mechanical test", *check4(story_map, failing_ids))]
    print(f"{'check':36} result  detail")
    for name, ok, detail in rows:
        print(f"{name:36} {'PASS' if ok else 'FAIL':6}  {detail}")
    print("\n-- rendered rules --")
    for c in cards6:
        print(render(c))
    for name, s in story_map.items():
        print(f"\n-- story: {name} --\n{s}")
    print(f"\nwall time {time.time() - t0:.1f}s")
    raise SystemExit(0 if all(r[1] for r in rows) else 1)


if __name__ == "__main__":
    main()
