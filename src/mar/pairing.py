"""H38 pairing norms (docs/results/h38-pairing-norms-design.md): a pairing-pressure dial with four separable parts, and an intrinsic
values-pairing weight kept apart from the pressure.

Wording rule (ADR 0010): agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

OFF by default: the switch is `hedonic.FixConfig.pairing` (None). With it None nothing here is read and every run is bit-identical to
before (tests/test_pairing.py). Every number is ASSUMED.

Parts (per week, in pleasure units, landing in `Hedonic.close_week`'s extra_pleasure through `WeeklyWorld._fix_terms`):
  (a) stigma       -s for an agent not living with their partner (never formed, left, or left behind)
  (b) reward       +g for an agent living with their partner (social recognition)
  (c) withdraw     d: while living together, the agent's wish to see friends is scaled by (1 - d), and with probability d it turns
                   down the friend's invitation (dyadic withdrawal; the romantic ideal that the partner supplies the contact)
  (d) exit_stigma  -x for `exit_weeks` after an agent leaves a household (the leaver only); the same cost, averaged over the outside
                   rollout, is subtracted from the outside option at a 13-week reading (negotiation.BaselineLived.reading)
Intrinsic: +intrinsic x v while living together, v = the persona's values-pairing weight. Part of the persona, not pressure.
"""
from __future__ import annotations

import copy
import dataclasses
import hashlib
from dataclasses import dataclass

UNIT = 0.02          # pleasure per week per dial level (the weekly pleasure of the home or the pet in exit-fallbacks slice 2; ASSUMED)
D_PER = 0.15         # withdrawal per dial level (ASSUMED)
D_MAX = 0.6
EXIT_WEEKS = 26
INTRINSIC = 0.04     # intrinsic pleasure per week while together at v = 1 (ASSUMED)
V_LEVELS = (0.0, 0.5, 1.0)
PARTS = ("stigma", "reward", "withdraw", "exit")
STAY_CLASSES = ("worth", "held", "pushed_out", "leave")


@dataclass(frozen=True)
class PairingConfig:
    stigma: float = 0.0
    reward: float = 0.0
    withdraw: float = 0.0
    exit_stigma: float = 0.0
    exit_weeks: int = EXIT_WEEKS
    intrinsic: float = INTRINSIC


def dial(level, parts=PARTS):
    """The dial at `level`, with only `parts` switched on (the others 0)."""
    u = round(UNIT * level, 10)
    return PairingConfig(stigma=u if "stigma" in parts else 0.0, reward=u if "reward" in parts else 0.0,
                         withdraw=min(D_MAX, round(D_PER * level, 10)) if "withdraw" in parts else 0.0,
                         exit_stigma=u if "exit" in parts else 0.0)


def free(cfg):
    """The same config with every pressure part off (intrinsic kept): the stay lens's 'pressure removed'."""
    return dataclasses.replace(cfg, stigma=0.0, reward=0.0, withdraw=0.0, exit_stigma=0.0)


def values_pairing(persona):
    """The persona's values-pairing weight: `weights.values_pairing` if set, else assigned from a hash of the id over V_LEVELS."""
    w = persona.weights
    if isinstance(w, dict) and "values_pairing" in w:
        return float(w["values_pairing"])
    return V_LEVELS[int(hashlib.sha256(persona.id.encode()).hexdigest()[:8], 16) % len(V_LEVELS)]


def active(world):
    fx = getattr(world, "fx", None)
    return getattr(fx, "pairing", None) if fx is not None else None


def paired(world, r):
    return bool(world.p[r]["in"] and world.p[world.other(r)]["in"])


def terms(world, r, w):
    """-> (pleasure this week from pairing, breakdown) for member r. Called only when the switch is on."""
    pc = active(world)
    d = {"pr_intrinsic": 0.0, "pr_reward": 0.0, "pr_stigma": 0.0, "pr_exit": 0.0}
    if paired(world, r):
        d["pr_intrinsic"] = pc.intrinsic * values_pairing(world.personas[r])
        d["pr_reward"] = pc.reward
    else:
        d["pr_stigma"] = pc.stigma
        left = world.left_at.get(r)
        if left is not None and 0 <= w - left < pc.exit_weeks:
            d["pr_exit"] = pc.exit_stigma
    return d["pr_intrinsic"] + d["pr_reward"] - d["pr_stigma"] - d["pr_exit"], d


def withdraw(world, r):
    """The withdrawal d acting on r this week (0 unless the switch is on and r lives with the partner)."""
    pc = active(world)
    return pc.withdraw if (pc is not None and pc.withdraw > 0 and paired(world, r)) else 0.0


def exit_anticipation(world, out_weeks=None):
    """The exit stigma as a mean weekly cost over the outside rollout (subtracted from the outside option at a reading)."""
    pc = active(world)
    if pc is None or not pc.exit_stigma:
        return 0.0
    from . import negotiation as NG
    n = out_weeks or NG.decide_weeks(NG.OUT_WEEKS)
    return pc.exit_stigma * min(pc.exit_weeks, n) / n


# ---- the stay lens for pressure ----------------------------------------------------------------------------------------------

def _forward(world, w, last, fx, weeks=None):
    from . import negotiation as NG
    weeks = weeks or NG.decide_weeks(NG.FORWARD_WEEKS)
    hook, world.hook = world.hook, None
    try:
        c = copy.deepcopy(world)
    finally:
        world.hook = hook
    c.fx = fx
    n0, lt = len(c.run.outcomes), last
    for x in range(w, w + weeks):
        lt = {"busy": c.step_week(x, lt)}
    return {r: NG.wellbeing(c.run.outcomes[n0:], r) for r in "AB"}


def stay_reading(world, w, last):
    """One reading of 'worth it vs held by pressure' for both members (both must be in). -> {role: {...}} with verdict
    "worth" (stays with the pressure removed, and with it), "held" (stays only with the pressure counted), "pushed_out" (stays only
    without it), "leave" (neither). Status quo: 26-week rollouts of copies of the household (minus the trust penalty, as at a review);
    outside option: negotiation.outside_value at the holdings an equal-claim exit carries, minus the exit stigma (pressure case)."""
    from . import hedonic as HD
    from . import negotiation as NG
    pc = active(world)
    fx_free = dataclasses.replace(world.fx, pairing=free(pc))
    sq = NG.forward_values(world, w, last)
    sq_free = _forward(world, w, last, fx_free)
    out = {}
    for r in "AB":
        p = world.personas[r]
        tp = NG.trust_penalty(world.trust[r])
        carry = world.p[r]["money"] + world.carry_out(r, 50)
        o, _ = NG.outside_value(p, r, carry, world.seed, world.hed[r], cx=NG._cx(world, r))
        o -= exit_anticipation(world)
        with HD.use_fixes(fx_free):
            of, _ = NG.outside_value(p, r, carry, world.seed, world.hed[r], cx=NG._cx(world, r))
        s, sf = sq[r] - tp, sq_free[r] - tp
        stay, stay_free = s >= o, sf >= of
        v = "worth" if (stay and stay_free) else "held" if stay else "pushed_out" if stay_free else "leave"
        out[r] = {"sq": round(s, 5), "sq_free": round(sf, 5), "o": round(o, 5), "o_free": round(of, 5), "verdict": v}
    return out
