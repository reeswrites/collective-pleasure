"""Household world for the evolution loop (ADR 0012), split out of world_api.py on 2026-11-11.

world_api.py keeps the world interface and the fishery adapter (engine). This module is the household (social) side, moved
here unchanged so the engine module no longer imports the household world at module level. world_api re-exports every
name from here lazily, so `from mar import world_api as W; W.HouseholdEvolveWorld` keeps working.
"""
import random
from dataclasses import dataclass
from pathlib import Path

from .cards import make_card
from .world_api import K_DEFAULT

# =====================================================================================================================
# Household world for the evolution loop (first household evolution run; docs/results/household-evolve-prereg.md).
# Scripted persona-driven agents, no model calls. Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for
# a modeled hedonic state derived from each persona's assigned preferences.
#
# The exam (docs/results/household-exam-prereg.md) is NOT in this module. The only thing taken from its section 1 is the
# six-id DENYLIST below (a mechanical rule: first byte of SHA-256 of the id < 48; `held_out_by_rule` recomputes it and a
# test asserts the two agree). Nothing else from the exam document appears in any evolution code, config, test or log.
# =====================================================================================================================
import dataclasses
import hashlib
import json as _json
from itertools import combinations as _combinations

from . import empowerment as _E
from . import household_oracle as _O
from . import hedonic as _HD
from . import lint as _lint
from . import liberty as _L
from . import negotiation as _NG
from . import personas as _P
from .worlds import household as _H

_ROOT = Path(__file__).parent.parent.parent
HH_RULES = _ROOT / "rules" / "household"
DENYLIST = ("g-10010", "g-10110", "g-11101", "g-01110", "g-11000", "g-00101")   # held out of every training use (exam doc section 1)
DENYLIST2 = ("g-00011", "g-10100", "g-01101", "g-11111", "g-10101", "g-00010")   # exam 2's held-out ids (docs/results/household-exam-2-prereg.md): denylist only
_EXTRA_DENY = ()


def use_extra_deny(ids):
    """Exclude more persona ids from training (run 2: DENYLIST2). Per process; the default () reproduces run 1."""
    global _EXTRA_DENY
    _EXTRA_DENY = tuple(ids)


def held_out_range(ids, lo, hi):
    """Exam 2's mechanical rule: held out iff the first byte of SHA-256(id) is in [lo, hi)."""
    return sorted(i for i in ids if lo <= hashlib.sha256(i.encode("utf-8")).digest()[0] < hi)


HAND_IDS = ("p-anchor", "p-bargainer", "p-host", "p-peacekeeper", "p-steward", "p-wanderer")
PRESSING_IDS = ("p-controller", "p-freerider", "p-overasker")
# training distribution (the ranges the exam doc permits training to draw from; everything outside them is the exam's)
TRAIN_WEEKS = (104, 130, 156)
TRAIN_SHOCK_MULT = (0.5, 1.5)          # job loss, illness, move: multiples of the defaults
TRAIN_NEW_CONNECTION = (0.15, 0.30)
TRAIN_START = (-0.1, -0.05, 0.0, 0.05, 0.1)
TRAIN_SEEDS = range(100, 900)
HH_NORM = {"liberty": 6.0}             # liberty bits that count as 1.0 in the elite's mean-of-objectives pick (ASSUMED)
HH_LIBRARY_VARIANTS = ("baseline", "needs_duty", "share_duty", "no_pressure_wall", "no_pressure_sanctioned", "exit_half",
                       "veto_consent", "author_seed", "author_seed_nocontrol", "free_chaotic",
                       "author_seed_v2_bindable", "author_seed_v2_free_exit")   # patch library: trap and contact_free are controls built to fail
TERM_PREFIX = {"contribution": ("N1",), "use": ("N2",), "taking": ("N3",), "change": ("N4",), "exit": ("N5",),
               "stay": ("N6",), "requests": ("N7", "N8")}
SANCTION_KINDS = ("warn", "cap_halve", "suspend")


def held_out_by_rule(ids):
    """The exam's mechanical rule: held out iff the first byte of SHA-256(id) is below 48."""
    return sorted(i for i in ids if hashlib.sha256(i.encode("utf-8")).digest()[0] < 48)


_PERSONAS = {}


def hh_personas():
    """id -> persona for the hand, pressing and grid directories (all 41)."""
    if not _PERSONAS:
        for d in (_ROOT / "personas", _ROOT / "personas" / "pressing", _ROOT / "personas" / "grid"):
            _PERSONAS.update({p.id: p for p in _P.load_dir(d)})
    return _PERSONAS


def training_persona_ids():
    return sorted(i for i in hh_personas() if i not in DENYLIST and i not in _EXTRA_DENY)


def _pairing_pool():
    """All training pairings (a, b): ordered, a != b, neither denylisted. Split by a hash into `train` (selection) and `val` (never
    selected on, used for the overfitting gap)."""
    ids = training_persona_ids()
    hand = [i for i in ids if i in HAND_IDS]
    press = [i for i in ids if i in PRESSING_IDS]
    grid = [i for i in ids if i.startswith("g-")]
    out = []
    for a, b in _combinations(hand, 2):
        out.append((a, b, "hand"))
    for p in press:
        for o in hand + press + grid[::3]:
            if o != p:
                out += [(p, o, "press"), (o, p, "press")]
    for a, b in _combinations(grid, 2):
        out.append((a, b, "grid"))
    for g in grid:
        for h in hand:
            out.append((min(g, h), max(g, h), "gridhand"))
    seen, uniq = set(), []
    for a, b, c in out:
        if (a, b) not in seen:
            seen.add((a, b))
            uniq.append((a, b, c))
    return uniq


def pairing_split(a, b):
    """'val' for about a fifth of the pairings, by a hash of the pair (stable), else 'train'."""
    return "val" if hashlib.sha256(f"{a}|{b}".encode()).digest()[1] % 5 == 0 else "train"


@dataclass(frozen=True)
class HRun:
    a: str
    b: str
    seed: int
    weeks: int
    rates: tuple          # (job_loss, illness, move, new_connection)
    start: float


@dataclass(frozen=True)
class HContext:
    """One generation's evaluation setting: the runs every candidate is scored on (common random numbers)."""
    runs: tuple
    key: tuple


def _draw_run(rng, pool):
    a, b, cohort = pool[rng.randrange(len(pool))]
    d = _HD.DEFAULT
    return HRun(a, b, rng.choice(TRAIN_SEEDS), rng.choice(TRAIN_WEEKS),
                (round(d.job_loss_rate * rng.uniform(*TRAIN_SHOCK_MULT), 4), round(d.illness_rate * rng.uniform(*TRAIN_SHOCK_MULT), 4),
                 round(d.move_rate * rng.uniform(*TRAIN_SHOCK_MULT), 4), round(rng.uniform(*TRAIN_NEW_CONNECTION), 3)),
                rng.choice(TRAIN_START))


def make_context(seed, gen, n_runs, split="train", tag="sel", weeks=None):
    """Deterministic draw of n_runs from the `split` pairing pool under the training distribution. weeks=None draws the horizon from
    TRAIN_WEEKS (the run-1 behaviour, unchanged); an int fixes the episode length for every run (run 2: the lifetime horizon). The draw
    sequence is the same either way, so the pairings, seeds, rates and starts of a context do not depend on `weeks`."""
    pool = [p for p in _pairing_pool() if pairing_split(p[0], p[1]) == split]
    rng = random.Random(f"{seed}|{gen}|{tag}|{split}")
    runs = tuple(_draw_run(rng, pool) for _ in range(n_runs))
    if weeks is not None:
        assert weeks <= max(TRAIN_WEEKS), "training horizons never exceed the 156-week household horizon"
        runs = tuple(dataclasses.replace(r, weeks=weeks) for r in runs)
    return HContext(runs, (tag, split, seed, gen, n_runs) + ((weeks,) if weeks is not None else ()))


def run_key(spec):
    return tuple(c.to_yaml() for c in spec)


def _with_rates(rates, fn):
    """Run fn with the household world's module-level shock rates set (restored afterwards; one process = one run at a time)."""
    saved = dict(_H.SHOCK_RATES)
    _H.SHOCK_RATES.update(zip(("job_loss", "illness", "move", "new_connection"), rates))
    try:
        return fn()
    finally:
        _H.SHOCK_RATES.clear()
        _H.SHOCK_RATES.update(saved)


_LIB_MEMO = {}


def hh_run_summary(gate, hr, snapshots=_L.HH_SNAPSHOTS, k=_L.HH_K, plain_k=None, levers=None, powers=False):
    """Run one household (rule gate, HRun) and return the per-run scalars used everywhere (training and, with other settings, the exam)."""
    ps = hh_personas()
    d = _HD.DEFAULT
    cfg = dataclasses.replace(d, job_loss_rate=hr.rates[0], illness_rate=hr.rates[1], move_rate=hr.rates[2],
                              new_connection_rate=hr.rates[3], start=hr.start)
    def _go():
        if levers is None:
            return _L.household_run_liberty(gate, (ps[hr.a], ps[hr.b]), hr.seed, hr.weeks, snapshots, k, cfg=cfg, powers=powers)
        with _HD.use_levers(levers):       # pleasure levers (ADR 0016) for every world built inside the block
            return _L.household_run_liberty(gate, (ps[hr.a], ps[hr.b]), hr.seed, hr.weeks, snapshots, k, cfg=cfg, powers=powers)
    r = _with_rates(hr.rates, _go)
    out = r["run"].outcomes
    sc, hs = _O.score(out), _O.hedonic_summary(out)
    tr = r["run"].trace
    return {"pleasure": hs["pleasure"], "fail": bool(hs["fail"]), "cooperation": sc["cooperation"], "freedom": sc["freedom"],
            "liberty": r["liberty_min"], "bits": r["bits_min"], "s_non": hs["s_non"], "up": bool(hs["pairing_up"]),
            "down": any(c == "down" for c in hs["class"].values()),
            "left": sum(1 for x in "AB" if not out[-1]["partners"][x]["in"]),
            "n_open": r["n_open"],
            "events": {"veto": sum(1 for t in tr if t["action"] == "veto" and t["executed"]),
                       "leave_blocked": sum(1 for t in tr if t["action"] == "leave" and not t["allowed"]),
                       "take": sum(1 for t in tr if t["action"] == "take_shared" and t["executed"]),
                       "request": sum(1 for t in tr if t["action"] == "request" and t["executed"]),
                       "sanctioned": sum(sum(o["sanctioned"].values()) for o in out)}}


# ---------------------------------------------------------------- redundancy (household): logical only, partner cards

def _hh_actions(card):
    return (_H.PARTNER_ACTIONS + _H.EXTRA_ACTIONS + ("veto", "take_shared")) if card.aim == "any" else (card.aim,)


def hh_redundant_cards(cards) -> list:
    """Ids of must / must_not partner cards implied by the conjunction of the others over the bounded domain (or forbidding nothing).
    A card is redundant when, for every action it governs, no state and take exist that the other cards allow and it forbids
    (z3, bounded by household.BOUNDS). Permissions (`may`) add no constraint and are never flagged (a `may` can switch on a world mechanism, so
    removing one is not a logical question). Sanctions and glosses are ignored (ASSUMED). A solver 'unknown' counts as NOT redundant."""
    import z3
    cards = list(cards)
    out = []
    for i, c in enumerate(cards):
        if c.deontic == "may" or c.attribute != "partner":
            continue
        others = cards[:i] + cards[i + 1:]
        with _H.household_namespace():
            v = _H._compile.violation(c)
        redundant = True
        for act in _hh_actions(c):
            vs = _H.violations(others, act)
            allowed = _H._ok(vs)
            s = z3.Solver()
            s.set("timeout", 10000)
            s.add(_H._domain(act), _H._take_dom(act), allowed, v)
            if s.check() != z3.unsat:
                redundant = False
                break
        if redundant:
            out.append(c.id)
    return out


# ---------------------------------------------------------------- the filter: lint + proof checks + redundancy

def _lint_keys(cards):
    rs = _lint.RuleSet("cand", "household", list(cards), {}, "")
    res = _lint.lint_set(rs, K_DEFAULT)
    return {(f["check"], f["verdict"], tuple(f["cards"])) for f in res["findings"] if f["verdict"] in ("fail", "open")}


def hh_filter(cards, parent=None, k=K_DEFAULT):
    """The pre-run filter. -> (ok, [reasons]). Reasons: 'lint:<check>', 'proof:<check>', 'redundancy'.
    Inherited findings: a lint finding or redundant card that the PARENT already had (same check, verdict, cards) is not held against the
    child (the author's seed sets are fixed inputs, not mutants); anything new rejects. The proof checks are the household worlds' five
    (a to e) at bound k; 'open' rejects."""
    reasons = []
    inherited = _lint_keys(parent) if parent is not None else set()
    for chk, verdict, ids in sorted(_lint_keys(cards) - inherited):
        reasons.append(f"lint:{chk}")
    for c in _H.check_spec(list(cards), k):
        if c["verdict"] != "pass":
            if parent is None or c["check"] not in {x["check"] for x in _H.check_spec(list(parent), k) if x["verdict"] != "pass"}:
                reasons.append(f"proof:{c['check']}")
    old = set(hh_redundant_cards(parent)) if parent is not None else set()
    if set(hh_redundant_cards(cards)) - old:
        reasons.append("redundancy")
    return (not reasons), reasons


# ---------------------------------------------------------------- card construction and mutation operators

def _hgloss(d):
    with _H.household_namespace():
        conds = " and ".join(_cond_en_h(c) for c in d["conditions"])
    who, aim = d["attribute"], d["aim"].replace("_", " ")
    tail = ""
    if d.get("or_else"):
        tail = f" Breaking it brings a {d['or_else']['kind'].replace('_', ' ')} for {d['or_else']['duration_months']} month(s)."
    if d["deontic"] == "must_not":
        return (f"When {conds}, a {who} must not {aim}." if conds else f"A {who} must never {aim}.") + tail
    if d["deontic"] == "must":
        return f"A {who} must {aim}" + (f" only when {conds}." if conds else " in every case.") + tail
    return f"A {who} may {aim}" + (f" when {conds}." if conds else " in every case.")


def _cond_en_h(c):
    from .english import _cond_en
    return _cond_en(c)


def _hrebuild(card, op, **changes):
    d = {"id": card.id, "attribute": card.attribute, "deontic": card.deontic, "aim": card.aim,
         "conditions": [dict(c) for c in card.conditions], "or_else": card.or_else, "gloss": card.gloss, "source": card.source}
    d.update(changes)
    d["gloss"] = _hgloss(d)
    d["source"] = f"evolved ({op}) from {card.id}"
    return make_card(d)


def _hreplace(spec, i, card):
    return tuple(card if j == i else c for j, c in enumerate(spec))


def _bound_range(expr):
    return _H.BOUNDS.get(expr, (0, 100))


def _hop_bound(spec, world, rng, summary=None):
    slots = [(i, j) for i, c in enumerate(spec) if c.deontic in ("must_not", "must") for j, cond in enumerate(c.conditions)
             if cond["expr"] in _H.BOUNDS and _bound_range(cond["expr"])[1] - _bound_range(cond["expr"])[0] > 1]
    if not slots:
        return None
    i, j = rng.choice(slots)
    card, cond = spec[i], spec[i].conditions[j]
    lo, hi = _bound_range(cond["expr"])
    step = max(1, round((hi - lo) * rng.choice((0.05, 0.1, 0.25))))
    value = max(lo, min(hi, cond["value"] + rng.choice((1, -1)) * step))
    if value == cond["value"]:
        return None
    conds = [dict(c) for c in card.conditions]
    conds[j]["value"] = value
    return _hreplace(spec, i, _hrebuild(card, "bound", conditions=conds))


def _hop_flip(spec, world, rng, summary=None):
    slots = [i for i, c in enumerate(spec) if c.deontic in ("must_not", "must")]
    if not slots:
        return None
    i = rng.choice(slots)
    card = spec[i]
    new = {"must_not": ("may", "must"), "must": ("must_not", "may")}[card.deontic]
    return _hreplace(spec, i, _hrebuild(card, "flip", deontic=rng.choice(new), or_else=None if card.deontic != "must_not" else card.or_else))


def _hop_add_condition(spec, world, rng, summary=None):
    slots = [i for i, c in enumerate(spec) if c.deontic in ("must_not", "must")]
    if not slots:
        return None
    i = rng.choice(slots)
    card = spec[i]
    names = [n for n in _H.STATE_VARS if n not in {c["expr"] for c in card.conditions}]
    if card.aim == "leave":
        names.append("take")
    expr = rng.choice(names)
    lo, hi = _bound_range(expr)
    cond = {"expr": expr, "op": rng.choice(("gt", "ge", "lt", "le")) if hi - lo > 1 else "eq", "value": rng.randint(lo, hi)}
    return _hreplace(spec, i, _hrebuild(card, "add_condition", conditions=[dict(c) for c in card.conditions] + [cond]))


def _hop_drop(spec, world, rng, summary=None):
    if len(spec) < 2:
        return None
    i = rng.randrange(len(spec))
    return tuple(c for j, c in enumerate(spec) if j != i)


def _hop_sanction(spec, world, rng, summary=None):
    slots = [i for i, c in enumerate(spec) if c.deontic == "must_not"]
    if not slots:
        return None
    i = rng.choice(slots)
    card = spec[i]
    if card.or_else and rng.random() < 0.4:
        s = None
    else:
        s = {"kind": rng.choice(SANCTION_KINDS), "duration_months": rng.randint(1, 3), "sanctioner": "household"}
        if s == card.or_else:
            return None
    return _hreplace(spec, i, _hrebuild(card, "sanction", or_else=s))


def _bundle_default():
    b = dict(_NG.IMPOSED)
    b["fine"] = "none"
    return b


def _term_cards(term, value):
    b = _bundle_default()
    b[term] = value
    if term == "requests" and value == "none":
        return []
    cards = _NG.compile_bundle(b, ["imposed"])
    pre = TERM_PREFIX[term]
    got = [c for c in cards if c.id.startswith(pre) and not c.id.startswith("N8")]
    if term == "stay" and not value:
        return []
    return got


def _hop_add_term(spec, world, rng, summary=None):
    """Swap one negotiated-pot term (docs/decisions/0013): drop the spec's cards for that term and add the term's cards for another value."""
    term = rng.choice(("contribution", "use", "taking", "exit", "stay", "requests"))
    value = rng.choice([v for v in _NG.TERMS[term]])
    new = _term_cards(term, value)
    pre = TERM_PREFIX[term]
    kept = tuple(c for c in spec if not c.id.startswith(pre))
    if not new and len(kept) == len(spec):
        return None
    out = kept + tuple(new)
    return out if run_key(out) != run_key(spec) else None


_LIB = []


def hh_library():
    if not _LIB:
        seen = set()
        for v in HH_LIBRARY_VARIANTS:
            for c in _H.load_variant(v):
                sig = (c.attribute, c.deontic, c.aim, tuple(map(lambda x: tuple(sorted(x.items())), c.conditions)))
                if sig not in seen:
                    seen.add(sig)
                    _LIB.append(c)
    return list(_LIB)


def _hop_patch(spec, world, rng, summary=None):
    """Add a library card (hand-written cards from the existing rule sets; never trap or contact_free). The scripted patcher sees ONLY the
    parent's run-event summary (counts of what happened in its runs) and the cards, never an objective or the exam."""
    have = {c.id for c in spec}
    have_sig = {(c.deontic, c.aim, tuple(map(lambda x: tuple(sorted(x.items())), c.conditions))) for c in spec}
    lib = [c for c in hh_library() if c.id not in have and (c.deontic, c.aim, tuple(map(lambda x: tuple(sorted(x.items())), c.conditions))) not in have_sig]
    if not lib:
        return None
    ev = summary or {}
    want = []
    if ev.get("veto"):
        want.append("veto")
    if ev.get("leave_blocked"):
        want.append("leave")
    if ev.get("take"):
        want.append("take_shared")
    if ev.get("request"):
        want += ["request", "refuse_request"]
    w = [3.0 if c.aim in want else 1.0 for c in lib]
    return spec + (rng.choices(lib, w)[0],)


HOPS = ("bound", "flip", "add_condition", "drop", "patch", "sanction", "add_term")
HWEIGHTS = (22, 8, 12, 10, 22, 8, 18)
HOPERATORS = dict(zip(HOPS, (_hop_bound, _hop_flip, _hop_add_condition, _hop_drop, _hop_patch, _hop_sanction, _hop_add_term)))


class HouseholdEvolveWorld:
    """World adapter for the household evolution loop (evolve.evolve_household). Not the fishery's Protocol: runs are persona pairings under
    drawn conditions (an HContext), scores are the four objectives plus reporting columns."""
    name = "household"
    objectives = ("pleasure", "no_fail", "liberty", "cooperation")
    YIELD_FLOOR = 0.0

    def __init__(self, levers=None, weeks=None, powers=False):
        """levers: a hedonic.LeverConfig for every run (None = off, the run-1 behaviour); weeks: a fixed episode length (None = the
        context's own); powers: liberty also counts normative powers (ADR 0014 amendment). Defaults reproduce run 1."""
        self._gates = {}
        self.levers, self.weeks, self.powers = levers, weeks, powers

    def load_spec(self, name):
        return tuple(_H.load_variant(name))

    def gate(self, spec):
        key = run_key(spec)
        if key not in self._gates:
            self._gates[key] = _H.PyGate(list(spec))
        return self._gates[key]

    def check(self, spec, parent=None):
        return hh_filter(spec, parent)

    def mutate(self, spec, rng, summary=None):
        name = rng.choices(HOPS, HWEIGHTS)[0]
        return HOPERATORS[name](spec, self, rng, summary), name

    def score_runs(self, spec, ctx):
        """-> (scores dict, event summary). Objectives: pleasure (mean over runs), no_fail (share of runs with no non-offsettable-suffering
        failure), liberty (mean over runs of the lower partner's liberty v2 in bits), cooperation. Reporting: freedom, bits, up, down, left."""
        gate = self.gate(spec)
        rows = [hh_run_summary(gate, hr, levers=self.levers, powers=self.powers) for hr in ctx.runs]
        m = lambda k: sum(float(r[k]) for r in rows if r[k] is not None) / max(1, sum(1 for r in rows if r[k] is not None))
        scores = {"pleasure": m("pleasure"), "no_fail": 1.0 - m("fail"), "liberty": m("liberty"), "cooperation": m("cooperation"),
                  "freedom": m("freedom"), "bits": m("bits"), "up": m("up"), "down": m("down"), "left": m("left")}
        ev = {k: sum(r["events"][k] for r in rows) for k in rows[0]["events"]}
        return scores, ev

    def norm_mean(self, scores):
        return (scores["pleasure"] + scores["no_fail"] + min(1.0, scores["liberty"] / HH_NORM["liberty"]) + scores["cooperation"]) / 4


# ---------------------------------------------------------------- core protections and plain-English rendering (reporting only)

def _ever_allowed(cards, action, take=0):
    """z3: is there a state (inside the bounds) where `action` (at `take`) violates no card? Returns (always_allowed, never_allowed)."""
    import z3
    vs = _H.violations(list(cards), action)
    out = {}
    for name, f in (("blocked_somewhere", z3.Or(*vs.values()) if vs else z3.BoolVal(False)),
                    ("allowed_somewhere", _H._ok(vs))):
        s = z3.Solver()
        s.set("timeout", 10000)
        s.add(_H._domain(action), Z3_TAKE(take), f)
        out[name] = s.check() == z3.sat
    return (not out["blocked_somewhere"], not out["allowed_somewhere"])


def Z3_TAKE(take):
    return _H.Z["take"] == take


def hh_forbids_veto(cards) -> bool:
    """Core protection 1: `veto` is violated in EVERY state (some must_not veto card covers the whole domain, or the cards jointly do)."""
    return _ever_allowed(cards, "veto")[1]


def hh_free_exit(cards) -> bool:
    """Core protection 2: a leave carrying the equal split (take 50) violates no card in ANY state (never blocked, now)."""
    return _ever_allowed(cards, "leave", 50)[0]


def hh_protections(cards) -> dict:
    return {"no_veto": hh_forbids_veto(cards), "free_exit": hh_free_exit(cards)}


def card_plain_english(card) -> str:
    """One line: the gloss, plus a sanction note if the card carries one."""
    s = card.gloss.strip()
    if card.or_else and "Breaking it" not in s:
        s += f" Breaking it brings a {card.or_else['kind'].replace('_', ' ')} for {card.or_else['duration_months']} month(s)."
    return s


def spec_diff_plain(base, other) -> list:
    """Plain-English differences of rule set `other` against `base`: cards added, removed, or changed (same id, different rule)."""
    b = {c.id: c for c in base}
    o = {c.id: c for c in other}
    out = []
    for i in sorted(o.keys() - b.keys()):
        out.append(f"ADDED {i}: {card_plain_english(o[i])}")
    for i in sorted(b.keys() - o.keys()):
        out.append(f"REMOVED {i}: {card_plain_english(b[i])}")
    for i in sorted(o.keys() & b.keys()):
        if o[i].to_yaml() != b[i].to_yaml() and (o[i].deontic, o[i].aim, o[i].conditions, o[i].or_else) != (b[i].deontic, b[i].aim, b[i].conditions, b[i].or_else):
            out.append(f"CHANGED {i}: was \"{card_plain_english(b[i])}\" now \"{card_plain_english(o[i])}\"")
    return out
