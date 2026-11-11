"""H38 pairing norms (docs/results/h38-pairing-norms-design.md): the switch is off by default and reproduces earlier runs; each part
of the pressure dial does what the design says. Numbers are ASSUMED; these tests check mechanisms, not the numbers' truth."""
import dataclasses
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h38_fingerprint as F  # noqa: E402
from mar import exit_fallback as EF  # noqa: E402
from mar import exit_items as EI  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar.worlds import household as H  # noqa: E402

PINNED = json.loads((Path(__file__).parent / "data" / "h38_pairing_off_fingerprints.json").read_text())


def _world(pc, a="p-anchor", b="p-host", seed=0, weeks=20, together=True):
    ps = RT.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=pc)
    w = H.WeeklyWorld(H.load_variant("baseline"), (ps[a], ps[b]), seed, weeks, fixes=fx, levers=RT.LEVERS)
    if not together:
        for r in "AB":
            w.p[r]["in"] = False
    return w


# ---- off by default, reproduction ----------------------------------------------------------------------------------------

def test_default_fix_config_has_no_pairing():
    assert HD.FixConfig().pairing is None
    assert not HD.fixes_on(HD.FixConfig())


def test_pairing_off_reproduces_pinned_runs():
    assert F.fingerprints() == PINNED


def test_pairing_alone_turns_fixes_on():
    assert HD.fixes_on(HD.FixConfig(pairing=PR.dial(0)))


# ---- the dial --------------------------------------------------------------------------------------------------------------

def test_dial_levels_and_parts():
    c = PR.dial(2)
    assert (c.stigma, c.reward, c.exit_stigma) == (0.04, 0.04, 0.04)
    assert abs(c.withdraw - 0.30) < 1e-12
    assert PR.dial(4).withdraw == 0.6 and PR.dial(8).withdraw == 0.6
    s = PR.dial(4, parts=("stigma",))
    assert (s.stigma, s.reward, s.withdraw, s.exit_stigma) == (0.08, 0.0, 0.0, 0.0)
    z = PR.dial(0)
    assert (z.stigma, z.reward, z.withdraw, z.exit_stigma) == (0, 0, 0, 0) and z.intrinsic > 0
    f = PR.free(PR.dial(4))
    assert (f.stigma, f.reward, f.withdraw, f.exit_stigma) == (0, 0, 0, 0) and f.intrinsic == PR.dial(4).intrinsic


def test_values_pairing_is_assigned_from_three_levels_and_overridable():
    ps = RT.personas()
    vs = [PR.values_pairing(p) for p in ps.values()]
    assert set(vs) <= set(PR.V_LEVELS)
    assert all(vs.count(x) >= 6 for x in PR.V_LEVELS)       # roughly balanced over the 38 personas
    p = dataclasses.replace(ps["p-anchor"], weights={**ps["p-anchor"].weights, "values_pairing": 0.5})
    assert PR.values_pairing(p) == 0.5


# ---- each part lands in the pleasure row ----------------------------------------------------------------------------------

def test_reward_and_intrinsic_paid_only_while_together():
    pc = PR.dial(2, parts=("reward",))
    w = _world(pc)
    p, d = PR.terms(w, "A", 0)
    v = PR.values_pairing(w.personas["A"])
    assert abs(p - (0.04 + pc.intrinsic * v)) < 1e-12 and d["pr_reward"] == 0.04
    w2 = _world(pc, together=False)
    p2, d2 = PR.terms(w2, "A", 0)
    assert p2 == 0.0 and d2["pr_reward"] == 0.0


def test_stigma_paid_only_while_apart():
    pc = PR.dial(2, parts=("stigma",))
    assert PR.terms(_world(pc), "A", 0)[1]["pr_stigma"] == 0.0
    p, d = PR.terms(_world(pc, together=False), "A", 0)
    assert d["pr_stigma"] == 0.04 and abs(p + 0.04) < 1e-12


def test_exit_stigma_paid_by_the_leaver_for_its_weeks():
    pc = PR.dial(2, parts=("exit",))
    w = _world(pc)
    w.p["A"]["in"] = False
    w.left_at["A"] = 10
    assert PR.terms(w, "A", 10 + pc.exit_weeks - 1)[1]["pr_exit"] == 0.04
    assert PR.terms(w, "A", 10 + pc.exit_weeks)[1]["pr_exit"] == 0.0
    assert PR.terms(w, "B", 12)[1]["pr_exit"] == 0.0           # the one left behind pays stigma (unpaired), not exit stigma


def test_a_leave_records_the_week():
    w = _world(PR.dial(1))
    w.wk = {r: {"income": 0, "spent_self": 0, "works": 0, "rests": 0, "friends": 0, "together": 0, "contrib": 0,
                "friend_initiated": 0, "sanctioned": 0, "conn_hit": 0.0, "sec_hit": 0.0, "pressed": 0, "took": 0} for r in "AB"}
    w.units = {"A": 10, "B": 10}
    w.apply("A", {"a": "leave", "take": 50, "why": "bar"}, 7, [])
    assert w.left_at["A"] == 7 and w.left_at["B"] is None


def test_terms_reach_the_weekly_pleasure_row_and_raw_is_recorded():
    lo = _world(PR.dial(0, parts=()), together=False)
    hi = _world(PR.dial(4, parts=("stigma",)), together=False)
    for w in (lo, hi):
        last = {"busy": {"A": False, "B": False}}
        for x in range(4):
            last = {"busy": w.step_week(x, last)}
    row_lo, row_hi = lo.run.outcomes[0]["hedonic"]["A"], hi.run.outcomes[0]["hedonic"]["A"]
    assert "p_raw" in row_hi and row_hi["fix"]["pr_stigma"] == 0.08
    assert row_hi["pleasure"] < row_lo["pleasure"]


def test_withdrawal_cuts_friend_visits_while_together():
    def visits(pc):
        w = _world(pc, a="g-00000", b="g-11111", weeks=40)
        w.play()
        return sum(o["hedonic"][r]["fix"]["friends"] for o in w.run.outcomes for r in "AB")
    assert visits(PR.dial(4, parts=("withdraw",))) < visits(PR.dial(0))


def test_exit_anticipation():
    w = _world(PR.dial(2, parts=("exit",)))
    assert abs(PR.exit_anticipation(w) - 0.04 * min(26, NG.OUT_WEEKS) / NG.OUT_WEEKS) < 1e-12
    assert PR.exit_anticipation(_world(None)) == 0.0


# ---- formation responds to pressure ---------------------------------------------------------------------------------------

def _formed(pc, a, b, seed):
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    ps = RT.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=pc)
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID["V2-split-loves"]):
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=30, decline=True)
    return not lived.apart, lived.week0


def test_stigma_lowers_the_outside_option_and_reward_raises_the_inside():
    _, w0 = _formed(PR.dial(0), "p-anchor", "p-host", 0)
    _, ws = _formed(PR.dial(4, parts=("stigma",)), "p-anchor", "p-host", 0)
    _, wr = _formed(PR.dial(4, parts=("reward",)), "p-anchor", "p-host", 0)
    assert all(ws["O"][r] < w0["O"][r] for r in "AB")
    assert all(wr["W"][r] > w0["W"][r] for r in "AB")


def test_a_later_formation_gets_items_and_money_in():
    ps = RT.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0))
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID["V2-split-loves"]):
        w = H.WeeklyWorld(H.load_variant("baseline"), (ps["p-anchor"], ps["p-host"]), 0, 30, deal={"pot": False, "commits": []})
        assert w.items is None
        for r in "AB":
            w.p[r]["in"] = False
        NG._form_baseline(w, 13)
    assert w.items is not None and set(w.items) == {"home", "pet", "collection"}
    assert w.money_in["A"] > 0 and w.money_in["B"] > 0


# ---- the stay lens -----------------------------------------------------------------------------------------------------------

def test_stay_lens_classes_and_no_pressure_means_nothing_held():
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    ps = RT.personas()
    for pc in (PR.dial(0), PR.dial(4)):
        fx = dataclasses.replace(RT.FIXES_ON, pairing=pc)
        with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True):
            w = H.WeeklyWorld(H.load_variant("baseline"), (ps["p-anchor"], ps["p-host"]), 0, 60)
            last = {"busy": {"A": False, "B": False}}
            for x in range(13):
                last = {"busy": w.step_week(x, last)}
            rd = PR.stay_reading(w, 13, last)
        assert set(rd) == {"A", "B"} and all(rd[r]["verdict"] in PR.STAY_CLASSES for r in "AB")
        if pc.stigma == 0:
            assert all(rd[r]["verdict"] != "held" for r in "AB")
