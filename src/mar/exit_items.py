"""Exit fallbacks, slice 2: indivisible household items (docs/results/exit-fallbacks-design.md, "Slice 2").

OFF by default (`ACTIVE` None): no world has items and nothing here is read. With items on, every household starts with a few
jointly held indivisible items. Each item has a price (money units) and a per-person sentimental premium m (valued above price):
partner r values item i at price_i x (1 + m_ir). Items with a weekly rate (home, pet) give their holder that much extra modeled
pleasure every week, scaled by (1 + m_ir); while the item is held jointly, each partner who is in the household gets it. Items
without a rate (a collection) matter only at exit: in the allocation, compensation and leverage. Everything numeric is ASSUMED and
placeholder: the valuations are the known weakness of slice 2 (the author's words: "it depends on what you put in and what you
value").

At the first exit while items are held jointly, the active exit fallback (mar.exit_fallback) allocates the pot AND the items:
  F0, F1  "claim": the leaver claims a share of everything (pot + items at price; F1 refuses a claim over half) and takes the items
          they value most that fit inside the claim, the rest of the claim in money from the pot.
  F2      "brought": each keeps the items they brought; the pot by what each put into it.
  F3      contested: the pot and the items are frozen (nobody gets an item's weekly pleasure); at the deadline the household settles at
          an equal split by "valuer" (below); a partner who runs short of money concedes everything to the other.
  F4      "valuer" with contribution shares: each item goes to whoever values it more (ties: who brought it), and money moves so that
          each ends with their contribution share (pot + bills basis) of everything at price.
  F5      "valuer" with the prenup's share (equal split 1/2, proportional = the put share, forfeit 0 for the leaver).
A negotiated exit term (N5*) on a pair without a fallback: items are not modelled for that pair (they stay joint; documented limit).
If the leaver comes back, the items they took become joint again (they move back in with them); money is not undone.
"""
from __future__ import annotations

from contextlib import contextmanager

from . import exit_fallback as EF

DEFAULT_ITEMS = (
    {"name": "home", "price": 60.0, "weekly": 0.02, "brought": "A"},
    {"name": "pet", "price": 10.0, "weekly": 0.02, "brought": "B"},
    {"name": "collection", "price": 20.0, "weekly": 0.0, "brought": "A"},
)
# The valuation grid (sentimental premium m per item per partner). Placeholder numbers; the grid is the point.
GRID = {
    "V0-price-only": {"A": {"home": 0, "pet": 0, "collection": 0}, "B": {"home": 0, "pet": 0, "collection": 0}},
    "V1-both-attached": {"A": {"home": 1, "pet": 1, "collection": 0}, "B": {"home": 1, "pet": 1, "collection": 0}},
    "V2-split-loves": {"A": {"home": 3, "pet": 0, "collection": 0}, "B": {"home": 0, "pet": 3, "collection": 0}},
    "V3-crossed": {"A": {"home": 0, "pet": 3, "collection": 0}, "B": {"home": 3, "pet": 0, "collection": 3}},
    "V4-one-sided-B": {"A": {"home": 0, "pet": 0, "collection": 0}, "B": {"home": 3, "pet": 3, "collection": 3}},
}

ACTIVE = None        # None = off; else {"items": [...], "premium": {"A": {...}, "B": {...}}}


@contextmanager
def use_items(premium, items=DEFAULT_ITEMS):
    """Every WeeklyWorld built inside the block starts with `items` held jointly, valued with `premium` ({role: {item: m}}).
    premium=None turns items off."""
    global ACTIVE
    saved = ACTIVE
    ACTIVE = None if premium is None else {"items": [dict(i) for i in items], "premium": premium}
    try:
        yield ACTIVE
    finally:
        ACTIVE = saved


def init_world(world):
    if ACTIVE is None or not world.pot:
        world.items = None
        return
    world.items = {i["name"]: {**i, "holder": "both"} for i in ACTIVE["items"]}
    world.item_premium = {r: dict(ACTIVE["premium"][r]) for r in "AB"}
    world.item_log = []


def value(world, r, name):
    it = world.items[name]
    return it["price"] * (1.0 + world.item_premium[r].get(name, 0.0))


def weekly_pleasure(world, r):
    """Extra modeled pleasure this week for partner r from the items they hold (or share while in the household)."""
    if not world.items:
        return 0.0
    out = 0.0
    for name, it in world.items.items():
        if not it["weekly"]:
            continue
        h = it["holder"]
        if h == r or (h == "both" and world.p[r]["in"]):
            out += it["weekly"] * (1.0 + world.item_premium[r].get(name, 0.0))
    return out


def joint(world):
    return [n for n, it in (world.items or {}).items() if it["holder"] == "both"]


def week_start(world, w):
    """Reunion: if both partners are in again, items held by one of them become joint again."""
    if world.items and all(world.p[x]["in"] for x in "AB") and not world.contest:
        for it in world.items.values():
            if it["holder"] in ("A", "B"):
                it["holder"] = "both"


# ---- allocation ------------------------------------------------------------------------------------------------------------

def _total_price(world, names):
    return world.pool + sum(world.items[n]["price"] for n in names)


def allocate(world, L, share, rule, names=None):
    """-> (items to L, items to the other, money to L out of the pot; may be negative = L pays the other, or above the pot = the
    other pays L the rest). share: L's share of everything at price (pot + items)."""
    names = list(joint(world) if names is None else names)
    S = world.other(L)
    T = _total_price(world, names)
    E = (share or 0.0) * T
    if rule == "claim":
        mine, rem = [], E
        for n in sorted(names, key=lambda n: (-value(world, L, n), n)):
            if world.items[n]["price"] <= rem + 1e-9:
                mine.append(n)
                rem -= world.items[n]["price"]
        return mine, [n for n in names if n not in mine], min(rem, world.pool)
    if rule == "brought":
        mine = [n for n in names if world.items[n]["brought"] == L]
        return mine, [n for n in names if n not in mine], world.pool * EF.contribution_share(world, L, "pot")
    if rule == "valuer":
        mine = []
        for n in names:
            vl, vs = value(world, L, n), value(world, S, n)
            if vl > vs or (vl == vs and world.items[n]["brought"] == L):
                mine.append(n)
        return mine, [n for n in names if n not in mine], E - sum(world.items[n]["price"] for n in mine)
    raise ValueError(rule)


def arm_rule(world, L, take):
    """-> (share, rule) for a leaver L claiming `take` percent, under the world's active fallback. None: items not modelled."""
    arm = EF.world_arm(world) if EF.ACTIVE is not None else None
    if arm is None or arm == "F1":
        if EF.negotiated(world.gate.cards):
            return None
        return take / 100.0, "claim"
    if arm == "F2":
        return None, "brought"
    if arm == "F4":
        return EF.contribution_share(world, L, "all"), "valuer"
    if arm == "F5":
        term = getattr(world, "prenup_exit", None) or "equal_split"
        return {"equal_split": 0.5, "proportional": EF.contribution_share(world, L, "pot"), "forfeit": 0.0}[term], "valuer"
    if arm == "F3":
        return 0.5, "valuer"
    raise ValueError(arm)


def execute(world, L, mine, theirs, money):
    """Move items and money. Money from the pot first; beyond the pot, the other pays from their own money; a negative amount is
    paid by L to the other (into the pot if the other is the one member in, else their money). Payments are capped by holdings."""
    S = world.other(L)
    for n in mine:
        world.items[n]["holder"] = L
    for n in theirs:
        world.items[n]["holder"] = S
    if money >= 0:
        from_pot = min(money, world.pool)
        world.pool -= from_pot
        extra = min(money - from_pot, max(0.0, world.p[S]["money"]))
        world.p[S]["money"] -= extra
        got = from_pot + extra
        world.p[L]["money"] += got
        return got
    pay = min(-money, max(0.0, world.p[L]["money"]))
    world.p[L]["money"] -= pay
    EF._pay(world, S, pay)
    return -pay


def settle_exit(world, L, take, w):
    """At L's leave with jointly held items: allocate pot and items by the active fallback. -> money carried out by L, or None when
    items are not modelled for this pair (the caller then uses the plain pot carry)."""
    if not world.items or not joint(world):
        return None
    ar = arm_rule(world, L, take)
    if ar is None:
        return None
    share, rule = ar
    if EF.ACTIVE == "F3" and EF.world_arm(world) == "F3":
        names = joint(world)
        for n in names:
            world.items[n]["holder"] = "frozen"
        world.contest = {"leaver": L, "from": w, "until": w + EF.CONTEST_WEEKS, "escrow": world.pool, "items": names}
        world.pool = 0
        world.item_log.append({"week": w, "leaver": L, "arm": "F3", "frozen": names})
        return 0.0
    mine, theirs, money = allocate(world, L, share, rule)
    got = execute(world, L, mine, theirs, money)
    world.item_log.append({"week": w, "leaver": L, "rule": rule, "share": share, "mine": mine, "theirs": theirs, "money": got})
    return got


def contest_items(world, how):
    """F3 contest end with items: reunited -> joint; conceded_X -> all to the other; settled -> equal split by valuer."""
    c = world.contest
    names = c.get("items") or []
    if not names:
        return False
    L, S = c["leaver"], world.other(c["leaver"])
    if how == "reunited":
        for n in names:
            world.items[n]["holder"] = "both"
        world.pool += c["escrow"]
        return True
    if how.startswith("conceded_"):
        win = world.other(how.split("_")[1])
        for n in names:
            world.items[n]["holder"] = win
        EF._pay(world, win, c["escrow"])
        return True
    world.pool += c["escrow"]                       # settle on the whole estate at an equal split, by valuer
    mine, theirs, money = allocate(world, L, 0.5, "valuer", names)
    execute(world, L, mine, theirs, money)
    return True


# ---- evaluator: leverage and exit cost with items ---------------------------------------------------------------------------

def _V(world, r, items_r, money_r):
    return money_r + sum(value(world, r, n) for n in items_r)


def forced_value(world, r, w):
    """r's valuation of what r can force by a no-deal exit now (as exit_fallback.forced_amount, with items)."""
    names = joint(world)
    arm = EF.world_arm(world) if EF.ACTIVE is not None else None
    if arm == "F3":
        o = world.other(r)
        if not EF._can_wait(world, o) and EF._can_wait(world, r):
            return _V(world, r, names, world.pool)
        if not EF._can_wait(world, r) and EF._can_wait(world, o):
            return 0.0
        mine, _, money = allocate(world, r, 0.5, "valuer", names)
        return _V(world, r, mine, money)
    if arm in (None, "F1"):
        claim = max([t for t in (0, 10, 25, 50, 75, 100) if world.decide(r, "leave", w, t, commit=False)[0] != "hard"], default=0)
        mine, _, money = allocate(world, r, claim / 100.0, "claim", names)
        return _V(world, r, mine, money)
    share, rule = arm_rule(world, r, 0)
    mine, _, money = allocate(world, r, share, rule, names)
    return _V(world, r, mine, money)


def reference_value(world, r):
    """r's valuation of the reference allocation: contribution share (pot + bills) of everything at price, items by valuer."""
    mine, _, money = allocate(world, r, EF.contribution_share(world, r, "all"), "valuer")
    return _V(world, r, mine, money)


def estate(world, r):
    return world.pool + sum(value(world, r, n) for n in joint(world))


def holdout_leverage(world, w):
    """Slice-2 holdout leverage: max over partners of (what r can force - the reference allocation), both in r's own valuation,
    over r's valuation of the whole joint estate; clipped at 0. None when a partner is out or nothing is joint."""
    if not all(world.p[x]["in"] for x in "AB") or (world.pool <= 0 and not joint(world)):
        return None
    out = 0.0
    for r in "AB":
        e = estate(world, r)
        if e > 0:
            out = max(out, (forced_value(world, r, w) - reference_value(world, r)) / e)
    return out


def exit_cost(world, r, w):
    """Slice-2 stay-test charge: (reference value - what r gets by leaving now under the arm) / r's estate, in r's valuation, >= 0.
    F3 leaving now gets nothing until the contest settles."""
    e = estate(world, r)
    if e <= 0:
        return 0.0
    arm = EF.world_arm(world) if EF.ACTIVE is not None else None
    if arm == "F3":
        now = 0.0
    elif arm in (None, "F1"):
        claim = max([t for t in (0, 10, 25, 50, 75, 100) if world.decide(r, "leave", w, t, commit=False)[0] != "hard"], default=0)
        mine, _, money = allocate(world, r, claim / 100.0, "claim")
        now = _V(world, r, mine, money)
    else:
        share, rule = arm_rule(world, r, 0)
        mine, _, money = allocate(world, r, share, rule)
        now = _V(world, r, mine, money)
    return max(0.0, reference_value(world, r) - now) / e
