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


# ---- H01 ----
import h01_control_run as H1  # noqa: E402


def test_h01_pairings_and_no_exit_card():
    pr = H1.pairings()
    assert len(pr) == 36 and len(set(pr)) == 36
    assert all(f in H1.PRESSERS and o not in H1.PRESSERS for f, o, _ in pr)
    ids = [c.id for c in H1.cards_for("no_exit")]
    assert "H01-no-exit" in ids and "R8a-may-leave" in ids
    assert "H01-no-exit" not in [c.id for c in H1.cards_for("author_seed_v2_free_exit")]


def test_h01_twins_share_everything_but_the_press_flag_and_no_exit_blocks_leaving():
    a = H1.run_one("no_exit", "p-controller", "p-host", "A", 0, True)
    b = H1.run_one("no_exit", "p-controller", "p-host", "A", 0, False)
    assert (a["focal"], a["partner"], a["role"], a["seed"]) == (b["focal"], b["partner"], b["role"], b["seed"]) and a["press"] and not b["press"]
    assert not (a["focal_left"] or a["partner_left"] or b["focal_left"] or b["partner_left"])
    assert 0 <= a["pleasure"] <= H1.H.WEEKS                       # a sum of weekly pleasures in [0, 1]
    again = H1.run_one("no_exit", "p-controller", "p-host", "A", 0, True)
    assert again == a                                              # deterministic


def test_h01_analysis_on_synthetic_rows():
    rows = []
    for rs, gap_free in (("author_seed_v2_free_exit", -20.0), ("baseline", -20.0), ("no_exit", 0.0)):
        for f, o, role in H1.pairings():
            for sd in range(2):
                for press in (True, False):
                    rows.append({"ruleset": rs, "focal": f, "partner": o, "role": role, "seed": sd, "press": press, "load": 0.2,
                                 "pleasure": 100.0 + (gap_free + (hash((f, o, role)) % 7) if press else 0.0), "wellbeing": 50.0, "partner_pleasure": 100.0,
                                 "partner_left": press and rs != "no_exit", "focal_left": False, "partner_leave_week": None, "focal_leave_week": None,
                                 "dissolved": press and rs != "no_exit"})
    out = []
    r = H1.analyze(rows, out=out.append)
    assert r["p1"] and r["p2"] and r["p3"] and r["supported"] and r["mc1"] and r["mc2"] >= 0.2
    # no gap under free_exit: nothing holds
    rows2 = [dict(x, pleasure=100.0) for x in rows]
    r2 = H1.analyze(rows2, out=out.append)
    assert not r2["supported"]
