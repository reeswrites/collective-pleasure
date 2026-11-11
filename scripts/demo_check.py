"""Five-minute demo, non-interactively (docs/demo.md): the five things the author says in chat, as `mar` calls.

  uv run python scripts/demo_check.py

Scripted agents only, small seeds, no model calls, no network. Works in a temp directory (a copy of the household rules, a scratch
experiments dir), so it leaves the repo untouched. Asserts that every step prints output and, where promised, writes a report file.
"""
import contextlib
import io
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar.cli import main  # noqa: E402

SEED, NEW = "author_seed_v2_bindable", "demo_pot_shared_needs_unless_agree"
QUOTE = "shared pot can only be used for shared needs unless both agree"


def mar(base, *args):
    buf, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
        code = main(["--runs-dir", str(base / "runs"), "--experiments-dir", str(base / "exp"),
                     "--household-rules", str(base / "rules"), *args])
    assert code == 0, f"mar {' '.join(args)} exited {code}: {err.getvalue()}"
    return buf.getvalue()


def report_of(out):
    path = Path(out.split("report: ")[1].splitlines()[0])
    assert path.exists() and path.stat().st_size > 500, f"no report at {path}"
    return path


def steps(base):
    yield ("1. show me my seed rules", lambda: mar(base, "household", "show", "--variant", SEED),
           lambda o: "Lint: PASS" in o and "In plain words:" in o)
    yield ("2. run my seed with the Anchor and the Wanderer",
           lambda: mar(base, "household", "run", "--variant", SEED, "--pair", "anchor,wanderer", "--seeds", "1", "--weeks", "52"),
           lambda o: report_of(o) and "spiral" in o)
    yield ("3. add a rule: shared pot only for shared needs unless both agree (new variant)",
           lambda: mar(base, "household", "card", "add", "--variant", NEW, "--base", SEED, "--id", "R9-pot-shared-needs-unless-agree",
                       "--attribute", "partner", "--deontic", "must_not", "--aim", "take_shared", "--cond", "consented:eq:0",
                       "--gloss", "The shared pot can only be used for shared needs unless both partners agree.",
                       "--source", "author, chat (demo)", "--quote", QUOTE),
           lambda o: "lint passes" in o and (base / "rules" / NEW / "R9-pot-shared-needs-unless-agree.yaml").exists())
    yield ("4. compare my seed with that variant across all pairings",
           lambda: mar(base, "household", "compare", "--variants", f"{SEED},{NEW}", "--pairs", "hand", "--seeds", "1", "--weeks", "52"),
           lambda o: report_of(o) and "Holm" in o)
    yield ("5. how did we get here?", lambda: mar(base, "timeline"),
           lambda o: Path(o.split("timeline: ")[1].splitlines()[0]).exists() and QUOTE in Path(o.split("timeline: ")[1].splitlines()[0]).read_text())


def main_check():
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / "rules").mkdir()
        shutil.copytree(ROOT / "rules" / "household" / SEED, base / "rules" / SEED)
        for name, go, ok in steps(base):
            t = time.time()
            out = go()
            assert out.strip(), f"step '{name}' printed nothing"
            assert ok(out), f"step '{name}' did not do what the demo promises:\n{out[-800:]}"
            print(f"PASS  {time.time() - t:5.1f}s  {name}")
    print(f"all five steps passed in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main_check()
