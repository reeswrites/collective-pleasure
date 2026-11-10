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
    sec_decay: float = 0.02
    sec_refill: float = 0.03
    sec_assets: float = 60.0          # assets at which security refill is full
    # non-offsettable conditions (ASSUMED)
    denied_below: float = 0.15
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
    # classification (ASSUMED)
    up_margin: float = 0.20
    tail_weeks: int = 8


DEFAULT = HedonicConfig()


def capacity(B, N, cfg=DEFAULT):
    return _clip(1 + cfg.cap_beta * (B - cfg.tip), cfg.cap_min, cfg.cap_max) * (1 - cfg.n_cap_penalty * N)


def feedback(B, cfg=DEFAULT):
    return (cfg.a_up if B >= cfg.tip else cfg.a_down) * (B - cfg.tip)


class Hedonic:
    """One agent's hedonic state. `persona` needs .needs (salience per need) and .aspirations (targets) and
    .weights (aspiration importances: security, autonomy, togetherness, money, other_connections)."""

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

    # -- close the week
    def close_week(self, aspiration_values, *, trapped=False, restricted=False, together_sessions=0, friction=0.0):
        """aspiration_values: {key: value achieved} (same units as the targets). -> row dict."""
        c = self.cfg
        L = self.level
        p_need = sum(self.sal[n] * _clip((L[n] - 0.5) / 0.5) for n in NEEDS)
        s_need = sum(self.sal[n] * _clip((0.5 - L[n]) / 0.5) for n in NEEDS)
        sat = {k: self.satisfaction(k, aspiration_values.get(k, 0.0)) for k in self.targets}
        p_asp = sum(self.asp_w[k] * sat[k] for k in sat)
        s_asp = c.unmet_aspiration * sum(self.asp_w[k] * (1 - sat[k]) for k in sat)
        pleasure = _clip(c.w_need * p_need + c.w_aspiration * p_asp + c.together_event * together_sessions + self.glow)
        self.glow *= c.glow_decay
        s_off = s_need + s_asp + friction
        active = {"trapped": (trapped, c.trapped_intensity),
                  "denied": (any(L[n] < c.denied_below for n in NEEDS), c.denied_intensity),
                  "diminished": (restricted, c.diminished_intensity)}
        s_non = 0.0
        for name, (on, inten) in active.items():
            self.run[name] = self.run[name] + 1 if on else 0
            if on:
                if self.run[name] >= c.onset_weeks:
                    s_non += inten
                else:
                    s_off += c.pre_onset_share * inten
        s_non, s_off = _clip(s_non), _clip(s_off)
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
                "conditions": {k: v for k, (v, _) in active.items()}}
