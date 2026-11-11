"""IT1 profit cells, plan and play arms (docs/results/ladder-it1-prereg-DRAFT.md). Spends money only when every guard passes.

  uv run python scripts/it1_run.py --dry-run                                  # cost table from the gate's mocked prompts; no calls
  uv run python scripts/it1_run.py --arm plan --model claude:claude-haiku-5-5 --max-usd 1 --prereg-approved   # live (NOT approved yet)

Guards before any call: the prereg file no longer says NOT APPROVED and --prereg-approved is given; the free gate
(scripts/it1_gate.py) passed and its frozen thresholds exist; the lint, the word test and a seed-0 mock panel through the real harness
pass again now; --max-usd is set and not below the worst-case estimate. Writes runs/it1/{log.jsonl,decisions.jsonl}.
"""
import argparse
import json
import sys
from pathlib import Path

from mar import it1
from mar import ladder_live as LL
from mar import lint as LI

PREREG = it1.REPO / "docs" / "results" / "ladder-it1-prereg-DRAFT.md"
OUT = it1.REPO / "runs" / "it1"


def guards(prereg_flag):
    """-> list of reasons to refuse (empty = all guards pass)."""
    why = []
    if not prereg_flag:
        why.append("--prereg-approved not given")
    if PREREG.exists() and "NOT APPROVED" in PREREG.read_text():
        why.append(f"{PREREG.name} is still marked NOT APPROVED")
    gate = it1.GATE_DIR / "gate.json"
    if not gate.exists() or not json.loads(gate.read_text()).get("ok"):
        why.append("the free gate has not passed (run scripts/it1_gate.py)")
    if not (it1.THRESHOLDS.exists() and (it1.GATE_DIR / "profit.json").exists()):
        why.append("frozen thresholds or profit sequences missing")
    return why


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--arm", choices=("plan", "play"), default="plan")
    ap.add_argument("--model", action="append", default=[])
    ap.add_argument("--seeds", nargs="+", type=int, default=list(it1.SEEDS))
    ap.add_argument("--cells", nargs="+", default=list(it1.CELLS), choices=list(it1.CELLS))
    ap.add_argument("--observe-months", type=int, default=0, choices=(0, 1))
    ap.add_argument("--paid-rule", choices=it1.PAID_RULES, default="victim_in")
    ap.add_argument("--smoke", type=int, default=None, help="stop after this many calls")
    ap.add_argument("--refusal-stop", type=float, default=0.25)
    ap.add_argument("--max-usd", type=float, default=None)
    ap.add_argument("--prereg-approved", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    gate = it1.GATE_DIR / "gate.json"
    if a.dry_run:
        if gate.exists():
            print(it1.cost_text(json.loads(gate.read_text())["cost"]))
        else:
            print("no gate.json yet: run scripts/it1_gate.py first (the cost table comes from its mocked prompts)")
        return 0
    if not a.model:
        ap.error("give at least one --model kind:model_id")
    why = guards(a.prereg_approved)
    if a.max_usd is None or a.max_usd <= 0:
        why.append("--max-usd (a positive hard cap) not given")
    if why:
        print("refusing to spend: " + "; ".join(why), file=sys.stderr)
        return 2
    cost = json.loads(gate.read_text())["cost"]
    specs = [LL.parse_model_spec(m) for m in a.model]
    worst = sum(r["usd_max"] or 0 for r in cost["rows"] if r["model"] in {s.label for s in specs})
    if worst > a.max_usd:
        print(f"refusing: worst-case estimate ${worst:.2f} for these models exceeds --max-usd ${a.max_usd:.2f}", file=sys.stderr)
        return 2
    ok, lines = LI.gate_ok(sorted({it1.CELLS[c][0] for c in a.cells}))
    words = it1.word_test(a.observe_months)
    thresholds = json.loads(it1.THRESHOLDS.read_text() if not a.observe_months else (it1.GATE_DIR / "thresholds_observe.json").read_text())
    profit = json.loads((it1.GATE_DIR / "profit.json").read_text())
    mg = it1.mock_gate(json.loads(it1.THRESHOLDS.read_text()), profit, seeds=(0,))
    if not (ok and not words and mg["ok"]):
        print(f"refusing to spend: pre-spend recheck failed (lint {ok}, words {words}, mock panel {mg['problems'][:3]})", file=sys.stderr)
        return 2
    OUT.mkdir(parents=True, exist_ok=True)
    spent = 0.0
    for spec in specs:
        left = a.max_usd - spent
        factory = lambda s, ledger: LL.real_backend(s, ledger, OUT / "jev-cache", "win")
        kw = dict(cells=tuple(a.cells), seeds=tuple(a.seeds), thresholds=thresholds, observe_months=a.observe_months,
                  paid_rule=a.paid_rule, max_usd=left, log_path=OUT / "log.jsonl")
        if a.arm == "plan":
            if spec.kind == "jev":
                print(f"{spec.label}: skipped (plan arm needs free text)")
                continue
            res = it1.run_plan(spec, factory, smoke_calls=a.smoke, refusal_stop=a.refusal_stop, **kw)
            spent += res["cost_usd"]
            print(f"{spec.label}: plan arm {len(res['runs'])} runs, candidates {res['candidates']}, refusals {res['refusal_rate']:.0%}, "
                  f"${res['cost_usd']:.4f}" + (f"; ABORTED: {res['aborted']}" if res["aborted"] else ""))
        else:
            res = it1.run_play(spec, factory, smoke_decisions=a.smoke, refusal_stop=a.refusal_stop, **kw)
            spent += sum(r.get("cost_usd", 0) for r in res)
            rows = [x for r in res for x in r.get("runs", [])]
            print(f"{spec.label}: play arm {len(rows)} runs, candidates {sum(bool(x.get('it1_candidate')) for x in rows)}, "
                  f"paid seams {sum(bool(x.get('paid_seam')) for x in rows)}, ${sum(r.get('cost_usd', 0) for r in res):.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
