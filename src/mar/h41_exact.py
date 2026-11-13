"""H41's choice aids in the H38 exact model (src/mar/h38_exact.py): a known-answer side model for trial periods and cheap exits.

Wording rule (ADR 0010): agents feel nothing; "pleasure" is a gloss for a modeled number. Every number is ASSUMED.

The H38 exact model (docs/results/h38-exact-model.md) has two people in 13-week blocks, together or apart, a pressure dial, and
choosers that form only if both say yes and stay unless either leaves. This extension adds three things, each off by default, so that
with all three off it reproduces h38_exact.solve exactly (tests/test_h41_exact.py):

  exit_cost   a cost of leaving that is not pressure: for `exit_cost_blocks` blocks after a person leaves, their raw pleasure is lower
              by exit_cost a week (a new place, moving, the things left behind). Part of how people live, so it stays in "lived".
  apart_gain  cheaper solo housing: raw pleasure apart is higher by apart_gain a week, for everyone apart (the cost of living alone
              falls, so leaving AND staying single get better).
  trial       every formation is a trial: the formation is decided over the trial (one block for a rollout chooser), and at the end of
              the first block together each person may leave with no exit cost and no exit stigma.

The freedom side gains one lens. held (as in H38) is "stays only because of pressure". held_cost is "stays only because of pressure or
the exit cost": with both removed the person would leave. held_time_cost is the matching share of person-weeks. Formation is reported
as formed0 (both say yes at block 0) and together (share of blocks together).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache

from . import h38_exact as X

FREE = X.FREE


@dataclass(frozen=True)
class Aids:
    exit_cost: float = 0.0
    exit_cost_blocks: int = 1
    apart_gain: float = 0.0
    trial: bool = False

    def free(self):
        """The counterfactual of the held_cost lens: the same aids with the exit cost removed."""
        return replace(self, exit_cost=0.0)


NONE = Aids()


@dataclass(frozen=True)
class Game:
    world: X.World
    pr: X.Pressure
    ch: X.Chooser
    kind: str
    v: tuple
    aid: Aids

    # state: (tog, q, eA, eB, xA, xB, ever, fresh). eA, eB: blocks of exit stigma left; xA, xB: blocks of exit cost left;
    # fresh: the coming block together is the first after formation (its end is the trial's end).

    @lru_cache(maxsize=None)
    def blk(self, together, q, cA, cB, kA, kB):
        out = []
        for i in range(2):
            w = self.world
            if together:
                lived = w.base - w.cost + w.rel[q] + w.intrinsic * self.v[i] - self.pr.withdraw * w.contact
                direct, suff = self.pr.reward, w.suff_together[q]
            else:
                lived = w.base + self.aid.apart_gain - (self.aid.exit_cost if (kA, kB)[i] > 0 else 0.0)
                direct = -self.pr.stigma - (self.pr.exit_stigma if (cA, cB)[i] > 0 else 0.0)
                suff = w.suff_apart
            raw = lived + direct
            out.append(X.Week(X.scale(raw, self.kind), X.scale(lived, self.kind), raw, min(1.0, max(0.0, suff))))
        return tuple(out)

    def y(self, i, wks, together):
        a, b = wks
        if self.ch.yardstick == "own":
            val = wks[i].pleasure
        elif self.ch.yardstick == "net":
            val = wks[i].pleasure - self.ch.w * wks[i].suff
        else:
            val = a.pleasure + b.pleasure
        return val + (self.ch.bias if together else 0.0)

    def eligible(self, s):
        return (not s[0]) and ((not s[6]) or self.world.reunite)

    def branches(self, s, dA, dB):
        tog, q, eA, eB, xA, xB, ever, fresh = s
        P, dec = X._transition(self.world), (lambda e: max(0, e - 1))
        XB, KB = self.pr.exit_blocks, self.aid.exit_cost_blocks
        out = []
        if tog:
            if dA and dB:
                for q2, p in enumerate(P[q]):
                    if p:
                        out.append((p, True, q, eA, eB, xA, xB, (True, q2, dec(eA), dec(eB), dec(xA), dec(xB), True, False)))
            else:
                end = s[7] == "end"
                cA = eA if dA else (XB if (self.pr.exit_stigma and not end) else 0)
                cB = eB if dB else (XB if (self.pr.exit_stigma and not end) else 0)
                kA = xA if dA else (KB if (self.aid.exit_cost and not end) else 0)
                kB = xB if dB else (KB if (self.aid.exit_cost and not end) else 0)
                out.append((1.0, False, None, cA, cB, kA, kB, (False, None, dec(cA), dec(cB), dec(kA), dec(kB), True, False)))
        else:
            if self.eligible(s) and dA and dB:
                for qb, pb in enumerate(self.world.q0):
                    for q2, p in enumerate(P[qb]):
                        if pb * p:
                            out.append((pb * p, True, qb, eA, eB, xA, xB,
                                        (True, q2, dec(eA), dec(eB), dec(xA), dec(xB), True, "end" if self.aid.trial else False)))
            else:
                out.append((1.0, False, None, eA, eB, xA, xB, (False, None, dec(eA), dec(eB), dec(xA), dec(xB), ever, False)))
        return out

    def horizon(self, t, s):
        h = self.ch.horizon
        if self.aid.trial and not s[0]:
            h = 1                                 # a rollout chooser scores a trial over the trial itself
        return min(h, self.world.T - t)

    @lru_cache(maxsize=None)
    def rollout(self, i, t, s, together):
        h = self.horizon(t, s)
        tog, q, eA, eB, xA, xB, _, fresh = s
        tot = 0.0
        if together:
            P = X._transition(self.world)
            dist = [0.0] * len(self.world.rel)
            if tog:
                dist[q] = 1.0
            else:
                dist = list(self.world.q0)
            for _ in range(h):
                tot += sum(p * self.y(i, self.blk(True, k, 0, 0, 0, 0), True) for k, p in enumerate(dist) if p)
                dist = [sum(dist[a] * P[a][b] for a in range(len(dist))) for b in range(len(dist))]
        else:
            c, k = [eA, eB], [xA, xB]
            end = fresh == "end"
            if tog and self.pr.exit_stigma and not end:
                c[i] = self.pr.exit_blocks
            if tog and self.aid.exit_cost and not end:
                k[i] = self.aid.exit_cost_blocks
            for _ in range(h):
                tot += self.y(i, self.blk(False, None, c[0], c[1], k[0], k[1]), False)
                c, k = [max(0, e - 1) for e in c], [max(0, e - 1) for e in k]
        return tot / h

    def decide_rollout(self, t, s):
        if not s[0] and not self.eligible(s):
            return (False, False)
        return tuple(self.rollout(i, t, s, True) >= self.rollout(i, t, s, False) for i in range(2))

    def value(self, t, s, dA, dB):
        out = [0.0, 0.0]
        for p, tg, q, cA, cB, kA, kB, nxt in self.branches(s, dA, dB):
            wks = self.blk(tg, q, cA, cB, kA, kB)
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
        if s[0]:
            return (yes[0] >= self.value(t, s, False, True)[0], yes[1] >= self.value(t, s, True, False)[1])
        no = self.value(t, s, False, False)
        return (yes[0] >= no[0], yes[1] >= no[1])

    def decide(self, t, s):
        return self.decide_rollout(t, s) if self.ch.rule == "rollout" else self.decide_optimal(t, s)


METRICS = X.METRICS + ("held_cost", "held_time_cost", "trial_ends")
START = (False, None, 0, 0, 0, 0, False, False)


@lru_cache(maxsize=None)
def solve(world=X.World(), pr=FREE, ch=X.CORRECTED, kind="cap", v=(0.5, 0.5), aid=NONE):
    """As h38_exact.solve, with the aids. The held lens compares with the same chooser under no pressure (H38's); the held_cost lens
    with no pressure and no exit cost."""
    g = Game(world, pr, ch, kind, v, aid)
    f = Game(world, FREE, ch, kind, v, aid)
    fc = Game(world, FREE, ch, kind, v, aid.free())
    dist = {START: 1.0}
    acc = dict.fromkeys(METRICS, 0.0)
    held = worth = leave = readings = held_time = form_dec = pushed = kept = flips = decisions = splits = forms = 0.0
    held_c = held_time_c = trial_ends = 0.0
    for t in range(world.T):
        nd = {}
        for s, ps in dist.items():
            d = g.decide(t, s)
            free_s = s[:2] + (0, 0) + s[4:]
            d0 = f.decide(t, free_s)
            dc = fc.decide(t, s[:2] + (0, 0, 0, 0) + s[6:])
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
                    if d[i] and not dc[i]:
                        held_c += ps
                if d[0] and d[1]:
                    held_time += ps * sum(not d0[i] for i in range(2))
                    held_time_c += ps * sum(not dc[i] for i in range(2))
                else:
                    splits += ps
                    if s[7] == "end":
                        trial_ends += ps
            elif g.eligible(s):
                form_dec += ps
                yes, yes0 = d[0] and d[1], d0[0] and d0[1]
                pushed += ps * (yes and not yes0)
                kept += ps * (yes0 and not yes)
                forms += ps * yes
                if yes:
                    held_time += ps * sum(not d0[i] for i in range(2))
                    held_time_c += ps * sum(not dc[i] for i in range(2))
                if t == 0:
                    acc["formed0"] = float(yes)
            for p, tg, q, cA, cB, kA, kB, nxt in g.branches(s, *d):
                w = ps * p
                for k in g.blk(tg, q, cA, cB, kA, kB):
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
    acc["held_time"], acc["held_time_cost"] = held_time / n, held_time_c / n
    acc["ends"] = splits / forms if forms else 0.0
    acc["held"], acc["worth"], acc["leave"] = ((held / readings, worth / readings, leave / readings) if readings else (0.0, 0.0, 0.0))
    acc["held_cost"] = held_c / readings if readings else 0.0
    acc["trial_ends"] = trial_ends / forms if forms else 0.0
    acc["pushed_in"], acc["kept_out"] = (pushed / form_dec, kept / form_dec) if form_dec else (0.0, 0.0)
    acc["flipped"] = flips / decisions if decisions else 0.0
    acc["readings"], acc["formations"] = readings, forms
    return acc


def population(world=X.World(), pr=FREE, ch=X.CORRECTED, kind="sat", aid=NONE, pairs=X.PAIRS, match=X.MATCH):
    rows = [solve(world.shifted(m), pr, ch, kind, v, aid) for v in pairs for m in match]
    return {k: sum(r[k] for r in rows) / len(rows) for k in METRICS}


# ---- H41's comparisons --------------------------------------------------------------------------------------------------------

BASE = Aids(exit_cost=0.04, exit_cost_blocks=1)        # ASSUMED: a block of a new place and its costs after leaving
ARMS = {"baseline": BASE, "cheap exit (no exit cost)": replace(BASE, exit_cost=0.0),
        "cheap solo housing": replace(BASE, apart_gain=0.01), "trial": replace(BASE, trial=True),
        "trial + cheap exit": replace(BASE, trial=True, exit_cost=0.0)}
CHOOSERS = {"rollout own 52w": X.CORRECTED, "rollout net w=1 52w": X.Chooser("net", "rollout", 4, w=1.0),
            "optimal own": X.Chooser("own", "optimal"), "optimal net w=1": X.Chooser("net", "optimal", w=1.0), "planner": X.PLANNER}
LEVELS = (0.5, 1, 2, 4)


def table(worth=0.0, kind="sat"):
    """Per chooser: each aid against the baseline, and the pressure levels against the baseline. -> rows."""
    rows = []
    wd = X.World().shifted(worth)
    for cname, ch in CHOOSERS.items():
        b = population(wd, FREE, ch, kind, BASE)
        for aname, aid in ARMS.items():
            a = population(wd, FREE, ch, kind, aid)
            rows.append({"chooser": cname, "arm": aname, **_d(a, b)})
        for L in LEVELS:
            a = population(wd, X.dial(L), ch, kind, BASE)
            rows.append({"chooser": cname, "arm": f"pressure L{L:g}", **_d(a, b)})
    return rows


def _d(a, b):
    return {"together": a["together"], "d_together": a["together"] - b["together"], "formed0": a["formed0"],
            "d_pleasure": a["pleasure"] - b["pleasure"], "d_lived": a["lived"] - b["lived"], "d_suff": a["suff"] - b["suff"],
            "held": a["held"], "held_cost": a["held_cost"], "held_time_cost": a["held_time_cost"], "trial_ends": a["trial_ends"]}


def main():
    for worth in (0.0, -0.05, -0.10):
        print(f"== household worth {worth:+.2f}, saturating scale; each arm against the baseline (exit cost {BASE.exit_cost} for "
              f"{BASE.exit_cost_blocks} block)")
        for r in table(worth):
            print(f"{r['chooser']:<20} {r['arm']:<26} together {r['together']:.3f} ({r['d_together']:+.3f})  dP {r['d_pleasure']:+.4f}  "
                  f"lived {r['d_lived']:+.4f}  dS {r['d_suff']:+.4f}  held {r['held']:.3f}  held_cost {r['held_cost']:.3f}  "
                  f"trial_ends {r['trial_ends']:.2f}")


if __name__ == "__main__":
    main()
