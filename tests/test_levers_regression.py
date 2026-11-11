"""Pleasure levers (ADR 0016): flags off must reproduce earlier runs bit for bit (fingerprints pinned before the levers existed)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import levers_fingerprint as F  # noqa: E402
from mar import hedonic as HD  # noqa: E402

PINNED = json.loads((Path(__file__).parent / "data" / "levers_off_fingerprints.json").read_text())


def test_default_runs_match_pinned_fingerprints():
    assert F.fingerprints() == PINNED


def test_all_flags_off_config_is_the_same_as_none():
    with HD.use_levers(HD.LeverConfig()):
        assert F.fingerprints() == PINNED
