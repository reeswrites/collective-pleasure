"""The gate: allow or reject one proposed action against the compiled cards."""
import z3
from .compile import compile_cards, POOL, MONTH_TOTAL, CATCH


class Gate:
    def __init__(self, cards):
        self.cards = list(cards)
        self._violations = compile_cards(self.cards)

    def check_action(self, state: dict, action: dict):
        """-> (allowed, reasons). reasons = ids of the cards the action violates."""
        sub = [(POOL, z3.IntVal(state["pool"])),
               (MONTH_TOTAL, z3.IntVal(state.get("month_total", 0))),
               (CATCH, z3.IntVal(action["catch"]))]
        reasons = [cid for cid, v in self._violations.items()
                   if z3.is_true(z3.simplify(z3.substitute(v, *sub)))]
        return (not reasons, reasons)


def check_action(cards, state, action):
    return Gate(cards).check_action(state, action)
