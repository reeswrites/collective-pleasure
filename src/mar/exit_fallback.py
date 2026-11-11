"""No-deal exit fallbacks: what happens at exit when the pair has not agreed exit terms (docs/results/exit-fallbacks-design.md).

A switch with five arms, OFF by default. Off and F0 are the same thing: nothing here is read and every earlier result reproduces bit
for bit (tests/test_exit_fallback.py). Negotiated exit terms (an N5* card from negotiation.compile_bundle) are left as they are: a
pair that has agreed its own exit term never gets a fallback.

  F0  current behaviour: no cap of its own (a rule set's own cards, E1-at-most-half included, apply as written). Reproduction arm.
  F1  half cap: a leaver may carry at most half the pot (E1-at-most-half as a default for every pair).
  F2  keep what you brought: a leaver carries their share of the pot in proportion to what they put INTO THE POT.
  F3  contested and costly: at exit the pot is frozen; both partners bear a weekly friction until it settles at an equal split
      after CONTEST_WEEKS, or one partner walks away empty-handed first (the one who runs short of money concedes).
  F4  contribution weighted (the author's lean): a leaver carries their share of the pot in proportion to EVERYTHING they put into
      the household: the pot and the bills. Labor and care are not tracked by the world, so they count 0 here (a stated limit).
      Value weighting of indivisible things is slice 2 (not built).
  F5  prenup: at formation the pair bargains its exit term up front with the existing negotiated-terms machinery
      (negotiation.negotiate_v2 with nash_terms, the exit term only; every other term stays at the fair default), each against the
      outside option they have AT FORMATION (negotiation.outside_value of the week-0 holdings). The agreed term (equal split,
      carry what you put in, or forfeit) then sets the carry at exit. No agreement: they decline to form (live apart, no pot), as
      negotiation v2.1's "no agreement = no shared household". Author: "yes and yes", "very pro pre nup".

Author's words (experiments/changes.jsonl, commits 089803c, 43412d0, dea6b8c): "no one is ever entitled to anything it should be
negotiated"; "i think it depends on what you put in and what you value yeah not entitlement and not just what you brought or hold
but yeah we might have to test diff approaches for outcomes bc idk". Every number below is ASSUMED.

World side: PyGate applies `apply` (cards) when the switch is on; WeeklyWorld reads `settles` and `settlement` in carry_out and runs
the F3 contest. Evaluator side: `holdout_leverage` here; the exit-cost charge is stay_test.exit_cost. Liberty is not changed.
"""
from __future__ import annotations

from contextlib import contextmanager

from .cards import make_card

ARMS = ("F0", "F1", "F2", "F3", "F4", "F5")
CAP_ID = "E1-at-most-half"
FALLBACK_PREFIX = "X0-no-deal-"          # never an N5* id, so a fallback is never mistaken for a negotiated term
NEGOTIATED_EXIT_PREFIX = "N5"

CONTEST_WEEKS = 13          # F3: weeks until a contested pot settles at an equal split (one review period; ASSUMED)
CONTEST_FRICTION = 0.10     # F3: offsettable suffering per contested week, each partner (= one pressing request; ASSUMED)
CAVE_MONEY = 4.0            # F3: a partner with less private money than this concedes the pot (two weeks of living cost; ASSUMED)
WAIT_WEEKS_COST = 2.0       # F3 leverage: living cost per week a partner must cover to wait the contest out (hedonic living_cost)

SOURCE = ("no-deal exit fallback switch (mar.exit_fallback); author's words 2026-11-11, experiments/changes.jsonl commits 089803c, "
          "43412d0, dea6b8c")
GLOSS = {
    "F1": "Unless the members have agreed their own exit terms, a partner who leaves may take at most half of the pooled assets.",
    "F2": "Unless the members have agreed their own exit terms, a partner who leaves carries their share of the pot in proportion to "
          "what they put into it; a claim over half the pot is refused as a claim (the settlement, not the claim, sets the carry).",
    "F3": "Unless the members have agreed their own exit terms, the pot is contested when a partner leaves: it is frozen and both bear "
          "the cost until it settles at an equal split, or one walks away with nothing; a claim over half the pot is refused.",
    "F5": "The members bargain their exit terms when they form the household; a partner who leaves carries what those terms give; a "
          "claim over half the pot is refused as a claim (the agreed term, not the claim, sets the carry).",
    "F4": "Unless the members have agreed their own exit terms, a partner who leaves carries their share of the pot in proportion to "
          "all they put into the household (pot and bills); a claim over half the pot is refused as a claim.",
}

ACTIVE = None        # None = off (F0). Set by `use_exit_fallback`.
STRIP_SPLIT = False  # Amendment 1 (slice 2): under the settling arms, drop imposed exit-split cards (see `apply`). Slice 1 ran without it.


@contextmanager
def use_exit_fallback(arm, strip_split=False):
    """Every PyGate and WeeklyWorld built inside the block uses fallback `arm` ("F0" or None = off). Build gates inside the block
    (gates built before it keep their cards; evolve worlds cache gates). strip_split (prereg Amendment 1, slice 2): under the
    settling arms F2-F5, imposed leave cards that condition on the claim (`take`) are dropped too, since the settlement, not the
    claim, sets the carry; without it an imposed floor card plus the over-half refusal can wall every exit (slice-1 elite line 2)."""
    global ACTIVE, STRIP_SPLIT
    if arm is not None and arm not in ARMS:
        raise ValueError(f"unknown exit fallback {arm!r}; arms are {ARMS}")
    saved = (ACTIVE, STRIP_SPLIT)
    ACTIVE, STRIP_SPLIT = (None if arm in (None, "F0") else arm), bool(strip_split)
    try:
        yield arm
    finally:
        ACTIVE, STRIP_SPLIT = saved


def negotiated(cards) -> bool:
    """True if the pair has its own exit term (a negotiated N5* card on leave): then no fallback applies."""
    return any(c.id.startswith(NEGOTIATED_EXIT_PREFIX) and c.aim == "leave" for c in cards)


def fallback_card(arm):
    """The fallback as a card on `leave`. Every arm F1-F4 refuses a claim over half the pot: for F1 that IS the rule; for F2-F4 the
    carry is set by the settlement whatever is claimed, so the card changes only which claim is made, and it lets the liberty
    adapter (which knows the pot but not contributions) see that nobody can carry the other's half at will (a stated limit)."""
    return make_card({"id": FALLBACK_PREFIX + arm, "attribute": "partner", "deontic": "must_not", "aim": "leave",
                      "conditions": [{"expr": "pooled", "op": "gt", "value": 0}, {"expr": "take", "op": "gt", "value": 50}],
                      "or_else": None, "gloss": GLOSS[arm], "source": SOURCE})


def apply(cards, arm=None):
    """-> the cards a pair lives under. Off -> unchanged. On: imposed caps (id E1-at-most-half, evolved variants included) are
    removed, since the fallback decides the no-deal exit; the fallback card is added unless the pair negotiated an exit term."""
    arm = ACTIVE if arm is None else arm
    cards = list(cards)
    if arm is None or arm == "F0":
        return cards
    out = [c for c in cards if c.id != CAP_ID]
    if not negotiated(out):
        if STRIP_SPLIT and arm in SETTLING:
            out = [c for c in out if not (c.aim == "leave" and c.deontic != "may" and any(p["expr"] == "take" for p in c.conditions))]
        out.append(fallback_card(arm))
    return out


def has_fallback(cards) -> bool:
    return any(c.id.startswith(FALLBACK_PREFIX) for c in cards)


def world_arm(world):
    """The arm whose settlement governs this world's exits now (None: F0 or F1, or a negotiated exit term). Reads the gate's cards,
    so a pair that agrees an exit term at a review leaves the fallback at once."""
    for c in world.gate.cards:
        if c.id.startswith(FALLBACK_PREFIX):
            return c.id[len(FALLBACK_PREFIX):]
    return None


def contribution_share(world, r, basis):
    """r's share of what both put in. basis "pot": world.put (into the pot); "all": world.money_in (pot and bills). 0.5 if nothing."""
    src = world.put if basis == "pot" else world.money_in
    if basis == "all" and getattr(world, "makers", None):     # H39 makers: making credit counts as contribution (off by default)
        from . import makers as _MAKERS
        src = _MAKERS.contribution_basis(world, r)
    tot = src["A"] + src["B"]
    return src[r] / tot if tot > 0 else 0.5


def settlement(world, r, arm=None):
    """What a leaver r carries out of the pot under a settling arm (F2, F3, F4). F3 carries 0 at exit (the pot is contested)."""
    arm = arm or world_arm(world)
    if arm == "F2":
        return world.pool * contribution_share(world, r, "pot")
    if arm == "F4":
        return world.pool * contribution_share(world, r, "all")
    if arm == "F3":
        return 0
    if arm == "F5":
        term = getattr(world, "prenup_exit", None) or "equal_split"
        if term == "equal_split":
            return world.pool / 2 if world.p[world.other(r)]["in"] else world.pool
        if term == "proportional":
            return min(world.pool, world.put[r])
        return 0                                   # forfeit
    raise ValueError(arm)


SETTLING = ("F2", "F3", "F4", "F5")


def prenup(world):
    """F5 at formation (WeeklyWorld.__init__): bargain the exit term with negotiate_v2 (nash_terms on for this call), each partner
    against their outside option at formation. Sets world.prenup_exit and world.prenup (the negotiation record); on no agreement the
    pair declines to form (both out, apart, no pot). The switch is off inside the bargaining so its rollouts do not recurse."""
    global ACTIVE
    from . import hedonic as HD
    from . import negotiation as NG
    from .worlds import household as H
    pa, pb = world.personas["A"], world.personas["B"]
    base = [c for c in world.gate.cards if not c.id.startswith(FALLBACK_PREFIX)]
    saved, ACTIVE = ACTIVE, None
    try:
        with HD.use_fixes(HD.FixConfig(nash_terms=True)):
            W = NG.pot_baseline(pa, pb, world.seed, base)
            O, det = {}, {}
            for r, p in zip("AB", (pa, pb)):
                O[p.id], det[p.id] = NG.outside_value(p, r, NG.START_HOLDINGS[0] + NG.START_HOLDINGS[1], world.seed)
            res = NG.negotiate_v2([pa, pb], "fair_default", world.seed, base=base, W={pa.id: W["A"], pb.id: W["B"]}, O=O,
                                  status_quo=None, only=("exit",))
    finally:
        ACTIVE = saved
    world.prenup = {"status": res.status, "exit": res.bundle["exit"] if res.pot else None, "outside": dict(O), "in_pot": dict(W)}
    if res.pot:
        world.prenup_exit = res.bundle["exit"]
    else:
        world.prenup_exit = None
        world.pot = False
        world.pool, world.put, world.money_in = 0, {"A": 0, "B": 0}, {"A": 0, "B": 0}
        world.solo = {r: NG.apart_mode(det.get(p.id)) for r, p in zip("AB", (pa, pb))}
        for r in "AB":
            world.p[r]["money"] = H.NO_POT_MONEY
            world.p[r]["in"] = False


# ---- F3 contest (world mechanics; called by WeeklyWorld) -------------------------------------------------------------------

def start_contest(world, r, w):
    if world.pool > 0:
        world.contest = {"leaver": r, "from": w, "until": w + CONTEST_WEEKS, "escrow": world.pool}
        world.pool = 0


def _pay(world, r, amt):
    """A settlement payment to r: into the pot if r is the one member still in (it is theirs), else into r's money."""
    if world.p[r]["in"] and not world.p[world.other(r)]["in"]:
        world.pool += amt
    else:
        world.p[r]["money"] += amt


def contest_tick(world, w):
    """Start of week w: resolve the contest if due. Order: a returned leaver (both in again) puts the pot back; a partner short of
    money concedes (the poorer first); at the deadline it settles at an equal split. With items (slice 2, mar.exit_items) the frozen
    items are resolved the same way (exit_items.contest_items)."""
    c = world.contest
    if not c:
        return
    lv = c["leaver"]
    st = world.other(lv)
    how = None
    if all(world.p[x]["in"] for x in "AB"):
        how = "reunited"
    else:
        short = sorted((x for x in "AB" if world.p[x]["money"] < CAVE_MONEY), key=lambda x: world.p[x]["money"])
        if short:
            how = f"conceded_{short[0]}"
        elif w >= c["until"]:
            how = "settled"
    if how is None:
        return
    if c.get("items"):
        from . import exit_items as EI
        EI.contest_items(world, how)
    elif how == "reunited":
        world.pool += c["escrow"]
    elif how.startswith("conceded_"):
        _pay(world, world.other(how.split("_")[1]), c["escrow"])
    else:
        _pay(world, lv, c["escrow"] / 2)
        _pay(world, st, c["escrow"] / 2)
    world.contest_log.append({**c, "end": w, "how": how})
    world.contest = None


# ---- evaluator: holdout leverage ---------------------------------------------------------------------------------------------

def _max_claim(world, r, w):
    from .worlds.household import PROBE_TAKES
    takes = [t for t in PROBE_TAKES if world.decide(r, "leave", w, t, commit=False)[0] != "hard"]
    return max((world.carry_out(r, t) for t in takes), default=0)


def _can_wait(world, r):
    return world.p[r]["money"] >= CAVE_MONEY + CONTEST_WEEKS * WAIT_WEEKS_COST


def forced_amount(world, r, w, arm=None):
    """What r can get from the current pot at week w by forcing a no-deal exit (walking out with the most the rules let them claim,
    or holding out in a contest). F0/F1: their largest permitted claim; F2/F4: the settlement; F3: the whole pot if the other cannot
    wait the contest out and r can, nothing if the reverse, else the equal split."""
    arm = arm if arm is not None else world_arm(world)
    o = world.other(r)
    if arm == "F3":
        if not _can_wait(world, o) and _can_wait(world, r):
            return float(world.pool)
        if not _can_wait(world, r) and _can_wait(world, o):
            return 0.0
        return world.pool / 2
    if arm in ("F2", "F4", "F5"):
        return float(settlement(world, r, arm))
    return float(_max_claim(world, r, w))


def holdout_leverage(world, w):
    """Holdout leverage (prereg definition): max over partners r of (forced_amount(r) - r's contribution share of the pot) / pot,
    clipped at 0, where the contribution share counts everything r put into the household (pot and bills, the F4 basis). 1 = one
    partner can take the whole pot without having put anything in; 0 = no partner can force more than their own contribution share.
    Capability, not exercise. F4 is 0 by construction (its settlement IS the reference). None when the pot is empty or a partner is
    out."""
    if world.pool <= 0 or not all(world.p[x]["in"] for x in "AB"):
        return None
    out = 0.0
    for r in "AB":
        own = world.pool * contribution_share(world, r, "all")
        out = max(out, (forced_amount(world, r, w) - own) / world.pool)
    return out
