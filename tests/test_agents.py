"""Agent backends, all offline: mar.agents.http.post_json is replaced by a fake transport."""
import json
import random

import pytest

from mar.agents import base, env, http
from mar.agents.base import Ledger, MissingKeyError, ParseError
from mar.agents.jev import JevAgent
from mar.agents.llm import LLMAgent, parse_reply
from mar.agents.scripted import ScriptedAgent
from mar.mocks import Exploiter

OPTS = base.bucket_options()


@pytest.fixture(autouse=True)
def offline(monkeypatch, tmp_path):
    monkeypatch.setattr(env, "ENV_PATH", tmp_path / "no.env")
    monkeypatch.setattr(http, "sleep", lambda s: None)
    for k in ("OPENROUTER_API_KEY", "AIMLAPI_API_KEY", "MAR_LLM_MODEL"):
        monkeypatch.delenv(k, raising=False)

    def refuse(*a, **k):
        raise AssertionError("network call not mocked")
    monkeypatch.setattr(http, "post_json", refuse)


class Fake:
    """Records calls; replies from a queue or a function."""
    def __init__(self, replies):
        self.replies, self.calls = replies, []

    def __call__(self, url, headers, body, timeout=60.0):
        self.calls.append((url, headers, body))
        r = self.replies(body) if callable(self.replies) else self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def jev_reply(probs, build="typesafe/jev-1.14-20261001", tokens=500, usd=None, qkey="action"):
    top = max(probs, key=probs.get)
    r = {"model": build, "answers": {qkey: {"choice": top, "confidence": probs[top], "probabilities": probs}},
         "usage": {"input_tokens": tokens, "output_tokens": 3}, "meta": {}}
    if usd is not None:
        r["meta"]["usd_spent"] = usd
    return r


def peaked(label="11-20", mass=0.89):
    rest = (1 - mass) / (len(OPTS) - 1)
    return {k: (mass if k == label else rest) for k in OPTS}


# ---- buckets and probabilities -------------------------------------------------------------

def test_eleven_buckets_cover_0_to_100():
    assert len(base.BUCKET_LABELS) == 11 and base.BUCKET_LABELS[:3] == ["0", "1-10", "11-20"]
    assert base.BUCKET_LABELS[-1] == "91-100"
    for n in range(0, 101):
        lo, hi = [int(x) for x in base.bucket_of(n).split("-")] if n else (0, 0)
        assert lo <= n <= hi
    assert base.bucket_of(-4) == "0" and base.bucket_of(250) == "91-100"


def test_bucket_sampling_is_in_range_and_deterministic():
    a = [base.sample_in_bucket("31-40", random.Random(7)) for _ in range(1)]
    r1, r2 = random.Random(3), random.Random(3)
    s1 = [base.sample_in_bucket("31-40", r1) for _ in range(50)]
    s2 = [base.sample_in_bucket("31-40", r2) for _ in range(50)]
    assert s1 == s2 and all(31 <= x <= 40 for x in s1) and len(set(s1)) > 5 and a
    assert base.sample_in_bucket("0", random.Random(0)) == 0


def test_temperature_scaling_flattens_sharpens_and_renormalizes():
    p = {"a": 0.89, "b": 0.07, "c": 0.04}
    assert base.temperature_scale(p, 1.0) == pytest.approx(p)
    hot, cold = base.temperature_scale(p, 3.0), base.temperature_scale(p, 0.5)
    assert sum(hot.values()) == pytest.approx(1) and hot["a"] < 0.89 and hot["c"] > 0.04
    assert cold["a"] > 0.89
    z = base.temperature_scale({"a": 0.5, "b": 0.5, "c": 0.0}, 2.0)
    assert z["c"] == 0.0 and z["a"] == pytest.approx(0.5)
    with pytest.raises(ValueError):
        base.temperature_scale(p, 0)


def test_sample_label_follows_probabilities():
    rng = random.Random(1)
    draws = [base.sample_label({"a": 0.8, "b": 0.2, "c": 0.0}, rng) for _ in range(2000)]
    assert "c" not in draws and 0.74 < draws.count("a") / 2000 < 0.86
    rng2 = random.Random(1)
    assert draws[:20] == [base.sample_label({"a": 0.8, "b": 0.2, "c": 0.0}, rng2) for _ in range(20)]


# ---- jev -----------------------------------------------------------------------------------

def test_jev_request_shape_parsing_and_cost_logging(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k-test")
    fake = Fake([jev_reply(peaked(), tokens=1000)])
    monkeypatch.setattr(http, "post_json", fake)
    led = Ledger("jev")
    probs = JevAgent(ledger=led).decide("state text", OPTS)
    url, headers, body = fake.calls[0]
    assert url == "https://openrouter.ai/api/alpha/decisions" and headers["Authorization"] == "Bearer k-test"
    assert body["model"] == "typesafe/jev-1.14" and body["state"] == "state text"
    q = body["questions"]["action"]
    assert q["type"] == "choice" and q["criteria"] == OPTS
    assert sum(probs.values()) == pytest.approx(1) and probs["11-20"] == pytest.approx(0.89)
    s = led.summary()
    assert s["model_builds"] == ["typesafe/jev-1.14-20261001"] and s["calls"] == 1
    assert s["input_tokens"] == 1000 and s["output_tokens"] == 3
    assert s["usd"] == pytest.approx(1000 * 0.042 / 1e6)


def test_jev_prefers_reported_usd_and_aimlapi_provider(monkeypatch):
    monkeypatch.setenv("AIMLAPI_API_KEY", "k2")
    fake = Fake([jev_reply(peaked(), usd=0.5)])
    monkeypatch.setattr(http, "post_json", fake)
    led = Ledger("jev")
    JevAgent(provider="aimlapi", ledger=led).decide("s", OPTS)
    assert fake.calls[0][0] == "https://api.aimlapi.com/v1/decisions" and led.summary()["usd"] == 0.5


def test_jev_temperature_applied_to_returned_probs(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(http, "post_json", Fake(lambda b: jev_reply(peaked())))
    p1 = JevAgent(temperature=1.0).decide("s", OPTS)
    p3 = JevAgent(temperature=3.0).decide("s", OPTS)
    assert p3["11-20"] < p1["11-20"] and sum(p3.values()) == pytest.approx(1)


def test_jev_sampling_deterministic_under_seed(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(http, "post_json", Fake(lambda b: jev_reply(peaked(mass=0.3))))
    probs = JevAgent(temperature=2.0).decide("s", OPTS)

    def draw(seed):
        r = random.Random(seed)
        return [base.sample_in_bucket(base.sample_label(probs, r), r) for _ in range(30)]
    assert draw(5) == draw(5) and draw(5) != draw(6)


def test_jev_cache_hits_skip_network_and_log_zero_cost(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    fake = Fake([jev_reply(peaked(), tokens=800)])
    monkeypatch.setattr(http, "post_json", fake)
    led = Ledger("jev")
    a = JevAgent(ledger=led, cache_dir=tmp_path / "c")
    first = a.decide("same context", OPTS)
    second = a.decide("same context", OPTS)
    assert first == second and len(fake.calls) == 1
    s = led.summary()
    assert s["calls"] == 1 and s["cache_hits"] == 1 and s["input_tokens"] == 800
    JevAgent(ledger=led, cache_dir=tmp_path / "c", temperature=2.0).decide("same context", OPTS)  # T not in key
    assert len(fake.calls) == 1
    fake.replies.append(jev_reply(peaked()))
    a.decide("other context", OPTS)
    assert len(fake.calls) == 2 and len(list((tmp_path / "c").glob("*.json"))) == 2


def test_jev_cache_works_without_a_key(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(http, "post_json", Fake([jev_reply(peaked())]))
    JevAgent(cache_dir=tmp_path).decide("c", OPTS)
    monkeypatch.delenv("OPENROUTER_API_KEY")
    JevAgent(cache_dir=tmp_path).decide("c", OPTS)  # no key, no network, still fine


def test_jev_message_returns_typed_report(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    fake = Fake(lambda b: jev_reply(peaked("31-40", 0.99), qkey="report"))
    monkeypatch.setattr(http, "post_json", fake)
    rep = JevAgent(rng=random.Random(0)).message("ctx", base.BUCKET_LABELS)
    assert rep.value == "31-40" and rep.talk == "" and "report" in fake.calls[0][2]["questions"]


def test_jev_refuses_latest_and_bad_provider_and_bad_response(monkeypatch):
    with pytest.raises(ValueError, match="latest"):
        JevAgent(model="typesafe/jev-latest")
    with pytest.raises(ValueError, match="provider"):
        JevAgent(provider="nope")
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(http, "post_json", Fake([{"model": "m", "answers": {}}]))
    with pytest.raises(ParseError):
        JevAgent().decide("s", OPTS)


def test_retry_with_backoff_then_success_and_give_up(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    waits = []
    monkeypatch.setattr(http, "sleep", waits.append)
    fake = Fake([http.HttpError(429, "slow down"), http.HttpError(503, "x"), jev_reply(peaked())])
    monkeypatch.setattr(http, "post_json", fake)
    JevAgent().decide("s", OPTS)
    assert len(fake.calls) == 3 and waits == [1.0, 2.0]
    monkeypatch.setattr(http, "post_json", Fake([http.HttpError(401, "bad key")]))
    with pytest.raises(http.HttpError):
        JevAgent().decide("t", OPTS)  # 401 is not retried
    monkeypatch.setattr(http, "post_json", Fake(lambda b: http.HttpError(500, "down")))
    with pytest.raises(http.HttpError):
        JevAgent().decide("u", OPTS)


# ---- llm -----------------------------------------------------------------------------------

def chat_reply(content, build="vendor/model-x", pin=100, pout=20, cost=None):
    u = {"prompt_tokens": pin, "completion_tokens": pout}
    if cost is not None:
        u["cost"] = cost
    return {"model": build, "choices": [{"message": {"content": content}}], "usage": u}


def test_llm_decide_message_parse_and_cost(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    fake = Fake([chat_reply('{"action": "1-10", "report": "", "talk": "go slow"}'),
                 chat_reply('{"action": "", "report": "11-20", "talk": "I will take a bit more"}', cost=0.002)])
    monkeypatch.setattr(http, "post_json", fake)
    led = Ledger("llm")
    a = LLMAgent(model="vendor/model-x", ledger=led, price_in=1.0, price_out=2.0)
    probs = a.decide("ctx", OPTS)
    assert probs["1-10"] == 1.0 and sum(probs.values()) == 1.0
    rep = a.message("ctx", base.BUCKET_LABELS)
    assert (rep.value, rep.talk) == ("11-20", "I will take a bit more")
    url, headers, body = fake.calls[0]
    assert url == "https://openrouter.ai/api/v1/chat/completions" and body["model"] == "vendor/model-x"
    assert headers["Authorization"] == "Bearer k"
    s = led.summary()
    assert s["calls"] == 2 and s["input_tokens"] == 200 and s["model_builds"] == ["vendor/model-x"]
    assert s["usd"] == pytest.approx((100 * 1 + 20 * 2) / 1e6 + 0.002)


def test_llm_strict_parse_one_retry_then_error(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    fake = Fake([chat_reply("I think 1-10"), chat_reply('```json\n{"action":"0","talk":"ok"}\n```')])
    monkeypatch.setattr(http, "post_json", fake)
    led = Ledger("llm")
    assert LLMAgent(model="m", ledger=led).decide("c", OPTS)["0"] == 1.0
    assert len(fake.calls) == 2 and "invalid" in fake.calls[1][2]["messages"][-1]["content"]
    assert led.summary()["calls"] == 2
    monkeypatch.setattr(http, "post_json", Fake([chat_reply('{"action":"99"}'), chat_reply("nope")]))
    with pytest.raises(ParseError):
        LLMAgent(model="m").decide("c", OPTS)


def test_parse_reply_rules():
    assert parse_reply('{"action":"a","talk":"x"}', {"a": ""})["action"] == "a"
    for bad in ('[1]', '{"action":"b"}', '{"action":"a","talk":3}', "{"):
        with pytest.raises(ParseError):
            parse_reply(bad, {"a": ""})
    with pytest.raises(ParseError):
        parse_reply('{"report":"zz"}', None, ["a"])


def test_llm_needs_a_model(monkeypatch):
    with pytest.raises(ValueError, match="MAR_LLM_MODEL"):
        LLMAgent()
    monkeypatch.setenv("MAR_LLM_MODEL", "from/env")
    assert LLMAgent().model == "from/env"


# ---- keys and env --------------------------------------------------------------------------

def test_missing_key_names_the_env_var():
    with pytest.raises(MissingKeyError, match="OPENROUTER_API_KEY"):
        JevAgent().decide("s", OPTS)
    with pytest.raises(MissingKeyError, match="AIMLAPI_API_KEY"):
        JevAgent(provider="aimlapi").decide("s", OPTS)
    with pytest.raises(MissingKeyError, match="OPENROUTER_API_KEY"):
        LLMAgent(model="m").decide("s", OPTS)


def test_dotenv_loader_reads_file_without_overriding(monkeypatch, tmp_path):
    p = tmp_path / ".env"
    p.write_text('# c\nOPENROUTER_API_KEY="from-file"\nexport AIMLAPI_API_KEY=abc\nEMPTY=\nMAR_LLM_MODEL=x/y\n')
    monkeypatch.setattr(env, "ENV_PATH", p)
    monkeypatch.setenv("MAR_LLM_MODEL", "already")
    assert env.require_key("OPENROUTER_API_KEY") == "from-file"
    assert env.get("AIMLAPI_API_KEY") == "abc" and env.get("EMPTY") is None
    assert env.get("MAR_LLM_MODEL") == "already"


def test_env_ignored_and_example_is_empty():
    from pathlib import Path
    root = Path(__file__).parent.parent
    assert ".env" in (root / ".gitignore").read_text().splitlines()
    for line in (root / ".env.example").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            assert line.split("=", 1)[1] == ""


# ---- scripted and budget -------------------------------------------------------------------

def test_scripted_wraps_a_mock():
    a = ScriptedAgent(Exploiter(size=10))
    obs = json.dumps({"month": 0, "subround": 0, "pool": 100, "month_total": 0, "own_month_total": 0, "n_agents": 4})
    assert a.decide(obs, OPTS)["1-10"] == 1.0
    assert a.message(obs, base.BUCKET_LABELS).value == "1-10"


def test_ledger_budget_limit():
    led = Ledger("jev", limit_usd=0.01)
    led.record("m", 1, 1, 0.006)
    with pytest.raises(base.BudgetExceeded):
        led.record("m", 1, 1, 0.006)


def test_jev_attempt_tag_makes_a_repeat_a_fresh_call_while_attempt_zero_keeps_the_old_cache_key(monkeypatch, tmp_path):
    """Correctness review 2026-11-10, finding 1: repeated attempts must not replay one cached response."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "k-test")
    fake = Fake([jev_reply(peaked()), jev_reply(peaked()), jev_reply(peaked())])
    monkeypatch.setattr(http, "post_json", fake)
    a0 = JevAgent(ledger=Ledger("jev"), cache_dir=tmp_path)
    a0.decide("same context", OPTS)
    a0.decide("same context", OPTS)                          # attempt 0 repeated: cached, no second call
    assert len(fake.calls) == 1
    a1 = JevAgent(ledger=Ledger("jev"), cache_dir=tmp_path)
    a1.sample_tag = "attempt-1"
    a1.decide("same context", OPTS)                          # attempt 1: a new cache entry, a real call
    assert len(fake.calls) == 2
    a1.decide("same context", OPTS)
    assert len(fake.calls) == 2 and len(list(tmp_path.glob("*.json"))) == 2
