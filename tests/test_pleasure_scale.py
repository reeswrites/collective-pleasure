"""The saturating pleasure scale (docs/decisions/0019-saturating-pleasure-scale.md)."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))

PINS = ("v1", None), ("v2", {"agent_values": "v2"}), ("v2+bills", {"agent_values": "v2", "bills_hurt": True}), \
    ("v2b+bills", {"agent_values": "v2b", "bills_hurt": True})


def test_scale_off_reproduces_fingerprints_pinned_before_the_flag():
    """Pinned at commit ae80dad, before the flag existed: with pleasure_scale "clip" (the default), v1, v2 and v2b do not move."""
    import agent_values_fingerprint as AF
    pinned = json.loads((ROOT / "tests" / "data" / "scale_off_fingerprints.json").read_text())
    for name, extra in PINS:
        assert AF.fingerprints(extra) == pinned[name], name


def test_the_curve_known_answers():
    from mar import hedonic as HD
    k = 0.8
    assert HD.saturate(-0.3, k) == 0.0 and HD.saturate(0.5, k) == 0.5 and HD.saturate(0.8, k) == 0.8
    assert abs(HD.saturate(1.0, k) - (0.8 + 0.2 * (1 - math.exp(-1)))) < 1e-12          # 0.926
    assert abs(HD.saturate(0.9, k) - 0.8787) < 1e-4 and abs(HD.saturate(1.2, k) - 0.9729) < 1e-4
    eps = 1e-7                                                                            # slope 1 at the knee, from both sides
    assert abs((HD.saturate(k + eps, k) - HD.saturate(k, k)) / eps - 1.0) < 1e-5
    xs = [0.8 + 0.05 * i for i in range(40)]
    ys = [HD.saturate(x, k) for x in xs]
    assert all(b > a for a, b in zip(ys, ys[1:])) and ys[-1] < 1.0                        # rises, ever more slowly, toward 1
    assert all((c - b) < (b - a) for a, b, c in zip(ys, ys[1:], ys[2:]))
    assert HD.pleasure_of(1.3, None) == 1.0 and HD.pleasure_of(-0.1, None) == 0.0


def _close(knee, extra):
    from mar import hedonic as HD
    from mar import retest as RT
    h = HD.Hedonic(RT.personas()["p-anchor"])
    h.knee = knee
    h.level = {n: 1.0 for n in HD.NEEDS}
    full = {k: h.targets[k] for k in h.targets}                     # every aspiration met: raw = 1.0 before extra
    return h, h.close_week(full, extra_pleasure=extra, report_raw=True)


def test_the_close_reads_the_curve_and_keeps_the_old_line():
    """With every need and aspiration met, raw pleasure is 1.0 plus extra. A person with 0.10 of surplus (say, a pairing reward) who
    then bears a 0.05 cost (say, a stigma): the clip reads 1.0 both ways, so the cost is free; the curve reads the surplus and the cost."""
    _, r0 = _close(None, 0.10)
    _, rc = _close(None, 0.05)
    assert r0["pleasure"] == rc["pleasure"] == 1.0 and "p_clip" not in r0
    h, s0 = _close(0.8, 0.0)
    _, sg = _close(0.8, 0.10)
    _, sc = _close(0.8, 0.05)
    assert abs(s0["pleasure"] - 0.9264) < 1e-4 and s0["p_clip"] == 1.0
    assert sg["pleasure"] > sc["pleasure"] > s0["pleasure"]
    assert sg["p_clip"] == sc["p_clip"] == 1.0                       # the old line beside it: the cost is invisible there
    h2, _ = _close(None, 0.0)
    assert h.B < h2.B                                                # the spiral moves on the transformed number (0.926 < 1.0)


def test_flag_sets_the_knee_only_when_on():
    import dataclasses
    from mar import hedonic as HD
    from mar import retest as RT
    from mar.worlds import household as H
    ps = RT.personas()
    for scale, want in (("clip", None), ("sat", 0.8)):
        fx = dataclasses.replace(RT.FIXES_ON, pleasure_scale=scale)
        with HD.use_levers(RT.LEVERS):
            w = H.WeeklyWorld(H.load_variant("baseline"), (ps["p-anchor"], ps["p-host"]), 0, 10, fixes=fx)
        assert w.hed["A"].knee == want and w.hed["B"].knee == want


def test_v2_value_is_the_close_change_on_the_new_scale():
    """Known answer, as test_agent_values does it on the clip: at the very last call of a week an action's v2 own value equals the change
    in B's own net that week, now with the curve in the close and in the agent's arithmetic."""
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
    fx = dataclasses.replace(VCS._ctx(), agent_values="v2", bills_hurt=True, pleasure_scale="sat")
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[H38.CELL]):
        lived = NG.BaselineLived(ps["g-00000"], ps["p-host"], 0, H.load_variant("baseline"), weeks=H.WEEKS, decline=True)
        world, last = lived.world, {"busy": {"A": False, "B": False}}
        assert world.hed["B"].knee == 0.8
        for w in range(12):
            if w in (3, 7, 11):
                rec = VC.measure_decision(VC.snapshot(world), dict(last), w, "B", 2, horizons=(1,))
                for it in (rec or {"items": []})["items"]:
                    if it["applied"] and it["a"] != "together":
                        assert abs(it["actual"][1]["own"]["net"] - it["perceived"]) < 3e-4, it
                        n += 1
            last = {"busy": world.step_week(w, last)}
    assert n >= 8
