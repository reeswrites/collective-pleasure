"""Hedonic model: needs, aspirations, two channels, spiral dynamics (docs/decisions/0010-hedonic-model.md).

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state
derived from each persona's assigned preferences. Every number here is ASSUMED unless a comment cites a source;
all tunables live in HedonicConfig (one block). This module imports nothing from the package.

State per agent: need levels in [0,1] (1 = sated); a position B in [-1,1] (the spiral variable); a
non-offsettable load N in [0,1]. Each week: pleasure flow P, offsettable suffering S_off (ordinary hardship,
compensable by pleasure), non-offsettable suffering S_non (a condition held past its onset: being trapped, a need
denied for weeks, being steadily restricted; never netted against pleasure, only removed by removing its cause).

Spiral: B' = clip(B + eta (P - S_off) - eta S_non + feedback(B)); feedback is a_up (B - tip) above the tip and
a_down (B - tip) below it, so distance from the tip is amplified in both directions. Capacity (how well an agent
meets needs, connects and negotiates) rises with B and falls with N. Motivation, not evidence for the numbers:
upward loop, Fredrickson 2001, Am. Psychologist 56(3):218-226 and Fredrickson & Joiner 2002, Psych. Science
13(2):172-175; downward loop, Mani et al. 2013, Science 341:976-980 and poverty-trap models.
"""
from contextlib import contextmanager
from dataclasses import dataclass

NEEDS = ("rest", "connection", "money", "security")
CONDITIONS = ("trapped", "denied", "diminished")


def _clip(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


@dataclass(frozen=True)
class HedonicConfig:
    # spiral (ASSUMED)
    tip: float = 0.0
    start: float = 0.0
    eta: float = 0.30
    a_up: float = 0.05
    a_down: float = 0.08
    cap_beta: float = 0.6
    cap_min: float = 0.5
    cap_max: float = 1.3
    n_cap_penalty: float = 0.5
    # need clocks per week (ASSUMED)
    rest_decay: float = 0.50
    rest_base: float = 0.40
    rest_action: float = 0.30
    work_fatigue: float = 0.10
    conn_decay: float = 0.30
    conn_cohabit: float = 0.10
    conn_friend: float = 0.35
    conn_together: float = 0.30
    conn_friend_initiated: float = 0.15
    money_scale: float = 8.0          # money level = money / money_scale
    living_cost: float = 2.0          # per agent per week
    sec_decay: float = 0.01
    sec_refill: float = 0.03
    sec_assets: float = 25.0          # assets at which security refill is full
    # non-offsettable conditions (ASSUMED)
    denied_below: float = 0.15
    denied_min_salience: float = 0.12  # a need the persona barely cares about is not 'denied' (calibration deviation)
    onset_weeks: int = 4
    trapped_intensity: float = 0.5
    denied_intensity: float = 0.5
    diminished_intensity: float = 0.4
    pre_onset_share: float = 0.5      # share of the intensity felt as ordinary hardship before onset
    n_decay: float = 0.25
    fail_weeks: int = 6               # consecutive weeks of non-offsettable suffering that fails a run
    # pleasure and suffering mix (ASSUMED)
    w_need: float = 0.5
    w_aspiration: float = 0.5
    unmet_aspiration: float = 0.3
    together_event: float = 0.10
    new_connection_event: float = 0.30
    glow_decay: float = 0.5
    # exogenous shocks: misalignment in the WIDER system outside the household (economy and workplace, health system,
    # housing market), not random fate. Rates per person-year (move: per household-year); low and tunable.
    job_loss_rate: float = 0.12       # BLS JOLTS layoffs and discharges, about 1.0-1.1 percent of employment per month
    illness_rate: float = 0.08        # ASSUMED
    new_connection_rate: float = 0.20  # ASSUMED (a good surprise from the wider world)
    move_rate: float = 0.087          # Census CPS 2022 mover rate, 8.7 percent (secondary-source reading)
    # classification (ASSUMED)
    up_margin: float = 0.20
    tail_weeks: int = 8


DEFAULT = HedonicConfig()


# ---- pleasure levers (docs/decisions/0016-pleasure-levers.md; docs/results/pleasure-levers-prereg.md) ----
# Three mechanisms from the author's notes (docs/notes/hedonic-technology-synthesis.md), each behind a flag that defaults OFF.
# With every flag off nothing below is read and runs are bit-identical to earlier results (tests/test_levers_regression.py).
# Every number is ASSUMED and lives in this one block. Source notes are named per group.
STRANDS = ("care", "affection", "intimacy", "logistics", "commitment", "desire")
SHAREABLE = ("care", "affection", "logistics", "intimacy")      # strands that can move to thin bonds first (unbundling love: care first, desire last)


@dataclass(frozen=True)
class LeverConfig:
    # flags
    adapt: bool = False          # L-A: satiety and tolerance on time together and friend contacts
    ritual: bool = False         # L-A: a ritual (scheduled weekly shared slot) can exist; negotiated by a week-0 stub, or imposed by a `must` ritual card
    commit: bool = False         # L-B: commitment friction and compounding payoff
    network: bool = False        # L-C: strands, bonds, coordination cost
    # controlled-experiment switches
    force_policy: str = ""       # "" = each persona's own policy (personas.lever_policy); "repeat" | "rotate" | "adaptive" forces everyone
    force_ritual: bool = False   # a ritual exists regardless of persona acceptance (controlled arm)
    ad_hoc_dose: int = 0         # control arm: this many untagged together sessions are forced each week (equal dose to a ritual)
    force_bonds: int = -1        # external bonds for every agent (-1 = persona policy); network only
    force_thick: int = -1        # thick external bonds (3 strands) per agent (-1 = persona policy)
    bond_shocks: bool = False    # L-C: bonds rupture one at a time
    # L-A adaptation (synthesis M1; notes: Optimal Stimulation and Hedonic Homeostasis, Engineering On-Demand Pleasure Technology)
    n_variants: int = 3
    hab_rate: float = 0.30
    hab_recover: float = 0.15
    tol_rate: float = 0.02
    tol_recover: float = 0.01
    tol_cap: float = 0.4
    switch_cost: float = 0.05
    # L-A anticipation (synthesis M3; notes: Engineering On-Demand Pleasure Technology, Relationships as a Hedonic Technology)
    antic_gain: float = 0.04
    antic_horizon: int = 4
    ritual_period: int = 1
    kept_window: int = 8
    event_boost: float = 0.0     # a prepared event is richer (off in the preregistered runs)
    # L-B commitment as a converter (synthesis M4; note: Commitment Is a Pleasure Technology)
    commit_friction: float = 0.02
    k_rate: float = 0.02
    k_decay: float = 0.004
    k_pay: float = 0.10
    breach_loss: float = 0.5
    # L-C unbundled networks (synthesis M5; note: unbundling love)
    strand_weight: tuple = (0.25, 0.20, 0.20, 0.15, 0.10, 0.10)   # in STRANDS order
    bond_capacity: float = 3.0
    strand_pay: float = 0.20
    care_suffer: float = 0.15
    care_ok: float = 0.3
    q0_start: float = 0.5
    q0_cohab: float = 0.03
    q0_together: float = 0.15
    q0_decay: float = 0.06
    qx_start: float = 0.4
    qx_visit: float = 0.30
    qx_decay: float = 0.05
    coord_a: float = 0.2
    coord_gamma: float = 1.7
    bond_shock_rate: float = 0.20     # per bond-year
    bond_shock_dur: tuple = (6, 20)   # weeks
    partner_rupture_conn: float = 0.15


ACTIVE_LEVERS = None     # module default, set by `use_levers`; WeeklyWorld(levers=None) reads it


@contextmanager
def use_levers(cfg):
    """Make `cfg` the lever config of every WeeklyWorld built inside the block (also the ones negotiation builds)."""
    global ACTIVE_LEVERS
    saved, ACTIVE_LEVERS = ACTIVE_LEVERS, cfg
    try:
        yield cfg
    finally:
        ACTIVE_LEVERS = saved


def levers_on(cfg):
    return cfg is not None and (cfg.adapt or cfg.ritual or cfg.commit or cfg.network or cfg.ad_hoc_dose > 0)


# ---- household fixes (docs/results/household-fixes-design.md; docs/results/v2-retest-prereg-DRAFT.md) ----
# Every flag defaults OFF. With every flag off nothing below is read and runs are bit-identical to earlier results
# (tests/test_levers_regression.py, tests/test_household_fixes.py). Every number is ASSUMED and lives in this one block.
@dataclass(frozen=True)
class FixConfig:
    # fix 1: contact matters (amplification and release; docs/results/horizon.md sections 4 and 5, scaled to weeks)
    contact: bool = False
    contact_motive: bool = False     # behavioral sub-flag: a persona asks for no contact when the partner's friend time crowds out its together time
    # fix 2: money and security count only as each persona values them (author Q9)
    valued_money: bool = False
    # fix 3: real outside options; Nash terms; leaving on the outside option (stay test addition B)
    real_outside: bool = False
    nash_terms: bool = False
    bar_leave: bool = False
    # stay test addition C: the leave menu includes the smallest take the exit term allows
    take_menu_terms: bool = False
    # fix 4: money fines as an opt-in negotiable term
    fines: bool = False
    fine_crowdout: bool = False
    # seed v2.3 support (docs/results/seed-v2.3-readback.md, confirmed 2026-11-11)
    roles: bool = False
    lapse_ladder: bool = False
    unhappy_ladder: bool = False
    trust_words: str | None = None   # None (v2.2 trust) | "actions" | "mostly" | "words"
    decency: bool = False
    # fix 1 parameters
    a_max: float = 0.5
    sociability: float = 0.8
    session_base: float = 0.10       # pleasure scale of one shared session (the hedonic model's together_event)
    c_visit: float = 0.15
    c_decay: float = 0.03
    c_start: float = 0.5
    overlap_C: float = 0.6
    want_half: float = 6.0
    t_cap: float = 1.0
    k_rel: float = 0.05
    t_pain: float = 0.6
    pain_rate: float = 0.05
    motive_p: float = 0.3
    # fix 2 parameters
    k_buy: float = 0.06
    s_half: float = 2.0
    w_ref: float = 1.0
    # fix 3 parameters
    nash_alpha: float = 0.5
    bar_every: int = 13
    leave_margin: float = 0.02
    bar_runs: int = 2
    # fix 4 parameters
    fine_amounts: tuple = (3, 6)
    keep_friction: float = 0.005
    crowd: float = 0.5
    breach_n_paid: float = 0.12
    # v2.3 parameters
    spec_gain: float = 0.25
    spec_ramp: int = 8
    checkin_cost: float = 0.01
    ladder_window: int = 8
    role_kept: float = 0.002
    role_lapse: float = 0.05
    decency_weeks: int = 4
    slid_window: int = 26
    word_gain: float = 0.01
    word_gain_tested: float = 0.05
    word_window: int = 8
    unhappy_window: int = 8
    skip_n: float = 0.4
    # H38 pairing norms (docs/results/h38-pairing-norms-design.md): a mar.pairing.PairingConfig, or None (off, the default)
    pairing: object = None
    # H38 formation check (docs/results/h38-formation-check-prereg.md): the yardstick and window agents decide to form and stay on.
    # "net" with 0 weeks is the old rule (net wellbeing = pleasure - suffering over 26-week rollouts), bit for bit. "pleasure" scores
    # each member's own clipped weekly pleasure (the verdict's measure, from that member's point of view); decide_weeks > 0 replaces the
    # 26-week windows of the formation, retry, reading and outside-option rollouts.
    decide_on: str = "net"
    decide_weeks: int = 0
    # Agent recalibration and bills (docs/results/agent-recalibration-prereg.md). Defaults are the old behaviour, bit for bit
    # (tests/test_agent_values.py). Read only in worlds where the fixes are on; not part of fixes_on.
    agent_values: str = "v1"         # "v1": PersonaAgent.utilities as before; "v2": the change to this week's close (mar.agent_values);
                                     # "v2b": v2 plus the bill horizon (a shared-bill payment credited by the settlement it feeds)
    bills_hurt: bool = False         # an unfunded bill costs a late fee, security (the lost buffer) and stress as the pot runs dry
    late_fee: float = 0.05           # share of the unfunded bill added when the pot pays it (ASSUMED)
    bill_stress: float = 0.30        # friction per member at settlement x unfunded share x dryness (ASSUMED)
    bill_runway: float = 30.0        # pot at which dryness is 0: three months of the couple's bill (ASSUMED)
    evict_stress: float = 0.30       # friction per member when even the pot cannot pay (ASSUMED); the rest carries one month
    # The pleasure scale (docs/decisions/0019-saturating-pleasure-scale.md). "clip" is the old weekly cap, bit for bit
    # (tests/test_pleasure_scale.py). "sat" replaces the clip in Hedonic.close_week with the saturating curve `saturate` (knee sat_knee),
    # so the spiral, the agents' own week and the evaluator all read it. Read only in worlds where the fixes are on; not part of fixes_on.
    pleasure_scale: str = "clip"
    sat_knee: float = 0.8            # ASSUMED (ADR 0019)
    # The hybrid agent (agent_values="hybrid"; mar.hybrid; docs/results/hybrid-agent-prereg.md)
    hybrid_k: int = 4                # sampled futures per option of a big choice
    hybrid_gap: int = 4              # weeks between an early (distress) reading and the last reading
    # Time together valued at the world's satiety (docs/results/hybrid-agent-prereg.md, Amendment 2). "persona" is the old rule, bit for bit
    # (tests/data/satiety_off_fingerprints.json): only an 'adaptive' persona expects satiety (ADR 0016, a persona trait). "world": every
    # v2, v2b and hybrid agent values one more session at the scale the world would give it (World._together_next). v1 does not read it.
    satiety_expect: str = "persona"


ACTIVE_FIXES = None      # module default, set by `use_fixes`; WeeklyWorld(fixes=None) reads it


@contextmanager
def use_fixes(cfg):
    """Make `cfg` the fix config of every WeeklyWorld built inside the block (also the ones negotiation builds)."""
    global ACTIVE_FIXES
    saved, ACTIVE_FIXES = ACTIVE_FIXES, cfg
    try:
        yield cfg
    finally:
        ACTIVE_FIXES = saved


_FIX_FLAGS = ("contact", "contact_motive", "valued_money", "real_outside", "nash_terms", "bar_leave", "take_menu_terms", "fines",
              "fine_crowdout", "roles", "lapse_ladder", "unhappy_ladder", "decency")


def fixes_on(cfg):
    return cfg is not None and (any(getattr(cfg, f) for f in _FIX_FLAGS) or cfg.trust_words is not None or cfg.pairing is not None
                                or cfg.decide_on != "net" or cfg.decide_weeks)


def active_fixes():
    """The open fix config if any flag is on, else None."""
    return ACTIVE_FIXES if fixes_on(ACTIVE_FIXES) else None


def fix_key(cfg=None):
    """A hashable signature of the active levers and fixes, for caches keyed across configs (None when both are off)."""
    f = cfg if cfg is not None else active_fixes()
    lv = ACTIVE_LEVERS if levers_on(ACTIVE_LEVERS) else None
    return None if (f is None and lv is None) else (repr(f), repr(lv))


def saturate(x, k):
    """ADR 0019: the saturating pleasure scale. 0 at or below 0; x up to the knee k; above it k + (1 - k)(1 - exp(-(x - k)/(1 - k))),
    continuous with slope 1 at the knee and rising ever more slowly toward 1."""
    import math
    if x <= k:
        return 0.0 if x < 0.0 else x
    return k + (1.0 - k) * (1.0 - math.exp(-(x - k) / (1.0 - k)))


def pleasure_of(raw, knee):
    """The week's pleasure from its raw sum: the old clip to [0, 1] when knee is None, else the saturating curve."""
    return _clip(raw) if knee is None else saturate(raw, knee)


def bought_pleasure(fx, spend):
    """Fix 2: pleasure bought by spending this week, with diminishing returns."""
    import math
    return fx.k_buy * (1.0 - math.exp(-max(0.0, spend) / fx.s_half))


class Satiety:
    """Satiety h per variant (fast) and tolerance t (slow) for one repeatable pleasure source (synthesis M1).
    The scale on a session is (1 - h[variant]) x (1 - tol_cap x t), times (1 - switch_cost) if the variant differs from the last used."""

    def __init__(self, cfg, n_variants=1):
        self.cfg, self.h, self.t, self.last = cfg, [0.0] * max(1, n_variants), 0.0, None

    def scale(self, k=0):
        return (1.0 - self.h[k]) * (1.0 - self.cfg.tol_cap * self.t)

    def best(self):
        """-> variant with the highest scale (the least satiated)."""
        return min(range(len(self.h)), key=lambda k: (self.h[k], k))

    def use(self, k=0):
        c = self.cfg
        s = self.scale(k) * (1.0 - (c.switch_cost if self.last is not None and self.last != k else 0.0))
        self.h[k] += c.hab_rate * (1.0 - self.h[k])
        self.t += c.tol_rate * (1.0 - self.t)
        self.last = k
        return s

    def week_end(self):
        c = self.cfg
        self.h = [x * (1.0 - c.hab_recover) for x in self.h]
        self.t *= 1.0 - c.tol_recover


def strand_sets(n_ext, n_thick=0):
    """Strands held by each external bond: thick bonds 3, thin bonds 2, cycling through SHAREABLE (care first)."""
    out, i = [], 0
    for j in range(n_ext):
        m = 3 if j < n_thick else 2
        out.append(tuple(SHAREABLE[(i + t) % len(SHAREABLE)] for t in range(m)))
        i += m
    return out


def strand_cover(cfg, q0, qx, sets):
    """-> {strand: cover in [0,1]}. The partner (thick core) holds all strands; supply of a bond to a strand is its quality times
    min(1, capacity / strands held); cover is 1 - product of (1 - supply) over the bonds that hold the strand."""
    cover = {}
    sup0 = q0 * min(1.0, cfg.bond_capacity / len(STRANDS))
    for s in STRANDS:
        miss = 1.0 - sup0
        for q, S in zip(qx, sets):
            if s in S:
                miss *= 1.0 - q * min(1.0, cfg.bond_capacity / len(S))
        cover[s] = 1.0 - miss
    return cover


def strand_terms(cfg, cover):
    """-> (pleasure, suffering) from the strand cover."""
    pay = cfg.strand_pay * sum(w * cover[s] for w, s in zip(cfg.strand_weight, STRANDS))
    suf = cfg.care_suffer * max(0.0, cfg.care_ok - cover["care"]) / cfg.care_ok
    return pay, suf


def coordination_units(cfg, n_ext):
    """Units per week a partner spends keeping n_ext external bonds going (convex: synthesis M5, 'unbundled lives cost coordination')."""
    return cfg.coord_a * n_ext ** cfg.coord_gamma if n_ext > 0 else 0.0


def capacity(B, N, cfg=DEFAULT):
    return _clip(1 + cfg.cap_beta * (B - cfg.tip), cfg.cap_min, cfg.cap_max) * (1 - cfg.n_cap_penalty * N)


def feedback(B, cfg=DEFAULT):
    return (cfg.a_up if B >= cfg.tip else cfg.a_down) * (B - cfg.tip)


PARTS = False            # observer layer (src/mar/observe.py): when True, every Hedonic built records the additive parts of each week's
#                          close (pleasure, offsettable and non-offsettable suffering by source) in `parts_acc`. Read-only: the arithmetic
#                          that sets pleasure, B and N is unchanged, and nothing the model reads depends on it. Off by default.


@contextmanager
def recording_parts(on=True):
    """Every Hedonic built inside the block records its weekly parts (observer layer)."""
    global PARTS
    saved, PARTS = PARTS, on
    try:
        yield
    finally:
        PARTS = saved


class Hedonic:
    """One agent's hedonic state. `persona` needs .needs (salience per need) and .aspirations (targets) and
    .weights (aspiration importances: security, autonomy, togetherness, money, other_connections)."""

    knee = None          # ADR 0019: None = the old clip; a number = the saturating curve's knee (set by WeeklyWorld when the flag is on)

    ASP_WEIGHT = {"security_buffer": "security", "together_per_week": "togetherness",
                  "friends_per_week": "other_connections", "savings_per_week": "money", "autonomy": "autonomy"}

    def __init__(self, persona, cfg=DEFAULT):
        self.cfg = cfg
        sal = {n: max(0.0, float(persona.needs[n])) for n in NEEDS}
        z = sum(sal.values()) or 1.0
        self.sal = {n: v / z for n, v in sal.items()}
        self.targets = dict(persona.aspirations)
        w = {k: max(0.0, float(persona.weights[self.ASP_WEIGHT[k]])) for k in self.targets}
        zw = sum(w.values()) or 1.0
        self.asp_w = {k: v / zw for k, v in w.items()}
        self.level = {"rest": 0.7, "connection": 0.6, "money": 0.6, "security": 0.6}
        self.B, self.N, self.glow = cfg.start, 0.0, 0.0
        self.run = {c: 0 for c in CONDITIONS}      # consecutive weeks each condition has held
        self.nonoff_run = 0                         # consecutive weeks with S_non > 0
        self.max_nonoff_run = 0
        self.parts_on, self.parts_acc, self.xparts = PARTS, [], None     # observer layer only; never read by the model

    def __deepcopy__(self, memo):
        """The default deep copy, except that a copy starts with no recorded parts (observer layer: a rollout's parts are its own)."""
        import copy
        c = self.__class__.__new__(self.__class__)
        memo[id(self)] = c
        for k, v in self.__dict__.items():
            setattr(c, k, [] if k == "parts_acc" else copy.deepcopy(v, memo))
        return c

    @property
    def capacity(self):
        return capacity(self.B, self.N, self.cfg)

    # -- need clocks
    def tick(self, *, rest_actions=0, work_blocks=0, friend_visits=0, together=0, friend_initiated=0, cohabiting=True,
             assets=0.0, money=0.0, extra_rest_drain=0.0, extra_security_drain=0.0, connection_penalty=0.0):
        """Advance the need clocks one week. Gains are scaled by capacity (a drained agent gets less from the same act)."""
        c, cap = self.cfg, self.capacity
        L = self.level
        L["rest"] = _clip(L["rest"] + c.rest_base + c.rest_action * cap * rest_actions - c.rest_decay
                          - c.work_fatigue * work_blocks - extra_rest_drain)
        L["connection"] = _clip(L["connection"] + (c.conn_cohabit if cohabiting else 0.0) - c.conn_decay - connection_penalty
                                + cap * (c.conn_friend * friend_visits + c.conn_together * together
                                         + c.conn_friend_initiated * friend_initiated))
        L["money"] = _clip(money / c.money_scale)
        L["security"] = _clip(L["security"] - c.sec_decay - extra_security_drain
                              + c.sec_refill * _clip(assets / c.sec_assets))

    def satisfaction(self, key, value):
        t = self.targets[key]
        return 1.0 if t <= 0 else _clip(value / t)

    def event_new_connection(self):
        self.glow += self.cfg.new_connection_event

    def _parts(self, sat, together_sessions, glow_used, extra_pleasure, friction, active, raw, pleasure, s_off_raw, s_off, s_non_raw,
               s_non):
        """The additive parts of this week's close (observer layer). Computed beside close_week's own arithmetic, never in place of it:
        pleasure = sum(p) + clip_p; s_off = sum(s_off parts) + clip_off; s_non = sum(s_non parts) + clip_non."""
        c, L = self.cfg, self.level
        vm = getattr(self, "valued", None)
        if vm is None:
            pn = {n: c.w_need * self.sal[n] * _clip((L[n] - 0.5) / 0.5) for n in NEEDS}
        else:
            fx, _money, _w_m, w_s = vm
            v_s = min(1.0, w_s / fx.w_ref)
            lost = self.sal["security"] * (1.0 - v_s)
            rc = self.sal["rest"] + self.sal["connection"]
            up = 1.0 + (lost / rc if rc > 0 else 0.0)
            pn = {"rest": c.w_need * self.sal["rest"] * up * _clip((L["rest"] - 0.5) / 0.5),
                  "connection": c.w_need * self.sal["connection"] * up * _clip((L["connection"] - 0.5) / 0.5),
                  "money": c.w_need * self.sal["money"] * _clip((L["money"] - 0.5) / 0.5),
                  "security": c.w_need * self.sal["security"] * v_s * _clip((L["security"] - 0.5) / 0.5)}
        sn = {n: self.sal[n] * _clip((0.5 - L[n]) / 0.5) for n in NEEDS}
        pa = {k: c.w_aspiration * self.asp_w[k] * sat[k] for k in sat}
        sa = {k: c.unmet_aspiration * self.asp_w[k] * (1 - sat[k]) for k in sat}
        pre = {k: (c.pre_onset_share * inten if on and self.run[k] < c.onset_weeks else 0.0) for k, (on, inten) in active.items()}
        non = {k: (inten if on and self.run[k] >= c.onset_weeks else 0.0) for k, (on, inten) in active.items()}
        return {"p_need": pn, "p_asp": pa, "together_event": c.together_event * together_sessions, "glow": glow_used,
                "extra": extra_pleasure, "x": self.xparts, "clip_p": pleasure - raw,
                "s_need": sn, "s_asp": sa, "friction": friction, "pre_onset": pre, "clip_off": s_off - s_off_raw,
                "s_non": non, "clip_non": s_non - s_non_raw, "pleasure": pleasure, "s_off": s_off, "s_non_total": s_non}

    # -- close the week
    def close_week(self, aspiration_values, *, trapped=False, restricted=False, together_sessions=0, friction=0.0,
                   extra_pleasure=0.0, report_raw=False):
        """aspiration_values: {key: value achieved} (same units as the targets). extra_pleasure: lever terms (anticipation,
        commitment payoff, strand cover), 0 when no lever is on. -> row dict."""
        c = self.cfg
        L = self.level
        vm = getattr(self, "valued", None)      # fix 2 (valued_money): (fix config, money held, money weight, security weight)
        if vm is None:
            p_need = sum(self.sal[n] * _clip((L[n] - 0.5) / 0.5) for n in NEEDS)
        else:
            fx, money, w_m, w_s = vm
            # Money: the need level saturates at 4 weeks of living costs, so it is a subsistence (means) term and counts for everyone;
            # money valued for its own sake beyond that already enters through the savings aspiration, weighted by the money weight.
            # Security: counts only as far as the persona values it (security weight); the share it does not value moves to rest and
            # connection, so the hedonic scale stays comparable (implementation choice, docs/results/v2-retest-prereg.md Amendment 1).
            v_s = min(1.0, w_s / fx.w_ref)
            lost = self.sal["security"] * (1.0 - v_s)
            rc = self.sal["rest"] + self.sal["connection"]
            up = 1.0 + (lost / rc if rc > 0 else 0.0)
            p_need = (sum(self.sal[n] * up * _clip((L[n] - 0.5) / 0.5) for n in ("rest", "connection"))
                      + self.sal["money"] * _clip((L["money"] - 0.5) / 0.5)
                      + self.sal["security"] * v_s * _clip((L["security"] - 0.5) / 0.5))
        s_need = sum(self.sal[n] * _clip((0.5 - L[n]) / 0.5) for n in NEEDS)
        sat = {k: self.satisfaction(k, aspiration_values.get(k, 0.0)) for k in self.targets}
        p_asp = sum(self.asp_w[k] * sat[k] for k in sat)
        s_asp = c.unmet_aspiration * sum(self.asp_w[k] * (1 - sat[k]) for k in sat)
        self.last_autonomy = aspiration_values.get("autonomy", 0.0)      # read only by agent values v2 (a record; the model never reads it)
        raw = c.w_need * p_need + c.w_aspiration * p_asp + c.together_event * together_sessions + self.glow + extra_pleasure
        pleasure = _clip(raw) if self.knee is None else saturate(raw, self.knee)
        glow_used = self.glow
        self.glow *= c.glow_decay
        s_off = s_need + s_asp + friction
        active = {"trapped": (trapped, c.trapped_intensity),
                  "denied": (any(L[n] < c.denied_below and self.sal[n] >= c.denied_min_salience for n in NEEDS), c.denied_intensity),
                  "diminished": (restricted, c.diminished_intensity)}
        s_non = 0.0
        for name, (on, inten) in active.items():
            self.run[name] = self.run[name] + 1 if on else 0
            if on:
                if self.run[name] >= c.onset_weeks:
                    s_non += inten
                else:
                    s_off += c.pre_onset_share * inten
        s_non_raw, s_off_raw = s_non, s_off
        s_non, s_off = _clip(s_non), _clip(s_off)
        if self.parts_on:
            self.parts_acc.append(self._parts(sat, together_sessions, glow_used, extra_pleasure, friction, active, raw, pleasure,
                                              s_off_raw, s_off, s_non_raw, s_non))
        if s_non > 0:
            self.N = _clip(self.N + 0.5 * s_non)
            self.nonoff_run += 1
        else:
            self.N = max(0.0, self.N - c.n_decay)
            self.nonoff_run = 0
        self.max_nonoff_run = max(self.max_nonoff_run, self.nonoff_run)
        self.B = _clip(self.B + c.eta * (pleasure - s_off) - c.eta * s_non + feedback(self.B, c), -1.0, 1.0)
        return {"pleasure": round(pleasure, 4), "s_off": round(s_off, 4), "s_non": round(s_non, 4), "B": round(self.B, 4),
                "N": round(self.N, 4), "capacity": round(self.capacity, 4), "tip": c.tip,
                "nonoff_run": self.nonoff_run, "levels": {n: round(L[n], 3) for n in NEEDS},
                "conditions": {k: v for k, (v, _) in active.items()}, **({"p_raw": round(raw, 4)} if report_raw else {}),
                **({"p_clip": round(_clip(raw), 4)} if self.knee is not None else {})}
