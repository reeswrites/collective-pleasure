"""Diagnose a live ladder log without any model call.

  uv run python scripts/ladder_live_analyze.py [LOG] [--replay] [--mocks]

Default (log only): per model, the distribution of logged deviation moves, refusals by rule set and seed, and how
many runs had both partners deviating (the oracle only counts a NON-deviating partner as a victim).
--replay: re-play each logged run's deviation moves as a script (all other slots follow the cooperative default) and
          re-classify it three ways: both partners' moves (should match the log), only A's moves, only B's moves.
--mocks:  scripted hypotheses on the real harness: do-nothing, random, symmetric adversaries, one-sided adversaries.
Limits of the log (stated, not worked around): only deviation moves are logged (request, leave, return,
refuse_request, gift_pooled), so work / spend_self / see_friend / spend_shared counts are not recoverable; Claude
refusal stop_details categories are not logged (the ledger is discarded), only per-run refusal counts.
"""
import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from mar import household_oracle as oracle
from mar import ladder_live as LL
from mar import seam_depth as S
from mar.worlds import household as H

DEFAULT_LOG = Path(__file__).resolve().parents[1] / "experiments/kept/ladder-capability-2026-11-10/log.jsonl"
MOVE_RE = re.compile(r"([AB]) m(\d)s(\d): (\w+)(?: take=(\d+))?(?: (\w+))?$")


def load(path):
    runs, models = [], {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r["kind"] == "ladder_live_run":
            runs.append(r)
        elif r["kind"] == "ladder_live_model":
            models[r["model"]] = r
    return runs, models


def parse_move(text):
    m = MOVE_RE.match(text)
    role, mo, sl, act, take, kind = m.groups()
    return {"role": role, "month": int(mo), "slot": int(sl), "action": act,
            "take": None if take is None else int(take), "kind": kind}


def label(mv):
    if mv["action"] == "request":
        return f"request:{mv['kind']}"
    if mv["action"] == "leave":
        return f"leave:{mv['take']}"
    return mv["action"]


def short(model):
    return model.split("/")[-1]


def pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "-"


def log_tables(runs, models):
    by = defaultdict(list)
    for r in runs:
        by[r["model"]].append(r)
    order = list(models) or list(by)
    out = []
    out.append("## (4) Deviation moves per model (all rule sets, 45 runs each)\n")
    labs = ["request:no_contact", "request:stay_home", "refuse_request", "leave:0", "leave:100", "return", "gift_pooled"]
    out.append("| model | decisions | deviations | dev. rate | " + " | ".join(labs) + " |")
    out.append("|---|---|---|---|" + "---|" * len(labs))
    for m in order:
        rs = by[m]
        c = Counter(label(parse_move(x)) for r in rs for x in r["moves"])
        dec = sum(r["decisions"] for r in rs)
        dev = sum(c.values())
        out.append(f"| {short(m)} | {dec} | {dev} | {pct(dev, dec)} | " + " | ".join(str(c.get(k, 0)) for k in labs) + " |")
    out.append("\nOther labels seen: " + ", ".join(sorted({label(parse_move(x)) for r in runs for x in r['moves']}
                                                         - set(labs))) + " (empty = none)")

    out.append("\n## Both partners deviating (no non-deviating victim possible)\n")
    out.append("| model | runs with >=1 deviation | both A and B deviated | only A | only B |")
    out.append("|---|---|---|---|---|")
    for m in order:
        rs = by[m]
        roles = [{parse_move(x)["role"] for x in r["moves"]} for r in rs]
        any_ = sum(1 for s in roles if s)
        out.append(f"| {short(m)} | {any_} | {sum(1 for s in roles if s == {'A', 'B'})} | "
                   f"{sum(1 for s in roles if s == {'A'})} | {sum(1 for s in roles if s == {'B'})} |")

    out.append("\n## Request kinds and out-of-model moves by rule set (count of logged moves)\n")
    out.append("| model | rule | requests | leaves | gift_pooled | refuse_request | class counts |")
    out.append("|---|---|---|---|---|---|---|")
    for m in order:
        for rule in S.LADDER:
            rs = [r for r in by[m] if r["rule"] == rule]
            mv = [parse_move(x) for r in rs for x in r["moves"]]
            c = Counter(x["action"] for x in mv)
            cl = Counter(r["class"] for r in rs)
            out.append(f"| {short(m)} | {rule[:2]} | {c['request']} | {c['leave']} | {c['gift_pooled']} | "
                       f"{c['refuse_request']} | {dict(cl)} |")

    out.append("\n## (5) Refusals (per-call refusal counts; stop_details categories were not logged)\n")
    out.append("| model | refusals | decisions | rate | " + " | ".join(r[:2] for r in S.LADDER) + " | by seed 0/1/2 | runs with >=1 |")
    out.append("|---|---|---|---|" + "---|" * len(S.LADDER) + "---|---|")
    for m in order:
        rs = by[m]
        tot, dec = sum(r["refusals"] for r in rs), sum(r["decisions"] for r in rs)
        per_rule = [sum(r["refusals"] for r in rs if r["rule"] == rl) for rl in S.LADDER]
        per_seed = [sum(r["refusals"] for r in rs if r["seed"] == s) for s in (0, 1, 2)]
        out.append(f"| {short(m)} | {tot} | {dec} | {pct(tot, dec)} | " + " | ".join(map(str, per_rule))
                   + f" | {'/'.join(map(str, per_seed))} | {sum(1 for r in rs if r['refusals'])}/{len(rs)} |")
    op = [r for r in runs if "opus" in r["model"]]
    if op:
        ref_runs = [r for r in op if r["refusals"]]
        out.append(f"\nOpus: refusals per run (runs with any): min {min((r['refusals'] for r in ref_runs), default=0)}, "
                   f"max {max((r['refusals'] for r in ref_runs), default=0)}; runs with 0 refusals: "
                   f"{sum(1 for r in op if not r['refusals'])}.")
        mixed = [r for r in op if r["refusals"] and r["moves"]]
        out.append(f"Opus runs that both refused some calls and made some deviation moves: {len(mixed)} of {len(op)}.")

    out.append("\n## (6) Haiku: caution profile\n")
    h = [r for r in runs if "haiku" in r["model"]]
    if h:
        out.append(f"runs {len(h)}, decisions {sum(r['decisions'] for r in h)}, deviation moves "
                   f"{sum(len(r['moves']) for r in h)}, refusals {sum(r['refusals'] for r in h)}, format errors "
                   f"{sum(r['format_errors'] for r in h)}, cost ${sum(r['usd'] for r in h):.3f} (of the six models' "
                   f"total ${sum(r['usd'] for r in runs):.3f}). Every decision was a non-deviation action "
                   f"(work, spend or see_friend; which is not logged). Nothing in the log separates 'declined the "
                   f"red-team task' from 'chose the first option, work, which SAFE_OPTION lists first'.")
    return "\n".join(out)


# ---- replay ----------------------------------------------------------------------------------------------

class Script:
    """Scripted agent: forced candidates at (month, slot), the cooperative default elsewhere."""
    def __init__(self, forced):
        self.base, self.forced = H.Cooperator(), forced

    @property
    def rng(self):
        return self.base.rng

    @rng.setter
    def rng(self, v):
        self.base.rng = v

    def consents(self, kind):
        return True

    def propose(self, o):
        f = self.forced.get((o["month"], o["slot"]))
        return [f] + self.base.propose(o) if f else self.base.propose(o)


def cand(mv):
    if mv["action"] == "request":
        return {"a": "request", "kind": mv["kind"]}
    if mv["action"] == "leave":
        return {"a": "leave", "take": mv["take"] or 0}
    return {"a": mv["action"]}


def play(cards, agents, seed):
    return LL.HouseholdAdapter.play(cards, agents, seed)


def replay_class(cards, moves, seed, roles):
    forced = {r: {(m["month"], m["slot"]): cand(m) for m in moves if m["role"] == r and r in roles} for r in "AB"}
    run = play(cards, {"A": Script(forced["A"]), "B": Script(forced["B"]), "C": H.Friend()}, seed)
    return LL.classify(run, cards)["kind"]


def replay_tables(runs):
    cards = {n: S.load_ladder(n) for n in S.LADDER}
    agg = defaultdict(lambda: Counter())
    for r in runs:
        mv = [parse_move(x) for x in r["moves"]]
        if not mv:
            agg[(r["model"], r["rule"])]["no deviation"] += 1
            continue
        c = cards[r["rule"]]
        agg[(r["model"], r["rule"])]["logged:" + r["class"]] += 1
        agg[(r["model"], r["rule"])]["replay both:" + replay_class(c, mv, r["seed"], "AB")] += 1
        for who, other in (("A", "B"), ("B", "A")):
            if any(m["role"] == who for m in mv):
                agg[(r["model"], r["rule"])][f"only {who}'s moves:" + replay_class(c, mv, r["seed"], who)] += 1
    out = ["## Replay of logged deviation moves (non-deviation slots filled by the cooperative default)\n",
           "'only A' keeps A's logged moves and plays B as a plain cooperator, so B is a victim not a deviator.\n",
           "| model | rule | counts |", "|---|---|---|"]
    for (m, rl), c in sorted(agg.items()):
        out.append(f"| {short(m)} | {rl[:2]} | {dict(sorted(c.items()))} |")
    tot = Counter()
    for (m, rl), c in agg.items():
        for k, v in c.items():
            if k.startswith("only"):
                tot[(rl[:2], k)] += v
    out.append("\nUnilateral replay totals over all models (rule, case: count):")
    for k, v in sorted(tot.items()):
        out.append(f"- {k[0]} {k[1]}: {v}")
    return "\n".join(out)


# ---- mocks -----------------------------------------------------------------------------------------------

class Always:
    """Issues `act` every round it can (request kind given), else the cooperative default."""
    def __init__(self, act):
        self.act, self.base = act, H.Cooperator()

    @property
    def rng(self):
        return self.base.rng

    @rng.setter
    def rng(self, v):
        self.base.rng = v

    def consents(self, kind):
        return True

    def propose(self, o):
        return [self.act] + self.base.propose(o)


class Coop(H.Cooperator):
    pass


class Quiet:
    """Do-nothing partner: only work and spend_shared, never sees the friend, never requests."""
    def consents(self, kind):
        return True

    def propose(self, o):
        return [{"a": "work"}, {"a": "spend_self"}]


class Rand:
    """Uniform random feasible-menu move for the harness vocabulary (what an uninformed model might emit)."""
    def consents(self, kind):
        return True

    def propose(self, o):
        opts = list(LL.feasible_options(o))
        self.rng.shuffle(opts)
        return [LL.option_to_candidate(k) for k in opts]


NC, SH = {"a": "request", "kind": "no_contact"}, {"a": "request", "kind": "stay_home"}
MOCKS = {
    "do-nothing (Cooperator x2)": lambda: (H.Cooperator(), H.Cooperator()),
    "quiet (work only, no friend, no request)": lambda: (Quiet(), Quiet()),
    "random menu x2": lambda: (Rand(), Rand()),
    "both request stay_home every round": lambda: (Always(SH), Always(SH)),
    "both request no_contact every round": lambda: (Always(NC), Always(NC)),
    "only A requests stay_home every round": lambda: (Always(SH), H.Cooperator()),
    "only A requests no_contact every round": lambda: (Always(NC), H.Cooperator()),
    "only B requests no_contact every round": lambda: (H.Cooperator(), Always(NC)),
    "A requests no_contact once (m0s0), B cooperative": lambda: (Script({(0, 0): NC}), H.Cooperator()),
    "A and B each request no_contact once (m0s0)": lambda: (Script({(0, 0): NC}), Script({(0, 0): NC})),
    "only A gifts every round": lambda: (Always({"a": "gift_pooled"}), H.Cooperator()),
    "only B gifts every round": lambda: (H.Cooperator(), Always({"a": "gift_pooled"})),
    "both gift every round": lambda: (Always({"a": "gift_pooled"}), Always({"a": "gift_pooled"})),
}


def mock_tables(seeds=range(6)):
    out = ["## Scripted mock agents on the real harness (class of each run; seeds 0.." + str(max(seeds)) + ")\n",
           "| mock | " + " | ".join(r[:2] for r in S.LADDER) + " |", "|---|" + "---|" * len(S.LADDER)]
    for name, mk in MOCKS.items():
        cells = []
        for rule in S.LADDER:
            cards = S.load_ladder(rule)
            cl = Counter()
            for s in seeds:
                a, b = mk()
                run = play(cards, {"A": a, "B": b, "C": H.Friend()}, s)
                cl[LL.classify(run, cards)["kind"]] += 1
            cells.append(", ".join(f"{k}:{v}" for k, v in sorted(cl.items())))
        out.append(f"| {name} | " + " | ".join(cells) + " |")
    out.append("\nFormal model (k=3, 2 months) per rule set:")
    for rule in S.LADDER:
        f = S.search(S.load_ladder(rule), 3, 0, S.BUDGET_DEFAULT)
        ex = None if not f["example"] else "; ".join(S.move_text(a) for a in f["example"])
        out.append(f"- {rule}: {f['status']}, depth {f['depth']}, agents {f['agents']}, example: {ex}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", nargs="?", default=str(DEFAULT_LOG))
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--mocks", action="store_true")
    a = ap.parse_args(argv)
    runs, models = load(a.log)
    print(log_tables(runs, models))
    if a.replay:
        print("\n" + replay_tables(runs))
    if a.mocks:
        print("\n" + mock_tables())
    return 0


if __name__ == "__main__":
    sys.exit(main())
