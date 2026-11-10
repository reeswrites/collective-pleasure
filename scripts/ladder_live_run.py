"""Place real models on the seam ladder. Refuses to run live without --max-usd; --dry-run prints the cost estimate only.

  uv run python scripts/ladder_live_run.py --dry-run --model jev:typesafe/jev-1.14 --model claude:claude-haiku-5-5
  uv run python scripts/ladder_live_run.py --max-usd 5 --model claude:claude-haiku-5-5 --model 'llm:<id>@0.05,0.2'
  uv run python scripts/ladder_live_run.py --arm propensity --dry-run --model claude:claude-haiku-5-5
  uv run python scripts/ladder_live_run.py --report-only
  uv run python scripts/ladder_live_run.py --gate-only            # lint + mock panel, no spend
  uv run python scripts/ladder_live_run.py --max-usd 1 --smoke 5 --model claude:claude-opus-5-5   # 5-decision smoke test

  uv run python scripts/ladder_live_run.py --arm win --dry-run --model claude:claude-haiku-5-5   # try-to-win arm (v2 harness)

Harness v2 (capability and win arms): one model plays the adversary against a scripted cooperative victim; L4 is one model choosing both
partners as a coordinated pair. A live run first runs the rule-set lint and a mock panel on the real harness and REFUSES to
spend unless both pass (the table is printed and saved to <out>/calibration.txt). Every decision is logged to <out>/decisions.jsonl.

Model ids are always explicit (kind:model_id). Writes runs/ladder_live/{log.jsonl,report.html}. Keys come from the
environment or .env (never pasted anywhere). Live runs call real APIs.
"""
import argparse
import sys
from pathlib import Path

from mar import ladder_live as LL
from mar import seam_depth as S


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", action="append", default=[], help="kind:model_id[@price_in,price_out]; repeatable")
    ap.add_argument("--seeds", type=int, nargs="+", default=list(LL.SEEDS_DEFAULT))
    ap.add_argument("--attempts", type=int, default=1)
    ap.add_argument("--rules", nargs="+", default=list(S.LADDER), choices=list(LL.LADDER_ALL), help="L5b_gift_pool is the repaired L5")
    ap.add_argument("--adversary", choices=list(LL.ROLES), default=LL.ADVERSARY_ROLE, help="which partner the model plays (capability arm)")
    ap.add_argument("--smoke", type=int, default=None, help="stop after this many model decisions (first rule set, first seed); a smoke test")
    ap.add_argument("--refusal-stop", type=float, default=None, help="abort a model once more than this share of its calls are refusals (after 5 calls)")
    ap.add_argument("--gate-only", action="store_true", help="run the lint and the mock panel, print and save the table, spend nothing")
    ap.add_argument("--arm", choices=list(LL.ARMS), default="capability",
                    help="capability: models told to probe the rules for loopholes (default); propensity: models just "
                         "live as a fixed persona, no red-team instruction; win: harness v2, the model plays the persona "
                         "with an explicit objective to maximize its own outcome (L4: the pair's joint outcome), no loophole "
                         "framing")
    ap.add_argument("--max-usd", type=float, default=None, help="required for live runs: hard spending cap")
    ap.add_argument("--allow-cap-below-worst", action="store_true",
                    help="accept a --max-usd below the worst-case estimate (every call retried once); the ledger still stops the "
                         "run at the cap, the model in progress is cut off and later models are skipped")
    ap.add_argument("--dry-run", action="store_true", help="print the cost estimate per model and stop")
    ap.add_argument("--report-only", action="store_true", help="rebuild report.html from the log")
    ap.add_argument("--out", default=str(LL.OUT_DIR))
    a = ap.parse_args(argv)
    out = Path(a.out)
    if a.report_only:
        print(LL.write_report(LL.load_models_from_log(out / "log.jsonl"), out))
        return 0
    if not a.model and not a.gate_only:
        ap.error("give at least one --model kind:model_id")
    try:
        specs = [LL.parse_model_spec(m) for m in a.model]
    except ValueError as e:
        ap.error(str(e))
    rules, seeds = tuple(a.rules), tuple(a.seeds)
    if a.smoke:
        rules, seeds = rules[:1], seeds[:1]
    kw = dict(rules=rules, seeds=seeds, attempts=a.attempts, arm=a.arm)
    if specs:
        print(LL.estimate_table(specs, **kw))
    if a.arm in LL.V2_ARMS or a.gate_only:
        ok, report = LL.prespend_gate(rules if not a.gate_only else tuple(a.rules), seeds, out, arm=a.arm)
        print(report)
        if a.gate_only:
            return 0 if ok else 2
        if not ok and not a.dry_run:
            print("refusing to spend: the pre-spend gate failed (see above)", file=sys.stderr)
            return 2
    if a.dry_run:
        return 0
    if a.max_usd is None or a.max_usd <= 0:
        print("refusing to run live without --max-usd (a positive hard cap in USD); use --dry-run to see estimates",
              file=sys.stderr)
        return 2
    worst = sum(LL.estimate(s, **kw)["usd_max"] for s in specs)
    if worst > a.max_usd and not a.allow_cap_below_worst:
        print(f"refusing: worst-case estimate ${worst:.4f} exceeds --max-usd ${a.max_usd:.4f}; raise the cap or drop models",
              file=sys.stderr)
        return 2
    results = LL.run_all(specs, lambda s, ledger: LL.real_backend(s, ledger, out / "jev-cache", a.arm), a.max_usd, out_dir=out,
                          adversary=a.adversary, smoke_decisions=a.smoke, refusal_stop=a.refusal_stop, **kw)
    note = f"Arm {a.arm}; cap ${a.max_usd:.2f}; seeds {list(seeds)}; {a.attempts} attempt(s) per rule set and seed."
    print(LL.write_report(LL.load_models_from_log(out / "log.jsonl") or results, out, note))
    for r in results:
        s = r.get("score")
        print(f"{r['model']}: " + ("skipped" if s is None else
              f"deepest {(s['deepest'] or {}).get('id', 'none')}, inventive {len(s['inventive'])}, "
              f"format errors {r['format_error_rate']:.1%}, refusals {r['refusal_rate']:.1%}, ${r['cost_usd']:.4f}, {r['wall_s']}s"
              + (f"; ABORTED: {r['aborted']}" if r["aborted"] else "")))
        if s is not None and r.get("harness") == "v2":
            ia = r["identical_attempts"]
            print(f"   refusal categories {r['refusal_categories'] or 'none'}; attempts with identical decisions: "
                  f"{ia['pairs_identical']} of {ia['attempt_pairs']} attempt pairs ({ia['groups_all_identical']} of {ia['groups']} groups); "
                  f"rule sets where every seed gave identical decisions: {r['identical_across_seeds']['rules_all_identical']} of {r['identical_across_seeds']['rules']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
