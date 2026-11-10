from itertools import product
from pathlib import Path

import pytest

from mar import personas as P

ROOT = Path(__file__).resolve().parent.parent / "personas"


def test_grid_covers_every_combination():
    g = P.grid()
    assert len(g) == 32 == len({p.id for p in g})
    combos = {tuple(p.axes[a] for a in P.AXES) for p in g}
    assert combos == set(product([0.2, 0.8], repeat=5))
    assert all(p.source == "grid" and P.validate(p) for p in g)
    assert len(P.grid(levels=3)) == 243


def test_mapping_extremes():
    w, style, risk = P.profile_from_axes({a: 0.0 for a in P.AXES})
    assert w["security"] == 1.0 and w["togetherness"] == 1.0 and style == "collaborative" and risk == 0.0
    w, style, risk = P.profile_from_axes({a: 1.0 for a in P.AXES})
    assert w["autonomy"] == 1.0 and w["other_connections"] == 1.0 and style == "avoidant" and risk == 1.0


def test_hand_personas_load_and_validate():
    hand = P.load_dir(ROOT)
    assert len(hand) == 6 and all(p.source == "hand" for p in hand)
    for p in hand:
        assert len(p.principles) == 3 and P.TODO not in p.principles


def test_hand_set_has_mismatched_pair():
    a, w = P.load(ROOT / "p-anchor.yaml"), P.load(ROOT / "p-wanderer.yaml")
    assert a.weights["security"] >= 0.8 and a.axes["certainty_openness"] <= 0.2
    assert w.weights["autonomy"] >= 0.8 and w.axes["certainty_openness"] >= 0.8


def test_grid_files_match_generator():
    files = {p.id: p for p in P.load_dir(ROOT / "grid")}
    assert set(files) == {p.id for p in P.grid()}
    for p in P.grid():
        assert files[p.id] == p


def test_blocklist_catches_planted_examples():
    p = P.load(ROOT / "p-anchor.yaml")
    for bad in ["She was raised Catholic.", "A woman who values order.", "Grew up as an immigrant."]:
        with pytest.raises(P.PersonaError, match="group-identity"):
            P.validate(P.Persona(**{**p.__dict__, "backstory": bad}))
    with pytest.raises(P.PersonaError, match="group-identity"):
        P.vary(p, "principles.0", "Men should lead.")


def test_blocklist_extendable():
    p = P.load(ROOT / "p-anchor.yaml")
    P.extend_blocklist("zorblax")
    try:
        with pytest.raises(P.PersonaError):
            P.vary(p, "backstory", "A zorblax by origin.")
    finally:
        P.BLOCKLIST.discard("zorblax")


def test_requires_profile_fields_and_ranges():
    p = P.load(ROOT / "p-anchor.yaml")
    bad = dict(p.__dict__, weights={k: v for k, v in p.weights.items() if k != "money"})
    with pytest.raises(P.PersonaError, match="weights"):
        P.validate(P.Persona(**bad))
    with pytest.raises(P.PersonaError):
        P.vary(p, "weights.money", 1.5)
    with pytest.raises(P.PersonaError):
        P.vary(p, "negotiation_style", "sulking")


def test_todo_only_for_grid():
    g = P.grid()[0]
    with pytest.raises(P.PersonaError, match="TODO"):
        P.validate(P.Persona(**{**g.__dict__, "source": "hand"}))


def test_vary_records_parent_and_leaves_original():
    p = P.load(ROOT / "p-anchor.yaml")
    q = P.vary(p, "weights.security", 0.2)
    assert q.id != p.id and q.id.startswith(p.id + "--") and q.parent == p.id
    assert q.weights["security"] == 0.2 and p.weights["security"] == 0.9
    assert {k: v for k, v in q.weights.items() if k != "security"} == \
        {k: v for k, v in p.weights.items() if k != "security"}


def test_save_load_roundtrip(tmp_path):
    q = P.vary(P.load(ROOT / "p-host.yaml"), "risk_tolerance", 0.3)
    path = P.save(q, tmp_path)
    assert P.load(path) == q


def test_render_plain_english():
    text = P.render(P.load(ROOT / "p-wanderer.yaml"))
    assert "Principles:" in text and "Backstory:" in text and "Cares about:" in text
    assert "—" not in text


def test_needs_and_aspirations_present_and_validated():
    for p in P.load_dir(ROOT) + P.grid():
        assert set(p.needs) == set(P.NEED_KEYS) and set(p.aspirations) == set(P.ASPIRATION_KEYS)
    p = P.load(ROOT / "p-anchor.yaml")
    assert p.needs["security"] == 0.9 and p.aspirations["together_per_week"] > p.aspirations["friends_per_week"]
    with pytest.raises(P.PersonaError, match="needs"):
        P.validate(P.Persona(**{**p.__dict__, "needs": {"rest": 2}}))


def test_old_files_without_goal_fields_get_defaults():
    p = P.load(ROOT / "p-wanderer.yaml")
    d = {k: v for k, v in p.__dict__.items() if k not in ("needs", "aspirations")}
    assert P.Persona(**d).needs == p.needs


def test_vary_weights_rederives_goals():
    p = P.load(ROOT / "p-anchor.yaml")
    q = P.vary(p, "weights.security", 0.2)
    assert q.needs["security"] == 0.2 and q.aspirations["security_buffer"] < p.aspirations["security_buffer"]
