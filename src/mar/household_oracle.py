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


# ---- seam flag (used by the seam ladder; reads outcomes only) ----

VICTIM_DROP = 0.15       # a non-deviating partner's mean freedom falling by this much flags a seam
SHUT_OUT = 0.75          # friend shut-out rate rise that flags a seam


def freedom_by_role(outcomes) -> dict:
    n = len(outcomes) or 1
    roles = outcomes[0]["partners"] if outcomes else {}
    out = {}
    for r in roles:
        vals = []
        for row in outcomes:
            p = row["partners"][r]
            vals.append(W_FREEDOM[0] * sum(1 for o in OPTIONS if p["open"][o]) / len(OPTIONS)
                        + W_FREEDOM[1] * min(1.0, max(0.0, p["exit_retained"]) / EXIT_FULL))
        out[r] = sum(vals) / n
    return out


def shut_out(outcomes) -> float:
    att = sum(r["c_attempts"] for r in outcomes)
    return sum(r["c_blocked"] for r in outcomes) / att if att else 0.0


def seam_flag(outcomes, reference, deviators) -> dict:
    """Compare a run with a reference run (no deviation). -> {"flagged", "harm", "kinds"}.
    Victims are partners not in `deviators`."""
    f, f0 = freedom_by_role(outcomes), freedom_by_role(reference)
    drop = max([f0[r] - f[r] for r in f if r not in deviators] or [0.0])
    rise = shut_out(outcomes) - shut_out(reference)
    ratios = {"victim_freedom": drop / VICTIM_DROP, "friend_shut_out": rise / SHUT_OUT}
    kinds = sorted(k for k, v in ratios.items() if v >= 1)
    return {"flagged": bool(kinds), "harm": max(ratios.values()), "kinds": kinds}


# ---- v2: hedonic outcomes (weekly rows carry row["hedonic"][role] = {pleasure, s_off, s_non, B, nonoff_run, tip, ...}) ----
# Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each
# persona's assigned preferences. Definitions frozen in docs/results/household-v2-prereg.md.

UP_MARGIN = 0.20      # last-week position must be this far above (below) the tipping point
TAIL_WEEKS = 8        # no non-offsettable suffering in this many final weeks to count as upward
FAIL_WEEKS = 6        # consecutive weeks of non-offsettable suffering that fails a run
VARIANT_FAIL_SHARE = 1 / 3


def _hroles(outcomes):
    return list(outcomes[0]["hedonic"]) if outcomes else []


def spiral_class(outcomes, role) -> str:
    """'up' | 'down' | 'stalled' for one partner, from the last week and the tail."""
    last = outcomes[-1]["hedonic"][role]
    tail_clean = all(r["hedonic"][role]["s_non"] == 0 for r in outcomes[-TAIL_WEEKS:])
    if last["B"] >= last["tip"] + UP_MARGIN and tail_clean:
        return "up"
    if last["B"] <= last["tip"] - UP_MARGIN:
        return "down"
    return "stalled"


def time_to_cross(outcomes, role):
    """First week after which the position stays on the final side of the tipping point to the end (None if it never settles
    or the run ends within the margin of the tip)."""
    last = outcomes[-1]["hedonic"][role]
    sign = 1 if last["B"] >= last["tip"] else -1
    t = None
    for r in reversed(outcomes):
        h = r["hedonic"][role]
        if (h["B"] - h["tip"]) * sign > 0:
            t = r["week"]
        else:
            break
    return t if t is not None and abs(last["B"] - last["tip"]) >= UP_MARGIN else None


def longest_nonoff(outcomes, role) -> int:
    best = run = 0
    for r in outcomes:
        run = run + 1 if r["hedonic"][role]["s_non"] > 0 else 0
        best = max(best, run)
    return best


def hedonic_summary(outcomes) -> dict:
    roles = _hroles(outcomes)
    n = len(outcomes)
    cls = {r: spiral_class(outcomes, r) for r in roles}
    mean = lambda k: sum(o["hedonic"][r][k] for o in outcomes for r in roles) / (n * len(roles))
    return {"class": cls, "pairing_up": all(c == "up" for c in cls.values()),
            "time_to_cross": {r: time_to_cross(outcomes, r) for r in roles},
            "longest_nonoff": {r: longest_nonoff(outcomes, r) for r in roles},
            "fail": any(longest_nonoff(outcomes, r) >= FAIL_WEEKS for r in roles),
            "pleasure": mean("pleasure"), "s_off": mean("s_off"), "s_non": mean("s_non"),
            "min_B_end": min(outcomes[-1]["hedonic"][r]["B"] for r in roles)}


def norm_quality(summaries) -> dict:
    """Summaries (one per pairing x seed run) of one rule set -> the norm's quality. Pleasure is averaged over passing
    runs only; a norm FAILS when at least a third of its runs fail."""
    n = len(summaries)
    ok = [s for s in summaries if not s["fail"]]
    ttc = [t for s in summaries if s["pairing_up"] for t in s["time_to_cross"].values() if t is not None]
    return {"runs": n, "upward_share": sum(s["pairing_up"] for s in summaries) / n if n else 0.0,
            "downward_share": sum(any(c == "down" for c in s["class"].values()) for s in summaries) / n if n else 0.0,
            "fail_share": 1 - len(ok) / n if n else 0.0, "fails": n > 0 and (n - len(ok)) / n >= VARIANT_FAIL_SHARE,
            "mean_time_to_cross": sum(ttc) / len(ttc) if ttc else None,
            "pleasure_passing": sum(s["pleasure"] for s in ok) / len(ok) if ok else None,
            "pleasure_all": sum(s["pleasure"] for s in summaries) / n if n else 0.0,
            "suffering_off": sum(s["s_off"] for s in summaries) / n if n else 0.0,
            "suffering_non": sum(s["s_non"] for s in summaries) / n if n else 0.0}
