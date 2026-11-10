"""ADICO rule cards: loading and validation.

A card is one rule. Fields: id, attribute (who), deontic (must | must_not | may),
aim (what action), conditions (list of predicates over catch / pool / month_total),
or_else (None or a sanction dict), gloss (one plain-English sentence), source.

Predicate: {expr: "month_total + catch", op: gt|ge|lt|le|eq, value: <int>}.
Meaning of conditions (ASSUMED, simplest reading):
  must_not -> the action is a violation when ALL predicates hold.
  must     -> the action is a violation unless ALL predicates hold.
  may      -> permission only; adds no constraint.
"""
from dataclasses import dataclass, field, asdict
from pathlib import Path
import yaml

DEONTICS = ("must", "must_not", "may")
OPS = ("gt", "ge", "lt", "le", "eq")
FIELDS = ("id", "attribute", "deontic", "aim", "conditions", "or_else", "gloss", "source")


@dataclass(frozen=True)
class Card:
    id: str
    attribute: str
    deontic: str
    aim: str
    conditions: tuple
    or_else: dict | None
    gloss: str
    source: str

    def to_yaml(self) -> str:
        d = asdict(self)
        d["conditions"] = [dict(c) for c in self.conditions]
        return yaml.safe_dump(d, sort_keys=False, default_flow_style=None)


def make_card(d: dict) -> Card:
    missing = [f for f in FIELDS if f not in d]
    if missing:
        raise ValueError(f"card {d.get('id')}: missing fields {missing}")
    if d["deontic"] not in DEONTICS:
        raise ValueError(f"card {d['id']}: bad deontic {d['deontic']!r}")
    if not str(d["gloss"]).strip() or not str(d["source"]).strip():
        raise ValueError(f"card {d['id']}: gloss and source are required")
    for c in d["conditions"]:
        if c["op"] not in OPS:
            raise ValueError(f"card {d['id']}: bad op {c['op']!r}")
    return Card(d["id"], d["attribute"], d["deontic"], d["aim"],
                tuple(dict(c) for c in d["conditions"]), d["or_else"], d["gloss"], d["source"])


def load_cards(directory) -> list[Card]:
    cards = [make_card(yaml.safe_load(p.read_text())) for p in sorted(Path(directory).glob("*.yaml"))]
    ids = [c.id for c in cards]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate card ids")
    return cards
