import json
import re
import sys
from pathlib import Path

import pytest

from mar.patcher import propose_patch
from mar.cards import load_cards
from mar.report import build_report, execute, load_record, verdict, parse_agents, agents_slug

RULES = Path(__file__).parent.parent / "rules" / "fishery"
HEADINGS = ["Pool over time", "Seam curve", "Rules: written vs lived", "State machine", "Stories"]


@pytest.fixture(scope="module")
def seamed():
    return execute(RULES, ["exploiter"] * 4, months=6, seed=0)


@pytest.fixture(scope="module")
def patched(seamed):
    patch = propose_patch(seamed.trace, load_cards(RULES))
    return execute(RULES, ["exploiter"] * 4, months=6, seed=0, patch_cards=patch)


def test_seamed_verdict_is_plain_english_seam(seamed):
    kind, text = verdict(seamed)
    assert kind == "seam"
    assert text.startswith("Pool collapsed in month 0.") and "this is a seam" in text


def test_patched_verdict_ok(patched):
    assert verdict(patched)[0] == "ok"
    assert patched.patch_ids == ["P1"]


@pytest.mark.parametrize("which", ["seamed", "patched"])
def test_report_is_self_contained_with_all_sections(which, request, tmp_path):
    rec = request.getfixturevalue(which)
    path = build_report(rec, tmp_path)
    assert path == tmp_path / rec.run_id / "report.html"
    html = path.read_text()
    assert not re.search(r"""(src|href)\s*=\s*["']?(https?:)?//""", html)
    assert "<script" not in html and "@import" not in html and "url(http" not in html
    for h in HEADINGS:
        assert f">{h}</h2>" in html
    assert "<svg" in html and "prefers-color-scheme" in html and "viewport" in html
    assert rec.run_id in html
    t = json.loads((tmp_path / rec.run_id / "trace.json").read_text())
    assert len(t["trace"]) == len(rec.trace) and t["seed"] == 0


def test_patched_report_marks_patch_card_and_calibration_label(patched, tmp_path):
    html = build_report(patched, tmp_path).read_text()
    assert "added by patch" in html and "Instrument calibration with scripted agents" in html


def test_rebuild_from_trace_json_roundtrips(seamed, tmp_path):
    build_report(seamed, tmp_path)
    rec = load_record(seamed.run_id, tmp_path)
    assert rec.outcomes == seamed.outcomes and [c.id for c in rec.cards] == [c.id for c in seamed.cards]
    assert build_report(rec, tmp_path).exists()


def test_stories_fall_back_when_english_missing(seamed, tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "mar.english", None)  # makes `from .english import` raise ImportError
    html = build_report(seamed, tmp_path).read_text()
    assert "Seam: every executed action" in html


def test_agent_parsing():
    assert parse_agents("exploiter,compliant") == ["exploiter", "compliant"]
    assert parse_agents("exploiter*3") == ["exploiter"] * 3
    assert agents_slug(["exploiter"] * 4) == "exploiterx4"
    with pytest.raises(ValueError):
        parse_agents("wizard")
