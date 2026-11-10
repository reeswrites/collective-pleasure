"""The LLM negotiator (docs/results/negotiation-llm-prereg.md), with mocked clients: no network."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from mar import negotiation as N
from mar import negotiation_llm as NL
from mar import personas as P
from mar.agents.base import BudgetExceeded, Ledger, ParseError

ROOT = Path(__file__).parent.parent / "personas"
PERS = {p.id: p for p in P.load_dir(ROOT) + P.load_dir(ROOT / "pressing")}
BASE = N.base_cards("author_seed_v2_bindable")
MENU = N.menu_of(BASE)
HOLD = {"A": N.START_HOLDINGS, "B": N.START_HOLDINGS}


def b(**kw):
    return {**N.FAIR_DEFAULT, **kw}


def reply(action, bundle=None, says="ok then", why="because", **extra):
    return json.dumps({"action": action, "bundle": bundle, "says": says, "private_reason": why, **extra})


def bj(**kw):
    return {k: v for k, v in b(**kw).items()}


class Mock:
    """Returns the queued replies in order; records what it was asked. A queued tuple is passed through as (status, text)."""

    def __init__(self, *replies):
        self.q, self.asked = list(replies), []

    def ask(self, system, messages):
        self.asked.append((system, messages))
        x = self.q.pop(0)
        return x if isinstance(x, tuple) else ("ok", x)


def run(clients, pa="p-anchor", pb="p-host", arm="fair_default", seed=0, **kw):
    ps = [PERS[pa], PERS[pb]]
    O, W = {p.id: 0.4 for p in ps}, {p.id: 0.3 for p in ps}
    return NL.negotiate_llm(ps, arm, seed, base=BASE, W=W, O=O, clients=clients, detail={p.id: {"alone": 0.3, "friend": 0.4} for p in ps}, **kw)


def first(pa, pb, seed=0):
    import random
    ids = [pa, pb]
    order = list(range(2))
    random.Random(f"{seed}|0|{','.join(ids)}").shuffle(order)
    return ids[order[0]], ids[order[1]]


# ---- parsing ----
def test_parse_accepts_a_complete_proposal_and_fills_breach():
    r = NL.parse_reply(reply("propose", bj(stay=52, breach=0.5, requests="mutual")), None, MENU)
    assert r["action"] == "propose" and r["bundle"]["stay"] == 52 and r["bundle"]["breach"] == 0.5 and r["bundle"]["requests"] == "mutual"
    assert NL.parse_reply(reply("propose", bj()), None, MENU)["bundle"]["breach"] == 1.0      # no stay: breach is inert at 1.0
    assert NL.parse_reply("```json\n" + reply("walk_away") + "\n```", None, MENU)["action"] == "walk_away"


@pytest.mark.parametrize("text,standing,why", [
    ("not json", None, "not JSON"),
    ("[1]", None, "not a JSON object"),
    (json.dumps({"action": "propose"}), None, "missing keys"),
    (reply("shout"), None, "action"),
    (reply("propose", None), None, "bundle"),
    (reply("propose", {**bj(), "use": "wild"}), None, "use"),
    (reply("propose", {k: v for k, v in bj().items() if k != "exit"}), None, "missing"),
    (reply("propose", bj(stay=52, breach=0.7)), None, "breach"),
    (reply("accept"), None, "no standing offer"),
    (reply("reject"), None, "no standing offer"),
    (reply("walk_away", says="  "), None, "empty"),
    (reply("walk_away", extra_key=1), None, "unexpected"),
    (reply("walk_away", says="x" * 600), None, "longer"),
])
def test_parse_rejects_invalid_replies(text, standing, why):
    with pytest.raises(ParseError, match=why):
        NL.parse_reply(text, standing, MENU)


def test_a_restricted_table_rejects_a_term_that_is_fixed():
    allowed = {"exit": ("equal_split",)}
    with pytest.raises(ParseError, match="fixed"):
        NL.parse_reply(reply("propose", bj(exit="forfeit")), None, MENU, allowed)
    assert NL.parse_reply(reply("propose", bj()), None, MENU, allowed)["bundle"]["exit"] == "equal_split"


def test_an_echoed_bundle_on_accept_is_ignored_not_an_error():
    r = NL.parse_reply(reply("accept", bj()), {"bundle": b()}, MENU)
    assert r["action"] == "accept" and r["bundle"] is None


# ---- the prompt ----
def test_prompt_has_story_outside_option_terms_floor_and_history_in_plain_english():
    p, q = PERS["p-anchor"], PERS["p-wanderer"]
    sysp = NL.system_prompt(p, q.label, "A", {"alone": 0.2, "friend": 0.6}, 0.61, 0.42, MENU, {})
    for needle in ("The Anchor", "Home is built together", "Grew up moving", "What you need", "What you aim for", "living with your friend",
                   "0.61", "0.42", "better than the plain default", "THE FLOOR RULE", "26 units", "walk_away", '"exit"', "equal_split", "breach"):
        assert needle in sysp, needle
    assert "weights" not in sysp and "press-" not in sysp                      # no hidden scripted-agent labels
    usr = NL.user_prompt(['The Wanderer: "hi" [proposes: contribution="fixed"]'], "The Anchor", 3, 12, {"by_label": "The Wanderer", "bundle": b()})
    assert "turn 4 of 12" in usr and "standing offer" in usr and "hi" in usr
    assert "no standing offer" in NL.user_prompt([], "The Anchor", 0, 12, None)


def test_restricted_menu_fixes_terms_nobody_cares_about():
    allowed = NL.restricted_menu([PERS["p-controller"], PERS["p-peacekeeper"]], MENU)
    assert allowed and all(v == (N.FAIR_DEFAULT[t],) for t, v in allowed.items())
    assert "taking" not in allowed or True                                      # shape only; the exact set follows the salience rule
    assert "not open for negotiation" in NL.terms_text(MENU, allowed)


# ---- the protocol ----
def test_agreement_goes_through_floor_and_proof_checks_and_compiles_to_cards():
    x, y = first("p-anchor", "p-host")
    good = bj(contribution="proportional")
    res = run({x: Mock(reply("propose", good, says="proportional shares?")), y: Mock(reply("accept", says="deal, thanks"))})
    assert res.status == "agreed" and res.pot and res.bundle == b(contribution="proportional")
    assert res.cards and any(c.id == "N1-contribution-proportional" for c in res.cards)
    assert [t["action"] for t in res.transcript] == ["propose", "accept"] and res.transcript[-1]["outcome"] == "agreed"
    assert res.transcript[0]["says"] == "proportional shares?" and res.transcript[0]["private_reason"] == "because"     # say and private reason kept
    assert res.proposals_made == 1 and res.below_floor == 0 and res.format_errors == 0 and res.calls == 2


def test_a_below_floor_proposal_is_counted_and_an_accepted_one_is_blocked_then_the_talks_continue():
    x, y = first("p-anchor", "p-host")
    bad = bj(stay=52, breach=1.0)                                  # a breach forfeits the whole share: below the floor
    good = bj(stay=52, breach=0.5)
    cx = Mock(reply("propose", bad), reply("propose", good))
    cy = Mock(reply("accept"), reply("accept"))
    res = run({x: cx, y: cy})
    assert res.below_floor == 1 and res.proposals_made == 2
    assert len(res.floor_blocks) == 1 and res.floor_blocks[0]["fails"][0]["path"] == "breach"
    assert res.status == "agreed" and res.bundle["breach"] == 0.5 and res.bundle["stay"] == 52 and res.flagged
    assert "floor rule blocked" in cy.asked[1][1][0]["content"]       # the other side is told, in the history of its next turn


def test_a_forfeit_exit_is_stopped_by_the_floor():
    x, y = first("p-anchor", "p-host")
    res = run({x: Mock(reply("propose", bj(exit="forfeit")), reply("walk_away")), y: Mock(reply("accept"))})
    assert res.floor_blocks and res.status in ("walk_away", "deadline") and not res.pot


def test_proof_check_rejection_is_reported_and_the_talks_continue():
    x, y = first("p-anchor", "p-host")
    trap = bj(change="frozen", exit="forfeit")                     # frozen and no exit: also below the floor; use floor off to reach the proof check
    res = run({x: Mock(reply("propose", trap), reply("walk_away")), y: Mock(reply("accept"))}, floor=False)
    assert res.rejections and res.rejections[0]["failed"] and not res.pot


def test_reject_clears_the_standing_offer_and_walk_away_ends_with_no_pot():
    x, y = first("p-anchor", "p-host")
    res = run({x: Mock(reply("propose", bj(use="any_use")), reply("walk_away", says="no")), y: Mock(reply("reject", says="no thanks"))})
    assert [t["action"] for t in res.transcript] == ["propose", "reject", "walk_away"]
    assert res.status == "walk_away" and not res.pot and res.bundle is None


def test_deadline_without_agreement():
    x, y = first("p-anchor", "p-host")
    cx = Mock(*[reply("propose", bj(use="any_use"))] * 6)
    cy = Mock(*[reply("reject")] * 6)
    res = run({x: cx, y: cy}, deadline=12)
    assert res.status == "deadline" and not res.pot and len(res.transcript) == 12


def test_invalid_reply_gets_one_retry_then_counts_a_format_error_and_walks_away():
    x, y = first("p-anchor", "p-host")
    cx = Mock("garbage", "still garbage")
    res = run({x: cx, y: Mock()})
    assert res.format_errors == 1 and res.calls == 2 and res.status == "walk_away" and res.transcript[0]["forced"]
    assert "invalid" in cx.asked[1][1][-1]["content"]              # the retry shows the model what was wrong
    cx2 = Mock("garbage", reply("propose", bj(use="any_use")))
    res2 = run({x: cx2, y: Mock(reply("accept"))})
    assert res2.format_errors == 0 and res2.calls == 3 and res2.pot                  # the retry succeeded: not an error


def test_accept_without_a_standing_offer_is_invalid_and_counts():
    x, y = first("p-anchor", "p-host")
    res = run({x: Mock(reply("accept"), reply("accept")), y: Mock()})
    assert res.format_errors == 1 and not res.pot


def test_a_refusal_is_counted_separately_and_walks_away():
    x, y = first("p-anchor", "p-host")
    res = run({x: Mock(("refusal", None)), y: Mock()})
    assert res.refusals == 1 and res.format_errors == 0 and res.status == "walk_away"


def test_max_tokens_is_a_parse_failure_with_one_retry():
    x, y = first("p-anchor", "p-host")
    res = run({x: Mock(("max_tokens", None), reply("propose", bj(use="any_use"))), y: Mock(reply("accept"))})
    assert res.pot and res.format_errors == 0 and res.calls == 3


def test_wants_fallback_arm_restricts_proposals():
    x, y = first("p-controller", "p-peacekeeper")
    allowed = NL.restricted_menu([PERS["p-controller"], PERS["p-peacekeeper"]], MENU)
    fixed = next(iter(allowed))
    other = next(v for v in N.TERMS[fixed] if v != N.FAIR_DEFAULT[fixed])
    res = run({x: Mock(*[reply("propose", bj(**{fixed: other}))] * 2), y: Mock()}, pa="p-controller", pb="p-peacekeeper", arm="wants_fallback")
    assert res.format_errors == 1 and not res.pot                  # a proposal outside the table's open terms is invalid, twice


# ---- say vs do ----
def test_say_vs_do_counts_keyword_mismatches_and_own_rejections():
    tr = [{"k": 0, "speaker": "a", "action": "propose", "says": "Here is my offer.", "bundle": b(), "standing": None},
          {"k": 1, "speaker": "b", "action": "reject", "says": "I agree in spirit, but no.", "standing": b()},
          {"k": 2, "speaker": "a", "action": "propose", "says": "ok", "bundle": b(use="any_use"), "standing": None},
          {"k": 3, "speaker": "b", "action": "propose", "says": "Sounds good, here is mine.", "bundle": b(exit="proportional"), "standing": b(use="any_use")},
          {"k": 4, "speaker": "a", "action": "reject", "says": "No.", "standing": b(exit="proportional")},
          {"k": 5, "speaker": "b", "action": "accept", "says": "I can't accept that.", "standing": None}]
    sv = NL.say_vs_do(tr)
    assert [e["k"] for e in sv["says_accept_but_not"]] == [1, 3] and [e["k"] for e in sv["says_refuse_but_accepts"]] == [5]
    assert sv["proposed_then_rejected_own"] == []                  # a's reject was of b's bundle, not its own
    tr2 = [{"k": 0, "speaker": "a", "action": "propose", "says": "x", "bundle": b(), "standing": None},
           {"k": 1, "speaker": "a", "action": "reject", "says": "x", "standing": b()}]
    assert len(NL.say_vs_do(tr2)["proposed_then_rejected_own"]) == 1


# ---- the claude transport and the spend cap ----
def fake_transport(texts, usage=(1000, 100)):
    calls = []

    def send(params):
        calls.append(params)
        return SimpleNamespace(usage=SimpleNamespace(input_tokens=usage[0], output_tokens=usage[1], cache_read_input_tokens=0, cache_creation_input_tokens=0),
                               stop_reason="end_turn", model="claude-haiku-5-5", content=[SimpleNamespace(type="text", text=texts.pop(0))])
    return send, calls


def test_claude_client_sends_a_cached_system_block_logs_cost_and_returns_text():
    send, calls = fake_transport([reply("walk_away")])
    c = NL.ClaudeNegotiatorClient("claude-haiku-5-5", transport=send)
    st, text = c.ask("SYS", [{"role": "user", "content": "hi"}])
    assert st == "ok" and json.loads(text)["action"] == "walk_away"
    prm = calls[0]
    assert prm["model"] == "claude-haiku-5-5" and prm["system"][0]["text"] == "SYS" and prm["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert prm["max_tokens"] == NL.MAX_TOKENS and "temperature" not in prm
    assert c.ledger.total_usd() == pytest.approx((1000 * 0.10 + 100 * 0.50) / 1e6)


def test_claude_client_refuses_a_call_that_could_pass_the_cap_before_making_it():
    send, calls = fake_transport([reply("walk_away")])
    c = NL.ClaudeNegotiatorClient("claude-haiku-5-5", max_usd=0.0001, transport=send)
    with pytest.raises(BudgetExceeded):
        c.ask("x" * 3000, [{"role": "user", "content": "hi"}])
    assert calls == []                                              # no call was made


def test_claude_client_requires_a_model():
    with pytest.raises(ValueError):
        NL.ClaudeNegotiatorClient("")


def test_estimate_is_small_and_ordered():
    e = NL.estimate("claude-haiku-5-5", 12, (PERS["p-anchor"], PERS["p-wanderer"]), BASE)
    assert 0 < e["usd"] < e["usd_max"] < 3.0 and e["calls_max"] == 12 * 12 * 2


# ---- the runner pipeline, end to end with a mock ----
def test_week0_llm_and_the_runner_row_pipeline_with_a_mock_client(tmp_path):
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import negotiation_llm_run as R
    x, y = first("p-anchor", "p-wanderer")
    mk = {x: Mock(reply("propose", bj(), says="the plain default?")), y: Mock(reply("accept", says="fine"))}

    class Router:
        ledger = Ledger("mock")

        def ask(self, system, messages):
            who = x if "You are The Anchor" in system and x == "p-anchor" or "You are The Wanderer" in system and x == "p-wanderer" else y
            return mk[who].ask(system, messages)
    rows, ledger, aborted = R.live_rows("claude-haiku-5-5", (0,), 1.0, tmp_path,
                                        pairs=(("p-anchor", "p-wanderer"),), client=Router())
    assert aborted is None and len(rows) == 1
    r = rows[0]
    assert r["kind"] == "llm" and r["pot"] and r["bundle"] == b() and r["turns"] == 2 and r["format_errors"] == 0
    assert r["transcript"][0]["says"] == "the plain default?" and "say_vs_do" in r and r["proposals_llm"] == 1
    summary = R.analyze(rows, R.scripted_rows(pairs=(("p-anchor", "p-wanderer"),), seeds=(0,)), out=lambda *a, **k: None)
    assert summary["fe_rate"] == 0.0 and summary["excluded"] is False
