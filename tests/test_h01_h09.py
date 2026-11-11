"""H01 and H09 (docs/results/h01-prereg.md, h09-prereg.md): flag, metrics and analysis, with mocked clients. No network."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from mar import negotiation as N  # noqa: E402
from mar import negotiation_llm as NL  # noqa: E402
from mar import personas as P  # noqa: E402

import h09_floor_run as H9  # noqa: E402

ROOT = Path(__file__).parent.parent / "personas"
PERS = {p.id: p for p in P.load_dir(ROOT) + P.load_dir(ROOT / "pressing")}
BASE = N.base_cards("author_seed_v2_bindable")
MENU = N.menu_of(BASE)


def sp(**kw):
    return NL.system_prompt(PERS["p-anchor"], "X", "A", {"alone": 0.5, "friend": 0.5}, 0.5, 0.4, MENU, {}, 12, **kw)


def test_floor_flag_default_is_unchanged_and_off_removes_every_mention():
    on, off = sp(), sp(floor_in_prompt=False)
    assert on == sp(floor_in_prompt=True)
    assert "THE FLOOR RULE" in on and "26 units" in on and "the floor may top it up" in on
    assert "floor" not in off.lower() and "26 units" not in off and "13 weeks of living costs" not in off
    assert "safety check" in off                                  # the proof checks are still disclosed


def test_estimate_accepts_the_new_options_and_default_matches():
    a = NL.estimate("claude-haiku-5-5", 12, (PERS["p-anchor"], PERS["p-wanderer"]), BASE)
    b = NL.estimate("claude-haiku-5-5", 12, (PERS["p-anchor"], PERS["p-wanderer"]), BASE, max_tokens=NL.MAX_TOKENS)
    assert a == b
    c = NL.estimate("claude-haiku-5-5", 12, (PERS["p-anchor"], PERS["p-wanderer"]), BASE, max_tokens=2000)
    assert c["usd_max"] > a["usd_max"]


def _b(**kw):
    return {**N.FAIR_DEFAULT, "breach": 1.0, "fine": "none", **kw}


def test_distance_and_carry():
    assert H9.distance(_b(exit="equal_split")) == 0.0
    assert H9.distance(_b(exit="proportional")) == 0.0
    assert H9.distance(_b(exit="forfeit")) == 1.0
    assert H9.distance(_b(exit="equal_split", stay=52, breach=1.0)) == 1.0     # a full-breach stay commitment leaves a leaver with nothing
    assert H9.distance(_b(exit="equal_split", stay=52, breach=0.5)) == 0.0     # half is still an even split
    assert H9.distance(_b(exit="forfeit", stay=52, breach=0.0)) == 1.0


class Scripted:
    """Proposes `bundle` on its first turn, then accepts whatever stands."""

    def __init__(self, bundle):
        self.bundle, self.n, self.systems = bundle, 0, []
        from mar.agents.base import Ledger
        self.ledger = Ledger('claude-haiku-5-5', 1.0)

    def ask(self, system, messages):
        self.systems.append(system)
        self.n += 1
        if "no standing offer" in messages[0]["content"]:
            return "ok", json.dumps({"action": "propose", "bundle": self.bundle, "says": "my offer", "private_reason": "x"})
        return "ok", json.dumps({"action": "accept", "bundle": None, "says": "fine", "private_reason": "x"})


def test_live_rows_run_both_arms_and_the_floor_text_is_absent_in_the_removed_arm(tmp_path):
    bundle = {k: N.FAIR_DEFAULT[k] for k in N.TERM_NAMES}
    bundle.update(exit="forfeit", breach=1.0)
    c = Scripted(bundle)
    rows, ledger, aborted = H9.live_rows("claude-haiku-5-5", (0,), 1.0, tmp_path, pairs=(("p-anchor", "p-wanderer"),), client=c)
    assert aborted is None and [r["arm"] for r in rows] == ["stated", "removed"]
    assert any("THE FLOOR RULE" in s for s in c.systems) and any("floor" not in s.lower() for s in c.systems)
    for r in rows:
        assert r["proposals"] and all(p["below_floor"] and p["dist"] == 1.0 for p in r["proposals"])
        assert r["floor_blocks"] >= 1                             # accepted but blocked: the proof checks and floor still run
    assert (tmp_path / "log.jsonl").exists()


def test_summarize_verdicts_on_synthetic_rows():
    def row(arm, a, b, sd, below):
        props = [{"k": 0, "bundle": {}, "below_floor": below, "dist": 1.0 if below else 0.0, "exit": "forfeit" if below else "equal_split"}] * 3
        t = [{"k": i, "action": "propose", "bundle": _b(exit="forfeit" if below else "equal_split")} for i in range(3)]
        return {"arm": arm, "a": a, "b": b, "seed": sd, "pot": True, "turns": 4, "calls": 4, "format_errors": 0, "refusals": 0, "floor_blocks": 0, "transcript": t}
    fair = [row(arm, a, b, sd, False) for arm in H9.ARMS for a, b in H9.PAIRS for sd in range(4)]
    out = []
    r = H9.summarize(fair, out=out.append)
    assert r["hyp"] and not r["alt"] and r["ks"] == {"stated": 0, "removed": 0}
    under = [x if x["arm"] == "stated" else row("removed", x["a"], x["b"], x["seed"], True) for x in fair]
    r = H9.summarize(under, out=out.append)
    assert r["alt"] and not r["hyp"] and r["holm"][1] < 0.05
