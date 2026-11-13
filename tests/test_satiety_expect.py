"""Time together valued at the world's satiety (docs/results/hybrid-agent-prereg.md, Amendment 2; FixConfig.satiety_expect)."""
import copy
import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

SAT = {"pleasure_scale": "sat"}
PINS = {"v1+sat": SAT, "v2+bills+sat": {"agent_values": "v2", "bills_hurt": True, **SAT},
        "v2b+bills+sat": {"agent_values": "v2b", "bills_hurt": True, **SAT},
        "hybrid+bills+sat": {"agent_values": "hybrid", "bills_hurt": True, **SAT}}


def test_flag_off_reproduces_fingerprints_pinned_before_the_change():
    """Pinned at commit b3e9fc0, before the flag existed: with satiety_expect "persona" (the default) nothing moves on the new scale."""
    import agent_values_fingerprint as AF
    pinned = json.loads((ROOT / "tests" / "data" / "satiety_off_fingerprints.json").read_text())
    for name, extra in PINS.items():
        fp = {**AF.formation_fps(extra), **AF.valuecheck_fp(extra)}
        if name != "hybrid+bills+sat":
            fp.update(AF.h39b_fps(extra))
        assert fp == pinned[name], name


def _world(**kw):
    from mar import hedonic as HD
    from mar import pairing as PR
    from mar import retest as RT
    from mar.worlds import household as H
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), agent_values="v2", bills_hurt=True, pleasure_scale="sat", **kw)
    ps = RT.personas()
    with HD.use_levers(RT.LEVERS):
        return H.WeeklyWorld(H.load_variant("baseline"), (ps["p-anchor"], ps["p-host"]), 0, 40, fixes=fx)


def _observed(world, weeks):
    """Step the world, keeping a deep copy of the world and A's observation at every call where time together is on the menu."""
    seen = []
    orig = world.obs

    def spy(r, w, last):
        o = orig(r, w, last)
        if r == "A" and o.get("partner_accepts") and o["in_hh"] and o["other_in"] and "lever" in o:
            seen.append((copy.deepcopy(world), o))
        return o
    world.obs = spy
    last = {"busy": {"A": False, "B": False}}
    for w in range(weeks):
        last = {"busy": world.step_week(w, last)}
    world.obs = orig
    return seen


def test_together_next_is_the_scale_the_world_gives_the_next_session():
    """Known answer: the observed together_next equals what the world records for a session played at that call."""
    seen = _observed(_world(satiety_expect="world"), 20)
    assert len(seen) >= 5
    scales = set()
    for c, o in seen:
        exp = o["lever"]["together_next"]
        c._lever_session("adhoc_agent")
        assert abs(c.lw["tog"][-1] - exp) < 1e-12
        scales.add(round(exp, 6))
    assert len(scales) >= 3 and min(scales) < 0.9          # satiety does bite in this life


def test_world_flag_values_one_session_at_the_world_scale_and_persona_flag_is_the_old_rule():
    """The own term of time together is the close's change with one session at together_next (world) or at 1 / the adaptive persona's
    own scale (persona, ADR 0016). Noise off."""
    from mar import agent_values as AV
    for mode in ("world", "persona"):
        seen = _observed(_world(satiety_expect=mode), 14)
        assert seen
        for c, o in seen[:6]:
            ag = c.agents["A"]
            ag._noise = lambda: 1.0
            parts = {}
            AV.utilities(ag, o, parts)
            lev = o["lever"]
            if mode == "world":
                ts = lev["together_next"]
            else:
                assert "together_next" not in lev
                ts = lev["together_scale"] if lev["adaptive"] else 1.0
            fs = lev["friend_scale"] if lev["adaptive"] else 1.0
            s = o["v2"]
            want = AV.week_net(AV.advance(s, together=1, scale=(fs, ts))) - AV.week_net(s)
            assert abs(parts["together"]["own_week"] - round(want, 6)) < 2e-6


def test_v1_does_not_read_the_flag():
    """v1's heuristics: the same life with the flag on or off."""
    import h38_pairing_run as H38
    from mar import pairing as PR
    outs = []
    for mode in ("persona", "world"):
        run, _, _ = H38.play(PR.dial(4), "p-anchor", "p-host", 0, stay=True, weeks=40,
                             rule={"decide_on": "pleasure", "decide_weeks": 52, "bills_hurt": True, "pleasure_scale": "sat",
                                   "satiety_expect": mode})
        outs.append([[o["hedonic"][r]["pleasure"] for r in "AB"] for o in run.outcomes])
    assert outs[0] == outs[1]
