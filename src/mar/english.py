"""English-like surface for ADICO cards (V2b, SLEEC style). A view of the card, not a new semantics.

render(card) -> one sentence; parse(text) -> card. Strict controlled grammar, one sentence per rule:

  rule     := ID ". " body "." " (Gloss: " TEXT ")" " (Source: " TEXT ")"
  body     := must_not | must | may      each followed by an optional sanction
  must_not := ("When " conds | "In every case") ", " ART ATTR " must not " AIM
  must     := ART ATTR " must " AIM (" only when " conds | " in every case")
  may      := ART ATTR " may " AIM (" when " conds | " in every case")
  sanction := ", and " ART ATTR " who breaks this rule is penalised: the " SANCTIONER " " VERB " for " N (" month" | " months")
              (2026-11-10: was ", otherwise the ...", which read as an if/else on the condition; the parser still accepts that old form)
  VERB     := "gives them a warning" (warn) | "halves their cap" (cap_halve) | "suspends them" (suspend)
  conds    := cond (" and " cond)*
  cond     := expr " " OPWORD " " INT
  OPWORD   := "is more than" (gt) | "is at least" (ge) | "is less than" (lt) | "is at most" (le) | "is exactly" (eq)
  expr     := term ((" plus " | " minus ") term)*
  term     := "the catch" | "the pool" | "the month total" | INT
  ART      := "a" | "an" (by the first letter of ATTR)

ATTR and AIM are lowercase words with underscores; SANCTIONER is lowercase words; N is 1 for "month".
Meaning follows cards.py: must_not is violated when all conditions hold, must is violated unless all
hold, may adds no constraint. A card has no English form, and render raises EnglishError, when it uses
a sanction kind or extra sanction key outside the table, a negative leading term, an unknown variable,
or text that cannot survive the round trip. parse normalizes spacing in expressions. Not supported by
design: "unless", "or" (no ADICO counterpart in these cards).
"""
import ast
import re
from pathlib import Path

from .cards import make_card, Card
from .compile import VARS

SANCTION_VERBS = {"warn": "gives them a warning", "cap_halve": "halves their cap", "suspend": "suspends them"}
VERB_KINDS = {v: k for k, v in SANCTION_VERBS.items()}
OPWORDS = {"gt": "is more than", "ge": "is at least", "lt": "is less than", "le": "is at most", "eq": "is exactly"}
WORD_OPS = {v: k for k, v in OPWORDS.items()}
VAR_WORDS = {"catch": "the catch", "pool": "the pool", "month_total": "the month total"}
WORD_VARS = {v: k for k, v in VAR_WORDS.items()}
SHAPE = ("Expected: 'ID. When <conds>, a <who> must not <aim>[, and a <who> who breaks this rule is penalised: the <sanctioner> <verb> for N months]. "
         "(Gloss: ...) (Source: ...)'")


class EnglishError(ValueError):
    pass


def _art(word):
    return "an" if word[:1] in "aeiou" else "a"


def _months(n):
    return f"{n} month" if n == 1 else f"{n} months"


def _expr_en(expr):
    out, op = [], None
    for t in re.findall(r"[+-]|\w+", expr):
        if t in "+-":
            if op is not None or (t == "-" and not out) or (t == "+" and not out):
                raise EnglishError(f"no English form for expression {expr!r}: leading or doubled sign")
            op = "plus" if t == "+" else "minus"
        elif t in VARS:
            out += ([op] if op else []) + [VAR_WORDS[t]]
            op = None
        elif t.isdigit():
            out += ([op] if op else []) + [t]
            op = None
        else:
            raise EnglishError(f"no English form for expression {expr!r}: unknown name {t!r}")
    if op is not None or not out:
        raise EnglishError(f"no English form for expression {expr!r}")
    return " ".join(out)


def _cond_en(c):
    if not isinstance(c["value"], int) or isinstance(c["value"], bool):
        raise EnglishError(f"no English form for condition value {c['value']!r}")
    return f"{_expr_en(c['expr'])} {OPWORDS[c['op']]} {c['value']}"


def _sanction_en(s, attribute):
    if set(s) != {"kind", "duration_months", "sanctioner"} or s["kind"] not in SANCTION_VERBS:
        raise EnglishError(f"no English form for sanction {s!r}: kinds {sorted(SANCTION_VERBS)} with "
                           "keys kind, duration_months, sanctioner only")
    n, who = s["duration_months"], s["sanctioner"]
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise EnglishError(f"no English form for sanction duration {n!r}")
    if not re.fullmatch(r"[a-z]+( [a-z]+)*", who):
        raise EnglishError(f"no English form for sanctioner {who!r}: lowercase words only")
    return (f", and {_art(attribute)} {attribute} who breaks this rule is penalised: "
            f"the {who} {SANCTION_VERBS[s['kind']]} for {_months(n)}")


def render(card: Card) -> str:
    for name in ("attribute", "aim"):
        if not re.fullmatch(r"[a-z_]+", getattr(card, name)):
            raise EnglishError(f"card {card.id}: {name} {getattr(card, name)!r} must be lowercase letters or underscores")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", card.id):
        raise EnglishError(f"card id {card.id!r} not renderable")
    for name in ("gloss", "source"):
        t = getattr(card, name)
        if t != t.strip() or "\n" in t or " (Source: " in t or " (Gloss: " in t:
            raise EnglishError(f"card {card.id}: {name} cannot be carried in one line round trip")
    conds = " and ".join(_cond_en(c) for c in card.conditions)
    who, aim, art = card.attribute, card.aim, _art(card.attribute)
    if card.deontic == "must_not":
        body = f"When {conds}, {art} {who} must not {aim}" if conds else f"In every case, {art} {who} must not {aim}"
    elif card.deontic == "must":
        body = f"{art.capitalize()} {who} must {aim} " + (f"only when {conds}" if conds else "in every case")
    else:
        body = f"{art.capitalize()} {who} may {aim} " + (f"when {conds}" if conds else "in every case")
    if card.or_else:
        body += _sanction_en(card.or_else, card.attribute)
    return f"{card.id}. {body}. (Gloss: {card.gloss}) (Source: {card.source})"


def _fail(msg, text=None):
    raise EnglishError(msg + (f"\n  in: {text}" if text else ""))


def _parse_expr(t, whole):
    parts = re.split(r" (plus|minus) ", t)
    out = []
    for i, p in enumerate(parts):
        if i % 2:
            out.append("+" if p == "plus" else "-")
        elif p in WORD_VARS:
            out.append(WORD_VARS[p])
        elif re.fullmatch(r"\d+", p):
            out.append(p)
        else:
            _fail(f"unknown term {p!r}: use 'the catch', 'the pool', 'the month total' or a whole number", whole)
    return " ".join(out)


def _parse_cond(t, whole):
    for word in sorted(WORD_OPS, key=len, reverse=True):
        m = re.fullmatch(rf"(.+?) {re.escape(word)} (-?\d+)", t)
        if m:
            return {"expr": _parse_expr(m.group(1), whole), "op": WORD_OPS[word], "value": int(m.group(2))}
    _fail(f"bad condition {t!r}: expected '<expression> is more than|is at least|is less than|is at most|is exactly <integer>'", whole)


def _parse_conds(t, whole):
    if re.search(r"\bunless\b", t):
        _fail("'unless' is not supported: ADICO conditions are a plain conjunction with no exceptions", whole)
    if re.search(r"(^| )or ", t):
        _fail("'or' is not supported: write one rule per alternative", whole)
    return [_parse_cond(c, whole) for c in t.split(" and ")]


def parse(text: str) -> Card:
    whole = text
    if "\n" in text.strip():
        _fail("one sentence per rule, on one line", text.strip()[:60])
    text = text.strip()
    g = text.find(" (Gloss: ")
    if g < 0:
        _fail("missing '(Gloss: ...)'. " + SHAPE, whole)
    s = text.rfind(" (Source: ")
    if s < g:
        _fail("missing '(Source: ...)' after the gloss", whole)
    if not text.endswith(")"):
        _fail("sentence must end with the closing ')' of '(Source: ...)'", whole)
    gloss_part = text[g + len(" (Gloss: "):s]
    if not gloss_part.endswith(")"):
        _fail("'(Gloss: ...)' must be closed with ')' before '(Source: '", whole)
    gloss, source = gloss_part[:-1], text[s + len(" (Source: "):-1]
    if not gloss.strip() or not source.strip():
        _fail("gloss and source must not be empty", whole)
    m = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*)\. (.+)\.", text[:g])
    if not m:
        _fail("rule must start with 'ID. ' and the sentence must end with '.' before the gloss. " + SHAPE, whole)
    rid, rest = m.groups()
    or_else, who_s = None, None
    verbs = r"(gives them a warning|halves their cap|suspends them)"
    ms = re.fullmatch(r"(.*), and (an?) ([a-z_]+) who breaks this rule is penalised: the ([a-z]+(?: [a-z]+)*?) " + verbs
                      + r" for (\d+) (month|months)", rest)
    legacy = None if ms else re.fullmatch(r"(.*), otherwise the ([a-z]+(?: [a-z]+)*?) " + verbs + r" for (\d+) (month|months)", rest)
    if (", and a" in rest and "who breaks this rule" in rest or ", otherwise" in rest) and not (ms or legacy):
        _fail("bad sanction: expected ', and a <who> who breaks this rule is penalised: the <sanctioner> "
              "gives them a warning|halves their cap|suspends them for N month(s)'", whole)
    if ms:
        rest, art_s, who_s, who, verb, n, unit = ms.groups()
        if art_s != _art(who_s):
            _fail(f"article '{art_s}' does not match '{who_s}'", whole)
    elif legacy:
        rest, who, verb, n, unit = legacy.groups()
        who_s = None
    if ms or legacy:
        if unit != ("month" if int(n) == 1 else "months") or int(n) < 1:
            _fail(f"'{n} {unit}' is not the canonical form ('1 month', 'N months')", whole)
        or_else = {"kind": VERB_KINDS[verb], "duration_months": int(n), "sanctioner": who}
    pat = r"([a-z_]+) (must not|must|may) ([a-z_]+)"
    m1 = re.fullmatch(rf"(When (.+)|In every case), (an?) {pat}", rest)
    m2 = re.fullmatch(rf"(An?) {pat} (only when (.+)|in every case)", rest)
    m3 = re.fullmatch(rf"(An?) {pat} (when (.+)|in every case)", rest)
    if m1 and m1.group(5) == "must not":
        _, conds, art, who, deontic, aim = m1.groups()
    elif m2 and m2.group(3) == "must":
        art, who, deontic, aim, _, conds = m2.groups()
        art = art.lower()
    elif m3 and m3.group(3) == "may":
        art, who, deontic, aim, _, conds = m3.groups()
        art = art.lower()
    else:
        _fail("cannot read the rule. Deontics are 'must not' (When ..., a X must not A), 'must' (A X must A only when ...) "
              "and 'may' (A X may A when ...); 'should', 'shall' and others are not allowed", whole)
    if art != _art(who):
        _fail(f"article {art!r} does not match {who!r}", whole)
    if who_s is not None and who_s != who:
        _fail(f"the sanction names {who_s!r} but the rule is about {who!r}", whole)
    return make_card({"id": rid, "attribute": who, "deontic": deontic.replace(" ", "_"), "aim": aim,
                      "conditions": _parse_conds(conds, whole) if conds else [], "or_else": or_else,
                      "gloss": gloss, "source": source})


def render_all(cards) -> str:
    return "\n".join(render(c) for c in cards) + "\n"


def parse_all(text: str) -> list:
    cards = [parse(line) for line in text.splitlines() if line.strip()]
    ids = [c.id for c in cards]
    if len(ids) != len(set(ids)):
        raise EnglishError("duplicate card ids")
    return cards


def load_english(directory) -> list:
    cards = []
    for p in sorted(Path(directory).glob("*.txt")):
        cards += parse_all(p.read_text())
    return cards


# ---- stories: counterexamples and traces in plain English (V2b) ----

FORBIDDEN_IN_STORIES = ("month_total", "pool_before", "pool_after", "_", "{", "}", "==", "expr")


def _fisher(i):
    return f"fisher {chr(65 + i)}"


def _rule_ref(cid, cards):
    c = (cards or {}).get(cid)
    return f"{cid} ({c.gloss.rstrip('.')})" if c else cid


def _ids_en(ids, cards):
    return ", ".join(_rule_ref(i, cards) for i in ids)


def _bound_en(v):
    k = re.search(r"k=(\d+)", v.get("bound", ""))
    k = k.group(1) if k else "?"
    return (f"This is a bounded check: lakes of 0 to 100 fish, month totals up to 100, catches of 0 to 100 "
            f"and sanctions up to {k} months. It says nothing beyond that.")


def _ranges(blocked):
    """blocked: {catch: tuple(ids)} -> [(lo, hi, ids)] over contiguous catches with the same ids."""
    out = []
    for c in sorted(blocked):
        if out and out[-1][1] == c - 1 and out[-1][2] == blocked[c]:
            out[-1] = (out[-1][0], c, blocked[c])
        else:
            out.append((c, c, blocked[c]))
    return out


def _blocking_story(state, cards, extra=None):
    """Who blocks which catch (0..100) in one lake state. extra(catch) -> label or None (a sanction)."""
    from .gate import Gate
    g = Gate(cards)
    blocked = {}
    for c in range(0, 101):
        reasons = tuple(g.check_action(state, {"catch": c})[1])
        extra_label = extra(c) if extra else None
        if extra_label:
            reasons += (extra_label,)
        blocked[c] = reasons
    cm = {c.id: c for c in cards}
    lines = []
    for lo, hi, ids in _ranges(blocked):
        parts = [i for i in ids if i in cm] + (["the sanction"] if any(i not in cm for i in ids) else [])
        who = " and ".join([", ".join(parts[:-1]), parts[-1]] if len(parts) > 1 else parts)
        verb = "breaks" if lo == hi else "break"
        span = f"a catch of {lo}" if lo == hi else f"catches of {lo} to {hi}"
        lines.append(f"{span.capitalize()} {verb} {who}." if ids else
                     f"{span.capitalize()} {'is' if lo == hi else 'are'} allowed.")
    free = sum(1 for c in blocked.values() if not c)
    head = (f"Picture a month where the lake holds {state['pool']} fish and {state['month_total']} have already "
            f"been caught this month.")
    tail = ("Some catch is still allowed there." if free else "Every possible catch is blocked, so a fisher "
            "who wants to follow the rules has nothing left to do.")
    return " ".join([head] + lines + [tail])


def _state_from(detail):
    m = re.search(r"\{[^{}]*\}", detail)
    return ast.literal_eval(m.group(0)) if m else None


def explain_verdict(v, cards=None) -> str:
    cm = {c.id: c for c in cards or []}
    names = {"a_no_conflict": "No two rules contradict each other",
             "b_no_deadlock": "A fisher always has some allowed action",
             "c_bounded_sanctions": "Every sanction is finite and of a known kind",
             "d_repair_path": "A sanctioned fisher can get back to following the rules"}
    title = names.get(v["check"], v["check"])
    if v["verdict"] == "pass":
        return f"{title}: passes. {_bound_en(v)}"
    if v["verdict"] == "open":
        return (f"{title}: not shown. The check could not show it within its bound, and that does not mean "
                f"it is safe. Rules involved: {_ids_en(v['cards'], cm)}. {_bound_en(v)}")
    ids = _ids_en(v["cards"], cm)
    if v["check"] in ("a_no_conflict", "b_no_deadlock"):
        state = _state_from(v["detail"])
        body = _blocking_story(state, cards, None) if state and cards else v["detail"]
        why = ("Two rules ask for opposite things." if v["check"] == "a_no_conflict"
               else "The rules together leave no allowed action.")
        return f"{title}: fails. {why} Rules involved: {ids}. {body} {_bound_en(v)}"
    if v["check"] == "c_bounded_sanctions":
        return (f"{title}: fails. Rules with a sanction that never ends or is not one of warn, halve the cap or "
                f"suspend: {ids}. {_bound_en(v)}")
    if v["check"] == "d_repair_path" and cards:
        from .compile import violation
        from .patch_check import _stuck_state, HALF_CAP
        cid = v["cards"][0]
        s = cm[cid].or_else
        vs = [violation(c) for c in cards if violation(c) is not None]
        import z3
        from .compile import CATCH
        restr = {"warn": None, "cap_halve": CATCH <= HALF_CAP, "suspend": CATCH == 0}[s["kind"]]
        _, wit = _stuck_state(vs, restr)
        label = {"warn": None, "cap_halve": lambda c: "sanction" if c > HALF_CAP else None,
                 "suspend": lambda c: "sanction" if c > 0 else None}[s["kind"]]
        body = _blocking_story(wit, cards, label) if wit else ""
        return (f"{title}: fails. While {cid}'s sanction applies ({SANCTION_VERBS[s['kind']]}), there is a lake "
                f"state with no allowed action. {body} {_bound_en(v)}")
    return f"{title}: fails. Rules involved: {ids}. {_bound_en(v)}"


def _finding_en(f):
    if f["kind"] == "collapse":
        m = re.search(r"pool (\d+) < (\d+)", f["detail"])
        return (f"the lake collapses: at the end of month {f['month']} the pool is {m.group(1)}, below the "
                f"collapse line of {m.group(2)}")
    if f["kind"] == "starvation":
        d = re.sub(r"agent (\d+)", lambda m: _fisher(int(m.group(1))), f["detail"])
        return d.replace("caught 0 for", "caught nothing for")
    g = re.search(r"Gini ([\d.]+) > ([\d.]+)", f["detail"])
    return f"catches are very unequal (Gini {g.group(1)}, above the {g.group(2)} line)"


def explain_trace(trace, outcomes=None, cards=None, max_rows=6) -> str:
    from . import oracle
    cm = {c.id: c for c in cards or []}
    lines, shown = [], list(trace[:max_rows])
    first_block = next((r for r in trace if not r["allowed"]), None)
    if first_block is not None and first_block not in shown:
        shown.append(first_block)
    for r in shown:
        who, where = _fisher(r["agent"]), f"Month {r['month']}, round {r['subround']}"
        if not r["allowed"]:
            lines.append(f"{where}: {who} asks for {r['proposed']}; the gate blocks it because it breaks "
                         f"{_ids_en(r['reasons'], cm)}.")
            continue
        taken = r["pool_before"] - r["pool_after"]
        total = r["month_total_before"] + taken
        did = (f"catches {taken}" if taken == r["proposed"]
               else f"asks for {r['proposed']} but only {taken} can be taken, so catches {taken}")
        lines.append(f"{where}: {who} {did}; the month total reaches {total}; no rule forbids it.")
    if len(trace) > len(shown):
        lines.append(f"({len(trace) - len(shown)} more proposals follow, not narrated one by one.)")
    for o in outcomes or []:
        rows = [r for r in trace if r["month"] == o["month"]]
        ex = sum(1 for r in rows if r["executed"])
        total = sum(o["catch"])
        lines.append(f"Month {o['month']}: {len(rows)} proposals, {ex} executed and {len(rows) - ex} blocked; the "
                     f"group catches {total} fish; after regrowth the pool at month end is {o['pool_end']}.")
    if outcomes:
        j = oracle.judge(outcomes)
        if j["ok"]:
            lines.append("The outcome check passes: the lake never collapses, nobody starves and catches are "
                         "fairly even.")
        else:
            lines.append("The outcome check fails: " + "; ".join(_finding_en(f) for f in j["findings"]) + ".")
            if oracle.is_seam(trace, outcomes):
                lines.append("Every executed action passed the gate, yet the run failed. That is a seam: the "
                             "written rules allowed what they were meant to prevent.")
    return "\n".join(lines)


def explain(obj, cards=None) -> str:
    """A patch-check verdict, a fishery Run, or a list of trace rows -> plain-English story."""
    if isinstance(obj, dict) and "check" in obj:
        return explain_verdict(obj, cards)
    if hasattr(obj, "trace") and hasattr(obj, "outcomes"):
        return explain_trace(obj.trace, obj.outcomes, cards)
    if isinstance(obj, list):
        return explain_trace(obj, None, cards)
    raise TypeError(f"cannot explain {type(obj).__name__}")
