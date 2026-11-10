"""`mar`: a thin command line over the library. Each command prints plain English.

  mar run --spec rules/fishery --agents exploiter,compliant --months 6 --seed 0
  mar run --spec rules/fishery --agents jev*3,llm*2 --temperature 2 --model <openrouter id> --dry-run
  mar rules show --spec rules/fishery
  mar check --spec rules/fishery [--k 3]
  mar loop --spec rules/fishery --rounds 2
  mar report <run_id>
  mar log [--last 10] [--run <id>]       experiment log (experiments/log.jsonl)
  mar keep <run_id>                      copy trace and report into experiments/kept/<run_id>/
  mar change record|list                 change log (experiments/changes.jsonl)
  mar question record|list               curiosity log (experiments/questions.jsonl)
  mar sweep --backend claude --agents claude*5 --claude-model <id> --seeds 0,1,2 [--batch]
  mar timeline [--keep]                  one HTML page of questions, decisions, changes, runs, commits;
                                         --keep also saves experiments/timelines/<date>.html and .md
  mar evolve [--v2] [--dry-run]          evolution loop on the fishery (scripted, no model calls, minutes)
  mar game vpgg|bargaining [--report-only]   the two rediscovery games (scripted, no model calls)
  mar empower --world fishery|vpgg       empowerment vs the hand-made freedom score
  mar ladder --model kind:id --max-usd N [--dry-run|--report-only]   live seam ladder (spends money)
  mar lint [--k 3]                       lint every rule set (exit 1 if any fails without known_flaw)
  mar results                            one-line verdicts of docs/results/*.md and the latest reports
  mar household                          stub until the household seed v2 run lands

Every run and loop appends one line to the experiment log (--note says why). Reports and traces go to
runs/<run_id>/ (override with --runs-dir; logs with --experiments-dir). Scripted agents make no calls.
jev and llm agents call the network and need keys in .env (see .env.example); --dry-run prices a run first.
"""
import argparse
import sys
from pathlib import Path

from . import log as explog
from . import oracle
from .agents.base import AgentError
from .agents.factory import AgentFactory
from .agents.jev import JEV_MODEL
from .cards import load_cards
from .patch_check import K_DEFAULT, check_patch, check_spec
from .patcher import propose_patch
from .report import (RunRecord, build_report, cond_text, execute, load_record, parse_agents, agents_slug,
                     rules_text, run_story, sanction_text, verdict)

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


def make_factory(a) -> AgentFactory:
    return AgentFactory(temperature=a.temperature, jev_provider=a.jev_provider, jev_model=a.jev_model,
                        llm_model=a.model, claude_model=a.claude_model or a.model, cache_share=a.cache_hit_share,
                        claude_out_tokens=a.claude_out_tokens, llm_temperature=a.llm_temperature, llm_price_in=a.llm_price_in,
                        llm_price_out=a.llm_price_out, cache_dir=Path(a.runs_dir) / "cache" / "jev",
                        max_usd=a.max_usd)


def dry_run(a, names, rounds=1) -> int:
    est = make_factory(a).estimate(names, a.months, rules_text(load_cards(a.spec)), rounds)
    if not est:
        print("Dry run: no jev or llm agents, so no model calls and no cost.")
        return 0
    print(f"Dry run (nothing is called or logged). Upper bounds, no cache hits, {rounds} run(s) of {a.months} months:")
    for kind, e in est.items():
        batch = f"; with --batch ${e['usd_batch']:.4f}" if "usd_batch" in e else ""
        print(f"  {kind}: up to {e['calls']} calls, about {e['input_tokens']} input tokens, "
              f"cost ${e['usd']:.4f}{batch} ({e['note']})")
    print(f"Total upper bound: ${sum(e['usd'] for e in est.values()):.4f}")
    return 0


def cmd_run(a) -> int:
    names = parse_agents(a.agents)
    if a.dry_run:
        return dry_run(a, names)
    factory = make_factory(a)
    rec = execute(a.spec, names, a.months, a.seed, factory=factory)
    path = build_report(rec, a.runs_dir)
    _log(a, rec, path)
    print(f"report: {path}")
    print(verdict(rec)[1])
    _print_usage(rec)
    print(f"logged: {Path(a.experiments_dir) / explog.LOG_NAME}")
    return 0


def _print_usage(rec):
    for kind, u in rec.backends.items():
        print(f"{kind}: {', '.join(u['model_builds']) or 'no model build seen'}; {u['calls']} calls "
              f"({u['cache_hits']} cached), {u['input_tokens']} in / {u['output_tokens']} out tokens, ${u['usd']:.4f}")
    if rec.reports:
        print(f"typed reports: {sum(r['lie'] for r in rec.reports)} of {len(rec.reports)} did not match what was done")


def _log(a, rec, report_path):
    b = rec.backends
    builds = sorted({m for u in b.values() for m in u["model_builds"]})
    explog.log_run(a.experiments_dir, rec, verdict(rec)[1], report_path, Path(report_path).parent / "trace.json",
                   a.spec, note=a.note, model="; ".join(builds) or None,
                   cost_usd=round(sum(u["usd"] for u in b.values()), 6) if b else None, backends=b)


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
    if a.dry_run:
        return dry_run(a, agents, a.rounds + 1)
    factory = make_factory(a)
    base = load_cards(a.spec)
    patch, history, checks = [], [], []
    rec = None
    for r in range(a.rounds + 1):
        rec = execute(a.spec, agents, a.months, a.seed, patch_cards=patch, factory=factory)
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
    rec.run_id = f"{rec.spec_name}-loop-{agents_slug(agents)}{factory.tag(agents)}-m{a.months}-s{a.seed}-r{a.rounds}"
    rec.kind, rec.history, rec.checks = "loop", history, checks
    rec.rounds = [{"round": h["round"], "seams": h["seams"]} for h in history]
    path = build_report(rec, a.runs_dir)
    _log(a, rec, path)
    print(f"report: {path}")
    print("Seams per round: " + ", ".join(f"round {h['round']}: {h['seams']}" for h in history))
    for h in history:
        print(f"  round {h['round']}: {h['note']}")
    print(verdict(rec)[1])
    _print_usage(rec)
    print(f"logged: {Path(a.experiments_dir) / explog.LOG_NAME}")
    return 0


def cmd_sweep(a) -> int:
    """Seeds of one setup. With --batch, all runs advance in lockstep and each step is one Message Batch."""
    import anthropic

    from .agents.batch import BatchCoordinator, run_lockstep
    names = parse_agents(a.agents)
    seeds = [int(x) for x in a.seeds.split(",") if x.strip()]
    if a.backend != "claude" or "claude" not in names:
        raise ValueError("mar sweep supports --backend claude and needs claude agents in --agents")
    if a.dry_run:
        return dry_run(a, names, len(seeds))
    base = make_factory(a)
    if a.batch:
        from .agents.claude import require_model
        require_model(base.claude_model)
        coord = BatchCoordinator(anthropic.Anthropic(), len(seeds), poll_s=a.poll_seconds)

        def job(seed):
            def go():
                f = make_factory(a)
                f.batch = True
                f.transport_for = lambda idx: _transport(coord, seed, idx)
                return execute(a.spec, names, a.months, seed, factory=f)
            return go
        results = run_lockstep(coord, [job(s) for s in seeds])
    else:
        results = []
        for s in seeds:
            try:
                results.append((execute(a.spec, names, a.months, s, factory=make_factory(a)), None))
            except AgentError as e:
                results.append((None, e))
    for s, (rec, err) in zip(seeds, results):
        if err is not None:
            print(f"seed {s}: failed: {err}", file=sys.stderr)
            continue
        path = build_report(rec, a.runs_dir)
        _log(a, rec, path)
        print(f"seed {s}: report: {path}")
        _print_usage(rec)
    failed = [e for _, e in results if e is not None]
    if failed:
        raise failed[0]
    print(f"logged: {Path(a.experiments_dir) / explog.LOG_NAME}")
    return 0


def _transport(coord, seed, idx):
    n = [0]

    def send(params):
        n[0] += 1
        return coord.request(f"r{seed}-a{idx}-c{n[0]}", params)
    return send


def cmd_log(a) -> int:
    rows = explog.read_rows(Path(a.experiments_dir) / explog.LOG_NAME)
    if a.run:
        hits = [r for r in rows if r["run_id"] == a.run]
        if not hits:
            raise ValueError(f"no log entry for run {a.run!r}")
        print("\n\n".join(explog.log_detail(r) for r in hits))
    else:
        print(explog.log_table(rows[-a.last:] if a.last > 0 else rows))
    return 0


def cmd_keep(a) -> int:
    dest = explog.keep(a.experiments_dir, a.runs_dir, a.run_id)
    print(f"kept: {dest} (trace.json, report.html). Commit it to cite this run.")
    return 0


def cmd_change(a) -> int:
    path = Path(a.experiments_dir) / explog.CHANGES_NAME
    if a.change_cmd == "list":
        print(explog.changes_text(explog.read_rows(path)))
        return 0
    row = explog.record_change(a.experiments_dir, a.kind, a.quote, a.reason, a.before, a.after, a.nwim)
    print(f"recorded {row['kind']} change in {path}" + (" (not what I meant)" if row["not_what_i_meant"] else ""))
    return 0


def cmd_question(a) -> int:
    path = Path(a.experiments_dir) / explog.QUESTIONS_NAME
    if a.question_cmd == "list":
        print(explog.questions_text(explog.read_rows(path)))
        return 0
    explog.record_question(a.experiments_dir, a.quote, a.topic, a.led_to)
    print(f"recorded question in {path}")
    return 0


def cmd_timeline(a) -> int:
    from .timeline import build_timeline
    p, counts = build_timeline(a.experiments_dir, a.runs_dir)
    print(f"timeline: {p}")
    print(", ".join(f"{n} {k}" for k, n in counts.items()))
    if a.keep:
        from .timeline import keep_snapshot
        h, m = keep_snapshot(a.experiments_dir)
        print(f"kept: {h}\nkept: {m}\nCommit both with a pathspec commit. They hold the author's own words.")
    return 0


def cmd_report(a) -> int:
    rec = load_record(a.run_id, a.runs_dir)
    print(f"report: {build_report(rec, a.runs_dir)}")
    print(verdict(rec)[1])
    return 0


SCRIPTS = explog.REPO / "scripts"
RESULTS = explog.REPO / "docs" / "results"
REPORT_DIRS = {"evolve": "runs/evolve", "evolve-v2": "runs/evolve-v2", "vpgg": "runs/vpgg",
               "bargaining": "runs/bargaining", "empowerment": "runs/empowerment", "ladder": "runs/ladder_live"}


def _script(name):
    """Load scripts/<name>.py as a module (scripts are not a package); its main() is the real entry point."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"mar_script_{name}", SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _call_main(mod, argv):
    """Run a script main() that reads sys.argv, with a controlled argv."""
    old = sys.argv
    sys.argv = ["script", *argv]
    try:
        return mod.main()
    finally:
        sys.argv = old


def _report_line(key):
    p = explog.REPO / REPORT_DIRS[key] / "report.html"
    print(f"report: {p}" if p.exists() else f"no report yet at {p}")
    return p


def cmd_evolve(a) -> int:
    name, key = ("evolve_v2_run", "evolve-v2") if a.v2 else ("evolve_run", "evolve")
    prereg = RESULTS / ("evolve-v2-prereg.md" if a.v2 else "evolve-prereg.md")
    if a.dry_run:
        print(f"Dry run (nothing is run). Would run scripts/{name}.py on the fishery: scripted agents, no model calls, "
              f"no network, no cost. Takes about {'5' if a.v2 else '4'} minutes. Prereg: {prereg}. "
              f"Report would go to {explog.REPO / REPORT_DIRS[key] / 'report.html'}.")
        return 0
    _call_main(_script(name), [])
    _report_line(key)
    return 0


def cmd_game(a) -> int:
    key = a.game
    if a.report_only:
        return 0 if _report_line(key).exists() else 2
    _call_main(_script(f"{key}_run"), ["--seeds", str(a.seeds)])
    _report_line(key)
    return 0


def cmd_empower(a) -> int:
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _call_main(_script("empowerment_run"), [])
    lines = buf.getvalue().splitlines()
    cut = next((i for i, ln in enumerate(lines) if ln.startswith("hand-made freedom")), len(lines))
    judge = [ln for ln in lines if " PASS " in ln or " FAIL " in ln]
    body = lines[:cut + 1] if a.world == "vpgg" else lines[:1] + lines[cut + 1:]
    print(f"world: {a.world} (the script computes both worlds; showing this one plus the judge lines)")
    print("\n".join(ln for ln in body if ln not in judge).rstrip())
    print("\n".join(judge))
    print(f"summary: {explog.REPO / REPORT_DIRS['empowerment'] / 'summary.json'} (no HTML report for this command)")
    return 0


def cmd_ladder(a) -> int:
    argv = []
    for m in a.model:
        argv += ["--model", m]
    argv += ["--seeds", *map(str, a.seeds), "--attempts", str(a.attempts)]
    if a.max_usd is not None:
        argv += ["--max-usd", str(a.max_usd)]
    mod = _script("ladder_live_run")
    if a.report_only:
        code = mod.main(["--report-only"])
        _report_line("ladder")
        return code
    if not a.model:
        raise ValueError("give at least one --model kind:model_id")
    print("Dry-run estimate first (nothing is called):")
    code = mod.main([*argv, "--dry-run"])
    if a.dry_run or code:
        return code
    if a.max_usd is None or a.max_usd <= 0:
        print("refusing to run live without --max-usd (a positive hard cap in USD). The estimate above is what it would cost. "
              "Show it to the author and get a yes in chat first.", file=sys.stderr)
        return 2
    code = mod.main(argv)
    _report_line("ladder")
    return code


def _one_line(path: Path) -> str:
    """Verdict line of a results file: first line under a Verdict/Summary/Bottom line heading, else the Status
    line, else the first paragraph after the title."""
    lines = path.read_text().splitlines()
    para = [ln.strip() for ln in lines[1:] if ln.strip() and not ln.startswith("#")]
    for i, ln in enumerate(lines):
        if ln.startswith("#") and any(w in ln.lower() for w in ("verdict", "summary", "bottom line")) and i > 0:
            for nxt in lines[i + 1:]:
                if nxt.strip() and not nxt.startswith("#"):
                    para = [nxt.strip()]
                    break
            break
    text = (para[0] if para else "").replace("**", "").replace("`", "")
    return text if len(text) <= 160 else text[:157].rstrip() + "..."


def cmd_results(a) -> int:
    for p in sorted(RESULTS.glob("*.md")):
        if p.name.endswith(("-prereg.md", "-prereg-DRAFT.md")) or p.name == "workbench.md":
            continue
        title = (p.read_text().splitlines() or [""])[0].lstrip("# ").strip()
        print(f"{p.name}: {title}\n    {_one_line(p)}")
    print("\nLatest reports:")
    found = False
    for rep in sorted(explog.REPO.glob("runs/**/report.html"), key=lambda x: x.stat().st_mtime, reverse=True):
        print(f"  {rep}")
        found = True
    if not found:
        print("  none yet (run a command to build one)")
    return 0


def cmd_lint(a) -> int:
    from . import lint as L
    res = L.lint_all(k=a.k, negotiated=a.negotiated)
    print(L.summary_table(res))
    bad = [r["name"] for r in res if r["status"] != "pass"]
    print("\nBounded verdicts; `open` is never safe. A flaw is waived only by a `known_flaw` field on a card it names. "
          + (f"Not clean: {len(bad)} rule sets." if bad else "All rule sets pass."))
    return 1 if bad else 0


def cmd_household(a) -> int:
    print("household commands land after the seed v2 run")
    return 0


def parser():
    p = argparse.ArgumentParser(prog="mar", description="Multi-agent rules workbench.")
    p.add_argument("--runs-dir", default="runs", help="where reports and traces go (default: runs)")
    p.add_argument("--experiments-dir", default=str(explog.REPO / "experiments"),
                   help="where the committed logs go (default: <repo>/experiments)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, agents=True, seed=True):
        sp.add_argument("--spec", required=True, help="directory of YAML rule cards, e.g. rules/fishery")
        if agents:
            sp.add_argument("--agents", default="exploiter*4", help="comma list of exploiter|compliant|explorer|jev|llm|claude, "
                            "name*n repeats, e.g. jev*3,llm*2 or claude*5 (default exploiter*4)")
            sp.add_argument("--months", type=int, default=6)
            if seed:
                sp.add_argument("--seed", type=int, default=0)
            sp.add_argument("--note", default=None, help="one-line plain summary of why this run was made")
            sp.add_argument("--dry-run", action="store_true", help="print the call count and an upper-bound cost; run nothing")
            sp.add_argument("--temperature", type=float, default=1.0,
                            help="Jev temperature T: probabilities become p^(1/T), renormalized (default 1; "
                            "T above 1 flattens an overconfident model)")
            sp.add_argument("--model", default=None, help="OpenRouter model id for llm agents (or MAR_LLM_MODEL in .env)")
            sp.add_argument("--jev-model", default=JEV_MODEL, help=f"pinned Jev build (default {JEV_MODEL}; latest is refused)")
            sp.add_argument("--jev-provider", default="openrouter", choices=["openrouter", "aimlapi"])
            sp.add_argument("--llm-temperature", type=float, default=0.7, help="sampling temperature sent to the llm")
            sp.add_argument("--llm-price-in", type=float, default=0.0, help="USD per 1M input tokens, for the llm estimate")
            sp.add_argument("--llm-price-out", type=float, default=0.0, help="USD per 1M output tokens, for the llm estimate")
            sp.add_argument("--claude-model", default=None, help="model id for claude agents (else --model); required, "
                            "no default. claude-haiku-5-5 $0.10/$0.50, claude-sonnet-5-5 $2/$10, claude-opus-5-5 "
                            "$4/$20 per 1M tokens in/out")
            sp.add_argument("--cache-hit-share", type=float, default=0.0,
                            help="ASSUMED share of claude input tokens served from the prompt cache, for --dry-run")
            sp.add_argument("--claude-out-tokens", type=int, default=150, help="assumed output tokens per claude call, for --dry-run")
            sp.add_argument("--max-usd", type=float, default=None, help="stop a backend once its spend passes this")

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
    sw = sub.add_parser("sweep", help="run one setup over several seeds; with --batch, as Message Batches")
    common(sw, seed=False)
    sw.add_argument("--seeds", default="0,1,2", help="comma list of seeds (default 0,1,2)")
    sw.add_argument("--backend", default="claude", help="only claude is supported")
    sw.add_argument("--batch", action="store_true", help="submit each step of all runs as one Message Batch: 50%% cost, "
                    "can take hours, not for interactive use (live loop is ASSUMED, mocked-tested only)")
    sw.add_argument("--poll-seconds", type=float, default=30.0)
    r = sub.add_parser("report", help="rebuild the report of an earlier run from its trace.json")
    r.add_argument("run_id")
    lg = sub.add_parser("log", help="show the experiment log")
    lg.add_argument("--last", type=int, default=10, help="how many recent entries (default 10; 0 for all)")
    lg.add_argument("--run", help="show every entry for one run id in full")
    k = sub.add_parser("keep", help="copy a run's trace.json and report.html into experiments/kept/<run_id>/")
    k.add_argument("run_id")
    ch = sub.add_parser("change", help="record or list rule and oracle changes").add_subparsers(
        dest="change_cmd", required=True)
    rc = ch.add_parser("record", help="append one change: the author's exact words, why, before and after")
    rc.add_argument("--kind", required=True, choices=["rule", "oracle"])
    rc.add_argument("--quote", required=True, help="the author's exact words, verbatim")
    rc.add_argument("--reason", required=True, help="one line: why this change")
    rc.add_argument("--before", required=True, help="file with the old text, or - for none")
    rc.add_argument("--after", required=True, help="file with the new text")
    rc.add_argument("--nwim", action="store_true", help="the author is rejecting what a run or rule did")
    ch.add_parser("list", help="print recorded changes")
    q = sub.add_parser("question", help="record or list the author's questions").add_subparsers(
        dest="question_cmd", required=True)
    qr = q.add_parser("record", help="append one question, quoted verbatim")
    qr.add_argument("--quote", required=True, help="the author's exact words, verbatim")
    qr.add_argument("--topic", help="short topic label")
    qr.add_argument("--led-to", action="append", default=[], help="ADR id, change row or run id (repeatable)")
    q.add_parser("list", help="print recorded questions")
    tl = sub.add_parser("timeline", help="build runs/timeline.html from questions, decisions, changes, runs, commits")
    tl.add_argument("--keep", action="store_true", help="also write a dated, committed snapshot: "
                    "experiments/timelines/<date>.html and .md (GitHub-readable)")
    ev = sub.add_parser("evolve", help="evolution loop on the fishery (scripted, no model calls)")
    ev.add_argument("--v2", action="store_true", help="the v2 setup (evolve_v2_run)")
    ev.add_argument("--dry-run", action="store_true", help="say what would run; run nothing")
    gm = sub.add_parser("game", help="rediscovery games: vpgg or bargaining (scripted, no model calls)")
    gm.add_argument("game", choices=["vpgg", "bargaining"])
    gm.add_argument("--seeds", type=int, default=20)
    gm.add_argument("--report-only", action="store_true", help="just print the path of the existing report")
    em = sub.add_parser("empower", help="empowerment vs the hand-made freedom score")
    em.add_argument("--world", required=True, choices=["fishery", "vpgg"])
    ld = sub.add_parser("ladder", help="live seam ladder: SPENDS MONEY; prints the estimate first, needs --max-usd")
    ld.add_argument("--model", action="append", default=[], help="kind:model_id[@price_in,price_out]; repeatable")
    ld.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ld.add_argument("--attempts", type=int, default=1)
    ld.add_argument("--max-usd", type=float, default=None, help="required for live runs: hard spending cap")
    ld.add_argument("--dry-run", action="store_true", help="print the estimate and stop")
    ld.add_argument("--report-only", action="store_true", help="rebuild report.html from the log")
    sub.add_parser("results", help="one-line verdicts of docs/results/*.md and paths of the latest reports")
    ln = sub.add_parser("lint", help="lint every rule set under rules/ (no legal move, no exit, contradictions, gloss vs fields)")
    ln.add_argument("--k", type=int, default=3)
    ln.add_argument("--negotiated", type=int, default=40, help="sample size of compiled negotiated agreements (0 = none)")
    sub.add_parser("household", help="stub: household commands land after the seed v2 run")
    return p


def main(argv=None) -> int:
    a = parser().parse_args(argv)
    try:
        if a.cmd == "rules":
            return cmd_rules_show(a)
        return {"run": cmd_run, "check": cmd_check, "loop": cmd_loop, "report": cmd_report,
                "log": cmd_log, "keep": cmd_keep, "change": cmd_change,
                "question": cmd_question, "timeline": cmd_timeline, "sweep": cmd_sweep,
                "evolve": cmd_evolve, "game": cmd_game, "empower": cmd_empower, "ladder": cmd_ladder,
                "results": cmd_results, "household": cmd_household, "lint": cmd_lint}[a.cmd](a)
    except (ValueError, FileNotFoundError, AgentError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
