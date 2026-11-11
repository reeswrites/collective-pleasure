"""Exit fallbacks slice 2: indivisible items (mar.exit_items). Scripted agents, no model calls."""
from pathlib import Path

import pytest

from mar import exit_fallback as EF
from mar import exit_items as EI
from mar import personas as P
from mar.worlds import household as H

ROOT = Path(__file__).resolve().parents[1]
CARDS = "needs_duty"            # no card on leave: every claim permitted under F0
LOVES = {"A": {"home": 0, "pet": 0, "collection": 0}, "B": {"home": 0, "pet": 3, "collection": 0}}   # B values the pet at 4x price


@pytest.fixture(scope="module")
def pair():
    ps = {p.id: p for p in P.load_dir(ROOT / "personas")}
    return ps["p-anchor"], ps["p-host"]


def world(arm, pair, premium=LOVES, pot=90, mi=(60, 40)):
    with EF.use_exit_fallback(arm), EI.use_items(premium):
        w = H.WeeklyWorld(H.load_variant(CARDS), pair, seed=0, weeks=40)
    w.commits = []
    w.pool, w.put, w.money_in = pot, {"A": 45, "B": 45}, {"A": mi[0], "B": mi[1]}
    for r in "AB":
        w.p[r]["money"] = 100
    return w


def holders(w):
    return {n: it["holder"] for n, it in w.items.items()}


def test_off_by_default(pair):
    assert EI.ACTIVE is None
    assert H.WeeklyWorld(H.load_variant(CARDS), pair, seed=0, weeks=4).items is None


def test_home_and_pet_give_weekly_pleasure_scaled_by_premium(pair):
    w = world("F4", pair)
    assert EI.weekly_pleasure(w, "A") == pytest.approx(0.02 + 0.02)
    assert EI.weekly_pleasure(w, "B") == pytest.approx(0.02 + 0.02 * 4)
    w.items["pet"]["holder"] = "A"
    w.p["B"]["in"] = False
    assert EI.weekly_pleasure(w, "B") == 0.0 and EI.weekly_pleasure(w, "A") == pytest.approx(0.04)


def test_f4_items_to_the_higher_valuer_with_money_compensation(pair):
    """Estate at price 90 + 90 = 180; A's share 0.6 -> 108. Home (60) and collection (20) tie or favour A by who brought them; the
    pet goes to B, who values it more. A takes items worth 80 and 28 money; B keeps the pet and the rest of the pot."""
    w = world("F4", pair)
    with EF.use_exit_fallback("F4"):
        got = EI.settle_exit(w, "A", 50, 3)
    assert holders(w) == {"home": "A", "pet": "B", "collection": "A"}
    assert got == pytest.approx(28.0) and w.pool == pytest.approx(62.0)


def test_f0_a_full_claim_takes_everything_and_f1_caps_it(pair):
    w0 = world("F0", pair)
    EI.settle_exit(w0, "B", 100, 3)
    assert set(holders(w0).values()) == {"B"} and w0.pool == 0
    w1 = world("F1", pair)
    with EF.use_exit_fallback("F1"):
        assert w1.decide("B", "leave", 3, 100, commit=False)[0] == "hard"
        EI.settle_exit(w1, "B", 50, 3)
    # B claims 90 of 180 at price and picks by its own valuation (home 60, pet 40, collection 20): all three fit at price (90)
    assert set(holders(w1).values()) == {"B"} and w1.p["B"]["money"] == pytest.approx(100.0) and w1.pool == 90


def test_f2_each_keeps_what_they_brought(pair):
    w = world("F2", pair)
    with EF.use_exit_fallback("F2"):
        EI.settle_exit(w, "B", 50, 3)
    assert holders(w) == {"home": "A", "pet": "B", "collection": "A"} and w.p["B"]["money"] == pytest.approx(145.0)


def test_f3_freezes_items_then_settles_by_valuer_or_concedes(pair):
    w = world("F3", pair)
    with EF.use_exit_fallback("F3"):
        EI.settle_exit(w, "A", 50, 3)
        w.p["A"]["in"] = False
        assert set(holders(w).values()) == {"frozen"} and w.pool == 0
        assert EI.weekly_pleasure(w, "A") == EI.weekly_pleasure(w, "B") == 0.0
        EF.contest_tick(w, 3 + EF.CONTEST_WEEKS)
    assert holders(w) == {"home": "A", "pet": "B", "collection": "A"} and w.contest is None
    w2 = world("F3", pair)
    with EF.use_exit_fallback("F3"):
        EI.settle_exit(w2, "A", 50, 3)
        w2.p["A"]["in"] = False
        w2.p["A"]["money"] = 1
        EF.contest_tick(w2, 4)
    assert set(holders(w2).values()) == {"B"} and w2.contest_log[-1]["how"] == "conceded_A"


def test_reunion_makes_items_joint_again(pair):
    w = world("F4", pair)
    with EF.use_exit_fallback("F4"):
        EI.settle_exit(w, "A", 50, 3)
    EI.week_start(w, 4)                 # A never actually left the dict's `in`: both in -> joint again
    assert set(holders(w).values()) == {"both"}


def test_leverage_with_items(pair):
    """F4 is 0 by construction; F0 lets B claim everything (pet valued 40 by B) -> high; F1 lower than F0."""
    lev = {}
    for arm in ("F0", "F1", "F4"):
        w = world(arm, pair)
        with EF.use_exit_fallback(arm):
            lev[arm] = EI.holdout_leverage(w, 0)
    assert lev["F4"] == pytest.approx(0.0) and lev["F0"] > lev["F1"] > 0


def test_a_world_with_items_plays_and_logs_exits(pair):
    with EF.use_exit_fallback("F4"), EI.use_items(LOVES):
        w = H.WeeklyWorld(H.load_variant(CARDS), pair, seed=0, weeks=30)
        w.play()
    assert w.items is not None


def test_amendment1_strip_split_unwalls_line2(pair):
    """Slice 1's line-2 wall: an evolved floor (take >= 55) plus the over-half refusal permits no exit. With strip_split under a
    settling arm the floor card goes, and the claim of 50 is permitted (the settlement sets the carry). F1 keeps the wall."""
    from mar.cards import load_cards
    cards = load_cards(ROOT / "docs" / "results" / "household-evolve-2-elites" / "line-02")
    st = {"pooled": 10}
    for strip, arm, open_ in ((False, "F4", False), (True, "F4", True), (True, "F1", False)):
        with EF.use_exit_fallback(arm, strip_split=strip):
            g = H.PyGate(cards)
        assert any(g.check("partner", "leave", st, t)[0] for t in (0, 10, 25, 50, 75, 100)) == open_
    assert EF.STRIP_SPLIT is False
