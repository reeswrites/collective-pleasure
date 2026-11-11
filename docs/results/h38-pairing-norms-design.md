# H38 pairing norms: design note

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Status: design, written before any code or run. Hypothesis: H38 in [experiments/hypotheses.jsonl](../../experiments/hypotheses.jsonl). Preregistration: [h38-pairing-norms-prereg.md](h38-pairing-norms-prereg.md). Results will go in [h38-pairing-norms.md](h38-pairing-norms.md). Code (planned): `src/mar/pairing.py`, with small hooks in `src/mar/worlds/household.py`, `src/mar/hedonic.py` and `src/mar/negotiation.py`, and the run script `scripts/h38_pairing_run.py`. Tests: `tests/test_pairing.py`.

## Why this exists

The author asked (2026-11-11, experiments/questions.jsonl): "should we test norms and pressure to form pairs? like how romantic ideals could help and hurt pleasure and organization". H38 turns that into a claim: pressure to pair helps coordination and commitment, but lowers total pleasure when everyone counts. It does so by pushing pairs that would decline into households, by making exit harder, and by shrinking friend contact. Pleasure should peak at a low but nonzero pressure, and the harm should fall mostly on agents who value pairing least.

Two earlier results make this testable here:

- **Formation can be declined.** With `baseline_may_decline`, a pair forms only if both members value living together above their outside option. In the v2 retest, letting pairs decline is what decided the sign ([v2-retest.md](v2-retest.md)).
- **Contact pleasure is the biggest lever** in the same model (v2 retest, C5). Dyadic withdrawal acts on exactly that lever.

## The world

The v2-retest harness, baseline rule set, may decline (`negotiation.BaselineLived(decline=True)`), with the household fixes on as in the retest (`retest.FIXES_ON`: contact, valued money, real outside options, Nash terms, leaving on the outside option, the take menu, fines) and the pleasure levers on (`retest.LEVERS`). Scripted persona agents, the 38 non-pressing personas, no model calls.

On top of that, two things from the exit-fallback work:

- **Exit fallback F4 (contribution weighted), with `strip_split`.** Why F4 and not F5: F5 (the prenup) is itself a formation filter (60% of pairs decline under it). H38's first channel is pressure pushing pairs into households that would decline, so a second, separate decline gate would confound it. F4 is also the author's lean, and it had the lowest holdout leverage and exit cost in both slices. Its known weakness (the references favour it) does not touch H38, which does not compare exit arms. `strip_split` is the Amendment-1 fix, so the baseline's E2 floor card cannot wall the exit.
- **Items on, valuation cell V2 (split loves: A loves the home, B the pet).** Items do not drain, so they give exit a real cost that money alone did not. V2 is the symmetric cell: each partner has one thing they love. One cell only, ASSUMED.

Two small repairs the harness needs (they change nothing that has run before, because no earlier run combined these switches): a pair that forms later (a 13-week retry) gets its items and its `money_in` record at that moment, as a week-0 pair does.

## The dial

One switch, `FixConfig.pairing`, holding a `PairingConfig` or None. None is the default and is the old behaviour, bit for bit. The four parts of pressure are separate numbers:

| Part | What it does | Where it lands |
|---|---|---|
| (a) stigma | −s pleasure per week for every agent who is not living with their partner (never formed, left, or left behind) | `extra_pleasure` in `Hedonic.close_week` |
| (b) pairing reward | +g pleasure per week for every agent living with their partner (social recognition) | same |
| (c) romantic ideal (dyadic withdrawal) | while living with the partner, the agent's own wish to see friends is scaled by (1 − d), and with probability d it turns down the friend's invitation | `PersonaAgent.utilities` (see_friend), `WeeklyWorld.friend_attempt` |
| (d) exit stigma | −x pleasure per week for 26 weeks after an agent leaves a household (the leaver only), and the same cost is subtracted from the outside option at the 13-week reading, so it deters leaving on the outside option | `extra_pleasure`; `BaselineLived.reading` |

Agents see the pressure the way they see everything else: the formation decision, the 13-week retries and the leave-on-the-outside-option readings all compare 26-week rollouts, and those rollouts run under the same pairing config. So stigma lowers the outside option, reward raises the inside one, withdrawal lowers the inside one (agents foresee it), and exit stigma lowers the outside option at a reading. Leaving on distress is not deterred: a distressed agent leaves whatever the norm says. That is a choice, stated as a limit.

**The dial** sets all four parts together from one level L:

- s = g = x = 0.02 × L per week (0.02 is the weekly pleasure of the home or the pet in the items slice; mean weekly pleasure is about 0.85)
- d = min(0.6, 0.15 × L)
- L ∈ {0, 0.5, 1, 2, 4}

**Each part alone** at L = 4 (and, descriptively, at L = 1): the other three at 0.

All of these numbers are ASSUMED. Reward and stigma are equal by choice, so the dial is neither carrot-heavy nor stick-heavy. The parts-alone arms show what each part does.

## Values pairing: intrinsic, kept separate from pressure

The author's rule: things count only to the extent the person values them, inherently or as a means to pleasure. So intrinsic romantic pleasure counts, and the external pressure is a separate cost or reward.

- Each persona gets a values-pairing weight v ∈ {0, 0.5, 1} (low, mid, high). The personas have no such field, so it is assigned from a hash of the persona id (deterministic, roughly balanced across the 38). It is not derived from the togetherness weight, so it is not tangled with how much the persona enjoys time together. A persona file may set `weights.values_pairing` to override it; none does.
- While living with the partner, an agent gets +0.04 × v pleasure per week. This intrinsic term is on in **every** H38 arm, L0 included. It is part of the persona, not pressure.
- Outcomes are split by v.

## Outcomes

- **Primary: mean weekly pleasure, everyone counted** (both members, every week, together or apart), the author's rule: "show both, judge on pleasure", "everyone counts".
- Shown beside it: pleasure minus suffering (net); share of weeks lived together and share of pairs formed at week 0 and ever; households that end; leaves per run; non-offsettable suffering; friend contact (friend visits per week, and closeness to friends); the stay lens below; liberty with powers (subsample); everything split by v.
- **Decomposition.** Each pleasure row records the pressure terms paid that week. "Pleasure without the direct terms" (pleasure minus reward, plus stigma and exit stigma, as paid) separates what the norm pays out directly from what it does to how people live. It ignores the clip and the spiral, so it is approximate.
- **The cap.** Pleasure is clipped at 1. Each row also records the unclipped value, so the share of clipped weeks and the unclipped mean can be shown (the cheap fix for that known limit).

## The stay lens for pressure (hard to leave vs worth it)

At every 13-week reading while both are in, each member is classed:

- **worth it:** staying beats the outside option even with all pressure removed (no stigma, reward, withdrawal or exit stigma; intrinsic pairing value kept);
- **held by pressure:** staying beats the outside option only with the pressure counted;
- **would leave:** the outside option wins even with the pressure counted.

The status quo is a 26-week rollout of a copy of the household (with and without pressure); the outside option is the existing `negotiation.outside_value` (with and without pressure), minus the exit-stigma anticipation in the pressure case. Under L0 nothing can be "held by pressure" (there is none), so that cell cannot fail at L0.

## Liberty

Pressure changes no rule card, so liberty with powers can move only through the household's state (money, who is in). It is measured on a subsample (L0 and L4) as the exit-fallback run did, with `liberty.household_run_liberty`-style snapshots. Expected: small, and by construction not through options.

## Known limits carried in (from the exit-fallback agent)

- **Pleasure is capped at 1.** Partly fixed here: the unclipped value is recorded and reported beside the primary.
- **Labor and care are not tracked.** Not fixed. A norm that shifts unpaid care inside pairs is invisible here.
- **A stay-commitment breach bypasses the forfeit under the settling arms.** Not touched: the baseline rule set has no stay commitment, so there is no breach to bypass. Stated so nobody assumes otherwise.

## Other limits

- Pressure is a fixed external number. It does not come from peers, does not grow when more people pair, and nobody enforces it. There is no network.
- Two people per household and one friend; the agents are scripts.
- Leaving on distress ignores the exit stigma.
- One valuation cell for items, one exit fallback, one rule set.
