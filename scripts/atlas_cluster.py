"""Pattern atlas, clustering step (EXPLORATORY, DESCRIPTIVE). Reads runs/atlas/records.jsonl.gz (scripts/atlas_run.py --run).

  uv run python scripts/atlas_cluster.py        -> runs/atlas/atlas.json and runs/atlas/atlas.md (a dump read when writing the doc)

Rule for k (stated before looking at the clusters): k in 3..8 with the highest mean silhouette of the best-of-10 k-medoids fit on
standardized CLUSTER_FEATURES (Euclidean). Stability: 30 resamples of 80 percent of runs, reclustered with new seeds; ARI against the
full-sample labels on the shared runs, and per-cluster best-match Jaccard (Hennig). Jaccard >= 0.75 reads as stable, 0.6-0.75 as a
pattern worth keeping an eye on, < 0.6 as not a stable cluster (Hennig's rough bands).
"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import atlas as AT  # noqa: E402

OUT = ROOT / "runs" / "atlas"


def load():
    with gzip.open(OUT / "records.jsonl.gz", "rt") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def groups(rec):
    m = rec["meta"]
    pa, pb = m["personas"]["A"], m["personas"]["B"]
    return {"family": m["family"], "arm": f"{m['family']}:{m['arm']}",
            "seed_rules": m.get("cand", "baseline" if m["family"] == "h38" or m["arm"] == "BASE-F" else "author_seed_v23_bindable"),
            "styles": "+".join(sorted((pa["style"], pb["style"]))),
            "v_pair": "+".join(sorted((f"{pa['v']:g}", f"{pb['v']:g}"))),
            "hand_pair": str(pa["id"].startswith("p-") and pb["id"].startswith("p-")),
            "persona": None}


def main():
    recs = load()
    recs.sort(key=lambda r: r["key"])
    feats = [AT.features(r["rows"], r["meta"]) for r in recs]
    X, Z, mu, sd = AT.matrix(feats)
    k, sil = AT.choose_k(Z)
    D = AT.dist(Z)
    lab, med, cost = AT.best_kmedoids(D, k, restarts=20)
    # order clusters by size, largest first
    order = [c for c, _ in Counter(lab.tolist()).most_common()]
    remap = {c: i for i, c in enumerate(order)}
    lab = np.array([remap[c] for c in lab])
    med = np.array([med[c] for c in order])
    st = AT.stability(Z, k, lab, reps=30)
    alt = {}
    for kk in (k - 1, k + 1):
        if kk >= 2:
            la, _, _ = AT.best_kmedoids(D, kk, restarts=10)
            alt[kk] = AT.ari(lab, la)
    gs = [groups(r) for r in recs]
    out = {"n": len(recs), "k": int(k), "silhouette": {int(a): b for a, b in sil.items()}, "ari_resample": st["ari"],
           "ari_mean": float(np.mean(st["ari"])), "jaccard": st["jaccard"], "ari_neighbor_k": {int(a): b for a, b in alt.items()},
           "features": list(AT.CLUSTER_FEATURES), "overall_mean": dict(zip(AT.CLUSTER_FEATURES, mu.round(4).tolist())),
           "clusters": []}
    for c in range(k):
        idx = np.where(lab == c)[0]
        zc = Z[idx].mean(0)
        dist_feats = sorted(zip(AT.CLUSTER_FEATURES, zc, X[idx].mean(0)), key=lambda t: -abs(t[1]))[:6]
        near, seen = [], set()
        for i in idx[np.argsort(D[med[c], idx])]:          # the medoid, then the nearest run whose story differs (EF seeds v2.2 and
            txt = tuple(AT.story(recs[i]["rows"]))          # v2.3 often play the same household identically)
            if txt not in seen:
                near.append(i)
                seen.add(txt)
            if len(near) == 2:
                break
        lifts = {}
        for gname in ("family", "arm", "seed_rules", "styles", "v_pair", "hand_pair"):
            lf = AT.lift(lab, [g[gname] for g in gs], c)
            lifts[gname] = {str(v): x for v, x in lf.items() if x[0] >= 3 and x[2] >= 1.3}
        pc = Counter(p for i in idx for p in (recs[i]["meta"]["a"], recs[i]["meta"]["b"]))
        pall = Counter(p for r in recs for p in (r["meta"]["a"], r["meta"]["b"]))
        plift = {p: (n, pall[p], (n / (2 * len(idx))) / (pall[p] / (2 * len(recs)))) for p, n in pc.items() if n >= 4}
        plift = dict(sorted(((p, v) for p, v in plift.items() if v[2] >= 1.5), key=lambda t: -t[1][2])[:8])
        ex = {}
        h4 = [feats[i]["held_share"] for i in idx if recs[i]["meta"]["arm"] == "L4" and feats[i]["held_share"] is not None]
        ex["held_share_L4"] = (float(np.mean(h4)), len(h4)) if h4 else None
        for key in ("held_share", "worth_share", "say_do_gap", "exiter_lower"):
            v = [feats[i][key] for i in idx if feats[i][key] is not None]
            ex[key] = (float(np.mean(v)), len(v)) if v else None
        ex["who_exits"] = dict(Counter(feats[i]["who_exits"] or "nobody" for i in idx))
        stories = []
        for i in near:
            m = recs[i]["meta"]
            names = {"A": m["a"], "B": m["b"]}
            stories.append({"key": recs[i]["key"], "lines": AT.story(recs[i]["rows"], m, names),
                            "features": {f: round(feats[i][f], 3) for f in AT.CLUSTER_FEATURES}})
        out["clusters"].append({"id": int(c), "size": int(len(idx)), "jaccard": st["jaccard"].get(int(c)),
                                "distinguishing": [(f, round(float(z), 2), round(float(x), 4)) for f, z, x in dist_feats],
                                "means": {f: round(float(x), 4) for f, x in zip(AT.CLUSTER_FEATURES, X[idx].mean(0))},
                                "lifts": lifts, "persona_lift": plift, "extras": ex, "medoids": stories,
                                "by_arm": dict(Counter(gs[i]["arm"] for i in idx))})
    out["labels"] = {recs[i]["key"]: int(lab[i]) for i in range(len(recs))}
    # H38: held vs worth, and cluster mix, by pressure
    h38 = {}
    for arm in ("L0", "L4"):
        ii = [i for i, r in enumerate(recs) if r["meta"]["family"] == "h38" and r["meta"]["arm"] == arm]
        hs = [feats[i]["held_share"] for i in ii if feats[i]["held_share"] is not None]
        ws = [feats[i]["worth_share"] for i in ii if feats[i]["worth_share"] is not None]
        h38[arm] = {"n": len(ii), "held_share": float(np.mean(hs)) if hs else None, "worth_share": float(np.mean(ws)) if ws else None,
                    "runs_any_held": int(sum(1 for i in ii if (feats[i]["held_share"] or 0) > 0)),
                    "pl_mean": float(np.mean([feats[i]["pl_mean"] for i in ii])),
                    "together": float(np.mean([feats[i]["together_share"] for i in ii])),
                    "clusters": dict(sorted(Counter(int(lab[i]) for i in ii).items()))}
    out["h38"] = h38
    # paired H38 transitions: which cluster a pairing-seed moves to from L0 to L4
    idx = {(r["meta"]["a"], r["meta"]["b"], r["meta"]["seed"], r["meta"]["arm"]): i for i, r in enumerate(recs) if r["meta"]["family"] == "h38"}
    trans = Counter()
    for (a, b, s, arm), i in idx.items():
        if arm == "L0" and (a, b, s, "L4") in idx:
            trans[(int(lab[i]), int(lab[idx[(a, b, s, "L4")]]))] += 1
    out["h38_transitions"] = {f"{x}->{y}": n for (x, y), n in sorted(trans.items())}
    (OUT / "atlas.json").write_text(json.dumps(out, indent=1, default=str))
    dump(out)


def dump(out):
    L = [f"n {out['n']}, k {out['k']}, silhouette {out['silhouette']}, ARI resample mean {out['ari_mean']:.3f} "
         f"(min {min(out['ari_resample']):.3f}), neighbor-k ARI {out['ari_neighbor_k']}"]
    L.append("overall means: " + json.dumps(out["overall_mean"]))
    for c in out["clusters"]:
        L.append(f"\n## cluster {c['id']}: size {c['size']}, Jaccard {c['jaccard']}")
        L.append("distinguishing (feature, z, raw mean): " + json.dumps(c["distinguishing"]))
        L.append("means: " + json.dumps(c["means"]))
        L.append("by arm: " + json.dumps(c["by_arm"]))
        L.append("lifts: " + json.dumps(c["lifts"]))
        L.append("persona lift: " + json.dumps(c["persona_lift"]))
        L.append("extras: " + json.dumps(c["extras"]))
        for s in c["medoids"]:
            L.append(f"### {s['key']}")
            L += s["lines"]
    L.append("\nH38: " + json.dumps(out["h38"], indent=1))
    L.append("H38 transitions L0->L4: " + json.dumps(out["h38_transitions"]))
    (OUT / "atlas.md").write_text("\n".join(L))
    print("\n".join(L[:3]))


if __name__ == "__main__":
    main()
