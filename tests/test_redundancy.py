from mar import redundancy as R
from mar import world_api as W
from mar.cards import make_card

SRC = "test fixture"


def card(cid, deontic, conds, aim="harvest"):
    return make_card({"id": cid, "attribute": "fisher", "deontic": deontic, "aim": aim, "conditions": conds,
                      "or_else": None, "gloss": "g", "source": SRC})


def cond(expr, op, value):
    return {"expr": expr, "op": op, "value": value}


def test_seed_specs_have_no_redundancy():
    spec = W.FisheryWorld().load_spec()
    assert R.redundant_cards(spec) == []


def test_f3_f4_flip_must_flip():
    """Run 1 elites: F4 flipped from may to must 'harvest only when catch >= 0' restates F3 (no negative catch)."""
    spec = W.FisheryWorld().load_spec()
    f3 = next(c for c in spec if c.id == "F3")
    f4 = next(c for c in spec if c.id == "F4")
    f4_must = make_card({"id": "F4", "attribute": f4.attribute, "deontic": "must", "aim": f4.aim,
                         "conditions": [cond("catch", "ge", 0)], "or_else": f4.or_else, "gloss": "g",
                         "source": "evolved (flip) | " + f4.source})
    assert R.redundant_cards([f3, f4_must]) == ["F3", "F4"]  # each implies the other
    pruned = R.prune([f3, f4_must])
    assert [c.id for c in pruned] == ["F3"]  # the evolved restatement goes, one card stays
    assert R.redundant_cards(pruned) == []
    # the original may-card never counts
    assert R.redundant_cards([f3, f4]) == []


def test_looser_cap_is_implied_by_tighter_cap():
    tight = card("A", "must_not", [cond("catch", "gt", 5)])
    loose = card("B", "must_not", [cond("catch", "gt", 10)])
    assert R.redundant_cards([tight, loose]) == ["B"]
    assert R.redundant_cards([loose, tight]) == ["B"]
    assert [c.id for c in R.prune([tight, loose])] == ["A"]


def test_independent_cards_not_redundant():
    a = card("A", "must_not", [cond("catch", "gt", 5)])
    b = card("B", "must_not", [cond("pool", "lt", 10), cond("catch", "gt", 0)])
    assert R.redundant_cards([a, b]) == []


def test_dead_card_is_redundant_and_may_is_ignored():
    dead = card("D", "must_not", [cond("catch", "gt", 5), cond("catch", "lt", 3)])  # never fires
    a = card("A", "must_not", [cond("catch", "gt", 5)])
    may = card("M", "may", [cond("catch", "gt", 0)])
    assert R.redundant_cards([a, dead, may]) == ["D"]
    assert R.redundant_cards([may]) == []


def test_prune_prefers_named_card():
    a = card("A", "must_not", [cond("catch", "gt", 5)])
    b = card("B", "must_not", [cond("catch", "gt", 5)])  # identical meaning: mutual
    assert [c.id for c in R.prune([a, b], prefer_remove=("A",))] == ["B"]
    assert [c.id for c in R.prune([a, b])] == ["A"]  # default: the later card goes
