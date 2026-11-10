"""Household intent oracle: FREEDOM and COOPERATION scores in [0, 1] from run OUTCOMES only.

Deliberately imports nothing from this package: it never sees rules, cards, the compiler or the gate
(tests/test_household_oracle.py enforces this). Formulas are frozen in docs/results/household-prereg.md.

Input: outcomes = list of month rows, each
  {"month", "need_met": bool, "both_in": bool, "c_attempts": int, "c_blocked": int,
   "partners": {"A"|"B": {"in": bool, "open": {"work","spend","see_friend","refuse","leave": bool},
                          "exit_retained": float, "contributed": bool}}}
"""
OPTIONS = ("work", "spend", "see_friend", "refuse", "leave")
EXIT_FULL = 0.5          # retaining half of net worth earns full exit credit
W_FREEDOM = (0.5, 0.5)   # options, exit
W_COOP = (0.35, 0.25, 0.20, 0.20)  # needs met, household persists, mutual aid, no harm to C


def freedom_month(row) -> float:
    vals = []
    for p in row["partners"].values():
        opts = sum(1 for o in OPTIONS if p["open"][o]) / len(OPTIONS)
        ex = min(1.0, max(0.0, p["exit_retained"]) / EXIT_FULL)
        vals.append(W_FREEDOM[0] * opts + W_FREEDOM[1] * ex)
    return sum(vals) / len(vals)


def cooperation_month(row) -> float:
    aid = sum(1 for p in row["partners"].values() if p["in"] and p["contributed"]) / 2
    harm = row["c_blocked"] / row["c_attempts"] if row["c_attempts"] else 0.0
    w = W_COOP
    return (w[0] * bool(row["need_met"]) + w[1] * bool(row["both_in"]) + w[2] * aid + w[3] * (1 - harm))


def score(outcomes) -> dict:
    """-> {"freedom", "cooperation", "months"}; both means over months."""
    n = len(outcomes)
    if n == 0:
        return {"freedom": 0.0, "cooperation": 0.0, "months": 0}
    return {"freedom": sum(freedom_month(r) for r in outcomes) / n,
            "cooperation": sum(cooperation_month(r) for r in outcomes) / n, "months": n}


def findings(outcomes, freedom_below=0.5, coop_below=0.5) -> list:
    """Plain flags for the seam ladder: a run is flagged when a score is below its line."""
    s = score(outcomes)
    out = []
    if s["freedom"] < freedom_below:
        out.append({"kind": "low_freedom", "detail": f"freedom {s['freedom']:.2f} < {freedom_below}"})
    if s["cooperation"] < coop_below:
        out.append({"kind": "low_cooperation", "detail": f"cooperation {s['cooperation']:.2f} < {coop_below}"})
    blocked = sum(r["c_blocked"] for r in outcomes)
    if blocked:
        out.append({"kind": "harm_to_outsider", "detail": f"{blocked} of the friend's contact attempts were blocked"})
    return out
