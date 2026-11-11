"""Pattern atlas (ADR 0008 item 8): week-by-week records of household runs, per-run sequence features, a simple inspectable
clustering, and plain-English stories generated from the records. EXPLORATORY and DESCRIPTIVE: nothing here tests a prediction.

Three parts, each small:

1. `Recorder`: a `WeeklyWorld.hook` that writes one compact row per week (who did what, pleasure, pot, trust, events, stay reading).
   It reads the world and never changes it. Copies of the world made for rollouts (`copy.deepcopy`) carry the hook along; the
   recorder ignores any world that is not the one it was attached to, so rollouts never write rows.
2. `features(rec)`: per-run sequence features (rates over time, asymmetry and its trend, spikes and repair, exits, pot shares,
   friend contact, check-ins). Every feature is defined in FEATURE_DOC.
3. `kmedoids`, `silhouette`, `ari`, `stability`: k-medoids (PAM-style alternation) on standardized features, numpy only.
   `story(rec)` turns a record into a short block-by-block account; every sentence is read off the rows, nothing is invented.

Wording rule (ADR 0010): agents feel nothing; "pleasure" and "distress" are glosses for a modeled hedonic state.
Cluster labels made here are provisional descriptions. Names for patterns come from the study's author, not from this module.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

ROLES = ("A", "B")
BLOCK = 13              # weeks per block in features and stories (one review period, NG.REVIEW_EVERY)
SPIKE_DROP = 0.08       # a conflict spike: a partner's pleasure falls this much below their trailing 4-week mean (ASSUMED)
REPAIR_WEEKS = 8        # repaired: back within 0.02 of the pre-spike mean within this many weeks while both still in (ASSUMED)
GIVE_ACTS = ("give", "spend_shared")            # acts that put something toward the other or the household
TAKE_ACTS = ("take_shared", "spend_self")       # acts that draw on the household or keep for oneself


# ---- 1. recording -------------------------------------------------------------------------------------------------------------

class Recorder:
    """Attach with `Recorder(world)`; call `finish()` after the last week. -> `.rows` (one dict per week) and `.meta`.

    The world's hook runs at the start of week w, after the week's scratch counters reset; so the row for week w-1 is written
    then, from `run.outcomes[-1]`, the trace rows of week w-1, and the world's standing state (pot, trust, pending requests).
    """

    def __init__(self, world, meta=None):
        self.world, self.rows, self.meta = world, [], dict(meta or {})
        self.prev_hook = world.hook
        self._t = len(world.run.trace)
        self._e = len(getattr(world, "events", []) or [])
        self._x = len(world.exit_log)
        self._stay = {}
        world.hook = self

    def __call__(self, world, w):
        if self.prev_hook:
            self.prev_hook(world, w)
        if world is not self.world:          # a rollout copy: never record
            return
        if w > 0:
            self._close(w - 1)

    def stay(self, w, reading):
        """Attach a stay reading (pairing.stay_reading output) taken before week w."""
        self._stay[w] = {r: reading[r]["verdict"] for r in ROLES}
        self.meta.setdefault("stay_readings", []).append({"week": w, **_plain(reading)})

    def lived(self, lived):
        """Copy a harness's decision logs (formation retries, 13-week readings, week-0 values) into meta."""
        for k in ("log", "retries", "week0"):
            v = getattr(lived, k, None)
            if v:
                self.meta[f"lived_{k}"] = _plain(v)
        return self

    @classmethod
    def from_observer(cls, obs, meta=None):
        """The same rows and meta, read from an observer (src/mar/observe.py) instead of a hook: `obs` is an Observer, its rows, or the
        {table: rows} that observe.read returns. Differences from the hook path: the observer reads each week at the end of that week,
        the hook at the start of the next, so pool, money, put and trust can differ on a week whose next start moved them (a harness
        formation, the slow trust recovery), and in the week before a harness formation the hook already reads both members in;
        `trace` keeps the rows the world checked, with the take as proposed. Everything else is the
        same (tests/test_atlas_observer.py)."""
        t = _tables(obs)
        self = cls.__new__(cls)
        self.world, self.prev_hook, self._stay = None, None, {}
        self.meta = dict(meta or {})
        self.rows = rows_from_observer(t)
        run = (t.get("run") or [{}])[0]
        end = (t.get("end") or [{}])[0]
        self.meta.setdefault("exits", end.get("exits", []))
        self.meta["cards"] = run.get("cards", [])
        self.meta["observer"] = run.get("schema")
        rd = t.get("reading", [])
        w0 = next((x for x in rd if x["kind"] == "formation0"), None)
        if w0:
            self.meta["lived_week0"] = {"W": {r: w0["m"][r]["W"] for r in ROLES}, "O": {r: w0["m"][r]["O"] for r in ROLES}}
        rt = [{"week": x["w"], "formed": x.get("formed"), "outside": {r: x["m"][r]["O"] for r in ROLES},
               "baseline": {r: x["m"][r]["W"] for r in ROLES}} for x in rd if x["kind"] == "retry"]
        if rt:
            self.meta["lived_retries"] = rt
        for s in t.get("stay", []):
            self.meta.setdefault("stay_readings", []).append({"week": s["w"], **{r: s[r] for r in ROLES}})
            for row in self.rows:
                if row["week"] == s["w"] - 1:
                    row["stay"] = {r: s[r]["verdict"] for r in ROLES}
        self.obs = t
        return self

    def finish(self):
        world = self.world
        last = len(world.run.outcomes) - 1
        if last >= 0 and (not self.rows or self.rows[-1]["week"] < last):
            self._close(last)
        self.meta.setdefault("exits", [dict(e) for e in world.exit_log])
        gate = getattr(world, "gate", None)
        self.meta["cards"] = [c.id for c in getattr(gate, "cards", [])]
        self.meta["bar_log"] = _plain(getattr(world, "bar_log", []))
        fs = getattr(world, "fstats", None)
        if fs:
            self.meta["fstats"] = {k: v for k, v in fs.items() if isinstance(v, (int, float))}
        return self

    def _close(self, w):
        world = self.world
        tr = world.run.trace[self._t:]
        self._t = len(world.run.trace)
        ev = (getattr(world, "events", []) or [])[self._e:]
        self._e = len(getattr(world, "events", []) or [])
        ex = world.exit_log[self._x:]
        self._x = len(world.exit_log)
        out = world.run.outcomes[-1] if world.run.outcomes else {}
        hed = out.get("hedonic", {}) if out.get("week") == w else {}
        row = {"week": w, "pool": round(float(world.pool), 3), "events": [[r, k] for (_, r, k) in ev if r in ROLES],
               "exits": [{"role": e["role"], "take": e.get("take", 0), "breach": bool(e.get("breach"))} for e in ex]}
        for r in ROLES:
            acts = Counter(t["action"] for t in tr if t.get("role") == r and t.get("executed"))
            blocked = sum(1 for t in tr if t.get("role") == r and not t.get("executed"))
            breach = sum(1 for t in tr if t.get("role") == r and t.get("breach"))
            kinds = Counter(t.get("kind") for t in tr if t.get("role") == r and t.get("executed") and t["action"] == "request")
            h = hed.get(r, {})
            fx = h.get("fix") or {}
            row[r] = {"in": bool(world.p[r]["in"]), "acts": dict(acts), "req_kinds": {str(k): v for k, v in kinds.items()},
                      "blocked": blocked, "breach": breach,
                      "pl": round(float(h.get("pleasure", np.nan)), 4), "s_non": round(float(h.get("s_non", 0.0)), 4),
                      "s_off": round(float(h.get("s_off", 0.0)), 4),
                      "money": round(float(world.p[r]["money"]), 2), "put": round(float(world.put[r]), 2),
                      "money_in": round(float(getattr(world, "money_in", {r: 0})[r]), 2),
                      "trust": round(float(getattr(world, "trust", {r: 0.0})[r]), 4),
                      "pending": sorted(world.pending[r]), "consent": int(world.consent[r]),
                      "bound": sorted(k for k, u in world.bound_req[r].items() if u > w) if hasattr(world, "bound_req") else [],
                      "terms": {k: fx[k] for k in FIX_TERMS if k in fx}}
        # compact trace rows: [role, action, kind, take, allowed, soft, breach, reasons, signature bits, utility]
        row["trace"] = [[t["role"], t["action"], t.get("kind"), t.get("take", 0), bool(t.get("allowed", True)), bool(t.get("soft")),
                         bool(t.get("breach")), list(t.get("reasons", [])), sig_bits(t.get("state")), t.get("u")]
                        for t in tr if t.get("role") in ROLES]
        if w + 1 in self._stay:                         # a reading taken before week w+1 describes the household at the end of w
            row["stay"] = self._stay[w + 1]
        self.rows.append(row)


FIX_TERMS = ("pr_reward", "pr_stigma", "pr_exit", "pr_intrinsic", "c_friend", "friends", "together_now")


def _tables(obs):
    if isinstance(obs, dict):
        return obs
    rows = obs.rows if hasattr(obs, "rows") else obs
    out = {}
    for r in rows:
        out.setdefault(r["t"], []).append(r)
    return out


def rows_from_observer(t):
    """Observer tables -> Recorder rows (one per week, same keys)."""
    weeks = {x["w"]: x for x in t.get("week", [])}
    st = {(x["w"], x["r"]): x for x in t.get("state", [])}
    dec = {}
    for d in t.get("decision", []):
        dec.setdefault(d["w"], []).append(d)
    out = []
    for w in sorted(weeks):
        wk = weeks[w]
        nxt = weeks.get(w + 1, {}).get("pre_events", [])          # the hook path reads the next week's harness events into this row
        row = {"week": w, "pool": round(float(wk["pool"]), 3), "events": [list(e) for e in wk["events"]] + [list(e) for e in nxt],
               "exits": [{"role": e["role"], "take": e.get("take", 0), "breach": bool(e.get("breach"))} for e in wk["exits"]]}
        tr = []
        for d in sorted(dec.get(w, []), key=lambda d: (d["k"], d["r"])):
            for c in d["cands"]:
                if c.get("tr"):
                    tr.append([d["r"], c["a"], c.get("kind"), c.get("take", 0), c["dec"] != "hard", c["dec"] == "soft",
                               c["dec"] == "breach", list(c.get("reasons", [])), d["sig"], c["u"]])
        for r in ROLES:
            s = st.get((w, r), {})
            mine = [x for x in tr if x[0] == r]
            acts = Counter(x[1] for x in mine if x[4])
            kinds = Counter(x[2] for x in mine if x[4] and x[1] == "request")
            fx = ((s.get("parts") or {}).get("x") or {}).get("fix") or {}
            row[r] = {"in": bool(s.get("in")), "acts": dict(acts), "req_kinds": {str(k): v for k, v in kinds.items()},
                      "blocked": sum(1 for x in mine if not x[4]), "breach": sum(1 for x in mine if x[6]),
                      "pl": round(float(s.get("pl", np.nan)), 4), "s_non": round(float(s.get("s_non", 0.0)), 4),
                      "s_off": round(float(s.get("s_off", 0.0)), 4), "money": round(float(s.get("money", 0.0)), 2),
                      "put": round(float(s.get("put", 0.0)), 2), "money_in": round(float(s.get("money_in", 0.0)), 2),
                      "trust": round(float(s.get("trust", 0.0)), 4), "pending": sorted(s.get("pending", [])),
                      "consent": int(s.get("consent", 0)), "bound": sorted(s.get("bound", [])),
                      "terms": {k: fx[k] for k in FIX_TERMS if k in fx}}
        row["trace"] = tr
        out.append(row)
    return out
SIG_KEYS = ("other_earns_more", "no_contact_request", "stay_home_request", "consented", "need_gap>0", "pooled>0", "bound_request",
            "other_in")


def sig_bits(state):
    """The miner's boolean view of a gate state (worlds.household.signature, plus bound_request and other_in) as a bit string."""
    if not state:
        return ""
    v = {"other_earns_more": state.get("other_earns_more", 0), "no_contact_request": state.get("no_contact_request", 0),
         "stay_home_request": state.get("stay_home_request", 0), "consented": state.get("consented", 0),
         "need_gap>0": int(state.get("need_gap", 0) > 0), "pooled>0": int(state.get("pooled", 0) > 0),
         "bound_request": state.get("bound_request", 0), "other_in": state.get("other_in", 1)}
    return "".join("1" if v[k] else "0" for k in SIG_KEYS)


def bits_sig(b):
    return {k: int(c) for k, c in zip(SIG_KEYS, b)}


def _plain(x):
    """JSON-safe copy (sets to sorted lists, numpy scalars to floats, tuples to lists)."""
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if isinstance(x, set):
        return sorted(_plain(v) for v in x)
    if isinstance(x, (np.floating, float)):
        return round(float(x), 5)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (int, str, bool)) or x is None:
        return x
    return str(x)


# ---- 2. features --------------------------------------------------------------------------------------------------------------

FEATURE_DOC = {
    "together_share": "share of weeks with both partners in the household",
    "first_exit": "week of the first leave as a share of the run (1.0 = nobody ever left)",
    "leaves": "number of leaves (a partner walking out; a later return can be followed by another leave)",
    "pl_mean": "mean weekly pleasure over both partners and all weeks",
    "pl_low": "mean weekly pleasure of the partner who did worse over the run",
    "pl_gap": "mean absolute pleasure gap between the partners, weeks both in",
    "s_non": "mean non-offsettable suffering (modeled), both partners",
    "req_rate": "requests made per partner-week, weeks both in",
    "refusal_rate": "refusals per request received (capped at 1), weeks both in",
    "give_in_rate": "share of partner-weeks with a pending request the partner consented to, among weeks with any pending request",
    "init_asym": "who initiates: |requests by A - by B| / all requests (0 = even, 1 = one partner makes every request)",
    "give_asym": "|net giving A - B| / total giving, net giving = give + spend_shared - take_shared (weeks both in)",
    "give_drift": "trend of the give imbalance across 13-week blocks, toward the partner who gives more overall "
                  "(positive = the bargain drifts more one-sided; per block)",
    "pl_gap_drift": "trend of the pleasure gap across 13-week blocks (positive = partners drift apart; per block)",
    "spikes": "conflict spikes per partner-year: pleasure falls SPIKE_DROP below the trailing 4-week mean",
    "repair": "share of spikes followed by recovery to within 0.02 of the pre-spike mean within REPAIR_WEEKS (1.0 when no spikes)",
    "checkins": "check-in, review-request and new-terms events per partner-year",
    "friends": "friend visits per partner-week",
    "pot_share_end": "larger partner's share of all money put into the household at the end (0.5 = even)",
}
CLUSTER_FEATURES = tuple(FEATURE_DOC)

# Descriptive only (not clustered): available in some families, absent in others, so clustering on them would sort by family.
EXTRA_DOC = {
    "who_exits": "role of the first leaver relative to giving: 'giver' (gave more), 'taker', or '' if nobody left",
    "exiter_lower": "1 if the first leaver had the lower mean pleasure in the 13 weeks before leaving",
    "held_share": "share of stay readings classed 'held' (stays only because of pairing pressure); H38 runs only",
    "worth_share": "share of stay readings classed 'worth'; H38 runs only",
    "say_do_gap": "share of a partner's words (check-in answers, agreed terms) taken back by a later lapse or breach; "
                  "only where trust_words is on (v2.3 seed). A behavioral proxy, not typed reports",
    "breaches": "actions taken in breach of a chosen commitment",
}


def _net_give(c):
    return sum(c.get(a, 0) for a in GIVE_ACTS) - c.get("take_shared", 0)


def _slope(y):
    y = np.asarray([v for v in y if v is not None and not np.isnan(v)], float)
    if len(y) < 3:
        return 0.0
    x = np.arange(len(y), dtype=float)
    return float(np.polyfit(x, y, 1)[0])


def spikes_and_repair(pl, inside):
    """pl: weekly pleasure of one partner; inside: weekly bool (both in). -> (spike weeks, repaired flags)."""
    sp, rep = [], []
    w = 4
    while w < len(pl):
        if inside[w] and all(inside[w - 4:w]):
            base = float(np.mean(pl[w - 4:w]))
            if pl[w] < base - SPIKE_DROP:
                sp.append(w)
                ok = any(pl[v] >= base - 0.02 and inside[v] for v in range(w + 1, min(len(pl), w + 1 + REPAIR_WEEKS)))
                rep.append(ok)
                w += 4                       # one spike per dip
                continue
        w += 1
    return sp, rep


def features(rows, meta=None):
    """rows: Recorder rows. -> dict of CLUSTER_FEATURES plus EXTRA_DOC keys (descriptive)."""
    meta = meta or {}
    n = len(rows)
    both = [rows[i]["A"]["in"] and rows[i]["B"]["in"] for i in range(n)]
    nb = max(1, sum(both))
    pl = {r: np.array([x[r]["pl"] for x in rows], float) for r in ROLES}
    acts = {r: [x[r]["acts"] for x in rows] for r in ROLES}
    f = {"together_share": sum(both) / max(1, n)}
    leaves = [(x["week"], e["role"]) for x in rows for e in x["exits"]]
    f["leaves"] = float(len(leaves))
    f["first_exit"] = leaves[0][0] / max(1, n) if leaves else 1.0
    allpl = np.concatenate([pl["A"], pl["B"]])
    f["pl_mean"] = float(np.nanmean(allpl)) if np.isfinite(allpl).any() else 0.0
    f["pl_low"] = float(min(np.nanmean(pl[r]) for r in ROLES))
    gaps = [abs(pl["A"][i] - pl["B"][i]) for i in range(n) if both[i]]
    f["pl_gap"] = float(np.mean(gaps)) if gaps else 0.0
    f["s_non"] = float(np.mean([x[r]["s_non"] for x in rows for r in ROLES]))
    req = {r: sum(acts[r][i].get("request", 0) for i in range(n) if both[i]) for r in ROLES}
    ref = {r: sum(acts[r][i].get("refuse_request", 0) for i in range(n) if both[i]) for r in ROLES}
    f["req_rate"] = (req["A"] + req["B"]) / (2 * nb)
    rr = [min(1.0, ref[r] / req["B" if r == "A" else "A"]) for r in ROLES if req["B" if r == "A" else "A"]]
    f["refusal_rate"] = float(np.mean(rr)) if rr else 0.0
    pend = [(x[r]["consent"]) for x in rows for r in ROLES if x[r]["pending"] and x["A"]["in"] and x["B"]["in"]]
    f["give_in_rate"] = float(np.mean(pend)) if pend else 0.0
    f["init_asym"] = abs(req["A"] - req["B"]) / (req["A"] + req["B"]) if (req["A"] + req["B"]) else 0.0
    giv = {r: sum(max(0, _net_give(acts[r][i])) for i in range(n) if both[i]) for r in ROLES}
    tot = giv["A"] + giv["B"]
    f["give_asym"] = abs(giv["A"] - giv["B"]) / tot if tot else 0.0
    big = "A" if giv["A"] >= giv["B"] else "B"
    sm = "B" if big == "A" else "A"
    imb, gapb = [], []
    for s in range(0, n, BLOCK):
        idx = [i for i in range(s, min(n, s + BLOCK)) if both[i]]
        if len(idx) < 4:
            continue
        gb = sum(max(0, _net_give(acts[big][i])) for i in idx)
        gs = sum(max(0, _net_give(acts[sm][i])) for i in idx)
        imb.append((gb - gs) / (gb + gs) if gb + gs else 0.0)
        gapb.append(float(np.mean([abs(pl["A"][i] - pl["B"][i]) for i in idx])))
    f["give_drift"] = _slope(imb)
    f["pl_gap_drift"] = _slope(gapb)
    nsp, nrep = 0, []
    for r in ROLES:
        sp, rep = spikes_and_repair(pl[r], both)
        nsp += len(sp)
        nrep += rep
    f["spikes"] = nsp / (2 * max(1, n) / 52)
    f["repair"] = float(np.mean(nrep)) if nrep else 1.0
    ck = sum(1 for x in rows for r, k in x["events"] if k in ("checkin", "ask_review", "terms"))
    f["checkins"] = ck / (2 * max(1, n) / 52)
    f["friends"] = sum(x[r]["acts"].get("see_friend", 0) for x in rows for r in ROLES) / (2 * max(1, n))
    mi = {r: rows[-1][r]["money_in"] if rows else 0.0 for r in ROLES}
    f["pot_share_end"] = max(mi.values()) / sum(mi.values()) if sum(mi.values()) else 0.5
    # descriptive extras
    if leaves:
        w0, r0 = leaves[0]
        f["who_exits"] = "giver" if r0 == big and tot else "taker" if tot else "even"
        o0 = "B" if r0 == "A" else "A"
        lo = max(0, w0 - BLOCK)
        f["exiter_lower"] = float(np.nanmean(pl[r0][lo:w0 + 1]) < np.nanmean(pl[o0][lo:w0 + 1]))
    else:
        f["who_exits"], f["exiter_lower"] = "", None
    st = [x["stay"][r] for x in rows if x.get("stay") for r in ROLES]
    f["held_share"] = st.count("held") / len(st) if st else None
    f["worth_share"] = st.count("worth") / len(st) if st else None
    fs = meta.get("fstats") or {}
    f["say_do_gap"] = fs["words_revoked"] / fs["words"] if fs.get("words") else None
    f["breaches"] = float(sum(x[r]["breach"] for x in rows for r in ROLES))
    return f


def matrix(feats, keys=CLUSTER_FEATURES):
    """-> (X raw, Z standardized, mu, sd). Constant columns get sd 1."""
    X = np.array([[float(f[k]) for k in keys] for f in feats], float)
    mu, sd = X.mean(0), X.std(0)
    sd[sd < 1e-12] = 1.0
    return X, (X - mu) / sd, mu, sd


# ---- 3. clustering ------------------------------------------------------------------------------------------------------------

def dist(Z):
    d = ((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1)
    return np.sqrt(np.maximum(d, 0.0))


def kmedoids(D, k, seed=0, iters=100):
    """Alternating k-medoids on a distance matrix: k-means++-style start, then assign / recompute medoid until stable.
    -> (labels, medoid indices, total cost). Deterministic given seed."""
    rng = np.random.default_rng(seed)
    n = len(D)
    med = [int(rng.integers(n))]
    while len(med) < k:
        dm = D[:, med].min(1) ** 2
        p = dm / dm.sum() if dm.sum() > 0 else np.full(n, 1 / n)
        med.append(int(rng.choice(n, p=p)))
    med = np.array(med)
    for _ in range(iters):
        lab = D[:, med].argmin(1)
        new = med.copy()
        for c in range(k):
            m = np.where(lab == c)[0]
            if len(m):
                new[c] = m[D[np.ix_(m, m)].sum(1).argmin()]
        if (new == med).all():
            break
        med = new
    lab = D[:, med].argmin(1)
    return lab, med, float(D[np.arange(n), med[lab]].sum())


def best_kmedoids(D, k, restarts=10, seed=0):
    """Best of `restarts` starts by total cost."""
    best = None
    for s in range(restarts):
        r = kmedoids(D, k, seed=seed * 1000 + s)
        if best is None or r[2] < best[2]:
            best = r
    return best


def silhouette(D, lab):
    n = len(D)
    ks = np.unique(lab)
    if len(ks) < 2:
        return 0.0
    s = np.zeros(n)
    for i in range(n):
        own = lab == lab[i]
        if own.sum() <= 1:
            continue
        a = D[i, own].sum() / (own.sum() - 1)
        b = min(D[i, lab == c].mean() for c in ks if c != lab[i])
        s[i] = (b - a) / max(a, b) if max(a, b) > 0 else 0.0
    return float(s.mean())


def ari(x, y):
    """Adjusted Rand index of two labelings of the same items."""
    x, y = np.asarray(x), np.asarray(y)
    _, xi = np.unique(x, return_inverse=True)
    _, yi = np.unique(y, return_inverse=True)
    M = np.zeros((xi.max() + 1, yi.max() + 1))
    np.add.at(M, (xi, yi), 1)

    def c2(v):
        return (v * (v - 1) / 2).sum()
    n = len(x)
    sij, sa, sb = c2(M), c2(M.sum(1)), c2(M.sum(0))
    exp = sa * sb / (n * (n - 1) / 2) if n > 1 else 0.0
    mx = (sa + sb) / 2
    return float((sij - exp) / (mx - exp)) if mx != exp else 1.0


def stability(Z, k, ref, reps=30, frac=0.8, seed=0, restarts=5):
    """Seed resampling: recluster random `frac` subsets (new k-medoids seeds each time) and compare with the reference labels on the
    shared items. -> {"ari": [...], "jaccard": {cluster: mean best-match Jaccard}} (Hennig's cluster-wise stability)."""
    rng = np.random.default_rng(seed)
    n = len(Z)
    aris, jac = [], {c: [] for c in np.unique(ref)}
    for i in range(reps):
        idx = np.sort(rng.choice(n, int(frac * n), replace=False))
        D = dist(Z[idx])
        lab, _, _ = best_kmedoids(D, k, restarts=restarts, seed=seed + 1 + i)
        aris.append(ari(ref[idx], lab))
        for c in jac:
            A = set(idx[ref[idx] == c])
            if not A:
                continue
            jac[c].append(max(len(A & set(idx[lab == j])) / len(A | set(idx[lab == j])) for j in np.unique(lab)))
    return {"ari": aris, "jaccard": {int(c): float(np.mean(v)) if v else None for c, v in jac.items()}}


def choose_k(Z, ks=range(3, 9), restarts=10):
    """The stated rule: the k in `ks` with the highest mean silhouette. -> (k, {k: silhouette})."""
    D = dist(Z)
    sil = {}
    for k in ks:
        lab, _, _ = best_kmedoids(D, k, restarts=restarts)
        sil[k] = silhouette(D, lab)
    return max(sil, key=sil.get), sil


def lift(labels, groups, c):
    """Over-representation of each group value in cluster c: share in cluster / share overall. -> {value: (n in c, n, lift)}."""
    labels, groups = np.asarray(labels), np.asarray(groups, dtype=object)
    out = {}
    nc = (labels == c).sum()
    for g in sorted(set(groups.tolist()), key=str):
        ng = (groups == g).sum()
        k = ((labels == c) & (groups == g)).sum()
        out[g] = (int(k), int(ng), float((k / nc) / (ng / len(groups))) if nc and ng else 0.0)
    return out


# ---- 4. stories ---------------------------------------------------------------------------------------------------------------

def _fmt_pl(v):
    return "n/a" if v is None or np.isnan(v) else f"{v:.2f}"


def story(rows, meta=None, names=None, block=BLOCK):
    """A short block-by-block account read off the rows. names: {"A": label, "B": label}. -> list of lines (plain English)."""
    names = names or {"A": "A", "B": "B"}
    lines = []
    n = len(rows)
    for s in range(0, n, block):
        seg = rows[s:s + block]
        e = seg[-1]["week"]
        both = [x["A"]["in"] and x["B"]["in"] for x in seg]
        bits = []
        if all(both):
            bits.append("together")
        elif not any(both):
            bits.append("living apart")
        else:
            bits.append(f"together {sum(both)} of {len(seg)} weeks")
        for r in ROLES:
            o = "B" if r == "A" else "A"
            c = Counter()
            for x in seg:
                c.update(x[r]["acts"])
            req = c.get("request", 0)
            ref = c.get("refuse_request", 0)
            g = c.get("give", 0) + c.get("spend_shared", 0)
            t = c.get("take_shared", 0)
            part = []
            if req:
                part.append(f"asked {req} time{'s' if req != 1 else ''}")
            if ref:
                part.append(f"refused {names[o]} {ref} time{'s' if ref != 1 else ''}")
            if g:
                part.append(f"put in {g}")
            if t:
                part.append(f"took from the pot {t} time{'s' if t != 1 else ''}")
            fr = c.get("see_friend", 0)
            if fr:
                part.append(f"saw friends {fr} time{'s' if fr != 1 else ''}")
            pl = np.nanmean([x[r]["pl"] for x in seg])
            bits.append(f"{names[r]} " + (", ".join(part) + "; " if part else "") + f"pleasure {_fmt_pl(pl)}")
        evs = []
        for x in seg:
            for ex in x["exits"]:
                evs.append(f"week {x['week']}: {names[ex['role']]} left" + (" in breach of a commitment" if ex["breach"] else ""))
            for r in ROLES:
                prev = rows[x["week"] - 1][r]["in"] if x["week"] > 0 else None
                if prev is False and x[r]["in"]:
                    evs.append(f"week {x['week']}: {names[r]} moved in")
            kinds = Counter((r, k) for r, k in x["events"] if k in ("checkin", "ask_review", "terms", "formed") or k.startswith("lapse"))
            for (r, k), m in kinds.items():
                if k == "ask_review":
                    evs.append(f"week {x['week']}: {names[r]} asked for a review")
                elif k == "terms":
                    if r == "A":
                        evs.append(f"week {x['week']}: new terms agreed")
                elif k.startswith("lapse"):
                    evs.append(f"week {x['week']}: {names[r]} let a role lapse")
            if x.get("stay") and any(v != "worth" for v in x["stay"].values()):
                evs.append(f"stay reading after week {x['week']}: " + ", ".join(f"{names[r]} {x['stay'][r]}" for r in ROLES))
        ck = sum(1 for x in seg for r, k in x["events"] if k == "checkin")
        if ck:
            evs.append(f"{ck} check-in{'s' if ck != 1 else ''}")
        lines.append(f"Weeks {seg[0]['week']}-{e}: " + "; ".join(bits) + "." + (" " + "; ".join(evs) + "." if evs else ""))
    return lines


# ---- 5. phase 2 (exploratory): does it even out, freely given vs pressured, what tipped, de facto rules -----------------------

LOPSIDED = 0.30         # a 13-week window is lopsided when one partner did more than 65 percent of the net giving (ASSUMED)
EVEN = 0.15             # an imbalance has evened out when the window is back within 57.5/42.5 (ASSUMED)
WINDOW = 13
MIN_FLOW = 4            # windows with fewer than this many giving acts are too thin to call (skipped, not counted as even)


def balance_series(rows, window=WINDOW):
    """-> list of (week, signed imbalance in [-1, 1] = (A - B) / (A + B) of net giving over the trailing window, or None when the
    window is thin or the partners were not both in for most of it). Net giving = give + spend_shared - take_shared, floored at 0."""
    out = []
    for i in range(len(rows)):
        seg = rows[max(0, i - window + 1):i + 1]
        both = [x for x in seg if x["A"]["in"] and x["B"]["in"]]
        if len(both) < window // 2 + 1:
            out.append((rows[i]["week"], None))
            continue
        g = {r: sum(max(0, _net_give(x[r]["acts"])) for x in both) for r in ROLES}
        tot = g["A"] + g["B"]
        out.append((rows[i]["week"], (g["A"] - g["B"]) / tot if tot >= MIN_FLOW else None))
    return out


def evening(rows):
    """The author's criterion, 'lopsided is normal for a while as long as it evens out'. Episodes: a run of weeks whose trailing
    window is lopsided (|imbalance| >= LOPSIDED) toward one partner; it ends evened when the window comes back within EVEN, or
    flips side; otherwise it ends unresolved (a partner left, the window went thin, or the run ended).
    -> {"episodes": [{"start", "end", "weeks", "toward", "outcome": "evened" | "exit" | "thin" | "run_end"}], "cum": final cumulative
    share of the larger giver, "never_evened": bool (some episode never evened), "ever_lopsided": bool}"""
    ser = balance_series(rows)
    exits = {x["week"] for x in rows for _ in x["exits"]}
    eps, cur = [], None
    for w, v in ser:
        if cur is None:
            if v is not None and abs(v) >= LOPSIDED:
                cur = {"start": w, "toward": "A" if v > 0 else "B"}
            continue
        side = 1 if cur["toward"] == "A" else -1
        if w in exits:
            eps.append({**cur, "end": w, "outcome": "exit"})
            cur = None
        elif v is None:
            eps.append({**cur, "end": w, "outcome": "thin"})
            cur = None
        elif v * side < EVEN:
            eps.append({**cur, "end": w, "outcome": "evened"})
            cur = None
            if abs(v) >= LOPSIDED:              # flipped straight to the other side
                cur = {"start": w, "toward": "A" if v > 0 else "B"}
    if cur is not None:
        eps.append({**cur, "end": rows[-1]["week"], "outcome": "run_end"})
    for e in eps:
        e["weeks"] = e["end"] - e["start"]
    g = {r: sum(max(0, _net_give(x[r]["acts"])) for x in rows if x["A"]["in"] and x["B"]["in"]) for r in ROLES}
    tot = g["A"] + g["B"]
    return {"episodes": eps, "cum": max(g.values()) / tot if tot else 0.5, "ever_lopsided": bool(eps),
            "never_evened": any(e["outcome"] != "evened" for e in eps)}


# Kinds of giving and accepting, read off the trace and the persona policy (worlds/household.py PersonaAgent). Each label says
# how much of it is read and how much is a guess.
GIVE_CLASS_DOC = {
    "a_own": "(a) the giver's own wish: a gift to the partner or a friend from the prosocial gift rule (fires when the giver is "
             "prosocial >= 0.5 and the partner is short of money); a 'yes' to a request by a persona whose style says yes on its "
             "own terms (collaborative or direct with low autonomy). READ from the policy; the policy models care, not pleasure "
             "in giving, so 'own pleasure' is a GUESS at the gloss",
    "b_hard": "(b) a request that was hard to refuse: a 'yes' to a request the receiver had bound itself to (commitment), or to a "
              "pressing 'time' request (the overasker). READ",
    "c_avoid": "(c) avoiding conflict or exit: a 'yes' from an accommodating persona (always yes) or an avoidant one (a coin "
               "flip). GUESS: the policy does not say why they say yes; this is the closest reading of the style",
    "reliance": "paying the household's bills (spend_shared): driven by an unpaid gap, security weight and prosociality. Reliance, "
                "which the author counts as fine; not split into (a) to (c)",
    "sanctioned": "a give or contribution made while a soft card's sanction was being weighed (the row is marked soft). READ",
}


def classify_gives(rows, meta, obs=None):
    """-> Counter of GIVE_CLASS_DOC keys over gives, bill contributions and accepted requests, both partners. An accepted request is
    a request row whose receiver's consent flag is 1 at the end of that week (READ; a second request the same week can overwrite it,
    rare). With observer tables (`obs`, or a Recorder built by from_observer) the accepted requests are read from the consent table
    instead: every answer, the coin flip and trust draw that made it, and whether a commitment overrode it (no guess, no overwrite)."""
    obs = obs if obs is not None else meta.get("_obs")
    if obs is not None:
        return _classify_gives_obs(rows, obs)
    styles = {r: meta["personas"][r]["style"] for r in ROLES}
    auto = {r: meta["personas"][r]["weights"].get("autonomy", 0.5) for r in ROLES}
    c = Counter()
    for x in rows:
        for t in x.get("trace", []):
            role, act, kind, _take, allowed, soft = t[0], t[1], t[2], t[3], t[4], t[5]
            if not allowed:
                continue
            if act in ("give", "spend_shared") and soft:
                c["sanctioned"] += 1
            elif act == "give":
                c["a_own"] += 1
            elif act == "spend_shared":
                c["reliance"] += 1
            elif act == "request":
                o = "B" if role == "A" else "A"
                if not x[o]["consent"]:
                    continue
                if kind in x[o].get("bound", []) or kind == "time":
                    c["b_hard"] += 1
                elif styles[o] in ("accommodating", "avoidant"):
                    c["c_avoid"] += 1
                elif styles[o] in ("collaborative", "direct") and auto[o] < 0.5:
                    c["a_own"] += 1
                else:
                    c["b_hard"] += 1          # a yes the style would not give: trust-scaled draws only lower yeses, so this is rare
    return c


def _classify_gives_obs(rows, obs):
    t = _tables(obs)
    c = Counter()
    for x in rows:
        for tr in x.get("trace", []):
            role, act, allowed, soft = tr[0], tr[1], tr[4], tr[5]
            if not allowed:
                continue
            if act in ("give", "spend_shared") and soft:
                c["sanctioned"] += 1
            elif act == "give":
                c["a_own"] += 1
            elif act == "spend_shared":
                c["reliance"] += 1
    for k in t.get("consent", []):
        if not k.get("final"):
            continue
        if k.get("bound") or k.get("kind") == "time":
            c["b_hard"] += 1
        elif k.get("style") in ("accommodating", "avoidant"):
            c["c_avoid"] += 1
        elif k.get("would"):
            c["a_own"] += 1
        else:
            c["b_hard"] += 1
    return c


def leave_reasons(rows, obs=None):
    """-> Counter of the harness's own leave reasons (events 'leave_<why>': distress, bar, ladder ...), or 'unrecorded' for an exit
    with no reason event (worlds without the fixes). With observer tables the reason is read off the leave decision itself, and a
    distress leave is split by the condition that held: 'distress:low' (4+ low weeks), 'distress:N' (non-offsettable load >= 0.2),
    'distress:trust' (trust below leave_below), joined with '+' when several held."""
    if obs is not None:
        c = Counter()
        for d in _tables(obs).get("decision", []):
            if d["chosen"] is None or d["cands"][d["chosen"]]["a"] != "leave":
                continue
            why = d["cands"][d["chosen"]].get("why")
            lc = d.get("leave_ctx") or {}
            if why in (None, "distress"):
                held = [k for k, f in (("low", "low"), ("N", "n_high"), ("trust", "trust_low")) if lc.get(f)]
                why = "distress:" + "+".join(held) if held else (why or "unrecorded")
            c[why] += 1
        return c
    c = Counter()
    for x in rows:
        why = [k[6:] for r, k in x["events"] if k.startswith("leave_")]
        for i, _e in enumerate(x["exits"]):
            c[why[i] if i < len(why) else "unrecorded"] += 1
    return c


def stay_margins(meta):
    """H38 stay readings -> per member-reading: margin (stay value - outside), the pressure part of it ((sq - sq_free) - (o - o_free)),
    the rest (everything the reading does not separate), and whether pressure decided it (verdict held or pushed_out)."""
    out = []
    for rd in meta.get("stay_readings", []):
        for r in ROLES:
            x = rd[r]
            m, mf = x["sq"] - x["o"], x["sq_free"] - x["o_free"]
            out.append({"week": rd["week"], "role": r, "margin": m, "pressure_part": m - mf, "rest": mf, "verdict": x["verdict"],
                        "pressure_decided": x["verdict"] in ("held", "pushed_out")})
    return out


def formation_margins(meta):
    """Week-0 and retry formation decisions -> [{week, role, margin (household value - outside value), decisive (lowest margin)}]."""
    out = []
    w0 = meta.get("lived_week0")
    evs = ([{"week": 0, "baseline": w0["W"], "outside": w0["O"]}] if w0 else []) + list(meta.get("lived_retries", []))
    for e in evs:
        if not all(r in e.get("baseline", {}) and r in e.get("outside", {}) for r in ROLES):
            continue                        # negotiated harness (Lived) logs by persona id with other fields: not a baseline retry
        ms = {r: e["baseline"][r] - e["outside"][r] for r in ROLES}
        lo = min(ms, key=ms.get)
        for r in ROLES:
            out.append({"week": e["week"], "role": r, "margin": ms[r], "decisive": r == lo, "formed": all(v >= 0 for v in ms.values())})
    return out


def trace_rows_for_miner(rows):
    """Compact trace rows -> the dicts worlds.household.mine reads (state rebuilt from the signature bits)."""
    out = []
    for x in rows:
        for t in x.get("trace", []):
            if not t[8]:
                continue
            s = bits_sig(t[8])
            st = {"other_earns_more": s["other_earns_more"], "no_contact_request": s["no_contact_request"],
                  "stay_home_request": s["stay_home_request"], "consented": s["consented"], "need_gap": s["need_gap>0"],
                  "pooled": s["pooled>0"]}
            out.append({"role": t[0], "action": t[1], "take": t[3] or 0, "allowed": t[4], "state": st})
    return out


def card_firings(rows, cards):
    """-> {card id: {"blocked": n, "soft": n, "breach": n, "cited_allowed": n}} counted from trace reasons (a card binds when it is
    cited on a blocked, sanctioned or breached row)."""
    f = {c: Counter() for c in cards}
    for x in rows:
        for t in x.get("trace", []):
            allowed, soft, breach, reasons = t[4], t[5], t[6], t[7]
            for c in cards:
                if any(c in s for s in reasons):
                    f[c]["blocked" if not allowed else "breach" if breach else "soft" if soft else "cited_allowed"] += 1
    return {c: dict(v) for c, v in f.items()}


def behavior_cells(rows):
    """Executed actions by signature bit: -> {(action, feature, value): count} and {(feature, value): partner-weeks seen}, weeks a
    partner is in. Used to find de facto regularities (an action that never happens in a state it could happen in)."""
    acts, base = Counter(), Counter()
    for x in rows:
        for r in ROLES:
            if not x[r]["in"]:
                continue
            ts = [t for t in x.get("trace", []) if t[0] == r and t[8]]
            if not ts:
                continue
            s = bits_sig(ts[0][8])
            for k, v in s.items():
                base[(k, v)] += 1
            done = {t[1] for t in ts if t[4]}
            for a in done:
                for k, v in s.items():
                    acts[(a, k, v)] += 1
    return acts, base


# ---- 6. short blind stories (story-rating set) -------------------------------------------------------------------------------

def _who_more(a, b, na, nb, what):
    if a + b < 3:
        return None
    if a >= 2 * b:
        return f"{na} {what} most of the time"
    if b >= 2 * a:
        return f"{nb} {what} most of the time"
    return f"they {what} about evenly"


def short_story(rows, names, parts=4):
    """A blind story of at most about 120 words: `parts` stretches, each told from behavior only (living together or apart, who paid
    the household's bills, asks and refusals, gifts, friends, moves, leaves, and stay readings put in words). No scores, no pleasure
    numbers, no arm or rule names. -> str."""
    n = len(rows)
    size = -(-n // parts)
    out = []
    for s in range(0, n, size):
        seg = rows[s:s + size]
        lo, hi = seg[0]["week"], seg[-1]["week"]
        na, nb = names["A"], names["B"]
        both = sum(1 for x in seg if x["A"]["in"] and x["B"]["in"])
        c = {r: Counter() for r in ROLES}
        for x in seg:
            for r in ROLES:
                c[r].update(x[r]["acts"])
        bits = []
        if both == len(seg):
            bits.append("They lived together")
        elif both == 0:
            bits.append("They lived apart")
        else:
            bits.append(f"They lived together {both} of {len(seg)} weeks")
        if both:
            b = _who_more(c["A"].get("spend_shared", 0), c["B"].get("spend_shared", 0), na, nb, "paid the bills")
            if b:
                bits.append(b)
        for r, o in (("A", "B"), ("B", "A")):
            q, f = c[r].get("request", 0), c[o].get("refuse_request", 0)
            if q:
                bits.append(f"{names[r]} asked {names[o]} for things {q} times and was turned down {f}")
            g = c[r].get("give", 0)
            if g:
                bits.append(f"{names[r]} gave money {g} time{'s' if g != 1 else ''}")
            t = c[r].get("take_shared", 0)
            if t:
                bits.append(f"{names[r]} took from the shared pot {t} time{'s' if t != 1 else ''}")
        fr = {r: c[r].get("see_friend", 0) / len(seg) for r in ROLES}
        for r in ROLES:
            if fr[r] >= 1.5:
                bits.append(f"{names[r]} saw friends a lot")
            elif fr[r] < 0.3:
                bits.append(f"{names[r]} rarely saw friends")
        evs = {}                                 # phrase -> weeks, so repeats read as one line
        for x in seg:
            wk = x["week"]
            for r in ROLES:
                left = any(e["role"] == r for e in x["exits"])
                back = bool(x[r]["acts"].get("return"))
                prev = rows[wk - 1][r]["in"] if wk > 0 else None
                if left and back:
                    ph = f"{names[r]} came back and left again"
                elif left:
                    ph = f"{names[r]} moved out"
                elif back:
                    ph = f"{names[r]} came back"
                elif prev is False and x[r]["in"] and wk > 0:
                    ph = f"{names[r]} moved in"
                else:
                    continue
                evs.setdefault(ph, []).append(wk)
        for ph, ws in evs.items():
            bits.append(f"{ph} in week {ws[0]}" if len(ws) == 1 else f"{ph} in weeks " + ", ".join(map(str, ws)))
        held = {r: sum(1 for x in seg if x.get("stay") and x["stay"][r] == "held") for r in ROLES}
        for r in ROLES:
            if held[r]:
                bits.append(f"{names[r]} stayed mainly under pressure to stay paired" + (" (said more than once)" if held[r] > 1 else ""))
        bits = list(dict.fromkeys(bits))
        if len(bits) > 7:                       # keep stories short: the first seven things that happened in the stretch
            bits = bits[:7]
        out.append(f"Weeks {lo}-{hi}: " + "; ".join(bits) + ".")
    return " ".join(out)
