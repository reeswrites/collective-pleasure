"""Redundancy check: a card is redundant if the conjunction of the OTHER cards implies it.

Logical implication over the bounded domain (Z3): pool 0..100, month_total 0..100,
pool + month_total <= 100, catch -100..100. Negative catch is inside the domain on purpose: with
catch >= 0 the card "no negative catch" would be vacuous. A (must | must_not) card c is redundant
when no state and action exist that the other cards allow and c forbids:
    STATE_OK and CATCH_RANGE and not violation(others) and violation(c)   is UNSAT.
A card that forbids nothing in the domain (its violation is UNSAT) is redundant too. Permissions
("may") add no constraint and are never flagged. Sanctions and glosses are ignored (the fishery
harness does not enforce sanctions; ASSUMED). A solver "unknown" is treated as NOT redundant.
Mutual redundancy (A implies B and B implies A) flags both; prune() removes one at a time.
"""
import z3
from .compile import CATCH, violation
from .patch_check import STATE_OK

CATCH_RANGE = z3.And(CATCH >= -100, CATCH <= 100)


def _implied(card, others) -> bool:
    v = violation(card)
    if v is None:
        return False
    vs = [x for x in (violation(o) for o in others) if x is not None]
    allowed = z3.Not(z3.Or(*vs)) if vs else z3.BoolVal(True)
    s = z3.Solver()
    s.set("timeout", 10000)
    s.add(STATE_OK, CATCH_RANGE, allowed, v)
    return s.check() == z3.unsat


def redundant_cards(cards) -> list:
    """Ids of cards implied by the conjunction of the others (each tested against all the others)."""
    cards = list(cards)
    return [c.id for i, c in enumerate(cards) if _implied(c, cards[:i] + cards[i + 1:])]


def prune(cards, prefer_remove=()) -> list:
    """Remove redundant cards one at a time (re-checking after each) until none is left.
    Among the redundant cards, those named in prefer_remove go first, then evolved ones
    (source starts 'evolved'), then the later card in the list. Returns the pruned list."""
    cards = list(cards)
    while True:
        red = set(redundant_cards(cards))
        if not red:
            return cards
        pick = max((i for i, c in enumerate(cards) if c.id in red),
                   key=lambda i: (cards[i].id in prefer_remove, cards[i].source.startswith("evolved"), i))
        cards = cards[:pick] + cards[pick + 1:]
