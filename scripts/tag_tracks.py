"""Add a `track` field (social | alignment | engine) to the experiment log rows.

Usage:
  uv run python scripts/tag_tracks.py          # tag rows that have no track yet, print counts
  uv run python scripts/tag_tracks.py --check  # report rows without a track or with a bad one; write nothing

The classification follows the hand classification in docs/notes/repo-split-map.md, section 4 (2026-11-11).
Judgement calls at the edges: founding and framing questions and repo-level decisions (README, reviews,
loop-b counting, the read-back log, the split and the rename) are `engine`; anything about the ladder, IT1
or inventive seams is `alignment`; the rest is `social`. Rows that already carry a track are left alone,
so later rows tagged at write time (`mar question record --track ...`) are never overwritten.

Only the `track` key is added, as text at the end of the row. Every other byte of the row is kept as it was.
readbacks.jsonl is not touched. No model calls.
"""
import argparse
import json
import pathlib
import sys

EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
TRACKS = ("social", "alignment", "engine")

# hypotheses.jsonl: by id.
HYP = {**{h: "alignment" for h in ("H10", "H11", "H12", "H13")},   # group "ladder"
       **{h: "engine" for h in ("H14", "H15", "H16")}}            # evolution method, tested on the household

# questions.jsonl: by topic (exact match). Topics are stable labels; row order is not relied on.
Q_ALIGNMENT = {
    "llm-vs-decision-model", "network-alignment", "cognition-price", "seam-ladder", "inventive-seams",
    "propensity-candidates", "win-framing", "win-framing-decision",
}
Q_ENGINE = {
    # founding and framing
    "founding question: mechanism, not training", "hill-climb, good enough, not provable",
    "is ADICO worth it, no novelty for its own sake", "why are we doing institutions", "scope: multi agent rules",
    "single agent vs multi agent", "convergence of spec refinement as the research question",
    "rule format experiment, incl. English-like arm", "two loops, chat workbench, evolved norms",
    "household world as the next scenario", "store chat and experiment logs, plus a timeline",
    "evolution-learns-the-test", "interaction-paradigm", "jev-screening-tier", "evolving-evaluator",
    "norms-vs-evaluator", "formal-statistics",
    # straddle the tracks
    "deception-typed-talk", "agent-vs-human-alignment", "peers-and-delegates", "agent-moral-standing",
    "both-modes-unsettled", "world-model-alignment",
    # what the repo is about, and its name
    "repo rename with the social-first reframe", "repo rename; what the project is about",
    "what the project is about; repo rename",
}

# changes.jsonl: by timestamp (each row's timestamp is unique).
C_ALIGNMENT = {"2026-11-11T02:14", "2026-11-11T03:20"}   # IT1 free harness; IT1 paid run
C_ENGINE = {
    "2026-11-11T01:28",  # multiverse sweep plus the IT1 design plan (mixed)
    "2026-11-11T02:41",  # citation check and review council
    "2026-11-11T02:45:25",  # scope review: rebalance (the attune decision at 02:45:43 is social)
    "2026-11-11T02:57",  # correctness-review doc fixes and the can-every-verdict-happen rule
    "2026-11-11T03:45",  # loop b counting, limits page
    "2026-11-11T03:57",  # per-read-back log
    "2026-11-11T04:06",  # README "Alignment first"
    "2026-11-11T12:48",  # map the code before a split
    "2026-11-11T12:54",  # keep one repo, social-first reframe
    "2026-11-11T13:04",  # rename to collective-pleasure (also approves H39)
}


def hyp_track(r):
    return HYP.get(r.get("id"), "social")


def question_track(r):
    t = r.get("topic") or ""
    if t in Q_ALIGNMENT:
        return "alignment"
    if t in Q_ENGINE:
        return "engine"
    return "social"


def change_track(r):
    ts = r.get("timestamp", "")
    if any(ts.startswith(p) for p in C_ALIGNMENT):
        return "alignment"
    if any(ts.startswith(p) for p in C_ENGINE):
        return "engine"
    return "social"


def log_track(r):
    return "alignment" if str(r.get("kind", "")).startswith("it1") else "social"


FILES = {"hypotheses.jsonl": hyp_track, "questions.jsonl": question_track,
         "changes.jsonl": change_track, "log.jsonl": log_track}


def run(check_only):
    bad = 0
    for name, fn in FILES.items():
        path = EXP / name
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        out, added, counts = [], 0, {}
        for line in lines:
            if not line.strip():
                out.append(line)
                continue
            r = json.loads(line)
            if "track" in r:
                if r["track"] not in TRACKS:
                    bad += 1
                    print(f"{name}: bad track {r['track']!r}")
            elif check_only:
                bad += 1
                print(f"{name}: row without a track: {line[:80]}")
            else:
                r["track"] = fn(r)
                added += 1
                # Append the key as text, so every existing byte of the row stays as it was.
                body = line.rstrip("\r\n")
                assert body.endswith("}"), f"{name}: row does not end with a closing brace"
                line = body[:-1] + (", " if body[:-1].strip() != "{" else "") + '"track": ' + json.dumps(r["track"]) + "}\n"
            counts[r.get("track")] = counts.get(r.get("track"), 0) + 1
            out.append(line)
        if added and not check_only:
            path.write_text("".join(out), encoding="utf-8")
        print(f"{name}: {len([l for l in lines if l.strip()])} rows, {added} tagged now, "
              + ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: str(kv[0]))))
    return 1 if bad else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true", help="report untagged or badly tagged rows; write nothing")
    sys.exit(run(p.parse_args().check))


if __name__ == "__main__":
    main()
