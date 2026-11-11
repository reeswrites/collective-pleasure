"""Pleasure demonstration instrument and report (docs/results/pleasure-demo-prereg.md).

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's
assigned preferences (docs/decisions/0010-hedonic-model.md). Everything here only READS the household world and the hedonic model;
neither is modified.

What this module does
- Instrument: `RecHedonic` is a subclass whose `close_week` recomputes, from the same state the model uses, the terms that add up to the
  week's pleasure flow (needs met, aspirations satisfied, time-together events, the glow of a new connection), then calls the model's own
  `close_week`. The recomputed total must equal the model's number (checked to 3e-4, counted in `max_err`). Terms are rescaled by the
  model's clip to [0, 1] so they add up to the realised pleasure. The model does not expose these terms; this is how they are read.
- Decomposition: each source is labelled individual or relational (SOURCE_GROUP). `connection` is the need clock fed by living with a
  partner, time together, friends and friend-initiated contact; it is labelled relational because every input to it is contact.
- Spiral classification: the oracle's own (`household_oracle.spiral_class`), lifted to the household: up (both partners up), down (any
  partner down), stalled (otherwise).
- Report: a self-contained HTML page (light/dark, phone width) built from per-run records, with vignettes generated from the traced
  events of actual runs.
"""
from __future__ import annotations

import html
import statistics

from . import hedonic as HD

# ---- sources -------------------------------------------------------------------------------------------------------------------

SOURCES = ("need:rest", "need:money", "need:security", "asp:security_buffer", "asp:savings_per_week", "asp:autonomy",
           "need:connection", "asp:together_per_week", "event:together", "asp:friends_per_week", "event:new_connection")
SOURCE_GROUP = {"need:rest": "individual", "need:money": "individual", "need:security": "individual",
                "asp:security_buffer": "individual", "asp:savings_per_week": "individual", "asp:autonomy": "individual",
                "need:connection": "connection", "asp:together_per_week": "time", "event:together": "time",
                "asp:friends_per_week": "social", "event:new_connection": "social"}
SUBGROUPS = ("individual", "time", "connection", "social")        # weekly series kept per run
RELATIONAL = ("time", "connection", "social")
CATEGORY = {"need:rest": "rest", "need:money": "money", "asp:savings_per_week": "money", "need:security": "security",
            "asp:security_buffer": "security", "asp:autonomy": "autonomy", "asp:together_per_week": "time together",
            "event:together": "time together", "need:connection": "connection", "asp:friends_per_week": "friends",
            "event:new_connection": "new connections"}
CATEGORIES = ("rest", "money", "security", "autonomy", "time together", "connection", "friends", "new connections")
CATEGORY_RELATIONAL = {c: c in ("time together", "connection", "friends", "new connections") for c in CATEGORIES}
SOURCE_TEXT = {"need:rest": "rest", "need:money": "money in hand", "need:security": "a sense of security",
               "asp:security_buffer": "a security buffer", "asp:savings_per_week": "saving", "asp:autonomy": "freedom of action",
               "need:connection": "connection", "asp:together_per_week": "time together (aspiration)",
               "event:together": "time together (events)", "asp:friends_per_week": "seeing friends",
               "event:new_connection": "a new connection"}


class RecHedonic(HD.Hedonic):
    """The hedonic model with the pleasure terms recorded each week (read-only: the numbers are the model's)."""

    def close_week(self, aspiration_values, **kw):
        c, L = self.cfg, self.level
        parts = {}
        for n in HD.NEEDS:
            parts["need:" + n] = c.w_need * self.sal[n] * HD._clip((L[n] - 0.5) / 0.5)
        for k in self.targets:
            parts["asp:" + k] = c.w_aspiration * self.asp_w[k] * self.satisfaction(k, aspiration_values.get(k, 0.0))
        parts["event:together"] = c.together_event * kw.get("together_sessions", 0)
        parts["event:new_connection"] = self.glow
        raw = sum(parts.values())
        row = super().close_week(aspiration_values, **kw)
        scale = row["pleasure"] / raw if raw > 1e-12 else 0.0
        err = abs(min(1.0, max(0.0, raw)) - row["pleasure"])
        self.max_err = max(getattr(self, "max_err", 0.0), err)
        self.terms.append({k: round(v * scale, 5) for k, v in parts.items()})
        return row


def record_week(world, w):
    """world.hook (called at the start of each week): the shared pot, trust each way and who is living together."""
    world.pd_log.append((w, round(world.pool, 2), world.trust["A"], world.trust["B"], int(world.p["A"]["in"] and world.p["B"]["in"])))


def instrument(world):
    """Swap each member's hedonic state for the recording subclass and log the pot and trust weekly. Call right after the world is built.
    The world's own results do not change."""
    for r in "AB":
        h = world.hed[r]
        h.__class__ = RecHedonic
        h.terms = []
    world.pd_log = []
    world.hook = record_week
    return world


def week_groups(term):
    out = {g: 0.0 for g in SUBGROUPS}
    for k, v in term.items():
        out[SOURCE_GROUP[k]] += v
    return out


# ---- per-run record --------------------------------------------------------------------------------------------------------------

def spiral_label(cls):
    """Household label from the two partners' classes: up (both), down (either), stalled (otherwise)."""
    v = list(cls.values())
    if all(c == "up" for c in v):
        return "up"
    if any(c == "down" for c in v):
        return "down"
    return "stalled"


def source_means(world):
    """Mean contribution of each source to a partner-week's pleasure (over weeks and both partners)."""
    n = len(world.hed["A"].terms) * 2
    return {k: round(sum(t[k] for r in "AB" for t in world.hed[r].terms if k in t) / n, 5) for k in SOURCES}


def relational_share(src):
    tot = sum(src.values())
    return sum(v for k, v in src.items() if SOURCE_GROUP[k] in RELATIONAL) / tot if tot > 0 else 0.0


def household_record(world, run, *, keep_events=True):
    """Compact per-run record from an instrumented, finished world (see the keys used by the report and the demo script)."""
    from . import household_oracle as oracle
    out = run.outcomes
    hs = oracle.hedonic_summary(out)
    rec = {"class": hs["class"], "pairing_up": hs["pairing_up"], "fail": hs["fail"], "pleasure": hs["pleasure"], "s_off": hs["s_off"],
           "s_non": hs["s_non"], "up": spiral_label(hs["class"]),
           "src": source_means(world), "max_err": max(world.hed[r].max_err if hasattr(world.hed[r], "max_err") else 0.0 for r in "AB"),
           "pl": {r: [round(o["hedonic"][r]["pleasure"], 3) for o in out] for r in "AB"},
           "B_end": {r: out[-1]["hedonic"][r]["B"] for r in "AB"},
           "together_weeks": sum(x[4] for x in world.pd_log), "weeks": len(out),
           "trust_min": min(min(x[2], x[3]) for x in world.pd_log), "trust_mean": statistics.fmean((x[2] + x[3]) / 2 for x in world.pd_log),
           "trust_end": [world.trust["A"], world.trust["B"]], "pool_end": world.pool}
    rec["rel_share"] = relational_share(rec["src"])
    if keep_events:
        rec["grp"] = {r: {g: [round(week_groups(t)[g], 3) for t in world.hed[r].terms] for g in SUBGROUPS} for r in "AB"}
        rec["pool"] = [x[1] for x in world.pd_log]
        rec["trust"] = [[x[2] for x in world.pd_log], [x[3] for x in world.pd_log]]
        rec["ev"] = [[t["week"], t["role"], t["action"], t.get("kind")] for t in run.trace if t["executed"]]
        rec["blocked"] = [[t["week"], t["role"], t["action"], (t["reasons"] or [""])[0]] for t in run.trace if not t["executed"]]
        rec["shocks"] = [[s["week"], s["role"], s["kind"]] for o in out for s in o["shocks"]]
        rec["trust_log"] = [list(x) for x in world.trust_log]
        rec["gifts"] = dict(world.gifts)
        rec["commits"] = world.commit_report() if world.mech else None
    return rec


# ---- plain English -------------------------------------------------------------------------------------------------------------

def label_of(pid):
    return pid.removeprefix("p-").replace("-", " ").capitalize()


def terms_english(b):
    """A negotiated bundle in plain English, from its term values."""
    if not b:
        return "no agreement"
    use = {"any_use": "either may draw on the one shared pot for anything", "needs_only": "the pot is for shared needs only",
           "caps": "the pot has spending caps"}[b["use"]]
    con = {"none": "nobody has to put money in", "fixed": "each puts in a fixed amount", "proportional": "each puts in in proportion to income"}[b["contribution"]]
    tk = {"allowed": "taking from it is allowed", "forbidden": "taking from it is forbidden", "repay": "taking is allowed if repaid"}[b["taking"]]
    parts = [use, con, tk]
    if b.get("stay"):
        parts.append(f"each is committed to stay {b['stay']} weeks")
    if b.get("requests") == "mutual":
        parts.append("each committed to honor the other's stay-home requests")
    parts.append({"unanimous": "changes need both to agree", "propose_accept": "changes need a proposal and acceptance", "frozen": "the terms cannot change"}[b["change"]])
    parts.append({"equal_split": "an equal split if one leaves", "proportional": "a split in proportion to what each put in",
                  "forfeit": "the leaver forfeits the share"}[b["exit"]])
    return "; ".join(parts)


def _spans(weeks):
    return ", ".join(str(w) for w in weeks) if weeks else "none"


def month_stats(rec, m):
    """Events and numbers of aligned 4-week month m (weeks 4m..4m+3), read from the traced run."""
    lo, hi = 4 * m, 4 * m + 3
    ev = [e for e in rec["ev"] if lo <= e[0] <= hi]
    mean = lambda xs: sum(xs) / len(xs) if xs else 0.0
    pl = {r: mean(rec["pl"][r][lo:hi + 1]) for r in "AB"}
    grp = {g: mean([rec["grp"][r][g][w] for r in "AB" for w in range(lo, hi + 1)]) for g in SUBGROUPS}
    tot = sum(grp.values()) or 1.0
    return {"lo": lo, "hi": hi, "ev": ev, "pl": pl, "mean": mean(list(pl.values())),
            "rel_share": sum(grp[g] for g in RELATIONAL) / tot, "grp": grp,
            "together": sorted({e[0] for e in ev if e[2] == "together"}), "n_together": sum(1 for e in ev if e[2] == "together")}


def month_score(rec, m):
    s = month_stats(rec, m)
    return s["mean"] + 0.004 * len(s["ev"]) + 0.01 * s["n_together"]


def best_month(rec, first=6):
    return max(range(first, rec["weeks"] // 4), key=lambda m: month_score(rec, m))


def worst_month(rec, first=6):
    return min(range(first, rec["weeks"] // 4), key=lambda m: month_stats(rec, m)["mean"])


def _count(ev, role, action, kind=None):
    return [e[0] for e in ev if e[1] == role and e[2] == action and (kind is None or e[3] == kind)]


def narrate_month(rec, m, names, variant_text, mood="good"):
    """Plain-English account of one month from the traced events: who did what, what was honored, the pot, how pleasure moved."""
    s = month_stats(rec, m)
    lo, hi = s["lo"], s["hi"]
    A, B = names["A"], names["B"]
    lines = []
    tw = s["together"]
    lines.append(f"They spent time together {len(tw)} time{'s' if len(tw) != 1 else ''} (weeks {_spans(tw)})." if tw else "They did not spend any dedicated time together.")
    for r, nm in (("A", A), ("B", B)):
        fr = _count(s["ev"], r, "see_friend")
        asks = [(e[0], e[3]) for e in s["ev"] if e[1] == r and e[2] == "request"]
        gives = _count(s["ev"], r, "give", "partner")
        takes = _count(s["ev"], r, "take_shared")
        spend = _count(s["ev"], r, "spend_shared")
        bits = []
        if fr:
            bits.append(f"saw a friend {len(fr)} time{'s' if len(fr) != 1 else ''}")
        for wk, kind in asks:
            bits.append(f"asked for {str(kind).replace('_', ' ')} in week {wk}")
        if gives:
            bits.append(f"gave {names['B' if r == 'A' else 'A']} a gift in week{'s' if len(gives) > 1 else ''} {_spans(gives)}")
        if takes:
            bits.append(f"drew on the shared pot {len(takes)} time{'s' if len(takes) != 1 else ''}")
        if spend:
            bits.append(f"put own money toward the shared bills {len(spend)} time{'s' if len(spend) != 1 else ''}")
        if bits:
            lines.append(f"{nm} " + ", ".join(bits) + ".")
    honored = [b for b in rec["blocked"] if lo <= b[0] <= hi and str(b[3]).startswith("commitment")]
    for wk, rl, act, why in honored[:3]:
        lines.append(f"In week {wk}, {names[rl]} wanted to {act.replace('_', ' ')} but was held to the {why.replace('commitment: ', 'commitment to ')} they had chosen, and honored it.")
    for c in [c for c in (rec.get("commits") or {}).get("log", []) if c["from"] <= hi and c["until"] > lo]:
        what = "stay" if c["kind"] == "stay" else f"honor {names[c['to']]}'s stay-home requests"
        lines.append(f"{names[c['by']]} was under a chosen commitment to {what} (weeks {c['from']} to {min(c['until'], rec['weeks'])}); " + ("it had been broken." if c["breached"] else "it stood unbroken."))
    ho = [x for x in rec["trust_log"] if lo <= x[0] <= hi and x[2] == "honored"]
    for wk, rl, why, val in ho:
        lines.append(f"In week {wk} a bound request ran its four weeks unbroken, so {names[rl]}'s trust in {names['B' if rl == 'A' else 'A']} rose to {val:.2f}.")
    br = [x for x in rec["trust_log"] if lo <= x[0] <= hi and x[2] == "breach"]
    for wk, rl, why, val in br:
        lines.append(f"In week {wk} {names['B' if rl == 'A' else 'A']} broke a commitment; {names[rl]}'s trust fell to {val:.2f}.")
    for wk, rl, kind in [x for x in rec["shocks"] if lo <= x[0] <= hi]:
        lines.append({"new_connection": f"A new connection came into {names[rl]}'s life in week {wk}.",
                      "job_loss": f"{names[rl]} lost a job in week {wk} (a shock from outside the household).",
                      "illness": f"{names[rl]} fell ill in week {wk}.", "move": f"The household had to move in week {wk}."}.get(kind, f"A {kind} shock hit in week {wk}."))
    p0, p1 = rec["pool"][lo], rec["pool"][min(hi + 1, len(rec["pool"]) - 1)]
    t0 = [rec["trust"][i][lo] for i in (0, 1)]
    t1 = [rec["trust"][i][hi] for i in (0, 1)]
    lines.append(f"The shared pot (where the shared bills are settled from) went from {p0:.0f} to {p1:.0f}. Trust: {A} in {B} {t0[0]:.2f} to {t1[0]:.2f}, {B} in {A} {t0[1]:.2f} to {t1[1]:.2f}.")
    prev = {r: (rec["pl"][r][lo - 1] if lo else rec["pl"][r][lo]) for r in "AB"}
    last = {r: rec["pl"][r][hi] for r in "AB"}
    lines.append(f"Modeled pleasure (0 to 1): {A} {prev['A']:.2f} the week before, {last['A']:.2f} at month end (mean {s['pl']['A']:.2f}); "
                 f"{B} {prev['B']:.2f} then {last['B']:.2f} (mean {s['pl']['B']:.2f}). About {s['rel_share'] * 100:.0f}% of it came from relational sources "
                 f"(time together, connection, friends, new connections), the rest from individual needs and aspirations.")
    head = f"{A} and {B}, seed {rec['seed']}, {variant_text}. Weeks {lo} to {hi} (month {m + 1} of {rec['weeks'] // 4})."
    return {"title": head, "terms": terms_english(rec.get("bundle")), "lines": lines, "month": m, "mood": mood,
            "pairing": f"{rec['a']}+{rec['b']}", "pleasure": s["mean"], "rel_share": s["rel_share"]}


def vignettes(rows, n_good=3):
    """Three good-month vignettes for the best seed v2.2 households (distinct pairings, both partners upward, still together) and one
    honest vignette of a downward household (worst by end position). -> list of narrate_month dicts."""
    v22 = [r for r in rows if r["arm"].startswith("v22") and "ev" in r]
    good = sorted((r for r in v22 if r["up"] == "up" and r["kind"] == "agreed" and r["together_weeks"] >= 0.9 * r["weeks"]),
                  key=lambda r: -(r["pleasure"] + 0.3 * r["rel_share"] + (0.15 if (r["commits"] or {}).get("made") else 0.0)))
    picked, seen = [], set()
    for r in good:
        key = (r["a"], r["b"])
        if key in seen:
            continue
        seen.add(key)
        picked.append(r)
        if len(picked) == n_good:
            break
    out = []
    for r in picked:
        names = {"A": label_of(r["a"]), "B": label_of(r["b"])}
        out.append(narrate_month(r, best_month(r), names, VARIANT_TEXT[r["arm"]], "good"))
    down = sorted((r for r in v22 if r["up"] == "down"), key=lambda r: min(r["B_end"].values()))
    if down:
        r = down[0]
        names = {"A": label_of(r["a"]), "B": label_of(r["b"])}
        v = narrate_month(r, worst_month(r), names, VARIANT_TEXT[r["arm"]], "down")
        q = lambda lo, hi: statistics.fmean(r["pl"][x][i] for x in "AB" for i in range(lo, hi))
        draws = {x: sum(1 for e in r["ev"] if e[1] == x and e[2] == "take_shared") for x in "AB"}
        zero = next((i for i, v0 in enumerate(r["pool"]) if v0 <= 0), None)
        v["lines"].append(f"Over the run {names['A']} drew on the shared pot {draws['A']} times and {names['B']} {draws['B']} times"
                          + (f"; the pot first hit zero in week {zero}." if zero is not None else "; it never ran out."))
        v["lines"].append(f"Over the whole run their mean pleasure was {r['pleasure']:.2f}: {q(0, 39):.2f} in the first quarter and {q(117, 156):.2f} in the last. "
                          f"Final classes: {names['A']} {r['class']['A']}, {names['B']} {r['class']['B']}.")
        out.append(v)
    return out


VARIANT_TEXT = {"v22_bindable": "seed v2.2 (bindable: a negotiated commitment can bind a partner to stay)",
                "v22_free_exit": "seed v2.2 (free exit: leaving can never be signed away)",
                "baseline": "the imposed baseline rule set", "trap": "the imposed trap rule set"}
ARM_LABEL = {"v22_bindable": "seed v2.2 bindable", "v22_free_exit": "seed v2.2 free exit", "baseline": "baseline", "trap": "trap (control)"}
ARM_ORDER = ("v22_bindable", "v22_free_exit", "baseline", "trap")


# ---- the HTML report -----------------------------------------------------------------------------------------------------------

CSS = """
:root{--bg:#fbfaf7;--fg:#1d1c1a;--mut:#5d5a54;--card:#ffffff;--line:#dcd8cf;--c0:#2a6f97;--c1:#8a5a9e;--c2:#6b7280;--c3:#b45309;
--i0:#7a8aa0;--i1:#8fa5b8;--i2:#a3b8a0;--i3:#bfae8e;--r0:#d9622b;--r1:#e08e3a;--r2:#c2456a;--r3:#9b3fb0;--up:#2f8f5b;--st:#c2a43a;--dn:#c0392b}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15161a;--fg:#ecebe6;--mut:#aaa79f;--card:#1e2026;--line:#3a3d46;--c0:#6bb3dd;--c1:#c39ad6;--c2:#9aa1ad;--c3:#e8a45a;
--i0:#8c9bb3;--i1:#7f96ab;--i2:#8fae8c;--i3:#b3a27f;--r0:#f0804a;--r1:#f0a75c;--r2:#e66f94;--r3:#c982dd;--up:#4cc183;--st:#e0c35a;--dn:#ee6a5a}}
:root[data-theme="dark"]{--bg:#15161a;--fg:#ecebe6;--mut:#aaa79f;--card:#1e2026;--line:#3a3d46;--c0:#6bb3dd;--c1:#c39ad6;--c2:#9aa1ad;--c3:#e8a45a;
--i0:#8c9bb3;--i1:#7f96ab;--i2:#8fae8c;--i3:#b3a27f;--r0:#f0804a;--r1:#f0a75c;--r2:#e66f94;--r3:#c982dd;--up:#4cc183;--st:#e0c35a;--dn:#ee6a5a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:980px;margin:0 auto;padding:20px 16px 60px}h1{font-size:1.6rem;margin:.2em 0}h2{font-size:1.2rem;margin:1.8em 0 .4em;border-top:1px solid var(--line);padding-top:1em}
p,li{max-width:70ch}.mut{color:var(--mut);font-size:.92rem}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:10px 0}
svg{width:100%;height:auto;display:block}table{border-collapse:collapse;width:100%;font-size:.9rem}td,th{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}.tile{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:6px}
.tile b{font-size:.72rem;font-weight:600;display:block;line-height:1.2}.leg span{display:inline-block;margin-right:12px;font-size:.85rem;white-space:nowrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:4px;vertical-align:-1px}.vig li{margin:.25em 0}.vig .t{font-weight:600}
.dn{border-left:4px solid var(--dn)}.gd{border-left:4px solid var(--up)}.wide{overflow-x:auto}
"""

ARM_COLOR = {"v22_bindable": "var(--c0)", "v22_free_exit": "var(--c1)", "baseline": "var(--c2)", "trap": "var(--c3)"}
CAT_COLOR = {"rest": "var(--i0)", "money": "var(--i1)", "security": "var(--i2)", "autonomy": "var(--i3)", "time together": "var(--r0)",
             "connection": "var(--r1)", "friends": "var(--r2)", "new connections": "var(--r3)"}
E = html.escape


def _mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def category_means(rows):
    """{category: mean contribution to pleasure per partner-week}."""
    out = {c: 0.0 for c in CATEGORIES}
    for r in rows:
        for k, v in r["src"].items():
            out[CATEGORY[k]] += v
    n = len(rows) or 1
    return {c: v / n for c, v in out.items()}


def spiral_shares(rows):
    n = len(rows) or 1
    return {k: sum(1 for r in rows if r["up"] == k) / n for k in ("up", "stalled", "down")}


def _legend():
    return '<p class="leg">' + "".join(f'<span><i class="sw" style="background:{CAT_COLOR[c]}"></i>{E(c)}</span>' for c in CATEGORIES) + "</p>"


def svg_stack(rows_by_arm):
    w, h, lab = 640, 24 * len(rows_by_arm) + 34, 150
    mx = max(sum(category_means(r).values()) for r in rows_by_arm.values()) or 1
    sc = (w - lab - 60) / mx
    parts = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Pleasure by source for each variant">']
    for i, (arm, rows) in enumerate(rows_by_arm.items()):
        y = 6 + 24 * i
        x = lab
        parts.append(f'<text x="0" y="{y + 14}" font-size="12" fill="currentColor">{E(ARM_LABEL[arm])}</text>')
        cm = category_means(rows)
        for c in CATEGORIES:
            ww = cm[c] * sc
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{max(ww, 0):.1f}" height="18" fill="{CAT_COLOR[c]}"><title>{E(c)}: {cm[c]:.3f}</title></rect>')
            x += ww
        parts.append(f'<text x="{x + 4:.1f}" y="{y + 14}" font-size="12" fill="currentColor">{sum(cm.values()):.3f}</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_spiral(rows_by_arm):
    w, h, lab = 640, 24 * len(rows_by_arm) + 8, 150
    sc = w - lab - 50
    cols = {"up": "var(--up)", "stalled": "var(--st)", "down": "var(--dn)"}
    parts = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Spiral shares">']
    for i, (arm, rows) in enumerate(rows_by_arm.items()):
        y = 4 + 24 * i
        sh = spiral_shares(rows)
        x = lab
        parts.append(f'<text x="0" y="{y + 14}" font-size="12" fill="currentColor">{E(ARM_LABEL[arm])}</text>')
        for k in ("up", "stalled", "down"):
            ww = sh[k] * sc
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{ww:.1f}" height="18" fill="{cols[k]}"><title>{k}: {sh[k]:.2f}</title></rect>')
            if sh[k] >= 0.08:
                parts.append(f'<text x="{x + ww / 2:.1f}" y="{y + 13}" font-size="11" text-anchor="middle" fill="#fff">{sh[k] * 100:.0f}%</text>')
            x += ww
    parts.append("</svg>")
    return "".join(parts)


def smooth(xs, k=13):
    return [_mean(xs[max(0, i - k + 1):i + 1]) for i in range(len(xs))]


def small_multiples(rows):
    by = {}
    for r in rows:
        by.setdefault((r["a"], r["b"]), {}).setdefault(r["arm"], []).append(r)
    tiles = []
    for (a, b), arms in sorted(by.items()):
        w, h = 150, 70
        ps = []
        for arm in ARM_ORDER:
            rs = arms.get(arm)
            if not rs:
                continue
            n = len(rs[0]["pl"]["A"])
            ser = smooth([_mean(_mean([r["pl"][x][i] for x in "AB"]) for r in rs) for i in range(n)])
            pts = " ".join(f"{i / (n - 1) * (w - 2) + 1:.1f},{(h - 3) - v * (h - 6):.1f}" for i, v in enumerate(ser) if i % 3 == 0 or i == n - 1)
            ps.append(f'<polyline points="{pts}" fill="none" stroke="{ARM_COLOR[arm]}" stroke-width="1.5"/>')
        tiles.append(f'<div class="tile"><b>{E(label_of(a))} + {E(label_of(b))}</b><svg viewBox="0 0 {w} {h}" role="img" '
                     f'aria-label="pleasure over time, {E(label_of(a))} and {E(label_of(b))}"><line x1="0" x2="{w}" y1="{h - 3}" y2="{h - 3}" stroke="var(--line)"/>{"".join(ps)}</svg></div>')
    return f'<div class="grid">{"".join(tiles)}</div>'


def svg_scatter(rows):
    w, h = 640, 300
    ml, mb = 40, 30
    pts = []
    xs = [r["trust_mean"] for r in rows]
    lo, hi = min(xs + [0.5]), max(xs + [0.8])
    lo = max(0.0, lo - 0.02)
    ys = [r["pleasure"] for r in rows]
    ylo, yhi = max(0.0, min(ys) - 0.02), min(1.0, max(ys) + 0.02)
    for r in rows:
        x = ml + (r["trust_mean"] - lo) / (hi - lo + 1e-9) * (w - ml - 10)
        y = (h - mb) - (r["pleasure"] - ylo) / (yhi - ylo + 1e-9) * (h - mb - 10)
        pts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{ARM_COLOR[r["arm"]]}" fill-opacity=".55"/>')
    ax = (f'<line x1="{ml}" x2="{w - 5}" y1="{h - mb}" y2="{h - mb}" stroke="var(--line)"/><line x1="{ml}" x2="{ml}" y1="5" y2="{h - mb}" stroke="var(--line)"/>'
          f'<text x="{w / 2}" y="{h - 6}" font-size="12" text-anchor="middle" fill="currentColor">mean trust over the run (assumed model)</text>'
          f'<text x="4" y="14" font-size="12" fill="currentColor">{yhi:.2f}</text><text x="4" y="{h - mb}" font-size="12" fill="currentColor">{ylo:.2f}</text>'
          f'<text x="{ml}" y="{h - mb + 14}" font-size="11" fill="currentColor">{lo:.2f}</text><text x="{w - 30}" y="{h - mb + 14}" font-size="11" fill="currentColor">{hi:.2f}</text>')
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Trust against pleasure, one dot per run">{ax}{"".join(pts)}</svg>'


def _vig_html(v):
    cls = "dn" if v["mood"] == "down" else "gd"
    items = "".join(f"<li>{E(x)}</li>" for x in v["lines"])
    return f'<div class="card vig {cls}"><p class="t">{E(v["title"])}</p><p class="mut">Terms: {E(v["terms"])}.</p><ul>{items}</ul></div>'


def build_report(rows, stats_rows=None, vigs=None, meta=None):
    """rows: per-run records (each with arm, a, b, seed, kind, plus household_record keys). -> HTML string."""
    by_arm = {a: [r for r in rows if r["arm"] == a] for a in ARM_ORDER if any(r["arm"] == a for r in rows)}
    v22 = [r for r in rows if r["arm"].startswith("v22")]
    vigs = vigs if vigs is not None else vignettes(rows)
    cm = {a: category_means(rs) for a, rs in by_arm.items()}
    rel = {a: sum(v for c, v in cm[a].items() if CATEGORY_RELATIONAL[c]) / (sum(cm[a].values()) or 1) for a in cm}
    head = "".join(f"<tr><td>{E(ARM_LABEL[a])}</td><td>{len(rs)}</td><td>{_mean(r['pleasure'] for r in rs):.3f}</td>"
                   f"<td>{spiral_shares(rs)['up'] * 100:.0f}% / {spiral_shares(rs)['stalled'] * 100:.0f}% / {spiral_shares(rs)['down'] * 100:.0f}%</td><td>{rel[a] * 100:.0f}%</td></tr>"
                   for a, rs in by_arm.items())
    st = ""
    if stats_rows:
        st = ('<h2>Preregistered demonstration questions</h2><div class="wide"><table><tr><th>ID</th><th>Quantity</th><th>Estimate [95% CI]</th><th>Holm p</th><th>Verdict</th></tr>'
              + "".join(f"<tr><td>{E(str(x['id']))}</td><td>{E(str(x['quantity']))}</td><td>{E(str(x['estimate']))}</td><td>{E(str(x['p']))}</td><td>{E(str(x['verdict']))}</td></tr>" for x in stats_rows)
              + "</table></div>")
    good = [v for v in vigs if v["mood"] == "good"]
    down = [v for v in vigs if v["mood"] == "down"]
    sub = (meta or {}).get("subtitle", "")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pleasure demo</title><style>{CSS}</style></head><body><main>
<h1>Does seed v2.2 produce pleasure in relationships?</h1>
<p class="mut">Modeled pleasure, not felt pleasure: agents feel nothing; "pleasure" is a gloss on a modeled hedonic state derived from assigned persona preferences. Scripted agents, assumed parameters (trust included). {E(sub)}</p>
<div class="wide"><table><tr><th>Variant</th><th>Runs</th><th>Mean pleasure</th><th>Households up / stalled / down</th><th>Relational share of pleasure</th></tr>{head}</table></div>
{st}
<h2>Where the pleasure comes from</h2><p class="mut">Mean contribution of each source to a partner-week of pleasure (0 to 1 scale). Cool colors are individual needs and aspirations; warm colors are relational (time together, connection, friends, new connections).</p>{_legend()}{svg_stack(by_arm)}
<h2>Upward and downward spirals</h2><p class="mut">A household is up when both partners end in the upward spiral, down when either ends in the downward one.</p>{svg_spiral(by_arm)}
<h2>Trust and pleasure</h2><p class="mut">One dot per seed v2.2 run. Trust is an assumed model variable; this is a description, not a cause.</p>{svg_scatter(v22)}
<p class="leg">{''.join(f'<span><i class="sw" style="background:{ARM_COLOR[a]}"></i>{E(ARM_LABEL[a])}</span>' for a in ("v22_bindable", "v22_free_exit") if a in by_arm)}</p>
<h2>A good month</h2><p class="mut">Written from the traced events of high-pleasure seed v2.2 households (both partners upward, living together), ranked by pleasure with a preference for households that negotiated commitments so that honored commitments can be shown. They are the best cases, not typical ones: most agreed households negotiate no commitments. Months are 4-week blocks.</p>{''.join(_vig_html(v) for v in good)}
<h2>An honest downward household</h2>{''.join(_vig_html(v) for v in down) or '<p class="mut">No seed v2.2 household ended downward.</p>'}
<h2>Pleasure over time, every pairing</h2><p class="mut">13-week running mean of both partners' pleasure, averaged over seeds. {''.join(f'<span class="mut"><i class="sw" style="background:{ARM_COLOR[a]}"></i>{E(ARM_LABEL[a])} </span>' for a in by_arm)}</p>{small_multiples(rows)}
</main></body></html>"""
