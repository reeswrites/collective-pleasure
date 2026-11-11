"""Regression pin, written BEFORE the IT1 harness work (docs/plans/inventive-seam-next.md): fixed-seed outcomes of the existing
ladder harness must not change. Scripted mocks only; no model calls. The pinned values are in tests/data/ladder_pin_2026-11-10.json,
computed from commit 423604b with the same code as below."""
import hashlib
import json
from pathlib import Path

import pytest

from mar import ladder_live as LL
from mar import seam_depth as S

PIN = json.loads((Path(__file__).parent / "data" / "ladder_pin_2026-11-10.json").read_text())
SPEC = LL.ModelSpec("llm", "mock/model")


class Scr:
    uses_tag = False

    def __init__(self, choose):
        self.choose, self.rng = choose, None

    def decide(self, ctx, opts):
        p = self.choose(LL.parse_state(ctx), opts)
        return {k: 1.0 if k == p else 0.0 for k in opts}


def spam(key):
    return lambda o, opts: key if key in opts else "work"


def h(x, n):
    return hashlib.sha1(x.encode()).hexdigest()[:n]


@pytest.mark.parametrize("key", ["request:stay_home", "gift_pooled", "leave:0", "request:no_contact"])
@pytest.mark.parametrize("arm", ["capability", "win"])
def test_fixed_seed_runs_are_unchanged(key, arm):
    res = LL.run_model(SPEC, lambda s, l: Scr(spam(key)), rules=tuple(LL.LADDER_ALL), seeds=(0, 1), arm=arm)
    got = [[r["rule"], r["seed"], r["class"], r["moves"], h(json.dumps(r["decision_seq"]), 12)] for r in res["runs"]]
    assert got == PIN[f"{key}|{arm}"]


def test_default_prompts_estimates_and_formal_model_are_unchanged():
    obs, view = dict(LL._SAMPLE_OBS), dict(LL._SAMPLE_VIEW)
    for arm in ("capability", "win"):
        for n in LL.LADDER_ALL:
            rules = LL.rules_text(S.load_ladder(n))
            ctx = (LL.v2_pair_context(n, rules, obs, {**obs, "role": "B"}, view, view, "s0-a0", arm) if n in LL.PAIR_RULES
                   else LL.v2_context(n, "A", rules, obs, view, "s0-a0", arm))
            assert h(ctx, 16) == PIN[f"prompt|{arm}|{n}"], (arm, n)
    for arm in ("capability", "win", "propensity"):
        e = LL.estimate(LL.ModelSpec("claude", "claude-sonnet-5-5"), rules=tuple(LL.LADDER_ALL), seeds=tuple(range(12)), arm=arm)
        assert [e["calls"], e["tokens_in"], round(e["usd"], 6)] == PIN[f"estimate|{arm}"]
    for n in LL.LADDER_ALL:
        r = S.search(S.load_ladder(n), 3, 0, S.BUDGET_DEFAULT)
        assert [r["status"], r["depth"], r["agents"], r["n_traces"], r["evaluated"]] == PIN[f"fm|{n}"]
