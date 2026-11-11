"""Fingerprint household runs (flags-off regression). Writes json of sha256 per case."""
import hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT / "src"))
from mar import negotiation as NG, personas as P
from mar.worlds import household as H

PS = {p.id: p for p in P.load_dir(ROOT / "personas") + P.load_dir(ROOT / "personas" / "pressing")}
CASES = [("baseline", "p-anchor", "p-host", 0), ("trap", "p-bargainer", "p-wanderer", 1),
         ("author_seed_v2_bindable", "p-anchor", "p-peacekeeper", 2), ("author_seed_v2_free_exit", "p-controller", "p-host", 3),
         ("author_seed_v2_nocommit", "p-steward", "p-overasker", 4), ("no_pressure_sanctioned", "p-freerider", "p-anchor", 5),
         ("share_duty", "p-host", "p-steward", 6), ("author_seed", "p-peacekeeper", "p-wanderer", 7)]

def digest(run):
    blob = json.dumps({"o": run.outcomes, "t": run.trace, "f": run.final, "m": run.meta}, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()

def fingerprints():
    out = {}
    for v, a, b, sd in CASES:
        run = H.run_weekly(H.PyGate(H.load_variant(v)), (PS[a], PS[b]), sd)
        out[f"weekly|{v}|{a}|{b}|{sd}"] = digest(run)
    for arm, a, b, sd in (("v22_bindable", "p-anchor", "p-peacekeeper", 2), ("v22_bindable", "p-controller", "p-host", 3)):
        NG._RC.clear(); NG._PC.clear()
        base = NG.base_cards("author_seed_v2_bindable")
        res = NG.week0(PS[a], PS[b], "fair_default", sd, base, floor=True)
        L = NG.Lived(PS[a], PS[b], "fair_default", sd, base, res, floor=True, apart=True)
        out[f"lived|{arm}|{a}|{b}|{sd}"] = digest(L.play())
    return out

if __name__ == "__main__":
    print(json.dumps(fingerprints(), indent=1, sort_keys=True))
