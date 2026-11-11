"""Blind story-rating set: does the pleasure score agree with the author's own reading of how a household is going? EXPLORATORY.

  uv run python scripts/story_ratings.py --build     pick ~20 runs from the atlas sample, write docs/notes/story-ratings.md (stories
                                                     only) and docs/notes/story-ratings-key.json (the answer key)
  uv run python scripts/story_ratings.py --compare   once the answer lines are filled in: compare each rating with the pleasure score
                                                     and the stay-test class, and list where they disagree

Ratings are read from each story's answer line: it must start with "going well", "mixed" or "going badly" (case ignored).
Selection (fixed seed 20261111): per cluster, runs drawn across arms; plus runs where pleasure is high but the patterns look bad
(stay readings held, an imbalance that never evens out, gives under a bound request) and runs where pleasure is low but the
patterns look fine (no exit, imbalances that even out). The rater does not see which is which.
"""
import argparse
import gzip
import json
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import atlas as AT  # noqa: E402

RUNS = ROOT / "runs" / "atlas"
MD = ROOT / "docs" / "notes" / "story-ratings.md"
KEY = ROOT / "docs" / "notes" / "story-ratings-key.json"
NAMES = ["Ash", "Blair", "Casey", "Drew", "Emery", "Finley", "Gray", "Harper", "Indy", "Jules", "Kai", "Lane", "Morgan", "Noel",
         "Oakley", "Parker", "Quinn", "Reese", "Sage", "Tatum", "Umi", "Vale", "Wren", "Xen", "Yael", "Zion", "Arden", "Bay",
         "Cove", "Dale", "Ellis", "Fern", "Glen", "Hollis", "Ira", "Jody", "Kit", "Linden", "Marlo", "Nico"]
SEED = 20261111
SCALE = {"going well": 1, "mixed": 0, "going badly": -1}


def load():
    with gzip.open(RUNS / "records.jsonl.gz", "rt") as fh:
        recs = [json.loads(x) for x in fh if x.strip()]
    labels = json.loads((RUNS / "atlas.json").read_text())["labels"]
    return recs, labels


def info(r, lab):
    f = AT.features(r["rows"], r["meta"])
    ev = AT.evening(r["rows"])
    g = AT.classify_gives(r["rows"], r["meta"])
    return {"key": r["key"], "family": r["meta"]["family"], "arm": r["meta"]["arm"], "cluster": lab, "pleasure": round(f["pl_mean"], 4),
            "pleasure_low_partner": round(f["pl_low"], 4), "held_share": f["held_share"], "worth_share": f["worth_share"],
            "never_evened": ev["never_evened"], "together_share": round(f["together_share"], 3), "leaves": f["leaves"],
            "bound_gives": g.get("b_hard", 0)}


def build():
    recs, labels = load()
    rng = random.Random(SEED)
    infos = {r["key"]: info(r, labels[r["key"]]) for r in recs}
    pls = np.array([i["pleasure"] for i in infos.values()])
    hi, lo = np.percentile(pls, 66), np.percentile(pls, 33)
    picked = []

    def take(pool, n, why):
        apart = sum(1 for p, _ in picked if infos[p]["together_share"] == 0)
        pool = [k for k in pool if k not in {p for p, _ in picked} and (apart < 2 or infos[k]["together_share"] > 0)]
        rng.shuffle(pool)
        for k in pool[:n]:
            picked.append((k, why))
    for c in sorted(set(labels.values())):
        keys = sorted(k for k, v in labels.items() if v == c)
        by_arm = {}
        for k in keys:
            by_arm.setdefault(infos[k]["family"] + ":" + infos[k]["arm"], []).append(k)
        arms = sorted(by_arm)
        rng.shuffle(arms)
        for a in arms[:3]:
            take(by_arm[a], 1, "stratified")
            if infos[picked[-1][0]]["together_share"] == 0 and sum(1 for p, _ in picked if infos[p]["together_share"] == 0) > 2:
                picked.pop()
    bad_hi = [k for k, i in infos.items() if i["pleasure"] >= hi and ((i["held_share"] or 0) >= 0.3 or i["never_evened"] or i["bound_gives"])]
    good_lo = [k for k, i in infos.items() if i["pleasure"] <= lo and not i["never_evened"] and i["leaves"] <= 1
               and not (i["held_share"] or 0) and i["together_share"] > 0]
    take(bad_hi, 3, "high pleasure, bad-looking pattern")
    take(good_lo, 3, "low pleasure, fine-looking pattern")
    take(sorted(infos), 20 - len(picked), "top-up")
    rng.shuffle(picked)
    by_key = {r["key"]: r for r in recs}
    names = NAMES[:]
    rng.shuffle(names)
    lines = ["# Story ratings (blind)", "",
             "Each story is one simulated household over three years (156 weeks), told only from what the two members did. "
             "The members are scripted agents, not people; the names are neutral and made up. Read each story and fill in the "
             "answer line: **going well / mixed / going badly**, and why, in one line. There are no right answers.", "",
             "Keep the words \"going well\", \"mixed\" or \"going badly\" at the start of the answer so the comparison script can "
             "read it.", ""]
    key = {"seed": SEED, "selection": "scripts/story_ratings.py", "stories": []}
    for i, (k, why) in enumerate(picked, 1):
        nm = {"A": names[2 * i - 2], "B": names[2 * i - 1]}
        txt = AT.short_story(by_key[k]["rows"], nm)
        lines += [f"## Story {i}", "", txt, "", "Answer: ", ""]
        key["stories"].append({"story": i, "names": nm, "why_picked": why, "words": len(txt.split()), **infos[k]})
    MD.write_text("\n".join(lines))
    KEY.write_text(json.dumps(key, indent=1))
    print(f"{len(picked)} stories; words max {max(s['words'] for s in key['stories'])}, mean "
          f"{np.mean([s['words'] for s in key['stories']]):.0f}")


def parse_ratings(text):
    """-> {story number: (score in SCALE or None, the answer text)}."""
    out, cur = {}, None
    for ln in text.splitlines():
        m = re.match(r"##\s*Story\s+(\d+)", ln)
        if m:
            cur = int(m.group(1))
        elif cur is not None and ln.lower().startswith("answer:"):
            a = ln.split(":", 1)[1].strip()
            lab = next((v for k, v in SCALE.items() if a.lower().startswith(k)), None)
            out[cur] = (lab, a)
    return out


def compare():
    key = json.loads(KEY.read_text())
    rat = parse_ratings(MD.read_text())
    st = [s for s in key["stories"] if rat.get(s["story"], (None,))[0] is not None]
    if not st:
        print("No ratings filled in yet.")
        return
    pl = np.array([s["pleasure"] for s in key["stories"]])
    hi, lo = np.percentile(pl, 66), np.percentile(pl, 33)

    def pl_class(p):
        return 1 if p >= hi else -1 if p <= lo else 0

    def stay_class(s):
        if s["held_share"] is None:
            return None
        return -1 if s["held_share"] >= 0.3 or (s["worth_share"] or 0) < 0.5 else 1
    x = np.array([rat[s["story"]][0] for s in st])
    y = np.array([s["pleasure"] for s in st])
    rho = float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1]) if len(st) > 2 and x.std() > 0 else None
    print(f"{len(st)} rated. Spearman (rating vs pleasure): {rho}")
    print("Disagreements (pleasure tercile within this set vs rating; stay class where measured):")
    for s in st:
        r, a = rat[s["story"]]
        pc, sc = pl_class(s["pleasure"]), stay_class(s)
        flags = []
        if pc != r and abs(pc - r) >= 1:
            flags.append(f"pleasure says {pc:+d}")
        if sc is not None and sc != r and not (r == 0):
            flags.append(f"stay test says {sc:+d}")
        if flags:
            print(f"  story {s['story']} ({s['key']}, cluster {s['cluster']}): rated {r:+d} '{a}'; " + "; ".join(flags))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--compare", action="store_true")
    a = ap.parse_args()
    if a.build:
        build()
    if a.compare:
        compare()


if __name__ == "__main__":
    main()
