"""H39 makers (src/mar/makers.py; docs/results/h39-makers-prereg.md): off-switch reproduction, traits, and the prereg's known-answer
cases. Scripted agents, no model calls."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from mar import makers as MK  # noqa: E402
from mar import retest as RT  # noqa: E402

PS = RT.personas()


def _play(a, b, seed, cfg, weeks=60, rule=None):
    import h38_pairing_run as H38
    from mar import pairing as PR
    with MK.use_makers(cfg):
        run, lived, _ = H38.play(PR.dial(0), a, b, seed, stay=False, weeks=weeks,
                                 rule=rule or {"decide_on": "weighted", "decide_weeks": 52})
    return run, lived


def _pl(run):
    return sum(o["hedonic"][r]["pleasure"] for o in run.outcomes for r in "AB") / (2 * len(run.outcomes))


@pytest.mark.slow
def test_makers_off_reproduces_pinned_fingerprints():
    import makers_fingerprint as MF
    pinned = json.loads((ROOT / "tests" / "data" / "makers_off_fingerprints.json").read_text())
    assert MF.fingerprints() == pinned


def test_traits_fixed_and_spread():
    ids = sorted(PS)
    t = [MK.traits(PS[i], MK.DEFAULT) for i in ids]
    assert t == [MK.traits(PS[i], MK.DEFAULT) for i in ids]
    assert {x["kind"] for x in t} == set(MK.KINDS)
    assert {x["e"] for x in t} == set(MK.ENJOY)
    assert {x["aim"] for x in t} == {"safe", "extractive"}
    ws = sorted(x["w"] for x in t)
    assert 0 <= ws[0] and ws[-1] <= 4
    assert 0.6 < ws[len(ws) // 2] < 1.6            # median near 1


def test_w_independent_of_risk_tolerance():
    import numpy as np
    xs = [(PS[i].risk_tolerance, MK.suffering_weight(PS[i])) for i in PS]
    r = np.corrcoef(*zip(*xs))[0, 1]
    assert abs(r) < 0.35


def test_weighted_rule_w0_equals_pleasure_rule():
    """With every w at 0 the weighted score is the pleasure score (checked on one stretch of weeks)."""
    from mar import hedonic as HD
    from mar import negotiation as NG
    rows = [{"hedonic": {"A": {"pleasure": 0.9, "s_off": 0.2, "s_non": 0.1}}}]
    p = PS["p-anchor"]
    with HD.use_fixes(HD.FixConfig(decide_on="weighted")):
        v = NG.wellbeing(rows, "A", p)
    assert v == pytest.approx(0.9 - MK.suffering_weight(p) * 0.3)


def test_known_answer_free_making_adds_pleasure():
    """Known answer 1: making with no time cost, by caring personas, adds pleasure over makers off (nobody leaves in 30 weeks)."""
    a, b = "p-anchor", "p-host"
    off, _ = _play(a, b, 0, None, weeks=30)
    on, lived = _play(a, b, 0, MK.config("zero", time_cost=0.0), weeks=30)
    assert sum(lived.world.makers["blocks"].values()) > 0
    assert _pl(on) > _pl(off) or _pl(off) >= 0.999


def test_known_answer_worthless_making_is_not_made():
    """Known answer 2: if no block is worth anything, nothing is made and the run equals makers off."""
    a, b = "g-00000", "g-11111"
    cfg = MK.config("hours", cook=0.0, care=0.0, care_low=0.0, art_weekly=0.0, proc=0.0, kappa=0.0, cue=0.0, goal=0.0)
    off, _ = _play(a, b, 1, None, weeks=30)
    on, lived = _play(a, b, 1, cfg, weeks=30)
    assert sum(lived.world.makers["blocks"].values()) == 0
    assert [o["hedonic"] for o in on.outcomes] == [o["hedonic"] for o in off.outcomes]


def test_known_answer_credit_inert_without_motive_or_exit():
    """Known answer 3: with kappa = 0, C-zero and C-hours differ only at an exit split; a run with no exit is identical."""
    a, b = "p-anchor", "p-host"
    z, lz = _play(a, b, 0, MK.config("zero", kappa=0.0), weeks=40)
    h, lh = _play(a, b, 0, MK.config("hours", kappa=0.0), weeks=40)
    if not lz.world.exit_log and not lh.world.exit_log:
        assert [o["hedonic"] for o in z.outcomes] == [o["hedonic"] for o in h.outcomes]


class _W:
    """A minimal world for the making choice."""

    def __init__(self, maker, receiver, aim, kind="cook"):
        from mar import hedonic as HD
        self.personas = {"A": PS[maker], "B": PS[receiver]}
        self.p = {r: {"in": True, "ill": 0, "jobless": 0, "money": 10} for r in "AB"}
        self.hed = {r: HD.Hedonic(self.personas[r], HD.DEFAULT) for r in "AB"}
        self.makers = MK.init_world(self) if MK.ACTIVE else None
        self.makers["traits"]["A"].update(kind=kind, aim=aim, e=0.5)

    def other(self, r):
        return "B" if r == "A" else "A"


def test_known_answer_extractive_makes_more_liked_less():
    """Known answer 4: against a sensitized, tolerant receiver, an extractive maker makes more blocks than a safe one, and each
    block is liked less than a fresh one."""
    with MK.use_makers(MK.config("zero")):
        safe, ext = _W("p-anchor", "p-host", "safe"), _W("p-anchor", "p-host", "extractive")
    for w in (safe, ext):
        w.makers["recv"]["B"].update(h=3, s=8)
    assert MK.choose_blocks(ext, "A") > MK.choose_blocks(safe, "A")
    assert MK.block_like(ext, "A", 1) < MK.block_like(ext, "A", 1, {"h": 0, "s": 0, "n": 0})


def test_credit_rules():
    with MK.use_makers(MK.config("zero")):
        w = _W("p-anchor", "p-host", "safe")
    st, cfg = w.makers, w.makers["cfg"]
    st["blocks"]["A"], st["liking_given"]["A"] = 10, 0.25
    assert MK.credit(w, "A", "zero") == 0
    assert MK.credit(w, "A", "hours") == pytest.approx(13.75)
    assert MK.credit(w, "A", "pleasure") == pytest.approx(13.75)      # 0.25 = 10 typical blocks
    assert MK.credit(w, "A", "bp") == pytest.approx(13.75)
    st["liking_given"]["A"] = 0.125
    assert MK.credit(w, "A", "bp") == pytest.approx(0.5 * 13.75 + 0.5 * 6.875)
    assert MK.credit(w, "A", "gift") == MK.credit(w, "A", "bp")


def test_motive_only_under_running_tally():
    with MK.use_makers(MK.config("zero", time_cost=0.012)):
        w = _W("p-anchor", "p-host", "safe")
    n = {rule: MK.choose_blocks(w, "A", rule) for rule in ("zero", "gift", "hours", "bp")}
    assert n["zero"] == n["gift"]
    assert n["hours"] >= n["zero"]


def test_protection_raises_perceived_completion():
    with MK.use_makers(MK.config("bp", protect="negotiated")):
        w = _W("p-anchor", "p-host", "safe", kind="artist")
    w.exit_log, w.bar_out, w.trust, w.weeks = [1], {"A": False, "B": False}, {"A": 0.7, "B": 0.7}, 156
    lo, _ = MK.project_values(w, "A", 0, False)
    hi, _ = MK.project_values(w, "A", 0, True)
    assert hi > lo


def test_contribution_share_includes_credit_and_protected_project():
    from mar import exit_fallback as EF
    with MK.use_makers(MK.config("hours")):
        w = _W("p-anchor", "p-host", "safe", kind="artist")
    w.money_in = {"A": 50, "B": 50}
    w.makers["blocks"]["A"] = 10
    assert EF.contribution_share(w, "A", "all") == pytest.approx((50 + 13.75) / 113.75)
    w.makers["project"]["A"] = {"done": 4, "protected": True, "from": 0}
    # B leaving: A's protected project counts for A; A leaving: it does not
    assert EF.contribution_share(w, "B", "all") == pytest.approx(50 / (113.75 + 5.5))
    assert EF.contribution_share(w, "A", "all") == pytest.approx((50 + 13.75) / 113.75)


# ---- H39b (docs/results/h39b-makers-rerun-prereg.md) -------------------------------------------------------------------------

@pytest.mark.slow
def test_flat_cost_reproduces_h39_fingerprints():
    """choice="flat_cost" (the default) is H39's making choice, bit-identical to commit 2b8a100."""
    import makers_fingerprint as MF
    pinned = json.loads((ROOT / "tests" / "data" / "makers_flatcost_fingerprints.json").read_text())
    assert MF.flat_cost_fps() == pinned


def _opp(**kw):
    return MK.config("zero", choice="opportunity", enjoy=MK.ENJOY_H39B, **kw)


def _stub(cfg, maker="p-anchor", receiver="p-host", aim="safe", kind="cook", e=0.0, care=None, money=None):
    import copy
    with MK.use_makers(cfg):
        w = _W(maker, receiver, aim, kind)
    w.makers["traits"]["A"]["e"] = e
    if care is not None or money is not None:
        p = copy.deepcopy(w.personas["A"])
        if care is not None:
            p.weights["togetherness"] = care
        if money is not None:
            p.weights["money"] = money
        w.personas["A"] = p
    w.units = {"A": 10, "B": 10}
    return w


IDLE = {"work": 0.05}                       # one work block planned per pass: 4 + 4 units, 2 idle
BOOKED = {"work": 0.30, "rest": 0.25, "together": 0.20, "see_friend": 0.15, "spend_self": 0.12, "spend_shared": 0.11}


def test_known_answer_k1_no_enjoyment_no_care_never_makes():
    """K1: enjoyment 0, care 0, safe, no tally: never makes, even with the whole week idle."""
    w = _stub(_opp(), e=0.0, care=0.0)
    assert MK.choose_blocks(w, "A", util={}) == 0
    assert MK.choose_blocks(w, "A", util=IDLE) == 0


def test_known_answer_k2_enjoyment_and_free_time_makes():
    """K2: enjoyment +1 and idle units: makes at least one block (here: the 2 idle units)."""
    w = _stub(_opp(), e=1.0, care=0.0)
    assert MK.choose_blocks(w, "A", util=IDLE) == 2
    assert MK.choose_blocks(w, "A", util={}) == 3


def test_known_answer_k3_booked_week_makes_nothing_flat_cost_would():
    """K3: every unit is planned for something worth more than a block: nothing is made under "opportunity"; the flat cost,
    which cannot see what is displaced, makes with the same values."""
    w = _stub(_opp(), e=1.0, care=1.0)
    assert sum(v for v, _ in MK.block_values(w, "A")[:1]) < 0.11
    assert MK.choose_blocks(w, "A", util=BOOKED) == 0
    wf = _stub(MK.config("zero"), e=1.0, care=1.0)
    assert MK.choose_blocks(wf, "A") > 0


def test_known_answer_k4_bills_unit_kept_unless_block_worth_more():
    """K4: work twice and one unit into unpaid bills fill 9 units. A modest block takes the idle unit, and the week left keeps
    paying into the bills; a second block costs the agent 0.1 of its own utility, so only a block worth more than that is made."""
    util = {"work": 0.30, "spend_shared": 0.20}
    assert MK.plan_week(util, 10)[1] == ["work", "work", "spend_shared"]
    w = _stub(_opp(), e=1.0, care=1.0)
    n, info = MK.opportunity(w, "A", util=util)
    assert n == 1 and info["displaced"] == [] and info["alt"] == 0.0
    assert "spend_shared" in MK.plan_value(util, 9)[1]
    assert MK.plan_value(util, 8)[0] == pytest.approx(0.7)      # V never falls below what fewer units could do
    rich = _stub(_opp(cook=0.5), e=1.0, care=1.0)
    n, info = MK.opportunity(rich, "A", util=util)
    assert n >= 2 and info["alt"] == pytest.approx(0.1)


def test_known_answer_k5_trap_only_with_extractive_maker():
    """K5: a receiver whose partner makes 3 blocks every week reaches the trap state with an extractive maker, never with a safe one."""
    out = {}
    for aim in ("safe", "extractive"):
        w = _stub(_opp(), aim=aim, e=1.0, care=1.0)
        w.agents = None
        w.exit_log, w.bar_out, w.trust, w.weeks = [], {"A": False, "B": False}, {"A": 0.7, "B": 0.7}, 156
        w.makers["traits"]["B"].update(kind="cook", aim="safe", e=-1.0)
        w.personas["B"] = w.personas["B"]
        orig = MK.opportunity
        MK.opportunity = lambda world, m, *a, **k: ((3, {"n": 3, "alt": 0.0, "parts": {}, "displaced": [], "plan": []}) if m == "A"
                                                    else (0, {"n": 0, "alt": 0.0, "parts": {}, "displaced": [], "plan": []}))
        try:
            for wk in range(20):
                w.units = {"A": 10, "B": 10}
                MK.week_start(w, wk)
        finally:
            MK.opportunity = orig
        out[aim] = w.makers["trap_weeks"]["B"]
    assert out["extractive"] > 0
    assert out["safe"] == 0


def test_known_answer_k6_lost_liking_zero_below_dose():
    """K6: one block a week stays below the tolerance dose (2): no liking is lost; three a week raise tolerance and lose liking."""
    out = {}
    for n in (1, 3):
        w = _stub(_opp(), e=1.0, care=1.0)
        w.exit_log, w.bar_out, w.trust, w.weeks = [], {"A": False, "B": False}, {"A": 0.7, "B": 0.7}, 156
        orig = MK.opportunity
        MK.opportunity = lambda world, m, *a, _n=n, **k: ((_n if m == "A" else 0),
                                                          {"n": 0, "alt": 0.0, "parts": {}, "displaced": [], "plan": []})
        try:
            for wk in range(10):
                w.units = {"A": 10, "B": 10}
                MK.week_start(w, wk)
        finally:
            MK.opportunity = orig
        out[n] = w.makers["lost_tol"]["B"]
    assert out[1] == 0.0
    assert out[3] > 0.0


def test_enjoyment_levels_keep_rank():
    for pid in PS:
        a, b = MK.traits(PS[pid], MK.DEFAULT), MK.traits(PS[pid], _opp())
        assert a["e_rank"] == b["e_rank"] and MK.ENJOY_H39B[b["e_rank"]] == b["e"] and MK.ENJOY[a["e_rank"]] == a["e"]
        assert {k: v for k, v in a.items() if k != "e"} == {k: v for k, v in b.items() if k != "e"}


def test_opportunity_in_the_world_runs_and_never_reads_time_cost():
    """In a real run, the opportunity choice gives the same run whatever time_cost says (it is not read)."""
    a, b = "p-anchor", "p-host"
    r1, l1 = _play(a, b, 0, _opp(), weeks=30)
    r2, l2 = _play(a, b, 0, _opp(time_cost=5.0), weeks=30)
    assert [o["hedonic"] for o in r1.outcomes] == [o["hedonic"] for o in r2.outcomes]
    assert l1.world.makers["dec"]["maker_weeks"] > 0


def test_known_answer_k7_partner_sessions_use_the_makers_units():
    """K7: units the maker's own plan leaves idle are not free when the partner plans time together (a session uses both partners'
    units): with the partner planning three sessions (6 of the maker's units), the maker's own work block fits only in the 4 left, so
    taking 3 of them for making displaces the work block."""
    mine = {"work": 0.30, "together": 0.08}
    partner = {"together": 0.5}
    w = _stub(_opp(), e=1.0, care=1.0)
    n_alone, info_alone = MK.opportunity(w, "A", util=mine)
    assert info_alone["alt"] == 0.0
    V0 = MK.plan_value(mine, 10, partner_sessions=3)
    assert V0[1].count("partner_together") == 3
    V1 = MK.plan_value(mine, 7, partner_sessions=3)
    assert V0[0] == pytest.approx(0.30 + 3 * 0.08)
    assert V0[0] - V1[0] == pytest.approx(0.30)
    n, info = MK.opportunity(w, "A", util=mine, partner_util=partner)
    assert n <= n_alone
