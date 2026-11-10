"""Tiny .env loader. Keys come ONLY from environment variables, which a repo-root .env may fill in.

Never prints or logs a value. Existing environment variables win over the file.
"""
import os
from pathlib import Path

from .base import MissingKeyError

ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


def load_env(path=None) -> list:
    """Read KEY=VALUE lines into os.environ (without overriding). Returns the names set."""
    p = Path(path) if path else ENV_PATH
    if not p.exists():
        return []
    names = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:]
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        if k and v and k not in os.environ:
            os.environ[k] = v
            names.append(k)
    return names


def get(name: str, default=None):
    load_env()
    return os.environ.get(name) or default


def require_key(name: str) -> str:
    v = get(name)
    if not v:
        raise MissingKeyError(f"{name} is not set. Put {name}=<your key> in {ENV_PATH} (copy .env.example) "
                              f"or export it in your shell. Never paste a key into chat.")
    return v
