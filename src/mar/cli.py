"""`mar`: a thin command line over the library. Each command prints plain English.

  mar run --spec rules/fishery --agents exploiter,compliant --months 6 --seed 0
  mar rules show --spec rules/fishery
  mar check --spec rules/fishery [--k 3]
  mar loop --spec rules/fishery --rounds 2
  mar report <run_id>

Reports and traces go to runs/<run_id>/ (override with --runs-dir). No LLM, no network.
"""
import argparse
import sys
from pathlib import Path

from . import oracle
from .cards import load_cards
from .patch_check import K_DEFAULT, check_patch, check_spec
from .patcher import propose_patch
from .report import (RunRecord, build_report, cond_text, execute, load_record, parse_agents, agents_slug,
                     run_story, sanction_text, verdict)

CHECK_NAMES = {"a_no_conflict": "No two rules contradict each other",
               "b_no_deadlock": "In every state some action is allowed",
               "c_bounded_sanctions": "Every sanction is finite",
               "d_repair_path": "A sanctioned agent can still act, and the sanction ends"}


def card_lines(c) -> str:
    verb = {"must": "must", "must_not": "must not", "may": "may"}[c.deontic]
    d = {"conditions": c.conditions}
    cond = cond_text(d)
    return (f"{c.id}  {c.attribute} {verb} {c.aim} when {cond}\n"
            f"    {c.gloss}\n    or else: {sanction_text(c.or_else)}\n    source: {c.source}")


def _explain_verdict(v, cards):
    try:
        from .english import explain
        return explain(v, cards)
    except Exception:  # ImportError or any story failure: fall back to the raw detail
        return f"{v['verdict']}. {v['detail']}"


def check_lines(cards, k):
    lines, ok = [], True
    for v in check_spec(cards, k):
        ok &= v["verdict"] == "pass"
        lines.append(f"[{v['verdict'].upper():4}] {CHECK_NAMES[v['check']]}: "
                     + (v["detail"] if v["verdict"] == "pass" else _explain_verdict(v, cards)))
    return ok, lines


def cmd_run(a) -> int:
    rec = execute(a.spec, parse_agents(a.agents), a.months, a.seed)
    path = build_report(rec, a.runs_dir)
    print(f"report: {path}")
    print(verdict(rec)[1])
    return 0


def cmd_rules_show(a) -> int:
    cards = load_cards(a.spec)
    print(f"{len(cards)} rules in {a.spec}\n")
    print("\n\n".join(card_lines(c) for c in cards))
    return 0


def cmd_check(a) -> int:
    cards = load_cards(a.spec)
    ok, lines = check_lines(cards, a.k)
    print("\n".join(lines))
    print(f"\nBounded verdicts: k={a.k} sanction months; pool 0..100, catch 0..100. "
          f"'open' means not shown within the bound, never 'safe'.")
    print("All four checks pass." if ok else "Not all checks pass.")
    return 0 if ok else 1


def cmd_loop(a) -> int:
    agents = parse_agents(a.agents)
    base = load_cards(a.spec)
    patch, history, checks = [], [], []
    rec = None
    for r in range(a.rounds + 1):
        rec = execute(a.spec, agents, a.months, a.seed, patch_cards=patch)
        seam = oracle.is_seam(rec.trace, rec.outcomes)
        entry = {"round": r, "seams": int(seam), "patch_ids": [c.id for c in patch],
                 "story": run_story(rec) if seam else "", "note": ""}
        if r < a.rounds:
            new = propose_patch(rec.trace, base + patch) if seam else []
            if not seam:
                entry["note"] = "No seam, so nothing to patch."
            elif not new:
                entry["note"] = "Seam found, but the scripted patcher has nothing more to propose."
            else:
                rep = check_patch(base + patch, new, a.k)
                checks = rep["verdicts"]
                if rep["accepted"]:
                    patch += new
                    entry["note"] = (f"Seam found. Scripted patch {rep['patch_ids']} passed all four solver "
                                     f"checks (k={a.k}) and was added.")
                else:
                    bad = [v["check"] for v in rep["verdicts"] if v["verdict"] != "pass"]
                    entry["note"] = f"Seam found. Patch {rep['patch_ids']} rejected by checks {bad}."
        else:
            entry["note"] = "Final re-run." if patch else "Final run."
        history.append(entry)
    rec.run_id = f"{rec.spec_name}-loop-{agents_slug(agents)}-m{a.months}-s{a.seed}-r{a.rounds}"
    rec.kind, rec.history, rec.checks = "loop", history, checks
    rec.rounds = [{"round": h["round"], "seams": h["seams"]} for h in history]
    path = build_report(rec, a.runs_dir)
    print(f"report: {path}")
    print("Seams per round: " + ", ".join(f"round {h['round']}: {h['seams']}" for h in history))
    for h in history:
        print(f"  round {h['round']}: {h['note']}")
    print(verdict(rec)[1])
    return 0


def cmd_report(a) -> int:
    rec = load_record(a.run_id, a.runs_dir)
    print(f"report: {build_report(rec, a.runs_dir)}")
    print(verdict(rec)[1])
    return 0


def parser():
    p = argparse.ArgumentParser(prog="mar", description="Multi-agent rules workbench.")
    p.add_argument("--runs-dir", default="runs", help="where reports and traces go (default: runs)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, agents=True):
        sp.add_argument("--spec", required=True, help="directory of YAML rule cards, e.g. rules/fishery")
        if agents:
            sp.add_argument("--agents", default="exploiter*4", help="comma list of exploiter|compliant|explorer, "
                            "name*n repeats (default exploiter*4)")
            sp.add_argument("--months", type=int, default=6)
            sp.add_argument("--seed", type=int, default=0)

    common(sub.add_parser("run", help="run the fishery under a spec; write a report"))
    rules = sub.add_parser("rules", help="read rules").add_subparsers(dest="rules_cmd", required=True)
    common(rules.add_parser("show", help="print the cards in readable form"), agents=False)
    c = sub.add_parser("check", help="solver checks (conflict, deadlock, sanctions, repair) with bound k")
    common(c, agents=False)
    c.add_argument("--k", type=int, default=K_DEFAULT, help="sanction months to look ahead")
    lp = sub.add_parser("loop", help="scripted refinement loop: run, find seam, patch, check, re-run")
    common(lp)
    lp.add_argument("--rounds", type=int, default=2)
    lp.add_argument("--k", type=int, default=K_DEFAULT)
    r = sub.add_parser("report", help="rebuild the report of an earlier run from its trace.json")
    r.add_argument("run_id")
    return p


def main(argv=None) -> int:
    a = parser().parse_args(argv)
    try:
        if a.cmd == "rules":
            return cmd_rules_show(a)
        return {"run": cmd_run, "check": cmd_check, "loop": cmd_loop, "report": cmd_report}[a.cmd](a)
    except (ValueError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
