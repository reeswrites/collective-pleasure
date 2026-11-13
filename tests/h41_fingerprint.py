"""Fingerprints pinned before the hybrid fixes (hybrid-agent-prereg.md, Amendment 3) and the H41 choice aids (h41-choice-aids-prereg.md).
Pinned in tests/data/h41_off_fingerprints.json at commit 660a34d, before either change existed. With every new flag at its default
these must reproduce exactly: the formation check's arms under the step-3 world for all four agent sets, and the stay test's trap and
baseline fixtures under the hybrid."""
import dataclasses
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

STEP3 = {"decide_on": "pleasure", "decide_weeks": 52, "bills_hurt": True, "pleasure_scale": "sat", "satiety_expect": "world"}
SETS = {"v1": {}, "v2": {"agent_values": "v2"}, "v2b": {"agent_values": "v2b"}, "hybrid": {"agent_values": "hybrid"}}
TRAP_CELL = ("p-anchor", "p-host", 900)
TRAP_WEEKS = 40


def _fp(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def formation(extra=None):
    """The formation check's G-L0 and G-L4 (stay readings on, 60 weeks, 3 cells) under each agent set in the step-3 world."""
    import agent_values_fingerprint as AF
    out = {}
    for name, s in SETS.items():
        fps = AF.formation_fps({**STEP3, **s, **(extra or {})})
        out.update({f"{name}:{k}": v for k, v in fps.items()})
    return out


def trap(extra=None):
    """The stay test's trap (T1-forfeit, imposed, no harness) and its baseline fixture under the hybrid, one pairing, 40 weeks."""
    import stay_test_run as STR
    from mar import hedonic as HD
    from mar import pairing as PR
    from mar import retest as RT
    from mar import stay_test as ST
    from mar.worlds import household as H
    ps = STR.personas()
    a, b, seed = TRAP_CELL
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **{**STEP3, **SETS["hybrid"], **(extra or {})})
    out = {}
    for arm in ("trap", "baseline"):
        with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
            world = H.WeeklyWorld(H.PyGate(H.load_variant(arm)), (ps[a], ps[b]), seed, TRAP_WEEKS)
            run, weeks = ST.play_with_stay_test(world, bar=False)
        rows = [[o["both_in"]] + [[o["hedonic"][r][k] for k in ("pleasure", "s_off", "s_non")] for r in "AB"] for o in run.outcomes]
        out[f"trap:{arm}:{a}:{b}:{seed}"] = _fp([rows, STR.compact(weeks)["held"]])
    return out


def fingerprints(extra=None):
    return {**formation(extra), **trap(extra)}


if __name__ == "__main__":
    print(json.dumps(fingerprints(), indent=1))
