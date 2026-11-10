"""Claude through the official `anthropic` SDK. No hardcoded model: the caller must pass one (--model).

Auth: anthropic.Anthropic() with no explicit key, so the SDK resolves ANTHROPIC_API_KEY or an `ant auth login`
profile. Request: messages.create(model, max_tokens=1024, system=[stable block with cache_control], messages=[state],
output_config={"effort": "low"}). No temperature, top_p, top_k or thinking budget (400 on current models).
The reply is the same strict JSON as the OpenRouter backend. stop_reason is checked before content is read:
"refusal" becomes a no-op action and is counted; "max_tokens" counts as a parse failure (one retry).

Prices are USD per 1M tokens (input, output) as given by the author on 2026-11-10; cache reads cost 0.1x input and
cache writes 1.25x input (ASSUMED standard 5-minute multipliers); Message Batches cost 0.5x.
"""
import random

import anthropic

from . import http
from .adapter import STATE_MARK
from .base import Agent, AgentError, Ledger, ParseError, Report
from .llm import SYSTEM, parse_reply

PRICES = {"claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.0, 10.0), "claude-opus-5-5": (4.0, 20.0)}
CACHE_READ_MULT, CACHE_WRITE_MULT, BATCH_MULT = 0.1, 1.25, 0.5
RETRY_5XX = 2
KEY_HINT = "Set ANTHROPIC_API_KEY or run `ant auth login`. Never paste a key into chat."


def claude_cost(model, input_tokens, output_tokens, cache_read=0, cache_write=0, batch=False):
    """USD for one call, or None if the model has no known price."""
    if model not in PRICES:
        return None
    pin, pout = PRICES[model]
    usd = (input_tokens * pin + cache_read * pin * CACHE_READ_MULT + cache_write * pin * CACHE_WRITE_MULT
           + output_tokens * pout) / 1e6
    return usd * (BATCH_MULT if batch else 1.0)


def require_model(model):
    if not model:
        raise ValueError("claude agents need an explicit model: pass --model (options: "
                         + ", ".join(f"{m} ${p[0]:g}/${p[1]:g} per 1M in/out" for m, p in PRICES.items()) + ")")
    return model


class ClaudeAgent(Agent):
    def __init__(self, model=None, ledger=None, client=None, transport=None, batch=False, max_tokens=1024,
                 effort="low", rng=None):
        self.model = require_model(model)
        self.ledger = ledger or Ledger("claude")
        self._client, self._transport, self.batch = client, transport, batch
        self.max_tokens, self.effort = max_tokens, effort
        self.rng = rng or random.Random(0)

    # -- transport ------------------------------------------------------------------------
    def _client_or_new(self):
        if self._client is None:
            try:
                self._client = anthropic.Anthropic()  # SDK resolves the key or profile; SDK retries 429/5xx itself
            except Exception as e:
                raise AgentError(f"could not create the Anthropic client ({e}). {KEY_HINT}")
        return self._client

    def _direct(self, params):
        for attempt in range(RETRY_5XX + 1):
            try:
                return self._client_or_new().messages.create(**params)
            except anthropic.RateLimitError as e:
                raise AgentError(f"Anthropic rate limit after the SDK's retries: {e}")
            except anthropic.AuthenticationError as e:
                raise AgentError(f"Anthropic rejected the credentials ({e}). {KEY_HINT}")
            except anthropic.APIStatusError as e:
                if e.status_code >= 500 and attempt < RETRY_5XX:
                    http.sleep(2.0 ** attempt)
                    continue
                raise AgentError(f"Anthropic API error {e.status_code}: {e}")
            except anthropic.APIConnectionError as e:
                raise AgentError(f"could not reach the Anthropic API: {e}")
            except TypeError as e:  # SDK raises this when no auth can be resolved
                raise AgentError(f"no Anthropic credentials found ({e}). {KEY_HINT}")

    def _send(self, params):
        return (self._transport or self._direct)(params)

    def build_params(self, stable, user):
        """Stable text goes in the cached system block and must be byte-identical across calls."""
        return {"model": self.model, "max_tokens": self.max_tokens,
                "system": [{"type": "text", "text": SYSTEM + "\n\n" + stable, "cache_control": {"type": "ephemeral"}}],
                "messages": [{"role": "user", "content": user}], "output_config": {"effort": self.effort}}

    # -- one call, with stop_reason handling --------------------------------------------------
    def _call(self, params):
        """-> ("ok", text) | ("refusal", None) | ("max_tokens", None)."""
        resp = self._send(params)
        u = resp.usage
        tin, tout = u.input_tokens or 0, u.output_tokens or 0
        cr, cw = getattr(u, "cache_read_input_tokens", 0) or 0, getattr(u, "cache_creation_input_tokens", 0) or 0
        self.ledger.record(getattr(resp, "model", None) or self.model, tin, tout,
                           claude_cost(self.model, tin, tout, cr, cw, self.batch), cache_read=cr, cache_write=cw)
        if resp.stop_reason == "refusal":
            self.ledger.note_refusal(getattr(getattr(resp, "stop_details", None), "category", None))
            return "refusal", None
        if resp.stop_reason == "max_tokens":
            return "max_tokens", None
        return "ok", "".join(b.text for b in resp.content if b.type == "text")

    def _ask(self, context, options=None, vocabulary=None):
        """-> parsed dict, or None if the model refused."""
        stable, _, state = context.partition(STATE_MARK)
        if not state:
            stable, state = "", context
        lines = [state]
        if options is not None:
            lines.append("Action options:\n" + "\n".join(f"- {k}: {d}" for k, d in options.items()))
        if vocabulary is not None:
            lines.append("Report: state the total fish you intend to catch this month, one of: "
                         + ", ".join(list(vocabulary)))
        params = self.build_params(stable, "\n\n".join(lines))
        why = None
        for attempt in range(2):
            status, text = self._call(params)
            if status == "refusal":
                return None
            try:
                if status == "max_tokens":
                    raise ParseError("reply was cut off at max_tokens")
                return parse_reply(text, options, vocabulary)
            except ParseError as e:
                if attempt == 1:
                    raise
                why = str(e)
                msgs = list(params["messages"])
                msgs += [{"role": "assistant", "content": text or "(cut off)"},
                         {"role": "user", "content": f"That reply was invalid: {why}. Reply again with only the JSON object."}]
                params = {**params, "messages": msgs}

    def decide(self, context, options):
        obj = self._ask(context, options=options)
        pick = "0" if obj is None and "0" in options else (obj or {}).get("action")
        if pick is None:
            pick = next(iter(options))
        return {k: 1.0 if k == pick else 0.0 for k in options}

    def message(self, context, vocabulary):
        vocab = list(vocabulary)
        obj = self._ask(context, vocabulary=vocab)
        if obj is None:
            return Report("0" if "0" in vocab else vocab[0], "intent", "[refused]")
        return Report(obj["report"], "intent", obj.get("talk", ""))
