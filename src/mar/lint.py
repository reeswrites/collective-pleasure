"""Rule-set lint: static, bounded checks on every rule set in rules/ (and on a sample of negotiated agreements).

Checks (letters follow the author's request of 2026-11-10):
  a  no reachable state where some role has no legal move (partner, friend; fisher; player)
  b  household worlds: no state where a partner has no legal exit within k (an exit is a legal `leave` at ANY take 0..100, now
     or after waiting up to k months, with or without first clearing standing requests by a legal refuse_request).
     Advisory b2 (a note, never a failure): the same with a meaningful exit, take >= 25.
  c  no contradicting cards: a must and a must_not on the same aim that cannot both be met in some state; and a `may` that
     some must_not wall makes wholly unavailable (every take blocked) in a state where the may applies, unless the may's gloss
     declares an exception
  d  every card has a gloss and a source (non-empty, not a placeholder)
  e  gloss mentions an exception (unless, except, ...) that the formal conditions cannot carry (conditions are AND-ed: a card
     with no conditions cannot hold an exception; a `must` cannot hold one at all). One condition is listed as a note to read.
  f  cards that reference an action (aim), actor (attribute) or state variable the world does not have
  x  sanctions finite and a repair path exists (the solver checks already in the worlds)

A finding is waived only when a card it names declares a field `known_flaw: <reason>` in its YAML. The status of a rule set is
fail (an unwaived fail), open (an unwaived open: the bound or the solver gave up, never "safe"), or pass (with the waived
findings listed). Every verdict is bounded by `bound_text`. Reachability is over-approximated by the variable bounds, so a fail
can name a state the world never reaches; a pass is a proof inside the bound.
No network, no model calls.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml
import z3

from . import english as E
from . import patch_check as PC
from .cards import load_cards, make_card
from .worlds import household as H

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "rules"
K_DEFAULT = 3
EXCEPTION_RE = re.compile(r"\b(unless|except|excepting|apart from|other than|save for|barring)\b", re.I)
MAY_EXCEPTION_RE = re.compile(r"\b(unless|except|only when|only if|but not|subject to|while|apart from|other than)\b", re.I)
PLACEHOLDER_RE = re.compile(r"^\W*(todo|tbd|xxx|fixme|n/?a|\?+|none)\W*$", re.I)

# world vocabulary: actors, aims, state variables
WORLDS = {
    "fishery": {"attributes": ("fisher",), "aims": ("harvest",), "vars": ("pool", "month_total", "catch"), "kind": "fishery"},
    "household": {"attributes": ("partner", "friend"),
                  "aims": H.PARTNER_ACTIONS + H.EXTRA_ACTIONS + ("veto", "take_shared", "any"),
                  "vars": H.VAR_NAMES, "kind": "household"},
    "vpgg": {"attributes": ("player",), "aims": ("abstain", "join", "contribute"), "vars": None, "kind": "indicator"},
    "bargaining": {"attributes": ("player",), "aims": ("exit", "continue", "agree"), "vars": None, "kind": "indicator"},
}
OPS = {"gt": lambda a, b: a > b, "ge": lambda a, b: a >= b, "lt": lambda a, b: a < b, "le": lambda a, b: a <= b,
       "eq": lambda a, b: a == b}


@dataclass
class RuleSet:
    name: str
    world: str
    cards: list
    flaws: dict = field(default_factory=dict)     # card id -> known_flaw reason
    origin: str = ""
    load_error: str = ""


def _raw_flaws(directory) -> dict:
    out = {}
    for p in sorted(Path(directory).glob("*.yaml")):
        d = yaml.safe_load(p.read_text())
        if isinstance(d, dict) and d.get("known_flaw"):
            out[d["id"]] = str(d["known_flaw"]).strip()
    return out


def _load_yaml_set(path, world, name=None) -> RuleSet:
    path = Path(path)
    name = name or str(path.relative_to(RULES))
    try:
        return RuleSet(name, world, load_cards(path), _raw_flaws(path), str(path))
    except Exception as e:                                   # a card that cannot even load is itself a finding
        return RuleSet(name, world, [], {}, str(path), load_error=f"{type(e).__name__}: {e}")


def discover(root=RULES) -> list:
    """Every rule set under rules/: leaf directories of YAML cards, the English fishery set, and the English patch over it."""
    root = Path(root)
    sets = []
    for d in sorted(p for p in root.rglob("*") if p.is_dir()):
        if d.name == "patch" or not list(d.glob("*.yaml")):
            continue
        world = d.relative_to(root).parts[0]
        if world in WORLDS:
            sets.append(_load_yaml_set(d, world))
    en = root / "fishery-en"
    if en.is_dir():
        try:
            base = E.load_english(en)
            sets.append(RuleSet("fishery-en", "fishery", base, {}, str(en)))
            patch = E.load_english(en / "patch")
            sets.append(RuleSet("fishery-en+patch", "fishery", base + patch, {}, str(en / "patch")))
        except Exception as e:
            sets.append(RuleSet("fishery-en", "fishery", [], {}, str(en), load_error=f"{type(e).__name__}: {e}"))
    return sets


def negotiated_sets(sample=40, variant="author_seed_v2_bindable", floor=26) -> list:
    """A deterministic sample of compiled negotiated agreements (base rules + compiled bundle + exit floor), evenly spaced over
    the 729-bundle menu, always including the first and last (all-defaults and all-extremes)."""
    from . import negotiation as N
    base = N.base_cards(variant)
    menu = N.menu_of(base)
    blist = N.bundles(menu["stay"], menu["requests"])
    n = len(blist)
    idx = sorted({round(i * (n - 1) / max(1, sample - 1)) for i in range(sample)})
    out = []
    for i in idx:
        b = blist[i]
        cards = base + N.compile_bundle(b, ["p-a", "p-b"]) + N.floor_cards(floor)
        out.append(RuleSet("negotiated/" + "-".join(str(b[t]) for t in N.TERM_NAMES), "household", cards, {},
                           f"negotiation.compile_bundle on {variant}, bundle #{i} of {n}"))
    return out


# ---- helpers ---------------------------------------------------------------------------------------------

def _finding(check, verdict, cards, detail):
    return {"check": check, "verdict": verdict, "cards": sorted(set(cards)), "detail": detail}


def _vars_in(expr):
    return set(re.findall(r"[A-Za-z_]\w*", expr))


def bound_text(world, k=K_DEFAULT):
    if world == "fishery":
        return PC.bound_text(k)
    if world == "household":
        return H.bound_text(k) + "; exit = legal leave at any take now or within k months of waiting (standing requests clearable by a legal refuse_request)"
    return "action-level: each card read over the indicator of its own aim (no state variables)"


# ---- d, e, f: static --------------------------------------------------------------------------------------

def check_fields(rs):
    bad = []
    for c in rs.cards:
        g, s = str(c.gloss).strip(), str(c.source).strip()
        if len(g) < 8 or PLACEHOLDER_RE.match(g) or len(s) < 8 or PLACEHOLDER_RE.match(s):
            bad.append(c.id)
    if bad:
        return [_finding("d", "fail", bad, "gloss or source missing, empty or a placeholder")]
    return []


def check_gloss_vs_formal(rs):
    out = []
    for c in rs.cards:
        if not EXCEPTION_RE.search(c.gloss):
            continue
        n = len(c.conditions)
        if c.deontic == "must":
            out.append(_finding("e", "fail", [c.id], "the gloss states an exception but conditions of a `must` are AND-ed (all must hold "
                                "to comply): no formal field can carry an exception"))
        elif n == 0:
            out.append(_finding("e", "fail", [c.id], "the gloss states an exception ('" + EXCEPTION_RE.search(c.gloss).group(0)
                                + "') but the card has no conditions: the exception is not in the formal fields"))
        elif n == 1:
            out.append(_finding("e", "note", [c.id], "the gloss states an exception and the card has one condition; read it to confirm the "
                                "condition is the exception"))
    return out


def check_vocabulary(rs):
    w = WORLDS[rs.world]
    out = []
    for c in rs.cards:
        if c.attribute not in w["attributes"]:
            out.append(_finding("f", "fail", [c.id], f"actor `{c.attribute}` is not in this world ({', '.join(w['attributes'])})"))
        if c.aim not in w["aims"]:
            out.append(_finding("f", "fail", [c.id], f"aim `{c.aim}` is not an action this world has ({', '.join(w['aims'])})"))
        allowed = set(w["vars"]) if w["vars"] is not None else set(w["aims"])
        bad = sorted({v for p in c.conditions for v in _vars_in(p["expr"]) if not v.isdigit() and v not in allowed})
        if bad:
            out.append(_finding("f", "fail", [c.id], f"condition variable(s) {bad} are not in this world"))
    return out


# ---- household: a, b, c ------------------------------------------------------------------------------------

def _hh_deadlock(rs):
    out = []
    p = H.check_deadlock(rs.cards)
    if p[0] != "pass":
        out.append(_finding("a", p[0], p[1], "partner: " + p[2]))
    if any(c.attribute == "friend" for c in rs.cards):
        vs = {a: H.violations(rs.cards, a, "friend") for a in H.FRIEND_ACTIONS}
        verdict, wit = H._solve(H._blocked(vs, H.FRIEND_ACTIONS))
        if verdict != "unsat":
            out.append(_finding("a", "fail" if verdict == "sat" else "open",
                                [c.id for c in rs.cards if c.attribute == "friend"], f"friend: no permitted action at state {wit}"))
    return out


def _exit_formula(cards, k, min_take=0, witness=None):
    """Formula: some state (or the given witness) where no leave with take >= min_take is legal now or within k months, even after
    a legal refuse_request clears standing requests."""
    vl, vr = H.violations(cards, "leave"), H.violations(cards, "refuse_request")
    Z = H.Z
    clear = [(Z["no_contact_request"], z3.IntVal(0)), (Z["stay_home_request"], z3.IntVal(0))]

    def leave_ok(t, cleared):
        sub = [(Z["months_in"], Z["months_in"] + t)] + (clear if cleared else [])
        sh = {cid: z3.substitute(v, *sub) for cid, v in vl.items()}
        return z3.Not(z3.ForAll([Z["take"]], z3.Implies(H._take_dom("leave", min_take), z3.Not(H._ok(sh)))))

    parts = []
    for t in range(k + 1):
        parts.append(z3.Not(z3.Or(leave_ok(t, False), z3.And(H._ok(vr), leave_ok(t, True)))))
    f = z3.And(*parts)
    if witness is not None:
        f = z3.substitute(f, *[(Z[n], z3.IntVal(witness[n])) for n in H.STATE_VARS])
    return f


def _exit_core(cards, k, wit, min_take=0):
    cur = list(cards)
    for c in list(cur):
        trial = [x for x in cur if x.id != c.id]
        s = z3.Solver()
        s.set("timeout", 10000)
        s.add(_exit_formula(trial, k, min_take, wit))
        if s.check() == z3.sat:
            cur = trial
    return [c.id for c in cur if c.aim in ("leave", "refuse_request", "any")]


def _hh_exit(rs, k):
    out = []
    for name, min_take, sev in (("b", 0, "fail"), ("b2", H.MIN_EXIT_TAKE, "note")):
        with_ns = H._solve(_exit_formula(rs.cards, k, min_take))
        verdict, wit = with_ns
        if verdict == "sat":
            core = _exit_core(rs.cards, k, wit, min_take)
            what = "no legal exit (leave at any take)" if min_take == 0 else f"no meaningful exit (leave carrying >= {min_take}%)"
            out.append(_finding(name, sev, core, f"{what} within k={k} at state {wit}"))
        elif verdict == "unknown":
            out.append(_finding(name, "open" if sev == "fail" else "note", [], "solver gave up"))
    return out


def _may_blocked(rs):
    """A `may` card whose action is wholly blocked (every take) by other HARD walls (a violated card with no or_else; a card with
    an or_else is soft in the household worlds, rules/README.md) in some state where the may applies."""
    out = []
    Z = H.Z
    with H.household_namespace():
        for m in (c for c in rs.cards if c.deontic == "may" and c.aim in H.PARTNER_ACTIONS):
            if MAY_EXCEPTION_RE.search(m.gloss):
                continue
            vs = {c.id: v for c in rs.cards if c.id != m.id and c.deontic != "may" and c.attribute == m.attribute
                  and c.or_else is None and c.aim in (m.aim, "any") and (v := H._compile.violation(c)) is not None}
            if not vs:
                continue
            applies = H._compile.conditions_expr(m)
            f = z3.And(z3.Exists([Z["take"]], z3.And(H._take_dom(m.aim), applies)),
                       z3.ForAll([Z["take"]], z3.Implies(z3.And(H._take_dom(m.aim), applies), z3.Not(H._ok(vs)))))
            verdict, wit = H._solve(f)
            if verdict == "sat":
                blockers = [cid for cid, v in vs.items()
                            if z3.is_true(z3.simplify(z3.substitute(v, *[(Z[n], z3.IntVal(wit[n])) for n in H.STATE_VARS],
                                                                    (Z["take"], z3.IntVal(0)))))] or sorted(vs)
                out.append(_finding("c", "fail", [m.id] + blockers,
                                    f"`may {m.aim}` ({m.id}) is wholly blocked by {sorted(blockers)} at state {wit}, and the may's gloss "
                                    f"declares no exception"))
            elif verdict == "unknown":
                out.append(_finding("c", "open", [m.id], "solver gave up on may-versus-must_not"))
    return out


def _household_checks(rs, k):
    out = _hh_deadlock(rs) + _hh_exit(rs, k)
    v = H.check_conflict(rs.cards)
    if v[0] != "pass":
        out.append(_finding("c", v[0], v[1], v[2]))
    out += _may_blocked(rs)
    spec = {c["check"]: c for c in H.check_spec(rs.cards, k)}
    for key in ("c_bounded_sanctions", "d_repair_path"):
        if spec[key]["verdict"] != "pass":
            out.append(_finding("x", spec[key]["verdict"], spec[key]["cards"], spec[key]["detail"]))
    return out


# ---- fishery ----------------------------------------------------------------------------------------------------

def _fishery_checks(rs, k):
    out = []
    for c in PC.check_spec(rs.cards, k):
        if c["verdict"] == "pass":
            continue
        letter = {"a_no_conflict": "c", "b_no_deadlock": "a"}.get(c["check"], "x")
        out.append(_finding(letter, c["verdict"], c["cards"], c["detail"]))
    return out


# ---- action-level worlds (vpgg, bargaining) -------------------------------------------------------------------------------

def _indicator_checks(rs, k):
    """Each card is read over the indicator of its own aim (1 = the action is taken). A must_not whose conditions all hold at
    indicator 1 bans the action outright. (a): some action is not banned. (c): a must on a banned aim; a `may` on a banned aim."""
    w = WORLDS[rs.world]
    banned = {}
    for c in rs.cards:
        if c.deontic != "must_not":
            continue
        ok = True
        for p in c.conditions:
            if _vars_in(p["expr"]) != {c.aim} or not OPS[p["op"]](1, p["value"]):
                ok = False
        if ok:
            banned.setdefault(c.aim, []).append(c.id)
    out = []
    if all(a in banned for a in w["aims"]):
        out.append(_finding("a", "fail", [i for ids in banned.values() for i in ids], "every action of this world is banned outright"))
    for c in rs.cards:
        if c.aim in banned and c.deontic in ("may", "must") and c.id not in banned[c.aim]:
            if c.deontic == "must" or not MAY_EXCEPTION_RE.search(c.gloss):
                out.append(_finding("c", "fail", [c.id] + banned[c.aim], f"`{c.deontic} {c.aim}` against an outright ban {banned[c.aim]}"))
    return out


# ---- driver -------------------------------------------------------------------------------------------------------------

def lint_set(rs, k=K_DEFAULT) -> dict:
    """-> {name, world, k, bound, status, findings (each with waived reason or None), waived, n_cards}."""
    findings = []
    if rs.load_error:
        findings.append(_finding("d", "fail", [], "rule set does not load: " + rs.load_error))
    else:
        findings += check_fields(rs) + check_gloss_vs_formal(rs) + check_vocabulary(rs)
        kind = WORLDS[rs.world]["kind"]
        try:
            findings += {"household": _household_checks, "fishery": _fishery_checks, "indicator": _indicator_checks}[kind](rs, k)
        except Exception as e:      # a lint that crashes on a rule set is reported, not hidden
            findings.append(_finding("a", "open", [], f"lint crashed on this set: {type(e).__name__}: {e}"))
    for f in findings:
        reasons = [rs.flaws[i] for i in f["cards"] if i in rs.flaws]
        f["waived"] = "; ".join(reasons) if (reasons and f["verdict"] == "fail") else None
    live = [f for f in findings if f["verdict"] in ("fail", "open") and not f["waived"]]
    status = "fail" if any(f["verdict"] == "fail" for f in live) else ("open" if live else "pass")
    return {"name": rs.name, "world": rs.world, "k": k, "bound": bound_text(rs.world, k), "status": status,
            "findings": findings, "waived": [f for f in findings if f["waived"]], "n_cards": len(rs.cards)}


def lint_all(root=RULES, k=K_DEFAULT, negotiated=40) -> list:
    sets = discover(root)
    if negotiated:
        sets += negotiated_sets(negotiated)
    return [lint_set(rs, k) for rs in sets]


def gate_ok(names, root=RULES, k=K_DEFAULT) -> tuple:
    """For the live runner: -> (ok, report lines). Refuse when any named rule set under rules/household/ladder fails lint without
    known_flaw. `names` are ladder directory names such as L1_exit_lock."""
    lines, ok = [], True
    for n in names:
        res = lint_set(_load_yaml_set(Path(root) / "household" / "ladder" / n, "household", f"household/ladder/{n}"), k)
        lines.append(f"{res['name']}: {res['status']}" + (f" (waived: {[f['cards'] for f in res['waived']]})" if res["waived"] else ""))
        ok = ok and res["status"] == "pass"
    return ok, lines


def summary_table(results) -> str:
    out = [f"{'rule set':<52}{'world':<11}{'k':>2}  {'status':<6} findings (unwaived fail/open | waived | notes)"]
    fam = {}
    rows = []
    for r in results:
        if r["name"].startswith("negotiated/"):
            fam.setdefault("negotiated/*", []).append(r)
        else:
            rows.append((r["name"], r))
    for name, rs in fam.items():
        worst = "fail" if any(r["status"] == "fail" for r in rs) else ("open" if any(r["status"] == "open" for r in rs) else "pass")
        rows.append((f"negotiated/* ({len(rs)} agreements)", {"world": "household", "k": rs[0]["k"], "status": worst,
                                                              "findings": [f for r in rs for f in r["findings"]],
                                                              "waived": [f for r in rs for f in r["waived"]]}))
    for name, r in rows:
        live = [f for f in r["findings"] if f["verdict"] in ("fail", "open") and not f["waived"]]
        notes = [f for f in r["findings"] if f["verdict"] == "note"]
        out.append(f"{name:<52}{r['world']:<11}{r['k']:>2}  {r['status']:<6} {len(live)} | {len(r['waived'])} | {len(notes)}")
    return "\n".join(out)


def _norm(detail):
    return re.sub(r"\{[^}]*\}", "{state}", detail)


def markdown(results, k=K_DEFAULT) -> str:
    """The findings document: per-set status table, then every distinct finding with the sets it appears in."""
    out = ["# Rule-set lint", "", "Generated by `uv run python scripts/lint_rules.py --md docs/results/lint.md` (no model calls). "
           f"Bound k={k}; verdicts are pass / fail / open; `open` is never safe; a fail is waived only by a `known_flaw` field on a "
           "card it names. Checks: a no legal move, b no legal exit within k, c contradiction, d gloss and source, e gloss exception "
           "absent from the formal fields, f references an action/actor/variable the world lacks, x sanctions. b2 (a meaningful exit, "
           "take 25 or more) is an advisory note and never fails a set.", "",
           "## Status per rule set", "", "| rule set | world | k | status | unwaived fail/open | waived | notes |", "|---|---|---|---|---|---|---|"]
    fam = [r for r in results if r["name"].startswith("negotiated/")]
    for r in [r for r in results if not r["name"].startswith("negotiated/")]:
        live = [f for f in r["findings"] if f["verdict"] in ("fail", "open") and not f["waived"]]
        out.append(f"| {r['name']} | {r['world']} | {r['k']} | {r['status']} | {len(live)} | {len(r['waived'])} | "
                   f"{sum(f['verdict'] == 'note' for f in r['findings'])} |")
    if fam:
        nfail = sum(r["status"] == "fail" for r in fam)
        out.append(f"| negotiated/* (sample of {len(fam)} compiled agreements) | household | {k} | "
                   f"{'fail' if nfail else 'pass'} ({nfail} of {len(fam)} fail) | | | |")
    groups = {}
    for r in results:
        for f in r["findings"]:
            if f["verdict"] == "pass":
                continue
            key = (f["check"], f["verdict"], tuple(f["cards"]), _norm(f["detail"]), f["waived"])
            groups.setdefault(key, []).append(r["name"])
    out += ["", "## Every finding", "", "Findings that repeat across the negotiated sample are listed once with a count.", ""]
    for (check, verdict, cards, detail, waived), names in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][2])):
        neg = [n for n in names if n.startswith("negotiated/")]
        plain = [n for n in names if not n.startswith("negotiated/")]
        where = ", ".join(plain) + (f"{', ' if plain else ''}{len(neg)} negotiated agreements" if neg else "")
        out.append(f"- **{check} {verdict}{' (waived by known_flaw)' if waived else ''}** `{', '.join(cards) or '-'}` in {where}: {detail}")
    return "\n".join(out) + "\n" + READING


READING = """
## Reading of the findings (2026-11-10)

No finding was a clear bug, so no rule card was changed other than declaring L5's defect. Each is listed, not fixed.

- **L5 (`household/ladder/L5_gift_pool`)**: b fails as the card-only review found (pooled above 50 with the other partner in: LD5a needs
  take 0, LD5b needs take 100). Both cards now carry `known_flaw`, so the set is `pass` with the finding waived. It is a historical
  fixture of the live ladder run. **L5b passes**: take 0 is the one legal exit above stake 50. Its advisory b2 note says that exit
  carries nothing, which is the intended design of the repaired pair, not a flaw.
- **L1 to L4 pass** (a no-move, b exit, c contradiction): the L1 to L3 exit locks are escapable by a legal `refuse_request`, which is
  why b passes; they are seams of the "harm without a victim-visible block" kind, not dead ends.
- **`author_seed_v2_*` (and every negotiated agreement built on them)**: e fails on R3a, R3a2 and R5: the gloss says "unless they
  negotiate that" or "unless they earlier chose to bind themselves", and the card has no conditions. rules/README.md documents these
  exceptions as mechanisms the world enforces outside the card (negotiated terms; commitments R5b, N6, N7). The lint finding is real
  (gloss and formal fields disagree) but it is the already-documented one; fixing it means changing the card format or the glosses,
  an author decision. N6-stay-52 has the same shape.
- **Negotiated agreements**: f fails on N4 (`amend`): the world has no amend action; README says change rules are "declared only".
  b2 notes on N5a-exit-forfeit mean a forfeit exit carries nothing from the pot; the exit floor (FLOOR-exit-floor, enforced by
  `WeeklyWorld.carry_out`, not by a card) is what gives the leaver 26 units, so this note is expected.
- **`fishery-en+patch`**: C1 is the deliberately conflicting patch fixture ("V2 fixture (deliberately conflicting patch)"); the
  English `.txt` format has no field for `known_flaw`, so it cannot declare itself and the set fails. Declaring it needs the author to
  choose a format (a sidecar file or an English suffix).
- **Not checked**: reachability is over-approximated by the variable bounds (a fail may name a state the world never reaches); the
  weekly world's mechanisms that are not cards (README table) are outside every check; `or_else` sanctions are treated as soft walls
  for the may check and as walls by the deadlock and exit checks (the worlds' own convention); the friend role has no cards in any
  set, so its check passes trivially.
"""

