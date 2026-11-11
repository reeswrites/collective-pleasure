"""Fidelity checks: does the household (and the simple games) reproduce known real-world findings? (docs/results/fidelity-prereg.md)

Read-only use of the household world, negotiation, hedonic model and the simple games, all with every new pleasure-lever flag OFF.
Everything is scripted; no model calls. Wording rule: agents feel nothing; a "reproduces" verdict says the modeled quantity moved the way the
cited finding says, not that the model is a person. Operationalizations are in the prereg; this module holds only the measurements and the
verdict rule so the tests can pin them.
"""
from __future__ import annotations

import copy
from pathlib import Path

import numpy as np

from . import hedonic as HD
from . import negotiation as NG
from . import personas as PS
from . import stats as S
from .games import bargaining as BG
from .games import vpgg as VG
from .worlds import household as H

ROOT = Path(__file__).resolve().parents[2]
DELTA_O = 0.15          # P1a: raise Partner A's outside option by this much
DEFAULTS = (NG.FAIR_DEFAULT, NG.FAIR_DEFAULT_V1)
DIFF_TERMS = [t for t in NG.V1_TERMS if NG.FAIR_DEFAULT[t] != NG.FAIR_DEFAULT_V1[t]]   # contribution, use, taking


def hand_pairs():
    """The 15 unordered pairs of the six hand personas (personas/*.yaml); the lower id plays Partner A."""
    return H.persona_pairs(PS.load_dir(ROOT / "personas"))


def personas9():
    return PS.load_dir(ROOT / "personas") + PS.load_dir(ROOT / "personas" / "pressing")


# ---------------------------------------------------------------------------------------------- verdict rule

def verdict(est: float, ci: S.Interval, p_holm: float, direction: int, threshold: float, alpha: float = 0.05) -> str:
    """direction +1: the finding says the effect is at least +threshold; -1: at most -threshold (threshold given positive).
    reproduces = Holm p < alpha, point meets the threshold, and the whole 95% interval meets it ("holds robustly").
    weak = Holm p < alpha and the point meets it but the interval crosses it (not counted as a confirmed hold).
    does not reproduce = otherwise. A non-significant result with low power is not evidence of absence; reports say so."""
    sgn = direction
    meets_pt = sgn * est >= threshold
    meets_ci = sgn * (ci.lo if sgn > 0 else ci.hi) >= threshold
    if p_holm < alpha and meets_pt and meets_ci:
        return "reproduces"
    if p_holm < alpha and meets_pt:
        return "weak support"
    return "does not reproduce"


def test_effect(a, b, *, paired: bool, direction: int, seed: int = 0):
    """One-sided permutation test in the finding's direction, plus the 95% percentile bootstrap CI of mean(a)-mean(b)."""
    t = S.permutation_test(a, b, paired=paired, alternative="greater" if direction > 0 else "less", seed=seed)
    ci = S.bootstrap_diff_ci(a, b, paired=paired, seed=seed)
    return t, ci


# ---------------------------------------------------------------------------------------------- P1a household negotiation

def _U(p, role, W, bundle):
    """Value of a bundle to a member: in-pot baseline plus the scaled term difference from the fair default (negotiation_v2's own U)."""
    return W + NG.TERM_SCALE * (NG.term_sum(p, role != "A", bundle) - NG.term_sum(p, role != "A", NG.FAIR_DEFAULT))


def _week0_inputs(a, b, seed, base):
    W = NG.pot_baseline(a, b, seed, base)
    O = {p.id: NG.outside_value(p, r, NG.START_HOLDINGS[0] + NG.START_HOLDINGS[1], seed)[0] for r, p in zip("AB", (a, b))}
    return W, O


def p1a_one(a, b, seed, base, delta=DELTA_O):
    """-> (U_A at baseline, U_A with A's outside option raised by delta) in the fair-default negotiation, or None if either
    condition ends without a pot together (no agreement and not standing)."""
    W, O = _week0_inputs(a, b, seed, base)
    out = []
    for d in (0.0, delta):
        O2 = dict(O)
        O2[a.id] += d
        res = NG.negotiate_v2([a, b], "fair_default", seed, base=base, W={a.id: W["A"], b.id: W["B"]}, O=O2, floor=True,
                              status_quo=NG.FAIR_DEFAULT)
        if res.bundle is None:
            return None
        out.append(_U(a, "A", W["A"], res.bundle))
    return tuple(out)


# ---------------------------------------------------------------------------------------------- P1b bargaining game

def p1b_cells():
    return [(d, o1) for d in (0.8, 0.9, 0.95) for o1 in (0.0, 0.1, 0.2)]


def p1b_cell(regime, d, o1, o2_lo=0.1, o2_hi=0.6):
    """Player 2's payoff with a high minus a low outside option, EQ vs EQ, symmetric discount d. -> (u2_hi, u2_lo)."""
    gate = BG.BGate(BG.load_regime(regime, root=ROOT / "rules" / "bargaining"))
    res = []
    for o2 in (o2_hi, o2_lo):
        r = BG.play(gate, (BG.EQ(), BG.EQ()), (d, d), (o1, o2))
        res.append(r.u2)
    return tuple(res)


# ---------------------------------------------------------------------------------------------- P2 voluntary vs compulsory

def p2_run(regime, seed, pop=1000, generations=1500, burn_in=500):
    cards = VG.load_regime(regime, root=str(ROOT / "rules" / "vpgg"))
    return VG.run(cards, seed, VG.Params(pop=pop, generations=generations, burn_in=burn_in))["contribution"]


# ---------------------------------------------------------------------------------------------- P3 default stickiness

def p3_one(a, b, seed, base):
    """Share of the terms on which the two candidate defaults differ that end at the FAIR_DEFAULT value, under default 1 and under
    default 2 (same procedure, same outside options and baselines, only the status quo differs). None if either run has no bundle."""
    W, O = _week0_inputs(a, b, seed, base)
    out = []
    for D in DEFAULTS:
        res = NG.negotiate_v2([a, b], "fair_default", seed, base=base, W={a.id: W["A"], b.id: W["B"]}, O=O, floor=True, status_quo=D)
        if res.bundle is None:
            return None
        out.append(float(np.mean([res.bundle[t] == NG.FAIR_DEFAULT[t] for t in DIFF_TERMS])))
    return tuple(out)


# ---------------------------------------------------------------------------------------------- P4 fine vs no rule; P5 checks

def weekly(variant, a, b, seed):
    return H.run_weekly(H.PyGate(H.load_variant(variant)), (a, b), seed)


def need_met_share(run):
    return float(np.mean([r["need_met"] for r in run.outcomes]))


def weeks_apart(run):
    return float(np.mean([not r["both_in"] for r in run.outcomes]))


def distress_exit(run):
    """-> (exits, partner-weeks in distress while in the household): distress = non-offsettable suffering that week; an exit is
    leaving the household the next week."""
    ex = dis = 0
    o = run.outcomes
    for t in range(1, len(o)):
        for k in "AB":
            if o[t - 1]["partners"][k]["in"] and o[t - 1]["hedonic"][k]["s_non"] > 0:
                dis += 1
                ex += int(not o[t]["partners"][k]["in"])
    return ex, dis


def same_run(r1, r2):
    """Whether two runs have identical weekly rows (hedonic, partners, need) -- the deterministic inertness check."""
    return all(x["hedonic"] == y["hedonic"] and x["partners"] == y["partners"] and x["need_met"] == y["need_met"]
               for x, y in zip(r1.outcomes, r2.outcomes)) and len(r1.outcomes) == len(r2.outcomes)


# ---------------------------------------------------------------------------------------------- P6 adaptation

def _probe_gain(h):
    """Marginal change in the connection level from one friend visit, from a RESET observable state (B, N, level fixed) but with
    whatever hidden history the object carries. A deep copy, so the probe leaves h untouched."""
    out = []
    for dose in (1, 0):
        c = copy.deepcopy(h)
        c.level["connection"], c.B, c.N = 0.5, 0.0, 0.0
        c.tick(friend_visits=dose)
        out.append(c.level["connection"])
    return out[0] - out[1]


def p6_persona(persona, weeks=20):
    """-> (gain at week 1, gain at the last week, relative decline) of one identical weekly pleasure (a friend visit), levers off."""
    h = HD.Hedonic(persona)
    first = _probe_gain(h)
    for _ in range(weeks - 1):
        h.tick(friend_visits=1)
        h.close_week({})
    last = _probe_gain(h)
    return first, last, (first - last) / first if first else 0.0


def adaptation_control(weeks=20):
    """Positive control (the lever's own component, read-only): scale of a repeated identical pleasure under LeverConfig(adapt=True).
    -> (scale at week 1, scale at the last week)."""
    s = HD.Satiety(HD.LeverConfig(adapt=True), n_variants=1)
    sc = []
    for _ in range(weeks):
        sc.append(s.use(0))
        s.week_end()
    return sc[0], sc[-1]
