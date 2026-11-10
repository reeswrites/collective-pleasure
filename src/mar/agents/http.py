"""The only place that touches the network. Tests replace `post_json` and `sleep`."""
import json
import time
import urllib.error
import urllib.request

from .base import AgentError

RETRY_STATUS = {0, 408, 429} | set(range(500, 600))


class HttpError(AgentError):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body[:300]}")
        self.status, self.body = status, body


def post_json(url: str, headers: dict, body: dict, timeout: float = 60.0) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise HttpError(e.code, e.read().decode(errors="replace"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise HttpError(0, str(e))


def sleep(seconds: float) -> None:
    time.sleep(seconds)


def post_with_retry(url, headers, body, tries: int = 4, base: float = 1.0) -> dict:
    """Retry on 429, 5xx and network errors with exponential backoff (base, 2*base, 4*base...)."""
    for attempt in range(tries):
        try:
            return post_json(url, headers, body)
        except HttpError as e:
            if e.status not in RETRY_STATUS or attempt == tries - 1:
                raise
            sleep(base * 2 ** attempt)
    raise AssertionError("unreachable")
