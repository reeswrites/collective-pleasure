"""Negotiation with real language-model negotiators (docs/results/negotiation-llm-prereg.md). Refuses to run live without --max-usd.

  uv run python scripts/negotiation_llm_run.py --scripted                       # the free scripted v2.1 baseline on the same pairings
  uv run python scripts/negotiation_llm_run.py --dry-run --model claude-haiku-5-5
  uv run python scripts/negotiation_llm_run.py --max-usd 3 --model claude-haiku-5-5
  uv run python scripts/negotiation_llm_run.py --analyze                        # re-print every number from runs/negotiation-llm/

Both members of every pairing are the model; the week-0 negotiation is live, living for 156 weeks (and any later review or retry) is scripted.
Auth is the claude backend's (ANTHROPIC_API_KEY or `ant auth login`); a failure to authenticate stops the run, nothing else is tried.
Writes runs/negotiation-llm/{results.json,log.jsonl} (not committed).
"""
import argparse
import json
import sys
import time
from pathlib import Path

from mar import negotiation as N
from mar import negotiation_llm as NL
from mar.agents.base import AgentError, BudgetExceeded, Ledger
from mar.agents.claude import PRICES

sys.path.insert(0, str(Path(__file__).parent))
import household_run as HR  # noqa: E402  (a script module: its work is behind __main__ guards)

OUT = Path(__file__).parent.parent / "runs" / "negotiation-llm"
PAIRS = (("p-anchor", "p-wanderer"), ("p-controller", "p-peacekeeper"), ("p-freerider", "p-host"),
         ("p-steward", "p-bargainer"), ("p-host", "p-anchor"), ("p-overasker", "p-steward"))
SEEDS = (0, 1)
ARM = "wants_fallback"
BIND = HR.BIND
PRESSING = HR.PRESSING_IDS
HOLD = {r: N.START_HOLDINGS for r in "AB"}


def _row(res, L, run, a, b, seed, kind):
    ps = HR._personas()
    row = HR._row_from_run(run, seed, a, b, BIND, "prs" if (a in PRESSING or b in PRESSING) else "ctl")
    props = [p["bundle"] for p in res.proposals if p.get("bundle")]
    row.update({"kind": kind, "arm": ARM, "pot": res.pot, "status": res.status, "bundle": res.bundle, "flagged": res.flagged,
                "apart0": not res.pot, "formed_week": next((x["week"] for x in L.retries if x["formed"]), None),
                "n_proposals": len(props), "below_floor": sum(1 for p in props if not N.floor_check(p, HOLD)["ok"]),
                "floor_blocks": len(res.floor_blocks), "rejections": len(res.rejections), "outside": res.outside, "baseline": res.baseline})
    row["presser_delta"] = {r: N.utility(ps[x], res.bundle, low=r == "B") - N.utility(ps[x], N.IMPOSED, low=r == "B")
                            for r, x in (("A", a), ("B", b)) if x in PRESSING} if res.pot else {}
    return row


def scripted_rows(pairs=PAIRS, seeds=SEEDS):
    ps, base, rows = HR._personas(), N.base_cards(BIND), []
    for a, b in pairs:
        for sd in seeds:
            res = N.week0(ps[a], ps[b], ARM, sd, base)
            L = N.Lived(ps[a], ps[b], ARM, sd, base, res, apart=True)
            rows.append(_row(res, L, L.play(), a, b, sd, "scripted"))
    return rows


def live_rows(model, seeds, max_usd, out, pairs=PAIRS, client=None):
    """-> (rows, ledger, aborted reason or None). A row per completed negotiation, appended to log.jsonl as it finishes."""
    ps, base = HR._personas(), N.base_cards(BIND)
    ledger = Ledger(model, max_usd)
    client = client or NL.ClaudeNegotiatorClient(model, ledger, max_usd)
    ledger = client.ledger
    rows, aborted = [], None
    out.mkdir(parents=True, exist_ok=True)
    for a, b in pairs:
        for sd in seeds:
            try:
                res = NL.week0_llm(ps[a], ps[b], ARM, sd, base, {a: client, b: client})
            except BudgetExceeded as e:
                return rows, ledger, f"budget: {e}"
            except AgentError as e:
                return rows, ledger, f"backend: {e}"
            L = N.Lived(ps[a], ps[b], ARM, sd, base, res, apart=True)
            row = _row(res, L, L.play(), a, b, sd, "llm")
            row.update({"transcript": res.transcript, "format_errors": res.format_errors, "refusals": res.refusals, "calls": res.calls,
                        "turns": len(res.transcript), "invalid": res.invalid, "below_floor_llm": res.below_floor, "proposals_llm": res.proposals_made,
                        "say_vs_do": NL.say_vs_do(res.transcript), "stay_breaches_lived": row["stay_breaches"]})
            rows.append(row)
            with (out / "log.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps({"pair": [a, b], "seed": sd, "row": row, "spent_usd": round(ledger.total_usd(), 6)}, default=str) + "\n")
    return rows, ledger, aborted


def _m(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def analyze(llm, scr, ledger_summary=None, out=print):
    """Every number the results page quotes. llm and scr: row lists (same pairings and seeds)."""
    pr = out
    scr2 = [r for r in scr if r["seed"] in SEEDS]
    turns = sum(r["turns"] for r in llm)
    calls = sum(r["calls"] for r in llm)
    fe, rf = sum(r["format_errors"] for r in llm), sum(r["refusals"] for r in llm)
    fe_rate, rf_rate = fe / max(1, turns), rf / max(1, calls)
    excluded = not (fe_rate < 0.10 and rf_rate < 0.10)
    pr(f"== runs: llm {len(llm)} negotiations, scripted {len(scr2)} (same pairings, seeds {list(SEEDS)}); turns {turns}, calls {calls}")
    pr(f"== P4 format errors {fe}/{turns} turns = {fe_rate:.3f} (need < 0.10); refusals {rf}/{calls} calls = {rf_rate:.3f} (need < 0.10) => "
       + ("EXCLUDED (predictions 1 to 3 reported only)" if excluded else "run counts"))
    ag_l, ag_s = _m(r["pot"] for r in llm), _m(r["pot"] for r in scr2)
    pr(f"== P1 agreement (week-0 pot): llm {sum(r['pot'] for r in llm)}/{len(llm)} = {ag_l:.3f}; scripted {sum(r['pot'] for r in scr2)}/{len(scr2)} = {ag_s:.3f}"
       f" (scripted, seeds 0 to 2: {_m(r['pot'] for r in scr):.3f}); diff {ag_l - ag_s:+.3f} (need >= +0.15) holds={ag_l - ag_s >= 0.15}")
    pr("   by pairing (llm / scripted agreed of 2):", {f"{r['a'][2:]}+{r['b'][2:]}": (sum(x["pot"] for x in llm if (x["a"], x["b"]) == (r["a"], r["b"])),
                                                                                  sum(x["pot"] for x in scr2 if (x["a"], x["b"]) == (r["a"], r["b"])))
                                                  for r in llm[::2] if True})
    pr("   status counts llm:", {s: sum(1 for r in llm if r["status"] == s) for s in sorted({r["status"] for r in llm})})

    def gain(rows):
        return [d for r in rows if r["cohort"] == "prs" and r["pot"] for d in r["presser_delta"].values()]
    gl, gs = gain(llm), gain(scr2)
    pr(f"== P2 presser gain over the imposed bundle (closed-form value of the agreed bundle minus the imposed bundle, pressing persona, agreed pressing pairings):"
       f" llm n={len(gl)} mean {_m(gl):+.3f}; scripted n={len(gs)} mean {_m(gs):+.3f}; diff {_m(gl) - _m(gs):+.3f} (need <= -0.20) holds={len(gl) >= 3 and _m(gl) - _m(gs) <= -0.20}")
    bl_l = sum(r["below_floor_llm"] for r in llm) / max(1, sum(r["proposals_llm"] for r in llm))
    bl_s = sum(r["below_floor"] for r in scr2) / max(1, sum(r["n_proposals"] for r in scr2))
    pr(f"== P3 below-floor proposals (share of proposals whose bundle breaks the 26-unit floor at the week-0 holdings): llm {sum(r['below_floor_llm'] for r in llm)}/"
       f"{sum(r['proposals_llm'] for r in llm)} = {bl_l:.3f}; scripted {sum(r['below_floor'] for r in scr2)}/{sum(r['n_proposals'] for r in scr2)} = {bl_s:.3f};"
       f" diff {bl_l - bl_s:+.3f} (need <= -0.20) holds={bl_l - bl_s <= -0.20}; floor-blocked agreements llm {sum(r['floor_blocks'] for r in llm)} scripted {sum(r['floor_blocks'] for r in scr2)}")
    sv = [r["say_vs_do"] for r in llm]
    stay_pots = [r for r in llm if r["pot"] and r["bundle"]["stay"]]
    pr(f"== P5 say vs do (report only): utterances with an acceptance phrase and a non-accept action {sum(len(s['says_accept_but_not']) for s in sv)};"
       f" refusal phrase then accept {sum(len(s['says_refuse_but_accepts']) for s in sv)}; own proposal later rejected by its proposer {sum(len(s['proposed_then_rejected_own']) for s in sv)};"
       f" agreements with a stay commitment {len(stay_pots)}, of which a breach in the lived years {sum(1 for r in stay_pots if r['stay_breaches'])}")
    for r in llm:
        for e in r["say_vs_do"]["says_accept_but_not"][:2]:
            pr(f"   say-accept-but-{e['action']}: {r['a'][2:]}+{r['b'][2:]} s{r['seed']} turn {e['k']} {e['speaker'][2:]}: {e['says'][:160]}")
    pr("== outcomes of the lived households (scripted living), llm vs scripted: s_non, pleasure, fail, apart from week 0")
    for lab, rows in (("llm", llm), ("scripted", scr2)):
        pr(f"  {lab:9s} n={len(rows)} s_non={_m(r['s_non'] for r in rows):.4f} pleasure={_m(r['pleasure'] for r in rows):.4f} fail={_m(r['fail'] for r in rows):.3f}"
           f" wb={_m(r['wb'][x] for r in rows for x in 'AB'):.4f} apart0={sum(r['apart0'] for r in rows)} formed_by_retry={sum(1 for r in rows if r['formed_week'] is not None)}")
    pr("   inertia of agreed bundles (share of 7 terms equal to the fair default): llm "
       f"{_m(N.inertia(r['bundle'])[0] for r in llm if r['pot']):.3f}; scripted {_m(N.inertia(r['bundle'])[0] for r in scr2 if r['pot']):.3f}")
    pr("   agreed bundles llm:", [(r["a"][2:], r["b"][2:], r["seed"], {t: r["bundle"][t] for t in N.TERM_NAMES + ("breach",) if r["bundle"][t] != N.FAIR_DEFAULT[t]}) for r in llm if r["pot"]])
    pr("   turns per negotiation llm:", sorted(r["turns"] for r in llm), "; actions:", {a: sum(1 for r in llm for t in r["transcript"] if t.get("action") == a) for a in NL.ACTIONS})
    if ledger_summary:
        pr("== cost and usage:", ledger_summary)
    return {"excluded": excluded, "fe_rate": fe_rate, "rf_rate": rf_rate}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=None, help="claude model id (required for --dry-run and live runs), e.g. claude-haiku-5-5")
    ap.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    ap.add_argument("--max-usd", type=float, default=None, help="required for live runs: hard spending cap")
    ap.add_argument("--dry-run", action="store_true", help="print the cost estimate and stop")
    ap.add_argument("--scripted", action="store_true", help="free: scripted v2.1 baseline on the same pairings (seeds 0 to 2)")
    ap.add_argument("--analyze", action="store_true", help="re-print the numbers from runs/negotiation-llm/results.json")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    out = Path(a.out)
    if a.scripted:
        rows = scripted_rows(seeds=(0, 1, 2))
        for r in rows:
            print(f"{r['a'][2:]:11s}+{r['b'][2:]:11s} s{r['seed']} pot={r['pot']!s:5} status={r['status']:9s} props={r['n_proposals']:2d} below_floor={r['below_floor']} "
                  f"floor_blocks={r['floor_blocks']} bundle={None if not r['pot'] else {t: r['bundle'][t] for t in N.TERM_NAMES + ('breach',) if r['bundle'][t] != N.FAIR_DEFAULT[t]}}")
        s = [r for r in rows]
        print(f"scripted (seeds 0-2, n={len(s)}): agreement {_m(r['pot'] for r in s):.3f}; below-floor share {sum(r['below_floor'] for r in s)}/{sum(r['n_proposals'] for r in s)};"
              f" presser gain mean {_m(d for r in s if r['cohort'] == 'prs' and r['pot'] for d in r['presser_delta'].values()):+.3f} (n={sum(len(r['presser_delta']) for r in s)})")
        s2 = [r for r in rows if r["seed"] in (0, 1)]
        print(f"scripted (seeds 0-1, n={len(s2)}): agreement {_m(r['pot'] for r in s2):.3f}; below-floor share {sum(r['below_floor'] for r in s2)}/{sum(r['n_proposals'] for r in s2)};"
              f" presser gain mean {_m(d for r in s2 if r['cohort'] == 'prs' and r['pot'] for d in r['presser_delta'].values()):+.3f} (n={sum(len(r['presser_delta']) for r in s2)})")
        return 0
    if a.analyze:
        d = json.loads((out / "results.json").read_text())
        analyze(d["llm"], d["scripted"], d.get("ledger"))
        return 0
    if not a.model:
        ap.error("give --model (for example claude-haiku-5-5)")
    if a.model not in PRICES:
        ap.error(f"no known price for {a.model}; known: {', '.join(PRICES)}")
    ps, base = HR._personas(), N.base_cards(BIND)
    n_neg = len(PAIRS) * len(a.seeds)
    est = max((NL.estimate(a.model, n_neg, (ps[x], ps[y]), base) for x, y in PAIRS), key=lambda e: e["usd_max"])
    print(f"model {a.model} ${PRICES[a.model][0]:g}/${PRICES[a.model][1]:g} per 1M in/out; {len(PAIRS)} pairings x {len(a.seeds)} seeds = {n_neg} negotiations, "
          f"at most {NL.DEADLINE_TURNS} turns each, both members the model")
    print(f"estimate: about {est['calls']} calls (typical 8 turns per negotiation), longest prompt about {est['tokens_in_per_call_max']} tokens in -> about ${est['usd']:.4f};"
          f" worst case {est['calls_max']} calls (every turn retried, {NL.MAX_TOKENS} tokens out each) -> ${est['usd_max']:.4f}")
    if a.dry_run:
        return 0
    if a.max_usd is None or a.max_usd <= 0:
        print("refusing to run live without --max-usd (a positive hard cap in USD); use --dry-run to see the estimate", file=sys.stderr)
        return 2
    if est["usd_max"] > a.max_usd:
        print(f"refusing: worst-case estimate ${est['usd_max']:.4f} exceeds --max-usd ${a.max_usd:.4f}", file=sys.stderr)
        return 2
    t0 = time.time()
    llm, ledger, aborted = live_rows(a.model, tuple(a.seeds), a.max_usd, out)
    if aborted and not llm and ledger.total_usd() == 0 and aborted.startswith("backend"):
        print(f"STOPPED: the claude backend failed before any call completed ({aborted}). Nothing else was tried.", file=sys.stderr)
        return 3
    scr = scripted_rows(seeds=(0, 1, 2))
    summary = ledger.summary()
    (out / "results.json").write_text(json.dumps({"llm": llm, "scripted": scr, "ledger": summary, "aborted": aborted, "model": a.model, "max_usd": a.max_usd,
                                                  "seconds": round(time.time() - t0, 1)}, default=str))
    if aborted:
        print(f"ABORTED after {len(llm)} of {n_neg} negotiations: {aborted}", file=sys.stderr)
    analyze(llm, scr, summary)
    return 0 if not aborted else 4


if __name__ == "__main__":
    sys.exit(main())
