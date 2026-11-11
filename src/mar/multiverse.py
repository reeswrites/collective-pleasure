"""Multiverse sensitivity sweep (docs/results/multiverse-prereg.md).

Asks whether eight headline conclusions survive when their ASSUMED parameters move across a plausible range.
Every existing module is used read-only. Parameters move only through dataclass fields, function arguments, or module
globals the code reads at call time. Globals and bound default arguments are patched in memory, per worker process, and
never in files. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state (ADR 0010).

Pieces:
  Param, lhs, oat, spearman, label   the design and the robustness label (generic, tested)
  horizon_point, gap_point            C1 to C3: exact solves in mar.horizon
  vpgg_freedom_point, vpgg_osc_task   C7, C8: mar.liberty, mar.empowerment, mar.games.vpgg
  negotiation_task, pleasure_task,
  seedv2_task, apply_household        C4 to C6: the household world, negotiation and hedonic model, patched per process
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import combinations_with_replacement, permutations
from pathlib import Path
from typing import Callable, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SEED = 20261110

# ---------------------------------------------------------------------------------------------------------- design


@dataclass(frozen=True)
class Param:
    """One swept parameter. kind: 'log' (uniform on log scale), 'lin', 'int' (integers lo..hi), 'set' (values)."""
    name: str
    default: float
    lo: float = 0.0
    hi: float = 0.0
    kind: str = "log"
    values: tuple = ()

    def at(self, u: float):
        """Map u in [0, 1) to a value in the range."""
        u = min(max(u, 0.0), 1.0 - 1e-12)
        if self.kind == "log":
            return float(math.exp(math.log(self.lo) + u * (math.log(self.hi) - math.log(self.lo))))
        if self.kind == "lin":
            return float(self.lo + u * (self.hi - self.lo))
        if self.kind == "int":
            vals = list(range(int(self.lo), int(self.hi) + 1))
            return vals[int(u * len(vals))]
        if self.kind == "set":
            return self.values[int(u * len(self.values))]
        raise ValueError(self.kind)

    def ends(self) -> tuple:
        if self.kind in ("log", "lin"):
            return (self.lo, self.hi)
        if self.kind == "int":
            return (int(self.lo), int(self.hi))
        return (self.values[0], self.values[-1])

    def position(self, v) -> float:
        """Where v sits in the range, 0 to 1 (for rank correlations; any monotone map would do)."""
        if self.kind == "log":
            return (math.log(v) - math.log(self.lo)) / (math.log(self.hi) - math.log(self.lo))
        if self.kind == "set":
            return self.values.index(v) / max(len(self.values) - 1, 1)
        return (v - self.lo) / (self.hi - self.lo) if self.hi != self.lo else 0.0


def defaults(params: Sequence[Param]) -> dict:
    return {p.name: p.default for p in params}


def lhs(params: Sequence[Param], n: int, seed: int = SEED) -> list[dict]:
    """Latin hypercube: each parameter's range is cut into n strata, one draw per stratum, strata shuffled per parameter."""
    rng = np.random.default_rng(seed)
    cols = {}
    for p in params:
        u = (rng.permutation(n) + rng.random(n)) / n
        cols[p.name] = [p.at(x) for x in u]
    return [{p.name: cols[p.name][i] for p in params} for i in range(n)]


def oat(params: Sequence[Param], extra: dict | None = None) -> list[tuple[str, object, dict]]:
    """One at a time: every parameter at its low and high end, the rest at defaults. extra: {name: [more values]}."""
    base = defaults(params)
    out = []
    for p in params:
        vals = list(p.ends()) + list((extra or {}).get(p.name, ()))
        for v in vals:
            out.append((p.name, v, {**base, p.name: v}))
    return out


def _rank(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    # average ties
    xs = x[order]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        if j > i:
            r[order[i:j + 1]] = (i + j) / 2
        i = j + 1
    return r


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return 0.0
    rx, ry = _rank(x), _rank(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def label(lhs_holds: Sequence[bool], oat_flips: Sequence[str], default_holds: bool = True) -> str:
    """The preregistered robustness label."""
    if not default_holds:
        return "not reproduced at HEAD"
    share = float(np.mean(lhs_holds)) if len(lhs_holds) else float("nan")
    if share < 0.5:
        return "flips"
    if share < 0.9 or oat_flips:
        return "fragile"
    return "robust"


def summarize(params: Sequence[Param], lhs_points: list[dict], lhs_margins: list[float], oat_rows: list[tuple[str, object, float]],
              default_margin: float) -> dict:
    """lhs_margins and oat margins are signed so that > 0 means the conclusion holds (>= 0 for 'at least' thresholds is applied by
    the caller through the margin it passes)."""
    holds = [m > 0 for m in lhs_margins]
    flips = sorted({f"{n} = {_fmt(v)}" for n, v, m in oat_rows if m <= 0})
    corr = {p.name: spearman([p.position(pt[p.name]) for pt in lhs_points], lhs_margins) for p in params}
    top = max(corr, key=lambda k: abs(corr[k])) if corr else None
    return {"share": float(np.mean(holds)) if holds else float("nan"), "n": len(holds), "oat_flips": flips,
            "spearman": corr, "top_param": top, "top_rho": corr.get(top) if top else None,
            "default_margin": default_margin, "label": label(holds, flips, default_margin > 0)}


def _fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def _pool_map(fn: Callable, tasks: list, workers: int):
    if workers <= 1:
        return [fn(t) for t in tasks]
    from multiprocessing import get_context
    with get_context("spawn").Pool(workers) as pool:
        return pool.map(fn, tasks, chunksize=1)


# ---------------------------------------------------------------------------------------------------------- C1, C2: horizon MDP

HORIZON_PARAMS = (
    Param("delta", 0.2, 0.1, 0.4), Param("rho", 0.25, 0.125, 0.5), Param("nuD", 2.0, 1.0, 4.0), Param("beta", 1.5, 0.75, 3.0),
    Param("f", 3.0, 1.5, 6.0), Param("mu", 0.5, 0.25, 1.0), Param("muz", 1.0, 0.5, 2.0), Param("theta", 0.1, 0.05, 0.2),
    Param("kappa", 0.5, 0.25, 1.0), Param("bR", 7.0, 5.0, 9.0, "lin"), Param("bS", 6.0, 3.0, 12.0), Param("bX", 12.0, 8.0, 16.0, "lin"),
    Param("bV", 1.0, 0.5, 2.0), Param("A", 4, 3, 5, "int"), Param("W", 3, 2, 4, "int"), Param("C", 3, 2, 4, "int"),
    Param("kcontrast", 1, 0, 2, "int"), Param("vK", 2, 1, 3, "int"),
)
CONCERT_MS = tuple(range(1, 9))


def horizon_q(v: dict):
    from mar import horizon as Hz
    kw = {}
    for k, x in v.items():
        if isinstance(x, (int, np.integer)) and k in ("A", "W", "C", "kcontrast", "vK"):
            kw[k] = int(x)
        else:
            kw[k] = Fraction(x).limit_denominator(100000)
    kw["bK"] = kw["bX"]                    # the module's own rule: with no carryover a concert is worth exactly a free treat
    return replace(Hz.HorizonParams(), **kw)


def horizon_point(v: dict) -> dict:
    """C1 and C2 at one parameter point. Uses mar.horizon's public building blocks; concert_gain's 'net_carryover' is
    gain(full) - gain(q.off()), recomputed here with each table built once for all spacings."""
    from mar import horizon as Hz
    q = horizon_q(v)
    tab = Hz.Table(q)
    loss95 = Hz.greedy_loss(tab, Hz.START, 26, 0.95)["pct"]
    loss1_52 = Hz.greedy_loss(tab, Hz.START, 52, 1.0)["pct"]
    toff = Hz.Table(q.off())
    nc_full = Hz.constrained_value(tab, Hz.START, 26, 0.95, Hz.no_concert_mask)
    nc_off = Hz.constrained_value(toff, Hz.START, 26, 0.95, Hz.no_concert_mask)
    net = {}
    for m in CONCERT_MS:
        g_full = Hz.schedule_value(tab, Hz.START, 26, 0.95, m) - nc_full
        g_off = Hz.schedule_value(toff, Hz.START, 26, 0.95, m) - nc_off
        net[m] = float(g_full - g_off)
    mstar = next((m for m in CONCERT_MS if net[m] > 1e-9), None)
    return {"loss95_26": float(loss95), "loss1_52": float(loss1_52), "net": net, "mstar": mstar, "states": len(tab.states),
            "c1_margin": float(loss95 - 10.0) + 1e-12,     # 'at least 10%': margin >= 0 holds; tiny shift so exactly 10 counts
            "c2_margin": float(min(-net[1], net[4])),
            "c2b_margin": 1.0 if mstar in (2, 3, 4) else -1.0}


# ---------------------------------------------------------------------------------------------------------- C3: friend-contact gap

GAP_PARAMS = (
    Param("cost_sess", 7.2, 1.8, 28.8), Param("cost_occ", 0.8, 0.4, 1.6), Param("A", 1.0, 0.5, 2.0), Param("kappa", 0.5, 0.25, 1.0),
    Param("tau_s", 3.0, 1.5, 6.0), Param("amp_bad", 1.0, 0.5, 2.0), Param("m_scale", 0.3, 0.15, 0.6), Param("base_scale", 1.0, 0.5, 2.0),
    Param("soc_scale", 1.0, 0.5, 2.0), Param("tau_w", 7.0, 3.5, 14.0), Param("tau_a", 60.0, 30.0, 120.0), Param("reset", 0.6, 0.3, 0.9, "lin"),
    Param("thr", 6.0, 3.0, 12.0), Param("rel", 1.5, 0.75, 3.0), Param("nu", 0.01, 0.005, 0.02), Param("tau_m", 45.0, 22.5, 90.0),
)
GAP_EXTRA = {"cost_sess": [24.0, 0.0]}
GAP_HS = (10, 20, 45, 90)
OVERLAP = 0.7


def gap_point(v: dict, gmax: int = 200) -> dict:
    from mar import horizon as Hz
    acts = tuple(replace(a, base=a.base * v["base_scale"], soc=1.0 + v["soc_scale"] * (a.soc - 1.0)) for a in Hz.DEFAULT_ACTIVITIES)
    ap = Hz.AmpParams(cost_sess=v["cost_sess"], cost_occ=v["cost_occ"], A=v["A"], kappa=v["kappa"], tau_s=v["tau_s"],
                      amp_bad=v["amp_bad"], m_scale=v["m_scale"], activities=acts)
    ctrl = replace(ap, activities=())
    sp = Hz.SelfParams(nu=v["nu"], tau_m=v["tau_m"])
    best, best_ctrl = {}, {}
    for h in GAP_HS:
        p = Hz.GapParams(H=float(h), tau_w=v["tau_w"], tau_a=v["tau_a"], reset=v["reset"], thr=v["thr"], rel=v["rel"])
        best[h] = Hz.amp_best(p, sp, ap, OVERLAP, gmax)["best_gap"]
        best_ctrl[h] = Hz.amp_best(p, sp, ctrl, OVERLAP, gmax)["best_gap"]
    mx = max(best.values())
    shorten = min(best_ctrl[h] - best[h] for h in GAP_HS)
    return {"best": best, "best_ctrl": best_ctrl, "max_best": mx, "min_shortening": shorten,
            "c3_margin": 14.5 - mx, "c3_7_margin": 7.5 - mx, "c3_ctrl_margin": shorten - 0.5}


# ---------------------------------------------------------------------------------------------------------- C7: VPGG freedom

VPGG_RS = (2.0, 2.5, 3.0, 3.5, 4.0, 4.5)
VPGG_SIGMA_SHARES = (0.25, 0.5, 0.75)
VPGG_KS = (2, 3, 4)


def vpgg_freedom_point(args) -> dict:
    """Liberty v2 and empowerment, voluntary against compulsory, over the 15 compositions of four others (as liberty_run.vpgg and
    empowerment_run.vpgg_part do it), at VPGGWorld(r, c=1, sigma) and horizon k."""
    r, share, k = args
    from mar import empowerment as E
    from mar import liberty as L
    from mar.games import vpgg as V
    sigma = share * (r - 1.0)
    w = E.VPGGWorld(r=r, c=1.0, sigma=sigma)
    gates = {n: V.VPGate(V.load_regime(n, str(ROOT / "rules" / "vpgg"))) for n in ("voluntary", "compulsory")}
    lib, emp = [], []
    for comp in combinations_with_replacement("CDL", 4):
        pol_l = lambda s, i, comp=comp: comp[i - 1] if i else "C"  # noqa: E731  (as liberty_run.vpgg)
        pol_e = lambda s, i, comp=comp: comp[i - 1]  # noqa: E731  (as empowerment_run.vpgg_part)
        lv = {n: L.liberty(w, g, w.initial(), 0, k, pol_l, version=2)["liberty"] for n, g in gates.items()}
        ev = {n: E.empowerment(w, g, w.initial(), 0, k, pol_e)["bits"] for n, g in gates.items()}
        lib.append(lv["voluntary"] - lv["compulsory"])
        emp.append(ev["voluntary"] - ev["compulsory"])
    lib, emp = np.array(lib), np.array(emp)
    out = {"r": r, "sigma_share": share, "sigma": sigma, "k": k,
           "lib_sum": float(lib.sum()), "lib_wins": int((lib > 1e-9).sum()), "emp_sum": float(emp.sum()), "emp_wins": int((emp > 1e-9).sum())}
    out["lib_holds"] = out["lib_sum"] > 0 and out["lib_wins"] >= 8
    out["emp_holds"] = out["emp_sum"] > 0 and out["emp_wins"] >= 8
    out["c7_margin"] = 1.0 if (out["lib_holds"] and out["emp_holds"]) else -1.0
    return out


# ---------------------------------------------------------------------------------------------------------- C8: VPGG oscillation

VPGG_OSC_PARAMS = (
    Param("revision", 0.1, 0.05, 0.4), Param("mutation", 0.002, 0.0005, 0.008), Param("pop", 5000, 1000, 10000),
    Param("rounds", 5, 1, 10, "int"), Param("r", 3.0, 2.2, 4.5, "lin"), Param("sigma_share", 0.5, 0.25, 0.75, "lin"),
)
OSC_SEEDS = (0, 1, 2)
OSC_FLOOR = 0.05


def vpgg_params(v: dict):
    from mar.games import vpgg as V
    r = float(v["r"])
    return V.Params(r=r, sigma=float(v["sigma_share"]) * (r - 1.0), revision=float(v["revision"]), mutation=float(v["mutation"]),
                    pop=int(round(v["pop"])), rounds=int(v["rounds"]))


def vpgg_osc_task(args) -> dict:
    key, v, seed = args
    import os
    os.chdir(ROOT)                          # load_regime's default root is relative
    from mar.games import vpgg as V
    res = V.run(V.load_regime("voluntary"), seed, vpgg_params(v))
    return {"key": key, "seed": seed, "std_c": float(res["std_c"]), "mean_share": [float(x) for x in res["mean_share"]]}


# ---------------------------------------------------------------------------------------------------------- C4 to C6: household patching

HED_FIELDS = ("living_cost", "denied_below", "conn_decay", "onset_weeks", "conn_together", "together_event", "eta", "trapped_intensity")
_STATE = {"orig": None, "applied": None}


def _set_default(func, name: str, value) -> None:
    """Rebind one default argument of func (positional-or-keyword or keyword-only), in memory."""
    code = func.__code__
    pos = code.co_varnames[:code.co_argcount]
    if func.__kwdefaults__ and name in func.__kwdefaults__:
        func.__kwdefaults__[name] = value
        return
    d = list(func.__defaults__ or ())
    first = len(pos) - len(d)
    i = pos.index(name) - first
    if i < 0:
        raise ValueError(f"{func.__name__}.{name} has no default")
    d[i] = value
    func.__defaults__ = tuple(d)


def _get_default(func, name: str):
    code = func.__code__
    pos = code.co_varnames[:code.co_argcount]
    d = func.__defaults__ or ()
    return d[pos.index(name) - (len(pos) - len(d))]


def apply_household(v: dict) -> None:
    """Patch the household world, hedonic model and negotiation for one multiverse point, in this process only.
    Missing keys go back to the original defaults. Clears every negotiation cache when the point changes."""
    from mar import hedonic as HD
    from mar import negotiation as NG
    from mar.worlds import household as H
    if _STATE["orig"] is None:
        _STATE["orig"] = {"cfg": HD.DEFAULT, "BREACH_N": H.BREACH_N, "NO_POT_MONEY": H.NO_POT_MONEY, "FLOOR": NG.FLOOR,
                          "OUT_WEEKS": _get_default(NG.alone_value, "weeks")}
    o = _STATE["orig"]
    key = tuple(sorted(v.items()))
    if _STATE["applied"] == key:
        return
    cfg = replace(o["cfg"], **{k: (int(v[k]) if k == "onset_weeks" else float(v[k])) for k in HED_FIELDS if k in v})
    HD.DEFAULT = cfg
    for f in (HD.capacity, HD.feedback, HD.Hedonic.__init__, H.WeeklyWorld.__init__, H.run_weekly):
        _set_default(f, "cfg", cfg)
    H.BREACH_N = float(v.get("BREACH_N", o["BREACH_N"]))
    H.NO_POT_MONEY = v.get("NO_POT_MONEY", o["NO_POT_MONEY"])
    floor = float(v.get("FLOOR", o["FLOOR"]))
    NG.FLOOR = floor
    _set_default(NG.floor_check, "floor", floor)
    ow = int(v.get("OUT_WEEKS", o["OUT_WEEKS"]))
    _set_default(NG.alone_value, "weeks", ow)
    _set_default(NG.pot_baseline, "weeks", ow)
    for c in ("_RC", "_PC", "_DCACHE", "_UCACHE", "_PCACHE"):
        getattr(NG, c).clear()
    _STATE["applied"] = key


_PS: dict = {}
PRESSING = ("p-controller", "p-freerider", "p-overasker")


def personas() -> dict:
    if not _PS:
        from mar import personas as P
        _PS.update({p.id: p for p in P.load_dir(ROOT / "personas") + P.load_dir(ROOT / "personas" / "pressing")})
    return _PS


def pairings() -> list[tuple[str, str, str]]:
    """The 57 pairings of the pleasure demo and negotiation v2.1: 15 hand pairs plus 42 ordered pairs with a pressing persona."""
    from mar.worlds import household as H
    ps = personas()
    hand = [p for i, p in ps.items() if i not in PRESSING]
    out = [(a.id, b.id, "ctl") for a, b in H.persona_pairs(hand)]
    out += [(a, b, "prs") for a, b in permutations(sorted(ps), 2) if a in PRESSING or b in PRESSING]
    return out


def _s_non(run) -> float:
    from mar import household_oracle as O
    return float(O.hedonic_summary(run.outcomes)["s_non"])


def negotiation_task(args) -> dict:
    """C4: week-0 negotiation, then, if no pot, the household played the v2 way (cohabiting, no pot) and the v2.1 way (apart)."""
    key, v, arm, a, b, seed = args
    apply_household(v)
    from mar import negotiation as NG
    ps = personas()
    base = NG.base_cards("author_seed_v2_bindable")
    NG._RC.clear(); NG._PC.clear()
    res = NG.week0(ps[a], ps[b], arm, seed, base, floor=True)
    out = {"key": key, "arm": arm, "a": a, "b": b, "seed": seed, "pot": bool(res.pot)}
    if res.pot:
        return out
    for name, apart in (("cohabit", False), ("apart", True)):
        NG._RC.clear(); NG._PC.clear()
        L = NG.Lived(ps[a], ps[b], arm, seed, base, res, floor=True, apart=apart)
        out[name] = _s_non(L.play())
    return out


def pleasure_task(args) -> dict:
    """C5: one run of the pleasure demo, as scripts/pleasure_demo.py::run_task does it, for arms v22_bindable and baseline."""
    key, v, arm, a, b, seed = args
    apply_household(v)
    from mar import negotiation as NG
    from mar import pleasure_report as PR
    from mar.worlds import household as H
    NG._RC.clear(); NG._PC.clear()
    ps = personas()
    if arm == "baseline":
        world = PR.instrument(H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), (ps[a], ps[b]), seed, H.WEEKS))
        rec = PR.household_record(world, world.play(), keep_events=False)
    else:
        base = NG.base_cards("author_seed_v2_bindable")
        res = NG.week0(ps[a], ps[b], "fair_default", seed, base, floor=True)
        L = NG.Lived(ps[a], ps[b], "fair_default", seed, base, res, floor=True, apart=True)
        PR.instrument(L.world)
        rec = PR.household_record(L.world, L.play(), keep_events=False)
    return {"key": key, "arm": arm, "a": a, "b": b, "seed": seed, "pleasure": float(rec["pleasure"]), "rel_share": float(rec["rel_share"]),
            "together_weeks": rec["together_weeks"], "weeks": rec["weeks"]}


def seedv2_task(args) -> dict:
    """C6: one imposed run of a seed v2 variant (cards at HEAD), as household_run_bits builds the world, without the snapshots."""
    key, v, variant, a, b, seed = args
    apply_household(v)
    from mar.worlds import household as H
    ps = personas()
    run = H.WeeklyWorld(H.PyGate(H.load_variant(variant)), (ps[a], ps[b]), seed, H.WEEKS).play()
    return {"key": key, "variant": variant, "a": a, "b": b, "seed": seed, "s_non": _s_non(run)}


NEG_PARAMS = (
    Param("OUT_WEEKS", 26, values=(13, 26, 52), kind="set"), Param("FLOOR", 26.0, 13.0, 52.0), Param("NO_POT_MONEY", 55.0, 40.0, 70.0, "lin"),
    Param("BREACH_N", 0.2, 0.1, 0.4), Param("living_cost", 2.0, 1.0, 4.0), Param("denied_below", 0.15, 0.075, 0.3),
    Param("conn_decay", 0.3, 0.15, 0.6), Param("onset_weeks", 4, values=(2, 4, 8), kind="set"),
)
PLEASURE_PARAMS = (
    Param("living_cost", 2.0, 1.0, 4.0), Param("conn_decay", 0.3, 0.15, 0.6), Param("conn_together", 0.3, 0.15, 0.6),
    Param("together_event", 0.1, 0.05, 0.2), Param("denied_below", 0.15, 0.075, 0.3), Param("eta", 0.3, 0.15, 0.6), Param("BREACH_N", 0.2, 0.1, 0.4),
)
SEEDV2_PARAMS = (
    Param("BREACH_N", 0.2, 0.05, 0.8), Param("denied_below", 0.15, 0.075, 0.3), Param("onset_weeks", 4, values=(2, 4, 8), kind="set"),
    Param("conn_decay", 0.3, 0.15, 0.6), Param("living_cost", 2.0, 1.0, 4.0), Param("trapped_intensity", 0.5, 0.25, 1.0),
)


def negotiation_aggregate(rows: list[dict]) -> dict:
    nopot = [r for r in rows if not r["pot"]]
    if not nopot:
        return {"n_nopot": 0, "cohabit": None, "apart": None, "diff": None, "c4_margin": -1.0}
    c = float(np.mean([r["cohabit"] for r in nopot]))
    ap = float(np.mean([r["apart"] for r in nopot]))
    d = np.array([r["cohabit"] - r["apart"] for r in nopot])
    se = float(d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float("nan")
    return {"n_nopot": len(nopot), "n": len(rows), "cohabit": c, "apart": ap, "diff": c - ap, "se": se, "c4_margin": (c - ap) - 0.02 + 1e-12}


def pleasure_aggregate(rows: list[dict]) -> dict:
    by = {}
    for r in rows:
        by.setdefault((r["a"], r["b"], r["seed"]), {})[r["arm"]] = r
    diffs = np.array([x["v22_bindable"]["pleasure"] - x["baseline"]["pleasure"] for x in by.values() if len(x) == 2])
    hh = [r["rel_share"] for r in rows if r["arm"] == "v22_bindable" and r["together_weeks"] >= 0.9 * r["weeks"]]
    d2a = float(diffs.mean())
    se = float(diffs.std(ddof=1) / math.sqrt(len(diffs)))
    d3 = float(np.mean(hh)) if hh else float("nan")
    return {"d2a": d2a, "se": se, "n": len(diffs), "d3": d3, "n_households": len(hh), "c5_margin": d2a,
            "c5_d3_margin": (d3 - 0.40) if hh else -1.0}


def seedv2_aggregate(rows: list[dict]) -> dict:
    by = {}
    for r in rows:
        by.setdefault((r["a"], r["b"], r["seed"]), {})[r["variant"]] = r["s_non"]
    d = np.array([x["author_seed_v2_bindable"] - x["author_seed_v2_free_exit"] for x in by.values() if len(x) == 2])
    m = float(d.mean())
    return {"diff": m, "abs_diff": abs(m), "n": len(d), "nonzero": int((np.abs(d) > 1e-12).sum()), "c6_margin": 0.02 - abs(m)}
