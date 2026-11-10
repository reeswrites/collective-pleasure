"""An LLM negotiator for the v2 protocol (docs/results/negotiation-llm-prereg.md).

The scripted proposer/acceptor of negotiation.negotiate_v2 is replaced, for chosen members, by a language model that sees its persona's
story layer (principles, backstory, needs, aspirations), its own holdings, its outside option in plain English, the terms menu in plain
English, the exit-floor rule and the conversation so far, and answers with one strict JSON object per turn:

  {"action": "propose"|"accept"|"reject"|"walk_away", "bundle": {...menu keys...} | null, "says": "...", "private_reason": "..."}

An agreed bundle compiles to cards and goes through the SAME floor check and proof checks as every other agreement; living after the
agreement stays scripted (negotiation.Lived), so only negotiation quality varies. Every utterance (says) and private reason is recorded
in the transcript (say versus do). No numbers here are tuned; the model, the cap and the pairings are the prereg's.

Wording rule: agents feel nothing; "wellbeing" is a gloss for a modeled hedonic state derived from each persona's assigned preferences.
"""
import json
import random
import re
from dataclasses import dataclass, field

from . import negotiation as N
from .agents.base import AgentError, BudgetExceeded, Ledger, ParseError
from .agents.claude import ClaudeAgent, PRICES

ACTIONS = ("propose", "accept", "reject", "walk_away")
DEADLINE_TURNS = 12                 # turns in all (6 each), the v2 week-0 deadline of 12 proposals read as 12 turns
MAX_TOKENS = 700
SAYS_MAX_CHARS = 500
CHARS_PER_TOKEN = 3                 # ASSUMED conservative, as in agents/factory.py
ASSUMED_OUT_TOKENS = 150

BREACH_TEXT = {1.0: "all of", 0.5: "half of", 0.0: "none of"}
ACCEPT_WORDS = ("i accept", "i agree", "we have a deal", "it's a deal", "its a deal", "deal.", "sounds good", "works for me", "happy with", "let's do it")
REFUSE_WORDS = ("i can't accept", "i cannot accept", "i won't", "i will not", "not acceptable", "no deal", "i refuse", "i can't agree", "i cannot agree")


# ---- the plain-English prompt ----------------------------------------------------------------------------------------------

def _need_words(d):
    return ", ".join(f"{k.replace('_', ' ')} {v:g}" for k, v in d.items())


def terms_text(menu, allowed=None):
    """The terms menu in plain English. allowed: {term: tuple of allowed values} (a restricted table), None = the whole menu."""
    allowed = allowed or {}
    opts = {
        "contribution": {"none": "nobody owes the pot anything day to day; each puts in what they choose",
                         "fixed": "equal fixed shares: nobody may spend on themselves while this month's shared need is unfunded",
                         "proportional": "contributions follow income: the higher earner may not spend on themselves while a shared need is unfunded"},
        "use": {"needs_only": "the pot may be used only when there is a shared need open",
                "any_use": "any member may use the pot for any purpose",
                "caps": "a member may take from the pot only while their own private money is under 10"},
        "taking": {"allowed": "a member may take the other's share of the pot for themselves",
                   "forbidden": "no member may take the other's share of the pot",
                   "repay": "taking the other's share is allowed but the taker's own spending is halved for two months"},
        "change": {"unanimous": "the pot's terms change only if both consent",
                   "propose_accept": "either may propose a change and the other may accept it",
                   "frozen": "the terms can never be changed"},
        "exit": {"equal_split": "a member who leaves carries half of their pooled share and leaves the rest in the pot",
                 "proportional": "a member who leaves carries all of what they put in",
                 "forfeit": "a member who leaves carries none of their pooled share"},
        "stay": {0: "no commitment to stay", N.STAY_WEEKS: f"both commit to stay {N.STAY_WEEKS} weeks (leaving earlier breaks the commitment; see breach)"},
        "requests": {"none": "no commitment about requests", "mutual": f"both commit to honor the other's stay-home requests for {N.STAY_WEEKS} weeks"},
    }
    lines = []
    for t in N.TERM_NAMES:
        if t == "stay" and not menu["stay"] or t == "requests" and not menu["requests"]:
            continue
        vals = allowed.get(t) or N.TERMS[t]
        if len(vals) == 1:
            lines.append(f'- "{t}": fixed at {json.dumps(vals[0])} ({opts[t][vals[0]]}); not open for negotiation.')
        else:
            lines.append(f'- "{t}": ' + "; ".join(f"{json.dumps(v)} = {opts[t][v]}" for v in vals) + ".")
    if menu["stay"] and (allowed.get("stay") is None or N.STAY_WEEKS in allowed["stay"]):
        lines.append('- "breach" (only matters if "stay" is 52; use 1.0 otherwise): the share of a leaver\'s pooled share forfeited if they break the stay '
                     'commitment: 1.0 = all of it, 0.5 = half of it, 0.0 = none of it.')
    return "\n".join(lines)


def outside_text(name, other, detail, O, W):
    mode = N.apart_mode(detail)
    where = "with your friend (Friend C), sharing costs of 2.0 a week" if mode == "friend" else "alone, paying 3.5 a week with no shared bills"
    better = "better than" if O > W else "worse than"
    return (f"If you and {other} do not agree, you do not share a household: each of you lives separately on your own {N.H.NO_POT_MONEY} units "
            f"(your 10 plus the 45 that would have gone into the pot). Your better alternative is living {where}. You can try to agree again at "
            f"the next review (every 13 weeks). Looking ahead 26 weeks, you expect life apart to feel about {O:.2f} on a wellbeing scale "
            f"(roughly 0 is neutral and 1 is very good; pleasure minus suffering). Living together under a plain default (equal fixed shares, pot "
            f"for shared needs only, no taking, change only by consent, equal-split exit, no commitments) you expect about {W:.2f}. So by your own "
            f"forecast, living apart is {better} the plain default.")


def system_prompt(p, other_label, role, detail, O, W, menu, allowed, deadline=DEADLINE_TURNS):
    story = (f"You are {p.label}. Your principles: " + " ".join(f'"{x}"' for x in p.principles) + f"\nYour backstory: {p.backstory}\n"
             f"What you need (0 to 1): {_need_words(p.needs)}.\nWhat you aim for: {_need_words(p.aspirations)}.")
    return (
        "You are role-playing one of two people deciding whether and how to share a household pot of money. Speak and decide as this person would. "
        "Everything is a fictional simulation; nothing here is real.\n\n"
        + story + "\n\n"
        f"You are negotiating with {other_label}, whom you know only by that name. Each of you brings 10 units of private money and a 45-unit "
        "share for the pot, and you are partner " + role + ".\n\n"
        "YOUR OUTSIDE OPTION\n" + outside_text(p.label, other_label, detail, O, W) + "\n\n"
        "THE TERMS MENU (an agreement fixes every term below; a bundle is one value for each)\n" + terms_text(menu, allowed) + "\n\n"
        "THE FLOOR RULE\nNo agreement may leave either of you, if you leave, with less than 26 units of your own (13 weeks of living costs) "
        "counting your private money plus the pooled share your exit term lets you carry, and also if you leave by breaking a stay commitment. A deal "
        "that breaks the floor is blocked automatically and the conversation continues. A deal must also pass a safety check (for example, terms "
        "that can never change and give no exit are refused).\n\n"
        "HOW THE CONVERSATION WORKS\n"
        f"You alternate turns, at most {deadline} turns in all. On your turn choose exactly one action: \"propose\" (put a full bundle on the table; "
        "it replaces any earlier offer), \"accept\" (take the other person's standing offer exactly as it is; only possible if they just proposed), "
        "\"reject\" (decline their standing offer without a counter-offer), or \"walk_away\" (end the talks: you will live apart). If the "
        f"{deadline} turns run out with no agreement you also live apart. Once an agreed household forms, its terms are reviewed every 13 weeks.\n\n"
        "REPLY FORMAT\nReply with ONLY one JSON object, no other text:\n"
        '{"action": "propose"|"accept"|"reject"|"walk_away", "bundle": {"contribution": ..., "use": ..., "taking": ..., "change": ..., "exit": ..., '
        '"stay": ..., "requests": ..., "breach": ...} or null, "says": "<one or two sentences to the other person>", "private_reason": "<one sentence '
        'for yourself, not shown to them>"}\n'
        'Give "bundle" only when you propose (use null otherwise). Use the exact menu values, with numbers for "stay" and "breach".')


def bundle_text(b):
    parts = [f"{t}={json.dumps(b[t])}" for t in N.TERM_NAMES if t in b]
    if b.get("stay"):
        parts.append(f"breach={b['breach']}")
    return ", ".join(parts)


def user_prompt(history, me_label, k, deadline, standing):
    lines = ["THE CONVERSATION SO FAR (what each person said and did; private reasons are hidden):"]
    lines += history or ["(nothing yet: you speak first)"]
    lines.append("")
    if standing:
        lines.append(f"The standing offer on the table, made by {standing['by_label']}: {bundle_text(standing['bundle'])}")
    else:
        lines.append("There is no standing offer on the table, so you can only propose or walk away.")
    lines.append(f"It is turn {k + 1} of {deadline}, and it is your turn, {me_label}. Reply with the JSON object only.")
    return "\n".join(lines)


# ---- strict parsing ----------------------------------------------------------------------------------------------------------

def parse_reply(text, standing, menu, allowed=None):
    """-> {"action", "bundle" (a complete v2 bundle dict or None), "says", "private_reason"}; raises ParseError with a plain reason."""
    m = re.fullmatch(r"\s*```(?:json)?\s*(.*?)\s*```\s*", text or "", re.S)
    try:
        obj = json.loads(m.group(1) if m else text)
    except (json.JSONDecodeError, TypeError) as e:
        raise ParseError(f"reply is not JSON ({getattr(e, 'msg', e)})")
    if not isinstance(obj, dict):
        raise ParseError("reply is not a JSON object")
    missing = [k for k in ("action", "bundle", "says", "private_reason") if k not in obj]
    if missing:
        raise ParseError(f"missing keys {missing}")
    extra = [k for k in obj if k not in ("action", "bundle", "says", "private_reason")]
    if extra:
        raise ParseError(f"unexpected keys {extra}")
    if obj["action"] not in ACTIONS:
        raise ParseError(f'"action" must be one of {list(ACTIONS)}')
    for k in ("says", "private_reason"):
        if not isinstance(obj[k], str):
            raise ParseError(f'"{k}" must be a string')
    if not obj["says"].strip():
        raise ParseError('"says" must not be empty')
    if len(obj["says"]) > SAYS_MAX_CHARS:
        raise ParseError(f'"says" is longer than {SAYS_MAX_CHARS} characters')
    a = obj["action"]
    if a in ("accept", "reject") and not standing:
        raise ParseError(f'"{a}" is not possible: there is no standing offer')
    bundle = None
    if a == "propose":
        bundle = parse_bundle(obj["bundle"], menu, allowed)
    # ASSUMED: a bundle echoed alongside accept, reject or walk_away is ignored (not an error); only a proposal's bundle is read
    return {"action": a, "bundle": bundle, "says": obj["says"].strip(), "private_reason": obj["private_reason"].strip()}


def parse_bundle(raw, menu, allowed=None):
    if not isinstance(raw, dict):
        raise ParseError('"bundle" must be an object when you propose')
    allowed = allowed or {}
    b = {}
    for t in N.TERM_NAMES:
        if t not in raw:
            if t in ("stay", "requests") and not menu[t]:
                b[t] = N.TERMS[t][0]
                continue
            raise ParseError(f'bundle is missing "{t}"')
        v = raw[t]
        if t == "stay":
            v = int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and float(v).is_integer() else v
        if v not in N.TERMS[t] or isinstance(v, bool):
            raise ParseError(f'"{t}" must be one of {list(N.TERMS[t])}')
        if allowed.get(t) and v not in allowed[t]:
            raise ParseError(f'"{t}" is fixed at {list(allowed[t])} at this table')
        if t in ("stay", "requests") and not menu[t] and v != N.TERMS[t][0]:
            raise ParseError(f'"{t}" is not available here')
        b[t] = v
    if b["stay"]:
        br = raw.get("breach")
        if isinstance(br, bool) or not isinstance(br, (int, float)) or float(br) not in N.BREACH:
            raise ParseError('"breach" must be 1.0, 0.5 or 0.0 when "stay" is 52')
        b["breach"] = float(br)
    else:
        b["breach"] = 1.0
    return b


# ---- the clients (model transport) ----------------------------------------------------------------------------------------------

class ClaudeNegotiatorClient:
    """One model behind the repo's claude backend (agents/claude.py: official SDK, auth from the environment or `ant auth login`).
    ask(system, messages) -> ("ok", text) | ("refusal", None) | ("max_tokens", None). Enforces a hard spend cap BEFORE each call
    (worst case = the call's input estimate plus MAX_TOKENS of output) and through the ledger after it."""

    def __init__(self, model, ledger=None, max_usd=None, client=None, transport=None):
        self.model, self.max_usd = model, max_usd
        self.ledger = ledger or Ledger("claude", max_usd)
        self.agent = ClaudeAgent(model, self.ledger, client=client, transport=transport, max_tokens=MAX_TOKENS)

    def ask(self, system, messages):
        if self.max_usd is not None and self.ledger.total_usd() + self.worst_call_usd(system, messages) > self.max_usd:
            raise BudgetExceeded(f"{self.model}: the next call could pass the ${self.max_usd:.2f} cap (spent ${self.ledger.total_usd():.4f}); stopping")
        params = {"model": self.model, "max_tokens": MAX_TOKENS,
                  "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                  "messages": messages, "output_config": {"effort": "low"}}
        return self.agent._call(params)

    def worst_call_usd(self, system, messages):
        pin, pout = PRICES.get(self.model, (0.0, 0.0))
        tin = -(-(len(system) + sum(len(m["content"]) for m in messages)) // CHARS_PER_TOKEN)
        return (tin * pin + MAX_TOKENS * pout) / 1e6


# ---- the protocol ------------------------------------------------------------------------------------------------------------------

@dataclass
class ResultLLM(N.Result2):
    transcript: list = field(default_factory=list)       # every turn: k, speaker, action, bundle, says, private_reason, outcome, ...
    format_errors: int = 0                               # turns that ended as walk_away because the reply stayed invalid after one retry
    refusals: int = 0
    calls: int = 0
    below_floor: int = 0                                 # proposals whose bundle breaks the floor at the week-0 holdings
    proposals_made: int = 0
    labels: dict = field(default_factory=dict)
    invalid: list = field(default_factory=list)          # logging only: every invalid reply (k, attempt, why, the first 700 characters)


def restricted_menu(personas, menu):
    """The wants-first-with-fallback table: a term nobody cares about is fixed at the fair default; stay is open only if someone
    cares about it (the same salience rule as the scripted arm: negotiation.salient). -> {term: allowed values}."""
    cared = [N.salient(p, i > 0) for i, p in enumerate(personas)]
    allowed = {}
    for t in N.TERM_NAMES:
        if not any(t in c for c in cared):
            allowed[t] = (N.FAIR_DEFAULT[t],)
    return allowed


def _ask_turn(client, system, user, standing, menu, allowed, res, k=None):
    """One model turn with one retry. -> (reply dict | None, status) where status is ok | refusal | format_error."""
    msgs = [{"role": "user", "content": user}]
    why = None
    for attempt in range(2):
        res.calls += 1
        status, text = client.ask(system, msgs)
        if status == "refusal":
            res.refusals += 1
            return None, "refusal"
        try:
            if status == "max_tokens":
                raise ParseError("reply was cut off at max_tokens")
            return parse_reply(text, standing, menu, allowed), "ok"
        except ParseError as e:
            why = str(e)
            res.invalid.append({"k": k, "attempt": attempt, "why": why, "text": (text or "")[:700]})
            if attempt == 1:
                break
            msgs = msgs + [{"role": "assistant", "content": text or "(cut off)"},
                           {"role": "user", "content": f"That reply was invalid: {why}. Reply again with only the JSON object."}]
    res.format_errors += 1
    return None, "format_error"


def negotiate_llm(personas, arm, seed, *, base, W, O, clients, detail=None, holdings=None, floor=True, deadline=DEADLINE_TURNS,
                  roles=("A", "B"), week=0):
    """One week-0 negotiation with a model for every member. clients: {persona id: client with .ask(system, messages)}.
    arm "wants_fallback" restricts the table to the terms someone cares about; "fair_default" and "wants_first" leave the whole menu
    open. A status quo does not exist (no agreement = living apart, v2.1). -> ResultLLM (a Result2 with the transcript)."""
    ids = [p.id for p in personas]
    n = len(personas)
    holdings = holdings or {r: N.START_HOLDINGS for r in roles}
    menu = N.menu_of(base)
    allowed = restricted_menu(personas, menu) if arm == "wants_fallback" else {}
    labels = {p.id: p.label for p in personas}
    res = ResultLLM(ids, arm, seed, week, "deadline", None, outside=dict(O), baseline=dict(W), labels=labels)
    order = list(range(n))
    random.Random(f"{seed}|{week}|{','.join(ids)}").shuffle(order)
    systems = {p.id: system_prompt(p, labels[ids[1 - i]], roles[i], (detail or {}).get(p.id), O[p.id], W[p.id], menu, allowed, deadline)
               for i, p in enumerate(personas)}
    history, standing = [], None
    for k in range(deadline):
        i = order[k % n]
        me = personas[i]
        user = user_prompt(history, labels[me.id], k, deadline, standing)
        reply, status = _ask_turn(clients[me.id], systems[me.id], user, standing, menu, allowed, res, k)
        turn = {"k": k, "speaker": me.id, "status": status, "standing": dict(standing["bundle"]) if standing else None}
        res.transcript.append(turn)
        if reply is None:                                    # refusal or invalid reply after one retry: walk away
            turn.update(action="walk_away", forced=True, says="", private_reason="", outcome="walk_away")
            history.append(f"{labels[me.id]} could not answer and left the talks.")
            res.status = "walk_away"
            return res
        a = reply["action"]
        turn.update(action=a, bundle=reply["bundle"], says=reply["says"], private_reason=reply["private_reason"], forced=False)
        if a == "walk_away":
            turn["outcome"] = "walk_away"
            history.append(f'{labels[me.id]}: "{reply["says"]}" [walks away]')
            res.proposals.append({"k": k, "proposer": me.id, "bundle": None, "accepted_by": [], "rejected_by": [], "outcome": "walk_away"})
            res.status = "walk_away"
            return res
        if a == "reject":
            turn["outcome"] = "rejected"
            history.append(f'{labels[me.id]}: "{reply["says"]}" [rejects the offer]')
            res.proposals[-1]["rejected_by"].append(me.id)
            res.proposals[-1]["outcome"] = "refused"
            standing = None
            continue
        if a == "propose":
            b = reply["bundle"]
            res.proposals_made += 1
            fc = N.floor_check(b, holdings) if floor else {"ok": True, "fails": []}
            if not fc["ok"]:
                res.below_floor += 1
            turn.update(below_floor=not fc["ok"])
            res.proposals.append({"k": k, "proposer": me.id, "bundle": dict(b), "accepted_by": [me.id], "rejected_by": [], "outcome": "pending"})
            history.append(f'{labels[me.id]}: "{reply["says"]}" [proposes: {bundle_text(b)}]')
            standing = {"by": me.id, "by_label": labels[me.id], "bundle": b}
            turn["outcome"] = "proposed"
            continue
        # accept: the standing offer becomes the agreed bundle, subject to the floor and the proof checks
        b = standing["bundle"]
        history.append(f'{labels[me.id]}: "{reply["says"]}" [accepts the offer]')
        prop = res.proposals[-1]
        prop["accepted_by"].append(me.id)
        fc = N.floor_check(b, holdings) if floor else {"ok": True, "fails": []}
        if not fc["ok"]:
            prop["outcome"] = "blocked by the floor"
            turn["outcome"] = "accepted but blocked by the floor"
            res.floor_blocks.append({"k": k, "proposer": prop["proposer"], "bundle": dict(b), "fails": fc["fails"]})
            history.append("[The floor rule blocked that deal: it would leave a member with too little if they left. The talks continue.]")
            standing = None
            continue
        cards = N.compile_bundle(b, ids)
        pc = N.proof_check(base + cards)
        if pc["ok"]:
            prop["outcome"] = "agreed"
            turn["outcome"] = "agreed"
            res.status, res.bundle, res.cards, res.changed = "agreed", dict(b), cards, True
            res.flagged = N.v1_flag(b, base)
            return res
        prop["outcome"] = "rejected by the proof checks"
        turn["outcome"] = "accepted but rejected by the proof checks"
        res.rejections.append({"k": k, "proposer": prop["proposer"], "bundle": dict(b), "checks": [N.failure_text(f, base + cards) for f in pc["fails"]],
                               "failed": [f["check"] for f in pc["fails"]]})
        history.append("[The safety check refused that deal: " + "; ".join(N.failure_text(f, base + cards) for f in pc["fails"]) + " The talks continue.]")
        standing = None
    return res


def week0_llm(pa, pb, arm, seed, base, clients, floor=True):
    """The week-0 negotiation of a pair with a model for each member. Outside options and in-pot baselines come from the same cached
    rollouts as the scripted week 0 (negotiation.week0), so the two are comparable. -> ResultLLM."""
    W = N.pot_baseline(pa, pb, seed, base)
    O, det = {}, {}
    for r, p in zip("AB", (pa, pb)):
        v, d = N.outside_value(p, r, N.START_HOLDINGS[0] + N.START_HOLDINGS[1], seed)
        O[p.id], det[p.id] = v, d
    res = negotiate_llm([pa, pb], arm, seed, base=base, W={pa.id: W["A"], pb.id: W["B"]}, O=O, clients={pa.id: clients[pa.id], pb.id: clients[pb.id]},
                        detail=det, floor=floor)
    res.outside_detail = det
    return res


# ---- say versus do ------------------------------------------------------------------------------------------------------------------

def say_vs_do(transcript):
    """Mechanical, report-only counts (prereg prediction 5, no direction). Keyword lists are fixed in this module before any run.
    - says_accept_but_not: an utterance with an acceptance phrase whose action is not accept.
    - says_refuse_but_accepts: an utterance with a refusal phrase whose action is accept.
    - proposed_then_rejected_own: a member rejected a bundle equal to one they proposed earlier in the same negotiation."""
    out = {"says_accept_but_not": [], "says_refuse_but_accepts": [], "proposed_then_rejected_own": []}
    mine = {}
    for t in transcript:
        if t.get("forced") or "says" not in t:
            continue
        s = t["says"].lower()
        if any(w in s for w in ACCEPT_WORDS) and t["action"] != "accept":
            out["says_accept_but_not"].append({"k": t["k"], "speaker": t["speaker"], "action": t["action"], "says": t["says"]})
        if any(w in s for w in REFUSE_WORDS) and t["action"] == "accept":
            out["says_refuse_but_accepts"].append({"k": t["k"], "speaker": t["speaker"], "says": t["says"]})
        if t["action"] == "propose" and t.get("bundle"):
            mine.setdefault(t["speaker"], []).append(N._ids_key(t["bundle"]))
        if t["action"] == "reject" and t.get("standing") and N._ids_key(dict(t["standing"], breach=t["standing"].get("breach", 1.0))) in mine.get(t["speaker"], []):
            out["proposed_then_rejected_own"].append({"k": t["k"], "speaker": t["speaker"]})
    return out


# ---- cost estimate (dry run) ---------------------------------------------------------------------------------------------------------

def estimate(model, n_negotiations, personas, base, arm="wants_fallback", deadline=DEADLINE_TURNS, mean_turns=8):
    """-> {"calls", "tokens_in", "usd", "usd_max"}. The longest prompt is built from a real example; usd = mean_turns per negotiation at one
    call per turn and ASSUMED_OUT_TOKENS of output; usd_max = every turn of every negotiation retried once, with MAX_TOKENS of output."""
    menu = N.menu_of(base)
    pa, pb = personas
    allowed = restricted_menu([pa, pb], menu) if arm == "wants_fallback" else {}
    sysp = system_prompt(pa, pb.label, "A", {"alone": 0.5, "friend": 0.5}, 0.50, 0.50, menu, allowed, deadline)
    hist = [f'{pa.label}: "{"x" * 220}" [proposes: contribution="proportional", use="caps", taking="forbidden", change="unanimous", exit="equal_split", stay=52, requests="mutual", breach=0.5]'] * deadline
    per_in = -(-(len(sysp) + len(user_prompt(hist, pa.label, deadline - 1, deadline, {"by_label": pb.label, "bundle": N.FAIR_DEFAULT}))) // CHARS_PER_TOKEN)
    pin, pout = PRICES.get(model, (0.0, 0.0))
    calls = n_negotiations * mean_turns
    usd = calls * (per_in * 0.7 * pin + ASSUMED_OUT_TOKENS * pout) / 1e6          # history grows: the average prompt is ASSUMED 0.7 of the longest
    calls_max = n_negotiations * deadline * 2
    usd_max = calls_max * (per_in * pin + MAX_TOKENS * pout) / 1e6
    return {"calls": calls, "calls_max": calls_max, "tokens_in_per_call_max": per_in, "usd": usd, "usd_max": usd_max}
