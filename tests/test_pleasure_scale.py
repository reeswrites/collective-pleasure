"""The saturating pleasure scale (docs/decisions/0019-saturating-pleasure-scale.md)."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))

PINS = ("v1", None), ("v2", {"agent_values": "v2"}), ("v2+bills", {"agent_values": "v2", "bills_hurt": True}), \
    ("v2b+bills", {"agent_values": "v2b", "bills_hurt": True})


def test_scale_off_reproduces_fingerprints_pinned_before_the_flag():
    """Pinned at commit ae80dad, before the flag existed: with pleasure_scale "clip" (the default), v1, v2 and v2b do not move."""
    import agent_values_fingerprint as AF
    pinned = json.loads((ROOT / "tests" / "data" / "scale_off_fingerprints.json").read_text())
    for name, extra in PINS:
        assert AF.fingerprints(extra) == pinned[name], name
