"""Fingerprints for the observer layer (docs/notes/observer-schema.md). Pinned in tests/data/observer_off_fingerprints.json BEFORE the
observer existed. Four families, small and fast: H38 pairing norms (L0, L4), exit fallbacks slice 2 (items on; F0, F4, F5), the seed v2
retest (BASE-F, V23-F) and household evolution (score_runs on a small validation context).

fingerprints(observe=None) runs them as they are. fingerprints(observe=cfg) runs the same cases inside `observe.use_observer(cfg)`, so
every world built (the lived world and every rollout world) carries an observer; the digests must not move."""
import contextlib
import dataclasses
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from mar import exit_fallback as EF  # noqa: E402
from mar import exit_items as EI  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar import world_api as W  # noqa: E402
from mar.cards import load_cards  # noqa: E402
from mar.worlds import household as H  # noqa: E402

H38_PAIRS = (("p-anchor", "p-host", 0), ("g-00000", "g-11111", 1))
H38_WEEKS = H.WEEKS
EF_ARMS = ("F0", "F4", "F5")
EF_RUNS = (0, 1)
V2_CELLS = (("BASE-F", "p-anchor", "p-wanderer", 0), ("V23-F", "p-bargainer", "p-steward", 1))
EVOLVE_SPECS = ("author_seed_v2_bindable", "baseline")


def _clear():
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()


def digest(run, world=None):
    blob = {"o": run.outcomes, "t": run.trace, "f": run.final, "m": run.meta}
    if world is not None:
        blob["x"] = world.exit_log
        blob["p"] = world.pool
    return hashlib.sha256(json.dumps(blob, sort_keys=True, default=str).encode()).hexdigest()[:20]


def h38_fps():
    out = {}
    ps = RT.personas()
    for arm, lv in (("L0", 0), ("L4", 4)):
        for a, b, s in H38_PAIRS:
            _clear()
            fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(lv))
            with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), \
                    EI.use_items(EI.GRID["V2-split-loves"]):
                lived = NG.BaselineLived(ps[a], ps[b], s, H.load_variant("baseline"), weeks=H38_WEEKS, decline=True)
                out[f"h38|{arm}|{a}|{b}|{s}"] = digest(lived.play(), lived.world)
    return out


def ef_fps():
    import exit_fallbacks_run as X
    out = {}
    ctx = X.ctx("val")
    for arm in EF_ARMS:
        with EF.use_exit_fallback(arm, strip_split=True), EI.use_items(EI.GRID["V2-split-loves"]):
            gate = H.PyGate(load_cards(str(H.RULES / "author_seed_v2_bindable")))
            for i in EF_RUNS:
                _clear()
                res = X.play_items(gate, ctx.runs[i])
                out[f"ef|{arm}|{i}"] = hashlib.sha256(json.dumps(res, sort_keys=True, default=str).encode()).hexdigest()[:20]
    return out


def v2_fps():
    out = {}
    for arm, a, b, s in V2_CELLS:
        run, _lived, world = RT.play_cell(arm, a, b, s)
        out[f"v2|{arm}|{a}|{b}|{s}"] = digest(run, world)
    return out


def evolve_fps():
    out = {}
    w = W.HouseholdEvolveWorld()
    ctx = W.make_context(777, 0, 2, split="val", tag="val")
    for name in EVOLVE_SPECS:
        sc, ev = w.score_runs(w.load_spec(name), ctx)
        out[f"evolve|{name}"] = hashlib.sha256(json.dumps([sc, ev], sort_keys=True, default=str).encode()).hexdigest()[:20]
    return out


def fingerprints(observe=None):
    if observe is None:
        cm = contextlib.nullcontext()
    else:
        from mar import observe as OB
        cm = OB.use_observer(observe)
    with cm:
        return {**h38_fps(), **ef_fps(), **v2_fps(), **evolve_fps()}


if __name__ == "__main__":
    print(json.dumps(fingerprints(), indent=1, sort_keys=True))
