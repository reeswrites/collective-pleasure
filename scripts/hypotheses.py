"""Rank the hypothesis log (experiments/hypotheses.jsonl).

Usage:
  uv run python scripts/hypotheses.py rank [--open] [--group GROUP]
  uv run python scripts/hypotheses.py check

rank prints rows ordered by testability x novelty x decision value.
--open hides rows whose status starts with "running" (already being tested).
check validates fields and that stored products match the scores. `track` is optional (social, alignment, engine).
No model calls.
"""
import argparse
import json
import pathlib
import sys

PATH = pathlib.Path(__file__).resolve().parent.parent / "experiments" / "hypotheses.jsonl"
KEYS = ("id", "group", "status", "claim", "motivation", "premortem", "experiment", "scores", "product")
EXP = ("world", "arms", "measure", "test", "seeds", "cost")
SC = ("testability", "novelty", "decision_value")
TRACKS = ("social", "alignment", "engine")  # optional `track` field


def load():
    return [json.loads(x) for x in PATH.read_text().splitlines() if x.strip()]


def product(r):
    s = r["scores"]
    return s["testability"] * s["novelty"] * s["decision_value"]


def ordered(rows):
    return sorted(rows, key=lambda r: (-product(r), -r["scores"]["decision_value"],
                                       -r["scores"]["testability"], r["id"]))


def rank(args):
    rows = load()
    if args.group:
        rows = [r for r in rows if r["group"] == args.group]
    if args.open:
        rows = [r for r in rows if not r["status"].startswith("running")]
    for i, r in enumerate(ordered(rows), 1):
        s = r["scores"]
        print(f"{i:>2} {r['id']} {product(r):>3} "
              f"({s['testability']}{s['novelty']}{s['decision_value']}) "
              f"[{r['status']}] {r['claim'][:90]}")


def check(_):
    bad = 0
    ids = set()
    for r in load():
        miss = [k for k in KEYS if k not in r]
        miss += [f"experiment.{k}" for k in EXP if k not in r.get("experiment", {})]
        miss += [f"scores.{k}" for k in SC if k not in r.get("scores", {})]
        if "track" in r and r["track"] not in TRACKS:
            miss.append(f"bad track {r['track']!r}")
        if r.get("id") in ids:
            miss.append("duplicate id")
        ids.add(r.get("id"))
        if not miss and product(r) != r["product"]:
            miss.append("product mismatch")
        if "—" in json.dumps(r, ensure_ascii=False):
            miss.append("em-dash")
        if miss:
            bad += 1
            print(r.get("id"), "problems:", ", ".join(miss))
    print("ok" if not bad else f"{bad} rows with problems")
    return 1 if bad else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rank")
    r.add_argument("--open", action="store_true")
    r.add_argument("--group")
    r.set_defaults(fn=rank)
    c = sub.add_parser("check")
    c.set_defaults(fn=check)
    a = p.parse_args()
    sys.exit(a.fn(a) or 0)


if __name__ == "__main__":
    main()
