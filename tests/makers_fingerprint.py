"""Fingerprints for the H39 makers switch's reproduction test (docs/results/h39-makers-prereg.md).
Pinned in tests/data/makers_off_fingerprints.json from a clean checkout BEFORE any makers hook existed. With makers off (the default)
the H38 world (F4, items V2, pairing dial 0) must reproduce these exactly under the old rule and the corrected rule, and the
retest / F4-items cells of tests/h38_fingerprint.py must too."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

CELLS = (("p-anchor", "p-host", 0), ("g-00000", "g-11111", 1), ("g-01010", "p-wanderer", 2), ("p-bargainer", "p-steward", 3))
RULES = {"old": None, "good": {"decide_on": "pleasure", "decide_weeks": 52}}
WEEKS = 60


def _fp(run):
    rows = [[o["both_in"]] + [[o["hedonic"][r][k] for k in ("pleasure", "s_off", "s_non")] for r in "AB"] for o in run.outcomes]
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:16]


def h38_world_fps():
    import h38_pairing_run as H38
    from mar import pairing as PR
    out = {}
    for name, rule in RULES.items():
        for a, b, s in CELLS:
            run, _, _ = H38.play(PR.dial(0), a, b, s, stay=False, weeks=WEEKS, rule=rule)
            out[f"H38:{name}:{a}:{b}:{s}"] = _fp(run)
    return out


def fingerprints():
    import h38_fingerprint as HF
    return {**h38_world_fps(), **HF.f4_items_fps()}


if __name__ == "__main__":
    print(json.dumps(fingerprints(), indent=1))
