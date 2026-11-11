# Agent recalibration and bills that hurt: design and preregistration

Wording rule: agents feel nothing; "pleasure", "suffering" and "value" are glosses for modeled numbers.

Status: written and committed before any code that changes behaviour, and before any run. Nothing here is a result. Scripted agents, no model calls. Follows [value-consistency.md](value-consistency.md) and the author's decision logged in experiments/changes.jsonl (2026-11-11T21:53:50Z, "Yes, your leans"): (c) unpaid bills hurt and drawing down the pot is a lost buffer; (b) recalibrate the agents' heuristics to the check's one-week values, preregistered with the check as the pass test, then rerun H39b and the H38 formation check. A forecasting bias as a persona trait (b2) is not part of this.

**Can be about / cannot be about (required).** This can be about whether the scripted persona agents, after the change, value their own actions the way the hedonic model scores them over one week, in the H38/H39b makers-off household; and, through the two reruns, whether H39b's and the formation check's findings depend on the old agents. It cannot be about how people value time or bills, about any horizon past one week (limit 13's horizon part stays), or about worlds other than this household. Limits in [docs/limits.md](../limits.md) that apply: 1 (scripted agents), 2 (ASSUMED numbers), 9 (pleasure capped at 1), 12 (pairing is nesting only), 13 (this work). Not touched: the persona set, the card set, the exit fallbacks.

## Two switches, both off by default

Both are fields of `hedonic.FixConfig`, so they reach every world a harness builds, rollouts included:

- `agent_values: "v1" | "v2"`, default `"v1"`. v1 is `PersonaAgent.utilities` as it is now.
- `bills_hurt: bool`, default `False`.

With both at their defaults every past run reproduces bit for bit. Pinned before any change, from commit 36a6460: `tests/data/agent_values_off_fingerprints.json` (H39b arms Z, BP, M0; the formation check's G-L0 and G-L4; one value-check decision record; `tests/agent_values_fingerprint.py`). The older pins (levers, H38 pairing, makers off, makers flat cost, observer) must also still pass.

The switches act only in worlds where the household fixes are on (every world in H38, H39, H39b, the formation check and the value check). The switches are not added to `fixes_on`.

## (c) Bills that hurt

**Now.** At the month's settlement (every 4th week) the bill (10 for a couple, 6 alone) is paid first from the month's contributions, then silently from the shared pot. Only when the pot cannot cover it does anyone feel anything: a security hit of 0.15 (ASSUMED). What the pot cannot cover then disappears.

**With `bills_hurt`.** At settlement, when contributions fell short of the bill by `short` (of `need`):

| Term | What it encodes | Size | Source |
|---|---|---|---|
| Late fee | being late costs money | 5% of `short`, paid from the pot with the bill | ASSUMED (a common lease term; not checked) |
| Lost buffer | the pot is the household's savings; drawing it down is losing security | each member in the household loses security level equal to their equal share of the draw ÷ `sec_assets` (25, the assets at which the model's security refill is full) | ASSUMED scale; the model's own security unit |
| Bill stress | being behind, felt more as the buffer runs dry | offsettable friction that week, each member in: 0.30 × (short ÷ need) × dryness, dryness = 1 − min(1, pot before settlement ÷ 30) | ASSUMED size (twice a warning week, `WARN_FRICTION` 0.15); runway 30 = three months of the couple's bill, ASSUMED. Context: 37% of US adults could not cover $400 from cash (Fed SHED 2025) and the median family holds about five weeks of income in the bank (SCF 2025), docs/notes/economy-calibration.md |
| Arrears and eviction risk | what the pot cannot cover does not vanish | the uncovered rest carries into next month's bill (one month only, then written off), and each member in gets 0.30 friction that week on top of the existing 0.15 security hit | ASSUMED |

**Known-answer cases** (tests, before any run):

- KA1. A pair with no money and an empty pot at settlement, bill unpaid: both suffer bill stress at full dryness (0.30) and the eviction friction (0.30), and the bill carries over.
- KA2. A pair with a full pot (90 at the start) and the bill unpaid: no bill stress, no eviction friction, no arrears. Each loses security equal to its share of the draw ÷ 25 (10.5 drawn, 5.25 each, 0.21), and the late fee leaves the pot.
- KA3. The bill fully funded by contributions: no bill term at all, bit-identical to `bills_hurt=False` that week.
- KA4. `bills_hurt=False`: bit-identical to now (the pins).

## (b) Agent values v2

v2 replaces the body of `PersonaAgent.utilities` when `agent_values="v2"`. Every candidate action's value becomes the change it makes to this week's close in the hedonic model's own arithmetic, for the agent itself, plus a prosocial share of the partner's change where the action changes the partner's week directly:

u(a) = ΔW_own(a) + prosocial × ΔW_partner(a) [time together and paying shared bills only] − sanction(a), times the same ±10% noise.

W is the projected net of this week's close: clipped pleasure − clipped offsettable suffering − non-offsettable suffering, with every action already taken this week counted and no further action. It follows the five items the author named:

1. **Levels after the drift and after earlier actions.** W ticks the need clocks with this week's drift (rest −0.1, connection −0.2 or −0.3 apart, money − living cost, security decay and refill from assets) and the week's counts so far (own rests, works, friend visits, together sessions, friend-initiated visits, money spent).
2. **The model's scale.** Needs are worth `w_need × salience × (L − 0.5)/0.5` above half and `−salience × (0.5 − L)/0.5` below (the valued-money weights when fix 2 is on); aspirations `0.5 × weight × satisfaction` and `−0.3 × weight × (1 − satisfaction)`. No `_m`, no divisors. A need dropping below 0.15 counts the denial condition at its onset stage. Pleasure is clipped at 1 and offsettable suffering at 1, as the model clips them; last week's raw pleasure stands in for the terms the agent does not project (items, pairing terms, makers, glow).
3. **The missing terms.** Time together's own pleasure (`together_event` 0.10 a session); fix 1 contact amplification, release and missing pain; fix 2 bought pleasure; the lever strand payoff and care suffering through this week's bond quality update; the partner's one-week change for together (its prosocial share); the bill terms of (c) in the settlement week.
4. **Sanctions at their real cost.** A warning is priced at `WARN_FRICTION` 0.15 for each week it adds beyond a warning already running (warnings do not stack in the model). `cap_halve` and `suspend` at 0.2 a week (the restricted condition before onset; ASSUMED; neither occurs in these worlds).
5. **The H39b planner in one unit.** `makers.WeekPlanner` feeds v2 the week's counts, rests and money after each planned action, so `opportunity` sets block values (pleasure units) against a time cost in the same units.

**Kept as they are, on purpose.** The one-week horizon (carried-over stocks are limit 13's horizon part, a later choice). The variety policy: only an "adaptive" persona expects a satiated source to pay less (ADR 0016, a persona trait). H38's withdrawal scaling of the wish to see friends (a manipulated norm). The floor of 0.003. The partner's consent to time together (`together_utility` ≥ 0.02) and every propose-only score (requests, refusals, gifts, leaving). Spending on oneself loses v1's 0.05 × autonomy weight + 0.02: the model's autonomy aspiration measures how open the rules are, not spending (value-consistency gap 5); the meaning is not settled here.

**Not fitted.** No number in v2 is chosen. Every coefficient is the hedonic model's own (HedonicConfig, FixConfig, LeverConfig) or a bill number fixed above. The pass test below is the target; if it fails, the mapping may be corrected only where it disagrees with the model's arithmetic, each change documented with the check's numbers before and after, never against an experiment's outcome.

## Exploratory pilot

None. The check's own numbers are the reference: [value-consistency.md](value-consistency.md) (main sample, 5,760 decisions, rows in runs/value-consistency/rows.jsonl).

## Power check

Not a hypothesis test. The check is a known-answer measurement with a fixed sample (H38's 120 confirmatory pairings × seeds 0–3 × 6 sampled weeks, both partners, the week's last call), the same sample design as the original. The bars are on point estimates; per-action gaps are also reported with the bootstrap interval resampling runs.

## Pass test: the value-consistency check rerun

World: H39b's M0 arm (the value check's world) with `agent_values="v2"` and `bills_hurt=True`. Same sample, same code (`scripts/value_consistency.py`), main measure own net (clipped pleasure − both kinds of suffering) at the 1-week horizon. The perceived value is the number the agent chooses on, now with v2's sanction price.

| ID | Quantity | v1 (check) | Bar |
|---|---|---|---|
| T1 | pooled rank correlation, perceived vs actual, 1 week | 0.43 | ≥ 0.70 |
| T2 | mean within-decision rank correlation, 1 week | 0.39 | ≥ 0.60 |
| T3 | agent's best (or idle) = best by actual, 1 week | 35% | ≥ 60% |
| T4 | best beats next best by actual, 1 week | 40% | ≥ 60% |
| T5 | slope of actual on perceived (through 0), 1 week | 1.2 | in [0.8, 1.25] |
| T6 | per action (work, rest, see a friend, together, pay shared bills, spend on oneself; n ≥ 100): \|mean actual − mean perceived\| at 1 week | 0.003 to 0.113 | ≤ max(0.015, 0.25 × \|mean actual\|), each action |

T6 excludes decisions where a soft rule binds the action; those are held to the 13-week actual with the same bound (a sanction runs four weeks, and v2 prices all of it).

**PASS** iff T1 to T6 all hold. Anything else is FAIL, reported as such, clause by clause.

## Can every verdict happen? (required)

Checked free, before any run, with `scripts/value_consistency.py --reach` on the v1 rows (no new runs):

| Verdict or clause | Free check | Result |
|---|---|---|
| PASS | v1 rows with perceived replaced by the 1-week actual (an oracle agent) | to be shown in the commit that adds `--reach` |
| T1 to T4, T6 fail | the v1 rows as they are | to be shown |
| T5 fails | v1 rows with perceived doubled | to be shown |

The metric sees the mechanism: every v2 term is a term of `Hedonic.close_week` or of the world's friction and extra-pleasure sums, which the check's actual reads (`valuecheck._rows`, the evaluator's net line).

## Are we measuring what we say? (required)

- **Construct card.** "Perceived" = the number the agent ranks actions by at that call, noise off, minus its sanction price. "Actual (1 week)" = the change in the agent's own modeled net for the decision week, against doing nothing at that call, with the rest of the world playing on. v2 encodes "the agent forecasts this week's modeled outcome of one more action correctly, given its week so far". It does not encode foresight past the week, people's foresight, or anything about real bills. `bills_hurt` encodes "a bill the household does not fund costs money, security and stress, more as the pot empties"; it does not encode credit, debt markets or an actual eviction.
- **Known-answer case.** The bills cases KA1 to KA3 above, as tests. For v2: a test that a forced action's v2 value equals the change in the world's own close when that action is applied to a copy at the last call (exact up to the terms v2 holds at last week's value).
- **One other way to measure it.** Every T row is also reported (no bar) on (i) own + prosocial × partner net, the utility's own definition, and (ii) unclipped pleasure − suffering. If they disagree with the main line, the write-up says so.
- **Story spot-check.** After the reruns, read three runs week by week (one per rerun arm family) and say whether the agents' weeks look like a household that keeps up with its bills and needs.

## The two reruns (preregistered as amendments before they run)

After the pass test (whatever its verdict, reported first), H39b and the H38 formation check rerun with `agent_values="v2"` and `bills_hurt=True`, same designs otherwise. Each gets a dated amendment in its own prereg file before its run: [h39b-makers-rerun-prereg.md](h39b-makers-rerun-prereg.md) Amendment 2 and [h38-formation-check-prereg.md](h38-formation-check-prereg.md) Amendment 1.

## Not testable by design

The reproduction pins (pass or fail). The known-answer bills tests. The v2-equals-the-model's-close test.

## Limits stated now

One world for the pass test. One-week horizon by design. The bill numbers are ASSUMED, one point each, not swept. v2 makes agents near-exact one-week forecasters of their own modeled week; any result that then changes may change because agents became accurate, not because the rules matter more or less.

## Amendments

None yet.
