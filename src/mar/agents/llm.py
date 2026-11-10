"""Chat-completions agent (OpenRouter). The model id is a config value the author fills in
(--model or MAR_LLM_MODEL in .env). It must reply with one JSON object:
  {"action": <option key>, "report": <vocabulary word>, "talk": <short free text>}
parsed strictly; one retry with the parse error shown to the model, then ParseError.
"""
import json
import random
import re

from . import env, http
from .base import Agent, Ledger, ParseError, Report

URL = "https://openrouter.ai/api/v1/chat/completions"
SYSTEM = ("You are one fisher in a shared lake. Reply with ONLY a JSON object, no other text: "
          '{"action": <one option key or "">, "report": <one vocabulary word or "">, "talk": <one short sentence>}.')


def parse_reply(text: str, options=None, vocabulary=None) -> dict:
    m = re.fullmatch(r"\s*```(?:json)?\s*(.*?)\s*```\s*", text, re.S)  # ASSUMED: a lone code fence is tolerated
    try:
        obj = json.loads(m.group(1) if m else text)
    except json.JSONDecodeError as e:
        raise ParseError(f"reply is not JSON ({e.msg})")
    if not isinstance(obj, dict):
        raise ParseError("reply is not a JSON object")
    if not isinstance(obj.get("talk", ""), str):
        raise ParseError('"talk" must be a string')
    if options is not None and obj.get("action") not in options:
        raise ParseError(f'"action" must be one of {list(options)}')
    if vocabulary is not None and obj.get("report") not in vocabulary:
        raise ParseError(f'"report" must be one of {list(vocabulary)}')
    return obj


class LLMAgent(Agent):
    def __init__(self, model=None, temperature=0.7, ledger=None, price_in=0.0, price_out=0.0, max_tokens=200,
                 rng=None):
        self.model = model or env.get("MAR_LLM_MODEL")
        if not self.model:
            raise ValueError("no LLM model set. Pass --model <openrouter model id> or put MAR_LLM_MODEL=... in .env")
        self.T, self.price_in, self.price_out, self.max_tokens = temperature, price_in, price_out, max_tokens
        self.ledger = ledger or Ledger("llm")
        self.rng = rng or random.Random(0)

    def _chat(self, messages) -> str:
        headers = {"Authorization": f"Bearer {env.require_key('OPENROUTER_API_KEY')}"}
        resp = http.post_with_retry(URL, headers, {"model": self.model, "messages": messages,
                                                   "temperature": self.T, "max_tokens": self.max_tokens,
                                                   "usage": {"include": True}})
        u = resp.get("usage") or {}
        tin, tout = u.get("prompt_tokens") or 0, u.get("completion_tokens") or 0
        usd = u.get("cost")
        if usd is None:
            usd = (tin * self.price_in + tout * self.price_out) / 1e6
        self.ledger.record(resp.get("model") or self.model, tin, tout, usd)
        try:
            return resp["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            raise ParseError("chat response has no choices[0].message.content")

    def _ask(self, context, options=None, vocabulary=None) -> dict:
        lines = [context]
        if options is not None:
            lines.append("Action options:\n" + "\n".join(f"- {k}: {d}" for k, d in options.items()))
        if vocabulary is not None:
            vocab = list(vocabulary)
            lines.append("Report: state the total fish you intend to catch this month, one of: " + ", ".join(vocab))
        msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": "\n\n".join(lines)}]
        text = self._chat(msgs)
        try:
            return parse_reply(text, options, vocabulary)
        except ParseError as e:
            msgs += [{"role": "assistant", "content": text},
                     {"role": "user", "content": f"That reply was invalid: {e}. Reply again with only the JSON object."}]
            return parse_reply(self._chat(msgs), options, vocabulary)

    def decide(self, context, options):
        obj = self._ask(context, options=options)
        return {k: 1.0 if k == obj["action"] else 0.0 for k in options}

    def message(self, context, vocabulary):
        vocab = list(vocabulary)
        obj = self._ask(context, vocabulary=vocab)
        return Report(obj["report"], "intent", obj.get("talk", ""))
