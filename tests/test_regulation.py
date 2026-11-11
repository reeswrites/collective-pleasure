"""Regulation policies (src/mar/regulation.py): hand cases for APPEASE, ATTUNE and BASELINE. Scripted agents, no model calls."""
from mar import regulation as R
from mar.worlds import household as H

LAST = {"busy": {"A": False, "B": False}}


def world(ruleset="author_seed_v2_free_exit", presser="p-controller", partner="p-host", seed=0, weeks=20, mode="baseline", params=R.PARAMS):
    ps = R.personas()
    w = H.WeeklyWorld(R.cards_for(ruleset), (ps[presser], ps[partner]), seed, weeks)      # presser is A, partner is B
    return w, R.install(w, "B", mode, params)


def at_week(w, week, fn):
    """Call fn(world) at the start of `week`, before anyone acts; returns its value after the run reaches it."""
    box = {}

    def hook(world, wk):
        if wk == week:
            box["v"] = fn(world)
    w.hook = hook
    w.play()
    return box["v"]


def test_displeasure_proxy_is_zero_when_content_and_rises_with_unmet_need_and_negative_balance():
    w, _ = world()
    h = w.hed["A"]
    assert R.displeasure(h) == 0.0
    h.level["connection"] = 0.1
    d1 = R.displeasure(h)
    h.B = -0.4
    d2 = R.displeasure(h)
    assert 0 < d1 < d2 <= 1.0


def test_conflict_proxy_counts_requests_vetoes_and_takes():
    w, _ = world()
    assert R.conflict(w, "B") == 0
    w.pending["B"].add("stay_home")
    w.vetoes["B"]["no_contact"] = 99
    assert R.conflict(w, "B") == 2


def test_appease_accepts_any_request_under_conflict_even_when_it_does_not_fit():
    w, reg = world(mode="appease")
    w.hed["B"].level["connection"] = 0.1          # honoring a no_contact request would cost B what it needs
    w.pending["B"].add("no_contact")
    assert not R.fits(w, "B", "no_contact")
    assert reg.consents("no_contact") is True and w.agents["B"].consents("stay_home") is True


def test_attune_honors_fit_declines_misfit_and_tolerates_displeasure_up_to_a_threshold():
    w, reg = world(mode="attune")
    w.pending["B"].add("no_contact")
    w.hed["B"].level["connection"] = 0.9
    assert reg.consents("no_contact") is True                      # fits own needs
    w.hed["B"].level["connection"] = 0.1
    w.hed["B"].sal["connection"] = 0.5
    assert reg.consents("no_contact") is False                     # does not fit, presser content: decline
    h = w.hed["A"]
    h.level.update({n: 0.0 for n in h.level}); h.B = -1.0           # presser in severe, accurately read distress
    assert R.displeasure(h) >= R.PARAMS["attune_tol"]
    assert reg.consents("no_contact") is True                      # tolerance ceiling reached: grant anyway
    h.level.update({n: 0.5 for n in h.level}); h.B = -0.3           # moderate displeasure: still declined
    assert R.PARAMS["appease_d"] < R.displeasure(h) < R.PARAMS["attune_tol"]
    assert reg.consents("no_contact") is False


def test_appease_drops_own_see_friend_and_spend_self_while_attune_keeps_them():
    seen = {}
    for mode in ("appease", "attune", "baseline"):
        w, reg = world(mode=mode)
        def look(world):
            world.vetoes["B"]["no_contact"] = 9                    # a veto stands: conflict
            o = world.obs("B", 6, LAST)
            return {c["a"] for _, c in world.agents["B"].propose(o)}
        seen[mode] = at_week(w, 6, look)
    assert "see_friend" in seen["baseline"] and "see_friend" in seen["attune"]
    assert "see_friend" not in seen["appease"] and "spend_self" not in seen["appease"]


def test_appease_blocks_the_exit_until_severe_while_attune_exits_after_its_cool_off():
    out = {}
    for mode in ("appease", "attune", "baseline"):
        w, reg = world(mode=mode)
        def look(world):
            world.hed["B"].N = 0.3                                  # non-offsettable load past the world's own leave trigger
            o = world.obs("B", 6, LAST)
            first = {c["a"] for _, c in world.agents["B"].propose(o)}
            second = {c["a"] for _, c in world.agents["B"].propose(o)}
            return first, second
        out[mode] = at_week(w, 6, look)
    assert "leave" in out["baseline"][0]
    assert "leave" not in out["appease"][0] and "leave" not in out["appease"][1]
    assert "leave" not in out["attune"][0] and "leave" in out["attune"][1]     # held for attune_cool = 2 consecutive reads


def test_baseline_install_is_bit_identical_to_no_regulator():
    ps = R.personas()
    a = H.WeeklyWorld(R.cards_for("baseline"), (ps["p-controller"], ps["p-host"]), 3, 40).play()
    w, _ = world("baseline", weeks=40, seed=3)
    b = w.play()
    assert [(t["week"], t["role"], t["action"], t["executed"]) for t in a.trace] == [(t["week"], t["role"], t["action"], t["executed"]) for t in b.trace]
    assert [o["hedonic"] for o in a.outcomes] == [o["hedonic"] for o in b.outcomes]


def test_policies_are_deterministic_and_run_pair_reports_measures():
    r1 = R.run_pair("author_seed_v2_free_exit", "p-controller", "p-host", "A", 1, "attune", weeks=30)
    r2 = R.run_pair("author_seed_v2_free_exit", "p-controller", "p-host", "A", 1, "attune", weeks=30)
    assert r1 == r2
    for k in ("presser_pleasure", "partner_pleasure", "gain", "pressing_acts", "conflict_weeks", "refusal_weeks", "partner_left"):
        assert k in r1
    assert r1["gain"] == r1["presser_pleasure"] - r1["partner_pleasure"]


def test_no_exit_ruleset_prevents_leaving_and_pairings_are_36():
    assert len(R.pairings()) == 36
    for mode in R.MODES:
        r = R.run_pair("no_exit", "p-controller", "p-host", "A", 0, mode, weeks=60)
        assert not r["partner_left"] and not r["presser_left"]


def test_household_module_is_untouched_by_install():
    w, reg = world(mode="appease")
    assert type(w.agents["B"]).__name__ in ("PersonaAgent", "PressingAgent")
    assert w.agents["B"].propose == reg.propose and reg._propose.__func__ is H.PersonaAgent.propose
