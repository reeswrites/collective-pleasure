"""No-deal exit fallbacks F0-F5 (mar.exit_fallback; docs/results/exit-fallbacks-design.md), the stay test's exit-cost charge and
holdout leverage. Scripted agents, no model calls."""
import json
import sys
from pathlib import Path

import pytest

from mar import exit_fallback as EF
from mar import negotiation as NG
from mar import personas as P
from mar import stay_test as ST
from mar.cards import load_cards
from mar.worlds import household as H

ROOT = Path(__file__).resolve().parents[1]
ELITES = ROOT / "docs" / "results" / "household-evolve-2-elites"
LAST = {"busy": {"A": False, "B": False}}


@pytest.fixture(scope="module")
def pair():
    ps = {p.id: p for p in P.load_dir(ROOT / "personas")}
    return ps["p-anchor"], ps["p-host"]


def world(arm, cards, pair, a=80, b=20, weeks=40):
    """A world built under `arm` where A put `a` and B put `b` into a pot holding a + b (nothing drawn), no stay commitments."""
    with EF.use_exit_fallback(arm):
        w = H.WeeklyWorld(cards, pair, seed=0, weeks=weeks)
    w.commits = []
    w.put, w.money_in, w.pool = {"A": a, "B": b}, {"A": a, "B": b}, a + b
    w.units, w.wk = {r: H.UNITS for r in "AB"}, {r: {"took": 0} for r in "AB"}      # so `apply` can be called outside a week
    return w


def ids(cards):
    return [c.id for c in cards]


SEED = "author_seed_v2_bindable"


# ---- off / F0: old results reproduce -------------------------------------------------------------------------------------

def test_off_by_default_and_f0_is_off():
    assert EF.ACTIVE is None
    cards = load_cards(ELITES / "line-12")
    assert ids(H.PyGate(cards).cards) == ids(cards)
    with EF.use_exit_fallback("F0"):
        assert EF.ACTIVE is None and ids(H.PyGate(cards).cards) == ids(cards)
    with pytest.raises(ValueError):
        with EF.use_exit_fallback("F9"):
            pass


@pytest.mark.parametrize("arm", [None, "F0"])
def test_off_reproduces_run2_validation_liberty_of_an_elite(arm):
    """Line 12's frozen validation liberty (manifest.json, household evolution run 2) is reproduced exactly, switch off and F0."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import household_evolve2_run as R
    man = json.loads((ELITES / "manifest.json").read_text())
    with EF.use_exit_fallback(arm):
        got = R.new_world().score_runs(tuple(load_cards(ELITES / "line-12")), R.val_ctx())[0]["liberty"]
    assert got == man["lines"]["line-12"]["val"]["liberty"]


def test_off_stay_test_holdings_unchanged(pair):
    """Off, the bar lens's free holdings ignore what a member put in: an imposed cap's cost stays hidden, as before."""
    w = world(None, H.load_variant("baseline"), pair)
    hc, hf, walled = ST.exit_holdings(w, "A", 0)
    assert hc == hf == w.p["A"]["money"] + 50 and not walled


# ---- F1: the half cap as a default -------------------------------------------------------------------------------------------

def test_f1_every_pair_starts_with_the_cap_and_imposed_caps_are_replaced():
    with EF.use_exit_fallback("F1"):
        gs = [H.PyGate(H.load_variant(SEED)), H.PyGate(load_cards(ELITES / "line-09"))]   # no cap; an evolved cap (take > 60)
    for g in gs:
        assert EF.has_fallback(g.cards) and EF.CAP_ID not in ids(g.cards)
        assert g.check("partner", "leave", {"pooled": 10}, 50)[0] and not g.check("partner", "leave", {"pooled": 10}, 75)[0]
    assert H.PyGate(H.load_variant(SEED)).check("partner", "leave", {"pooled": 10}, 100)[0]      # outside the block: as before


def test_bigger_contributor_under_the_cap_is_hard_to_leave(pair):
    """A put 80 of a pot of 100. Under F1 A may carry 50: an exit cost of 30 that the stay test now charges; B bears none."""
    w = world("F1", H.load_variant(SEED), pair)
    with EF.use_exit_fallback("F1"):
        ca, cb = ST.exit_cost(w, "A", 0), ST.exit_cost(w, "B", 0)
        hc, hf, _ = ST.exit_holdings(w, "A", 0)
        hcb, hfb, _ = ST.exit_holdings(w, "B", 0)
    assert ca == {"put_in": 80.0, "max_carry": 50.0, "cost": 30.0, "bigger": True}
    assert cb["cost"] == 0.0 and not cb["bigger"]
    assert hf - hc == 30 and hfb == hcb


def test_bar_lens_reads_held_when_the_cap_is_the_only_gap(monkeypatch, pair):
    w = world("F1", H.load_variant(SEED), pair)
    monkeypatch.setattr(NG, "forward_values", lambda world, wk, last: {"A": 60.5, "B": 999.0})
    monkeypatch.setattr(NG, "trust_penalty", lambda t: 0.0)
    monkeypatch.setattr(NG, "outside_value", lambda p, r, hold, seed, hed=None, cx=None: (float(hold), None))
    with EF.use_exit_fallback("F1"):
        rd = ST.bar_reading(w, 13, LAST)
    money = w.p["A"]["money"]
    assert (rd["A"]["o_cost"], rd["A"]["o_free"]) == (money + 50, money + 80)
    assert rd["A"]["verdict"] == "held" and rd["B"]["verdict"] == "worth" and ST.pair_bar_verdict(rd) == "held"


def test_a_negotiated_exit_term_is_left_as_it_is(pair):
    """A pair whose agreed bundle sets the exit term 'proportional' (N5a) gets no fallback in any arm; the imposed cap is dropped,
    and the bigger contributor carries what they put in (no exit cost): the cap renegotiated away."""
    terms = NG.compile_bundle(dict(NG.FAIR_DEFAULT, exit="proportional"), [p.id for p in pair])
    imposed = NG.base_cards(SEED) + list(load_cards(ELITES / "line-12"))
    for arm in ("F1", "F2", "F3", "F4", "F5"):
        w = world(arm, imposed + terms, pair)
        assert EF.negotiated(w.gate.cards) and not EF.has_fallback(w.gate.cards) and EF.CAP_ID not in ids(w.gate.cards)
        with EF.use_exit_fallback(arm):
            c = ST.exit_cost(w, "A", 0)
        assert w.exit_basis == "put" and c["cost"] == 0.0 and c["max_carry"] == 80.0


# ---- F2, F4: settlements ----------------------------------------------------------------------------------------------------

def test_f2_and_f4_settle_on_contributions_whatever_is_claimed(pair):
    w2 = world("F2", H.load_variant("baseline"), pair)
    w4 = world("F4", H.load_variant("baseline"), pair)
    w4.money_in = {"A": 80, "B": 120}           # B paid more of the bills: F4 counts it, F2 does not
    with EF.use_exit_fallback("F2"):
        assert w2.carry_out("A", 12) == w2.carry_out("A", 50) == 80.0
    with EF.use_exit_fallback("F4"):
        assert w4.carry_out("A", 50) == pytest.approx(40.0) and w4.carry_out("B", 50) == pytest.approx(60.0)
        assert ST.exit_cost(w4, "B", 0)["cost"] == 0.0 and ST.exit_cost(w4, "B", 0)["bigger"]


def test_f4_counts_bill_payments(pair):
    with EF.use_exit_fallback("F4"):
        w = H.WeeklyWorld(H.load_variant("baseline"), pair, seed=0, weeks=8)
        w.play()
    assert w.money_in["A"] >= H.POT_PUT and sum(w.money_in.values()) > sum(w.put.values()) - 1e-9


# ---- F3: contested and costly ------------------------------------------------------------------------------------------------

def test_f3_contest_freezes_costs_and_settles_at_half(pair):
    w = world("F3", H.load_variant("baseline"), pair)
    for r in "AB":
        w.p[r]["money"] = 100
    with EF.use_exit_fallback("F3"):
        assert w.carry_out("A", 50) == 0 and w.retained_fraction("A", 50) == pytest.approx((100 + 50) / 150)
        w.apply("A", {"a": "leave", "take": 50}, 3, [])
        w.p["A"]["in"] = False
        assert w.pool == 0 and w.contest["escrow"] == 100
        EF.contest_tick(w, 3 + EF.CONTEST_WEEKS - 1)
        assert w.contest is not None
        EF.contest_tick(w, 3 + EF.CONTEST_WEEKS)
    assert w.contest is None and w.contest_log[-1]["how"] == "settled"
    assert w.p["A"]["money"] == 150 and w.pool == 50


def test_f3_the_one_short_of_money_walks_away_empty_handed(pair):
    w = world("F3", H.load_variant("baseline"), pair)
    w.p["A"]["money"], w.p["B"]["money"] = 100, 1
    with EF.use_exit_fallback("F3"):
        w.apply("A", {"a": "leave", "take": 50}, 0, [])
        w.p["A"]["in"] = False
        EF.contest_tick(w, 1)
    assert w.contest_log[-1]["how"] == "conceded_B" and w.p["A"]["money"] == 200 and w.pool == 0


def test_f3_contest_adds_friction_to_both(pair):
    """The weekly friction lands in offsettable suffering for both partners while the pot is contested."""
    def s_off(contest):
        with EF.use_exit_fallback("F3"):
            w = H.WeeklyWorld(H.load_variant("baseline"), pair, seed=0, weeks=2)
            w.p["A"]["in"] = False           # A has left (a contest with both in ends at once: reunited)
            w.contest = contest
            w.step_week(0, LAST)
        return [w.run.outcomes[-1]["hedonic"][r]["s_off"] for r in "AB"]
    base, cont = s_off(None), s_off({"leaver": "A", "from": 0, "until": 99, "escrow": 0})
    assert all(c >= b + EF.CONTEST_FRICTION - 1e-4 or c == 1.0 for b, c in zip(base, cont))


# ---- F5: prenup ----------------------------------------------------------------------------------------------------------------

def test_f5_bargains_an_exit_term_at_formation(pair):
    with EF.use_exit_fallback("F5"):
        w = H.WeeklyWorld(H.load_variant(SEED), pair, seed=0, weeks=8)
    assert w.prenup["status"] in ("agreed", "stood", "deadline", "no_bundle", "no_pot")
    if w.prenup["exit"] is not None:
        assert w.prenup_exit in NG.TERMS["exit"] and w.pot and all(w.p[r]["in"] for r in "AB")
    assert EF.ACTIVE is None


def test_f5_no_agreement_means_they_decline_to_form(monkeypatch, pair):
    real = NG.negotiate_v2

    def refuse(*a, **k):
        res = real(*a, **k)
        res.bundle, res.status = None, "no_bundle"
        return res
    monkeypatch.setattr(NG, "negotiate_v2", refuse)
    with EF.use_exit_fallback("F5"):
        w = H.WeeklyWorld(H.load_variant(SEED), pair, seed=0, weeks=8)
    assert w.prenup["exit"] is None and not w.pot and w.pool == 0
    assert not any(w.p[r]["in"] for r in "AB") and w.p["A"]["money"] == H.NO_POT_MONEY


def test_f5_settles_on_the_agreed_term(pair):
    w = world("F5", H.load_variant("baseline"), pair)
    with EF.use_exit_fallback("F5"):
        for term, a_gets in (("equal_split", 50), ("proportional", 80), ("forfeit", 0)):
            w.prenup_exit = term
            assert w.carry_out("A", 12) == a_gets


# ---- holdout leverage ----------------------------------------------------------------------------------------------------------

def test_holdout_leverage_by_arm(pair):
    """A put 80, B 20 (all money in). F0 without a cap: A can walk out with the whole pot, leverage (100 - 80) / 100 = 0.2 for A,
    (100 - 20) / 100 = 0.8 for B -> 0.8. F1: B can force 50 against a contribution of 20 -> 0.3. F2 and F4: 0. F3 with both able to
    wait: the equal split, as F1 -> 0.3; with B unable to wait, A can hold out for the whole pot -> 0.2."""
    cards = H.load_variant("needs_duty")
    assert not any(c.aim == "leave" for c in cards)
    lev = {}
    for arm in ("F0", "F1", "F2", "F3", "F4"):
        w = world(arm, cards, pair)
        for r in "AB":
            w.p[r]["money"] = 100
        with EF.use_exit_fallback(arm):
            lev[arm] = EF.holdout_leverage(w, 0)
            if arm == "F3":
                w.p["B"]["money"] = 1
                lev["F3-poor-B"] = EF.holdout_leverage(w, 0)
    assert lev == pytest.approx({"F0": 0.8, "F1": 0.3, "F2": 0.0, "F3": 0.3, "F4": 0.0, "F3-poor-B": 0.2})
