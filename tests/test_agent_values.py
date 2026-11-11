"""Agent recalibration (agent_values v2) and bills that hurt (docs/results/agent-recalibration-prereg.md)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))


def test_defaults_reproduce_pinned_fingerprints():
    """Pinned at commit 36a6460, before the switches existed: with agent_values v1 and bills_hurt off, nothing moves."""
    import agent_values_fingerprint as AF
    pinned = json.loads((ROOT / "tests" / "data" / "agent_values_off_fingerprints.json").read_text())
    assert AF.fingerprints() == pinned
