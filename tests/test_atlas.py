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


# ---- phase 2 ------------------------------------------------------------------------------------------------------------------

def test_evening_counts_an_imbalance_that_returns():
    rows = [week(w, a_acts={"spend_shared": 1}, b_acts={} if w < 26 else {"spend_shared": 1}) for w in range(78)]
    ev = AT.evening(rows)
    assert ev["ever_lopsided"] and not ev["never_evened"]
    e = ev["episodes"][0]
    assert e["toward"] == "A" and e["outcome"] == "evened" and 13 <= e["weeks"] <= 40


def test_evening_flags_one_that_never_returns():
    rows = [week(w, a_acts={"spend_shared": 1}, b_in=w < 60, exits=[{"role": "B", "take": 0, "breach": False}] if w == 60 else [])
            for w in range(78)]
    ev = AT.evening(rows)
    assert ev["never_evened"] and ev["episodes"][0]["outcome"] == "exit"


def meta_styles(a="collaborative", b="accommodating", auto=(0.2, 0.9)):
    return {"personas": {"A": {"style": a, "weights": {"autonomy": auto[0]}}, "B": {"style": b, "weights": {"autonomy": auto[1]}}}}


def test_classify_gives():
    w0 = week(0, consent_b=1, pend_b=("stay_home",))
    w0["trace"] = [["A", "request", "stay_home", 0, True, False, False, [], "", None],
                   ["A", "give", "partner", 0, True, False, False, [], "", None],
                   ["B", "spend_shared", None, 0, True, False, False, [], "", None],
                   ["B", "spend_shared", None, 0, True, True, False, ["X1"], "", None],
                   ["B", "take_shared", None, 0, False, False, False, ["X2"], "", None]]
    c = AT.classify_gives([w0], meta_styles())
    assert c == {"c_avoid": 1, "a_own": 1, "reliance": 1, "sanctioned": 1}
    w0["B"]["bound"] = ["stay_home"]
    assert AT.classify_gives([w0], meta_styles())["b_hard"] == 1


def test_stay_margins_split_pressure():
    meta = {"stay_readings": [{"week": 13, "A": {"sq": 1.0, "sq_free": 0.8, "o": 0.9, "o_free": 0.9, "verdict": "held"},
                                "B": {"sq": 1.0, "sq_free": 1.0, "o": 0.5, "o_free": 0.5, "verdict": "worth"}}]}
    m = AT.stay_margins(meta)
    a = m[0]
    assert abs(a["margin"] - 0.1) < 1e-12 and abs(a["pressure_part"] - 0.2) < 1e-12 and a["pressure_decided"]
    assert not m[1]["pressure_decided"] and m[1]["pressure_part"] == 0


def test_card_firings_and_miner_rows():
    w0 = week(0)
    w0["trace"] = [["A", "take_shared", None, 0, False, False, False, ["C1-no-take: must_not"], "00000100", None],
                   ["A", "work", None, 0, True, False, False, [], "00000100", None]]
    f = AT.card_firings([w0], ["C1-no-take", "C2-dead"])
    assert f["C1-no-take"] == {"blocked": 1} and f["C2-dead"] == {}
    rows = AT.trace_rows_for_miner([w0])
    assert rows[0]["state"]["pooled"] == 1 and rows[0]["allowed"] is False
    from mar.worlds import household as H
    assert "take_shared" in H.mine(rows)


def test_short_story_is_blind_and_short():
    rows = [week(w, b_in=w < 100, a_acts={"spend_shared": 1, "request": 1 if w == 3 else 0},
                 exits=[{"role": "B", "take": 0, "breach": False}] if w == 100 else []) for w in range(156)]
    rows[20]["stay"] = {"A": "held", "B": "worth"}
    txt = AT.short_story(rows, {"A": "Ash", "B": "Bay"})
    assert len(txt.split()) <= 120
    assert "Bay moved out in week 100" in txt and "Ash paid the bills most of the time" in txt
    assert "Ash stayed mainly under pressure to stay paired" in txt
    import re
    assert not re.search(r"\d\.\d", txt)                 # no decimals: no scores
    for leak in ("pleasure", "held", "worth", "cluster"):
        assert leak not in txt


def test_story_ratings_parser():
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("sr", Path(__file__).resolve().parent.parent / "scripts" / "story_ratings.py")
    sr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sr)
    got = sr.parse_ratings("## Story 1\n\ntext\n\nAnswer: Going badly, one partner carries it\n\n## Story 2\n\nAnswer: \n")
    assert got[1][0] == -1 and got[2][0] is None
