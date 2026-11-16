"""KG1, KG2, KG3 and KW under TT2 (docs/results/tt2-prereg.md): a LAT member may give its partner money by the existing `give` action
(GIVE = 3, the seed v2 gift policy, the hybrid's fork value); nowhere else; forecasts do not see it. Each check asserts the flag-off
behaviour first."""
import copy
import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

from test_time_together import A6, LAST, _fresh_week, _world  # noqa: E402

TT2 = {"together_bg": 3.3, "lat_bg_keep": 0.2, "lat_travel": 0.33, "together_subst": True, "h41_lat": True}


def _lat(gifts, pair=("p-anchor", "p-host"), a_money=0, b_money=30):
    from mar import hybrid as HY
    w, fx = _world(pair=pair, **TT2, lat_gifts=gifts)
    HY.make_lat(w, {"A": "friend", "B": "friend"})
    _fresh_week(w)
    w.p["A"]["money"], w.p["B"]["money"] = a_money, b_money
    assert w.lat_on()
    return w, fx


def _menu(w, fx, r):
    from mar import hedonic as HD
    from mar import retest as RT
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        o = w.obs(r, 0, dict(LAST))
        return [c for _, c in w.agents[r].propose(o)]


def _gives(menu):
    return [c for c in menu if c["a"] == "give" and c.get("kind") == "partner"]


def test_off_by_default():
    from mar import hedonic as HD
    assert HD.FixConfig().lat_gifts is False


def test_kg1_flag_off_no_gift_under_lat():
    w, fx = _lat(False)
    assert not w.feasible("B", "give", "partner")
    assert not _gives(_menu(w, fx, "B"))


def test_kg1_flag_on_gift_under_lat():
    from mar.worlds import household as H
    w, fx = _lat(True)
    assert w.agents["B"].prosocial >= 0.5
    assert w.feasible("B", "give", "partner")
    assert len(_gives(_menu(w, fx, "B"))) == 1
    # the policy: partner < 4 and own >= 8
    for a_m, b_m, want in ((3, 8, True), (4, 30, False), (0, 7, False)):
        w2, fx2 = _lat(True, a_money=a_m, b_money=b_m)
        assert bool(_gives(_menu(w2, fx2, "B"))) is want, (a_m, b_m)
    # feasibility: at least GIVE + 1
    w3, _ = _lat(True, b_money=3)
    assert not w3.feasible("B", "give", "partner")
    # executing it moves exactly 3, total money unchanged, one time unit
    tot = w.p["A"]["money"] + w.p["B"]["money"]
    u = w.units["B"]
    w._apply("B", {"a": "give", "kind": "partner"}, 0, [])
    assert w.p["A"]["money"] == 3 and w.p["B"]["money"] == 27 and w.p["A"]["money"] + w.p["B"]["money"] == tot
    assert w.units["B"] == u - H.V2_COST["give"]


def test_kg1_low_prosocial_does_not_propose():
    w, fx = _lat(True, pair=("p-host", "p-bargainer"))
    assert w.agents["B"].prosocial < 0.5
    assert w.feasible("B", "give", "partner")          # feasible, but the policy never proposes it
    assert not _gives(_menu(w, fx, "B"))


def test_kg2_only_under_lat():
    # apart but not LAT
    w, fx = _lat(True)
    w.lat = False
    assert not w.lat_on() and not w.feasible("B", "give", "partner")
    assert not _gives(_menu(w, fx, "B"))
    # both in the household: the old rule (needs mech, which the baseline cards lack)
    h, fxh = _world(**TT2, lat_gifts=True)
    _fresh_week(h)
    h.p["A"]["money"], h.p["B"]["money"] = 0, 30
    assert h.p["A"]["in"] and h.p["B"]["in"] and not h.mech
    assert h.feasible("B", "give", "partner")          # as before the flag: both in
    assert not _gives(_menu(h, fxh, "B"))               # not proposed (no seed v2 aim), as before


def test_kg3_forecasts_do_not_see_gifts():
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import retest as RT
    vals = {}
    for g in (False, True):
        w, fx = _lat(g)
        w.p["A"]["jobless"] = 20
        with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
            vals[g] = HY.forecast(copy.deepcopy(w), 0, dict(LAST), 13)
    assert vals[False] == vals[True]


def test_kw_rerun_with_tt2_flags_on():
    from mar import hedonic as HD
    from mar import hybrid as HY

    def rows(pl, s_off, s_non, n=10):
        return [{"hedonic": {r: {"pleasure": pl, "s_off": s_off, "s_non": s_non} for r in "AB"}} for _ in range(n)]
    home, out = rows(0.90, 0.15, 0.05), rows(0.88, 0.10, 0.00)
    for w, forms in ((2.0, False), (0.0, True), (None, True)):
        fx = dataclasses.replace(HD.FixConfig(), agent_values="hybrid", **{**A6, "hybrid_w": w}, **TT2, lat_gifts=True)
        V = {t: {r: HY.score(home, r, None, fx) for r in "AB"} for t in HY.TERMS}
        O = {r: HY.score(out, r, None, fx) for r in "AB"}
        assert HY.choose_term(V, O)[1] is forms, w
