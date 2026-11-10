from pathlib import Path
import pytest
from mar.cards import load_cards, make_card
from mar.english import render, parse, render_all, load_english, EnglishError
from mar.fishery import run_fishery
from mar.gate import Gate
from mar.mocks import Exploiter
from mar.patcher import propose_patch

ROOT = Path(__file__).parent.parent
RULES, EN = ROOT / "rules" / "fishery", ROOT / "rules" / "fishery-en"


def conflicting():
    return make_card({"id": "C1", "attribute": "fisher", "deontic": "must", "aim": "harvest",
                      "conditions": [{"expr": "catch", "op": "ge", "value": 20}], "or_else": None,
                      "gloss": "Every fisher must take at least 20 fish per harvest action.",
                      "source": "V2 fixture (deliberately conflicting patch)"})


def v2_cards():
    cards = load_cards(RULES)
    trace = run_fishery([Exploiter() for _ in range(4)], Gate(cards), seed=0).trace
    return cards + propose_patch(trace, cards) + [conflicting()]


def test_round_trip_identity_for_all_v2_cards():
    cards = v2_cards()
    assert len(cards) == 6
    for c in cards:
        s = render(c)
        assert "\n" not in s
        assert parse(s) == c, s


def test_checked_in_files_are_generated_by_render():
    for p, c in zip(sorted(RULES.glob("*.yaml")), load_cards(RULES)):
        assert (EN / (p.stem + ".txt")).read_text() == render_all([c])
    assert load_english(EN) == load_cards(RULES)
    pc = {c.id: c for c in v2_cards()}
    assert (EN / "patch" / "P1.txt").read_text() == render_all([pc["P1"]])
    assert (EN / "patch" / "C1.txt").read_text() == render_all([pc["C1"]])


def test_deontic_templates_and_sanction_wording():
    f1 = render(load_cards(RULES)[0])
    assert f1.startswith("F1. When the catch is more than 10, a fisher must not harvest, otherwise the monitor "
                         "halves their cap for 2 months. (Gloss: ")
    assert " only when the catch is at least 20." in render(conflicting())
    assert "for 1 month." in render(v2_cards()[4])


BASE = "R1. When the catch is more than 10, a fisher must not harvest. (Gloss: g.) (Source: s.)"


@pytest.mark.parametrize("text,fragment", [
    (BASE.replace("must not", "should not"), "cannot read the rule"),
    (BASE.replace("R1. ", ""), "rule must start with"),
    (BASE.replace("harvest. (Gloss", "harvest (Gloss"), "must end with"),
    (BASE.replace(" (Gloss: g.)", ""), "missing '(Gloss"),
    (BASE.replace(" (Source: s.)", ""), "missing '(Source"),
    (BASE.replace("g.", ""), "must not be empty"),
    (BASE.replace("the catch", "the lake"), "unknown term"),
    (BASE.replace("is more than", "exceeds"), "bad condition"),
    (BASE.replace("harvest.", "harvest, otherwise the monitor fines them for 2 months."), "bad sanction"),
    (BASE.replace("harvest.", "harvest, otherwise the monitor suspends them for 1 months."), "canonical form"),
    (BASE.replace("harvest.", "harvest unless the pool is at most 5."), "cannot read the rule"),
    (BASE.replace("more than 10", "more than 10 or the pool is at most 5"), "'or' is not supported"),
    (BASE.replace("more than 10", "more than 10 unless the pool is at most 5"), "'unless' is not supported"),
    (BASE.replace("a fisher", "an fisher"), "article"),
    ("", "missing"),
])
def test_parse_rejects_malformed_with_clear_error(text, fragment):
    with pytest.raises(EnglishError) as e:
        parse(text)
    assert fragment in str(e.value)


def test_render_refuses_what_has_no_english_form():
    odd = {"id": "X1", "attribute": "fisher", "deontic": "must_not", "aim": "harvest",
           "conditions": [{"expr": "catch", "op": "gt", "value": 1}], "gloss": "g", "source": "s",
           "or_else": {"kind": "fine", "duration_months": 1, "sanctioner": "monitor"}}
    with pytest.raises(EnglishError, match="no English form for sanction"):
        render(make_card(odd))
