"""Loop b counting (docs/results/loop-b-counting-prereg.md). No model calls, no network.

Applies the preregistered counting rule to experiments/questions.jsonl and experiments/changes.jsonl.
The rule needs judgment, so the primary rater's labels are written out below (LABELS), one entry per event,
with a topic key per opportunity item (TOPICS) for the pass number. Everything else is mechanical:
dedupe, items, halves, sessions, rates, fatigue proxies, rater agreement and the verdict.

    uv run python scripts/loop_b_count.py [--rater2 docs/results/loop-b-rater2.json]
"""
import argparse
import json
import random
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mar import log as explog  # noqa: E402
from mar.stats import fisher_exact_p, risk_difference  # noqa: E402

CORRECTION = {"B1", "B2", "B3", "B4"}
OPPORTUNITY = CORRECTION | {"R", "U", "C"}
ALL_KINDS = OPPORTUNITY | {"S", "D", "G", "Q"}
LOCAL = timezone(timedelta(hours=-5))  # repo commit times are -0500
SESSION_GAP_MIN = 60
N_POWER = 40          # items per half for 80% power at 0.6 vs 0.3 (prereg power table)
DROP = 0.20
LEN_RATIO = 0.7
BARE_RISE = 0.20
KAPPA_MIN = 0.6
BARE_WORDS = {"yes", "yeah", "yep", "ok", "okay", "sure", "and", "that", "matches", "1", "2", "3"}

# Primary rater's labels. Opportunity rows list one kind per item (prereg Step 2).
LABELS = {
    "q11": ["S"], "q12": ["S"], "q13": ["Q"], "q14": ["Q"], "q15": ["S"],
    "q16": ["S"], "q17": ["Q"], "q18": ["S"], "q19": ["S"], "q20": ["S"], "q21": ["S"],
    "q22": ["S"], "q23": ["S"], "q24": ["Q"], "q25": ["S"], "q26": ["Q"], "q27": ["Q"],
    "q28": ["S"], "q29": ["S"], "q30": ["S"], "q31": ["D"], "q32": ["S"], "q33": ["S"], "q34": ["Q"],
    "c0": ["B1"],                 # seed read-back: sharing optional -> shared always; control (nwim)
    "q35": ["S"], "q36": ["S"],
    "q37": ["C"],                 # accepts equal liberty + domination penalty
    "q38": ["B2"],                # liberty answer: withdrawal not counted as loss of freedom (hedged)
    "c1": ["B1"],                 # R3b rejected: pot rules are negotiated (nwim)
    "q39": ["S"], "q40": ["D"], "q41": ["D"],
    "c2": ["B4"],                 # "1": single pot, against the coded per-person shares (T2)
    "q42": ["G"],
    "q43": ["C"],                 # accepts Claude's default exit floor
    "q44": ["D"], "q45": ["D"],
    "c3": ["B1", "B2"],           # 12-13 negotiated exit terms (B1); rule 8 implicit penalties, "idk" (B2)
    "q46": ["C"],                 # v2.2 confirmed with a condition (T: condition leaves content as shown)
    "q47": ["S"], "q48": ["S"],
    "c4": ["B1"],                 # oracle: companionship undercounted (nwim)
    "q49": ["S"], "q50": ["G"], "c5": ["G"], "c6": ["G"], "c7": ["G"],
    "q51": ["S"], "q52": ["S"], "q53": ["S"], "q54": ["S"], "q55": ["S"], "q56": ["S"], "q57": ["S"],
    "q58": ["S"], "q59": ["S"], "q60": ["S"], "q61": ["S"], "q62": ["S"], "c8": ["G"], "q63": ["S"],
    "q64": ["C"],                 # Q11: accepts Claude's recommendation (sweep centers)
    "q65": ["B1"],                # Q12: rejects the two-mode framing
    "q66": ["C"],                 # Q12: accepts three lenses (adds novelty reward: T1 not triggered, content kept)
    "q67": ["D"],
    "q68": ["C"],                 # Q12 biology read-back confirmed
    "q69": ["B2"],                # ... then widened: novelty also carries liking (T3)
    "q70": ["S"], "c9": ["G"], "q71": ["G"], "c10": ["G"],
    "c11": ["C"],                 # score: pleasure minus suffering, hedged
    "c12": ["R"],                 # baseline may decline: Claude's finding, author approves
    "c13": ["G"], "q72": ["G"],
    "q73": ["B3"],                # trust: "only actions" -> "mostly actions"
    "q74": ["B2"],                # fines on lapsed roles: no default fine, only by mutual choice
    "q75": ["B2"],                # ladder covers general unhappiness too
    "q76": ["C"],                 # decency floor confirmed
    "c14": ["G"], "c15": ["G"], "c16": ["G"],
    "c17": ["B4"],                # verdict rule: judge on pleasure, against the net-wellbeing draft
    "c18": ["C"],                 # everyone counts: the draft already counted everyone
    "q77": ["B2", "U"],           # Q2: renegotiating directly can be fine too; Q4: not quite sure
    "q78": ["U"],                 # Q4 unevenness, unsure
    "c19": ["C", "G"],            # Q4: picks Claude's first option, "mostly"; "do all three" is G
    "c20": ["G"],
    "q80": ["C", "C"],            # Q6, Q7
    "q81": ["B2"],                # Q8: giving into a void, receiver pleasure need not be real
    "q82": ["C", "C"],            # Q8 (revised), Q9
    "q83": ["C"],                 # Q10 "yes that matches" (the revision prompt is not logged: T5)
    "q84": ["C"],                 # Q13: position stands
    "c21": ["G"],
}

# Topic key per opportunity item, for the pass number (prereg Design: Pass).
TOPICS = {
    "c0": ["seed-sharing"], "q37": ["freedom-measure"], "q38": ["freedom-measure"], "c1": ["seed-pot"],
    "c2": ["seed-pot"], "q43": ["exit-floor"], "c3": ["seed-exit-terms", "seed-commitment"],
    "q46": ["seed-exit-terms"], "c4": ["oracle-companionship"], "q64": ["Q11"], "q65": ["Q12"],
    "q66": ["Q12"], "q68": ["Q12"], "q69": ["Q12"], "c11": ["retest-score"], "c12": ["retest-baseline"],
    "q73": ["Q2-trust"], "q74": ["Q2-fines"], "q75": ["Q2-ladder"], "q76": ["Q5-floor"],
    "c17": ["retest-verdict"], "c18": ["retest-who-counts"], "q77": ["Q2-ladder", "Q4"], "q78": ["Q4"],
    "c19": ["Q4", None], "q80": ["Q6", "Q7"], "q81": ["Q8"], "q82": ["Q8", "Q9"], "q83": ["Q10"],
    "q84": ["Q13"],
}

# Author words that appear only in a document (rule T5): reported as a sensitivity line, never counted.
UNLOGGED = [("Q10", "B2", "why narrowing into a partners world particular versus just in general",
             "docs/notes/hedonic-technology-synthesis.md section 5, Q10 read-back record")]


# ------------------------------------------------------------------ loading

def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def load_events(exp_dir=ROOT / "experiments") -> list:
    """Author events in time order: dedupe same quote < 10 s apart, keep the changes row."""
    exp = Path(exp_dir)
    ev = []
    for i, r in enumerate(explog.read_rows(exp / explog.QUESTIONS_NAME)):
        if not r.get("backfilled"):
            ev.append({"id": f"q{i}", "ts": _ts(r["timestamp"]), "quote": r.get("quote") or "", "src": "q"})
    changes = []
    for i, r in enumerate(explog.read_rows(exp / explog.CHANGES_NAME)):
        changes.append({"id": f"c{i}", "ts": _ts(r["timestamp"]), "quote": r.get("quote") or "", "src": "c",
                        "nwim": bool(r.get("not_what_i_meant"))})
    keep = []
    for e in ev:
        dup = any(c["quote"] == e["quote"] and abs((c["ts"] - e["ts"]).total_seconds()) < 10 for c in changes)
        if not dup:
            keep.append(e)
    out = sorted(keep + changes, key=lambda e: (e["ts"], e["id"]))
    return out


def attach(events, labels, topics=None) -> list:
    """Items in time order. Each item: event id, ts, kind, topic, quote. Raises if an event has no label."""
    missing = [e["id"] for e in events if e["id"] not in labels]
    if missing:
        raise ValueError(f"unlabeled events: {missing}")
    bad = {k for v in labels.values() for k in v} - ALL_KINDS
    if bad:
        raise ValueError(f"unknown kinds: {bad}")
    items = []
    for e in events:
        for j, kind in enumerate(labels[e["id"]]):
            topic = (topics or {}).get(e["id"], [None] * 9)[j] if topics else None
            items.append({"event": e["id"], "ts": e["ts"], "kind": kind, "topic": topic, "quote": e["quote"]})
    return items


def opportunity_items(items) -> list:
    out = [dict(it) for it in items if it["kind"] in OPPORTUNITY]
    seen = {}
    for it in out:
        t = it["topic"]
        seen[t] = seen.get(t, 0) + 1
        it["pass"] = seen[t] if t is not None else 1
    return out


# ------------------------------------------------------------------ measures

def n_corr(items) -> int:
    return sum(it["kind"] in CORRECTION for it in items)


def rate(items):
    return n_corr(items) / len(items) if items else None


def halves(seq):
    h = len(seq) // 2
    return seq[:h], seq[h:]


def sessions(events, gap_min=SESSION_GAP_MIN) -> dict:
    """event id -> session number (1-based); new session after a gap > gap_min between events."""
    out, s, prev = {}, 1, None
    for e in events:
        if prev is not None and (e["ts"] - prev).total_seconds() / 60 > gap_min:
            s += 1
        out[e["id"]] = s
        prev = e["ts"]
    return out


def words(q: str) -> int:
    return len(q.split())


def is_bare(q: str) -> bool:
    w = re.sub(r"[^\w\s]", " ", q.lower()).split()
    return 0 < len(w) <= 4 and all(x in BARE_WORDS for x in w)


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def opp_events_by_half(opp):
    """Opportunity events (one entry per event) split by the half of their first item."""
    first, second = halves(opp)
    ids1 = list(dict.fromkeys(it["event"] for it in first))
    ids2 = [i for i in dict.fromkeys(it["event"] for it in second) if i not in ids1]
    q = {it["event"]: it["quote"] for it in opp}
    return [q[i] for i in ids1], [q[i] for i in ids2]


def kappa(a: list, b: list):
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def kappa_ci(a, b, n_boot=2000, seed=0):
    rng = random.Random(seed)
    n = len(a)
    ks = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        k = kappa([a[i] for i in idx], [b[i] for i in idx])
        if k is not None:
            ks.append(k)
    ks.sort()
    return ks[int(0.025 * len(ks))], ks[int(0.975 * len(ks)) - 1]


def agreement(events, lab1, lab2):
    """P0a: kappa on 'is an opportunity' over all events. P0b: kappa on 'holds a correction' over events
    either rater marked an opportunity. Also raw agreement on the full kind list."""
    ids = [e["id"] for e in events]
    opp1 = [int(any(k in OPPORTUNITY for k in lab1[i])) for i in ids]
    opp2 = [int(any(k in OPPORTUNITY for k in lab2[i])) for i in ids]
    either = [i for i, x, y in zip(ids, opp1, opp2) if x or y]
    cor1 = [int(any(k in CORRECTION for k in lab1[i])) for i in either]
    cor2 = [int(any(k in CORRECTION for k in lab2[i])) for i in either]
    exact = sum(lab1[i] == lab2[i] for i in ids) / len(ids)
    return {"n_events": len(ids), "kappa_opp": kappa(opp1, opp2), "kappa_opp_ci": kappa_ci(opp1, opp2),
            "n_either_opp": len(either), "kappa_corr": kappa(cor1, cor2), "kappa_corr_ci": kappa_ci(cor1, cor2),
            "agree_opp": sum(x == y for x, y in zip(opp1, opp2)) / len(ids),
            "agree_corr": sum(x == y for x, y in zip(cor1, cor2)) / len(either) if either else None,
            "exact_kind_list": exact,
            "disagreements": [(i, lab1[i], lab2[i]) for i in ids if lab1[i] != lab2[i]],
            "n_corr_rater1": sum(sum(k in CORRECTION for k in lab1[i]) for i in ids),
            "n_corr_rater2": sum(sum(k in CORRECTION for k in lab2[i]) for i in ids),
            "n_opp_items_rater1": sum(sum(k in OPPORTUNITY for k in lab1[i]) for i in ids),
            "n_opp_items_rater2": sum(sum(k in OPPORTUNITY for k in lab2[i]) for i in ids)}


def p1_clause(first, second):
    k1, n1, k2, n2 = n_corr(first), len(first), n_corr(second), len(second)
    if not n1 or not n2:
        return {"holds": False, "drop": None, "p": None}
    drop = k1 / n1 - k2 / n2
    p = fisher_exact_p(k1, n1, k2, n2, alternative="greater")
    return {"holds": drop >= DROP and p < 0.05, "drop": drop, "p": p, "k1": k1, "n1": n1, "k2": k2,
            "n2": n2, "ci": risk_difference(k1, n1, k2, n2) if 0 < k1 + k2 < n1 + n2 else None}


def analyze(opp, kappas=None):
    """Verdict from a list of opportunity items (each with kind, quote, event, pass) and optional
    kappas (kappa_opp, kappa_corr). Pure: used on the real logs and on synthetic fixtures."""
    first, second = halves(opp)
    p1 = p1_clause(first, second)
    q1, q2 = opp_events_by_half(opp)
    m1, m2 = _median([words(q) for q in q1]), _median([words(q) for q in q2])
    ratio = (m2 / m1) if m1 else None
    b1 = sum(map(is_bare, q1)) / len(q1) if q1 else 0.0
    b2 = sum(map(is_bare, q2)) / len(q2) if q2 else 0.0
    p2a = ratio is not None and ratio >= LEN_RATIO
    p2b = (b2 - b1) < BARE_RISE
    f1 = [it for it in first if it.get("pass", 1) == 1]
    s1 = [it for it in second if it.get("pass", 1) == 1]
    p3 = p1_clause(f1, s1)
    p3["holds"] = p3["drop"] is not None and p3["drop"] >= DROP and p3["p"] < 0.05
    p0a = p0b = None
    if kappas is not None:
        p0a = kappas["kappa_opp"] is not None and kappas["kappa_opp"] >= KAPPA_MIN
        p0b = kappas["kappa_corr"] is not None and kappas["kappa_corr"] >= KAPPA_MIN
    if kappas is not None and not (p0a and p0b):
        verdict = "rule not operational"
    elif len(first) < N_POWER or len(second) < N_POWER:
        d = p1["drop"]
        word = "falling" if d is not None and d >= DROP else "rising" if d is not None and d <= -DROP else "flat"
        verdict = f"descriptive only, underpowered ({word})"
    elif p1["holds"] and p2a and p2b:
        verdict = "converging"
    elif p1["holds"]:
        verdict = "falling, fatigue not excluded"
    else:
        verdict = "not converging"
    return {"verdict": verdict, "P0a": p0a, "P0b": p0b, "P1": p1, "P2a": p2a, "P2b": p2b, "P3": p3,
            "len_median": (m1, m2), "len_ratio": ratio, "bare": (b1, b2), "n_half": (len(first), len(second)),
            "pass2_share": (sum(it.get("pass", 1) > 1 for it in first) / len(first) if first else None,
                            sum(it.get("pass", 1) > 1 for it in second) / len(second) if second else None)}


# ------------------------------------------------------------------ report

def by_kind(items) -> dict:
    out = {}
    for it in items:
        out[it["kind"]] = out.get(it["kind"], 0) + 1
    return dict(sorted(out.items()))


def report(events, items, opp, res, agree=None) -> str:
    sess = sessions(events)
    lines = [f"events {len(events)}, items {len(items)}, opportunity items {len(opp)}, corrections {n_corr(opp)}",
             f"kinds (all items): {by_kind(items)}"]
    for s in sorted(set(sess.values())):
        evs = [e for e in events if sess[e["id"]] == s]
        so = [it for it in opp if sess[it["event"]] == s]
        t0, t1 = evs[0]["ts"].astimezone(LOCAL), evs[-1]["ts"].astimezone(LOCAL)
        si = [it for it in items if sess[it["event"]] == s]
        lines.append(f"session {s}: {t0:%Y-%m-%d %I:%M %p} to {t1:%I:%M %p} local, events {len(evs)}, "
                     f"opp items {len(so)}, corrections {n_corr(so)}, rate {rate(so) if so else None}, "
                     f"kinds {by_kind(si)}")
        a, b = halves(so)
        lines.append(f"  within session halves: {n_corr(a)}/{len(a)} then {n_corr(b)}/{len(b)}")
    lines.append(f"halves: {res['P1']}")
    lines.append(f"P2 median words {res['len_median']} ratio {res['len_ratio']}; bare share {res['bare']}")
    lines.append(f"P3 pass-1 only: {res['P3']}; pass>=2 share by half {res['pass2_share']}")
    hours = {}
    for it in opp:
        h = it["ts"].astimezone(LOCAL).strftime("%I %p")
        k = hours.setdefault(it["ts"].astimezone(LOCAL).hour, [h, 0, 0])
        k[1] += it["kind"] in CORRECTION
        k[2] += 1
    lines.append("by local hour: " + ", ".join(f"{v[0]}: {v[1]}/{v[2]}" for _, v in sorted(hours.items())))
    lines.append("items in order: " + " ".join(f"{it['event']}:{it['kind']}(p{it['pass']})" for it in opp))
    for topic, kind, quote, where in UNLOGGED:
        lines.append(f"sensitivity (T5, not counted): {topic} {kind} \"{quote}\" in {where}; with it, "
                     f"{n_corr(opp) + 1}/{len(opp) + 1}")
    if agree:
        lines.append("agreement: " + json.dumps({k: v for k, v in agree.items() if k != "disagreements"}))
        for d in agree["disagreements"]:
            lines.append(f"  disagree {d[0]}: rater1 {d[1]} rater2 {d[2]}")
    lines.append(f"VERDICT: {res['verdict']}  (P0a {res['P0a']}, P0b {res['P0b']}, P1 {res['P1']['holds']}, "
                 f"P2a {res['P2a']}, P2b {res['P2b']}, P3 {res['P3']['holds']})")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rater2", default=None)
    args = ap.parse_args(argv)
    events = load_events()
    items = attach(events, LABELS, TOPICS)
    opp = opportunity_items(items)
    agree = None
    if args.rater2:
        lab2 = json.loads(Path(args.rater2).read_text())
        agree = agreement(events, LABELS, lab2)
    res = analyze(opp, agree)
    print(report(events, items, opp, res, agree))
    if agree:  # sensitivity: the verdict and rates under the second rater's labels
        opp2 = opportunity_items(attach(events, lab2))
        f, s = halves(opp2)
        print(f"rater2 labels: opp items {len(opp2)}, corrections {n_corr(opp2)}, halves "
              f"{n_corr(f)}/{len(f)} then {n_corr(s)}/{len(s)}, verdict {analyze(opp2)['verdict']}")


if __name__ == "__main__":
    main()
