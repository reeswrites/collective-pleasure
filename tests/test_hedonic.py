from pathlib import Path

from mar import hedonic as Hd
from mar import personas as P

ROOT = Path(__file__).resolve().parent.parent / "personas"


def agent(pid="p-host", cfg=Hd.DEFAULT):
    return Hd.Hedonic(P.load(ROOT / f"{pid}.yaml"), cfg)


def good(a, weeks=1, **kw):
    """A week in which everything is going well."""
    for _ in range(weeks):
        a.tick(rest_actions=1, friend_visits=1, together=1, assets=60, money=12)
        row = a.close_week({k: 10 * v for k, v in a.targets.items()}, together_sessions=1, **kw)
    return row


def bad(a, weeks=1):
    for _ in range(weeks):
        a.tick(work_blocks=2, cohabiting=True, assets=0, money=0)
        row = a.close_week({k: 0 for k in a.targets})
    return row


def test_salience_and_importances_are_normalised():
    a = agent()
    assert abs(sum(a.sal.values()) - 1) < 1e-9 and abs(sum(a.asp_w.values()) - 1) < 1e-9


def test_rest_decays_without_rest_and_holds_with_it():
    a = agent()
    for _ in range(4):
        a.tick(assets=30, money=8)
    assert a.level["rest"] < 0.4
    b = agent()
    for _ in range(8):
        b.tick(rest_actions=1, assets=30, money=8)
    assert b.level["rest"] > 0.7


def test_tipping_point_amplifies_in_both_directions():
    up, down = agent(), agent()
    up.B, down.B = 0.05, -0.05
    for _ in range(40):
        up.tick(rest_actions=1, friend_visits=1, together=1, assets=60, money=12)
        up.close_week({k: 10 * v for k, v in up.targets.items()}, together_sessions=1)
        down.tick(work_blocks=2, assets=0, money=0)
        down.close_week({k: 0 for k in down.targets})
    assert up.B > 0.5 and down.B < -0.5


def test_feedback_is_zero_at_tip_and_stronger_below():
    assert Hd.feedback(0.0) == 0
    assert abs(Hd.feedback(-0.5)) > Hd.feedback(0.5)


def test_capacity_rises_with_B_and_falls_with_N():
    assert Hd.capacity(0.8, 0) > Hd.capacity(0, 0) > Hd.capacity(-0.8, 0)
    assert Hd.capacity(0.5, 0.8) < Hd.capacity(0.5, 0)


def test_non_offsettable_is_not_cancelled_by_pleasure_and_needs_removal():
    a = agent()
    rows = [good(a, trapped=True) for _ in range(8)]
    assert rows[2]["s_non"] == 0 and rows[3]["s_non"] > 0           # onset at 4 weeks
    assert rows[-1]["pleasure"] > 0.5 and rows[-1]["s_non"] > 0      # pleasure does not remove it
    assert a.max_nonoff_run >= 5 and a.N > 0 and rows[-1]["capacity"] < Hd.capacity(a.B, 0)
    row = good(a, trapped=False)                                     # removing the cause removes it
    assert row["s_non"] == 0 and a.nonoff_run == 0


def test_pre_onset_hardship_is_offsettable():
    a = agent()
    row = good(a, restricted=True)
    assert row["s_non"] == 0 and row["s_off"] > 0


def test_need_denied_for_weeks_becomes_non_offsettable():
    a = agent()
    rows = [bad(a) for _ in range(6)]
    assert rows[-1]["s_non"] > 0 and rows[-1]["conditions"]["denied"]


def test_new_connection_glow_decays():
    a = agent()
    a.event_new_connection()
    g1 = a.glow
    good(a)
    assert 0 < a.glow < g1
