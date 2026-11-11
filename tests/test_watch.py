"""Household replay viewer (src/mar/watch.py, docs/notes/viewer.md): run keys, the mood mapping, event wording, decision cards, the
page's constraints, and one real run end to end (re-run with the observer on, as `mar watch` does when no observer file exists)."""
import json
import re

import pytest

from mar import watch as WT

NAMES = {"A": "Kit", "B": "Hollis"}


def _state(w, r, **kw):
    s = {"w": w, "r": r, "in": True, "money": 10.0, "levels": {"rest": 0.6, "connection": 0.8, "money": 0.5, "security": 0.7},
         "cond_run": {"trapped": 0, "denied": 0, "diminished": 0}, "low": 0, "trust": 0.7, "N": 0.0, "pl": 0.95,
         "wk": {"friends": 1}}
    s.update(kw)
    return s


# ---- run keys ------------------------------------------------------------------------------------------------------------------

def test_norm_key_accepts_short_full_and_atlas_forms():
    assert WT.norm_key("h38", "L0|a|b|1") == "h38|L0|a|b|1"
    assert WT.norm_key("h38", "h38|L0|a|b|1") == "h38|L0|a|b|1"
    assert WT.norm_key("h38", "L4|a|b") == "h38|L4|a|b|0"
    assert WT.norm_key("ef", "F0|author_seed_v23_bindable|21") == "ef|F0|author_seed_v23_bindable|21"
    assert WT.norm_key("ef", "ef|F0|author_seed_v23_bindable|21|0") == "ef|F0|author_seed_v23_bindable|21"   # atlas key
    with pytest.raises(ValueError):
        WT.norm_key("ef", "F0|x")
    with pytest.raises(ValueError):
        WT.norm_key("fishery", "a|b")


def test_names_are_fixed_by_persona_and_distinct():
    p = {"A": {"id": "g-10011"}, "B": {"id": "g-11011"}}
    n1, n2 = WT.names_for(p), WT.names_for(p)
    assert n1 == n2 and n1["A"] != n1["B"]
    assert WT.names_for({"A": {"id": "x"}, "B": {"id": "x"}})["A"] != WT.names_for({"A": {"id": "x"}, "B": {"id": "x"}})["B"]


# ---- mood mapping --------------------------------------------------------------------------------------------------------------

def test_mood_reads_component_states():
    m = WT.mood(_state(3, "A"), {"targets": {"friends_per_week": 0.66}})
    assert m["lonely"] == pytest.approx(0.2) and m["lonely_w"] == "not lonely"
    assert m["stress"] == pytest.approx(0.4) and m["stress_w"] == "a little worried about money"
    assert m["content"] == pytest.approx(0.95) and m["content_w"] == "content"
    assert m["trust"] == pytest.approx(0.7) and m["trust_w"] == "trusts"
    assert m["distress"] == 0 and m["distress_w"] == "no lasting hurt"
    assert m["friends"] == 1 and m["friends_want"] == 0.66
    assert "trap" not in m                                   # no wanting-trap row without maker data


def test_mood_bad_week():
    s = _state(9, "B", levels={"rest": 0.1, "connection": 0.2, "money": 0.05, "security": 0.1}, trust=0.3, N=0.25, pl=0.6,
               cond_run={"trapped": 0, "denied": 5, "diminished": 0}, low=4)
    m = WT.mood(s)
    assert m["lonely_w"] == "lonely" and m["stress_w"] == "stressed about money"
    assert m["content_w"] == "unhappy" and m["trust_w"] == "does not trust"
    assert m["distress_w"] == "in distress" and m["distress"] == pytest.approx(0.625)
    assert m["denied"] == 5 and m["low"] == 4
    assert m["short"] == ["money", "rest", "a sense of security"]      # needs under 0.15, worst first


def test_mood_wanting_trap_when_recorded():
    m = WT.mood(_state(0, "A", want={"tol": 0.1, "sens": 0.6}))
    assert m["trap"] == pytest.approx(0.6) and m["trap_w"] == "in a wanting trap"


# ---- events --------------------------------------------------------------------------------------------------------------------

def _tables():
    weeks = [{"w": w, "pool": 50.0, "both_in": w < 5, "pre_events": [], "events": [], "exits": [], "shocks": []} for w in range(8)]
    weeks[5]["events"] = [["B", "leave_bar"]]
    weeks[5]["exits"] = [{"week": 5, "role": "B", "take": 50, "breach": False}]
    weeks[2]["shocks"] = [{"week": 2, "kind": "job_loss", "role": "A", "duration": 8}]
    return {
        "run": [{"run_key": "h38|L0|a|b|0", "pair_key": "a|b|0", "weeks": 8, "meta": {"family": "h38", "arm": "L0"},
                 "personas": {"A": {"id": "a", "targets": {"friends_per_week": 0.5}}, "B": {"id": "b"}}, "items": True}],
        "week": weeks,
        "state": [_state(w, r, **({"in": False} if r == "B" and w >= 5 else {})) for w in range(8) for r in "AB"],
        "consent": [{"w": 1, "asker": "A", "receiver": "B", "kind": "time", "answer": False, "bound": False},
                    {"w": 2, "asker": "B", "receiver": "A", "kind": "stay_home", "answer": True, "bound": True}],
        "flow": [{"w": 3, "src": "A", "dst": "bills", "amt": 3.0, "cause": "spend_shared", "actor": "A"},
                 {"w": 4, "src": "A", "dst": "bills", "amt": 2.0, "cause": "spend_shared", "actor": "A"},
                 {"w": 4, "src": "B", "dst": "bills", "amt": 1.0, "cause": "spend_shared", "actor": "B"},
                 {"w": 3, "src": "B", "dst": "A", "amt": 2.0, "cause": "give_partner", "actor": "B"},
                 {"w": 4, "src": "pot", "dst": "A", "amt": 5.0, "cause": "take_shared", "actor": "A"},
                 {"w": 5, "src": "pot", "dst": "B", "amt": 24.4, "cause": "leave", "actor": "B"}],
        "item": [{"w": -1, "holders": {"home": "both", "pet": "both"}, "prev": None, "cause": "start"},
                 {"w": 5, "holders": {"home": "A", "pet": "B"}, "prev": {"home": "both", "pet": "both"}, "cause": "exit"}],
        "reading": [{"kind": "formation0", "w": 0, "formed": True, "m": {r: {
            "W": 0.8, "O": 0.7, "margin": 0.1, "W_parts": {"partner": 0.3, "money": 0.1}, "O_parts": {"partner": 0.1, "money": 0.2}}
            for r in "AB"}},
            {"kind": "reading", "w": 5, "bar_out": {"A": False, "B": True}, "bar_runs": {"A": 0, "B": 2}, "exit_anticipation": 0.0,
             "m": {"A": {"W": 0.8, "O": 0.7, "margin": 0.1, "W_parts": {"partner": 0.3}, "O_parts": {"partner": 0.2}},
                   "B": {"W": 0.5, "O": 0.7, "margin": -0.2, "W_parts": {"money": 0.2, "friends": 0.0},
                         "O_parts": {"money": 0.05, "friends": 0.35}}}}],
        "stay": [{"w": 5, "A": {"verdict": "worth"}, "B": {"verdict": "leave"}}],
        "decision": [{"w": 5, "r": "B", "k": 0, "chosen": 0, "runner": 1, "margin": 0.01, "cands": [
            {"a": "leave", "u": 0.9, "st": "chosen", "take": 50, "parts": {"policy": 0.9}},
            {"a": "leave", "u": 0.89, "st": "open", "take": 25, "parts": {"policy": 0.89}},
            {"a": "rest", "u": 0.1, "st": "open", "parts": {"rest": 0.11, "noise": -0.01}}],
            "leave_ctx": {"bar": True, "N": 0.0, "low_weeks": 0, "trust": 0.7, "cond_run": {"denied": 0}}}],
        "replay": [{"w": 5, "kind": "stay", "r": "B", "window": 13, "faithful": True,
                    "alt": {"exits": []}, "diff": {"A": {"net": 0.05}, "B": {"net": -0.12}}}],
        "together": [{"w": 1, "initiator": "A", "partner": "B", "accepted": True}],
    }


def test_event_wording():
    ev = WT.events(_tables(), NAMES)
    txt = [(e["w"], e["text"]) for e in ev]
    assert (1, "Kit asked Hollis for time together; Hollis said no") in txt
    assert (2, "Hollis asked Kit to stay home; Kit said yes (an earlier agreement bound them)") in txt
    assert (2, "Kit lost their job (for 8 weeks)") in txt
    assert (3, "Kit covered the bill (3)") in txt
    assert (3, "Hollis gave Kit 2") in txt
    assert (4, "Both paid toward the bills (Kit 2, Hollis 1)") in txt
    assert (4, "Kit took 5 from the shared pot") in txt
    assert (5, "Hollis moved out (the outside option looked better), taking 24 from the shared pot") in txt
    assert (5, "The home stayed with Kit; the pet stayed with Hollis") in txt
    assert (5, "Check-in: Kit wants to stay; Hollis would rather leave") in txt
    assert (0, "Kit and Hollis moved in together") in txt
    assert [e["w"] for e in ev] == sorted(e["w"] for e in ev)
    lvl = {e["text"]: e["lvl"] for e in ev}
    assert lvl["Kit covered the bill (3)"] == 3 and lvl["Kit asked Hollis for time together; Hollis said no"] == 1


def test_distress_leave_names_the_unmet_need():
    t = _tables()
    t["week"][5]["events"] = []
    t["decision"][0]["leave_ctx"] = {"bar": False, "N": 0.25, "n_high": True, "low": False, "trust_low": False, "low_weeks": 0,
                                     "cond_run": {"denied": 4}}
    t["state"] = [s if (s["w"], s["r"]) != (4, "B") else _state(4, "B", levels={"rest": 0.05, "connection": 0.9, "money": 0.5,
                                                                                "security": 0.6}) for s in t["state"]]
    ev = [e["text"] for e in WT.events(t, NAMES) if e["kind"] == "leave"]
    assert ev == ["Hollis moved out (distress: rest unmet for 4 weeks), taking 24 from the shared pot"]


# ---- decision cards ------------------------------------------------------------------------------------------------------------

def test_tipping_part():
    # margin 0.1 = partner +0.2, money -0.1: removing partner flips it, removing money does not
    tip, top = WT.tipping({"partner": 0.3, "money": 0.1}, {"partner": 0.1, "money": 0.2}, 0.1)
    assert tip == "partner" and top[0] == ("partner", 0.2)
    tip, _ = WT.tipping({"a": 0.3, "b": 0.3}, {"a": 0.0, "b": 0.0}, 0.6)     # neither alone flips it
    assert tip is None
    tip, _ = WT.tipping({"money": 0.5}, {"money": 0.51}, 0.07, {"exit_anticipation": 0.08})   # O is net of the exit stigma
    assert tip == "exit_anticipation"


def test_cards():
    cs = WT.cards(_tables(), NAMES)
    assert [c["kind"] for c in cs] == ["formation0", "reading", "leave"]
    f = cs[0]
    assert f["title"] == "Move in together?" and f["result"] == "They moved in together."
    assert f["members"]["A"]["wants"] == "live together" and f["members"]["A"]["tip"] == "time with the partner"
    r = cs[1]
    assert r["members"]["B"]["wants"] == "leave" and r["members"]["B"]["tip"] == "friends"
    assert r["members"]["B"]["stay_test"] == "leave" and r["result"] == "Hollis moved out."
    lv = cs[2]
    assert lv["title"] == "Hollis moves out" and lv["opts"] == ["move out", "rest"]       # other take sizes folded in
    assert lv["margin"] == pytest.approx(0.8)
    assert lv["tip"] == "two 13-week checks in a row found the outside option better"
    assert lv["replay"] == ("If Hollis had stayed: over the next 13 weeks, Hollis worse off (-0.12 pleasure a week), "
                            "Kit better off (+0.05 pleasure a week); nobody left in that time.")
    assert lv["result"] == "Hollis moved out, taking 24 from the shared pot."


def test_give_balance():
    give, bal = WT.give_series(_tables(), 8)
    assert give["A"][4] == pytest.approx(-3.0) and give["B"][3] == 2.0
    assert bal[0] is None and bal[3] == pytest.approx((3 - 2) / 5)


# ---- the page ------------------------------------------------------------------------------------------------------------------

def _check_page(html):
    assert len(html.encode()) < WT.MAX_BYTES
    assert re.search(r"<title>([^<]+)</title>", html).group(1) == "Household Replay"
    assert ":root{" in html and '@media (prefers-color-scheme:dark){:root:not([data-theme="light"])' in html
    assert ':root[data-theme="dark"]' in html and "body{background:var(--bg)" in html
    assert not re.search(r"""(src|href)\s*=\s*["']?(https?:)?//""", html)          # no external requests
    assert "fetch(" not in html and "@import" not in html
    blob = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1)
    return json.loads(blob)


def test_page_builds_from_extract():
    run = WT.extract(_tables())
    html = WT.build([WT.entry("one", "h38|L0|a|b|0", "why"), WT.entry("two", ["h38|L0|a|b|0", "h38|L0|a|b|0"])],
                    {"h38|L0|a|b|0": run})
    data = _check_page(html)
    assert data["entries"][1]["runs"][0]["label"] == "No pairing pressure (H38 L0)"
    assert data["runs"]["h38|L0|a|b|0"]["names"] == WT.names_for({"A": {"id": "a"}, "B": {"id": "b"}})


def test_page_escapes_script_end():
    run = WT.extract(_tables(), title="</script><b>x")
    assert "</script><b>" not in WT.build([WT.entry("t", "h38|L0|a|b|0")], {"h38|L0|a|b|0": run}).split('id="data"')[1][:20000]


def test_real_run_rerun_and_page(tmp_path):
    """The atlas's "asking that ends it" medoid, re-run with the observer on (no file in tmp cache): the asker is refused, leaves at
    week 8; the page builds."""
    key = WT.norm_key("ef", "F0|author_seed_v23_bindable|21|0")
    path, size = WT.page([WT.entry("asking", key)], tmp_path / "p.html", cache=tmp_path)
    assert (tmp_path / "obs" / WT.file_name(key)).exists() or WT.find(key) is not None
    data = _check_page(path.read_text())
    run = data["runs"][key]
    n = run["names"]
    leaves = [e for e in run["events"] if e["kind"] == "leave"]
    assert [e["w"] for e in leaves] == [8, 106]
    assert leaves[0]["text"].startswith(f"{n['A']} moved out (distress:")
    asks = [e for e in run["events"] if e["kind"] == "ask"]
    assert len(asks) == 18 and all(e["text"].endswith(f"{n['B']} said no") for e in asks)
    assert any(c["kind"] == "leave" and c["replay"] for c in run["decisions"])
    assert len(run["mood"]["A"]) == 156 and size == path.stat().st_size


def test_cli_watch_needs_a_run():
    from mar import cli
    assert cli.main(["watch"]) == 2
    assert cli.main(["watch", "fishery", "a|b"]) == 2
