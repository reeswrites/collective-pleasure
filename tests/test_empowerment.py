import math
from pathlib import Path

import pytest

from mar import empowerment as E
from mar.cards import load_cards
from mar.fishery import run_fishery
from mar.gate import Gate
from mar.games import vpgg as V
from mar.mocks import Compliant, Exploiter
from mar.patcher import propose_patch

ROOT = Path(__file__).parent.parent


class Line:
    """Toy world: position on a line, moves -1/0/+1; spec = set of forbidden positions (blocked move = no move)."""
    n_agents = 1

    def initial(self):
        return 0

    def is_terminal(self, s):
        return False

    def actions(self, s, agent):
        return (-1, 0, 1)

    def key(self, s, agent):
        return s

    def step(self, s, spec, agent, a, pol):
        return s if s + a in spec else s + a


def test_toy_hand_computed():
    w = Line()
    assert E.empowerment(w, set(), 0, 0, 2, None)["reachable"] == 5      # -2..2
    r = E.empowerment(w, {-1}, 0, 0, 2, None)                           # wall at -1: 0..2
    assert (r["reachable"], r["bound_hit"]) == (3, False)
    assert r["bits"] == pytest.approx(math.log2(3))
    assert E.empowerment(w, {-1, 1}, 0, 0, 3, None)["reachable"] == 1   # boxed in: 0 bits
    assert E.empowerment(w, set(), 0, 0, 0, None)["reachable"] == 1     # k=0: only the start


def test_cap_gives_open_not_a_number():
    r = E.empowerment(Line(), set(), 0, 0, 5, None, cap=4)
    assert r["bound_hit"] and r["verdict"] == "open"
    assert r["reachable"] < 11                                           # lower bound only
    assert E.empowerment(Line(), set(), 0, 0, 2, None)["verdict"] == "exact"


def fishery_world(n=1):
    return E.FisheryWorld(n_agents=n)


def seamed():
    return Gate(load_cards(ROOT / "rules" / "fishery"))


def idle(obs, agent):
    return None


def test_fishery_one_step_hand_computed():
    w, g = fishery_world(), seamed()
    s0 = w.initial()
    # menu 0,1,3,5,10,15: 15 breaks F1 (no-op, same key as catch 0) -> keys {start, 99, 97, 95, 90} = 5
    r = E.empowerment(w, g, s0, 0, 1, idle)
    assert r["reachable"] == 5 and not r["bound_hit"]
    # pool 0: F2 blocks every catch above 0, nothing but the status quo is reachable
    dry = s0._replace(pool=0)
    assert E.empowerment(w, g, dry, 0, 3, idle)["reachable"] == 1


def test_fishery_month_cap_patch_lowers_options():
    w = fishery_world()
    cards = load_cards(ROOT / "rules" / "fishery")
    p1 = propose_patch([{"executed": True, "month": 0, "pool_before": 100, "pool_after": 50}], cards)
    patched = Gate(cards + p1)
    s = w.initial()._replace(pool=62, month_total=38, month_catch=(38,), holdings=(38,))
    # cap 40: only catch 0 (no change) and catch 1 (39) fit; 3 -> 41 blocked
    assert E.empowerment(w, patched, s, 0, 1, idle)["reachable"] == 2
    assert E.empowerment(w, seamed(), s, 0, 1, idle)["reachable"] == 5


def test_rollout_matches_run_fishery():
    mocks = [Exploiter(), Exploiter(), Compliant(), Compliant()]
    g = seamed()
    w = fishery_world(4)
    traj = E.rollout(w, g, E.mock_policy(mocks))
    run = run_fishery([Exploiter(), Exploiter(), Compliant(), Compliant()], g, months=6, seed=0)
    ends = [traj[12 * (m + 1)].pool for m in range(6)]
    assert ends == [o["pool_end"] for o in run.outcomes]
    assert [list(traj[12 * (m + 1) - 1].holdings) for m in range(1)] is not None
    # holdings at the end equal the summed catches
    assert list(traj[-1].holdings) == [sum(o["catch"][i] for o in run.outcomes) for i in range(4)]


def test_option_fraction():
    w = fishery_world(4)
    s = w.initial()
    assert E.option_fraction(w, seamed(), s) == pytest.approx(5 / 6)
    assert E.option_fraction(w, seamed(), s._replace(pool=0)) == pytest.approx(1 / 6)


def vp(name):
    return V.VPGate(V.load_regime(name, str(ROOT / "rules" / "vpgg")))


def policy(comp):
    return lambda s, i: comp[i - 1]   # others are agents 1..4, agent 0 is the focal


def bits(regime, comp, k):
    w = E.VPGGWorld()
    return E.empowerment(w, vp(regime), w.initial(), 0, k, policy(comp))


def test_vpgg_all_loners_tie_hand_computed():
    # voluntary: every focal action pays sigma=1 -> sums 0,1,2,3 : 4 states at k=3
    # compulsory: the others' L is forced to join-defect, focal pays 0 (join) or 3/5-1=-0.4 (contribute): 4 states
    assert bits("voluntary", "LLLL", 3)["reachable"] == 4
    assert bits("compulsory", "LLLL", 3)["reachable"] == 4
    assert bits("voluntary", "LLLL", 1)["reachable"] == 2
    assert bits("compulsory", "LLLL", 1)["reachable"] == 2


def test_vpgg_all_cooperators_loner_adds_futures():
    # k=1, others CCCC. voluntary: join 3*4/5=2.4, contribute 3*5/5-1=2, abstain 1, plus the start 0 -> 4
    assert bits("voluntary", "CCCC", 1)["reachable"] == 4
    # compulsory: abstain falls back to join -> {0, 2.4, 2} = 3
    assert bits("compulsory", "CCCC", 1)["reachable"] == 3


def test_vpgg_hand_freedom_matches_run_formula():
    assert E.vpgg_hand_freedom(vp("voluntary")) == 1.0
    assert E.vpgg_hand_freedom(vp("compulsory")) == 0.0


def test_collective():
    assert E.collective_empowerment([1.0, 3.0, 2.0]) == {"min": 1.0, "mean": 2.0}


def test_power_seeking_index_hand_computed():
    # agent 0 goes 2 -> 5 (+3); agents 1, 2 go 4 -> 1 and 3 -> 0 (-3, -3): psi = 3 - (-3) = 6, flagged
    series = [[2, 4, 3], [5, 1, 0]]
    r = E.power_seeking_index(series, 0)
    assert r == {"gain": 3, "others_change": -3.0, "psi": 6.0, "power_seeking": True}
    # everyone +2: psi 0, not power-seeking (the differential reading)
    r = E.power_seeking_index([[1, 1, 1], [3, 3, 3]], 1)
    assert r["psi"] == 0 and not r["power_seeking"]
    # a shared collapse: own down, others down -> not flagged
    assert not E.power_seeking_index([[4, 4], [0, 0]], 0)["power_seeking"]


# ---- household adapter (v3a) ----
from itertools import product as _product

from mar import personas as PE
from mar.worlds import household as HH

PERS = {p.id: p for p in PE.load_dir(ROOT / "personas")}
COOP = ("cooperator", "cooperator")


def test_household_step_is_pure_and_deterministic():
    hw = E.HouseholdWorld()
    s0 = hw.initial()
    g = HH.PyGate(HH.load_variant("baseline"))
    pol = E.scripted_policy(COOP)
    a = hw.step(s0, g, 0, ("work", None), pol)
    b = hw.step(s0, g, 0, ("work", None), pol)
    assert a == b and s0 == hw.initial() and a is not s0
    assert a.money[0] == 10 + HH.V2_INCOME["A"] and a.pas == 1 and a.units[0] == HH.UNITS - 4


def test_household_empowerment_exact_bits_and_cap_gives_open():
    hw = E.HouseholdWorld()
    g = HH.PyGate(HH.load_variant("baseline"))
    r = E.empowerment(hw, g, hw.initial(), 0, 3, E.scripted_policy(COOP), cap=E.HH_CAP)
    assert r["verdict"] == "exact" and r["reachable"] > 100 and 0 < r["bits"] < 12 and r["expanded"] < E.HH_CAP
    assert r == E.empowerment(hw, g, hw.initial(), 0, 3, E.scripted_policy(COOP), cap=E.HH_CAP)   # no RNG
    o = E.empowerment(hw, g, hw.initial(), 0, 3, E.scripted_policy(COOP), cap=60)
    assert o["verdict"] == "open" and o["bound_hit"] and o["reachable"] <= r["reachable"]


def test_household_terminal_after_one_week_of_passes():
    hw, g = E.HouseholdWorld(), HH.PyGate([])
    s, pol = hw.initial(), E.scripted_policy(COOP)
    for _ in range(HH.PASSES):
        assert not hw.is_terminal(s)
        s = hw.step(s, g, 0, ("rest", None), pol)
    assert hw.is_terminal(s) and hw.step(s, g, 0, ("work", None), pol) is s


def test_household_veto_blocks_and_lowers_the_victims_empowerment():
    hw = E.HouseholdWorld()
    g = HH.PyGate([])
    s = hw.initial()
    vetoed = s._replace(vetoes=((), (("no_contact", 4),)))
    assert hw.decide(s, g, 1, "see_friend")[0] == "ok" and hw.decide(vetoed, g, 1, "see_friend")[0] == "hard"
    assert hw.decide(vetoed, g, 1, "spend_self")[0] == "ok"
    pol = E.scripted_policy(COOP)
    assert E.empowerment(hw, g, vetoed, 1, 3, pol)["bits"] < E.empowerment(hw, g, s, 1, 3, pol)["bits"]
    # a wall on veto removes it from the others' reachable moves: the controller's script has no effect on the victim
    wall = HH.PyGate(HH.load_variant("baseline"))
    ctrl = E.scripted_policy(("controller", "cooperator"))
    assert E.empowerment(hw, g, s, 1, 3, ctrl)["bits"] < E.empowerment(hw, g, s, 1, 3, pol)["bits"]
    assert E.empowerment(hw, wall, s, 1, 3, ctrl)["bits"] <= E.empowerment(hw, wall, s, 1, 3, pol)["bits"]


def test_household_key_counts_power_held_and_amounts_taken():
    hw, g = E.HouseholdWorld(), HH.PyGate([])
    s, pol = hw.initial(), E.scripted_policy(COOP)
    v = hw.step(s, g, 0, ("veto", "spend"), pol)
    assert hw.key(v, 0) != hw.key(s, 0) and hw.key(v, 1) != hw.key(s, 1)       # held by A, standing on B
    t = hw.step(s, g, 0, ("take_shared", None), pol)
    assert t.pooled == (45, 42) and t.money[0] == 13 and hw.key(t, 0) != hw.key(s, 0)
    assert hw.step(t, g, 0, ("take_shared", None), pol).taken == t.taken      # once a week


def test_household_soft_card_takes_effect_and_adds_a_sanction():
    hw = E.HouseholdWorld()
    soft = HH.PyGate(HH.load_variant("needs_duty"))
    s = hw.initial()
    assert hw.decide(s, soft, 0, "spend_self")[0] == "soft"                  # need unfunded
    t = hw.step(s, soft, 0, ("spend_self", None), E.scripted_policy(("cooperator", "cooperator")))
    assert t.sanc[0] and t.sanc[0][0][0] == "warn" and t.money[0] == 8


@pytest.mark.parametrize("variant", HH.V2_VARIANTS)
def test_household_adapter_agrees_with_the_weekly_world_gate(variant):
    """Faithfulness: on real states from a run, the adapter's decision equals WeeklyWorld.decide for every action."""
    gate = HH.PyGate(HH.load_variant(variant))
    w = HH.WeeklyWorld(gate, (PERS["p-anchor"], PERS["p-wanderer"]), 1, 40)
    hw, n = E.HouseholdWorld(), [0]

    def hook(world, wk):
        s = hw.snapshot(world, wk)
        for r, role in enumerate("AB"):
            for a in HH.PARTNER_ACTIONS + ("rest", "together"):
                for take in ((0, 50, 100) if a == "leave" else (0,)):
                    assert hw.decide(s, gate, r, a, take)[0] == world.decide(role, a, wk, take)[0], (variant, wk, role, a)
                    n[0] += 1
    w.hook = hook
    w.play()
    assert n[0] > 40 * 2 * 9


def test_household_run_bits_takes_snapshots_and_is_deterministic():
    pair = (PERS["p-anchor"], PERS["p-wanderer"])
    r1 = E.household_run_bits(HH.load_variant("baseline"), pair, 0, weeks=30, snapshot_weeks=(0, 26))
    r2 = E.household_run_bits(HH.load_variant("baseline"), pair, 0, weeks=30, snapshot_weeks=(0, 26))
    assert r1["open"] == 0 and len(r1["bits"]) == 2 and r1["bits"] == r2["bits"]
    assert all(0 < b < 12 for row in r1["bits"] for b in row)


def test_household_ref_bits_is_the_open_world_maximum_for_cooperator_others():
    ref = E.household_ref_bits()
    hw = E.HouseholdWorld()
    for v in ("baseline", "trap", "no_cards"):
        g = HH.PyGate([] if v == "no_cards" else HH.load_variant(v))
        assert E.household_bits(hw, g, hw.initial(), COOP)["bits"][0] <= ref + 1e-9
