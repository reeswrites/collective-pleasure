"""The hybrid agent (docs/results/hybrid-agent-prereg.md; mar.hybrid). Known-answer cases, run before the pass tests."""
import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

HYB = {"agent_values": "hybrid", "bills_hurt": True, "pleasure_scale": "sat", "decide_on": "pleasure", "decide_weeks": 13}


def _fx(**kw):
    from mar import pairing as PR
    from mar import retest as RT
    return dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **{**HYB, **kw})


def _world(weeks=30, **kw):
    from mar import hedonic as HD
    from mar import retest as RT
    from mar.worlds import household as H
    ps = RT.personas()
    with HD.use_levers(RT.LEVERS):
        return H.WeeklyWorld(H.load_variant("baseline"), (ps["p-anchor"], ps["p-host"]), 0, weeks, fixes=_fx(**kw))


def test_futures_are_fresh_and_reproducible():
    """A sampled future does not see the lived world's own shocks; the same seed gives the same future; held-out seeds differ."""
    from mar import hybrid as HY
    w = _world(156)
    a = HY.copy_world(w)
    b = HY.copy_world(w)
    fs = HY.future_seed(w.seed, 10, 0)
    HY.resample(a, 10, fs, 140)
    HY.resample(b, 10, fs, 140)
    assert a.shocks == b.shocks
    real = {k: v for k, v in w.shocks.items() if 10 <= k < 150}
    assert real and all(10 <= k < 150 for k in a.shocks)
    futures = []
    for k in range(4):
        c = HY.copy_world(w)
        HY.resample(c, 10, HY.future_seed(w.seed, 10, k), 140)
        futures.append(c.shocks)
    assert all(f != real for f in futures) and len({repr(f) for f in futures}) == 4
    assert {HY.future_seed(0, 10, k) for k in range(4)}.isdisjoint({HY.future_seed(0, 10, k, "held") for k in range(16)})
    assert a.fork_ok is False


def test_agreed_shares_are_paid_at_settlement():
    """Income term, couple's bill of 10, nothing paid by action, money 20 each: A pays 10 x 6/11, B 10 x 5/11, nothing is short."""
    from mar import hybrid as HY
    w = _world()
    HY.set_agreement(w, "income")
    w.step_agent = lambda *a, **k: None
    last = {"busy": {"A": False, "B": False}}
    for k in range(3):
        last = {"busy": w.step_week(k, last)}
    for r in "AB":
        w.p[r]["money"] = 20 + 2                  # the week's living cost comes first
    pool = w.pool
    w.step_week(3, last)
    assert abs(w.wk["A"]["agreed_paid"] - 60 / 11) < 1e-9 and abs(w.wk["B"]["agreed_paid"] - 50 / 11) < 1e-9
    assert w.arrears == 0 and w.pool == pool and w.wk["A"]["bill_fric"] == 0.0 if "bill_fric" in w.wk["A"] else True
    HY.set_agreement(w, "equal")
    assert w.agree["share"] == {"A": 0.5, "B": 0.5}


def test_choose_term_maximises_the_worse_off_members_gain():
    from mar import hybrid as HY
    V = {"income": {"A": 0.80, "B": 0.70}, "equal": {"A": 0.76, "B": 0.74}}
    assert HY.choose_term(V, {"A": 0.72, "B": 0.72}) == ("equal", True)
    assert HY.choose_term(V, {"A": 0.72, "B": 0.75}) == ("equal", False)


def test_yardstick_and_forecast_traits():
    """Mean weekly pleasure; a persona horizon cuts it, a discount weights early weeks, an outside-option bias is added as is."""
    from mar import hybrid as HY
    from mar import retest as RT
    rows = [{"hedonic": {"A": {"pleasure": x, "s_off": 0.5, "s_non": 0.5}}} for x in (0.9, 0.5, 0.1)]
    p = dataclasses.replace(RT.personas()["p-anchor"])
    assert abs(HY.score(rows, "A", p) - 0.5) < 1e-12                        # suffering does not enter the yardstick
    p.forecast = {"horizon": 2}
    assert abs(HY.score(rows, "A", p) - 0.7) < 1e-12
    p.forecast = {"discount": 0.5}
    assert abs(HY.score(rows, "A", p) - (0.9 + 0.25 + 0.025) / 1.75) < 1e-12
    from mar import hedonic as HD
    from mar import negotiation as NG
    q = dataclasses.replace(RT.personas()["p-anchor"])
    with HD.use_levers(RT.LEVERS), HD.use_fixes(_fx()):
        v0, _ = NG.outside_value(q, "A", 55, 0)
        q.forecast = {"outside_bias": 0.05}
        v1, _ = NG.outside_value(q, "A", 55, 0)
    assert abs(v1 - v0 - 0.05) < 1e-12


def test_rescore_drops_propose_only_actions_inside_a_forecast_and_keeps_the_forced_marker():
    from mar import hybrid as HY
    w = _world()
    c = HY.copy_world(w)
    c._ncall = {"A": 1, "B": 0}
    c._wk_snap = None
    cands = [(0.12, {"a": "give", "kind": "partner"}), (0.02, {"a": "rest"}), (99.0, {"a": "request", "kind": "time"})]
    out = HY.rescore(c, "A", 5, cands)
    assert [x[1]["a"] for x in out] == ["request", "rest"]


def test_a_hybrid_life_runs_and_its_choices_are_simulated():
    """A short lived run: week 0 is chosen on K futures under a bill term; readings use sampled futures; the run is deterministic."""
    import h38_pairing_run as H38
    from mar import hybrid as HY
    from mar import pairing as PR
    outs = []
    for _ in range(2):
        HY.STATS.update(futures=0, future_weeks=0, forks=0, choices=0)
        run, lived, rd = H38.play(PR.dial(0), "p-anchor", "p-host", 0, stay=True, weeks=30, rule=HYB)
        outs.append([o["hedonic"]["A"]["pleasure"] for o in run.outcomes])
        assert HY.STATS["choices"] >= 1 and HY.STATS["futures"] >= 4 * 2
        assert lived.week0["term"] in HY.TERMS
        if not lived.apart:
            assert lived.world.agree["term"] == lived.week0["term"]
    assert outs[0] == outs[1]


def test_hybrid_off_is_untouched_by_the_hooks():
    """With agent_values v2 the hybrid's hooks never run: no agreement, no call counter, no snapshot."""
    import h38_pairing_run as H38
    from mar import pairing as PR
    run, lived, _ = H38.play(PR.dial(0), "p-anchor", "p-host", 0, stay=False, weeks=14,
                             rule={"agent_values": "v2", "decide_on": "pleasure", "decide_weeks": 13})
    wd = lived.world
    assert not hasattr(wd, "agree") and not hasattr(wd, "_ncall") and not hasattr(wd, "_wk_snap")


def test_partner_payment_under_the_agreement_changes_nothing_when_shares_are_covered():
    """PT-R amendment 1: in the settlement week, a payment by A counts toward A's agreed share, so the partner's projection must not
    expect A to pay its full share on top. A's extra payment leaves B's week unchanged; without the amendment B would see the bill
    short by less and value A's payment above 0."""
    from mar import agent_values as AV
    from mar import hybrid as HY
    w = _world()
    HY.set_agreement(w, "income")
    w.step_agent = lambda *a, **k: None
    last = {"busy": {"A": False, "B": False}}
    for k in range(3):
        last = {"busy": w.step_week(k, last)}
    w.p["A"]["money"], w.p["B"]["money"] = 30, 4      # B cannot pay all its share this month; A can pay its own
    w.pool, w.funded = 0, 0
    s = AV.snapshot(w, "B", 3)
    assert s["settle"] and s["agree"]["o_paid"] == 0
    t = AV._paid(s, 3)
    assert abs(AV.week_net(t) - AV.week_net(s)) < 1e-12
    old = dict(t, agree=dict(t["agree"], o_paid=0))      # the projection before the amendment: A's share expected on top
    assert AV.week_net(old) - AV.week_net(s) > 0.002
