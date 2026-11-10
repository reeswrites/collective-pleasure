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
