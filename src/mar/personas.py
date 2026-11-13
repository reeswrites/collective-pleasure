"""Personas for the household world. Two layers, one file each (personas/<id>.yaml).

Story layer: three principles and a short backstory, in natural language. LLM agents play this.
Profile layer: typed fields (five weights in [0,1], a negotiation style, risk tolerance). Jev agents
and analysis read this. Axis positions sit between the layers: each is in [0,1] and says where the
persona sits between two poles (0 is the first pole, 1 is the second).

Guardrails (CONTRIBUTING.md, dual-use): principles and histories only. Never gender, race, religion,
nationality or other group identities. No real people. validate() rejects persona text that uses a
blocklisted word. The blocklist is small and explicit on purpose. Extend it with extend_blocklist().
It is a tripwire, not a proof: a human still reads every persona.

The axis-to-weight mapping in profile_from_axes is ASSUMED. It is a starting guess, not a finding.
"""
import re
from dataclasses import dataclass, field, replace, asdict
from itertools import product
from pathlib import Path

import yaml

# (name, pole at position 0, pole at position 1)
AXES = {
    "certainty_openness": ("certainty", "openness"),
    "togetherness_independence": ("togetherness", "independence"),
    "security_adventure": ("security", "adventure"),
    "giving_keeping": ("giving", "keeping"),
    "directness_avoidance": ("directness", "avoidance"),
}
WEIGHT_KEYS = ("security", "autonomy", "togetherness", "money", "other_connections")
NEED_KEYS = ("rest", "connection", "money", "security")
ASPIRATION_KEYS = ("security_buffer", "together_per_week", "friends_per_week", "savings_per_week", "autonomy")
STYLES = ("direct", "accommodating", "avoidant", "competitive", "collaborative")
SOURCES = ("grid", "hand", "generated")
TODO = "TODO"

# Group-identity terms. Whole-word, case-insensitive. Extend with extend_blocklist().
BLOCKLIST = {
    "gender", "male", "female", "man", "men", "woman", "women", "boy", "girl", "gay", "lesbian",
    "transgender", "trans", "nonbinary", "race", "racial", "ethnic", "ethnicity", "black", "white",
    "asian", "latino", "latina", "hispanic", "african", "european", "indian", "chinese", "mexican",
    "american", "religion", "religious", "christian", "muslim", "jewish", "hindu", "buddhist",
    "catholic", "atheist", "nationality", "immigrant", "caste", "disabled",
}


def extend_blocklist(*words):
    BLOCKLIST.update(w.lower() for w in words)


class PersonaError(ValueError):
    pass


@dataclass
class Persona:
    id: str
    label: str
    axes: dict
    principles: list
    backstory: str
    weights: dict
    negotiation_style: str
    risk_tolerance: float
    tags: list = field(default_factory=list)
    source: str = "hand"
    version: int = 1
    parent: str = ""        # id of the persona this was varied from, if any
    varied: str = ""        # what changed, e.g. "weights.security=0.9"
    needs: dict = field(default_factory=dict)         # salience in [0,1] of each need clock (hedonic model)
    aspirations: dict = field(default_factory=dict)   # targets; their weights are the persona's weights
    forecast: dict = field(default_factory=dict)      # hybrid agent only (mar.hybrid): optional big-choice forecast traits
    #                                                   {"horizon": weeks, "discount": per week, "outside_bias": added to the outside option}; empty = neutral

    def __post_init__(self):
        """Missing needs or aspirations take the ASSUMED defaults from the weights (older files stay valid)."""
        if not self.needs and isinstance(self.weights, dict) and set(self.weights) == set(WEIGHT_KEYS):
            self.needs = needs_from_weights(self.weights)
        if not self.aspirations and isinstance(self.weights, dict) and set(self.weights) == set(WEIGHT_KEYS):
            self.aspirations = aspirations_from_weights(self.weights)


def _r(x):
    return round(max(0.0, min(1.0, x)), 2)


def needs_from_weights(w):
    """ASSUMED: salience of the four need clocks (rest, connection, money, security), docs/decisions/0010.
      rest 0.5 for everyone; connection 0.3 + 0.4 togetherness + 0.3 other_connections;
      money 0.3 + 0.5 money; security = security weight (floored at 0.1)."""
    return {"rest": 0.5, "connection": _r(0.3 + 0.4 * w["togetherness"] + 0.3 * w["other_connections"]),
            "money": _r(0.3 + 0.5 * w["money"]), "security": _r(max(0.1, w["security"]))}


def aspirations_from_weights(w):
    """ASSUMED targets, one per weight. The persona's weight for that value is the aspiration's importance.
      security_buffer: target security level (0.4 + 0.5 security); together_per_week: 1.5 x togetherness
      sessions; friends_per_week: 1.5 x other_connections visits; savings_per_week: 3 x money units;
      autonomy: share of own options kept open (1.0, importance = autonomy weight)."""
    return {"security_buffer": _r(0.4 + 0.5 * w["security"]), "together_per_week": round(1.5 * w["togetherness"], 2),
            "friends_per_week": round(1.5 * w["other_connections"], 2), "savings_per_week": round(3 * w["money"], 2),
            "autonomy": 1.0}


def profile_from_axes(axes):
    """ASSUMED mapping from axis positions to the profile layer. Documented in docs/results/personas.md.

    certainty_openness (co), togetherness_independence (ti), security_adventure (sa),
    giving_keeping (gk), directness_avoidance (da). All in [0,1]; 1 is the second pole.
      security          = 0.6 (1 - sa) + 0.4 (1 - co)
      autonomy          = 0.6 ti + 0.4 co
      togetherness      = 0.7 (1 - ti) + 0.3 (1 - gk)
      money             = 0.6 gk + 0.4 (1 - sa)
      other_connections = 0.6 ti + 0.4 sa
      risk_tolerance    = 0.7 sa + 0.3 co
      negotiation_style: da < 0.5 is direct-leaning, else avoidance-leaning; gk < 0.5 is giving.
        direct+giving collaborative, direct+keeping competitive,
        avoidant+giving accommodating, avoidant+keeping avoidant.
    """
    co, ti = axes["certainty_openness"], axes["togetherness_independence"]
    sa, gk, da = axes["security_adventure"], axes["giving_keeping"], axes["directness_avoidance"]
    weights = {
        "security": _r(0.6 * (1 - sa) + 0.4 * (1 - co)),
        "autonomy": _r(0.6 * ti + 0.4 * co),
        "togetherness": _r(0.7 * (1 - ti) + 0.3 * (1 - gk)),
        "money": _r(0.6 * gk + 0.4 * (1 - sa)),
        "other_connections": _r(0.6 * ti + 0.4 * sa),
    }
    if da < 0.5:
        style = "collaborative" if gk < 0.5 else "competitive"
    else:
        style = "accommodating" if gk < 0.5 else "avoidant"
    return weights, style, _r(0.7 * sa + 0.3 * co)


def grid(axes=None, levels=2):
    """Skeletons for every combination of axis levels (levels ** len(axes)). Story layer is TODO.
    Level positions are evenly spaced from 0.2 to 0.8 (ASSUMED); with 2 levels they are 0.2 and 0.8."""
    axes = axes or AXES
    pos = [0.5] if levels == 1 else [round(0.2 + 0.6 * i / (levels - 1), 2) for i in range(levels)]
    out = []
    for combo in product(range(levels), repeat=len(axes)):
        a = {name: pos[i] for name, i in zip(axes, combo)}
        weights, style, risk = profile_from_axes(a)
        pid = "g-" + "".join(str(i) for i in combo)
        poles = ", ".join(axes[n][0] if i < levels / 2 else axes[n][1] for n, i in zip(axes, combo))
        out.append(Persona(pid, f"Grid {poles}", a, [TODO] * 3, TODO, weights, style, risk,
                           tags=["grid"], source="grid", needs=needs_from_weights(weights),
                           aspirations=aspirations_from_weights(weights)))
    return out


def _text_fields(p):
    return [("label", p.label), ("backstory", p.backstory)] + [(f"principles[{i}]", t) for i, t in enumerate(p.principles)] + \
           [("tags", t) for t in p.tags]


def validate(p):
    """Raise PersonaError listing every problem. Returns p if clean."""
    errs = []
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*(--[a-z0-9._=-]+)*", p.id or ""):
        errs.append(f"bad id {p.id!r}")
    if p.source not in SOURCES:
        errs.append(f"source must be one of {SOURCES}")
    if not isinstance(p.version, int) or p.version < 1:
        errs.append("version must be a positive integer")
    if set(p.axes) != set(AXES):
        errs.append(f"axes must be exactly {sorted(AXES)}")
    elif not all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in p.axes.values()):
        errs.append("axis positions must be in [0,1]")
    if set(p.weights) != set(WEIGHT_KEYS):
        errs.append(f"weights must be exactly {list(WEIGHT_KEYS)}")
    elif not all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in p.weights.values()):
        errs.append("weights must be in [0,1]")
    if p.negotiation_style not in STYLES:
        errs.append(f"negotiation_style must be one of {STYLES}")
    if not isinstance(p.risk_tolerance, (int, float)) or not 0 <= p.risk_tolerance <= 1:
        errs.append("risk_tolerance must be in [0,1]")
    if not isinstance(p.tags, list):
        errs.append("tags must be a list")
    if not isinstance(p.needs, dict) or set(p.needs) != set(NEED_KEYS) or \
            not all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in p.needs.values()):
        errs.append(f"needs must be exactly {list(NEED_KEYS)} with values in [0,1]")
    if not isinstance(p.aspirations, dict) or set(p.aspirations) != set(ASPIRATION_KEYS) or \
            not all(isinstance(v, (int, float)) and v >= 0 for v in p.aspirations.values()):
        errs.append(f"aspirations must be exactly {list(ASPIRATION_KEYS)} with values >= 0")
    if not isinstance(p.principles, list) or len(p.principles) != 3 or not all(isinstance(t, str) and t.strip() for t in p.principles):
        errs.append("exactly 3 non-empty principles required")
    if not isinstance(p.backstory, str) or not p.backstory.strip():
        errs.append("backstory required")
    if p.source != "grid":
        if TODO in p.principles or p.backstory.strip() == TODO:
            errs.append("TODO placeholders are only allowed for grid skeletons")
        elif len(re.findall(r"[.!?](?:\s|$)", p.backstory)) > 4:
            errs.append("backstory should be short (at most 4 sentences)")
    if "—" in p.backstory or any("—" in t for t in p.principles if isinstance(t, str)):
        errs.append("no em-dashes")
    for where, text in _text_fields(p):
        if not isinstance(text, str):
            continue
        for w in re.findall(r"[a-z]+", text.lower()):
            if w in BLOCKLIST:
                errs.append(f"{where} uses group-identity term {w!r}")
    if errs:
        raise PersonaError(f"{p.id}: " + "; ".join(errs))
    return p


def save(p, directory="personas"):
    validate(p)
    path = Path(directory) / f"{p.id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(asdict(p), sort_keys=False, allow_unicode=True, width=100))
    return path


def load(path):
    d = yaml.safe_load(Path(path).read_text())
    try:
        p = Persona(**d)
    except TypeError as e:
        raise PersonaError(f"{path}: {e}")
    return validate(p)


def load_dir(directory="personas"):
    return [load(f) for f in sorted(Path(directory).glob("*.yaml"))]


def vary(p, fld, value):
    """One-field change for tunability. fld is 'weights.<key>', 'axes.<name>', 'principles.<i>',
    or a top-level field (negotiation_style, risk_tolerance, backstory, label). Returns a new
    validated Persona with id '<id>--<field>-<value>' and parent set. The original is untouched."""
    q = replace(p, axes=dict(p.axes), weights=dict(p.weights), principles=list(p.principles), tags=list(p.tags),
                needs=dict(p.needs), aspirations=dict(p.aspirations))
    if "." in fld:
        head, key = fld.split(".", 1)
        if head in ("weights", "axes"):
            d = getattr(q, head)
            if key not in d:
                raise PersonaError(f"no {head} key {key!r}")
            d[key] = value
        elif head == "principles":
            if not key.isdigit() or int(key) >= len(q.principles):
                raise PersonaError(f"bad principle index {key!r}")
            q.principles[int(key)] = value
        else:
            raise PersonaError(f"cannot vary {fld!r}")
    elif fld in ("negotiation_style", "risk_tolerance", "backstory", "label"):
        setattr(q, fld, value)
    else:
        raise PersonaError(f"cannot vary {fld!r}")
    if fld.startswith("weights."):   # derived goals follow the weights (ASSUMED mapping)
        q.needs, q.aspirations = needs_from_weights(q.weights), aspirations_from_weights(q.weights)
    slug = re.sub(r"[^a-z0-9._=-]+", "-", f"{fld}-{value}".lower())[:40].strip("-")
    q.id = f"{p.id}--{slug}"
    q.parent, q.varied = p.id, f"{fld}={value}"
    return validate(q)


def _band(x):
    return "very high" if x >= 0.8 else "high" if x >= 0.6 else "middling" if x >= 0.4 else "low" if x >= 0.2 else "very low"


def render(p):
    """Plain English, both layers."""
    lines = [f"{p.label} ({p.id}, {p.source}, version {p.version})."]
    lines.append("Principles: " + " ".join(f"{i}. {t}" for i, t in enumerate(p.principles, 1)))
    lines.append(f"Backstory: {p.backstory}")
    pos = []
    for name, v in p.axes.items():
        lo, hi = AXES[name]
        pos.append(f"{lo} {hi} {v:.2f}".replace(f"{lo} {hi}", f"between {lo} (0) and {hi} (1):"))
    lines.append("Leanings: " + "; ".join(pos) + ".")
    lines.append("Cares about: " + ", ".join(f"{k.replace('_', ' ')} {_band(v)} ({v:.2f})" for k, v in p.weights.items()) + ".")
    lines.append("Needs (salience): " + ", ".join(f"{k} {v:.2f}" for k, v in p.needs.items()) + ". Aspirations (targets): "
                 + ", ".join(f"{k.replace('_', ' ')} {v:g}" for k, v in p.aspirations.items()) + ".")
    lines.append(f"Negotiates in a {p.negotiation_style} way. Risk tolerance is {_band(p.risk_tolerance)} ({p.risk_tolerance:.2f}).")
    if p.tags:
        lines.append("Tags: " + ", ".join(p.tags) + ".")
    if p.parent:
        lines.append(f"Varied from {p.parent}: {p.varied}.")
    return "\n".join(lines)


# ---- negotiation stub (seed v2; docs/results/household-seed-v2-prereg.md). ASSUMED: a fixed function of the persona, no randomness ----
COMMIT_WEEKS = 52      # length of every commitment the stub proposes


def commitment_proposal(p):
    """What a persona proposes at the start of a household -> {"stay": weeks (0 = none), "requests": kind or None}.
    Security-seeking, togetherness-valuing, low-autonomy personas (security >= 0.6, autonomy < 0.4, togetherness >= 0.5)
    propose a mutual stay of COMMIT_WEEKS; if their style is competitive or collaborative they also propose that the
    partner accept their `stay_home` requests for the same time. Autonomy-seeking personas propose nothing."""
    w = p.weights
    if w["security"] >= 0.6 and w["autonomy"] < 0.4 and w["togetherness"] >= 0.5:
        return {"stay": COMMIT_WEEKS,
                "requests": "stay_home" if p.negotiation_style in ("competitive", "collaborative") else None}
    return {"stay": 0, "requests": None}


def accepts_commitment(p, kind):
    """Whether a persona accepts a proposed commitment of `kind` ("stay" or "requests") from the partner."""
    s, a = p.negotiation_style, p.weights["autonomy"]
    if kind == "stay":
        return a < 0.5 and s != "competitive"
    if kind == "requests":
        return a < 0.3 and s in ("accommodating", "collaborative")
    return False


# ---- pleasure levers (docs/decisions/0016-pleasure-levers.md). ASSUMED mapping from principles (weights and axes) to lever use ----
def variety_policy(p):
    """L-A. How a persona picks among variants of a repeated pleasure (synthesis M1: micro-novelty, spacing).
      'adaptive' (rotate AND space: an action's utility falls with its satiety): risk tolerance >= 0.5
      'rotate' (cycle variants): openness (certainty_openness >= 0.5) or adventure (security_adventure >= 0.5)
      'repeat' (do the best one again): everyone else (a certainty-seeker with a favorite)."""
    if p.risk_tolerance >= 0.5:
        return "adaptive"
    if p.axes["certainty_openness"] >= 0.5 or p.axes["security_adventure"] >= 0.5:
        return "rotate"
    return "repeat"


def ritual_proposal(p):
    """L-A. Whether a persona proposes a standing weekly shared slot: wants a fixed time (togetherness >= 0.5, security >= 0.4)."""
    w = p.weights
    return bool(w["togetherness"] >= 0.5 and w["security"] >= 0.4)


def accepts_ritual(p):
    """L-A. Whether a persona accepts a proposed ritual: a recurring slot costs some autonomy (autonomy < 0.6)."""
    return bool(p.weights["autonomy"] < 0.6)


def bond_policy(p):
    """L-C. -> {"n_ext": external bonds, "n_thick": how many of them are thick (3 strands)}.
    n_ext = 1 + round(3 x other_connections), at most 5; n_thick = 1 if togetherness >= 0.8 else 0 (a very togetherness-valuing persona
    keeps a second close bond rather than spreading thin)."""
    w = p.weights
    n = min(5, 1 + int(round(3 * w["other_connections"])))
    return {"n_ext": n, "n_thick": 1 if w["togetherness"] >= 0.8 else 0}


def lever_policy(p):
    """-> every lever-relevant choice of a persona, in one dict."""
    return {"variety": variety_policy(p), "ritual_proposes": ritual_proposal(p), "ritual_accepts": accepts_ritual(p),
            "commit": commitment_proposal(p), **bond_policy(p)}
