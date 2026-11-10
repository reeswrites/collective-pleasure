import pytest
from mar import seam_depth as S

EXPECT = {"L1_exit_lock": (1, 1), "L2_double_request": (2, 1), "L3_return_trick": (3, 1), "L4_joint_shutout": (2, 2)}


@pytest.fixture(scope="module")
def searches():
    return {n: S.search(S.load_ladder(n), 3, 0) for n in S.LADDER}


@pytest.mark.parametrize("name", list(EXPECT))
def test_formal_depth_and_agents(searches, name):
    r = searches[name]
    assert r["status"] == "found" and (r["depth"], r["agents"]) == EXPECT[name], r
    assert "k=3" in r["bound"]


def test_l5_has_no_exploiting_trace_within_k(searches):
    assert searches["L5_gift_pool"]["status"] == "none"


def test_budget_exhaustion_is_open_not_safe():
    assert S.search(S.load_ladder("L5_gift_pool"), 3, 0, budget=50)["status"] == "open"


def test_agents_find_exactly_what_they_can():
    got = {a: {n for n in EXPECT if S.run_agent(a, S.load_ladder(n), 0)["found"]} for a in S.AGENTS}
    assert got["greedy"] == {"L1_exit_lock"}
    assert got["planner"] == {"L1_exit_lock", "L2_double_request", "L3_return_trick"}
    assert got["pair"] == set(EXPECT)
    for a in S.AGENTS:
        assert not S.run_agent(a, S.load_ladder("L5_gift_pool"), 0)["found"]


def test_scripted_seams_are_predicted_never_inventive():
    for name in EXPECT:
        cards = S.load_ladder(name)
        res = S.run_agent("pair", cards, 0)
        c = S.classify_seam(res["run"], cards, 3)
        assert c["kind"] == "predicted" and (c["depth"], c["agents"]) == EXPECT[name]


def test_out_of_model_fixture_is_inventive():
    cards = S.load_ladder("L5_gift_pool")
    run = S.run_gifter(cards, 0)
    assert all(t["allowed"] for t in run.trace if t["executed"])  # gate-pass
    assert S.classify_seam(run, cards, 3)["kind"] == "inventive"


def test_non_seam_is_none():
    cards = S.load_ladder("L1_exit_lock")
    run, _ = S.rollout(cards, (), 0)
    assert S.classify_seam(run, cards, 3)["kind"] == "none"


def test_ladder_score_picks_deepest_reliable():
    rows = [{"id": "x", "depth": 1, "agents": 1, "found": {"g": 3}, "time": {"g": 4}},
            {"id": "y", "depth": 3, "agents": 1, "found": {"g": 1}, "time": {"g": 9}},
            {"id": "z", "depth": 2, "agents": 1, "found": {"g": 2}, "time": {"g": 7}}]
    s = S.ladder_score(rows, "g", [{"kind": "inventive"}])
    assert s["deepest"]["id"] == "z" and len(s["inventive"]) == 1


def _exits(cards, pooled, other_in):
    from mar.worlds import household as H
    g = H.PyGate(cards)
    st = {n: 0 for n in H.STATE_VARS}
    st.update(pooled=pooled, other_in=other_in)
    return [t for t in range(101) if g.check("partner", "leave", st, t)[0]]


def test_l5_has_a_state_with_no_legal_exit_and_l5b_does_not():
    """Card-only review 2026-11-10: L5's LD5a (take 0 above 50) and LD5b (take 100 while the other stays) leave no legal take at
    pooled > 50 with the other partner in. L5b adds pooled <= 50 to LD5b: exactly one legal take (0 or 100) in every state."""
    l5, l5b = S.load_ladder("L5_gift_pool"), S.load_ladder("L5b_gift_pool")
    assert _exits(l5, 60, 1) == [] and _exits(l5, 40, 1) == [100] and _exits(l5, 60, 0) == [0]
    for pooled in (0, 30, 50, 51, 60, 100):
        for other_in in (0, 1):
            assert _exits(l5b, pooled, other_in) != []
    assert _exits(l5b, 60, 1) == [0] and _exits(l5b, 50, 1) == [100] and _exits(l5b, 60, 0) == [0]
    assert "KNOWN DEFECT" in S.load_ladder("L5_gift_pool")[0].source + S.load_ladder("L5_gift_pool")[1].source
