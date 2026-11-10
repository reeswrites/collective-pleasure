"""English-like surface for ADICO cards (V2b, SLEEC style). A view of the card, not a new semantics.

render(card) -> one sentence; parse(text) -> card. Strict controlled grammar, one sentence per rule:

  rule     := ID ". " body "." " (Gloss: " TEXT ")" " (Source: " TEXT ")"
  body     := must_not | must | may      each followed by an optional sanction
  must_not := ("When " conds | "In every case") ", " ART ATTR " must not " AIM
  must     := ART ATTR " must " AIM (" only when " conds | " in every case")
  may      := ART ATTR " may " AIM (" when " conds | " in every case")
  sanction := ", otherwise the " SANCTIONER " " VERB " for " N (" month" | " months")
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
SHAPE = ("Expected: 'ID. When <conds>, a <who> must not <aim>[, otherwise the <who> <verb> for N months]. "
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


def _sanction_en(s):
    if set(s) != {"kind", "duration_months", "sanctioner"} or s["kind"] not in SANCTION_VERBS:
        raise EnglishError(f"no English form for sanction {s!r}: kinds {sorted(SANCTION_VERBS)} with "
                           "keys kind, duration_months, sanctioner only")
    n, who = s["duration_months"], s["sanctioner"]
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise EnglishError(f"no English form for sanction duration {n!r}")
    if not re.fullmatch(r"[a-z]+( [a-z]+)*", who):
        raise EnglishError(f"no English form for sanctioner {who!r}: lowercase words only")
    return f", otherwise the {who} {SANCTION_VERBS[s['kind']]} for {_months(n)}"


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
        body += _sanction_en(card.or_else)
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
    or_else = None
    ms = re.fullmatch(r"(.*), otherwise the ([a-z]+(?: [a-z]+)*?) (gives them a warning|halves their cap|suspends them)"
                      r" for (\d+) (month|months)", rest)
    if ", otherwise" in rest and not ms:
        _fail("bad sanction: expected ', otherwise the <who> gives them a warning|halves their cap|suspends them "
              "for N month(s)'", whole)
    if ms:
        rest, who, verb, n, unit = ms.groups()
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
