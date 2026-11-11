"""Observer layer demo (docs/notes/observer-schema.md, section "Demo"). EXPLORATORY: no prereg, no prediction tested. Scripted persona
agents, no model calls. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Re-runs 40 runs of two atlas families with the observer on, then reads three things the pattern atlas could not:
  1. which part tipped formation and leave decisions (reading rows: household and outside values split into parts);
  2. whether lopsided stretches even out, in 13-week blocks of the money and time flows (flow and together rows);
  3. "if they had stayed": the 13-week difference a stay replay measures at each leave (replay rows).

  uv run python scripts/observer_demo.py --run        40 runs, at most 3 workers -> runs/observer-demo/obs/ (manifest.json + one file a run)
  uv run python scripts/observer_demo.py --time       observer off vs on, wall time of 4 runs each
  uv run python scripts/observer_demo.py --analyze    the three readings, printed (the doc quotes them)

The sample: H38 pairing norms, arms L0 and L4, the first 10 confirmatory pairings, seed 0, with the stay readings every 13 weeks
(= atlas_run.play_h38); exit fallbacks slice 2, arm F4, items cell V2-split-loves, the author's seed v2.2 (bindable), validation runs
0-19 (= atlas_run.play_ef).
"""
import argparse
import dataclasses
import json
import statistics as stt
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from mar import observe as OB  # noqa: E402

OUT = ROOT / "runs" / "observer-demo"
WORKERS = 3
CFG = OB.ObsConfig(replay_rate=0.05, replay_window=13, replay_leaves=True, replay_pressure=True, replay_seed=0)
H38_ARMS, H38_N, EF_N = ("L0", "L4"), 10, 20
EF_CAND, EF_CELL = "author_seed_v2_bindable", "V2-split-loves"


def play_h38(arm, a, b, seed, observe=True):
    import h38_pairing_run as P
    from mar import exit_fallback as EF
    from mar import exit_items as EI
    from mar import hedonic as HD
    from mar import negotiation as NG
    from mar import pairing as PR
    from mar import retest as RT
    from mar.worlds import household as H
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=P.ARMS[arm])
    rec = OB.collecting() if observe else HD.recording_parts(False)
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[P.CELL]), rec:
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=H.WEEKS, decline=True)
        world = lived.world
        ob = OB.Observer(world, CFG, run_key=f"h38|{arm}|{a}|{b}|{seed}", meta={"family": "h38", "arm": arm},
                         harness=lived) if observe else None
        last = {"busy": {"A": False, "B": False}}
        for w in range(world.weeks):
            if w and w % NG.REVIEW_EVERY == 0:
                if lived.apart and lived.decline:
                    lived.retry(w, last)
                elif all(world.p[r]["in"] for r in "AB"):
                    rd = PR.stay_reading(world, w, last)
                    if ob is not None:
                        ob.stay(w, rd)
                    lived.reading(w, last)
            if world.early_review:
                world.ladder_reviewed(w)
            last = {"busy": world.step_week(w, last)}
    return ob.finish() if ob is not None else world


def play_ef(i, observe=True):
    import exit_fallbacks_run as X
    from mar import exit_fallback as EF
    from mar import exit_items as EI
    from mar import hedonic as HD
    from mar import world_api as W
    from mar.cards import load_cards
    from mar.worlds import household as H
    hr = X.ctx("val").runs[i]
    ps = W.hh_personas()
    cfg = dataclasses.replace(HD.DEFAULT, job_loss_rate=hr.rates[0], illness_rate=hr.rates[1], move_rate=hr.rates[2],
                              new_connection_rate=hr.rates[3], start=hr.start)
    box = {}
    rec = OB.collecting() if observe else HD.recording_parts(False)
    with EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[EF_CELL]), rec:
        gate = H.PyGate(load_cards(str(H.RULES / EF_CAND)))

        def go():
            with HD.use_levers(X.LEVERS):
                wk = H.WeeklyWorld(gate, (ps[hr.a], ps[hr.b]), hr.seed, hr.weeks, cfg)
                if observe:
                    box["ob"] = OB.Observer(wk, CFG, run_key=f"ef|F4|{EF_CAND}|{i}", meta={"family": "ef", "arm": "F4", "run": i})
                wk.play()
            return wk
        wk = W._with_rates(hr.rates, go)
    return box["ob"].finish() if observe else wk


def tasks():
    import h38_pairing_run as P
    from mar import retest as RT
    out = [("h38", arm, a, b, 0) for a, b in RT.sample(P.CONFIRM["n_other"], P.CONFIRM["sample_seed"])[:H38_N] for arm in H38_ARMS]
    return out + [("ef", "F4", i, None, 0) for i in range(EF_N)]


def task(t, observe=True):
    fam, arm, x, y, s = t
    t0 = time.time()
    ob = play_h38(arm, x, y, s, observe) if fam == "h38" else play_ef(x, observe)
    secs = round(time.time() - t0, 2)
    if not observe:
        return {"secs": secs}
    e = OB.write_run(ob, OUT)
    e.update(secs=secs, family=fam, arm=arm)
    return e


def run():
    ts = tasks()
    with Pool(min(WORKERS, 3)) as pool:
        entries = pool.map(task, ts)
    p = OB.write_manifest(OUT, entries, "observer-demo", CFG, note="40 runs: H38 L0/L4 x 10 pairings (seed 0); exit fallbacks F4 with "
                          "items, validation runs 0-19. EXPLORATORY (scripts/observer_demo.py).")
    b = [e["bytes"] for e in entries]
    print(f"wrote {p}: {len(entries)} runs, {sum(b) / 1e6:.2f} MB, {stt.mean(b) / 1e3:.0f} kB a run (median {stt.median(b) / 1e3:.0f})")


def time_cmp():
    ts = [t for t in tasks() if t[0] == "h38"][:2] + [t for t in tasks() if t[0] == "ef"][:2]
    for t in ts:
        off = task(t, observe=False)["secs"]
        t0 = time.time()
        task(t, observe=True)
        print(t, f"off {off:.2f}s  on {time.time() - t0:.2f}s")


# ---- analyses ------------------------------------------------------------------------------------------------------------------

def load():
    m = json.loads((OUT / "obs" / "manifest.json").read_text())
    return m, {e["run_key"]: OB.read(OUT / e["file"]) for e in m["runs"]}


def fam_of(key):
    f = key.split("|")
    return f[0] if f[0] == "ef" else f"{f[0]} {f[1]}"


def tip(m, extra_o=None):
    """The part that tipped one member's verdict: diff_g = W_parts - O_parts per group (extra_o: terms subtracted from O outside its
    rollout, e.g. the exit stigma, as their own parts). A part tips the verdict when removing it alone flips the sign of the margin; of
    those, the largest. -> (part or 'none-alone', margin, diffs)."""
    if not m["W_parts"] or not m["O_parts"]:
        return None
    d = {g: m["W_parts"].get(g, 0.0) - m["O_parts"].get(g, 0.0) for g in OB.GROUPS}
    for k, v in (extra_o or {}).items():
        d[k] = d.get(k, 0.0) + v
    margin = sum(d.values())
    flip = {g: v for g, v in d.items() if v * margin > 0 and abs(v) > abs(margin)}
    return (max(flip, key=lambda g: abs(flip[g])) if flip else "none-alone"), margin, d


def a1_tipping(runs):
    print("\n== 1. What tipped formation and leave decisions ==")
    form = defaultdict(Counter)
    for key, t in runs.items():
        for rd in t.get("reading", []):
            if rd["kind"] not in ("formation0", "retry"):
                continue
            for r in "AB":
                x = tip(rd["m"][r])
                if x:
                    form[(fam_of(key), "wants in" if x[1] > 0 else "wants out")][x[0]] += 1
    for k in sorted(form):
        n = sum(form[k].values())
        print(f"  formation {k[0]:7s} {k[1]:9s} n={n:3d}: " + ", ".join(f"{g} {c}" for g, c in form[k].most_common(4)))
    bar = defaultdict(Counter)
    for key, t in runs.items():
        for rd in t.get("reading", []):
            if rd["kind"] != "reading":
                continue
            for r in "AB":
                m = rd["m"][r]
                x = tip(m, {"trust": -rd["trust_pen"][r], "pressure": rd.get("exit_anticipation", 0.0)})
                if x and x[1] < 0:              # the outside option beat staying at this reading (the bar's comparison)
                    bar[fam_of(key)][x[0]] += 1
    for k in sorted(bar):
        n = sum(bar[k].values())
        print(f"  reading where outside beat staying {k:7s} n={n:3d}: " + ", ".join(f"{g} {c}" for g, c in bar[k].most_common(4)))
    lv = defaultdict(Counter)
    cond = defaultdict(Counter)
    for key, t in runs.items():
        st = {(s["w"], s["r"]): s for s in t.get("state", [])}
        for d in t.get("decision", []):
            if d["chosen"] is None or d["cands"][d["chosen"]]["a"] != "leave":
                continue
            c = d["cands"][d["chosen"]]
            lc = d.get("leave_ctx") or {}
            why = c.get("why", "distress")
            if why == "distress":
                held = [k for k, f in (("low", "low"), ("N", "n_high"), ("trust", "trust_low")) if lc.get(f)]
                why = "distress:" + "+".join(held)
                if lc.get("n_high"):
                    runs_ = {k: v for k, v in lc.get("cond_run", {}).items() if v}
                    prev = st.get((d["w"] - 1, d["r"]), {})
                    low_needs = [n for n, v in (prev.get("levels") or {}).items() if v < 0.15]
                    cond[fam_of(key)][",".join(sorted(runs_)) + (f" (needs below 0.15: {','.join(low_needs)})" if low_needs else "")] += 1
            lv[fam_of(key)][why] += 1
    for k in sorted(lv):
        print(f"  leaves {k:7s}: " + ", ".join(f"{g} {c}" for g, c in lv[k].most_common()))
    for k in sorted(cond):
        print(f"  N-driven leaves {k:7s}, condition streaks at the leave: " + "; ".join(f"{g}: {c}" for g, c in cond[k].most_common(4)))
    return form, bar, lv


GIVE_CAUSES = ("give_partner", "spend_shared")


def contributions(t, block=13):
    """Per 13-week block (weeks both members were in), each member's net money into the household (gifts to the partner, bill and pot
    contributions, minus draws from the pot: take_shared, the safety net) and the together sessions each started."""
    inside = {x["w"]: x["both_in"] for x in t.get("week", [])}
    out = defaultdict(lambda: {"A": 0.0, "B": 0.0, "tA": 0, "tB": 0, "weeks": 0})
    for w, both in inside.items():
        if both:
            out[w // block]["weeks"] += 1
    for f in t.get("flow", []):
        if not inside.get(f["w"]):
            continue
        b = out[f["w"] // block]
        if f["cause"] in GIVE_CAUSES and f["src"] in "AB" and f["dst"] in ("A", "B", "bills", "pot"):
            b[f["src"]] += f["amt"]
        elif f["cause"] in ("take_shared", "safety_net") and f["dst"] in ("A", "B") and f["src"] == "pot":
            b[f["dst"]] -= f["amt"]
    for x in t.get("together", []):
        if inside.get(x["w"]) and x["initiator"] in ("A", "B"):
            out[x["w"] // block]["t" + x["initiator"]] += 1
    return dict(sorted(out.items()))


def imbalance(a, b):
    tot = abs(a) + abs(b)
    return (a - b) / tot if tot >= 4 else None


def a2_evening(runs, lop=0.30, even=0.15):
    print("\n== 2. Do lopsided stretches even out (13-week blocks, money and time) ==")
    res = defaultdict(lambda: Counter())
    gaps = defaultdict(list)
    for key, t in runs.items():
        blocks = contributions(t)
        for what in ("money", "time"):
            ser = [(k, imbalance(b["A"], b["B"]) if what == "money" else imbalance(b["tA"], b["tB"]))
                   for k, b in blocks.items() if b["weeks"] >= 7]
            ser = [(k, v) for k, v in ser if v is not None]
            fam = fam_of(key)
            for i, (k, v) in enumerate(ser):
                if abs(v) < lop:
                    continue
                res[(fam, what)]["lopsided"] += 1
                nxt = [u for kk, u in ser[i + 1:i + 3] if kk <= k + 2]
                if not nxt:
                    res[(fam, what)]["no later block"] += 1
                elif any(u * v < 0 and abs(u) >= even for u in nxt):
                    res[(fam, what)]["reversed within 2 blocks"] += 1
                elif any(abs(u) < even for u in nxt):
                    res[(fam, what)]["evened within 2 blocks"] += 1
                else:
                    res[(fam, what)]["stayed lopsided same way"] += 1
            if ser:
                tot = {r: sum(b[r if what == "money" else "t" + r] for b in blocks.values() if b["weeks"] >= 7) for r in "AB"}
                gaps[(fam, what)].append(abs(imbalance(tot["A"], tot["B"]) or 0.0))
    for k in sorted(res):
        c = res[k]
        n = c["lopsided"]
        print(f"  {k[0]:7s} {k[1]:5s}: {n:3d} lopsided blocks; " + ", ".join(f"{g} {c[g]}" for g in
              ("reversed within 2 blocks", "evened within 2 blocks", "stayed lopsided same way", "no later block")) +
              f"; whole-run |imbalance| median {stt.median(gaps[k]):.2f} over {len(gaps[k])} runs")
    return res


def a3_stayed(runs):
    print("\n== 3. If they had stayed (13-week stay replay at each leave) ==")
    out = defaultdict(list)
    for key, t in runs.items():
        why = {}
        for d in t.get("decision", []):
            if d["chosen"] is not None and d["cands"][d["chosen"]]["a"] == "leave":
                why[(d["w"], d["r"])] = d["cands"][d["chosen"]].get("why", "distress")
        for x in t.get("replay", []):
            if x["kind"] != "stay":
                continue
            r, o = x["r"], "B" if x["r"] == "A" else "A"
            out[(fam_of(key), why.get((x["w"], r), "?"))].append((x["diff"][r]["net"], x["diff"][o]["net"], x["alt"]["exits"], x["faithful"]))
    for k in sorted(out):
        xs = out[k]
        lv = [a for a, _, _, _ in xs if a is not None]
        pt = [b for _, b, _, _ in xs if b is not None]
        still = sum(1 for *_, ex, _ in xs if not ex)
        print(f"  {k[0]:7s} leave on {k[1]:9s} n={len(xs):3d}: leaver net if stayed {stt.mean(lv):+.3f} (median {stt.median(lv):+.3f}, "
              f"better for {sum(1 for v in lv if v > 0)}/{len(lv)}); partner {stt.mean(pt):+.3f} (better for "
              f"{sum(1 for v in pt if v > 0)}/{len(pt)}); no leave in the window {still}/{len(xs)}; faithful {sum(1 for *_, f in xs if f)}/{len(xs)}")
    return out


def storage(m):
    print("\n== storage ==")
    by = defaultdict(list)
    for e in m["runs"]:
        by[e["family"] + " " + e["arm"]].append(e)
    for k, es in sorted(by.items()):
        print(f"  {k:7s} n={len(es)}: {stt.mean(e['bytes'] for e in es) / 1e3:.0f} kB a run (gzipped JSONL), "
              f"{stt.mean(sum(e['rows'].values()) for e in es):.0f} rows, {stt.mean(e['secs'] for e in es):.1f} s")
    rows = Counter()
    for e in m["runs"]:
        rows.update(e["rows"])
    print("  rows a run by table: " + ", ".join(f"{k} {v / len(m['runs']):.0f}" for k, v in rows.most_common()))
    print(f"  total {m['total_bytes'] / 1e6:.2f} MB for {len(m['runs'])} runs")


def analyze():
    m, runs = load()
    storage(m)
    a1_tipping(runs)
    a2_evening(runs)
    a3_stayed(runs)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--time", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.run:
        run()
    if a.time:
        time_cmp()
    if a.analyze:
        analyze()
