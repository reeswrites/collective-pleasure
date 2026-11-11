"""Observer layer for the household world (docs/notes/instrumentation.md is the build list; docs/notes/observer-schema.md is the schema).

OFF by default. A world carries an observer only when one is attached: `Observer(world, cfg)` after building it, or every world built
inside a `use_observer(cfg)` block. With no observer the world runs exactly as before (tests/test_observer.py pins fingerprints of four
experiment families taken before this module existed). With one, the world still runs exactly as before: the observer only reads, makes
no draw from any random stream the world uses, and writes nothing the world reads. The same test runs the families with an observer on
every world (counterfactual replays included) and checks the same fingerprints.

What it records, by the build list's numbering (each row carries `t`, its table):
  decision   D1 D2 D4 D7  every step_agent call: the scored candidates with their utility parts, the status of each, the chosen one,
                          the runner-up and the margin; leave and gift context when they bear on the call
  consent    D3           every consents() call that answered a request: style, autonomy, the style's answer, the coin flip, trust and
                          the trust draw, the final answer, and a commitment that overrode it
  reading    D5           formation, retry, 13-week reading and review decisions: each member's household and outside values, with
                          both split into parts (rollout means)
  negotiation D6          each negotiation round at a review or retry: the offer, each member's value and bar, accept or reject
  state      S1 S2        per member per week: need levels, B, N, capacity, condition streaks, trust, standing requests, and the week's
                          pleasure and suffering split into parts (hedonic.Hedonic._parts) and grouped (GROUPS)
  friend     S3           every friend invitation: met, blocked by a rule, or declined under H38 withdrawal
  trust      S4           every trust move with its cause, "kept" included
  word       S5           every word said (trust_words) and every word taken back
  flow       F1           every money movement: (from, to, amount, cause)
  together   F2           every together session: who started it, and whether the partner was willing
  item       F3           item custody at the start and at every change
  rule       R1           every card, sanction, veto or commitment that blocked, sanctioned or was breached by a candidate; and the
                          cards checked for each executed action (verdict "permit")
  sanction   R2           each sanction's start and end
  commit     R3           each commitment made, renewed, ended or breached
  veto       R4           each veto laid (the actions it stopped are rule rows with src "veto")
  replay     C1 C3        sampled counterfactual replays from a deep copy of the world at the start of the week: the other option at
                          one decision ("swap"), staying instead of a leave ("stay"), and the same week with the pairing pressure off
                          ("pressure_off"); every row carries a stable `pair_key` so paired arms line up (C3)

Wording rule (ADR 0010): agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
import random
from contextlib import contextmanager
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from . import hedonic as HD

SCHEMA = "mar.observer/1"
TABLES = ("run", "week", "decision", "consent", "reading", "negotiation", "state", "friend", "trust", "word", "flow", "together",
          "item", "rule", "sanction", "commit", "veto", "replay", "stay", "end")
GROUPS = ("money", "security", "rest", "connection", "partner", "friends", "items", "pressure", "intrinsic", "autonomy", "levers",
          "friction", "conditions", "other", "clip")
ROLES = ("A", "B")


@dataclass(frozen=True)
class ObsConfig:
    """replay_rate: share of weeks sampled for a swap replay (and, with the pairing switch on, a pressure-off replay); 0 = none.
    replay_window: weeks each replay runs. replay_leaves: every executed leave also gets a "stay" replay. replay_seed: the sampler's
    own seed (the sampler is a separate random.Random keyed by (replay_seed, pair_key, week); it never touches the world's streams).
    max_replays: cap per run. decisions / state / flows: switch tables off to save space."""
    replay_rate: float = 0.0
    replay_window: int = 13
    replay_leaves: bool = True
    replay_pressure: bool = True
    replay_seed: int = 0
    max_replays: int = 60
    decisions: bool = True
    state: bool = True
    flows: bool = True


ACTIVE = None        # the config of an open use_observer block, else None


@contextmanager
def use_observer(cfg=None):
    """Every WeeklyWorld built inside the block carries an Observer (rollout worlds too), and every Hedonic records its parts."""
    global ACTIVE
    saved, ACTIVE = ACTIVE, (cfg or ObsConfig())
    try:
        with HD.recording_parts(True):
            yield ACTIVE
    finally:
        ACTIVE = saved


def collecting():
    """For explicit attach: build the harness inside this block so week-0 rollouts record their parts too."""
    return HD.recording_parts(True)


# ---- parts -------------------------------------------------------------------------------------------------------------------

def _r(x, n=6):
    return round(float(x), n)


def groups(p, measure="net"):
    """One week's Hedonic parts -> {group: contribution}. With measure "net" the groups sum to pleasure - s_off - s_non (the persona
    evaluation negotiation.wellbeing uses); with "pleasure" to pleasure. The connection need is one pool (cohabiting, friends and time
    together all fill it), so it is its own group and is not split by source."""
    g = dict.fromkeys(GROUPS, 0.0)
    pn, pa = p["p_need"], p["p_asp"]
    g["money"] += pn["money"] + pa.get("savings_per_week", 0.0)
    g["security"] += pn["security"] + pa.get("security_buffer", 0.0)
    g["rest"] += pn["rest"]
    g["connection"] += pn["connection"]
    g["partner"] += pa.get("together_per_week", 0.0) + p["together_event"]
    g["friends"] += pa.get("friends_per_week", 0.0)
    g["autonomy"] += pa.get("autonomy", 0.0)
    g["other"] += p["glow"]
    x = p.get("x") or {}
    items = x.get("items", 0.0)
    g["items"] += items
    fx = x.get("fix") or {}
    fix_pl = x.get("fix_pl", 0.0)
    pressure = fx.get("pr_reward", 0.0) - fx.get("pr_stigma", 0.0) - fx.get("pr_exit", 0.0)
    intrinsic = fx.get("pr_intrinsic", 0.0)
    bought = fx.get("bought", 0.0)
    g["pressure"] += pressure
    g["intrinsic"] += intrinsic
    g["money"] += bought
    contact = fix_pl - pressure - intrinsic - bought          # fix 1: amplification (friend, partner) and release
    amp = x.get("amp")
    if amp and contact:
        g["friends"] += amp[0]
        g["partner"] += amp[1]
        g["other"] += contact - amp[0] - amp[1]
    else:
        g["other"] += contact
    g["levers"] += x.get("lever_pl", 0.0)
    g["other"] += p["extra"] - items - fix_pl - x.get("lever_pl", 0.0)     # rounding residue; 0 when nothing else lands there
    g["clip"] += p["clip_p"]
    if measure == "pleasure":
        return g
    sn, sa = p["s_need"], p["s_asp"]
    g["money"] -= sn["money"] + sa.get("savings_per_week", 0.0)
    g["security"] -= sn["security"] + sa.get("security_buffer", 0.0)
    g["rest"] -= sn["rest"]
    g["connection"] -= sn["connection"]
    g["partner"] -= sa.get("together_per_week", 0.0)
    g["friends"] -= sa.get("friends_per_week", 0.0)
    g["autonomy"] -= sa.get("autonomy", 0.0)
    lever_fr = x.get("lever_fr", 0.0)
    g["levers"] -= lever_fr
    g["friction"] -= p["friction"] - lever_fr
    g["conditions"] -= sum(p["pre_onset"].values()) + sum(p["s_non"].values())
    g["clip"] -= p["clip_off"] + p["clip_non"]
    return g


def mean_groups(plist, measure=None):
    """Mean of groups() over a rollout's weekly parts. measure None reads the active fix config (negotiation.wellbeing's rule)."""
    if not plist:
        return None
    if measure is None:
        fx = HD.active_fixes()
        measure = "pleasure" if (fx is not None and fx.decide_on == "pleasure") else "net"
    acc = dict.fromkeys(GROUPS, 0.0)
    for p in plist:
        for k, v in groups(p, measure).items():
            acc[k] += v
    return {k: _r(v / len(plist)) for k, v in acc.items()}


def rollout_parts(hed, n0):
    """Parts recorded by a rollout's Hedonic after index n0, grouped and averaged (None when the Hedonic did not record parts)."""
    if not getattr(hed, "parts_on", False):
        return None
    return mean_groups(hed.parts_acc[n0:])


def utility_parts(agent, o, a, v, n):
    """D2: the parts of one action's utility (PersonaAgent.utilities), computed beside the agent's own arithmetic from the same pure
    functions. v is the utility after the withdrawal and lever scales, n the noise factor (a draw already made). Parts sum to v * n."""
    from .worlds import household as H
    h, cap, L = o["hed"], o["hed"].capacity, o["hed"].level
    asp, sat = o["asp"], h.satisfaction

    def need(nm, d):
        return h.sal[nm] * H._m(L[nm]) * min(max(d, -1.0), 1.0 - L[nm]) if d > 0 else h.sal[nm] * H._m(L[nm]) * d

    cost_money = lambda x: need("money", x / h.cfg.money_scale)  # noqa: E731
    b = {}
    if a == "work":
        inc = H.V2_INCOME[o["role"]]
        b = {"money": need("money", inc / h.cfg.money_scale) / 1.5,
             "savings": 0.3 * h.asp_w["savings_per_week"] * (sat("savings_per_week", max(0, asp["net"] + inc))
                                                             - sat("savings_per_week", max(0, asp["net"]))) / 1.5,
             "rest": -need("rest", h.cfg.work_fatigue) / 1.5}
    elif a == "rest":
        b = {"rest": need("rest", h.cfg.rest_action * cap) / 1.2}
    elif a == "see_friend":
        b = {"connection": need("connection", h.cfg.conn_friend * cap) / 1.2,
             "friends": 0.5 * h.asp_w["friends_per_week"] * (sat("friends_per_week", asp["friends"] + 1)
                                                             - sat("friends_per_week", asp["friends"])) / 1.2}
    elif a == "together":
        b = {"connection": need("connection", h.cfg.conn_together * cap) / 1.2,
             "together": 0.5 * h.asp_w["together_per_week"] * (sat("together_per_week", asp["together"] + 1)
                                                               - sat("together_per_week", asp["together"])) / 1.2,
             "partner": 0.05 * agent.prosocial * cap * o["partner_conn_deficit"] / 1.2}
    elif a == "spend_self":
        b = {"autonomy": 0.05 * h.asp_w["autonomy"] + 0.02, "money": -cost_money(2),
             "savings": -0.3 * h.asp_w["savings_per_week"] * (sat("savings_per_week", max(0, asp["net"]))
                                                              - sat("savings_per_week", max(0, asp["net"] - 2)))}
    elif a == "spend_shared" and o["gap"] > 0:
        frac = o["gap"] / max(1, o["need_month"])
        f = frac * (1.0 if o["last_week_of_month"] else 0.6)
        threat = max(0.3, min(1.0, 1 - o["pooled"] / 2 / 30))
        b = {"bills": f * 0.10, "security": f * 0.9 * h.sal["security"] * threat, "household": f * 0.5 * agent.prosocial * cap,
             "money": -cost_money(3)}
    s = sum(b.values())
    s1 = s * (1.0 - o["withdraw"]) if (a == "see_friend" and o.get("withdraw")) else s
    lv = o.get("lever")
    s2 = s1
    if lv and lv["adaptive"]:
        s2 = s1 * (lv["together_scale"] if a == "together" else lv["friend_scale"] if a == "see_friend" else 1.0)
    if s1 != s:
        b["pressure_withdraw"] = s1 - s
    if s2 != s1:
        b["lever_spacing"] = s2 - s1
    if abs(v - s2) > 1e-12:
        b["other"] = v - s2
    b["noise"] = v * n - v
    return {k: _r(x) for k, x in b.items()}


# ---- counterfactual replays --------------------------------------------------------------------------------------------------

def _same(c, t):
    return c["a"] == t["a"] and c.get("kind") == t.get("kind") and c.get("take", 0) == t.get("take", 0)


def forced(world, r, w, cands):
    """A replay copy's step_agent hook (world._force is set only on copies). Suppress drops actions for a role over the window; swap
    puts one candidate first at one decision (week, role, call index), so the copy executes it if it is feasible and not blocked."""
    f = world._force
    k = f["calls"].get((w, r), 0)
    f["calls"][(w, r)] = k + 1
    sup = f.get("suppress", {}).get(r)
    if sup and w < f["until"]:
        cands = [(u, c) for u, c in cands if c["a"] not in sup]
    sw = f.get("swap")
    if sw and sw["w"] == w and sw["r"] == r and sw["k"] == k:
        hit = next(((u, c) for u, c in cands if _same(c, sw["cand"])), None)
        f["swap_found"] = hit is not None
        if hit is not None:
            cands = [(99.0, hit[1])] + [x for x in cands if x is not hit]
    return cands


def _branch_summary(c, n0, w0, weeks):
    from . import negotiation as NG
    outs = c.run.outcomes[n0:]
    s = {"weeks": len(outs), "both_in": sum(1 for o in outs if o["both_in"]), "pot": _r(c.pool, 3),
         "exits": [[e["week"], e["role"]] for e in c.exit_log if e["week"] >= w0]}
    for r in ROLES:
        s[r] = {"net": _r(NG.wellbeing(outs, r)) if outs else None,
                "pleasure": _r(sum(o["hedonic"][r]["pleasure"] for o in outs) / len(outs)) if outs else None,
                "in_weeks": sum(1 for o in outs if o["partners"][r]["in"]), "money": _r(c.p[r]["money"], 3),
                "B": _r(c.hed[r].B, 4), "N": _r(c.hed[r].N, 4), "trust": _r(c.trust[r], 4)}
    return s


def _acts(c, w):
    return {r: [[t["action"], t.get("kind"), t.get("take", 0)] for t in c.run.trace if t.get("week") == w and t.get("role") == r
                and t.get("executed")] for r in ROLES}


# ---- the observer ------------------------------------------------------------------------------------------------------------

def pair_key(world):
    pa, pb = world.personas["A"], world.personas["B"]
    return f"{pa.id}|{pb.id}|{world.seed}"


class Observer:
    """Attach with Observer(world, cfg, run_key=..., meta=...). Rows accumulate in memory (`rows`); write(path) writes them as gzipped
    JSONL. Deep copies of the world (rollouts, replays) carry no observer: __deepcopy__ returns None."""

    def __init__(self, world, cfg=None, run_key=None, meta=None, harness=None):
        self.world, self.cfg = world, cfg or ObsConfig()
        self.pair_key = pair_key(world)
        self.run_key = run_key or self.pair_key
        self.rows = []
        self.calls = {r: 0 for r in ROLES}
        self.week = -1
        self._consent = {}
        self._snap, self._sampled = None, False
        self._replays = 0
        self._leaves = []
        self._open_sanc, self._open_veto, self._commits, self._items = {}, {}, {}, None
        self._ev, self._ex = len(getattr(world, "events", []) or []), len(world.exit_log)
        world.observer = self
        self._role = {}
        for r in ROLES:
            ag = world.agents[r]
            if hasattr(ag, "consents") and hasattr(ag, "persona"):
                ag._obs = self
                self._role[id(ag)] = r
            h = world.hed[r]
            h.parts_on = True
            if h.parts_acc is None:
                h.parts_acc = []
        self._header(meta or {})
        if harness is not None:
            self.harness(harness)
        self._commit_diff(-1, "start")
        self._item_diff(-1, "start")

    def __deepcopy__(self, memo):
        return None

    def __reduce__(self):            # a pickled world drops its observer, as a deep copy does
        return (_none, ())

    # -- rows
    def add(self, t, **kw):
        kw["t"] = t
        self.rows.append(kw)

    def _header(self, meta):
        w = self.world
        pers = {}
        for r in ROLES:
            p, h, ag = w.personas[r], w.hed[r], w.agents[r]
            pers[r] = {"id": p.id, "style": p.negotiation_style, "weights": {k: _r(v, 4) for k, v in p.weights.items()},
                       "sal": {k: _r(v, 4) for k, v in h.sal.items()}, "targets": dict(h.targets),
                       "asp_w": {k: _r(v, 4) for k, v in h.asp_w.items()}, "prosocial": _r(getattr(ag, "prosocial", 0.0), 4),
                       "agent": type(ag).__name__}
        self.add("run", schema=SCHEMA, run_key=self.run_key, pair_key=self.pair_key, seed=w.seed, weeks=w.weeks, meta=_plain(meta),
                 personas=pers, cards=[c.id for c in w.gate.cards], fixes=repr(w.fx) if w.fx else None,
                 levers=repr(w.lv) if w.lv else None, mech=w.mech, pot=w.pot, items=bool(w.items), cfg=asdict(self.cfg),
                 bal0=self.balances())

    def harness(self, lived):
        """Drain decisions a harness logged before this observer existed (week-0 formation)."""
        for rec in getattr(lived, "obs_pending", []) or []:
            self.rows.append(rec)
        lived.obs_pending = []
        lived.observer = self

    # -- money
    def balances(self):
        w = self.world
        return {"A": float(w.p["A"]["money"]), "B": float(w.p["B"]["money"]), "pot": float(w.pool), "bills": float(w.funded),
                "escrow": float((w.contest or {}).get("escrow", 0.0)) if isinstance(w.contest, dict) else 0.0}

    def flow_direct(self, w, src, dst, amount, cause, **kw):
        if self.cfg.flows and amount and abs(amount) > 1e-9:
            self.add("flow", w=w, src=src, dst=dst, amt=_r(amount, 4), cause=cause, **_plain(kw))

    def flow_diff(self, w, cause, actor, before):
        """Flows implied by the balance change since `before`: sources (balances that fell) paired greedily with sinks (that rose);
        what does not pair comes from or goes to "outside" (income, living costs)."""
        if not self.cfg.flows:
            return
        now = self.balances()
        d = {k: now[k] - before[k] for k in now}
        src = [[k, -v] for k, v in d.items() if v < -1e-9]
        dst = [[k, v] for k, v in d.items() if v > 1e-9]
        while src and dst:
            m = min(src[0][1], dst[0][1])
            self.flow_direct(w, src[0][0], dst[0][0], m, cause, actor=actor)
            src[0][1] -= m
            dst[0][1] -= m
            if src[0][1] <= 1e-9:
                src.pop(0)
            if dst[0][1] <= 1e-9:
                dst.pop(0)
        for k, v in src:
            self.flow_direct(w, k, "outside", v, cause, actor=actor)
        for k, v in dst:
            self.flow_direct(w, "outside", k, v, cause, actor=actor)

    # -- agent callbacks
    def consent_detail(self, agent, kind, would, trust, draw, answer):
        r = self._role.get(id(agent))
        if r is None:
            return
        coin = getattr(agent, "_coin", None)
        agent._coin = None
        p = agent.persona
        self._consent[r] = {"kind": kind, "style": p.negotiation_style, "autonomy": _r(p.weights["autonomy"], 4), "would": bool(would),
                            "coin": None if coin is None else _r(coin), "trust": _r(trust, 4),
                            "draw": None if draw is None else _r(draw), "answer": bool(answer)}

    # -- decisions (D1 D2 D4 D7, R1)
    def decision(self, r, w, o, order, i):
        from .worlds import household as H
        k = self.calls[r]
        self.calls[r] += 1
        if not self.cfg.decisions:
            return
        world = self.world
        P = o.get("_parts") or {}
        cands, runner, stop = [], None, False
        for j, (u, cand, dec, sanc, reasons) in enumerate(order):
            a = cand["a"]
            below = u <= 0.003 and a not in ("leave", "return")
            stop = stop or below
            feas = world.feasible(r, a, cand.get("kind"))
            in_trace = (not stop) and feas and (j == i or (dec == "hard" and (i is None or j < i)))
            cost = sum(H.SANCTION_UTILITY[s["kind"]] * H.MONTH_WEEKS * s["duration_months"] for s in sanc) if dec == "soft" else 0.0
            if j == i:
                st = "chosen"
            elif below:
                st = "below"
            elif not feas:
                st = "infeasible"
            elif dec == "hard":
                st = "blocked"
            else:
                st = "open" if (i is None or j > i) else "skipped"
                if i is not None and j > i and runner is None:
                    runner = j
            plain = set(cand) == {"a"} and a in P
            parts = dict(P[a]) if plain else {"policy": _r(u + cost)}
            if cost:
                parts["sanction"] = _r(-cost)
            if plain and abs(u + cost - sum(P[a].values())) > 1e-6:
                parts["policy"] = _r(u + cost - sum(P[a].values()))      # a pressing agent's rescaling of the persona utility
            c = {"a": a, "u": _r(u), "dec": dec, "st": st, "parts": parts}
            if in_trace:
                c["tr"] = 1             # this candidate has a row in run.trace (checked by the world: blocked, or executed)
            for key in ("kind", "take", "why", "motive"):
                if cand.get(key) not in (None, 0, False):
                    c[key] = cand[key]
            if reasons:
                c["reasons"] = list(reasons)
            cands.append(c)
        rec = {"w": w, "r": r, "k": k, "in": bool(o["in_hh"]), "partner_accepts": bool(o.get("partner_accepts")), "chosen": i,
               "runner": runner,
               "margin": _r(order[i][0] - order[runner][0]) if (i is not None and runner is not None) else None,
               "sig": _sig(world.state(r, w)), "cands": cands}
        if o["in_hh"]:
            hed = o["hed"]
            low, nn, tr = o["low_weeks"] >= 4, hed.N >= 0.2, o.get("trust", 1.0) < H.TRUST["leave_below"]
            bar = bool(o.get("bar_leave"))
            if low or nn or tr or bar or any(c["a"] == "leave" for c in cands):
                rec["leave_ctx"] = {"low_weeks": o["low_weeks"], "N": _r(hed.N, 4), "trust": _r(o.get("trust", 1.0), 4), "low": low,
                                    "n_high": nn, "trust_low": tr, "bar": bar, "open": bool(o.get("leave_open", True)),
                                    "takes": list(o.get("leave_takes", H.LEAVE_TAKES)), "cond_run": dict(hed.run),
                                    "ladder": world.ladder[r]["stage"] if world.fx and hasattr(world, "ladder") else None}
        if o.get("mech") and o["other_in"]:
            pro = getattr(world.agents[r], "prosocial", 0.0)
            rec["gift_ctx"] = {"prosocial": _r(pro, 4), "partner_money": o["partner_money"], "own_money": o["own_money"],
                               "fires": bool(pro >= 0.5 and o["partner_money"] < 4 and o["own_money"] >= 8)}
        if r in self._consent:
            rec["consent"] = self._consent.pop(r)            # the refuse decision: would this member say yes to what stands on them
        self.add("decision", **rec)
        sig = rec["sig"]
        for c in cands:
            for why in c.get("reasons", []):
                src = ("sanction" if why.startswith("sanction ") else "veto" if why.startswith("veto:")
                       else "commitment" if why.startswith("commitment:") else "card")
                card = world.cards.get(why) if src == "card" else None
                self.add("rule", w=w, r=r, a=c["a"], src=src, card=why, verdict=c["dec"],
                         deontic=card.deontic if card else None, acted=c["st"] == "chosen", sig=sig)
        if i is not None:
            a = order[i][1]["a"]
            checked = [c.id for c in world.gate._by.get(("partner", a), [])]
            if checked and order[i][2] == "ok":
                self.add("rule", w=w, r=r, a=a, src="card", card=checked, verdict="permit", deontic=None, acted=True, sig=sig)

    def breached(self, r, a, w, before):
        self.flow_diff(w, "breach_fine", r, before)
        self.add("commit", w=w, event="breach", by=r, action=a)

    def applied(self, r, cand, w, sanc, before):
        a = cand["a"]
        oth = "B" if r == "A" else "A"
        world = self.world
        self.flow_diff(w, a if a != "give" else f"give_{cand.get('kind')}", r, before)
        if a == "together":
            self.add("together", w=w, initiator=r, partner=oth, accepted=True, tag="agent")
        elif a == "veto":
            self.add("veto", w=w, by=r, on=oth, kind=cand["kind"], until=world.vetoes[oth][cand["kind"]])
        elif a == "request":
            d = self._consent.pop(oth, None) or {}
            self.add("consent", w=w, asker=r, receiver=oth, **d, final=int(world.consent[oth]),
                     bound=bool(world.mech and world.req_commit(oth, r, cand["kind"], w)), motive=bool(cand.get("motive")))
        elif a == "leave":
            self._leaves.append((w, r, self.calls[r] - 1))
        for s in sanc:
            self.add("sanction", w=w, r=r, event="start", kind=s["kind"], card=s["card"], until=w + 4 * s["duration_months"])

    def friend(self, w, tgt, outcome, **kw):
        self.add("friend", w=w, r=tgt, outcome=outcome, **_plain(kw))

    def trust(self, w, who, why, before, after):
        self.add("trust", w=w, r=who, why=why, d=_r(after - before), v=_r(after))

    def word(self, w, speaker, receiver, gain, event, said=None):
        self.add("word", w=w, speaker=speaker, receiver=receiver, gain=_r(gain), event=event, said=said)

    def together(self, w, initiator, partner, accepted):
        self.add("together", w=w, initiator=initiator, partner=partner, accepted=accepted, tag=initiator)

    # -- harness callbacks (negotiation.py)
    def reading(self, rec):
        self.rows.append(dict(rec, t="reading"))

    def negotiation(self, rec):
        self.rows.append(dict(rec, t="negotiation"))

    def stay(self, w, reading):
        self.add("stay", w=w, **_plain(reading))

    # -- the week
    def week_begin(self, w, last_week):
        self.week = w
        self.calls = {r: 0 for r in ROLES}
        self._leaves = []
        ev = (getattr(self.world, "events", []) or [])
        self._pre = [[x[1], x[2]] for x in ev[self._ev:] if x[1] in ROLES]      # the harness's events between weeks (formed, terms)
        self._ev = len(ev)
        self._commit_diff(w, "harness")
        self._snap = None
        cfg, world = self.cfg, self.world
        if self._replays >= cfg.max_replays:
            return
        self._sampled = cfg.replay_rate > 0 and self._sampler(w).random() < cfg.replay_rate
        leave_possible = cfg.replay_leaves and any(world.p[r]["in"] and (world.distressed(r) or world.bar_out[r]) for r in ROLES)
        if self._sampled or leave_possible:
            self._snap = (self._copy(), {"busy": dict(last_week["busy"])})

    def _sampler(self, w):
        h = hashlib.sha256(f"{self.cfg.replay_seed}|{self.pair_key}|{w}".encode()).hexdigest()
        return random.Random(int(h[:16], 16))

    def _copy(self):
        """A deep copy of the world as it stands, without its run log (not needed to step on) and without any hook (a harness hook would
        otherwise see the copy's weeks). The live world is restored before this returns."""
        from .worlds import household as H
        world = self.world
        run, hook = world.run, world.hook
        world.run, world.hook = H.Run(), None
        try:
            return copy.deepcopy(world)
        finally:
            world.run, world.hook = run, hook

    def week_end(self, w, row, busy, settle):
        world = self.world
        ev = (getattr(world, "events", []) or [])
        self.add("week", w=w, pool=_r(world.pool, 3), both_in=bool(row["both_in"]), need_met=bool(row["need_met"]), settle=bool(settle),
                 pre_events=getattr(self, "_pre", []), events=[[x[1], x[2]] for x in ev[self._ev:] if x[1] in ROLES],
                 exits=_plain(world.exit_log[self._ex:]),
                 shocks=_plain(row.get("shocks", [])), busy=dict(busy), c_blocked=row.get("c_blocked", 0))
        self._ev, self._ex = len(ev), len(world.exit_log)
        if self.cfg.state:
            for r in ROLES:
                self._state_row(w, r, row)
        self._sanction_ends(w)
        self._veto_ends(w)
        self._commit_diff(w, "week")
        self._item_diff(w, "week")
        if self._snap is not None:
            self._replay_week(w)
            self._snap = None

    def _state_row(self, w, r, row):
        world = self.world
        h, me, wk = world.hed[r], world.p[r], world.wk[r]
        parts = h.parts_acc[-1] if h.parts_acc else None
        hr = row["hedonic"][r]
        rec = {"w": w, "r": r, "in": bool(me["in"]), "money": _r(me["money"], 3), "put": _r(world.put[r], 3),
               "money_in": _r(world.money_in[r], 3), "B": _r(h.B, 4), "N": _r(h.N, 4),
               "glow": _r(h.glow, 4), "cap": _r(h.capacity, 4), "levels": {k: _r(v, 4) for k, v in h.level.items()},
               "cond_run": dict(h.run), "low": me["low"], "trust": _r(world.trust[r], 4), "pending": sorted(world.pending[r]),
               "consent": int(world.consent[r]), "bound": sorted(k for k, u in world.bound_req[r].items() if u > w),
               "vetoes": sorted(k for k, u in world.vetoes[r].items() if u > w),
               "sanctions": [s["kind"] for s in world.sanctions[r] if s["until"] > w], "jobless": me["jobless"], "ill": me["ill"],
               "bar_out": bool(world.bar_out[r]), "pl": hr["pleasure"], "s_off": hr["s_off"], "s_non": hr["s_non"],
               "wk": {k: v for k, v in wk.items() if v}}
        if world.fx is not None and hasattr(world, "ladder"):
            rec["ladder"] = world.ladder[r]["stage"]
        if parts is not None:
            rec["g"] = {k: _r(v) for k, v in groups(parts).items() if v}
            rec["parts"] = _compact(parts)
        self.add("state", **rec)

    def _sanction_ends(self, w):
        world = self.world
        for r in ROLES:
            live = {id(s): s for s in world.sanctions[r]}
            for sid, s in list(self._open_sanc.get(r, {}).items()):
                if sid not in live:
                    self.add("sanction", w=w, r=r, event="end", kind=s["kind"], card=s["card"], until=s["until"])
            self._open_sanc[r] = live

    def _veto_ends(self, w):
        world = self.world
        for r in ROLES:
            live = dict(world.vetoes[r])
            for k, u in self._open_veto.get(r, {}).items():
                if k not in live:
                    self.add("veto", w=w, on=r, kind=k, until=u, event="end")
            self._open_veto[r] = live

    def _commit_diff(self, w, when):
        world = self.world
        live = {id(c): c for c in world.commits}
        for cid, c in live.items():
            key = (c["kind"], c["by"], c["to"], c.get("type"), c["from"], c["until"], c["breached"])
            old = self._commits.get(cid)
            if old is None:
                self.add("commit", w=w, event="made", when=when, kind=c["kind"], by=c["by"], to=c["to"], type=c.get("type"),
                         frm=c["from"], until=c["until"])
            elif old != key:
                ev = "renewed" if c["until"] > old[5] else "ended" if c["until"] < old[5] else "changed"
                if c["breached"] != old[6]:
                    ev = "breach_counted"
                self.add("commit", w=w, event=ev, when=when, kind=c["kind"], by=c["by"], to=c["to"], until=c["until"],
                         breached=c["breached"])
        for cid, old in self._commits.items():
            if cid not in live:
                self.add("commit", w=w, event="dropped", when=when, kind=old[0], by=old[1], to=old[2])
        self._commits = {cid: (c["kind"], c["by"], c["to"], c.get("type"), c["from"], c["until"], c["breached"])
                         for cid, c in live.items()}

    def _item_diff(self, w, when):
        items = self.world.items
        now = {n: it["holder"] for n, it in items.items()} if items else None
        if now != self._items:
            self.add("item", w=w, holders=now, prev=self._items, when=when,
                     cause="exit" if self._leaves else ("start" if when == "start" else "custody"))
            self._items = now

    # -- replays (C1 C3)
    def _replay_week(self, w):
        world, cfg = self.world, self.cfg
        snap, last = self._snap
        win = max(1, min(cfg.replay_window, world.weeks - w))
        jobs = []
        if cfg.replay_leaves:
            for (lw, r, k) in self._leaves:
                jobs.append(("stay", {"suppress": {r: {"leave"}}, "until": w + win}, r, k, None))
        if self._sampled:
            ds = [x for x in self.rows[-200:] if x["t"] == "decision" and x["w"] == w and x["runner"] is not None]
            if ds:
                d = ds[int(self._sampler(w + 100000).random() * len(ds))]
                alt = d["cands"][d["runner"]]
                cand = {"a": alt["a"], **({"kind": alt["kind"]} if "kind" in alt else {}), **({"take": alt["take"]} if "take" in alt else {})}
                jobs.append(("swap", {"swap": {"w": w, "r": d["r"], "k": d["k"], "cand": cand}, "until": w + 1}, d["r"], d["k"],
                             {"chosen": d["cands"][d["chosen"]]["a"], "alt": alt["a"], "margin": d["margin"]}))
        if not jobs and not (self._sampled and cfg.replay_pressure and getattr(world.fx, "pairing", None) is not None):
            return
        fact = self._step_copy(snap, last, w, win, None)
        base = _branch_summary(fact, 0, w, win)
        faithful = _acts(fact, w) == _acts(world, w) if world.run.trace else None
        for kind, force, r, k, info in jobs:
            if self._replays >= cfg.max_replays:
                break
            self._replays += 1
            cf = self._step_copy(snap, last, w, win, force)
            alt = _branch_summary(cf, 0, w, win)
            diff = {x: {m: (_r(alt[x][m] - base[x][m]) if isinstance(alt[x][m], (int, float)) and base[x][m] is not None
                            and alt[x][m] is not None else None) for m in ("net", "pleasure", "in_weeks", "money", "B", "N", "trust")}
                    for x in ROLES}
            self.add("replay", w=w, kind=kind, r=r, k=k, window=win, pair_key=self.pair_key, info=info, faithful=faithful,
                     applied=cf._force.get("swap_found", True), fact=base, alt=alt, diff=diff, acts_alt=_acts(cf, w))
        if self._sampled and cfg.replay_pressure and getattr(world.fx, "pairing", None) is not None and self._replays < cfg.max_replays:
            from . import pairing as PR
            self._replays += 1
            free = replace(world.fx, pairing=PR.free(world.fx.pairing))
            cf = self._step_copy(snap, last, w, 1, None, fx=free)
            f1, a1 = _acts(fact, w), _acts(cf, w)
            self.add("replay", w=w, kind="pressure_off", r=None, k=None, window=1, pair_key=self.pair_key, info=None,
                     faithful=faithful, applied=True, acts_fact=f1, acts_alt=a1,
                     changed={r: f1[r] != a1[r] for r in ROLES})

    def _step_copy(self, snap, last, w, weeks, force, fx=None):
        c = copy.deepcopy(snap)
        if force is not None:
            c._force = dict(force, calls={})
        if fx is not None:
            c.fx = fx
        lt = last
        for x in range(w, w + weeks):
            lt = {"busy": c.step_week(x, lt)}
        return c

    def finish(self, lived=None):
        world = self.world
        self.add("end", weeks=len(world.run.outcomes), exits=_plain(world.exit_log), pool=_r(world.pool, 3),
                 trust={r: _r(world.trust[r], 4) for r in ROLES}, replays=self._replays)
        return self

    # -- output
    def write(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, "wt") as f:
            for row in self.rows:
                f.write(json.dumps(_plain(row), separators=(",", ":")) + "\n")
        return path


def _none():
    return None


def write_run(ob, exp_dir):
    """Write one observer's rows to <exp_dir>/obs/<run_key>.jsonl.gz -> manifest entry."""
    exp_dir = Path(exp_dir)
    name = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in ob.run_key)
    p = ob.write(exp_dir / "obs" / f"{name}.jsonl.gz")
    counts = {}
    for row in ob.rows:
        counts[row["t"]] = counts.get(row["t"], 0) + 1
    return {"run_key": ob.run_key, "pair_key": ob.pair_key, "file": f"obs/{p.name}", "bytes": p.stat().st_size, "rows": counts}


def write_manifest(exp_dir, entries, experiment, cfg, note=""):
    """<exp_dir>/obs/manifest.json: schema version, experiment, observer config, one entry per run (file, bytes, row counts)."""
    exp_dir = Path(exp_dir)
    m = {"schema": SCHEMA, "experiment": experiment, "note": note, "cfg": asdict(cfg), "doc": "docs/notes/observer-schema.md",
         "runs": sorted(entries, key=lambda e: e["run_key"]),
         "total_bytes": sum(e["bytes"] for e in entries)}
    p = exp_dir / "obs" / "manifest.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(m, indent=1))
    return p


def _sig(state):
    from . import atlas as AT
    return AT.sig_bits(state)


def _compact(p):
    out = {}
    for k, v in p.items():
        if k in ("pleasure", "s_off", "s_non_total"):
            continue
        if isinstance(v, dict):
            v = {kk: _r(vv) for kk, vv in v.items() if isinstance(vv, (int, float)) and vv}
            if v:
                out[k] = v
        elif isinstance(v, (int, float)) and v:
            out[k] = _r(v)
    x = p.get("x") or {}
    if x:
        out["x"] = _plain({k: v for k, v in x.items() if v})
    return out


def _plain(x):
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if isinstance(x, set):
        return sorted(_plain(v) for v in x)
    if isinstance(x, float):
        return round(x, 6)
    if isinstance(x, (int, str, bool)) or x is None:
        return x
    try:
        import numpy as np
        if isinstance(x, np.floating):
            return round(float(x), 6)
        if isinstance(x, np.integer):
            return int(x)
    except ImportError:
        pass
    return str(x)


def read(path):
    """-> {table: [rows]} from one observer file."""
    out = {}
    with gzip.open(path, "rt") as f:
        for line in f:
            row = json.loads(line)
            out.setdefault(row["t"], []).append(row)
    return out


def harness_record(world, harness, rec):
    """A harness decision (negotiation.py) goes to the world's observer if it has one, else waits on the harness for an observer
    attached later (week-0 formation happens before an explicit attach is possible). Only called while parts are being recorded."""
    ob = getattr(world, "observer", None) if world is not None else None
    if ob is not None:
        ob.rows.append(_plain(rec))
    elif harness is not None:
        harness.obs_pending = getattr(harness, "obs_pending", None) or []
        harness.obs_pending.append(_plain(rec))
