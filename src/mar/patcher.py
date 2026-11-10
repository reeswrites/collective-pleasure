"""SCRIPTED patcher with the interface the LLM patcher will later have.

Input: a failing trace (list of proposal rows from fishery.Run.trace) and the current
cards. It never receives, and must not import, the oracle. Output: proposed new cards.
"""
from .cards import make_card

MONTH_CAP = 40  # V2 fixture: stock 100 -> 60 after the cap, regrows to capacity
GLOSS = "Together, fishers may take no more than 40 fish in one month."
SOURCE = ("V2 fixture, scripted patch. Sustainability bound from GovSim dynamics "
          "(Piatti et al. 2024, arXiv 2404.16698): leaving 60 of 100 doubles back to capacity.")


def _has_month_cap(cards):
    return any(c.deontic == "must_not" and any(p["expr"].replace(" ", "") == "month_total+catch"
                                               for p in c.conditions) for c in cards)


def propose_patch(failing_trace, cards):
    month_totals = {}
    for r in failing_trace:
        if r["executed"]:
            month_totals[r["month"]] = month_totals.get(r["month"], 0) + (r["pool_before"] - r["pool_after"])
    if _has_month_cap(cards) or not month_totals or max(month_totals.values()) <= MONTH_CAP:
        return []
    n = 1 + sum(1 for c in cards if c.id.startswith("P"))
    return [make_card({
        "id": f"P{n}", "attribute": "fisher", "deontic": "must_not", "aim": "harvest",
        # "catch > 0" matters: without it the card also blocks catch 0 in states already over the
        # cap, and the deadlock check (b) correctly fails it (first V2 run; docs/surprises.md).
        "conditions": [{"expr": "catch", "op": "gt", "value": 0},
                       {"expr": "month_total + catch", "op": "gt", "value": MONTH_CAP}],
        "or_else": {"kind": "suspend", "duration_months": 1, "sanctioner": "monitor"},
        "gloss": GLOSS, "source": SOURCE})]
