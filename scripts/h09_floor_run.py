"""H09: do LLM negotiators avoid below-floor terms because of a fairness prior, or because they understood the floor?
Prereg: docs/results/h09-prereg.md. Results: docs/results/h09.md. Refuses to run live without --max-usd.

  uv run python scripts/h09_floor_run.py --dry-run --model claude-haiku-5-5
  uv run python scripts/h09_floor_run.py --model claude-haiku-5-5 --max-usd 1
  uv run python scripts/h09_floor_run.py --analyze            # re-print every number from experiments/kept/h09-2026-11-10/results.json

Two arms, the same 6 pairings x seeds, the same model for both members: "stated" (the floor rule is in the prompt, as in the pilot) and
"removed" (the floor rule is not in the prompt; the floor and proof checks still run after the fact, so the model is told only "that deal
could not take effect" when a deal is blocked). Proposals, not agreements, are the measurement. Living after agreement is not run.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mar import negotiation as N  # noqa: E402
from mar import negotiation_llm as NL  # noqa: E402
from mar import stats as S  # noqa: E402
from mar.agents.base import AgentError, BudgetExceeded, Ledger  # noqa: E402
from mar.agents.claude import PRICES  # noqa: E402
import negotiation_llm_run as NR  # noqa: E402  (a script module: its work is behind __main__ guards)

OUT = Path(__file__).parent.parent / "experiments" / "kept" / "h09-2026-11-10"
PAIRS = NR.PAIRS
SEEDS = (0, 1, 2, 3, 4)
ARMS = ("stated", "removed")
MAX_TOKENS = 2000                       # the pilot's 700 cut replies off; the model spends about 500 tokens before the JSON
HOLD = NR.HOLD
EVEN_CARRY = N.START_HOLDINGS[1]        # what a leaver carries under an even split of the whole pot: half of 90 = 45
ALPHA = 0.05
SHARE_H0 = 0.20                         # P1: below-floor share in the removed arm is rejected as >= 0.20
RD_MARGIN = 0.20                        # P2: the upper bound of (removed minus stated) below-floor share must be under this
DIST_POINT = 0.15                       # P3a: mean distance of proposed exits from an even split, removed arm
DIST_DIFF = 0.10                        # P3b: removed minus stated mean distance (pairing level)


def carry(b):
    """What a leaver would carry out of the pot under bundle b at the week-0 holdings: the lowest over the exit path and, with a stay
    commitment, the breach path (own private money excluded)."""
    m, sh = N.START_HOLDINGS
    paths = ["exit"] + (["breach"] if b["stay"] else [])
    return min(N.retained(b, m, sh, p) - m for p in paths)


def distance(b):
    """Distance of the proposed exit terms from an even split, in [0, 1]: 0 = a leaver carries half the pot (45 of 90), 1 = nothing."""
    return 1.0 - min(1.0, carry(b) / EVEN_CARRY)


def proposals(row):
    """Every proposal of a negotiation: {k, bundle, below_floor, dist, exit}."""
    out = []
    for t in row["transcript"]:
        if t.get("action") == "propose" and t.get("bundle"):
            b = t["bundle"]
            out.append({"k": t["k"], "bundle": b, "below_floor": not N.floor_check(b, HOLD)["ok"], "dist": distance(b), "exit": b["exit"]})
    return out


def live_rows(model, seeds, max_usd, out, pairs=PAIRS, arms=ARMS, client=None, max_tokens=MAX_TOKENS):
    """-> (rows, ledger, aborted reason or None). A row per completed negotiation (arms interleaved so a stop leaves both arms), appended to log.jsonl."""
    ps, base = NR.HR._personas(), N.base_cards(NR.BIND)
    ledger = Ledger(model, max_usd)
    client = client or NL.ClaudeNegotiatorClient(model, ledger, max_usd, max_tokens=max_tokens)
    ledger = client.ledger
    rows, aborted = [], None
    out.mkdir(parents=True, exist_ok=True)
    for sd in seeds:
        for a, b in pairs:
            for arm in arms:
                try:
                    res = NL.week0_llm(ps[a], ps[b], NR.ARM, sd, base, {a: client, b: client}, floor_in_prompt=(arm == "stated"))
                except BudgetExceeded as e:
                    return rows, ledger, f"budget: {e}"
                except AgentError as e:
                    return rows, ledger, f"backend: {e}"
                row = {"arm": arm, "a": a, "b": b, "seed": sd, "status": res.status, "pot": res.pot, "bundle": res.bundle,
                       "transcript": res.transcript, "format_errors": res.format_errors, "refusals": res.refusals, "calls": res.calls,
                       "turns": len(res.transcript), "invalid": res.invalid, "floor_blocks": len(res.floor_blocks), "rejections": len(res.rejections),
                       "outside": res.outside, "baseline": res.baseline}
                row["proposals"] = proposals(row)
                rows.append(row)
                with (out / "log.jsonl").open("a", encoding="utf-8") as f:
                    f.write(json.dumps({"row": row, "spent_usd": round(ledger.total_usd(), 6)}, default=str) + "\n")
    return rows, ledger, aborted


def _m(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def summarize(rows, ledger_summary=None, out=print):
    """Every number the results page quotes. rows: negotiation rows of both arms. Returns the numbers as a dict."""
    def pr(*a):
        out(" ".join(str(x) for x in a))
    res = {}
    by = {arm: [r for r in rows if r["arm"] == arm] for arm in ARMS}
    for arm in ARMS:
        rs = by[arm]
        turns, calls = sum(r["turns"] for r in rs), sum(r["calls"] for r in rs)
        fe, rf = sum(r["format_errors"] for r in rs), sum(r["refusals"] for r in rs)
        res[arm] = {"n": len(rs), "turns": turns, "calls": calls, "format_errors": fe, "refusals": rf,
                    "fe_rate": fe / max(1, turns), "rf_rate": rf / max(1, calls),
                    "agreed": sum(r["pot"] for r in rs), "props": [p for r in rs for p in proposals(r)]}
        pr(f"== arm {arm}: {len(rs)} negotiations, {turns} turns, {calls} calls; format errors {fe}/{turns} = {fe / max(1, turns):.3f}; refusals {rf}/{calls}"
           f" = {rf / max(1, calls):.3f}; agreed {res[arm]['agreed']}/{len(rs)}")
    excluded = [a for a in ARMS if not (res[a]["fe_rate"] < 0.10 and res[a]["rf_rate"] < 0.10)]
    pr("== exclusion rule (format errors < 10% of turns and refusals < 10% of calls, each arm):", f"EXCLUDED arms {excluded}" if excluded else "both arms count")
    ks = {a: sum(p["below_floor"] for p in res[a]["props"]) for a in ARMS}
    ns = {a: len(res[a]["props"]) for a in ARMS}
    for a in ARMS:
        ci = S.clopper_pearson(ks[a], ns[a]) if ns[a] else None
        pr(f"== below-floor proposals, {a}: {ks[a]}/{ns[a]} = {ks[a] / max(1, ns[a]):.3f}; Clopper-Pearson 95% {ci}")
    # P1: removed arm, H0 share >= SHARE_H0, one-sided exact binomial
    p1 = S.sign_test(ks["removed"], ns["removed"], SHARE_H0, "less") if ns["removed"] else 1.0
    # P2: Fisher one-sided removed > stated; risk difference interval
    p2 = S.fisher_exact_p(ks["removed"], ns["removed"], ks["stated"], ns["stated"], "greater") if ns["removed"] and ns["stated"] else 1.0
    rd = S.risk_difference(ks["removed"], ns["removed"], ks["stated"], ns["stated"]) if ns["removed"] and ns["stated"] else None
    ph = S.holm([p1, p2])
    pr(f"== P1 removed-arm share vs H0 share >= {SHARE_H0}: exact one-sided p = {p1:.4g}, Holm {ph[0]:.4g}; holds (hypothesis) = {ph[0] < ALPHA}")
    pr(f"== P2 removed minus stated below-floor share: risk difference {rd} (Newcombe); Fisher one-sided (removed > stated) p = {p2:.4g}, Holm {ph[1]:.4g};"
       f" holds (hypothesis) = {ph[1] >= ALPHA and rd is not None and rd.hi < RD_MARGIN}")
    res.update({"p1": p1, "p2": p2, "holm": ph, "rd": rd, "ks": ks, "ns": ns, "excluded": excluded})
    # P3: distance from an even split
    dist = {a: [p["dist"] for p in res[a]["props"]] for a in ARMS}
    pairing_means = {a: {} for a in ARMS}
    for a in ARMS:
        for (x, y) in PAIRS:
            ds = [p["dist"] for r in by[a] if (r["a"], r["b"]) == (x, y) for p in proposals(r)]
            if ds:
                pairing_means[a][(x, y)] = _m(ds)
    common = [k for k in PAIRS if k in pairing_means["stated"] and k in pairing_means["removed"]]
    sr = [pairing_means["removed"][k] for k in common]
    ss = [pairing_means["stated"][k] for k in common]
    d_rm, d_st = _m(dist["removed"]), _m(dist["stated"])
    if len(common) >= 2:
        pt = S.permutation_test(sr, ss, paired=True, alternative="greater")
        dci = S.mean_difference(sr, ss, paired=True)
        pr(f"== P3 distance of proposed exit terms from an even split (0 even, 1 forfeit): removed {d_rm:.3f} (n={len(dist['removed'])}), stated {d_st:.3f} (n={len(dist['stated'])});"
           f" pairing-level (n={len(common)}) removed minus stated {dci} (paired bootstrap), permutation one-sided p = {pt.p:.4g};"
           f" P3a (removed <= {DIST_POINT}) = {d_rm <= DIST_POINT}; P3b (difference < {DIST_DIFF}) = {dci.estimate < DIST_DIFF}  [DESCRIPTIVE: 6 pairings]")
        res.update({"d_removed": d_rm, "d_stated": d_st, "dci": dci, "p3": pt.p})
    ex = {a: {e: sum(1 for p in res[a]["props"] if p["exit"] == e) for e in N.TERMS["exit"]} for a in ARMS}
    pr("== exit term of proposals:", ex)
    # opening proposals (turns 0 and 1: before any deal was blocked)
    op = {a: [p for p in res[a]["props"] if p["k"] <= 1] for a in ARMS}
    pr("== opening proposals (turn 0 or 1), below floor:", {a: f"{sum(p['below_floor'] for p in op[a])}/{len(op[a])}" for a in ARMS})
    # robustness: share of negotiations with any below-floor proposal; cluster bootstrap of the share by pairing
    for a in ARMS:
        anyb = sum(1 for r in by[a] if any(p["below_floor"] for p in proposals(r)))
        pr(f"== negotiations with at least one below-floor proposal, {a}: {anyb}/{len(by[a])}; floor blocks (accepted then blocked) {sum(r['floor_blocks'] for r in by[a])}")
        vals = [p["below_floor"] for r in by[a] for p in proposals(r)]
        cl = [r["a"] + "|" + r["b"] for r in by[a] for _ in proposals(r)]
        if vals and len(set(cl)) > 1:
            pr(f"   pairing-cluster bootstrap 95% CI of the below-floor share, {a}: {S.cluster_bootstrap_ci([float(v) for v in vals], cl)}")
    ag = {a: res[a]["agreed"] for a in ARMS}
    if res["stated"]["n"] and res["removed"]["n"]:
        pr(f"== P4 agreement (report only): stated {ag['stated']}/{res['stated']['n']}, removed {ag['removed']}/{res['removed']['n']}; risk difference "
           f"{S.risk_difference(ag['removed'], res['removed']['n'], ag['stated'], res['stated']['n'])}")
    hyp = (not excluded) and ph[0] < ALPHA and ph[1] >= ALPHA and rd is not None and rd.hi < RD_MARGIN
    alt = (not excluded) and ph[1] < ALPHA and ns["removed"] > 0 and ks["removed"] / ns["removed"] >= SHARE_H0
    pr(f"== VERDICT: fairness prior supported = {hyp}; understanding supported = {alt}" + ("" if hyp or alt else "  (neither: inconclusive)"))
    res.update({"hyp": hyp, "alt": alt})
    if ledger_summary:
        pr("== cost and usage:", ledger_summary)
    return res


def merge(out):
    """Combine the log.jsonl files under out (the run was split by seed into parallel processes: out/log.jsonl holds seed 0, out/seed<k>/ the rest)
    into out/results.json. Rows are de-duplicated by (arm, pairing, seed); the top-level log counts for seed 0 only. Cost = the sum of each
    log's last recorded spend (a stopped process's calls are paid for even if its rows are dropped)."""
    out = Path(out)
    rows, seen, usd = [], set(), 0.0
    for lp in [out / "log.jsonl"] + sorted(out.glob("seed*/log.jsonl")):
        last = 0.0
        for line in lp.read_text().splitlines():
            d = json.loads(line)
            last = d["spent_usd"]
            r = d["row"]
            if lp.parent == out and r["seed"] != 0:
                continue
            key = (r["arm"], r["a"], r["b"], r["seed"])
            if key not in seen:
                seen.add(key)
                rows.append(r)
        usd += last
    rows.sort(key=lambda r: (r["seed"], PAIRS.index((r["a"], r["b"])), r["arm"]))
    res = {"rows": rows, "ledger": {"usd_total": round(usd, 6), "note": "sum of each process's last logged spend"}, "model": "claude-haiku-5-5",
           "max_tokens": MAX_TOKENS, "seeds": sorted({r["seed"] for r in rows}), "aborted": None}
    (out / "results.json").write_text(json.dumps(res, default=str))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=None, help="claude model id, e.g. claude-haiku-5-5")
    ap.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    ap.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    ap.add_argument("--max-usd", type=float, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--merge", action="store_true", help="combine the per-seed logs under --out into results.json, then analyze")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    out = Path(a.out)
    if a.merge:
        d = merge(out)
        summarize(d["rows"], d["ledger"])
        return 0
    if a.analyze:
        d = json.loads((out / "results.json").read_text())
        summarize(d["rows"], d.get("ledger"))
        return 0
    if not a.model:
        ap.error("give --model (for example claude-haiku-5-5)")
    if a.model not in PRICES:
        ap.error(f"no known price for {a.model}; known: {', '.join(PRICES)}")
    ps, base = NR.HR._personas(), N.base_cards(NR.BIND)
    n_neg = len(PAIRS) * len(a.seeds) * len(ARMS)
    est = max((NL.estimate(a.model, n_neg, (ps[x], ps[y]), base, max_tokens=a.max_tokens, assumed_out_tokens=500) for x, y in PAIRS), key=lambda e: e["usd_max"])
    print(f"model {a.model} ${PRICES[a.model][0]:g}/${PRICES[a.model][1]:g} per 1M in/out; {len(PAIRS)} pairings x {len(a.seeds)} seeds x {len(ARMS)} arms = {n_neg} negotiations, "
          f"at most {NL.DEADLINE_TURNS} turns each, max_tokens {a.max_tokens}")
    print(f"estimate: about {est['calls']} calls (typical 8 turns per negotiation, 500 tokens out), longest prompt about {est['tokens_in_per_call_max']} tokens in -> about "
          f"${est['usd']:.4f}; worst case {est['calls_max']} calls (every turn retried, {a.max_tokens} tokens out each) -> ${est['usd_max']:.4f}")
    if a.dry_run:
        return 0
    if a.max_usd is None or a.max_usd <= 0:
        print("refusing to run live without --max-usd", file=sys.stderr)
        return 2
    t0 = time.time()
    rows, ledger, aborted = live_rows(a.model, tuple(a.seeds), a.max_usd, out, max_tokens=a.max_tokens)
    if aborted and not rows and ledger.total_usd() == 0 and aborted.startswith("backend"):
        print(f"STOPPED: the claude backend failed before any call completed ({aborted}).", file=sys.stderr)
        return 3
    summary = ledger.summary()
    (out / "results.json").write_text(json.dumps({"rows": rows, "ledger": summary, "aborted": aborted, "model": a.model, "max_usd": a.max_usd,
                                                  "max_tokens": a.max_tokens, "seeds": list(a.seeds), "seconds": round(time.time() - t0, 1)}, default=str))
    if aborted:
        print(f"ABORTED after {len(rows)} of {n_neg} negotiations: {aborted}", file=sys.stderr)
    summarize(rows, summary)
    return 0 if not aborted else 4


if __name__ == "__main__":
    sys.exit(main())
