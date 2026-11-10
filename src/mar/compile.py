"""Compile ADICO cards to Z3 constraints over (state, action).

State vars: pool, month_total (fish already taken this month by everyone).
Action var: catch. violation(card) is a Z3 Bool that is true exactly when the
proposed action breaks that card (see cards.py for the reading of conditions).
"""
import re
import z3

POOL, MONTH_TOTAL, CATCH = z3.Ints("pool month_total catch")
VARS = {"pool": POOL, "month_total": MONTH_TOTAL, "catch": CATCH}
_OPS = {"gt": lambda a, b: a > b, "ge": lambda a, b: a >= b, "lt": lambda a, b: a < b,
        "le": lambda a, b: a <= b, "eq": lambda a, b: a == b}


def parse_expr(text: str):
    """'month_total + catch' / 'catch - pool' -> Z3 term. Only + and - over the three vars."""
    tokens = re.findall(r"[+-]|\w+", text)
    term, sign = None, 1
    for t in tokens:
        if t == "+":
            sign = 1
        elif t == "-":
            sign = -1
        else:
            v = VARS[t] if t in VARS else int(t)
            v = v if sign == 1 else -v
            term = v if term is None else term + v
            sign = 1
    return term


def predicate(c: dict):
    return _OPS[c["op"]](parse_expr(c["expr"]), c["value"])


def conditions_expr(card):
    return z3.And(*[predicate(c) for c in card.conditions]) if card.conditions else z3.BoolVal(True)


def violation(card):
    """Z3 Bool: true when (state, action) breaks the card; None for permissions."""
    if card.deontic == "must_not":
        return conditions_expr(card)
    if card.deontic == "must":
        return z3.Not(conditions_expr(card))
    return None


def compile_cards(cards) -> dict:
    return {c.id: v for c in cards if (v := violation(c)) is not None}
