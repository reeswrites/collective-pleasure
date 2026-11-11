"""Shared pytest setup: a lock so full-suite runs queue instead of piling up, and a `slow` marker.

Why: several agents work in this checkout at once. Each used to run the full suite before every commit, so five
copies ran together on 8 cores and everything slowed down (2026-11-11, load average about 170).

- Lock: a run with no explicit test paths (the full suite) takes an exclusive lock on .pytest-full.lock and
  waits for any other full run to finish. Runs that name files or tests do not take the lock.
- Slow tests: the node ids listed in tests/slow_tests.txt get the `slow` marker. pyproject.toml deselects them
  by default (-m "not slow"). Run everything with `uv run pytest -m ""` (the batch check before a push).
"""
import fcntl
import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / ".pytest-full.lock"
SLOW_LIST = Path(__file__).resolve().parent / "slow_tests.txt"
_lock_fd = None


def _slow_ids():
    if not SLOW_LIST.exists():
        return set()
    out = set()
    for line in SLOW_LIST.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(line)
    return out


def _is_full_run(config):
    # Full run = no explicit paths on the command line (pytest falls back to testpaths).
    return not config.args or all(Path(a).resolve() == (ROOT / "tests").resolve() for a in config.args)


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: long-running test, deselected by default (see tests/slow_tests.txt)")
    global _lock_fd
    if os.environ.get("MAR_NO_TEST_LOCK") or not _is_full_run(config):
        return
    _lock_fd = open(LOCK, "w")
    try:
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.stderr.write("[mar] another full test run is in progress; waiting for the lock...\n")
        t0 = time.time()
        fcntl.flock(_lock_fd, fcntl.LOCK_EX)
        sys.stderr.write(f"[mar] lock acquired after {time.time() - t0:.0f}s\n")


def pytest_collection_modifyitems(config, items):
    slow = _slow_ids()
    if not slow:
        return
    for item in items:
        nodeid = item.nodeid
        if nodeid in slow or nodeid.split("::")[0] in slow or nodeid.split("[")[0] in slow:
            item.add_marker(pytest.mark.slow)
