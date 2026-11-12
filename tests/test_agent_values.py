"""Agent recalibration (agent_values v2) and bills that hurt (docs/results/agent-recalibration-prereg.md)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))


def test_defaults_reproduce_pinned_fingerprints():
    """Pinned at commit 36a6460, before the switches existed: with agent_values v1 and bills_hurt off, nothing moves."""
    import agent_values_fingerprint as AF
    pinned = json.loads((ROOT / "tests" / "data" / "agent_values_off_fingerprints.json").read_text())
    assert AF.fingerprints() == pinned


def test_v2_reproduces_pinned_fingerprints():
    """Pinned at commit dff1c4d, before the bill horizon existed (docs/results/agent-bill-horizon-prereg.md): agent_values v2, with and
    without bills that hurt, must not move when v2b is added."""
    import agent_values_fingerprint as AF
    pinned = json.loads((ROOT / "tests" / "data" / "agent_values_v2_fingerprints.json").read_text())
    assert AF.fingerprints({"agent_values": "v2", "bills_hurt": True}) == pinned["v2+bills"]
    assert AF.fingerprints({"agent_values": "v2"}) == pinned["v2"]


# ---- bills that hurt: known-answer cases (prereg KA1 to KA4) -------------------------------------------------------------------

def _world(bills=True, values="v1"):
    import dataclasses
    from mar import hedonic as HD
    from mar import retest as RT
    from mar.worlds import household as H
    ps = RT.personas()
    fx = dataclasses.replace(RT.FIXES_ON, bills_hurt=bills, agent_values=values)
    with HD.use_levers(RT.LEVERS):
        w = H.WeeklyWorld(H.load_variant("baseline"), (ps["p-anchor"], ps["p-host"]), 0, 20, fixes=fx)
    w.step_agent = lambda *a, **k: None          # nobody acts: the settlement alone
    return w


def _settle_week(w, pool, money):
    w.pool = pool
    for r in "AB":
        w.p[r]["money"] = money
    last = {"busy": {"A": False, "B": False}}
    rows = []
    for k in range(4):
        last = {"busy": w.step_week(k, last)}
        rows.append(w.run.outcomes[-1])
    return rows[-1]


def test_ka1_no_money_empty_pot_suffers_and_the_bill_carries():
    hurt, plain = _world(True), _world(False)
    rh, rp = _settle_week(hurt, 0, 0), _settle_week(plain, 0, 0)
    for r in "AB":
        assert hurt.wk[r]["bill_fric"] == 0.30 * 1.0 * 1.0 + 0.30          # full stress at an empty pot, plus eviction stress
        assert rh["hedonic"][r]["s_off"] > rp["hedonic"][r]["s_off"]
    assert hurt.arrears == 10 * 1.05 and hurt.need_month() == 10 + 10 * 1.05


def test_ka2_full_pot_no_stress_only_the_lost_buffer():
    hurt, plain = _world(True), _world(False)
    _settle_week(hurt, 90, 20)
    _settle_week(plain, 90, 20)
    for r in "AB":
        assert hurt.wk[r]["bill_fric"] == 0.0
        assert abs(hurt.wk[r]["sec_hit"] - 10.5 / 2 / 25) < 1e-12
        assert abs(hurt.hed[r].level["security"] - (plain.hed[r].level["security"] - 0.21)) < 0.01   # the buffer, less a refill nudge
    assert hurt.arrears == 0 and abs(hurt.pool - (plain.pool - 0.5)) < 1e-9                  # the late fee left the pot


def test_ka3_funded_bill_costs_nothing():
    hurt, plain = _world(True), _world(False)
    hurt.funded = plain.funded = 10
    rh, rp = _settle_week(hurt, 30, 20), _settle_week(plain, 30, 20)
    assert [rh["hedonic"][r] for r in "AB"] == [rp["hedonic"][r] for r in "AB"]
    assert hurt.pool == plain.pool and hurt.arrears == 0


def test_ka4_bills_off_is_the_old_settlement():
    w = _world(False)
    _settle_week(w, 0, 0)
    assert w.arrears == 0 and w.need_month() == 10 and "bill_fric" not in w.wk["A"]


# ---- agent values v2 ------------------------------------------------------------------------------------------------------------

def test_v2_value_is_the_models_own_week_change_at_the_last_call():
    """Known answer: at the very last call of a week (partner B, third pass) nothing else happens before the close, so an action's v2
    own value must equal the change in B's own net that week (the hedonic rows round to 4 decimals)."""
    import dataclasses
    sys.path.insert(0, str(ROOT / "scripts"))
    import h38_pairing_run as H38
    import value_consistency as VCS
    from mar import exit_fallback as EF
    from mar import exit_items as EI
    from mar import hedonic as HD
    from mar import negotiation as NG
    from mar import retest as RT
    from mar import valuecheck as VC
    from mar.worlds import household as H
    ps = RT.personas()
    n = 0
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    fx = dataclasses.replace(VCS._ctx(), agent_values="v2", bills_hurt=True)
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[H38.CELL]):
        lived = NG.BaselineLived(ps["g-00000"], ps["p-host"], 0, H.load_variant("baseline"), weeks=H.WEEKS, decline=True)
        world, last = lived.world, {"busy": {"A": False, "B": False}}
        for w in range(12):
            if w in (3, 7, 11):
                rec = VC.measure_decision(VC.snapshot(world), dict(last), w, "B", 2, horizons=(1,))
                for it in (rec or {"items": []})["items"]:
                    if it["applied"] and it["a"] != "together":
                        assert abs(it["actual"][1]["own"]["net"] - it["perceived"]) < 3e-4, it
                        n += 1
            last = {"busy": world.step_week(w, last)}
    assert n >= 8


def test_v2_sanction_is_priced_at_the_friction_it_adds():
    w = _world(True, "v2")
    sanc = [{"kind": "warn", "duration_months": 1, "card": "D1-needs-first"}]
    assert w.sanction_cost("A", 5, sanc) == 0.15 * 4
    w.sanctions["A"].append({"kind": "warn", "until": 7, "card": "D1-needs-first"})     # running two more weeks: only the extension
    assert abs(w.sanction_cost("A", 5, sanc) - 0.15 * 2) < 1e-12
    v1 = _world(True, "v1")
    assert v1.sanction_cost("A", 5, sanc) == 0.01 * 4                                      # v1: the old estimate


def test_v2_planner_starts_from_the_agents_own_values():
    """Item 5: makers.WeekPlanner under v2 reads the same values the agent chooses on (noise off), so the planner's time cost is in the
    hedonic model's units."""
    from mar import makers as MK
    w = _world(True, "v2")
    last = {"busy": {"A": False, "B": False}}
    w.step_agent = type(w).step_agent.__get__(w)
    for k in range(3):
        last = {"busy": w.step_week(k, last)}
    w.wk = {r: {"income": 0, "spent_self": 0, "works": 0, "rests": 0, "friends": 0, "together": 0, "contrib": 0, "friend_initiated": 0,
                "sanctioned": 0, "conn_hit": 0.0, "sec_hit": 0.0, "pressed": 0, "took": 0} for r in "AB"}
    w.units = {"A": 10, "B": 10}
    plan = MK.WeekPlanner(w, "A", 3)
    o = w.obs("A", 3, last)
    ag = w.agents["A"]
    ag._noise = lambda: 1.0
    try:
        direct = ag.utilities(o)
    finally:
        del ag._noise
    got = plan()
    assert set(got) <= set(direct) and all(abs(got[a] - direct[a]) < 1e-12 for a in got)
    after = plan((0, 0, 0, 0, 0, 1))                                                      # one planned rest moves the values
    assert after["rest"] < got["rest"]
