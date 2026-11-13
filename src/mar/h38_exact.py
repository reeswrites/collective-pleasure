"""H38's mechanism as a tiny exact model: two people, together or apart, a pairing-pressure dial, one formation and stay rule.

Wording rule (ADR 0010): agents feel nothing; "pleasure" is a gloss for a modeled number. Every number is ASSUMED.

The step-back review (docs/notes/step-back-review.md, plan step 2) asked for this beside the household simulation: the household
gave H38 three signs across three agent sets, and the exact models (horizon, liking vs wanting, H32-v2) are what held up. Results:
docs/results/h38-exact-model.md. Nothing here touches the household; it reads nothing from it.

Time is in 13-week blocks (the household's reading cadence), T = 12 blocks = 156 weeks. Every quantity is per week.

The world (per person, per week, raw pleasure before the scale):
  apart     base                                                       (base includes friend contact)
  together  base - cost + rel[q] + intrinsic * v - withdraw * contact    q = the household's state (good, mid, bad), a Markov
                                                                         chain over blocks; drawn from q0 at formation
  pressure  together: + reward.  apart: - stigma, and - exit_stigma for exit_blocks blocks after the person leaves (the leaver only)
  suffering together suff_together[q], apart suff_apart (never scaled)
The scale turns raw into pleasure: "cap" (clip to [0, 1], the household's), "sat" (ADR 0019's curve: identity below a knee of 0.8, then a saturating
curve with slope 1 at the knee and asymptote 1; the review's option b), "uncapped" (floor 0 only).
"Lived" pleasure is the same with the direct terms (reward, stigma, exit stigma) taken out: what pressure does to how people live.
Withdrawal and the intrinsic values-pairing term are part of the life, so they stay in.

Choosers. A pair forms only if both say yes (at block 0, and at each later block while never formed: the household's 13-week
retries; no reunion after a split, as in negotiation.BaselineLived). Either can end it at a block start (a stay reading).
  yardstick  "own" (own pleasure), "net" (own pleasure - w * own suffering), "evaluator" (the pair's total pleasure: everyone counts)
  rule       "rollout": the household's rule. Compare the mean yardstick over the next `horizon` blocks living together (no further
             choices, the state drifting) with the same span apart (the leaver's exit stigma included). "optimal": backward induction
             over the whole remaining time, each person on their own yardstick, partner's choices foreseen (subgame perfect).
  bias       added to every forecast week together, in yardstick units. < 0 under-forms, > 0 over-forms. The named distortion.
Agents see the pressure, as in the household.

Outputs (`solve`, `population`): pleasure everyone counted, lived pleasure, raw, suffering, net, weeks together, and the freedom side:
held (share of stay readings where a person stays only because of pressure: stays with it, would leave with it removed; the
stay lens of pairing.stay_reading), held_time (share of person-weeks lived in a household one would leave without pressure),
pushed_in (formation decisions where the pair forms only because of pressure), flipped (share of all personal decisions that
pressure changes). The domination proxy is held_time; flipped is the wider reading.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace
from functools import lru_cache
from itertools import product

UNIT = 0.02      # pleasure per week per dial level, as pairing.UNIT (ASSUMED there)
D_PER = 0.15     # withdrawal per dial level, as pairing.D_PER
D_MAX = 0.6
PARTS = ("stigma", "reward", "withdraw", "exit")
V_LEVELS = (0.0, 0.5, 1.0)
SCALES = ("cap", "sat", "uncapped")
YARDSTICKS = ("own", "net", "evaluator")
KNEE = 0.8


@dataclass(frozen=True)
class World:
    """Every field is ASSUMED. Defaults are set from the H38 design and first principles (docs/results/h38-exact-model.md)."""
    T: int = 12                               # blocks of 13 weeks (156 weeks, the verdict's span)
    base: float = 0.95                        # raw pleasure apart: needs and aspirations nearly met (H38 L0 unclipped mean 1.00)
    contact: float = 0.06                     # friend contact inside base; withdrawal removes withdraw x contact while together
    cost: float = 0.05                        # what a household costs below the cap (bills, money, rest)
    rel: tuple = (0.25, 0.12, 0.0)            # relational gain together by state (good, mid, bad): time together, items
    suff_together: tuple = (0.13, 0.16, 0.25) # suffering together by state (formation check: 0.169 together vs 0.113 apart)
    suff_apart: float = 0.11
    stay_p: float = 0.7                       # chance the state keeps from one block to the next; else to a neighbour
    q0: tuple = (0.35, 0.40, 0.25)            # state at formation
    intrinsic: float = 0.04                   # pairing.INTRINSIC: + intrinsic x v per week together
    reunite: bool = False                     # may a pair re-form after a split (the household: no)

    def shifted(self, delta):
        """The same world with every state's relational gain moved by delta (how much a household is worth)."""
        return replace(self, rel=tuple(r + delta for r in self.rel))


@dataclass(frozen=True)
class Pressure:
    stigma: float = 0.0
    reward: float = 0.0
    withdraw: float = 0.0
    exit_stigma: float = 0.0
    exit_blocks: int = 2                      # 26 weeks, pairing.EXIT_WEEKS

    @property
    def off(self):
        return not (self.stigma or self.reward or self.withdraw or self.exit_stigma)


FREE = Pressure()


def dial(level, parts=PARTS):
    """H38's dial at `level` with only `parts` on (pairing.dial, same numbers)."""
    u = round(UNIT * level, 10)
    return Pressure(stigma=u if "stigma" in parts else 0.0, reward=u if "reward" in parts else 0.0,
                    withdraw=min(D_MAX, round(D_PER * level, 10)) if "withdraw" in parts else 0.0,
                    exit_stigma=u if "exit" in parts else 0.0)


@dataclass(frozen=True)
class Chooser:
    yardstick: str = "own"
    rule: str = "rollout"
    horizon: int = 4          # blocks (rollout only): 2 = the old 26-week rule, 4 = the corrected 52-week rule
    w: float = 1.0            # suffering weight of the net yardstick (the old rule: 1)
    bias: float = 0.0

    def label(self):
        h = f"{self.horizon * 13}w" if self.rule == "rollout" else "full"
        b = f" bias {self.bias:+.2f}" if self.bias else ""
        return f"{self.yardstick} {h}{b}"


PLANNER = Chooser("evaluator", "optimal")
OLD_RULE = Chooser("net", "rollout", 2)          # H38: net wellbeing over 26 weeks
CORRECTED = Chooser("own", "rollout", 4)         # formation check: own pleasure over 52 weeks


def scale(x, kind="cap", knee=KNEE):
    x = max(0.0, x)
    if kind == "uncapped":
        return x
    if kind == "cap":
        return min(1.0, x)
    if kind == "sat":
        return x if x <= knee else knee + (1 - knee) * (1 - math.exp(-(x - knee) / (1 - knee)))
    raise ValueError(kind)


def transition(world):
    n = len(world.rel)
    P = []
    for q in range(n):
        nb = [j for j in (q - 1, q + 1) if 0 <= j < n]
        row = [0.0] * n
        row[q] = world.stay_p if nb else 1.0
        for j in nb:
            row[j] += (1 - world.stay_p) / len(nb)
        P.append(tuple(row))
    return tuple(P)


_transition = lru_cache(maxsize=None)(transition)


# ---- one person-week ---------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Week:
    pleasure: float
    lived: float
    raw: float
    suff: float


def week(world, pr, v, together, q, exit_on, kind):
    if together:
        lived = world.base - world.cost + world.rel[q] + world.intrinsic * v - pr.withdraw * world.contact
        direct, suff = pr.reward, world.suff_together[q]
    else:
        lived = world.base
        direct, suff = -pr.stigma - (pr.exit_stigma if exit_on else 0.0), world.suff_apart
    raw = lived + direct
    return Week(scale(raw, kind), scale(lived, kind), raw, min(1.0, max(0.0, suff)))


# ---- the game ------------------------------------------------------------------------------------------------------------------
# A state at the start of a block: (tog, q, eA, eB, ever). tog: lived together last block (then q is the state the coming block
# will have); eA, eB: blocks of exit stigma left; ever: the pair has formed before.

@dataclass(frozen=True)
class Game:
    world: World
    pr: Pressure
    ch: Chooser
    kind: str
    v: tuple            # (vA, vB)

    @lru_cache(maxsize=None)
    def blk(self, together, q, cA, cB):
        """-> (week A, week B) for a block lived together (state q) or apart (exit counters cA, cB during the block)."""
        return tuple(week(self.world, self.pr, self.v[i], together, q, (cA, cB)[i] > 0, self.kind) for i in range(2))

    def y(self, i, wks, together):
        """Person i's perceived yardstick for one week of a block."""
        a, b = wks
        if self.ch.yardstick == "own":
            val = wks[i].pleasure
        elif self.ch.yardstick == "net":
            val = wks[i].pleasure - self.ch.w * wks[i].suff
        else:
            val = a.pleasure + b.pleasure
        return val + (self.ch.bias if together else 0.0)

    def branches(self, s, dA, dB):
        """-> [(prob, together, q of the block, cA, cB during the block, next state)]."""
        tog, q, eA, eB, ever = s
        XB, P, dec = self.pr.exit_blocks, _transition(self.world), (lambda e: max(0, e - 1))
        out = []
        if tog:
            if dA and dB:
                for q2, p in enumerate(P[q]):
                    if p:
                        out.append((p, True, q, eA, eB, (True, q2, dec(eA), dec(eB), True)))
            else:
                cA = eA if dA else (XB if self.pr.exit_stigma else 0)
                cB = eB if dB else (XB if self.pr.exit_stigma else 0)
                out.append((1.0, False, None, cA, cB, (False, None, dec(cA), dec(cB), True)))
        else:
            if self.eligible(s) and dA and dB:
                for qb, pb in enumerate(self.world.q0):
                    for q2, p in enumerate(P[qb]):
                        if pb * p:
                            out.append((pb * p, True, qb, eA, eB, (True, q2, dec(eA), dec(eB), True)))
            else:
                out.append((1.0, False, None, eA, eB, (False, None, dec(eA), dec(eB), ever)))
        return out

    def eligible(self, s):
        return (not s[0]) and ((not s[4]) or self.world.reunite)

    # -- the rollout rule --
    @lru_cache(maxsize=None)
    def rollout(self, i, t, s, together):
        """Mean perceived yardstick over the next min(horizon, T - t) blocks: together (state drifting from the current one, or
        from q0 at formation) or apart (person i leaving now if the pair is together)."""
        h = min(self.ch.horizon, self.world.T - t)
        tog, q, eA, eB, _ = s
        tot = 0.0
        if together:
            P = _transition(self.world)
            dist = [0.0] * len(self.world.rel)
            if tog:
                dist[q] = 1.0
            else:
                dist = list(self.world.q0)
            for _ in range(h):
                tot += sum(p * self.y(i, self.blk(True, k, 0, 0), True) for k, p in enumerate(dist) if p)
                dist = [sum(dist[a] * P[a][b] for a in range(len(dist))) for b in range(len(dist))]
        else:
            c = [eA, eB]
            if tog and self.pr.exit_stigma:
                c[i] = self.pr.exit_blocks
            for _ in range(h):
                tot += self.y(i, self.blk(False, None, c[0], c[1]), False)
                c = [max(0, e - 1) for e in c]
        return tot / h

    def decide_rollout(self, t, s):
        if not s[0] and not self.eligible(s):
            return (False, False)
        return tuple(self.rollout(i, t, s, True) >= self.rollout(i, t, s, False) for i in range(2))

    # -- the optimal rule (backward induction) --
    def value(self, t, s, dA, dB):
        """-> (VA, VB): perceived yardstick summed over blocks t.. with the given choices now and equilibrium choices later."""
        out = [0.0, 0.0]
        for p, tg, q, cA, cB, nxt in self.branches(s, dA, dB):
            wks = self.blk(tg, q, cA, cB)
            cont = self.V(t + 1, nxt) if t + 1 < self.world.T else (0.0, 0.0)
            for i in range(2):
                out[i] += p * (self.y(i, wks, tg) + cont[i])
        return tuple(out)

    @lru_cache(maxsize=None)
    def V(self, t, s):
        return self.value(t, s, *self.decide_optimal(t, s))

    @lru_cache(maxsize=None)
    def decide_optimal(self, t, s):
        if not s[0] and not self.eligible(s):
            return (False, False)
        yes = self.value(t, s, True, True)
        if s[0]:   # each compares staying (partner stays) with leaving alone
            return (yes[0] >= self.value(t, s, False, True)[0], yes[1] >= self.value(t, s, True, False)[1])
        no = self.value(t, s, False, False)
        return (yes[0] >= no[0], yes[1] >= no[1])

    def decide(self, t, s):
        return self.decide_rollout(t, s) if self.ch.rule == "rollout" else self.decide_optimal(t, s)


METRICS = ("pleasure", "lived", "raw", "suff", "net", "together", "formed0", "ends", "held", "worth", "leave", "held_time",
           "pushed_in", "kept_out", "flipped", "readings", "formations")


@lru_cache(maxsize=None)
def solve(world=World(), pr=FREE, ch=CORRECTED, kind="cap", v=(0.5, 0.5)):
    """Exact expected outcomes for one pair (forward over the state distribution, decisions from `ch` under `pr`; the stay lens
    and flips against the same chooser with the pressure removed). -> dict of METRICS. Means are per person-week."""
    g, f = Game(world, pr, ch, kind, v), Game(world, FREE, ch, kind, v)
    dist = {(False, None, 0, 0, False): 1.0}
    acc = dict.fromkeys(METRICS, 0.0)
    held = worth = leave = readings = held_time = form_dec = pushed = kept = flips = decisions = splits = forms = 0.0
    for t in range(world.T):
        nd = {}
        for s, ps in dist.items():
            d = g.decide(t, s)
            free_s = (s[0], s[1], 0, 0, s[4])
            d0 = f.decide(t, free_s)
            if s[0] or g.eligible(s):
                decisions += 2 * ps
                flips += ps * sum(d[i] != d0[i] for i in range(2))
            if s[0]:
                readings += 2 * ps
                for i in range(2):
                    if d[i] and d0[i]:
                        worth += ps
                    elif d[i]:
                        held += ps
                    elif not d0[i]:
                        leave += ps
                if d[0] and d[1]:
                    held_time += ps * sum(not d0[i] for i in range(2))
                else:
                    splits += ps
            elif g.eligible(s):
                form_dec += ps
                yes, yes0 = d[0] and d[1], d0[0] and d0[1]
                pushed += ps * (yes and not yes0)
                kept += ps * (yes0 and not yes)
                forms += ps * yes
                if yes:   # a block lived together by someone who would not have formed without pressure
                    held_time += ps * sum(not d0[i] for i in range(2))
                if t == 0:
                    acc["formed0"] = float(yes)
            for p, tg, q, cA, cB, nxt in g.branches(s, *d):
                w = ps * p
                wks = g.blk(tg, q, cA, cB)
                for k in wks:
                    acc["pleasure"] += w * k.pleasure
                    acc["lived"] += w * k.lived
                    acc["raw"] += w * k.raw
                    acc["suff"] += w * k.suff
                acc["together"] += w * tg
                nd[nxt] = nd.get(nxt, 0.0) + w
        dist = nd
    n = 2 * world.T
    for k in ("pleasure", "lived", "raw", "suff"):
        acc[k] /= n
    acc["net"] = acc["pleasure"] - acc["suff"]
    acc["together"] /= world.T
    acc["held_time"] = held_time / n
    acc["ends"] = splits / forms if forms else 0.0
    acc["held"], acc["worth"], acc["leave"] = ((held / readings, worth / readings, leave / readings) if readings else (0.0, 0.0, 0.0))
    acc["pushed_in"], acc["kept_out"] = (pushed / form_dec, kept / form_dec) if form_dec else (0.0, 0.0)
    acc["flipped"] = flips / decisions if decisions else 0.0
    acc["readings"], acc["formations"] = readings, forms
    return acc


PAIRS = tuple(product(V_LEVELS, repeat=2))
MATCH = (-0.10, -0.05, 0.0, 0.05, 0.10)   # pairs differ in how good their household is: a shift of rel, known to both (ASSUMED)


def population(world=World(), pr=FREE, ch=CORRECTED, kind="cap", pairs=PAIRS, match=MATCH):
    """Mean of `solve` over a population of pairs: every ordered pair of values-pairing weights times every match shift,
    equally weighted (45 pairs by default)."""
    rows = [solve(world.shifted(m), pr, ch, kind, v) for v in pairs for m in match]
    return {k: sum(r[k] for r in rows) / len(rows) for k in METRICS}


def effect(world=World(), pr=None, ch=CORRECTED, kind="cap", pairs=PAIRS, match=MATCH):
    """Pressure `pr` (default the dial at L4) against none, same chooser. -> dict: d_pleasure, d_lived, d_direct, d_together,
    plus the pressured run's held, held_time, pushed_in, kept_out, flipped, and the free run's gap to the planner."""
    pr = dial(4) if pr is None else pr
    a, b = population(world, FREE, ch, kind, pairs, match), population(world, pr, ch, kind, pairs, match)
    best = population(world, FREE, PLANNER, kind, pairs, match)
    return {"d_pleasure": b["pleasure"] - a["pleasure"], "d_lived": b["lived"] - a["lived"],
            "d_direct": (b["pleasure"] - b["lived"]) - (a["pleasure"] - a["lived"]), "d_together": b["together"] - a["together"],
            "d_net": b["net"] - a["net"],
            "held": b["held"], "held_time": b["held_time"], "pushed_in": b["pushed_in"], "kept_out": b["kept_out"],
            "flipped": b["flipped"], "free_gap": best["pleasure"] - a["pleasure"],
            "free_together_gap": a["together"] - best["together"], "free": a, "pressed": b}


def sign(x, tol=5e-4):
    return "+" if x > tol else "-" if x < -tol else "0"


def verdict(e, tol=5e-4):
    """The evaluator rule (2026-11-12): a win raises pleasure without raising domination. -> "win", "trade-off", "loss" or "none"."""
    up, dom = e["d_pleasure"] > tol, e["held_time"] > tol or e["held"] > tol
    if up and not dom:
        return "win"
    if up:
        return "trade-off"
    return "loss" if e["d_pleasure"] < -tol else "none"


# ---- the sign map ----------------------------------------------------------------------------------------------------------------

CHOOSERS = tuple(Chooser(y, "rollout", h) for y in YARDSTICKS for h in (1, 2, 4, 12)) + tuple(Chooser(y, "optimal") for y in YARDSTICKS)
BIASES = (-0.06, -0.03, 0.0, 0.03, 0.06)
WORTH = (-0.20, -0.15, -0.10, -0.05, 0.0, 0.05)


def sign_map(pr=None, worlds=WORTH, biases=(0.0,), choosers=CHOOSERS, kinds=SCALES):
    """-> list of rows (chooser label, scale, worth shift, bias, effect numbers)."""
    rows = []
    for ch, kind, dw, b in product(choosers, kinds, worlds, biases):
        c = replace(ch, bias=b)
        e = effect(World().shifted(dw), pr, c, kind)
        rows.append({"chooser": c.label(), "yardstick": c.yardstick, "rule": c.rule, "horizon": c.horizon, "scale": kind,
                     "worth": dw, "bias": b, **{k: v for k, v in e.items() if k not in ("free", "pressed")},
                     "verdict": verdict(e)})
    return rows


KEY = (OLD_RULE, CORRECTED, Chooser("own", "optimal"), PLANNER)
PART_SETS = {"L4": PARTS, "stigma": ("stigma",), "reward": ("reward",), "exit": ("exit",), "withdraw": ("withdraw",),
             "no withdraw": ("stigma", "reward", "exit")}


def _line(e):
    return (f"dP {e['d_pleasure']:+.3f}  lived {e['d_lived']:+.3f}  direct {e['d_direct']:+.3f}  together {e['d_together']:+.2f}  "
            f"held {e['held']:.2f}  held_time {e['held_time']:.2f}  {verdict(e)}")


def wins(levels=(0.5, 1, 4), choosers=(OLD_RULE, CORRECTED, Chooser("own", "rollout", 1), Chooser("own", "optimal"), PLANNER),
         biases=(-0.06, 0.0, 0.06), worlds=(-0.10, 0.0, 0.05)):
    """The evaluator rule over a grid: -> (counts by verdict, list of winning cells)."""
    counts, out = {}, []
    for L, (name, parts), ch, b, kind, dw in product(levels, PART_SETS.items(), choosers, biases, SCALES, worlds):
        c = replace(ch, bias=b)
        e = effect(World().shifted(dw), dial(L, parts), c, kind)
        v = verdict(e)
        counts[v] = counts.get(v, 0) + 1
        if v == "win":
            out.append((L, name, c.label(), kind, dw, e))
    return counts, out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="H38 exact model: the tables in docs/results/h38-exact-model.md")
    ap.add_argument("--wins", action="store_true", help="also search the grid for evaluator-rule wins (a few minutes)")
    a = ap.parse_args(argv)
    print("== The full dial at L4 against none, by scale, household worth and chooser")
    for kind, dw, ch in product(SCALES, WORTH, KEY):
        e = effect(World().shifted(dw), dial(4), ch, kind)
        f = e["free"]
        print(f"{kind:<8} worth {dw:+.2f}  {ch.label():<15} L0: formed {f['formed0']:.2f} together {f['together']:.2f}  "
              f"gap to planner {e['free_gap']:+.4f} | {_line(e)}")
    print("== Each part alone at L4 (cap)")
    for dw, ch, (name, parts) in product((0.0, -0.10), KEY, PART_SETS.items()):
        print(f"worth {dw:+.2f}  {ch.label():<15} {name:<12} {_line(effect(World().shifted(dw), dial(4, parts), ch, 'cap'))}")
    print("== Formation quality: forecast bias (own 52w and planner, cap)")
    for dw, b, ch in product((0.0, -0.10), BIASES, (CORRECTED, PLANNER)):
        e = effect(World().shifted(dw), dial(4), replace(ch, bias=b), "cap")
        print(f"worth {dw:+.2f}  {replace(ch, bias=b).label():<26} L0 together {e['free']['together']:.2f}  {_line(e)}")
    if a.wins:
        counts, ws = wins()
        print("== Evaluator rule:", counts)
        for L, name, lab, kind, dw, e in ws:
            print(f"win: L{L} {name} {lab} {kind} worth {dw:+.2f} {_line(e)} flipped {e['flipped']:.3f}")


if __name__ == "__main__":
    main()
