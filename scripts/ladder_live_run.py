"""Place real models on the seam ladder. Refuses to run live without --max-usd; --dry-run prints the cost estimate only.

  uv run python scripts/ladder_live_run.py --dry-run --model jev:typesafe/jev-1.14 --model claude:claude-haiku-5-5
  uv run python scripts/ladder_live_run.py --max-usd 5 --model claude:claude-haiku-5-5 --model 'llm:<id>@0.05,0.2'
  uv run python scripts/ladder_live_run.py --report-only

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
    ap.add_argument("--rules", nargs="+", default=list(S.LADDER), choices=list(S.LADDER))
    ap.add_argument("--max-usd", type=float, default=None, help="required for live runs: hard spending cap")
    ap.add_argument("--dry-run", action="store_true", help="print the cost estimate per model and stop")
    ap.add_argument("--report-only", action="store_true", help="rebuild report.html from the log")
    ap.add_argument("--out", default=str(LL.OUT_DIR))
    a = ap.parse_args(argv)
    out = Path(a.out)
    if a.report_only:
        print(LL.write_report(LL.load_models_from_log(out / "log.jsonl"), out))
        return 0
    if not a.model:
        ap.error("give at least one --model kind:model_id")
    try:
        specs = [LL.parse_model_spec(m) for m in a.model]
    except ValueError as e:
        ap.error(str(e))
    kw = dict(rules=tuple(a.rules), seeds=tuple(a.seeds), attempts=a.attempts)
    table = LL.estimate_table(specs, **kw)
    print(table)
    if a.dry_run:
        return 0
    if a.max_usd is None or a.max_usd <= 0:
        print("refusing to run live without --max-usd (a positive hard cap in USD); use --dry-run to see estimates",
              file=sys.stderr)
        return 2
    worst = sum(LL.estimate(s, **kw)["usd_max"] for s in specs)
    if worst > a.max_usd:
        print(f"refusing: worst-case estimate ${worst:.4f} exceeds --max-usd ${a.max_usd:.4f}; raise the cap or drop models",
              file=sys.stderr)
        return 2
    results = LL.run_all(specs, lambda s, ledger: LL.real_backend(s, ledger, out / "jev-cache"), a.max_usd, out_dir=out, **kw)
    note = f"Cap ${a.max_usd:.2f}; seeds {a.seeds}; {a.attempts} attempt(s) per rule set and seed."
    print(LL.write_report(LL.load_models_from_log(out / "log.jsonl") or results, out, note))
    for r in results:
        s = r.get("score")
        print(f"{r['model']}: " + ("skipped" if s is None else
              f"deepest {(s['deepest'] or {}).get('id', 'none')}, inventive {len(s['inventive'])}, "
              f"format errors {r['format_error_rate']:.1%}, refusals {r['refusal_rate']:.1%}, ${r['cost_usd']:.4f}, {r['wall_s']}s"
              + (f"; ABORTED: {r['aborted']}" if r["aborted"] else "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
