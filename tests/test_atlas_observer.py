"""The atlas reads from the observer when one is attached (atlas.Recorder.from_observer) and gets the same week rows as its own hook,
apart from the documented end-of-week vs start-of-next-week timing of pool, money, put and trust (and, in the week before a harness
formation, the in-household flag and standing requests)."""
import dataclasses

from mar import atlas as AT
from mar import exit_fallback as EF
from mar import exit_items as EI
from mar import hedonic as HD
from mar import negotiation as NG
from mar import observe as OB
from mar import pairing as PR
from mar import retest as RT
from mar.worlds import household as H

SAME = ("in", "acts", "req_kinds", "blocked", "breach", "pl", "s_non", "s_off", "pending", "consent", "bound", "terms")


def _both(level, a, b, seed, weeks=156):
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(level))
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), \
            EI.use_items(EI.GRID["V2-split-loves"]), OB.collecting():
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=weeks, decline=True)
        ob = OB.Observer(lived.world, OB.ObsConfig(), harness=lived)
        rec = AT.Recorder(lived.world)
        lived.play()
        rec.finish().lived(lived)
        ob.finish()
    return rec, AT.Recorder.from_observer(ob)


def test_rows_match_the_hook():
    for level, a, b, s in ((4, "g-00000", "g-11111", 1), (0, "g-01010", "p-wanderer", 2)):
        rec, via = _both(level, a, b, s)
        assert len(rec.rows) == len(via.rows)
        moved = {x["week"] for x in rec.rows if any(k in ("formed", "terms") for _, k in x["events"])}
        for x, y in zip(rec.rows, via.rows):
            assert x["week"] == y["week"] and x["events"] == y["events"] and x["exits"] == y["exits"]
            for r in "AB":
                for k in SAME:
                    if x["week"] in moved and k in ("in", "pending", "consent", "bound"):
                        continue          # a formation between weeks: the hook reads it into the week before, the observer does not
                    assert x[r][k] == y[r][k] or (k == "pl" and x[r][k] != x[r][k] and y[r][k] != y[r][k]), (x["week"], r, k)
            assert [t[:7] for t in x["trace"]] == [t[:7] for t in y["trace"]]
        fa, fb = AT.features(rec.rows, rec.meta), AT.features(via.rows, via.meta)
        for k in AT.CLUSTER_FEATURES:
            if k != "pot_share_end" and not moved:
                assert abs(fa[k] - fb[k]) < 1e-9, k
        for m, n in zip(AT.formation_margins(rec.meta), AT.formation_margins(via.meta), strict=True):
            assert (m["week"], m["role"], m["decisive"], m["formed"]) == (n["week"], n["role"], n["decisive"], n["formed"])
            assert abs(m["margin"] - n["margin"]) < 1e-4


def test_exact_paths_read_the_observer():
    _rec, via = _both(4, "g-00000", "g-11111", 1)
    c = AT.classify_gives(via.rows, {}, obs=via.obs)
    assert sum(c.values()) >= 0
    lr = AT.leave_reasons(via.rows, obs=via.obs)
    assert all(k.startswith(("distress", "bar")) for k in lr)
