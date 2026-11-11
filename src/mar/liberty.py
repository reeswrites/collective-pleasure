"""Liberty: equal liberty plus a non-domination penalty (docs/results/liberty-prereg.md; all choices ASSUMED there).

liberty(world, spec, state, agent, k, policy) -> {"reachable", "bits", "c", "bits_c", "d", "bits_d", "liberty", "open", ...}
  c  = compatible futures: keys i reaches within k steps along paths where every move passes the harm test (no other
       member j ends with fewer reachable futures than under i's restraint action `noop`).
  d  = domination exposure: the most compatible futures any single other member could remove by one action at will
       (first step), capability not exercise. A wall (the gate making that action ineffective) removes the power.
  liberty = bits_c - w * bits_d, bits_d = log2(1 + d), w = 1 ASSUMED.

Adapter: empowerment's four methods, plus `noop(state, agent)` and `force_policy(policy, j, action)` (fishery and VPGG
are handled here; a household adapter must supply both). The policy must be defined for every agent index.
"""
from collections import namedtuple
from math import log2

from . import empowerment as E
from .games import vpgg as V

W_DEFAULT = 1.0
K_DEFAULT = 2

# ---- v2: classification of members' actions (docs/results/liberty-v2-prereg.md; ASSUMED where judgment is involved) ----
INTERFERENCE = "interference"  # acts on another member's own options: veto, block, take from the shared stock, force
WITHDRAWAL = "withdrawal"      # the member exercising their own options to decline cooperation: leave, abstain, rest
OWN = "own"                    # the member using their own options (contribute, work, the contested option)

TOY_CLASS = {
    (0, "x"): (OWN, "A's own contested option"),
    (0, "work"): (OWN, "A's own work"),
    (0, "rest"): (WITHDRAWAL, "restraint, A declines to act"),
    (1, "pass"): (WITHDRAWAL, "restraint, B declines to act"),
    (1, "work"): (OWN, "B's own work"),
    (1, "veto"): (INTERFERENCE, "blocks A's option: acts on A"),
}
VPGG_CLASS = {
    "contribute": (OWN, "puts in own resources"),
    "join": (WITHDRAWAL, "joins but declines to supply own resources"),
    "abstain": (WITHDRAWAL, "leaves the pool, withdraws own participation"),
}
PARTNER_CLASS = {
    (0, "joint"): (OWN, "A's option, but it needs B's participation (agreement-dependent)"),
    (0, "solo"): (OWN, "A's own option"),
    (0, "rest"): (WITHDRAWAL, "restraint"),
    (1, "pass"): (WITHDRAWAL, "restraint, B stays and participates as scripted"),
    (1, "veto"): (INTERFERENCE, "blocks A's solo option"),
    (1, "leave"): (WITHDRAWAL, "B leaves: withdraws own participation"),
    (1, "abstain"): (WITHDRAWAL, "B sits this step out: withdraws own participation"),
}


def classify(world, state, agent, action):
    """INTERFERENCE | WITHDRAWAL | OWN for `agent` playing `action`. world.classify wins; else the tables above."""
    if hasattr(world, "classify"):
        return world.classify(state, agent, action)
    if isinstance(world, E.FisheryWorld):
        return WITHDRAWAL if action == 0 else INTERFERENCE  # catch > 0 draws on a stock others' futures depend on
    if isinstance(world, E.VPGGWorld):
        return VPGG_CLASS[action][0]
    raise TypeError(f"{type(world).__name__} needs classify (the per-action table, with a rationale each)")


def force_policy(world, policy, j, action):
    """The same scripted policy except member j plays `action` (the same call path as j's script)."""
    if hasattr(world, "force_policy"):
        return world.force_policy(policy, j, action)
    if isinstance(world, E.FisheryWorld):
        return lambda obs, a: action if a == j else policy(obs, a)
    if isinstance(world, E.VPGGWorld):
        letter = {v: k for k, v in V.INTENT.items()}[action]
        return lambda s, a: letter if a == j else policy(s, a)
    raise TypeError(f"{type(world).__name__} needs force_policy")


def noop_action(world, state, agent):
    """Restraint action: world.noop if given; fishery catch 0; VPGG abstain (a request; the gate may make it join)."""
    if hasattr(world, "noop"):
        return world.noop(state, agent)
    if isinstance(world, E.FisheryWorld):
        return 0
    if isinstance(world, E.VPGGWorld):
        return "abstain"
    raise TypeError(f"{type(world).__name__} needs noop")


class _Ctx:
    """One measurement: caches member reach counts, tracks cap hits."""

    def __init__(self, world, spec, k, policy, cap, version=1):
        self.world, self.spec, self.k, self.policy, self.cap, self.version = world, spec, k, policy, cap, version
        self.open = False
        self._n = {}

    def n(self, s, j):
        """|F_j(s)|: plain reachable futures of member j from s, everyone else on script."""
        key = (s, j)
        if key not in self._n:
            r = E.empowerment(self.world, self.spec, s, j, self.k, self.policy, self.cap)
            self.open |= r["bound_hit"]
            self._n[key] = r["reachable"]
        return self._n[key]

    def compatible(self, s, i, a, pol):
        w = self.world
        if self.version == 2 and classify(w, s, i, a) != INTERFERENCE:
            return True  # leaving, abstaining or using one's own options harms no one (no claim on i's cooperation)
        s_a = w.step(s, self.spec, i, a, pol)
        s_0 = w.step(s, self.spec, i, noop_action(w, s, i), pol)
        return all(self.n(s_a, j) >= self.n(s_0, j) for j in range(w.n_agents) if j != i)

    def reach(self, s, i, first=None, compat=True):
        """Keys i reaches within k steps; compat prunes incompatible moves. `first` = policy for step 1 only."""
        w = self.world
        layer, keys, expanded = {s}, {w.key(s, i)}, 0
        for t in range(self.k):
            pol = first if (t == 0 and first is not None) else self.policy
            nxt = set()
            for st in layer:
                if w.is_terminal(st):
                    nxt.add(st)
                    continue
                for a in w.actions(st, i):
                    if expanded >= self.cap:
                        self.open = True
                        break
                    expanded += 1
                    if compat and not self.compatible(st, i, a, pol):
                        continue
                    nxt.add(w.step(st, self.spec, i, a, pol))
                if self.open and expanded >= self.cap:
                    break
            keys.update(w.key(st, i) for st in nxt)
            layer = nxt
        return keys


def liberty(world, spec, state, agent, k, policy, w=W_DEFAULT, cap=E.CAP_DEFAULT, version=2):
    """version 1: the original (all of j's actions count toward D). version 2: only INTERFERENCE counts toward D and the
    harm test; options lost when a member WITHDRAWS (ado) are excluded from the option set and reported."""
    if version == 1:
        return _liberty_v1(world, spec, state, agent, k, policy, w, cap)
    ctx = _Ctx(world, spec, k, policy, cap, version=2)
    plain = E.empowerment(world, spec, state, agent, k, policy, cap)
    ctx.open |= plain["bound_hit"]
    c_all = len(ctx.reach(state, agent))
    ado, d, by, ado_by = 0, 0, None, None
    for j in range(world.n_agents):
        if j == agent:
            continue
        base = len(ctx.reach(state, agent, force_policy(world, policy, j, noop_action(world, state, j))))
        for b in world.actions(state, j):
            kind = classify(world, state, j, b)
            if kind == OWN:
                continue
            red = len(ctx.reach(state, agent, force_policy(world, policy, j, b)))
            if kind == WITHDRAWAL and c_all - red > ado:
                ado, ado_by = c_all - red, (j, b)
            elif kind == INTERFERENCE and base - red > d:
                d, by = base - red, (j, b)
    ado = min(ado, c_all - 1)
    c = c_all - ado
    d = min(d, c - 1)
    bits_c, bits_d = log2(c), log2(1 + d)
    return {"reachable": plain["reachable"], "bits": plain["bits"], "c": c, "c_all": c_all, "ado": ado, "ado_by": ado_by,
            "bits_c": bits_c, "d": d, "bits_d": bits_d, "liberty": bits_c - w * bits_d, "blocker": by,
            "open": ctx.open, "k": k, "w": w, "version": 2}


def _liberty_v1(world, spec, state, agent, k, policy, w=W_DEFAULT, cap=E.CAP_DEFAULT):
    ctx = _Ctx(world, spec, k, policy, cap)
    plain = E.empowerment(world, spec, state, agent, k, policy, cap)
    ctx.open |= plain["bound_hit"]
    c = len(ctx.reach(state, agent))
    d, by = 0, None
    for j in range(world.n_agents):
        if j == agent:
            continue
        base = len(ctx.reach(state, agent, force_policy(world, policy, j, noop_action(world, state, j))))
        for b in world.actions(state, j):
            red = base - len(ctx.reach(state, agent, force_policy(world, policy, j, b)))
            if red > d:
                d, by = red, (j, b)
    d = min(d, c - 1)
    bits_c, bits_d = log2(c), log2(1 + d)
    return {"reachable": plain["reachable"], "bits": plain["bits"], "c": c, "bits_c": bits_c, "d": d, "bits_d": bits_d,
            "liberty": bits_c - w * bits_d, "blocker": by, "open": ctx.open, "k": k, "w": w, "version": 1}


def liberty_all(world, spec, state, policy, k=K_DEFAULT, w=W_DEFAULT, cap=E.CAP_DEFAULT, version=2):
    return [liberty(world, spec, state, i, k, policy, w, cap, version) for i in range(world.n_agents)]


# ---- toy two-partner veto world (the kind-master case) ----

TState = namedtuple("TState", "t nx aw bw vetoed")
TSpec = namedtuple("TSpec", "veto_right")


class ToyVetoWorld:
    """Partner A (0) has a contested option `x`; partner B (1) may `veto` it if spec.veto_right (persistent). Each step B
    acts first, then A. Keys: A (x done, work done); B (work done, veto placed). Scripts are policy(state, i) -> action."""
    n_agents = 2
    MENU = {0: ("x", "work", "rest"), 1: ("pass", "work", "veto")}
    HORIZON = 3

    def initial(self):
        return TState(0, 0, 0, 0, False)

    def is_terminal(self, s):
        return s.t >= self.HORIZON

    def actions(self, s, agent):
        return self.MENU[agent]

    def key(self, s, agent):
        return (s.nx, s.aw) if agent == 0 else (s.bw, s.vetoed)

    def noop(self, s, agent):
        return "rest" if agent == 0 else "pass"

    def force_policy(self, policy, j, action):
        return lambda s, a: action if a == j else policy(s, a)

    def classify(self, s, agent, action):
        return TOY_CLASS[(agent, action)][0]

    def step(self, s, spec, agent, action, policy):
        if self.is_terminal(s):
            return s
        act = {i: (action if i == agent else policy(s, i)) for i in (0, 1)}
        bw, vetoed, nx, aw = s.bw, s.vetoed, s.nx, s.aw
        if act[1] == "work":
            bw += 1
        elif act[1] == "veto" and spec.veto_right:
            vetoed = True
        if act[0] == "x" and not vetoed:
            nx += 1
        elif act[0] == "work":
            aw += 1
        return TState(s.t + 1, nx, aw, bw, vetoed)


def kind_master(s, i):
    """Script: A rests, B passes (the veto is held and never used)."""
    return "rest" if i == 0 else "pass"


def exercising_master(s, i):
    """Script: A rests, B vetoes at every step."""
    return "rest" if i == 0 else "veto"


# ---- v2 hand world: partner who can veto, leave or abstain; A's `joint` option needs B's participation ----

PState = namedtuple("PState", "t nj ns present vetoed")


class PartnerWorld:
    """A (0): joint (counts only if B is present and participating THIS step: agreement-dependent), solo (counts unless
    vetoed), rest. B (1): pass (participates), veto (needs spec.veto_right; blocks A's solo from then on), leave
    (permanently absent), abstain (absent this step). B acts first. Keys: A (nj, ns); B (present, vetoed)."""
    n_agents = 2
    MENU = {0: ("joint", "solo", "rest"), 1: ("pass", "veto", "leave", "abstain")}
    HORIZON = 3

    def initial(self):
        return PState(0, 0, 0, True, False)

    def is_terminal(self, s):
        return s.t >= self.HORIZON

    def actions(self, s, agent):
        return self.MENU[agent]

    def key(self, s, agent):
        return (s.nj, s.ns) if agent == 0 else (s.present, s.vetoed)

    def noop(self, s, agent):
        return "rest" if agent == 0 else "pass"

    def force_policy(self, policy, j, action):
        return lambda s, a: action if a == j else policy(s, a)

    def classify(self, s, agent, action):
        return PARTNER_CLASS[(agent, action)][0]

    def step(self, s, spec, agent, action, policy):
        if self.is_terminal(s):
            return s
        act = {i: (action if i == agent else policy(s, i)) for i in (0, 1)}
        present, vetoed, nj, ns = s.present, s.vetoed, s.nj, s.ns
        here = present
        if act[1] == "leave":
            present = here = False
        elif act[1] == "abstain":
            here = False
        elif act[1] == "veto" and spec.veto_right:
            vetoed = True
        if act[0] == "joint" and here:
            nj += 1
        elif act[0] == "solo" and not vetoed:
            ns += 1
        return PState(s.t + 1, nj, ns, present, vetoed)


def partner_stays(s, i):
    """Script: A rests, B passes (stays, participates, never vetoes)."""
    return "rest" if i == 0 else "pass"


# ---- household (slice 1 of the household evolution run; docs/results/household-liberty.md) ----
# The adapter lives on empowerment.HouseholdWorld (noop, force_policy, classify; table E.HH_CLASS). Everything here is
# a measurement, never a rule.

HH_K = 2                       # the household liberty horizon in passes (k = 3 is the plain-empowerment horizon; ASSUMED cheaper here)
HH_SNAPSHOTS = (0, 52)         # weeks at which liberty is measured in a run (ASSUMED)
_HH_MEMO = {}                  # id(gate) -> (gate, {measurement key: result}); a pure cache, values are identical to a fresh call


def household_liberty(world, gate, state, scripts, k=HH_K, w=W_DEFAULT, cap=E.HH_CAP, version=2):
    """Both partners' liberty at `state` against the scripted others. -> list of two liberty() dicts."""
    pol = E.scripted_policy(scripts)
    return liberty_all(world, gate, state, pol, k, w, cap, version)


def household_run_liberty(cards, personas, seed=0, weeks=E.HH.WEEKS, snapshots=HH_SNAPSHOTS, k=HH_K, w=W_DEFAULT,
                          cap=E.HH_CAP, cfg=None, press=True, version=2, plain_k=None):
    """Run one weekly household world and measure liberty (and plain empowerment) of both partners at the start of the
    snapshot weeks. -> {"run", "snaps": [{"week", "liberty": [l0, l1], "bits": [b0, b1], "c": [..], "ado": [..], "d": [..], "open"}],
    "liberty_min": mean over snapshots of the lower of the two partners' liberty, "bits_min": same for plain empowerment}.
    Open snapshots (cap hit) are kept in `snaps` with open=True and left out of the means. plain_k: horizon for the plain
    empowerment column (default = k, so the two columns are comparable)."""
    from .hedonic import DEFAULT
    gate = cards if isinstance(cards, E.HH.PyGate) else E.HH.PyGate(cards)
    wk = E.HH.WeeklyWorld(gate, personas, seed, weeks, cfg or DEFAULT)
    scripts = tuple(E.script_for(p) if press else "cooperator" for p in personas)
    hw = E.HouseholdWorld(tuple(E.consent_for(p) for p in personas))
    snaps = []

    memo = _HH_MEMO.setdefault(id(gate), (gate, {}))[1]      # same state, scripts, consents, k: same answer (the gate is kept alive here)

    def hook(world, wk_):
        if wk_ in snapshots and wk_ < weeks:
            state = hw.snapshot(world, wk_)
            mk = (state, scripts, hw.consents, k, w, cap, version)
            if mk not in memo:
                memo[mk] = household_liberty(hw, gate, state, scripts, k, w, cap, version)
            res = memo[mk]
            snaps.append({"week": wk_, "liberty": [r["liberty"] for r in res], "bits": [r["bits"] for r in res],
                          "c": [r["c"] for r in res], "ado": [r.get("ado", 0) for r in res], "d": [r["d"] for r in res],
                          "open": any(r["open"] for r in res)})
    wk.hook = hook
    run = wk.play()
    ok = [s for s in snaps if not s["open"]]
    mean = lambda xs: sum(xs) / len(xs) if xs else None
    return {"run": run, "snaps": snaps, "n_open": len(snaps) - len(ok),
            "liberty_min": mean([min(s["liberty"]) for s in ok]), "bits_min": mean([min(s["bits"]) for s in ok]),
            "d_mean": mean([sum(s["d"]) / 2 for s in ok]), "ado_mean": mean([sum(s["ado"]) / 2 for s in ok])}
