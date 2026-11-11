"""Fingerprints of retest-harness runs (fixes on) and exit-fallback runs (F4, items), for the H38 pairing switch's reproduction test.
Pinned in tests/data/h38_pairing_off_fingerprints.json BEFORE the pairing switch existed."""
import hashlib
import json

from mar import exit_fallback as EF
from mar import exit_items as EI
from mar import hedonic as HD
from mar import negotiation as NG
from mar import retest as RT
from mar.worlds import household as H

CELLS = (("BASE-F", "p-anchor", "p-host", 0), ("BASE-F", "g-00000", "g-11111", 1), ("V22-F", "p-anchor", "p-wanderer", 0),
         ("V23-F", "p-bargainer", "p-steward", 1))
WEEKS = 60


def _fp(run):
    rows = [[o["both_in"]] + [[o["hedonic"][r][k] for k in ("pleasure", "s_off", "s_non")] for r in "AB"] for o in run.outcomes]
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:16]


def retest_fps():
    out = {}
    for arm, a, b, s in CELLS:
        run, _, _ = RT.play_cell(arm, a, b, s)
        out[f"{arm}:{a}:{b}:{s}"] = _fp(run)
    return out


def f4_items_fps():
    """BaselineLived with fixes on, under F4 (strip_split) and items V2: the H38 world with the pairing switch off."""
    out = {}
    ps = RT.personas()
    for a, b, s in (("p-anchor", "p-host", 0), ("g-00000", "g-11111", 1), ("g-01010", "p-wanderer", 2)):
        for c in (NG._RC, NG._PC, NG._BC):
            c.clear()
        with HD.use_levers(RT.LEVERS), HD.use_fixes(RT.FIXES_ON), EF.use_exit_fallback("F4", strip_split=True), \
                EI.use_items(EI.GRID["V2-split-loves"]):
            lived = NG.BaselineLived(ps[a], ps[b], s, H.load_variant("baseline"), weeks=WEEKS, decline=True)
            out[f"F4V2:{a}:{b}:{s}"] = _fp(lived.play())
    return out


def fingerprints():
    return {**retest_fps(), **f4_items_fps()}


if __name__ == "__main__":
    print(json.dumps(fingerprints(), indent=1))
