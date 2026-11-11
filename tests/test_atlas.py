"""Pattern atlas (src/mar/atlas.py): features on hand-made week rows, clustering helpers, and the recorder on a real world."""
import numpy as np

from mar import atlas as AT


def week(w, a_in=True, b_in=True, a_acts=None, b_acts=None, pl=(0.9, 0.9), exits=(), events=(), pend_b=(), consent_b=0, mi=(10, 10)):
    def side(i_n, acts, p, pend, cons, m):
        return {"in": i_n, "acts": dict(acts or {}), "req_kinds": {}, "blocked": 0, "breach": 0, "pl": p, "s_non": 0.0, "s_off": 0.0,
                "money": 5, "put": 5, "money_in": m, "trust": 1.0, "pending": list(pend), "consent": cons, "bound": [], "terms": {}}
    return {"week": w, "pool": 10, "events": [list(e) for e in events], "exits": list(exits), "trace": [],
            "A": side(a_in, a_acts, pl[0], (), 0, mi[0]), "B": side(b_in, b_acts, pl[1], pend_b, consent_b, mi[1])}


def test_steady_household_has_no_exit_and_even_giving():
    rows = [week(w, a_acts={"spend_shared": 1}, b_acts={"spend_shared": 1}) for w in range(52)]
    f = AT.features(rows)
    assert f["together_share"] == 1.0 and f["first_exit"] == 1.0 and f["leaves"] == 0
    assert f["give_asym"] == 0.0 and abs(f["give_drift"]) < 1e-12
    assert f["spikes"] == 0 and f["repair"] == 1.0 and f["who_exits"] == ""
    assert set(AT.CLUSTER_FEATURES) <= set(f)


def test_drifting_bargain_and_early_exit():
    rows = []
    for w in range(52):
        a = {"spend_shared": 1}
        b = {"spend_shared": 1} if w < 13 else {}
        rows.append(week(w, b_in=w < 40, a_acts=a, b_acts=b, mi=(30, 10),
                         exits=[{"role": "B", "take": 50, "breach": False}] if w == 40 else []))
    f = AT.features(rows)
    assert f["give_drift"] > 0                       # A's share of giving grows: the bargain drifts one-sided
    assert f["give_asym"] > 0.5
    assert abs(f["first_exit"] - 40 / 52) < 1e-9 and f["who_exits"] == "taker"
    assert f["pot_share_end"] == 0.75


def test_requests_refusals_and_give_in():
    rows = [week(w, a_acts={"request": 1} if w % 4 == 0 else {}, b_acts={"refuse_request": 1} if w % 8 == 0 else {},
                 pend_b=("stay_home",) if w % 4 == 0 else (), consent_b=1 if w % 8 == 4 else 0) for w in range(32)]
    f = AT.features(rows)
    assert f["init_asym"] == 1.0
    assert abs(f["refusal_rate"] - 0.5) < 1e-9      # A asked 8 times, B refused 4
    assert abs(f["give_in_rate"] - 0.5) < 1e-9


def test_spike_and_repair():
    pl = [0.9] * 10 + [0.7] + [0.9] * 10
    sp, rep = AT.spikes_and_repair(np.array(pl), [True] * len(pl))
    assert sp == [10] and rep == [True]
    pl2 = [0.9] * 10 + [0.7] * 11
    sp2, rep2 = AT.spikes_and_repair(np.array(pl2), [True] * len(pl2))
    assert sp2 == [10] and rep2 == [False]


def test_kmedoids_finds_separated_groups_and_is_stable():
    rng = np.random.default_rng(0)
    Z = np.vstack([rng.normal(0, 0.1, (20, 2)), rng.normal(5, 0.1, (20, 2)), rng.normal((0, 5), 0.1, (20, 2))])
    D = AT.dist(Z)
    lab, med, _ = AT.best_kmedoids(D, 3)
    truth = np.repeat([0, 1, 2], 20)
    assert AT.ari(lab, truth) == 1.0
    assert AT.silhouette(D, lab) > 0.9
    k, sil = AT.choose_k(Z, ks=range(2, 6))
    assert k == 3
    st = AT.stability(Z, 3, lab, reps=5)
    assert min(st["ari"]) == 1.0 and all(v == 1.0 for v in st["jaccard"].values())


def test_ari_and_lift():
    assert AT.ari([0, 0, 1, 1], [1, 1, 0, 0]) == 1.0
    assert AT.ari([0, 0, 1, 1], [0, 1, 0, 1]) < 0
    lf = AT.lift([0, 0, 0, 1], ["x", "x", "y", "y"], 0)
    assert lf["x"][:2] == (2, 2) and abs(lf["x"][2] - 4 / 3) < 1e-12     # 2 of 3 in the cluster vs 2 of 4 overall


def test_story_reads_rows():
    rows = [week(w, b_in=w < 20, a_acts={"spend_shared": 1}, exits=[{"role": "B", "take": 0, "breach": False}] if w == 20 else [])
            for w in range(26)]
    lines = AT.story(rows, names={"A": "Ana", "B": "Bo"})
    assert len(lines) == 2 and lines[0].startswith("Weeks 0-12: together")
    assert "week 20: Bo left" in lines[1] and "Ana put in 13" in lines[1]


def test_recorder_matches_plain_run_and_ignores_copies():
    """The recorder only reads: a recorded run equals the plain run, and deep copies (rollouts) write nothing."""
    import copy

    from mar import retest as RT
    from mar.worlds import household as H
    ps = RT.personas()
    a, b = RT.sample(0, 38)[0]
    cards = H.load_variant("baseline")
    plain = H.WeeklyWorld(H.PyGate(cards), (ps[a], ps[b]), 3, 30).play()
    world = H.WeeklyWorld(H.PyGate(cards), (ps[a], ps[b]), 3, 30)
    rec = AT.Recorder(world)
    last = {"busy": {"A": False, "B": False}}
    for w in range(10):
        last = {"busy": world.step_week(w, last)}
    c = copy.deepcopy(world)
    lc = dict(last)
    for w in range(10, 14):
        lc = {"busy": c.step_week(w, lc)}
    n = len(rec.rows)
    for w in range(10, 30):
        last = {"busy": world.step_week(w, last)}
    rec.finish()
    assert n == 9 and len(rec.rows) == 30
    assert [o["hedonic"] for o in world.run.outcomes] == [o["hedonic"] for o in plain.outcomes]
    assert [r["week"] for r in rec.rows] == list(range(30))
    f = AT.features(rec.rows, rec.meta)
    assert all(np.isfinite(f[k]) for k in AT.CLUSTER_FEATURES)
