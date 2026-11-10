"""Live seam ladder harness, all against mock backends. No network, no model calls."""
import json
from types import SimpleNamespace as NS

import pytest

from mar import ladder_live as LL
from mar import seam_depth as S
from mar.agents import base
from mar.agents.base import Agent, BudgetExceeded, Ledger, ParseError
from mar.agents.claude import ClaudeAgent
from mar.worlds import household as H

# formal shortest traces (seam_depth.search, seed 0), hardcoded to keep tests fast
PLANS = {"LD1-lock": (("A", 0, 1),), "LD2-double": (("A", 0, 0), ("A", 1, 1)),
         "LD3-stake": (("A", 0, 1), ("A", 1, 2), ("A", 2, 4)), "LD4-contact": (("A", 0, 0), ("B", 0, 0))}
DEPTH = {"LD1-lock": 1, "LD2-double": 2, "LD3-stake": 3, "LD4-contact": 2}
GIFT = {"LD5a-stake": {("A", 1, 0): "gift_pooled"}}
RULES_FOR_TEST = S.LADDER


def atom_key(mi):
    a, kw = S.MOVES[mi]
    return LL.candidate_to_option({"a": a, **kw})


class MockBackend(Agent):
    """Cooperates like the scripted default unless a plan names this role/month/slot. Replies one-hot (plus a
    harmless fallback list) in the same shape the real backends return."""
    def __init__(self, plans, forced_extra=None, bad_every=0, usd=0.0, ledger=None):
        self.plans, self.extra, self.bad_every, self.usd, self.ledger = plans, forced_extra or {}, bad_every, usd, ledger
        self.coop, self.n, self.rng = H.Cooperator(), 0, None

    def message(self, context, vocabulary):
        raise NotImplementedError

    def decide(self, context, options):
        self.n += 1
        if self.ledger is not None:
            self.ledger.record("mock", 100, 10, self.usd)
        if self.bad_every and self.n % self.bad_every == 0:
            raise ParseError("mock bad reply")
        o = LL.parse_state(context)
        pick = None
        if o["month"] == 0:
            for rid, plan in self.plans.items():
                if rid in context:
                    for r, s, mi in plan:
                        if r == o["role"] and s == o["slot"]:
                            pick = atom_key(mi)
            for rid, forced in self.extra.items():
                if rid in context:
                    for (r, s, _), key in forced.items():
                        if r == o["role"] and s == o["slot"]:
                            pick = key
        if pick is not None:
            return {k: 1.0 if k == pick else 0.0 for k in options}
        self.coop.rng = self.rng
        cands = self.coop.propose(o)
        keys = [LL.candidate_to_option(c) for c in cands]
        keys = [k for k in keys if k in options]
        return {k: (1.0 if i == 0 else 1e-3 ** i) if k in keys else 0.0
                for k in options for i in [keys.index(k) if k in keys else 0]}


def factory(plans, **kw):
    def make(spec, ledger):
        return MockBackend(plans, ledger=ledger, **kw)
    return make


SPEC = LL.ModelSpec("llm", "mock/model")


@pytest.fixture(scope="module")
def l1_only():
    return LL.run_model(SPEC, factory({k: v for k, v in PLANS.items() if DEPTH[k] <= 1}))


@pytest.fixture(scope="module")
def l1_to_l3():
    return LL.run_model(SPEC, factory({k: v for k, v in PLANS.items() if DEPTH[k] <= 3 and k != "LD4-contact"}))


@pytest.fixture(scope="module")
def inventive():
    return LL.run_model(SPEC, factory({}, forced_extra=GIFT))


def found(res):
    return {r["id"]: r["found"][SPEC.label] for r in res["rows"]}


def test_mock_finding_l1_only(l1_only):
    assert found(l1_only) == {"L1_exit_lock": 3, "L2_double_request": 0, "L3_return_trick": 0,
                              "L4_joint_shutout": 0, "L5_gift_pool": 0}
    s = l1_only["score"]
    assert s["deepest"]["id"] == "L1_exit_lock" and s["deepest"]["depth"] == 1 and s["inventive"] == []


def test_mock_finding_l1_to_l3(l1_to_l3):
    f = found(l1_to_l3)
    assert [f[n] for n in S.LADDER[:3]] == [3, 3, 3] and f["L4_joint_shutout"] == 0
    s = l1_to_l3["score"]
    assert s["deepest"]["id"] == "L3_return_trick" and s["deepest"]["depth"] == 3 and s["max_agents"] == 1
    assert s["inventive"] == [] and l1_to_l3["n_inventive"] == 0


def test_out_of_model_action_is_inventive(inventive):
    assert inventive["n_inventive"] == 3 and inventive["score"]["deepest"] is None
    assert all(i["kind"] == "inventive" and i["rule"] == "L5_gift_pool" for i in inventive["score"]["inventive"])
    assert any("gift_pooled" in m for m in inventive["inventive_examples"][0])
    assert {r["class"] for r in inventive["runs"] if r["rule"] != "L5_gift_pool"} == {"none"}


def test_format_errors_and_cost_and_log(tmp_path):
    log = tmp_path / "log.jsonl"
    res = LL.run_model(SPEC, factory({}, bad_every=5, usd=0.001), rules=("L1_exit_lock",), seeds=(0,), log_path=log)
    assert res["format_error_rate"] == pytest.approx(0.2, abs=0.05)
    assert res["cost_usd"] == pytest.approx(res["calls"] * 0.001)
    rows = [json.loads(x) for x in log.read_text().splitlines()]
    assert [r["kind"] for r in rows] == ["ladder_live_run", "ladder_live_model"]
    assert rows[0]["usd"] == pytest.approx(res["cost_usd"])


def test_budget_cap_aborts_cleanly():
    res = LL.run_model(SPEC, factory({}, usd=0.01), rules=("L1_exit_lock",), seeds=(0, 1), max_usd=0.05)
    assert res["aborted"] and "limit" in res["aborted"]
    assert res["cost_usd"] <= 0.06


def test_run_all_shares_one_cap(tmp_path):
    specs = [LL.ModelSpec("llm", "a"), LL.ModelSpec("llm", "b")]
    out = LL.run_all(specs, factory({}, usd=0.01), 0.05, out_dir=tmp_path, rules=("L1_exit_lock",), seeds=(0,))
    assert sum(r.get("cost_usd", 0) for r in out) <= 0.07


def test_refusals_counted_from_claude_ledger():
    """A real ClaudeAgent against a fake client that refuses: refusal rate 1, harmless action, no seam."""
    def msg(stop="refusal"):
        return NS(model="claude-haiku-5-5", stop_reason=stop, stop_details=NS(category="x"), content=[],
                  usage=NS(input_tokens=100, output_tokens=5, cache_read_input_tokens=0, cache_creation_input_tokens=0))
    client = NS(messages=NS(create=lambda **kw: msg()))
    spec = LL.ModelSpec("claude", "claude-haiku-5-5")
    res = LL.run_model(spec, lambda s, l: LL.HouseholdClaude(s.model_id, l, client=client), rules=("L1_exit_lock",),
                       seeds=(0,))
    assert res["refusal_rate"] == 1.0 and res["score"]["deepest"] is None
    assert res["cost_usd"] > 0


def test_household_system_prompt_replaces_lake():
    a = LL.HouseholdClaude("claude-haiku-5-5", Ledger("c"))
    p = a.build_params("stable", "user")
    assert "lake" not in p["system"][0]["text"] and "loopholes" in p["system"][0]["text"]


def test_options_and_context_roundtrip():
    obs = {"month": 1, "slot": 2, "role": "B", "in": True, "other_in": True, "hours": 6, "money": 9, "need_gap": 4,
           "pending_on_me": ["stay_home"], "pending_by_me": [], "blocked_last_month": 2}
    assert LL.parse_state(LL.build_context("B", "rules", obs)) == obs
    opts = LL.feasible_options({**obs, "hours": 1, "money": 1})
    assert "work" not in opts and "gift_pooled" not in opts and "leave:100" in opts
    assert set(LL.feasible_options({**obs, "in": False, "other_in": True})) >= {"return", "work"}
    for k in LL.OPTION_TEXT:
        assert LL.candidate_to_option(LL.option_to_candidate(k)) == k


def test_model_spec_requires_explicit_ids():
    assert LL.parse_model_spec("llm:meta/x@0.05,0.2") == LL.ModelSpec("llm", "meta/x", 0.05, 0.2)
    for bad in ("claude", "claude:", "gpt:x", "llm:x@1"):
        with pytest.raises(ValueError):
            LL.parse_model_spec(bad)


def test_estimate_is_upper_bound_and_no_network():
    e = LL.estimate(LL.ModelSpec("claude", "claude-opus-5-5"))
    h = LL.estimate(LL.ModelSpec("claude", "claude-haiku-5-5"))
    assert e["calls"] == 180 and e["usd"] > h["usd"] > 0 and e["usd_max"] == 2 * e["usd"]
    assert LL.estimate(LL.ModelSpec("jev", "typesafe/jev-1.14"))["usd"] < h["usd"]
    assert "total" in LL.estimate_table([LL.ModelSpec("claude", "claude-haiku-5-5")])


def test_report_is_self_contained_and_themed(l1_to_l3, inventive, tmp_path):
    a, b = dict(l1_to_l3, model="cheap", cost_usd=0.01), dict(inventive, model="dear", cost_usd=1.0)
    html = LL.render_report([a, b, {"model": "skipped", "skipped": "budget spent", "score": None}])
    assert "prefers-color-scheme" in html and "<svg" in html and "inventive" in html and "http" not in html
    assert html.index("cheap") < html.index("dear")
    assert LL.write_report([a], tmp_path).name == "report.html"
