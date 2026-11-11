import math
from pathlib import Path

import pytest

from mar import empowerment as E
from mar import liberty as L
from mar.games import vpgg as V

ROOT = Path(__file__).parent.parent
W = L.ToyVetoWorld()
RIGHT, WALL = L.TSpec(True), L.TSpec(False)


def lib(spec, agent, pol=L.kind_master, k=2):
    return L.liberty(W, spec, W.initial(), agent, k, pol)


def test_toy_plain_empowerment_hand_computed():
    # A: (nx, nw) with nx + nw <= 2 -> 6 keys. B: (bw 0..2, no veto) + (0,T), (1,T) -> 5 with the right, 3 under the wall.
    assert E.empowerment(W, RIGHT, W.initial(), 0, 2, L.kind_master)["reachable"] == 6
    assert E.empowerment(W, WALL, W.initial(), 0, 2, L.kind_master)["reachable"] == 6
    assert E.empowerment(W, RIGHT, W.initial(), 1, 2, L.kind_master)["reachable"] == 5
    assert E.empowerment(W, WALL, W.initial(), 1, 2, L.kind_master)["reachable"] == 3


def test_unexercised_veto_lowers_liberty_not_empowerment():
    a_r, a_w = lib(RIGHT, 0), lib(WALL, 0)
    assert a_r["bits"] == pytest.approx(a_w["bits"]) == pytest.approx(math.log2(6))
    assert (a_r["c"], a_r["d"]) == (6, 3) and a_r["blocker"][0] == 1 and a_r["blocker"][1] == "veto"
    assert (a_w["c"], a_w["d"]) == (6, 0)
    assert a_r["liberty"] == pytest.approx(math.log2(6) - 2)
    assert a_w["liberty"] == pytest.approx(math.log2(6))


def test_wall_costs_vetoer_empowerment_not_liberty():
    b_r, b_w = lib(RIGHT, 1), lib(WALL, 1)
    assert b_r["bits"] == pytest.approx(math.log2(5)) and b_w["bits"] == pytest.approx(math.log2(3))
    assert b_r["c"] == b_w["c"] == 3          # the veto path is incompatible: it shrinks A's futures
    assert b_r["d"] == b_w["d"] == 0
    assert b_r["liberty"] == pytest.approx(b_w["liberty"]) == pytest.approx(math.log2(3))


def test_exercised_veto_lowers_plain_empowerment():
    r = E.empowerment(W, RIGHT, W.initial(), 0, 2, L.exercising_master)
    assert r["reachable"] == 3


def test_invariants_and_single_member():
    for spec in (RIGHT, WALL):
        for i in (0, 1):
            r = lib(spec, i)
            assert 0 <= r["bits_c"] <= r["bits"] + 1e-12 and r["liberty"] <= r["bits"] + 1e-12 and not r["open"]

    class Solo(L.ToyVetoWorld):
        n_agents = 1
    r = L.liberty(Solo(), RIGHT, W.initial(), 0, 2, L.kind_master)
    assert r["d"] == 0 and r["c"] == r["reachable"]


def test_cap_gives_open():
    assert L.liberty(W, RIGHT, W.initial(), 0, 2, L.kind_master, cap=3)["open"]


def test_fishery_zero_pool_has_zero_liberty():
    from mar.mocks import Compliant, Exploiter
    w = E.FisheryWorld(n_agents=2, months=3, subrounds=2)
    s = w.initial()._replace(pool=0)
    pol = E.mock_policy([Exploiter(), Compliant()])
    class Strict:
        def check_action(self, state, act):
            return (act["catch"] == 0 or act["catch"] <= state["pool"], [])
    r = L.liberty(w, Strict(), s, 0, 1, pol)
    assert r["c"] == 1 and r["liberty"] == 0.0


def test_vpgg_runs_and_respects_invariants():
    w = E.VPGGWorld()
    g = V.VPGate(V.load_regime("voluntary", str(ROOT / "rules" / "vpgg")))
    pol = lambda s, i: "CDLL"[i - 1] if i else "C"  # noqa: E731
    r = L.liberty(w, g, w.initial(), 0, 2, pol)
    assert 0 <= r["bits_c"] <= r["bits"] + 1e-12 and r["liberty"] <= r["bits"] + 1e-12 and not r["open"]


# ---- v2: interference vs withdrawal (docs/results/liberty-v2-prereg.md) ----

PW = L.PartnerWorld()


def plib(spec, version, agent=0):
    return L.liberty(PW, spec, PW.initial(), agent, 2, L.partner_stays, version=version)


def test_v2_a_veto_counts_as_domination():
    r = plib(RIGHT, 2)
    assert r["blocker"] == (1, "veto") and r["d"] == 2    # solo keys (0,1), (0,2) are held at B's sufferance
    assert r["liberty"] == pytest.approx(0.0)             # log2(3) - log2(3)
    assert plib(WALL, 2)["d"] == 0                        # the wall removes the veto and D with it


def test_v2_a_partner_leaving_is_not_domination():
    w = plib(WALL, 2)
    assert w["d"] == 0 and w["blocker"] is None
    assert plib(WALL, 1)["d"] == 3 and plib(WALL, 1)["blocker"] == (1, "leave")   # v1 scored the exit as domination
    assert w["liberty"] == pytest.approx(math.log2(3))


def test_v2_a_partner_abstaining_is_not_domination():
    class OnlyAbstain(L.PartnerWorld):
        MENU = {0: ("joint", "solo", "rest"), 1: ("pass", "abstain")}
    r2 = L.liberty(OnlyAbstain(), WALL, PW.initial(), 0, 2, L.partner_stays, version=2)
    r1 = L.liberty(OnlyAbstain(), WALL, PW.initial(), 0, 2, L.partner_stays, version=1)
    assert r2["d"] == 0 and r2["blocker"] is None and r1["d"] > 0
    assert r2["ado"] > 0 and r2["ado_by"] == (1, "abstain")


def test_v2_agreement_dependent_option_excluded_and_reported():
    r = plib(WALL, 2)
    assert r["c_all"] == 6 and r["ado"] == 3 and r["c"] == 3 and r["ado_by"] == (1, "leave")
    assert r["bits_c"] == pytest.approx(math.log2(3))     # keys needing B's joint participation are not A's own options
    assert r["bits"] == pytest.approx(math.log2(6))       # plain empowerment still counts them (the loss stays visible)


def test_v2_equals_v1_on_toy_veto_world():
    for spec in (RIGHT, WALL):
        for i in (0, 1):
            a, b = lib(spec, i), L.liberty(W, spec, W.initial(), i, 2, L.kind_master, version=1)
            assert a["liberty"] == pytest.approx(b["liberty"]) and a["d"] == b["d"] and a["c"] == b["c"] and a["ado"] == 0


def test_v2_classification_tables_complete():
    for i in (0, 1):
        for a in W.actions(None, i):
            assert W.classify(None, i, a) in (L.INTERFERENCE, L.WITHDRAWAL, L.OWN)
    for a in V.ACTIONS:
        assert L.classify(E.VPGGWorld(), None, 1, a) != L.INTERFERENCE
    fw = E.FisheryWorld(n_agents=2)
    assert L.classify(fw, None, 0, 0) == L.WITHDRAWAL and L.classify(fw, None, 0, 3) == L.INTERFERENCE


def test_v2_invariants_and_solo():
    for spec in (RIGHT, WALL):
        for i in (0, 1):
            r = plib(spec, 2, i)
            assert r["liberty"] <= r["bits"] + 1e-12 and 0 <= r["bits_c"] <= r["bits"] + 1e-12 and not r["open"]

    class Solo(L.PartnerWorld):
        n_agents = 1
    r = L.liberty(Solo(), RIGHT, PW.initial(), 0, 2, L.partner_stays)
    assert r["d"] == 0 and r["ado"] == 0


# ---- household adapter (slice 1 of the household evolution run) ----

from mar.worlds import household as HH  # noqa: E402


def test_household_classification_table_covers_the_menu_and_follows_the_adr():
    hw = E.HouseholdWorld()
    s = hw.initial()
    for act in E.HH_MENU:
        kind = hw.classify(s, 0, act)
        assert kind in (E.INTERFERENCE, E.WITHDRAWAL, E.OWN)
        assert E.hh_class(act)[1]                           # a one-line rationale each
    assert hw.classify(s, 0, ("veto", "no_contact")) == E.INTERFERENCE
    assert hw.classify(s, 0, ("veto", "spend")) == E.INTERFERENCE
    assert hw.classify(s, 0, ("take_shared", None)) == E.INTERFERENCE
    assert hw.classify(s, 0, ("leave", 100)) == E.INTERFERENCE      # carries the other's half out
    for act in (("leave", 0), ("leave", 50), ("rest", None), ("refuse_request", None)):
        assert hw.classify(s, 1, act) == E.WITHDRAWAL
    for act in (("work", None), ("spend_self", None), ("see_friend", None), ("request", "time"), ("return", None)):
        assert hw.classify(s, 0, act) == E.OWN


def test_household_noop_and_force_policy():
    hw = E.HouseholdWorld()
    assert hw.noop(hw.initial(), 0) == ("rest", None)
    pol = hw.force_policy(E.scripted_policy(("cooperator", "cooperator")), 1, ("veto", "spend"))
    assert pol(hw.initial(), 1) == [("veto", "spend")]
    assert pol(hw.initial(), 0)[-1] == ("rest", None)       # the other member keeps the script


def _hh_liberty(variant, scripts=("cooperator", "cooperator"), k=2):
    hw = E.HouseholdWorld()
    gate = HH.PyGate(HH.load_variant(variant))
    return L.household_liberty(hw, gate, hw.initial(), scripts, k=k)


def test_household_liberty_has_the_v2_invariants():
    for v in ("baseline", "veto_consent", "author_seed_v2_bindable"):
        for r in _hh_liberty(v):
            assert not r["open"]
            assert r["c"] >= 1 and 0 <= r["d"] <= r["c"] - 1
            assert r["c"] + r["ado"] == r["c_all"] or r["ado"] == r["c_all"] - r["c"]
            assert r["liberty"] <= r["bits"] + 1e-9       # compatible, penalised futures never exceed plain reach


def test_household_over_split_exit_is_domination_and_a_half_exit_is_not():
    """Hand case (author_seed_v2 imposed, no negotiated exit term): the partner able to carry the WHOLE pot out dominates; baseline's
    E1 wall (never more than half) removes that blocker, so a leave of more than half is the exposure in one and not the other."""
    free = _hh_liberty("author_seed_v2_free_exit")
    walled = _hh_liberty("baseline")
    assert free[0]["blocker"] == (1, ("leave", 100)) and free[1]["blocker"] == (0, ("leave", 100))
    assert all(r["blocker"] is None or r["blocker"][1][0] != "leave" for r in walled)
    assert all(f["liberty"] < w["liberty"] for f, w in zip(free, walled))


def test_household_withdrawal_is_not_domination():
    """The partner leaving, resting or refusing is never the blocker of v2 liberty at the initial state."""
    for v in ("baseline", "free_chaotic", "author_seed_v2_free_exit"):
        for r in _hh_liberty(v):
            if r["blocker"] is not None:
                assert E.hh_class(r["blocker"][1])[0] == E.INTERFERENCE


def test_household_run_liberty_smoke(tmp_path):
    from mar import personas as P
    ps = {p.id: p for p in P.load_dir(ROOT / "personas")}
    r = L.household_run_liberty(HH.load_variant("baseline"), (ps["p-anchor"], ps["p-wanderer"]), 0, weeks=26, snapshots=(0, 13))
    assert len(r["snaps"]) == 2 and r["liberty_min"] is not None
    assert r["bits_min"] >= r["liberty_min"] - 1e-9


def test_household_run_liberty_memo_returns_identical_values():
    from mar import personas as P
    ps = {p.id: p for p in P.load_dir(ROOT / "personas")}
    gate = HH.PyGate(HH.load_variant("baseline"))
    a = L.household_run_liberty(gate, (ps["p-anchor"], ps["p-wanderer"]), 0, weeks=20, snapshots=(0, 10))
    b = L.household_run_liberty(gate, (ps["p-anchor"], ps["p-wanderer"]), 0, weeks=20, snapshots=(0, 10))      # second call hits the memo
    fresh = L.household_run_liberty(HH.load_variant("baseline"), (ps["p-anchor"], ps["p-wanderer"]), 0, weeks=20, snapshots=(0, 10))
    assert a["snaps"] == b["snaps"] == fresh["snaps"]


def test_household_run_bits_accepts_cfg_and_k():
    from dataclasses import replace
    from mar import hedonic as HD
    from mar import personas as P
    ps = {p.id: p for p in P.load_dir(ROOT / "personas")}
    r = E.household_run_bits(HH.load_variant("baseline"), (ps["p-anchor"], ps["p-wanderer"]), 0, weeks=14, snapshot_weeks=(0, 7), k=2,
                             cfg=replace(HD.DEFAULT, start=0.05))
    assert len(r["bits"]) == 2 and r["open"] == 0
