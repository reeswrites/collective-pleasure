"""Fingerprints for the agent recalibration switch's reproduction test (docs/results/agent-recalibration-prereg.md).
Pinned in tests/data/agent_values_off_fingerprints.json from a clean checkout (commit 36a6460) BEFORE the switch existed. With
FixConfig(agent_values="v1", bills_hurt=False), the defaults, these must reproduce exactly: H39b's opportunity-choice arms, the H38
formation check's corrected-rule arms, and one value-consistency decision record."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

CELLS = (("p-anchor", "p-host", 0), ("g-00000", "g-11111", 1), ("g-01010", "p-wanderer", 2), ("p-bargainer", "p-steward", 3))
WEEKS = 60


def _fp(run):
    rows = [[o["both_in"]] + [[o["hedonic"][r][k] for k in ("pleasure", "s_off", "s_non")] for r in "AB"] for o in run.outcomes]
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:16]


def h39b_fps(extra=None):
    """H39b arms Z, BP and M0 (opportunity choice, enjoyment -1/0/+1, the weighted rule). extra: FixConfig overrides (the switch)."""
    import h38_pairing_run as H38
    import h39_makers_run as H39
    from mar import makers as MK
    from mar import pairing as PR
    ovr = {"choice": "opportunity", "enjoy": MK.ENJOY_H39B}
    out = {}
    for arm in ("Z", "BP", "M0"):
        cfg, rule = H39.arm_setup(arm, ovr)
        for a, b, s in CELLS:
            with MK.use_makers(cfg):
                run, _, _ = H38.play(PR.dial(0), a, b, s, stay=False, weeks=WEEKS, rule={**rule, **(extra or {})})
            out[f"H39b:{arm}:{a}:{b}:{s}"] = _fp(run)
    return out


def formation_fps(extra=None):
    """The formation check's corrected-rule arms G-L0 and G-L4 (stay readings on)."""
    import h38_pairing_run as H38
    from mar import pairing as PR
    rule = {"decide_on": "pleasure", "decide_weeks": 52, **(extra or {})}
    out = {}
    for name, pc in (("G-L0", PR.dial(0)), ("G-L4", PR.dial(4))):
        for a, b, s in CELLS[:3]:
            run, _, _ = H38.play(pc, a, b, s, stay=True, weeks=WEEKS, rule=rule)
            out[f"FC:{name}:{a}:{b}:{s}"] = _fp(run)
    return out


def valuecheck_fp(extra=None):
    """One sampled decision of the value-consistency check (M0 world, week 9, partner A, last call, 13-week horizon)."""
    import value_consistency as VCS
    from mar import exit_fallback as EF
    from mar import exit_items as EI
    from mar import hedonic as HD
    from mar import negotiation as NG
    from mar import retest as RT
    from mar import valuecheck as VC
    from mar.worlds import household as H
    import dataclasses
    import h38_pairing_run as H38
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    fx = dataclasses.replace(VCS._ctx(), **(extra or {}))
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[H38.CELL]):
        lived = NG.BaselineLived(ps["p-anchor"], ps["p-host"], 0, H.load_variant("baseline"), weeks=H.WEEKS, decline=True)
        world = lived.world
        last = {"busy": {"A": False, "B": False}}
        for w in range(9):
            last = {"busy": world.step_week(w, last)}
        rec = VC.measure_decision(VC.snapshot(world), dict(last), 9, "A", 2, horizons=(1, 13))
    return {"VC:p-anchor:p-host:0:w9:A": hashlib.sha256(json.dumps(rec, sort_keys=True, default=str).encode()).hexdigest()[:16]}


def fingerprints(extra=None):
    return {**h39b_fps(extra), **formation_fps(extra), **valuecheck_fp(extra)}


if __name__ == "__main__":
    print(json.dumps(fingerprints(), indent=1))
