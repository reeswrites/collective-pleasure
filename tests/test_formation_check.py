"""H38 formation check (docs/results/h38-formation-check-prereg.md): the decision-yardstick flag is off by default and reproduces H38's
runs exactly; on, agents decide to form and stay on their own clipped pleasure over 52-week rollouts. Numbers are ASSUMED; these tests
check mechanisms, not the numbers' truth."""
import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import h38_pairing_run as H38  # noqa: E402
from mar import exit_fallback as EF  # noqa: E402
from mar import exit_items as EI  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import multiverse as MV  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar.worlds import household as H  # noqa: E402

# Four H38 confirmatory rows (runs/h38-pairing/rows.jsonl), copied BEFORE the flag existed.
PINNED = json.loads((Path(__file__).parent / "data" / "h38_formation_off_rows.json").read_text())
GOOD = {"decide_on": "pleasure", "decide_weeks": 52}


def test_default_is_the_old_rule():
    f = HD.FixConfig()
    assert (f.decide_on, f.decide_weeks) == ("net", 0)
    assert not HD.fixes_on(f)
    assert HD.fixes_on(HD.FixConfig(**GOOD))


def test_flag_off_reproduces_h38_rows_exactly():
    for o in PINNED:
        run, lived, rd = H38.play(H38.ARMS[o["arm"]], o["a"], o["b"], o["seed"])
        rec = json.loads(json.dumps(H38.record(run, lived, rd, o["arm"], o["a"], o["b"], o["seed"])))
        assert rec == o, (o["arm"], o["a"], o["b"], o["seed"])


def test_multiverse_defaults_are_untouched():
    assert MV._get_default(NG.alone_value, "weeks") == NG.OUT_WEEKS == 26
    assert MV._get_default(NG.pot_baseline, "weeks") == 26
    assert MV._get_default(NG.baseline_value, "weeks") == 26
    assert MV._get_default(NG.forward_values, "weeks") == NG.FORWARD_WEEKS == 26


def _rows():
    return [{"hedonic": {"A": {"pleasure": 0.9, "s_off": 0.2, "s_non": 0.1}}}, {"hedonic": {"A": {"pleasure": 0.5, "s_off": 0.0, "s_non": 0.0}}}]


def test_wellbeing_is_net_by_default_and_own_pleasure_under_the_flag():
    with HD.use_fixes(RT.FIXES_ON):
        assert abs(NG.wellbeing(_rows(), "A") - 0.55) < 1e-12
    with HD.use_fixes(dataclasses.replace(RT.FIXES_ON, **GOOD)):
        assert abs(NG.wellbeing(_rows(), "A") - 0.70) < 1e-12


def test_decide_weeks():
    assert NG.decide_weeks(26) == 26
    with HD.use_fixes(RT.FIXES_ON):
        assert NG.decide_weeks(26) == 26 and NG.decide_weeks(0) == 0
    with HD.use_fixes(dataclasses.replace(RT.FIXES_ON, **GOOD)):
        assert NG.decide_weeks(26) == 52 and NG.decide_weeks(0) == 52


def _ctx(rule):
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **rule)
    return HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[H38.CELL])


def test_every_decision_rollout_uses_the_flag_window():
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    a, b, c_, d = _ctx(GOOD)
    with a, b, c_, d:
        NG.outside_value(ps["p-anchor"], "A", 55, 0)
        NG.baseline_value(ps["p-anchor"], ps["p-host"], 0, H.load_variant("baseline"))
    assert {k[5] for k in NG._RC} == {52}
    assert {k[3] for k in NG._BC} == {52}
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()


def test_forward_and_stay_rollouts_use_the_flag_window():
    ps = RT.personas()
    a, b, c_, d = _ctx(GOOD)
    with a, b, c_, d:
        w = H.WeeklyWorld(H.load_variant("baseline"), (ps["p-anchor"], ps["p-host"]), 0, 60)
        n0 = NG.STATS["rollout_weeks"]
        NG.forward_values(w, 0, {"busy": {"A": False, "B": False}})
        assert NG.STATS["rollout_weeks"] - n0 == 52


def test_exit_anticipation_spreads_over_the_flag_window():
    ps = RT.personas()
    for rule, n in (({}, 26), (GOOD, 52)):
        fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(4, parts=("exit",)), **rule)
        with HD.use_fixes(fx):
            w = H.WeeklyWorld(H.load_variant("baseline"), (ps["p-anchor"], ps["p-host"]), 0, 20, fixes=fx, levers=RT.LEVERS)
            assert abs(PR.exit_anticipation(w) - 0.08 * 26 / n) < 1e-12


def test_flag_changes_some_formation_decisions():
    """On the H38 pairings, the corrected rule forms some pair-seed the old rule declines (the diagnosis's mechanism)."""
    ps = RT.personas()
    changed = 0
    for a, b in H38.pairings(H38.CONFIRM)[:12]:
        calls = []
        for rule in ({}, GOOD):
            for c in (NG._RC, NG._PC, NG._BC):
                c.clear()
            x = _ctx(rule)
            with x[0], x[1], x[2], x[3]:
                lv = NG.BaselineLived(ps[a], ps[b], 0, H.load_variant("baseline"), weeks=20, decline=True)
            calls.append(lv.apart)
        changed += calls[0] != calls[1]
        if changed:
            break
    assert changed
