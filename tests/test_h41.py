"""H41 choice aids (docs/results/h41-choice-aids-prereg.md): the world and hybrid hooks, and the exact side model (mar.h41_exact)."""
import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def _world(weeks=20, apart=False, **kw):
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import pairing as PR
    from mar import retest as RT
    from mar.worlds import household as H
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), agent_values="hybrid", bills_hurt=True, pleasure_scale="sat",
                             satiety_expect="world", **kw)
    ps = RT.personas()
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        deal = {"pot": False, "commits": []} if apart else None
        w = H.WeeklyWorld(H.load_variant("baseline"), (ps["p-anchor"], ps["p-host"]), 0, weeks, **({"deal": deal} if deal else {}))
        if apart:
            for r in "AB":
                w.p[r]["in"] = False
            w.solo = {"A": "alone", "B": "alone"}
        else:
            HY.set_agreement(w, "income")
    return w, fx


def _play(world, fx, weeks):
    from mar import hedonic as HD
    from mar import retest as RT
    last = {"busy": {"A": False, "B": False}}
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        for w in range(weeks):
            last = {"busy": world.step_week(w, last)}
    return world


def _sessions(world, fx, weeks):
    from mar import hedonic as HD
    from mar import retest as RT
    last, n = {"busy": {"A": False, "B": False}}, 0
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        for w in range(weeks):
            last = {"busy": world.step_week(w, last)}
            n += world.wk["A"]["together"]
    return n


def test_lat_allows_time_together_while_apart_and_plain_apart_does_not():
    from mar import hybrid as HY
    w, fx = _world(apart=True, h41_lat=True)
    assert not w.can_meet()
    HY.make_lat(w, {"A": "alone", "B": "alone"})
    assert w.lat_on() and w.can_meet()
    assert w.need_month() == 0 and not w.pot                    # no shared home: no bills, no pot
    n_lat = _sessions(w, fx, 12)
    assert all(not o["both_in"] for o in w.run.outcomes)
    plain, fx2 = _world(apart=True)
    assert _sessions(plain, fx2, 12) == 0 and n_lat > 0


def test_cheap_solo_housing_lowers_the_weekly_cost_of_living_alone_only():
    w, _ = _world(apart=True, solo_cost=1.125)
    assert w.solo_cost() == 1.125
    w2, _ = _world(apart=True)
    assert w2.solo_cost() == 1.5


def test_prenup_exit_term_reaches_a_forecast_without_any_exit():
    """Even with no exit in any sampled future, the exit term moves the forecast: the freedom probe reads what a member could carry
    out (exit_retained), and that feeds autonomy. So hybrid.score_options scores every exit term."""
    from mar import exit_fallback as EF
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import retest as RT
    vals = {}
    with EF.use_exit_fallback("F5", strip_split=True):
        w, fx = _world()
        with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
            x0 = HY.STATS.get("future_exits", 0)
            for t in HY.PRENUP_TERMS:
                vals[t] = HY.forecast(w, 0, {"busy": {"A": False, "B": False}}, 20, edit=lambda c, t=t: HY.set_agreement(c, f"income|{t}"))
            exits = HY.STATS.get("future_exits", 0) - x0
    assert exits == 0
    assert vals["forfeit"]["A"] < vals["equal_split"]["A"] and vals["forfeit"]["B"] < vals["equal_split"]["B"]


def test_set_agreement_reads_the_prenup_term_after_the_bar():
    from mar import hybrid as HY
    w, _ = _world()
    HY.set_agreement(w, "equal|forfeit")
    assert w.agree["term"] == "equal" and w.prenup_exit == "forfeit"


def test_choose_term_is_unchanged_for_the_bill_terms_and_takes_lat():
    from mar import hybrid as HY
    O = {"A": 0.80, "B": 0.80}
    V = {"income": {"A": 0.82, "B": 0.81}, "equal": {"A": 0.81, "B": 0.81}}
    assert HY.choose_term(V, O) == ("income", True)
    V["lat"] = {"A": 0.83, "B": 0.82}
    assert HY.choose_term(V, O) == ("lat", True)
    assert HY.choose_term({"income": {"A": 0.79, "B": 0.9}, "equal": {"A": 0.78, "B": 0.9}}, O)[1] is False


# ---- the exact side model ----------------------------------------------------------------------------------------------------

def test_exact_extension_reproduces_h38_with_no_aids():
    from mar import h38_exact as X
    from mar import h41_exact as Y
    for ch in (X.CORRECTED, X.PLANNER, X.OLD_RULE):
        for pr in (X.FREE, X.dial(4)):
            for kind in ("cap", "sat"):
                a, b = X.solve(X.World(), pr, ch, kind, (0.0, 1.0)), Y.solve(X.World(), pr, ch, kind, (0.0, 1.0))
                assert all(abs(a[k] - b[k]) < 1e-12 for k in X.METRICS)


def test_exact_known_answers_for_the_aids():
    from mar import h38_exact as X
    from mar import h41_exact as Y
    wd = X.World()
    # an exit cost keeps the planner out of some households; removing it raises time together and removes held_cost
    base = Y.population(wd, Y.FREE, X.PLANNER, "sat", Y.BASE)
    cheap = Y.population(wd, Y.FREE, X.PLANNER, "sat", Y.ARMS["cheap exit (no exit cost)"])
    assert cheap["together"] > base["together"] and cheap["held_cost"] == 0.0 and base["held_cost"] > 0.0
    # cheaper solo housing makes living apart better, so everyone pairs less
    for ch in (X.CORRECTED, X.PLANNER):
        assert Y.population(wd, Y.FREE, ch, "sat", Y.ARMS["cheap solo housing"])["together"] < \
            Y.population(wd, Y.FREE, ch, "sat", Y.BASE)["together"]
    # a trial ends some households at its end, and with no pressure held (by pressure) stays 0
    tr = Y.population(wd, Y.FREE, X.CORRECTED, "sat", Y.ARMS["trial"])
    assert tr["trial_ends"] > 0 and tr["held"] == 0.0
