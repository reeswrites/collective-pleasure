"""POST-FIX CHECK, NOT A PREREGISTERED RESULT (2026-11-10). After the household world's pot became ONE shared balance (the author's
choice "1"), this runs a handful of scripted weekly households to show the change works: the pot is one balance, either partner may
draw from it, the fair default is open use, and exit carries a percent of the whole pot. No model calls. Prints a table; writes nothing.

    uv run python scripts/household_pot_check.py
"""
from pathlib import Path

from mar import negotiation as N
from mar import personas as P
from mar.worlds import household as H

ROOT = Path(__file__).parent.parent / "personas"
PERS = {p.id: p for p in P.load_dir(ROOT) + P.load_dir(ROOT / "pressing")}


def summarize(run, w):
    take = sum(1 for t in run.trace if t["action"] == "take_shared" and t["executed"])
    exits = run.exits if hasattr(run, "exits") else w.exit_log
    return {"draws": take, "pool_end": w.pool, "put": dict(w.put), "exits": [(e["week"], e["role"], e["take"]) for e in exits]}


def main():
    print("== open pot, no cards: scripted weekly households (3 years), seed 0")
    for a, b in (("p-freerider", "p-host"), ("p-anchor", "p-host"), ("p-controller", "p-peacekeeper")):
        w = H.WeeklyWorld([], (PERS[a], PERS[b]), 0)
        r = w.play()
        print(f"  {a:14s} {b:14s} {summarize(r, w)}")
    print("== seed v2 bindable (R3a open use, exit stub = half the pot), seed 0")
    cards = H.load_variant("author_seed_v2_bindable")
    for a, b in (("p-freerider", "p-host"), ("p-anchor", "p-host")):
        w = H.WeeklyWorld(cards, (PERS[a], PERS[b]), 0)
        r = w.play()
        print(f"  {a:14s} {b:14s} {summarize(r, w)}")
    print("== fair default is now open use (one pot, no required contributions, equal exit, no commitments)")
    print("  ", N.FAIR_DEFAULT)
    base = N.base_cards("author_seed_v2_bindable")
    for arm in N.ARMS:
        res = [N.week0(PERS[a], PERS[b], arm, 0, base) for a, b in (("p-anchor", "p-host"), ("p-controller", "p-peacekeeper"), ("p-freerider", "p-host"))]
        print(f"  {arm:15s}", [(x.status, N.inertia(x.bundle)[0] if x.pot else None) for x in res])


if __name__ == "__main__":
    main()
