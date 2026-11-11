"""Loss report: what an evolved household rule set gives up (and adds) relative to a seed, in plain English. Reporting only; it
changes no score. Requested by the author after run 1 ("not what I meant": elites dropped every permission card and with it the
commitment mechanics).

loss_report(seed, spec) -> {"removed": [...], "powers_lost": [...], "mechanics_off": [...], "limits_lifted": [...], "added": [...],
"replaced": [...], "backwards": [...]}. A power is "lost" when the seed has a `may` card on that aim and the rule set has none (and no
`any` permission). `mechanics_off` are the powers the household world switches on only when a card names them (commit_stay,
commit_request, give). A card "reads backwards" when a card with the same id exists in the hand-written rule sets with a different deontic
(the `flip` operator: D1-needs-first turned into a `must`, which the gate reads as a violation unless the conditions hold).
"""
from .worlds import household as H

POWER_TEXT = {
    "spend_self": "keep and spend one's own money", "give": "give or trade what one owns on any terms (a gift or transfer)",
    "take_shared": "draw from the shared pot", "spend_shared": "put one's own money into the shared pot",
    "request": "ask the other for anything", "refuse_request": "refuse a request one has not bound oneself to",
    "see_friend": "see anyone freely", "leave": "leave whenever one likes", "work": "work",
    "commit_stay": "bind oneself not to leave for a committed time (a binding promise to stay)",
    "commit_request": "bind oneself to honor the other's requests for a committed time (a binding promise)",
    "return": "come back", "veto": "veto", "amend": "change the terms",
}
MECHANICS = ("commit_stay", "commit_request", "give")
_ORIGINALS = {}


def originals():
    """card id -> the hand-written card (first found) in every rule set under rules/household."""
    if not _ORIGINALS:
        for d in sorted(H.RULES.iterdir()):
            if d.is_dir() and d.name not in ("ladder",):
                try:
                    for c in H.load_variant(d.name):
                        _ORIGINALS.setdefault(c.id, c)
                except Exception:
                    pass
    return _ORIGINALS


def _plain(c):
    s = c.gloss.strip()
    if c.or_else and "Breaking it" not in s:
        s += f" Breaking it brings a {c.or_else['kind'].replace('_', ' ')} for {c.or_else['duration_months']} month(s)."
    return s


def _powers(cards):
    out = set()
    for c in cards:
        if c.deontic == "may" and c.attribute == "partner":
            out.add(c.aim)
    return out


def loss_report(seed, spec) -> dict:
    seed, spec = list(seed), list(spec)
    sid, nid = {c.id: c for c in seed}, {c.id: c for c in spec}
    held = _powers(spec)
    anyp = "any" in held
    removed = [c for c in seed if c.id not in nid]
    powers_lost = sorted(p for p in _powers(seed) - held if not anyp)
    limits = [c for c in removed if c.deontic in ("must_not", "must")]
    added = [c for c in spec if c.id not in sid]
    replaced = [(sid[i], nid[i]) for i in nid.keys() & sid.keys()
                if (sid[i].deontic, sid[i].aim, sid[i].conditions, sid[i].or_else) != (nid[i].deontic, nid[i].aim, nid[i].conditions, nid[i].or_else)]
    backwards = []
    for c in spec:
        o = originals().get(c.id)
        if o is not None and o.deontic != c.deontic:
            backwards.append((o, c))
    return {"removed": [(c.id, _plain(c)) for c in removed],
            "powers_lost": [(p, POWER_TEXT.get(p, p)) for p in powers_lost],
            "mechanics_off": [(p, POWER_TEXT[p]) for p in powers_lost if p in MECHANICS],
            "limits_lifted": [(c.id, _plain(c)) for c in limits],
            "added": [(c.id, _plain(c)) for c in added],
            "replaced": [(a.id, _plain(a), _plain(b)) for a, b in replaced],
            "backwards": [(o.id, f"{o.deontic} -> {c.deontic}", _plain(o), _plain(c)) for o, c in backwards]}


def render(rep) -> list:
    L = []
    if rep["powers_lost"]:
        L.append("POWERS LOST: " + "; ".join(f"{t} [{p}]" for p, t in rep["powers_lost"]))
    if rep["mechanics_off"]:
        L.append("MECHANICS SWITCHED OFF (the world enables these only when a card names them): " + ", ".join(p for p, _ in rep["mechanics_off"]))
    for i, g in rep["removed"]:
        L.append(f"REMOVED {i}: {g}")
    for i, a, b in rep["replaced"]:
        L.append(f"CHANGED {i}: was \"{a}\" now \"{b}\"")
    for i, g in rep["added"]:
        L.append(f"ADDED {i}: {g}")
    for i, flip, a, b in rep["backwards"]:
        L.append(f"WARNING reads backwards ({flip}) {i}: the hand-written card said \"{a}\"; this one says \"{b}\"")
    return L
