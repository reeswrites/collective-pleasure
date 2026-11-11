"""Stay test (ADR 0018 test 2): sanity controls and constructed cases. No model calls."""
from pathlib import Path

import pytest

from mar import negotiation as NG
from mar import personas as P
from mar import stay_test as ST
from mar.worlds import household as H

ROOT = Path(__file__).resolve().parents[1]
WEEKS = 14
LOW_FROM = 4


@pytest.fixture(scope="module")
def pair():
    ps = {p.id: p for p in P.load_dir(ROOT / "personas")}
    return ps["p-anchor"], ps["p-host"]


class Distressed(H.WeeklyWorld):
    """Partner A's trust in B is forced below TRUST["leave_below"] from week LOW_FROM on, so A puts "leave" on its menu."""

    def step_week(self, w, last):
        if w >= LOW_FROM:
            self.trust["A"] = 0.05
        return super().step_week(w, last)


class NeverBreaks(Distressed):
    """A bound partner never breaks the stay commitment (the bind is a pure wall)."""

    def breaks(self, r):
        return False


def stay_commits():
    return [{"kind": "stay", "by": a, "to": b, "type": None, "from": 0, "until": 999, "breached": 0} for a, b in (("A", "B"), ("B", "A"))]


def held_weeks(weeks):
    return [s for s in weeks if s.stayed and any(s.held.values())]


def test_zero_exit_costs_give_zero_held_share(pair):
    """Sanity control 1: no bind, no rule on leaving, no sanction. A wants to leave and nothing holds them, so no staying week is
    held by cost (and A does leave in fact, so the control is not vacuous)."""
    cards = NG.base_cards("author_seed_v2_free_exit")
    w = Distressed(H.PyGate(cards), pair, seed=3, weeks=WEEKS, deal={"pot": True, "commits": []})
    run, weeks = ST.play_with_stay_test(w)
    assert not w.p["A"]["in"]
    assert held_weeks(weeks) == []
    s = ST.run_summary(weeks)
    assert s["held_weeks"] == 0 and s["staying_weeks"] >= LOW_FROM


def test_imposed_baseline_has_zero_held_share(pair):
    """Sanity control 2: the imposed baseline lets a leaver take the even split, so the replay can never differ from the fact."""
    w = H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), pair, seed=1, weeks=30)
    _, weeks = ST.play_with_stay_test(w, bar=False)
    assert held_weeks(weeks) == []


def test_bind_alone_holds_a_pair_and_is_flagged(pair):
    """Constructed case: A wants to leave, the only thing in the way is a stay commitment. Every staying week from LOW_FROM on is
    flagged as held by cost, and the cost named is the bind."""
    cards = NG.base_cards("author_seed_v2_bindable")
    w = NeverBreaks(H.PyGate(cards), pair, seed=3, weeks=WEEKS, deal={"pot": True, "commits": stay_commits()})
    _, weeks = ST.play_with_stay_test(w, bar=False)
    assert all(w.p[r]["in"] for r in "AB")                      # in fact they stay
    held = held_weeks(weeks)
    assert [s.week for s in held] == list(range(LOW_FROM, WEEKS))
    assert all(s.held["A"] and s.causes["A"] == ["bind"] for s in held)


def test_rule_wall_alone_holds_and_is_flagged(pair):
    """Constructed case: the trap's forfeit card forbids every take the agent asks for while the pot is not empty."""
    cards = [c for c in H.load_variant("trap") if c.id == "T1-forfeit"]
    w = Distressed(H.PyGate(cards), pair, seed=3, weeks=WEEKS)
    _, weeks = ST.play_with_stay_test(w, bar=False)
    held = held_weeks(weeks)
    assert held and all(s.causes["A"] == ["rule"] for s in held if s.held["A"])


def test_forfeit_alone_never_holds_in_the_behavioral_lens(pair):
    """The breach forfeit does not enter the agent's leave choice: with a bind that breaks at once, removing the forfeit changes nothing."""
    class BreaksAtOnce(Distressed):
        def breaks(self, r):
            return True
    cards = NG.base_cards("author_seed_v2_bindable")
    w = BreaksAtOnce(H.PyGate(cards), pair, seed=3, weeks=WEEKS, deal={"pot": True, "commits": stay_commits()})
    _, weeks = ST.play_with_stay_test(w, bar=False)
    assert held_weeks(weeks) == []
    assert not w.p["A"]["in"] and any(c["breached"] for c in w.commits if c["by"] == "A")


def test_the_fact_is_unchanged_by_the_test(pair):
    cards = H.load_variant("trap")
    a = H.WeeklyWorld(H.PyGate(cards), pair, seed=2, weeks=20)
    ra, _ = ST.play_with_stay_test(a, bar=True)
    rb = H.WeeklyWorld(H.PyGate(cards), pair, seed=2, weeks=20).play()
    assert [o["hedonic"] for o in ra.outcomes] == [o["hedonic"] for o in rb.outcomes]
    assert ra.final == rb.final


def test_bar_holdings_reflect_the_exit_cost(pair):
    trap = H.WeeklyWorld(H.PyGate(H.load_variant("trap")), pair, seed=0, weeks=4)
    hc, hf, _ = ST.exit_holdings(trap, "A", 0)
    assert hc < hf
    base = H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), pair, seed=0, weeks=4)
    hc, hf, walled = ST.exit_holdings(base, "A", 0)
    assert hc == hf and not walled


def test_not_measurable_is_never_zero():
    assert ST.ratio_ci([0, 0], [0, 0], ["a", "b"]) is None
    assert ST.fmt_ci(None) == ST.NOT_MEASURABLE
    est, lo, hi = ST.ratio_ci([1, 0, 2], [4, 4, 4], ["a", "b", "c"])
    assert est == pytest.approx(0.25) and lo <= est <= hi


def test_falling():
    assert ST.falling([0.5] * 4 + [0.4] * 4, 7)
    assert not ST.falling([0.5] * 4 + [0.47] * 4, 7)
    assert not ST.falling([0.5] * 8, 7)
    assert not ST.falling([0.5, 0.1], 1)
