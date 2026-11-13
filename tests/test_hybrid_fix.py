"""The hybrid's Amendment 3 (docs/results/hybrid-agent-prereg.md): the suffering weight in big choices (FixConfig.hybrid_w) and readings
run by the world (FixConfig.hybrid_readings). Both off by default."""
import dataclasses
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))


def _rows(pl, s_off, s_non, n=10):
    return [{"hedonic": {r: {"pleasure": pl, "s_off": s_off, "s_non": s_non} for r in "AB"}} for _ in range(n)]


def _fx(**kw):
    from mar import hedonic as HD
    return dataclasses.replace(HD.FixConfig(), agent_values="hybrid", **kw)


def test_w_zero_is_the_flag_off_and_w_subtracts_both_kinds_of_suffering():
    from mar import hybrid as HY
    rows = _rows(0.83, 0.07, 0.11)
    off = HY.score(rows, "A", None, _fx())
    assert abs(off - 0.83) < 1e-12
    assert HY.score(rows, "A", None, _fx(hybrid_w=0.0)) == off
    assert abs(HY.score(rows, "A", None, _fx(hybrid_w=1.0)) - (0.83 - 0.18)) < 1e-12
    assert abs(HY.score(rows, "A", None, _fx(hybrid_w=2.5)) - (0.83 - 2.5 * 0.18)) < 1e-12


def test_known_answer_high_w_declines_a_household_with_more_suffering_and_slightly_more_pleasure():
    """KW: the household gives 0.02 a week more pleasure and 0.10 a week more suffering than the outside option."""
    from mar import hybrid as HY
    home, out = _rows(0.90, 0.15, 0.05), _rows(0.88, 0.10, 0.00)
    for w, forms in ((2.0, False), (0.0, True), (None, True)):
        fx = _fx(hybrid_w=w)
        V = {t: {r: HY.score(home, r, None, fx) for r in "AB"} for t in HY.TERMS}
        O = {r: HY.score(out, r, None, fx) for r in "AB"}
        assert HY.choose_term(V, O)[1] is forms, w


def test_persona_weight_is_h39s_draw_and_a_high_w_persona_declines():
    from mar import hybrid as HY
    from mar import makers as MK
    from mar import retest as RT
    ps = RT.personas()
    ws = {pid: MK.suffering_weight(p) for pid, p in ps.items()}
    assert all(0.0 <= w <= 4.0 for w in ws.values()) and min(ws.values()) < 0.7 < 1.4 < max(ws.values())
    hi = max(ws, key=ws.get)
    fx = _fx(hybrid_w="persona")
    assert HY.weight(ps[hi], fx) == ws[hi]
    home, out = _rows(0.90, 0.15, 0.05), _rows(0.88, 0.10, 0.00)
    assert HY.score(home, "A", ps[hi], fx) < HY.score(out, "A", ps[hi], fx)       # w > 0.2 declines this household
    assert HY.score(home, "A", ps[hi], _fx()) > HY.score(out, "A", ps[hi], _fx())


def _trap_world(weeks=30, **kw):
    import formation_check_3 as FC3
    import stay_test_run as STR
    from mar import hedonic as HD
    from mar import pairing as PR
    from mar import retest as RT
    from mar.worlds import household as H
    ps = STR.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **FC3.rule("hybrid"), **kw)
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        return H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), (ps["p-anchor"], ps["p-host"]), 900, weeks), fx


def _play(world, fx, weeks):
    from mar import hedonic as HD
    from mar import retest as RT
    last = {"busy": {"A": False, "B": False}}
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        for w in range(weeks):
            last = {"busy": world.step_week(w, last)}


def test_world_runs_the_13_week_reading_only_without_a_harness_and_never_inside_a_forecast(monkeypatch):
    from mar import hybrid as HY
    from mar import negotiation as NG
    calls = []
    monkeypatch.setattr(NG.BaselineLived, "reading", lambda self, w, last: calls.append((w, HY.lived(self.world))))
    for mode, harness, want in (("harness", False, []), ("world", False, [13]), ("world", True, [])):
        calls.clear()
        world, fx = _trap_world(hybrid_readings=mode)
        if harness:
            world.harness = True
        _play(world, fx, 14)
        assert [w for w, _ in calls if w % 13 == 0] == want, (mode, harness)
        assert all(ok for _, ok in calls)
    world, fx = _trap_world(hybrid_readings="world")
    c = HY.copy_world(world)
    assert not HY.lived(c)
    calls.clear()
    _play(c, fx, 14)
    assert calls == []


@pytest.mark.slow
def test_flag_off_reproduces_fingerprints_pinned_before_the_change():
    import h41_fingerprint as F
    pinned = json.loads((ROOT / "tests" / "data" / "h41_off_fingerprints.json").read_text())
    assert F.fingerprints() == pinned


@pytest.mark.slow
def test_world_readings_change_nothing_under_the_harness():
    """Under BaselineLived the harness runs every hybrid reading, so hybrid_readings='world' leaves the formation check's lives as pinned."""
    import agent_values_fingerprint as AF
    import h41_fingerprint as F
    pinned = json.loads((ROOT / "tests" / "data" / "h41_off_fingerprints.json").read_text())
    fp = AF.formation_fps({**F.STEP3, **F.SETS["hybrid"], "hybrid_readings": "world"})
    assert {f"hybrid:{k}": v for k, v in fp.items()} == {k: v for k, v in pinned.items() if k.startswith("hybrid:FC")}
