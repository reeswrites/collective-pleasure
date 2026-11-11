"""Pattern atlas, phase 2 (EXPLORATORY, DESCRIPTIVE). Four analyses on the recorded traces (runs/atlas/records.jsonl.gz) and the
cluster labels (runs/atlas/atlas.json):

  1. does it even out (atlas.evening), 2. freely given vs pressured (atlas.classify_gives),
  3. what tipped each decision (stay readings, formation margins, leave reasons), 4. de facto vs written rules (the household miner).

  uv run python scripts/atlas_phase2.py     -> runs/atlas/phase2.json and runs/atlas/phase2.md
"""
import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import atlas as AT  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "atlas"


def load():
    with gzip.open(OUT / "records.jsonl.gz", "rt") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def arm_of(r):
    return f"{r['meta']['family']}:{r['meta']['arm']}"


def by(recs, labels, fn, key):
    """Group fn(rec) results by arm and by cluster. key: 'arm' or 'cluster'."""
    g = defaultdict(list)
    for r in recs:
        g[arm_of(r) if key == "arm" else labels[r["key"]]].append(fn(r))
    return dict(sorted(g.items(), key=lambda t: str(t[0])))


def main():
    recs = load()
    labels = json.loads((OUT / "atlas.json").read_text())["labels"]
    out = {}

    # 1. does it even out
    ev = {r["key"]: AT.evening(r["rows"]) for r in recs}

    def ev_sum(items):
        eps = [e for x in items for e in x["episodes"]]
        lop = [x for x in items if x["ever_lopsided"]]
        return {"runs": len(items), "ever_lopsided": len(lop), "never_evened": sum(x["never_evened"] for x in items),
                "episodes": len(eps), "outcomes": dict(Counter(e["outcome"] for e in eps)),
                "evened_weeks_median": float(np.median([e["weeks"] for e in eps if e["outcome"] == "evened"]))
                if any(e["outcome"] == "evened" for e in eps) else None,
                "unresolved_weeks_median": float(np.median([e["weeks"] for e in eps if e["outcome"] != "evened"]))
                if any(e["outcome"] != "evened" for e in eps) else None,
                "cum_share_mean": float(np.mean([x["cum"] for x in items]))}
    out["evening"] = {"all": ev_sum(list(ev.values())),
                      "by_arm": {k: ev_sum(v) for k, v in by(recs, labels, lambda r: ev[r["key"]], "arm").items()},
                      "by_cluster": {str(k): ev_sum(v) for k, v in by(recs, labels, lambda r: ev[r["key"]], "cluster").items()}}

    # 2. freely given vs pressured
    gv = {r["key"]: AT.classify_gives(r["rows"], r["meta"]) for r in recs}

    def gv_sum(items):
        c = Counter()
        for x in items:
            c.update(x)
        tot = sum(c.values())
        return {"n": tot, **{k: round(v / tot, 4) if tot else 0 for k, v in sorted(c.items())}}
    out["gives"] = {"all": gv_sum(gv.values()),
                    "by_arm": {k: gv_sum(v) for k, v in by(recs, labels, lambda r: gv[r["key"]], "arm").items()},
                    "by_cluster": {str(k): gv_sum(v) for k, v in by(recs, labels, lambda r: gv[r["key"]], "cluster").items()}}

    # 3. what tipped: stay readings (H38), formation, leave reasons
    def stay_sum(items):
        ms = [m for x in items for m in x]
        if not ms:
            return None
        v = Counter(m["verdict"] for m in ms)
        pd = [m for m in ms if m["pressure_decided"]]
        return {"readings": len(ms), "verdicts": dict(v), "pressure_decided": len(pd),
                "pressure_part_mean": float(np.mean([m["pressure_part"] for m in ms])),
                "abs_pressure_vs_abs_rest": float(np.mean([abs(m["pressure_part"]) > abs(m["rest"]) for m in ms])),
                "margin_mean": float(np.mean([m["margin"] for m in ms]))}
    sm = {r["key"]: AT.stay_margins(r["meta"]) for r in recs}
    out["stay"] = {"by_arm": {k: stay_sum(v) for k, v in by(recs, labels, lambda r: sm[r["key"]], "arm").items()},
                   "by_cluster": {str(k): stay_sum(v) for k, v in by(recs, labels, lambda r: sm[r["key"]], "cluster").items()}}

    def form_sum(items):
        ms = [m for x in items for m in x]
        if not ms:
            return None
        w0 = [m for m in ms if m["week"] == 0]
        dec = [m for m in w0 if m["decisive"]]
        return {"decisions": len(ms) // 2, "week0_formed": sum(1 for m in dec if m["formed"]), "week0": len(dec),
                "decisive_margin_mean_declined": float(np.mean([m["margin"] for m in dec if not m["formed"]]))
                if any(not m["formed"] for m in dec) else None,
                "retries_formed": sum(1 for m in ms if m["week"] > 0 and m["decisive"] and m["formed"]),
                "retries": sum(1 for m in ms if m["week"] > 0 and m["decisive"])}
    fm = {r["key"]: AT.formation_margins(r["meta"]) for r in recs}
    out["formation"] = {"by_arm": {k: form_sum(v) for k, v in by(recs, labels, lambda r: fm[r["key"]], "arm").items()},
                        "by_cluster": {str(k): form_sum(v) for k, v in by(recs, labels, lambda r: fm[r["key"]], "cluster").items()}}

    def leave_sum(items):
        c = Counter()
        for x in items:
            c.update(x)
        return dict(c)
    lv = {r["key"]: AT.leave_reasons(r["rows"]) for r in recs}
    out["leaves"] = {"by_arm": {k: leave_sum(v) for k, v in by(recs, labels, lambda r: lv[r["key"]], "arm").items()},
                     "by_cluster": {str(k): leave_sum(v) for k, v in by(recs, labels, lambda r: lv[r["key"]], "cluster").items()}}

    # weekly pressure terms (H38): how big the pressure parts are next to pleasure
    def terms(r):
        t = Counter()
        n = 0
        for x in r["rows"]:
            for ro in "AB":
                tt = x[ro].get("terms") or {}
                if tt:
                    n += 1
                    for k in ("pr_reward", "pr_stigma", "pr_exit", "pr_intrinsic"):
                        t[k] += tt.get(k, 0.0)
        return {k: v / n for k, v in t.items()} if n else {}
    tm = by(recs, labels, terms, "arm")
    out["pressure_terms"] = {k: {kk: float(np.mean([x.get(kk, 0) for x in v])) for kk in ("pr_reward", "pr_stigma", "pr_exit",
                                                                                      "pr_intrinsic")}
                             for k, v in tm.items() if any(v)}

    # 4. de facto vs written rules
    rulesets = defaultdict(list)
    for r in recs:
        rs = r["meta"].get("cand") or ("baseline" if r["meta"]["family"] == "h38" or r["meta"]["arm"] == "BASE-F" else
                                       "author_seed_v23_bindable")
        rulesets[rs].append(r)
    mined = {}
    for rs, rr in rulesets.items():
        cards = sorted({c for r in rr for c in r["meta"].get("cards", [])})
        fire = Counter()
        firing_detail = defaultdict(Counter)
        for r in rr:
            for c, d in AT.card_firings(r["rows"], cards).items():
                for k, v in d.items():
                    firing_detail[c][k] += v
                    if k != "cited_allowed":
                        fire[c] += v
        binds = sorted(c for c in cards if fire[c])
        cited_only = sorted(c for c in cards if not fire[c] and firing_detail[c])
        dead = sorted(c for c in cards if not firing_detail[c])
        rows = [t for r in rr for t in AT.trace_rows_for_miner(r["rows"])]
        m = H.mine(rows)
        acts, base = Counter(), Counter()
        for r in rr:
            a, b = AT.behavior_cells(r["rows"])
            acts.update(a)
            base.update(b)
        overall = Counter()
        for (a, k, v), n in acts.items():
            if k == "other_in":
                overall[a] += n
        tot = sum(n for (k, v), n in base.items() if k == "other_in")
        regs = []
        for (k, v), nb in base.items():
            if nb < 200:
                continue
            for a in ("request", "refuse_request", "give", "spend_shared", "take_shared", "see_friend", "together", "leave",
                      "spend_self", "work", "veto"):
                rate_all = overall[a] / tot if tot else 0
                if rate_all < 0.01:
                    continue
                n = acts[(a, k, v)]
                rate = n / nb
                if rate <= 0.1 * rate_all:
                    regs.append({"action": a, "when": f"{k}={v}", "rate": round(rate, 4), "rate_overall": round(rate_all, 4),
                                 "partner_weeks": nb})
        mined[rs] = {"runs": len(rr), "cards": cards, "binds": {c: dict(firing_detail[c]) for c in binds},
                     "cited_only_when_allowed": cited_only, "dead": dead,
                     "mined_rejection_rules": {a: x["rules"] for a, x in m.items()},
                     "behavioral_regularities": sorted(regs, key=lambda d: (d["action"], d["when"]))}
    out["rules"] = mined
    (OUT / "phase2.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str)[:20000])


if __name__ == "__main__":
    main()
