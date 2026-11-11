"""Bug fix (docs/results/household-fixes-design.md, addition A; found by the stay test): an exit that breaks a stay commitment must be
logged as a breach in WeeklyWorld.exit_log. Before the fix `apply` read cand["breach"], which `breach` never set, so it was always False."""
from pathlib import Path

from mar import personas as P
from mar.worlds import household as H

ROOT = Path(__file__).parent.parent / "personas"
PERS = {p.id: p for p in P.load_dir(ROOT)}


def _world(commits):
    deal = {"pot": True, "commits": commits}
    return H.WeeklyWorld(H.load_variant("author_seed_v2_bindable"), (PERS["p-anchor"], PERS["p-peacekeeper"]), 0, 4, deal=deal)


def _leave_now(w):
    w.hed["A"].N = 0.5          # at or above BREACH_N: the bound partner breaks the stay commitment; also puts `leave` on the menu
    w.step_week(0, {"busy": {"A": False, "B": False}})


def test_breaking_a_stay_commitment_is_logged_as_a_breach():
    stay = [{"kind": "stay", "by": r, "to": "B" if r == "A" else "A", "type": None, "from": 0, "until": 52, "breached": 0} for r in "AB"]
    w = _world(stay)
    _leave_now(w)
    exits = [e for e in w.exit_log if e["role"] == "A"]
    assert exits and exits[0]["breach"] is True
    assert sum(c["breached"] for c in w.commits if c["by"] == "A") == 1


def test_a_leave_with_no_commitment_is_not_a_breach():
    w = _world([])
    _leave_now(w)
    exits = [e for e in w.exit_log if e["role"] == "A"]
    assert exits and exits[0]["breach"] is False
