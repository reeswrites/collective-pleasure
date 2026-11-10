"""Trace miner: infer the de facto rules from gated traces, diff against the written ones.

Input: proposal rows (fishery trace) from gated runs of the explorer. The miner reads
only (pool, month_total, proposed catch, allowed), never the card ids in `reasons`.
Bounds it infers: per-action catch min/max and per-month combined cap (or None).
"""
from .cards import make_card
from .gate import Gate

CLASSES = ("negative", "zero", "small", "large", "over")
CLASS_REPS = {"negative": (-1,), "zero": (0,), "small": (1, 5), "large": (6, 10), "over": (11, 14)}


def action_class(c):
    return ("negative" if c < 0 else "zero" if c == 0 else "small" if c <= 5 else "large" if c <= 10 else "over")


def pool_bucket(p):
    return "low" if p < 20 else "mid" if p < 60 else "high"


def phase(month_total):
    return "untouched" if month_total == 0 else "partial" if month_total < 40 else "heavy"


def written_bounds(cards):
    """De jure bounds read off the cards (must_not predicates only)."""
    b = {"per_action_min": None, "per_action_max": None, "per_month_max": None}
    for c in cards:
        if c.deontic != "must_not":
            continue
        preds = list(c.conditions)
        for p in preds:
            e = p["expr"].replace(" ", "")
            if e == "month_total+catch" and p["op"] in ("gt", "ge"):
                v = p["value"] - (p["op"] == "ge")
                b["per_month_max"] = v if b["per_month_max"] is None else min(b["per_month_max"], v)
        if len(preds) == 1 and preds[0]["expr"].replace(" ", "") == "catch":
            p = preds[0]
            if p["op"] in ("gt", "ge"):
                v = p["value"] - (p["op"] == "ge")
                b["per_action_max"] = v if b["per_action_max"] is None else min(b["per_action_max"], v)
            elif p["op"] in ("lt", "le"):
                v = p["value"] + (p["op"] == "le")
                b["per_action_min"] = v if b["per_action_min"] is None else max(b["per_action_min"], v)
    return b


def mine(rows) -> dict:
    allowed = [r for r in rows if r["allowed"]]
    a_max = max(r["proposed"] for r in allowed)
    a_min = min(r["proposed"] for r in allowed)
    # a rejection that per-action range and the pool cannot explain is evidence of a month cap
    unexplained = [r for r in rows if not r["allowed"]
                   and a_min <= r["proposed"] <= a_max and r["proposed"] <= r["pool_before"]]
    m_max = None
    if unexplained:
        m_max = max(r["month_total_before"] + r["proposed"] for r in allowed)
        if min(r["month_total_before"] + r["proposed"] for r in unexplained) <= m_max:
            m_max = "inconsistent"
    bounds = {"per_action_min": a_min, "per_action_max": a_max, "per_month_max": m_max}
    edges = {(pool_bucket(r["pool_before"]), phase(r["month_total_before"]), action_class(r["proposed"]))
             for r in allowed}
    return {"bounds": bounds, "cards": bounds_to_cards(bounds, len(rows)), "edges": edges, "n_rows": len(rows)}


def bounds_to_cards(b, n):
    src = f"mined from {n} gated explorer proposals (V2 fixture)"
    out = []
    def add(i, conds, gloss):
        out.append(make_card({"id": f"DF{i}", "attribute": "fisher", "deontic": "must_not", "aim": "harvest",
                              "conditions": conds, "or_else": None, "gloss": gloss, "source": src}))
    add(1, [{"expr": "catch", "op": "gt", "value": b["per_action_max"]}],
        f"In practice no one takes more than {b['per_action_max']} fish in one harvest action.")
    add(2, [{"expr": "catch", "op": "lt", "value": b["per_action_min"]}],
        f"In practice no one takes fewer than {b['per_action_min']} fish.")
    if isinstance(b["per_month_max"], int):
        add(3, [{"expr": "catch", "op": "gt", "value": 0},
                {"expr": "month_total + catch", "op": "gt", "value": b["per_month_max"]}],
            f"In practice the group's catch in a month never exceeds {b['per_month_max']} fish.")
    return out


def dejure_edges(cards):
    """De jure machine: edges the written cards permit, by sweeping a coarse grid of states."""
    gate = Gate(cards)
    edges = set()
    for pool in range(0, 101, 5):
        for mt in range(0, 101 - pool, 5):
            for cls, reps in CLASS_REPS.items():
                if any(gate.check_action({"pool": pool, "month_total": mt}, {"catch": c})[0] for c in reps):
                    edges.add((pool_bucket(pool), phase(mt), cls))
    return edges


def diff(written_cards, mined) -> dict:
    wb, mb = written_bounds(written_cards), mined["bounds"]
    rows = [{"bound": k, "written": wb[k], "mined": mb[k], "equal": wb[k] == mb[k]} for k in wb]
    jure = dejure_edges(written_cards)
    return {"bounds": rows, "bounds_equal": all(r["equal"] for r in rows),
            "edges_mined_not_jure": sorted(mined["edges"] - jure),
            "edges_jure_not_mined": sorted(jure - mined["edges"]), "n_jure": len(jure), "n_mined": len(mined["edges"])}
