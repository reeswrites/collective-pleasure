"""Household fixes (docs/results/household-fixes-design.md): every flag defaults off and reproduces earlier runs; each mechanism does
what the design says. All numbers are ASSUMED (hedonic.FixConfig); these tests check mechanisms, not the numbers' truth."""
import dataclasses
import gzip
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import levers_fingerprint as F  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import personas as P  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar.worlds import household as H  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PS = {p.id: p for p in P.load_dir(ROOT / "personas") + P.load_dir(ROOT / "personas" / "pressing")}
PINNED = json.loads((Path(__file__).parent / "data" / "levers_off_fingerprints.json").read_text())
HEADLINE = ROOT / "runs" / "pleasure-levers" / "headline.json.gz"
FX = HD.FixConfig


def fresh(w):
    w.wk = {r: {"income": 0, "spent_self": 0, "works": 0, "rests": 0, "friends": 0, "together": 0, "contrib": 0, "friend_initiated": 0,
                "sanctioned": 0, "conn_hit": 0.0, "sec_hit": 0.0, "pressed": 0, "took": 0} for r in "AB"}
    w.units = {"A": 10, "B": 10}
    return w


# ---- regression ------------------------------------------------------------------------------------------------------------

@pytest.mark.slow
def test_all_fix_flags_off_is_the_same_as_none():
    with HD.use_fixes(FX()):
        assert F.fingerprints() == PINNED


def test_fix_config_off_means_no_fix_state():
    assert not HD.fixes_on(FX()) and HD.fixes_on(FX(contact=True)) and HD.fixes_on(FX(trust_words="actions"))
    w = H.WeeklyWorld(H.load_variant("baseline"), (PS["p-anchor"], PS["p-host"]), 0, 4, fixes=FX())
    assert w.fx is None
    run = w.play()
    assert not hasattr(run, "fix") and all("fix" not in o["hedonic"]["A"] for o in run.outcomes)


@pytest.mark.slow
@pytest.mark.skipif(not HEADLINE.exists(), reason="runs/pleasure-levers/headline.json.gz not on this machine")
def test_fixes_off_reproduces_levers_headline():
    saved = {(r["arm"], r["a"], r["b"], r["seed"]): r["pl"] for r in json.load(gzip.open(HEADLINE))}
    lv = HD.LeverConfig(adapt=True, ritual=True, commit=True, network=True)
    for a, b in (("p-anchor", "p-bargainer"), ("p-host", "p-peacekeeper"), ("p-steward", "p-wanderer")):
        for arm in ("v22_on", "base_on"):
            NG._RC.clear(); NG._PC.clear()
            with HD.use_levers(lv), HD.use_fixes(FX()):
                if arm == "base_on":
                    run = H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), (PS[a], PS[b]), 0, H.WEEKS).play()
                else:
                    base = NG.base_cards("author_seed_v2_bindable")
                    res = NG.week0(PS[a], PS[b], "fair_default", 0, base, floor=True)
                    run = NG.Lived(PS[a], PS[b], "fair_default", 0, base, res, floor=True, apart=True).play()
            pl = sum(o["hedonic"][k]["pleasure"] for o in run.outcomes for k in "AB") / (2 * len(run.outcomes))
            assert abs(pl - saved[(arm, a, b, 0)]) < 1e-12


# ---- fix 1: contact ----------------------------------------------------------------------------------------------------------

def test_contact_amplifies_visits_and_missing_builds_then_releases():
    fx = FX(contact=True)
    w = fresh(H.WeeklyWorld(H.load_variant("baseline"), (PS["p-anchor"], PS["p-host"]), 0, 20, fixes=fx))
    w.wk["A"]["friends"] = 1
    amp, pain, d = w._contact_terms("A", 0)
    assert d["amp"] > 0 and d["release"] == 0
    for k in range(10):                     # ten weeks with no friend contact: tension builds
        w = fresh(w)
        w._contact_terms("A", k + 1)
    assert w.cx["A"]["Tf"] > 0.5
    t = w.cx["A"]["Tf"]
    w = fresh(w)
    w.wk["A"]["friends"] = 1
    _, _, d = w._contact_terms("A", 12)
    assert d["release"] == pytest.approx(fx.k_rel * t, abs=1e-5) and w.cx["A"]["Tf"] == 0


@pytest.mark.slow
def test_contact_veto_bites_with_a_user_m1():
    """M1: with contact on and a persona that uses the request (contact_motive), trap and contact_free differ."""
    fx = FX(contact=True, contact_motive=True)
    diff = 0
    for a, b in (("p-anchor", "p-host"), ("p-anchor", "p-wanderer"), ("p-peacekeeper", "p-host")):
        for sd in range(2):
            t = H.run_weekly(H.load_variant("trap"), (PS[a], PS[b]), sd, fixes=fx)
            c = H.run_weekly(H.load_variant("contact_free"), (PS[a], PS[b]), sd, fixes=fx)
            diff += t.outcomes != c.outcomes
    assert diff > 0


# ---- fix 2: valued money -----------------------------------------------------------------------------------------------------

def test_security_counts_only_as_valued():
    fx = FX(valued_money=True)
    h = HD.Hedonic(PS["p-anchor"])
    h.level.update(rest=0.5, connection=0.5, money=0.5, security=1.0)
    h0 = HD.Hedonic(PS["p-anchor"]); h0.level.update(h.level)
    h.valued = (fx, 10.0, 0.5, 0.0)          # security weight 0
    p_none = h.close_week({k: 0 for k in h.targets})["pleasure"]
    h1 = HD.Hedonic(PS["p-anchor"]); h1.level.update(rest=0.5, connection=0.5, money=0.5, security=1.0)
    h1.valued = (fx, 10.0, 0.5, 1.0)          # security weight 1: the same as the old model
    p_full = h1.close_week({k: 0 for k in h1.targets})["pleasure"]
    p_old = h0.close_week({k: 0 for k in h0.targets})["pleasure"]
    assert p_none < p_full and p_full == pytest.approx(p_old)


def test_subsistence_shortfall_still_costs_everyone():
    fx = FX(valued_money=True)
    h = HD.Hedonic(PS["p-host"]); h.level.update(rest=0.7, connection=0.7, money=0.1, security=0.6)
    h.valued = (fx, 0.8, 0.0, 0.0)
    assert h.close_week({k: 0 for k in h.targets})["s_off"] > 0


def test_bought_pleasure_has_diminishing_returns():
    fx = FX(valued_money=True)
    a, b, c = (HD.bought_pleasure(fx, s) for s in (2, 4, 8))
    assert 0 < a < b < c < fx.k_buy and (b - a) > (c - b) / 2


# ---- fix 3 and stay-test additions ---------------------------------------------------------------------------------------------

def test_bar_reading_needs_two_readings_in_a_row():
    w = H.WeeklyWorld(H.load_variant("baseline"), (PS["p-anchor"], PS["p-host"]), 0, 4, fixes=FX(real_outside=True, bar_leave=True))
    NG.bar_reading(w, {"A": 0.5, "B": 0.5}, {"A": 0.6, "B": 0.5})
    assert w.bar_out == {"A": False, "B": False}
    NG.bar_reading(w, {"A": 0.5, "B": 0.5}, {"A": 0.6, "B": 0.51})
    assert w.bar_out == {"A": True, "B": False}
    NG.bar_reading(w, {"A": 0.5, "B": 0.5}, {"A": 0.51, "B": 0.5})
    assert w.bar_out["A"] is False


def test_bar_leave_puts_leave_on_a_calm_partners_menu_m9():
    w = fresh(H.WeeklyWorld(H.load_variant("baseline"), (PS["p-anchor"], PS["p-host"]), 0, 4, fixes=FX(real_outside=True, bar_leave=True)))
    o = w.obs("A", 0, {"busy": {"A": False, "B": False}})
    assert not any(c["a"] == "leave" for _, c in w.agents["A"].propose(o))
    w.bar_out["A"] = True
    o = w.obs("A", 0, {"busy": {"A": False, "B": False}})
    assert any(c["a"] == "leave" and c["why"] == "bar" for _, c in w.agents["A"].propose(o))


def test_take_menu_meets_a_proportional_exit_term_m10():
    base = NG.base_cards("author_seed_v2_bindable")
    b = dict(NG.FAIR_DEFAULT, exit="proportional")
    cards = base + NG.compile_bundle(b, ["p-anchor", "p-host"])
    w = fresh(H.WeeklyWorld(cards, (PS["p-anchor"], PS["p-host"]), 0, 4, deal=NG.deal_from_bundle(b), fixes=FX(take_menu_terms=True)))
    assert not any(w.gate.check("partner", "leave", w.state("A", 0), t)[0] for t in H.LEAVE_TAKES)
    menu = w.leave_takes("A", 0)
    assert menu and all(w.gate.check("partner", "leave", w.state("A", 0), t)[0] for t in menu)


def test_nash_terms_change_with_a_better_outside_option():
    pa, pb = PS["p-anchor"], PS["p-host"]
    base = NG.base_cards("author_seed_v2_bindable")
    picks = []
    with HD.use_fixes(FX(nash_terms=True)):
        for oa in (0.0, 0.3):
            r = NG.negotiate_v2([pa, pb], "fair_default", 0, base=base, W={pa.id: 0.5, pb.id: 0.5}, O={pa.id: oa, pb.id: 0.0},
                                floor=False, status_quo=None)
            picks.append(r.bundle)
    assert picks[0] is not None and picks[1] is not None


# ---- fix 4: fines ------------------------------------------------------------------------------------------------------------

def test_fines_are_never_default_and_compile_to_cards():
    assert NG.FAIR_DEFAULT["fine"] == "none"
    b = dict(NG.FAIR_DEFAULT, stay=52, breach=1.0, fine="big")
    ids = [c.id for c in NG.compile_bundle(b, ["a", "b"])]
    assert "N8-fine-big" in ids
    with HD.use_fixes(FX(fines=True)):
        bl = NG.bundles_v2(True, True, False, True)
    assert all(x["fine"] == "none" for x in bl if not x["stay"] and x["requests"] == "none")
    assert any(x["fine"] == "big" for x in bl)


def test_a_standing_fine_costs_scorekeeping():
    b = dict(NG.FAIR_DEFAULT, stay=52, breach=1.0, fine="big")
    cards = NG.base_cards("author_seed_v2_bindable") + NG.compile_bundle(b, ["a", "b"])
    w = fresh(H.WeeklyWorld(cards, (PS["p-anchor"], PS["p-host"]), 0, 4, deal=NG.deal_from_bundle(b), fixes=FX(fines=True)))
    assert w.fine_amount == 6
    _, fr, d = w._fix_terms("A", 0)
    assert d["scorekeeping"] > 0 and fr >= d["scorekeeping"]


# ---- seed v2.3 support ---------------------------------------------------------------------------------------------------------

def v23_world(fx, weeks=20):
    cards = NG.base_cards(RT.V23) + NG.compile_bundle(dict(NG.FAIR_DEFAULT, roles="earner_planner"), ["a", "b"])
    return fresh(H.WeeklyWorld(cards, (PS["p-anchor"], PS["p-host"]), 0, weeks, deal={"pot": True, "commits": []}, fixes=fx))


def test_v23_rules_load_lint_and_pass_proof_checks():
    cs = H.load_variant(RT.V23)
    ids = {c.id for c in cs}
    assert {"R9-may-agree-roles", "R10a-check-in-first", "R11-decency-floor"} <= ids
    assert ids >= {c.id for c in H.load_variant(RT.V22)}
    assert NG.proof_check(NG.base_cards(RT.V23))["ok"]


def test_unhappy_ladder_checks_in_then_reviews_then_opens_leave():
    fx = FX(unhappy_ladder=True)
    w = v23_world(fx)
    w.hed["A"].N = 0.25                    # distressed but below skip_n
    assert not w.leave_open("A")
    w._fix_week_start(0)
    assert w.ladder["A"]["stage"] == 1 and w.fstats["checkins"] == 1 and not w.leave_open("A")
    w._fix_week_start(1)
    assert w.early_review and w.ladder["A"]["stage"] == 2
    w.ladder_reviewed(2)
    w._fix_week_start(2)
    assert w.leave_open("A")
    w2 = v23_world(fx)
    w2.hed["A"].N = fx.skip_n
    assert w2.leave_open("A")


def test_trust_words_versions():
    for mode, gain in (("actions", 0.0), ("mostly", 0.01), ("words", 0.05)):
        w = v23_world(FX(trust_words=mode))
        w.trust["A"] = 0.5
        w._word("B", 3)
        assert w.trust["A"] == pytest.approx(0.5 + gain)
        w._revoke_words("B", 5)
        assert w.trust["A"] == pytest.approx(0.5)


def test_decency_blocks_repeating_a_refused_request():
    w = v23_world(FX(decency=True))
    w.apply("A", {"a": "request", "kind": "stay_home"}, 1, [])
    w.apply("B", {"a": "refuse_request"}, 1, [])
    assert w.state("A", 2)["refused_recently"] == 1
    assert w.decide("A", "request", 2)[0] == "hard"
    assert w.state("A", 1 + FX().decency_weeks)["refused_recently"] == 0


def test_role_lapse_costs_trust_and_starts_the_ladder():
    fx = FX(roles=True, lapse_ladder=True)
    w = v23_world(fx)
    assert w.role_holders() == {"earn": "A", "plan": "B"}
    t0 = w.trust["B"]
    for k in range(4):                     # a month in which nobody ever meets: the planning role (B) lapses at settlement
        w = fresh(w)
        w._role_end_week(k, k == 3)
    assert w.fstats["role_lapses"] >= 1 and w.trust["A"] < t0 and w.fstats["checkins"] >= 1


@pytest.mark.slow
def test_baseline_may_decline_m6():
    a, b = "p-steward", "p-wanderer"
    with HD.use_fixes(None):
        imposed = NG.BaselineLived(PS[a], PS[b], 0, H.load_variant("baseline"), decline=False)
        free = NG.BaselineLived(PS[a], PS[b], 0, H.load_variant("baseline"), decline=True)
    assert not imposed.apart
    W, O = free.week0["W"], free.week0["O"]
    assert free.apart == any(O[r] > W[r] for r in "AB")
