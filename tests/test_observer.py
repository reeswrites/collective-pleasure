"""Observer layer (src/mar/observe.py; docs/notes/observer-schema.md): off by default and bit-identical when off; with an observer on
every world (replays included) the runs are still bit-identical; the recorded parts add up to the numbers the model used."""
import copy
import dataclasses
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import observer_fingerprint as F  # noqa: E402
from mar import exit_fallback as EF  # noqa: E402
from mar import exit_items as EI  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import observe as OB  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar.worlds import household as H  # noqa: E402

PINNED = json.loads((Path(__file__).parent / "data" / "observer_off_fingerprints.json").read_text())


def _h38(level=4, a="g-00000", b="g-11111", seed=1, weeks=60, cfg=None):
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(level))
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), \
            EI.use_items(EI.GRID["V2-split-loves"]), OB.collecting():
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=weeks, decline=True)
        ob = OB.Observer(lived.world, cfg or OB.ObsConfig(replay_rate=0.2, replay_window=6), harness=lived)
        run = lived.play()
        ob.finish()
    return run, lived, ob


# ---- off, and bit-identical ------------------------------------------------------------------------------------------------

def test_off_by_default():
    ps = RT.personas()
    w = H.WeeklyWorld(H.load_variant("baseline"), (ps["p-anchor"], ps["p-host"]), 0, 4)
    assert w.observer is None and w._force is None and OB.ACTIVE is None
    assert not w.hed["A"].parts_on and not HD.PARTS


def test_off_reproduces_pinned_runs():
    assert F.fingerprints() == PINNED


def test_on_reproduces_pinned_runs():
    """Every world built (the lived world, every rollout world) carries an observer with swap, stay and pressure-off replays."""
    assert F.fingerprints(OB.ObsConfig(replay_rate=0.25, replay_window=4)) == PINNED


def test_explicit_attach_changes_no_outcome():
    run_on, _, ob = _h38()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    ps = RT.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(4))
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), \
            EI.use_items(EI.GRID["V2-split-loves"]):
        run_off = NG.BaselineLived(ps["g-00000"], ps["g-11111"], 1, H.load_variant("baseline"), weeks=60, decline=True).play()
    assert F.digest(run_on) == F.digest(run_off)
    assert any(r["t"] == "replay" for r in ob.rows)


def test_deep_copy_drops_the_observer():
    _, lived, ob = _h38(weeks=3)
    c = copy.deepcopy(lived.world)
    assert c.observer is None and c.agents["A"]._obs is None
    assert lived.world.observer is ob and c.hed["A"].parts_acc == []


# ---- the parts add up ------------------------------------------------------------------------------------------------------

def test_parts_add_up():
    _, _, ob = _h38()
    dec = [r for r in ob.rows if r["t"] == "decision"]
    assert dec
    for d in dec:
        for c in d["cands"]:
            assert abs(sum(c["parts"].values()) - c["u"]) < 1e-4, c
        if d["chosen"] is not None and d["runner"] is not None:
            assert abs(d["margin"] - (d["cands"][d["chosen"]]["u"] - d["cands"][d["runner"]]["u"])) < 1e-5
    st = [r for r in ob.rows if r["t"] == "state"]
    assert len(st) == 2 * 60
    for s in st:
        assert abs(sum(s["g"].values()) - (s["pl"] - s["s_off"] - s["s_non"])) < 2e-4
    rd = [r for r in ob.rows if r["t"] == "reading"]
    assert rd and rd[0]["kind"] == "formation0"
    for x in rd:
        for r in "AB":
            m = x["m"][r]
            assert m["W_parts"] is not None and abs(sum(m["W_parts"].values()) - m["W"]) < 1e-4
            ea = x.get("exit_anticipation", 0.0)
            assert m["O_parts"] is not None and abs(sum(m["O_parts"].values()) - ea - m["O"]) < 1e-4


def test_replays_are_faithful_and_isolated():
    _, _, ob = _h38()
    rp = [r for r in ob.rows if r["t"] == "replay"]
    assert rp and all(r["faithful"] for r in rp)
    assert all(r["applied"] for r in rp if r["kind"] == "swap")
    assert {"swap", "pressure_off"} <= {r["kind"] for r in rp}


def test_flows_balance_the_money():
    """For each member and the pot: balance at attach + flows in - flows out = balance at the end (the ledger misses nothing)."""
    for lv, a, b, s in ((4, "g-00000", "g-11111", 1), (0, "p-anchor", "p-wanderer", 2), (4, "g-01010", "p-wanderer", 2)):
        _, lived, ob = _h38(level=lv, a=a, b=b, seed=s, weeks=156, cfg=OB.ObsConfig())
        w, bal = lived.world, dict(ob.rows[0]["bal0"])
        for f in (r for r in ob.rows if r["t"] == "flow"):
            for k, sign in ((f["src"], -1), (f["dst"], 1)):
                if k in bal:
                    bal[k] += sign * f["amt"]
        assert abs(bal["A"] - w.p["A"]["money"]) < 1e-3 and abs(bal["B"] - w.p["B"]["money"]) < 1e-3
        assert abs(bal["pot"] - w.pool) < 1e-3


def test_write_and_read(tmp_path):
    _, _, ob = _h38(weeks=6, cfg=OB.ObsConfig())
    p = ob.write(tmp_path / "r.jsonl.gz")
    back = OB.read(p)
    assert back["run"][0]["schema"] == OB.SCHEMA and len(back["state"]) == 12
