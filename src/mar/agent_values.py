"""Agent values v2 (docs/results/agent-recalibration-prereg.md): an action's value is the change it makes to this week's close in the
hedonic model's own arithmetic. Read only when FixConfig(agent_values="v2"); v1 (PersonaAgent.utilities as it was) is the default.

The pieces:
  snapshot(world, r, w)   what the agent knows at a call: its levels, its week so far (own and partner's actions, the friend's visit),
                          its money, the pot and the month's bills, the fix and lever state that this week's close will read.
  advance(s, ...)         the snapshot after planned actions (makers.WeekPlanner): counts, money, the bill funded.
  week_net(s, d)          the projected net of this week's close (clipped pleasure - clipped offsettable suffering - non-offsettable),
                          with the extra actions d and nothing else this week.
  utilities(agent, o)     {action: value}: own change + prosocial share of the partner's change (together, shared bills), noise.

Kept on purpose (prereg, "Kept as they are"): one-week horizon; only an adaptive persona expects satiety (ADR 0016); H38 withdrawal
scales the wish to see friends. Terms this week's close reads that no action here changes (items, pairing terms, ritual anticipation,
commitment payoff and friction, glow, warnings and presses already running) are held at their current value; the makers' terms at last
week's. Wording rule: agents feel nothing; "pleasure" and "value" are glosses for modeled numbers.
"""
from __future__ import annotations

from . import hedonic as HD

SANCTION_COST_V2 = {"cap_halve": 0.2, "suspend": 0.2}   # per week: the restricted condition before onset (0.5 x 0.4; ASSUMED)


def _clip(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


# ---- what the agent knows at a call --------------------------------------------------------------------------------------------

def snapshot(world, r, w):
    from .worlds import household as H
    me, oth = world.p[r], world.other(r)
    o = world.p[oth]
    h, wk, fx, lv = world.hed[r], world.wk[r], world.fx, world.lv
    adapt = bool(lv and lv.adapt)
    lw = world.lw if (lv and world.cur_w == w) else {"tog": [], "fr": {"A": [], "B": []}, "visits": {"A": {}, "B": {}}}
    with_f = world.with_friend(r)
    cohab = (me["in"] and o["in"]) or with_f
    cpen = wk["conn_hit"] + (0.1 if world.moved else 0.0)
    if lv and lv.network and world._down("H", 0, w):
        cpen += lv.partner_rupture_conn
    s = {"role": r, "h": h, "L": h.level, "cap": h.capacity, "in": me["in"], "both": me["in"] and o["in"], "cohab": cohab,
         "rests": wk["rests"], "works": wk["works"], "friends": wk["friends"], "together": wk["together"],
         "fi": wk["friend_initiated"] + (1 if with_f else 0), "income": wk["income"], "spent": wk["spent_self"],
         "eff_tog": sum(lw["tog"]) if adapt else wk["together"], "eff_fr": sum(lw["fr"][r]) if adapt else wk["friends"],
         "money": float(me["money"]), "ill": bool(me["ill"]), "sec_hit": wk["sec_hit"], "conn_pen": cpen,
         "out_cost": HD.DEFAULT.living_cost + (1 if me["ill"] else 0) + (0 if (me["in"] or with_f) else 1.5),
         "pool": float(world.pool), "n_in": sum(1 for x in "AB" if world.p[x]["in"]),
         "settle": w % H.MONTH_WEEKS == H.MONTH_WEEKS - 1, "need": world.need_month(), "funded": world.funded,
         "bills_hurt": bool(fx.bills_hurt), "fx": fx, "lv": lv,
         "autonomy": getattr(h, "last_autonomy", 1.0)}
    if fx.valued_money:
        s["v_s"] = min(1.0, float(world.personas[r].weights["security"]) / fx.w_ref)
    # terms this week's close reads that no action here changes
    warn = any(x["kind"] == "warn" and x["until"] > w for x in world.sanctions[r])
    fric = (H.WARN_FRICTION if warn else 0.0) + H.PRESS_FRICTION * wk["pressed"]
    if world.contest:
        fric += H._EXIT.CONTEST_FRICTION
    extra = h.glow + (H._ITEMS.weekly_pleasure(world, r) if world.items else 0.0)
    if world.makers:
        mp, mf = getattr(world, "_mk_last", {}).get(r, (0.0, 0.0))
        extra += mp
        fric += mf
    if fx.pairing is not None:
        extra += H._PAIR.terms(world, r, w)[0]
    if fx.fines and world.fine_amount and s["both"]:
        fric += fx.keep_friction * (1.0 - float(world.personas[r].weights["security"]))
    fric += fx.checkin_cost * wk.get("checkin", 0)
    if lv:
        _, _, d = world._lever_terms(r, w)          # pure: reads the state, changes nothing
        extra += d.get("antic", 0.0) + d.get("k_pay", 0.0)
        fric += d.get("commit_friction", 0.0)
        if lv.network:
            s["q0"], s["qx"], s["sets"] = world.q0, list(world.qx[r]), world.sets[r]
            s["n_sess"] = len(lw["tog"])
            s["visits"] = dict(lw["visits"][r])
            s["down0"] = world._down("H", 0, w)
            s["downx"] = [world._down(r, j + 1, w) for j in range(world.nx[r])]
            s["pick"] = world._pick_bond(r)
            s["_strand_memo"] = {}          # shared by the snapshot's advanced copies: bond quality depends on sessions and visits only
    s["extra"], s["fric"] = extra, fric
    if fx.contact:
        s["cx"] = dict(world.cx[r])
        s["overlap_ab"] = world.overlap_ab
        s["partner_tog"] = wk["together"] if (me["in"] and o["in"]) else 0
    return s


def advance(s, friends=0, together=0, works=0, self_spends=0, shared=0, rests=0, inc=0, self_step=2, share_step=3, scale=None):
    """The snapshot after planned actions (makers.WeekPlanner): counts, money, the bill funded. Satiety is not advanced (scale: the
    per-session scale the agent expects, 1 for a non-adaptive persona)."""
    if not (friends or together or works or self_spends or shared or rests):
        return s
    t = dict(s)
    fs, ts = (scale or (1.0, 1.0))
    t["friends"] += friends; t["eff_fr"] += friends * fs
    t["together"] += together; t["eff_tog"] += together * ts
    t["works"] += works; t["income"] += inc * works
    t["rests"] += rests
    t["spent"] += self_step * self_spends
    t["money"] += inc * works - self_step * self_spends - share_step * shared
    for _ in range(shared):                       # as the world applies a payment: the bill first, any surplus into the pot
        if t["funded"] >= t["need"]:
            t["pool"] += share_step
        else:
            t["funded"] += share_step
    if "n_sess" in t:
        t["n_sess"] += together
        if friends and t.get("pick") is not None:
            v = dict(t["visits"]); v[t["pick"]] = v.get(t["pick"], 0) + friends; t["visits"] = v
    if "partner_tog" in t:
        t["partner_tog"] += together
    return t


# ---- this week's close, projected ----------------------------------------------------------------------------------------------

def _contact(fx, cx, n_f, n_p, cohab_pair, overlap_ab):
    """The world's _contact_terms for one week, on a copy of the closeness state -> (pleasure, pain). Same arithmetic."""
    cf, Tf, af, cp, Tp, ap, was = cx["cf"], cx["Tf"], cx["af"], cx["cp"], cx["Tp"], cx["ap"], cx["was_with"]
    unit = fx.session_base * fx.a_max * fx.sociability
    amp = unit * (n_f * cf * fx.overlap_C + n_p * cp * overlap_ab)
    rel = pain = 0.0
    if n_f > 0:
        rel += fx.k_rel * Tf
        Tf = 0.0
    else:
        af += 1
        want = 0.5 ** (af / fx.want_half)
        Tf += cf * want * (1.0 - Tf / fx.t_cap)
    if cohab_pair:
        if not was:
            rel += fx.k_rel * Tp
        Tp = 0.0
    else:
        ap += 1
        want = 0.5 ** (ap / fx.want_half)
        Tp += cp * want * (1.0 - Tp / fx.t_cap)
    for T in (Tf, Tp):
        if T > fx.t_pain:
            pain += fx.pain_rate * (T - fx.t_pain)
    return amp + rel, pain


def _strands(s):
    key = (s["n_sess"], tuple(sorted(s["visits"].items())))
    memo = s["_strand_memo"]
    if key not in memo:
        memo[key] = _strands_calc(s)
    return memo[key]


def _strands_calc(s):
    lv = s["lv"]
    g = 1.0 - ((1.0 - lv.q0_cohab) if s["both"] else 1.0) * (1.0 - lv.q0_together) ** s["n_sess"]
    q0 = 0.0 if s["down0"] else (s["q0"] + g * (1.0 - s["q0"])) * (1.0 - lv.q0_decay)
    qx = []
    for j, q in enumerate(s["qx"]):
        gj = 1.0 - (1.0 - lv.qx_visit) ** s["visits"].get(j, 0)
        qx.append(0.0 if s["downx"][j] else (q + gj * (1.0 - q)) * (1.0 - lv.qx_decay))
    return HD.strand_terms(lv, HD.strand_cover(lv, q0, qx, s["sets"]))


def week_net(s, parts=None):
    """Projected net of this week's close for the snapshot s (its counts are the week as it would end). parts: a dict to fill."""
    h, c, cap, L, fx = s["h"], s["h"].cfg, s["cap"], s["L"], s["fx"]
    rest = _clip(L["rest"] + c.rest_base + c.rest_action * cap * s["rests"] - c.rest_decay - c.work_fatigue * s["works"]
                 - (0.3 if s["ill"] else 0.0))
    conn = _clip(L["connection"] + (c.conn_cohabit if s["cohab"] else 0.0) - c.conn_decay - s["conn_pen"]
                 + cap * (c.conn_friend * s["eff_fr"] + c.conn_together * s["eff_tog"] + c.conn_friend_initiated * s["fi"]))
    m, pool = s["money"] - s["out_cost"], s["pool"]
    if m < 0:
        d = min(pool, -m + 2)
        pool -= d; m += d
    m = max(0.0, m)
    sec_hit, bill_fric = s["sec_hit"], 0.0
    if s["settle"]:
        need = s["need"]
        short = max(0, need - s["funded"])
        if s["bills_hurt"] and short > 0:
            due = short * (1.0 + fx.late_fee)
            before = pool
            d = min(pool, due)
            pool -= d
            if s["in"]:
                sec_hit += d / max(1, s["n_in"]) / c.sec_assets
                bill_fric += fx.bill_stress * (short / max(1, need)) * (1.0 - min(1.0, before / fx.bill_runway))
            if due - d > 0.01 and s["in"]:
                sec_hit += 0.15
                bill_fric += fx.evict_stress
        else:
            d = min(pool, short)
            pool -= d
            if short - d > 0.01 and s["in"]:
                sec_hit += 0.15
    share = (pool / 2 if s["both"] else pool) if s["in"] else 0.0
    sec = _clip(L["security"] - c.sec_decay - sec_hit + c.sec_refill * _clip((m + share) / c.sec_assets))
    lv = {"rest": rest, "connection": conn, "money": _clip(m / c.money_scale), "security": sec}
    sal = h.sal
    if fx.valued_money:
        v_s = s["v_s"]
        lost = sal["security"] * (1.0 - v_s)
        rc = sal["rest"] + sal["connection"]
        up = 1.0 + (lost / rc if rc > 0 else 0.0)
        p_need = (sum(sal[n] * up * _clip((lv[n] - 0.5) / 0.5) for n in ("rest", "connection"))
                  + sal["money"] * _clip((lv["money"] - 0.5) / 0.5) + sal["security"] * v_s * _clip((lv["security"] - 0.5) / 0.5))
    else:
        p_need = sum(sal[n] * _clip((lv[n] - 0.5) / 0.5) for n in HD.NEEDS)
    s_need = sum(sal[n] * _clip((0.5 - lv[n]) / 0.5) for n in HD.NEEDS)
    net = s["income"] - HD.DEFAULT.living_cost - 2.5 - s["spent"]          # BILLS_WEEKLY = 2.5
    av = {"security_buffer": sec, "together_per_week": s["together"], "friends_per_week": s["friends"],
          "savings_per_week": max(0, net), "autonomy": s["autonomy"]}
    sat = {k: h.satisfaction(k, av.get(k, 0.0)) for k in h.targets}
    p_asp = sum(h.asp_w[k] * sat[k] for k in sat)
    s_asp = c.unmet_aspiration * sum(h.asp_w[k] * (1 - sat[k]) for k in sat)
    extra, fric = s["extra"], s["fric"] + bill_fric
    if fx.contact:
        n_f = s["friends"] + s["fi"]
        a, p = _contact(fx, s["cx"], n_f, s["partner_tog"], s["both"], s["overlap_ab"])
        extra += a; fric += p
    if fx.valued_money:
        extra += HD.bought_pleasure(fx, s["spent"])
    if "n_sess" in s:
        pay, suf = _strands(s)
        extra += pay; fric += suf
    raw = c.w_need * p_need + c.w_aspiration * p_asp + c.together_event * s["eff_tog"] + extra
    s_off, s_non = s_need + s_asp + fric, 0.0
    run = h.run
    denied = any(lv[n] < c.denied_below and sal[n] >= c.denied_min_salience for n in HD.NEEDS)
    for name, on, inten in (("trapped", run["trapped"] > 0, c.trapped_intensity), ("denied", denied, c.denied_intensity),
                            ("diminished", run["diminished"] > 0, c.diminished_intensity)):
        if on:
            if run[name] + 1 >= c.onset_weeks:
                s_non += inten
            else:
                s_off += c.pre_onset_share * inten
    out = _clip(raw) - _clip(s_off) - _clip(s_non)
    if parts is not None:
        parts.update(pleasure=_clip(raw), s_off=_clip(s_off), s_non=_clip(s_non), raw=raw, levels=lv, bill_fric=bill_fric)
    return out


# ---- the agent's values ---------------------------------------------------------------------------------------------------------

def utilities(agent, o, parts=None):
    """-> {action: value} (noise applied as v1 does: one draw per action, in order). parts: a dict to fill with each action's
    own and partner terms (observer layer)."""
    from .worlds import household as H
    s, ps = o["v2"], o.get("v2_partner")
    h = o["hed"]
    lev = o.get("lever")
    adaptive = bool(lev and lev["adaptive"])
    ts = lev["together_scale"] if adaptive else 1.0
    fs = lev["friend_scale"] if adaptive else 1.0
    base = week_net(s)
    u, pp = {}, {}

    def own(**kw):
        return week_net(advance(s, scale=(fs, ts), **kw)) - base

    if o["can_work"] and o["in_hh"] is not None:
        u["work"] = own(works=1, inc=H.V2_INCOME[o["role"]])
    u["rest"] = own(rests=1)
    if o["can_see_friend"]:
        u["see_friend"] = own(friends=1)
    if o["in_hh"] and o["other_in"] and o["partner_accepts"]:
        mine = own(together=1)
        theirs = (week_net(advance(ps, together=1, scale=(1.0, ts))) - week_net(ps)) if ps is not None else 0.0
        u["together"] = mine + agent.prosocial * theirs
        pp["together"] = (mine, theirs)
    u["spend_self"] = own(self_spends=1, self_step=H.SELF_STEP)
    mine = own(shared=1, share_step=H.SHARE_STEP)
    theirs = 0.0
    if ps is not None and s["settle"] and s["bills_hurt"]:
        t = dict(ps)
        if t["funded"] >= t["need"]:
            t["pool"] += H.SHARE_STEP
        else:
            t["funded"] += H.SHARE_STEP
        theirs = week_net(t) - week_net(ps)
    u["spend_shared"] = mine + agent.prosocial * theirs
    pp["spend_shared"] = (mine, theirs)
    if o.get("withdraw") and "see_friend" in u:     # H38 dyadic withdrawal: a manipulated norm, kept
        u["see_friend"] *= 1.0 - o["withdraw"]
    out = {}
    for a, v in u.items():
        n = agent._noise()
        out[a] = v * n
        if parts is not None:
            m, t = pp.get(a, (v, 0.0))
            parts[a] = {"own_week": round(m, 6), "partner_share": round(agent.prosocial * t, 6), **(
                {"withdraw": round(v - (m + agent.prosocial * t), 6)} if abs(v - (m + agent.prosocial * t)) > 1e-12 else {}),
                "noise": round(v * n - v, 6)}
    return out


def sanction_cost(world, r, w, sanc):
    """v2: what the sanctions would really cost. A warning costs WARN_FRICTION for each week it adds beyond a warning already running
    (warnings do not stack); cap_halve and suspend SANCTION_COST_V2 a week."""
    from .worlds import household as H
    until = max([x["until"] for x in world.sanctions[r] if x["kind"] == "warn" and x["until"] > w], default=w)
    cost = 0.0
    for x in sanc:
        weeks = H.MONTH_WEEKS * x["duration_months"]
        if x["kind"] == "warn":
            new = w + weeks
            cost += H.WARN_FRICTION * max(0, new - max(until, w))
            until = max(until, new)
        else:
            cost += SANCTION_COST_V2.get(x["kind"], 0.0) * weeks
    return cost
