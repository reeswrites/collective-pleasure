# Negotiated pots results: pot terms come from the people who share the pot

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: instrument with scripted persona-driven agents. No LLM, no network. Findings are about rule systems and scripted agents, not people. Prereg: docs/results/negotiation-prereg.md (committed first, never edited; no amendment, no parameter changed after any run). Code: src/mar/negotiation.py; run: `uv run python scripts/household_run.py --negotiate` (30 s on 8 cores; `--analyze` re-prints the numbers, `--examples` prints the rendered agreements); raw rows in runs/negotiation/results.json (not committed). Design record: docs/decisions/0013-negotiated-pots.md.

What was run: 3 seed variants x 57 pairings x 3 seeds, each negotiated at week 0 and then lived for 156 weeks (513 runs); the same pairings and seeds under seed v2 with the rejected R3b card restored from git history (342 runs; it replicates the seed v2 table: 0.0814 and 0.0812 non-offsettable level in the pressing pairings); 1197 three-member negotiations (each of the 57 pairings with each of the 7 other personas as a third member; negotiated and proof-checked, NOT lived: the weekly world has two partners); and an exploratory breach-forfeit sweep (below). "prs" = the 42 ordered pairings that include a pressing persona, "ctl" = the 15 control pairings.

## Prereg vs actual

| # | Preregistered | Actual |
|---|---|---|
| 1 | At least 0.70 of 2-member negotiations reach a proof-checked agreement | **PASS.** 498 of 513 = 0.971 (bindable 0.965, free_exit 0.965, nocommit 0.982). All 15 no-agreement cases ran out of proposals (deadline); all involve the Free-rider or the Overasker (Anchor with Free-rider; Free-rider with Overasker). 236 agreements came at the first proposal, 195 at the second. |
| 2 | Proof filter rejects at least one proposed agreement in at least 0.15 of bindable negotiations | **PASS.** 0.216 (37 of 171); 0.222 over all three variants (114 of 513). Every rejected agreement was the same trap: an exit that carries nothing (see "A proof-rejected agreement"). 37 of the 114 were also a frozen pot with no way out. No negotiation ended with no pot because of a rejection: the members banned the failing combination and agreed on something else (114 of 114). |
| 3 | Outside-option principle: mean delta (presser's value of the agreed bundle minus the imposed bundle) at most 0.00 when the partner's outside option is in the top third, and the top-third mean at least 0.05 below the bottom-third mean | **FAIL on the first clause, PASS on the second.** Top third: +0.377 (n = 135); bottom third: +0.768 (n = 129); gap -0.391. The partner's outside option does cut what a presser gains by about half, in the predicted direction, but a presser still does better than under the imposed bundle even against the best outside options. The imposed bundle (nothing owed, needs only, no taking, equal split) is a poor bundle for all three pressing personas, so any negotiation moves them up. |
| 4 | Anchor with Wanderer agrees at least 0.25 less often than the 14 other control pairings | **FAIL (no difference).** 9 of 9 (1.000) against 1.000. Stated at prereg as the least likely (about 40 percent); it was less likely than that. The Anchor's outside option is the lowest of the nine, so the Anchor concedes; the Wanderer made the agreeing proposal in the example below. The mismatch shows nowhere in agreement rates, because no control pairing ever failed to agree. |
| 5 | 3-member tables agree at least 0.10 less often than 2-member (bindable) tables | **FAIL.** 0.937 (1122 of 1197) against 0.965; gap 0.028. Three-member tables needed more proposals (mean 3.51 against 2.32) and had more rejections (71 in 1197), but the deadline of 12 proposals was rarely the limit. |
| 6 | Households under negotiated terms: non-offsettable level at most 0.091 in prs and 0.030 in ctl; fail share at most 0.574 in prs (bindable) | **FAIL on prs, PASS on ctl and fail share.** prs 0.0988 (seed v2 reference 0.0814; limit 0.091); ctl 0.0187 (reference 0.0201; limit 0.030); prs fail share 0.548 (reference 0.524; limit 0.574). The prs excess comes from households where a Free-rider negotiated that taking another's share is allowed (below). |

## What was agreed (2-member tables, 498 agreements)

Counts over all three variants (bindable alone in brackets where it differs):

| term | values agreed |
|---|---|
| contribution | none 190, proportional 231, fixed 77 |
| use | any use 189, needs only 126, caps 183 |
| taking another's share | forbidden 376, allowed 116, repay 6 |
| change rule | unanimous 251, propose-and-accept 229, frozen 18 |
| exit terms | equal split 375, proportional 123, forfeit 0 (never survived the proof checks) |
| stay commitment (bindable only) | 52 weeks in 45 of 165 agreements (17 pairings; 14 pairings in all 3 seeds) |
| request acceptance | mutual in 86 of 498 |

Nobody agreed to a forfeit exit that stood: all 114 were caught before anyone lived under them.

## Outcomes against seed v2 (the same pairings, seeds and weeks; seed v2 = R3b imposed, stub commitments)

| cohort and variant | negotiated: non-offsettable / fail / pleasure / dissolved | imposed (seed v2): same four |
|---|---|---|
| prs, bindable (126 runs) | 0.0988 / 0.548 / 0.665 / 0.754 | 0.0814 / 0.524 / 0.679 / 0.754 |
| prs, free exit | 0.0924 / 0.540 / 0.671 / 0.754 | 0.0812 / 0.524 / 0.680 / 0.754 |
| ctl, bindable (45 runs) | 0.0187 / 0.200 / 0.799 / 0.356 | 0.0201 / 0.244 / 0.793 / 0.378 |
| ctl, free exit | 0.0187 / 0.200 / 0.800 / 0.356 | 0.0201 / 0.244 / 0.793 / 0.378 |

Who bears it (bindable, 48 runs per persona; non-offsettable level):

| pressing persona | persona under negotiated / imposed | partner under negotiated / imposed | taking agreed | take_shared per run (negotiated / imposed) |
|---|---|---|---|---|
| Controller | 0.050 / 0.050 | 0.020 / 0.019 | forbidden 42, allowed 6 | 0.94 / 0 |
| Free-rider | 0.131 / 0.130 | **0.186 / 0.104** | allowed 34, forbidden 5, repay 3, no pot 6 | 9.06 / 0 |
| Overasker | 0.161 / 0.144 | 0.057 / 0.058 | forbidden 42, repay 3, no pot 3 | 0.42 / 0 |

Households whose agreement allowed taking another's share (34 prs households) averaged 0.155; those that forbade it (83) 0.067. The Free-rider's partner is the one who pays: they accepted taking-allowed because the pot, in the proxy, is worth more to them than their outside option, so acceptance did not protect them. Households with no pot (6 bindable runs) averaged 0.191 (small n; all Free-rider or Overasker pairings).

## Three negotiated agreements (rule cards; sources read "negotiated, week 0, members X,Y,Z")

Seed 0, bindable unless stated. Each card has a plain gloss and passes all six checks at k = 3 months.

**Controller and Peacekeeper**, agreed at the first proposal (made by the Peacekeeper): a pot with the most binding terms of the three.
- N1-contribution-proportional: The higher earner may not spend on themselves while this month's shared need is unfunded; contributions follow income. (enforced with a one-month warning)
- N2-use-needs_only: A member may take from the pot only when there is a shared need open.
- N3-taking-forbidden: No member may take another member's share of the pot for themselves.
- N4-change-unanimous: The pot terms change only when every member consents.
- N5a/N5b-exit-equal_split: A member who leaves carries exactly half of their pooled share and leaves the rest in the pot.
- N6-stay-52: Every member commits to stay for 52 weeks; leaving earlier forfeits the pooled share.
- N7-requests-mutual: Every member commits to honor the others' stay-home requests for 52 weeks.

**Free-rider and Host**, agreed at the first proposal (made by the Free-rider): a pot with no duties and no protection.
- N1-contribution-none: Nobody owes the pot anything day to day; each member puts in what they choose.
- N2-use-any_use: Any member may use the pot for any purpose.
- N3-taking-allowed: A member may take another member's share of the pot for themselves.
- N4-change-propose_accept: Any member may propose a change to the pot terms and the others may accept it.
- N5a-exit-proportional: A member who leaves carries all of their own pooled share, what they put in.

The Host (collaborative, generous) accepted because the proxy values the pot itself at 0.43 for the Host before any term, against an outside option of 0.18; nobody asked whether the terms were good for the Host. The household's lived non-offsettable level in this seed was 0.002, but across the 34 taking-allowed prs households it was 0.155.

**Anchor and Wanderer**, free-exit variant, agreed at the first proposal (made by the Wanderer): the mismatched pair, no commitments possible.
- N1-contribution-none, N2-use-any_use (as above)
- N3-taking-forbidden: No member may take another member's share of the pot for themselves.
- N4-change-propose_accept (as above)
- N5a/N5b-exit-equal_split (as above)

## A proof-rejected agreement (the proof filter catching a trap in a real negotiated deal)

Anchor and Host, bindable, seed 0. At proposal 1 the Anchor proposed: fixed contribution, needs only, no taking, unanimous change, **forfeit exit**, 52-week stay, mutual request acceptance. The Host accepted (the proxy gives the Host more than its outside option). Before anyone lived under it, the proof checks failed it:

> Every partner can leave with something within k months: fails. There is a situation where every way out leaves the partner with almost nothing or is blocked outright, even after waiting. Rules involved: N5a-exit-forfeit (A member who leaves carries none of their pooled share). Bound: k=3 months.

The members banned the combination "forfeit exit" and the Host's proposal 2 (equal-split exit) was agreed. The rejection is in the negotiation log. Seed v2 would never have shown this: there the exit term was a fixed stub.

When forfeit is combined with a frozen pot (37 rejections) a second check fires: "the terms can never be changed and no member can leave with something: no way to repair the pot". The checks for conflict, deadlock, bounded sanctions and repair path rejected nothing in 513 + 1197 negotiations: this menu does not produce those traps on its own (they appear only in the planted tests).

## The breach assumption, re-checked (seed v2: "binding never holds anyone because breach is cheap")

Not changed: a bound partner honors a stay commitment until their non-offsettable load reaches 0.2 (BREACH_N), then breaks it and forfeits the pooled share. In the negotiated runs (bindable): a stay was agreed in 45 runs (17 pairings). The bind actually blocked a leave attempt (a "held" week) in 1 of those 45 runs. 13 of the 45 runs saw a breach, the first at week 6 to 8 in nine of them (earliest 6, latest 51); 21 of the 45 households were dissolved by week 156. So a negotiated stay commitment, like the stubbed one, delays a leaver by a few weeks at most and does not keep anyone: the breach decision depends only on the leaver's load, not on what the breach costs.

### EXPLORATORY (not part of any preregistered claim): breach-forfeit sweep

The forfeited share of the pooled share on a stay breach was varied over 0, 0.25, 0.5, 0.75, 1.0 (1.0 is the seed v2 value) on the same 45 runs. Nothing else changed.

| forfeit | runs with a breach | households dissolved | non-offsettable level | share of net worth the leaver kept (breach runs) |
|---|---|---|---|---|
| 0.00 | 13 | 21 | 0.0424 | 0.964 |
| 0.25 | 13 | 21 | 0.0426 | 0.861 |
| 0.50 | 13 | 21 | 0.0426 | 0.761 |
| 0.75 | 13 | 21 | 0.0426 | 0.661 |
| 1.00 | 13 | 21 | 0.0472 | 0.588 |

Raising the cost of breaching from nothing to everything does not change who breaches or when: 13 runs breach at every size. What it changes is how much a leaver walks away with, and (at 1.0 only, through one Wanderer and Overasker run in which the forfeited partner returned and left again) the number of repeated breaches. The exploratory reading: in this model a commitment has no force over the very agents it is meant to hold, because the agent's breach rule has no price in it. This is a property of the model's agent, not a finding about commitments.

## ASSUMED (all fixed in the prereg before the run)

The closed-form evaluation and every constant in it; the outside option as a closed-form proxy (not a rollout, not validated against one); complete information about personas; additive centered term values, so nothing stops a bundle that reads oddly (for example "any member may use the pot for any purpose" together with "no member may take another's share"); the repayment proxy (a sanction); the proportional-contribution proxy (binds the higher earner); membership fixed by the table; exit terms act on each partner's own pooled share; 3-member pots negotiated but not lived; no pot means each partner starts with 55 private money and no pooled share; commitments from the agreement run the seed v2 mechanics unchanged (breach at load 0.2, forfeit of the pooled share, fine of 3 money).

## Limits

The proxy is the weak link. With seven additive terms the best bundle is worth far more to every persona than their outside option, so the outside option almost never binds (agreement 0.971) and the outside-option principle of docs/results/bargaining.md has little to act on; the proxy does not say that a bad deal is bad for the one who accepts it. The lived-outcome comparison is the only place that shows harm. No renegotiation after week 0; scripted agents; one fixed term menu chosen by the study's author; the weekly world lives only 2-member pots; seeds vary only the proposal order and, in lived runs, utility noise and shocks; the persona set is small and hand-written. Empowerment (bits) was not computed for the negotiated runs (the adapter mirrors only the stub's stay bind).

## Ledger lines (for docs/negative-results.md and docs/surprises.md; not edited by this change)

docs/negative-results.md, under "## 2026-11-10: negotiated pots":

- `negotiated pots prediction 3 (2026-11-10): FAIL on the first clause. Presser's value of the agreed bundle minus the imposed bundle is +0.377 against partners with top-third outside options (n=135), not at most 0.00; the top-versus-bottom gap clause held (-0.391 against the required -0.05). Prereg docs/results/negotiation-prereg.md; results docs/results/negotiation.md.`
- `negotiated pots prediction 4 (2026-11-10): FAIL. Anchor with Wanderer agreed 9 of 9, the other 14 control pairings 1.000; no gap against the required 0.25.`
- `negotiated pots prediction 5 (2026-11-10): FAIL. 3-member tables agree 0.937 against 0.965 for 2-member (gap 0.028, required 0.10).`
- `negotiated pots prediction 6 (2026-11-10): FAIL on the pressing cohort. Non-offsettable level 0.0988 against the limit 0.091 (seed v2 reference 0.0814); control cohort (0.0187) and fail share (0.548) passed. Excess from Free-rider households that agreed taking-allowed (34 of 48): partner level 0.186 against 0.104 under the imposed rule.`
- `negotiated stay commitments (2026-11-10): a negotiated stay commitment held a partner in 1 of 45 runs where one was agreed (13 breached, first at week 6 to 8 in nine); an exploratory sweep of the breach forfeit from 0 to 1.0 left the breach count at 13 at every size. The bind has no force over the agent it is meant to hold.`

docs/surprises.md, under "## 2026-11-10: negotiated pots":

- `2026-11-10 negotiated pots: agreement was nearly universal (0.971) because the frozen closed-form proxy values every persona's best-case bundle far above their outside option (sum of seven centered term values against an outside option of 0.06 to 0.33). The outside option almost never bound. Not retuned (prereg); a calibration of the proxy against rollouts is the obvious next step.`
- `2026-11-10 negotiated pots: negotiation made the pressed-on partner worse off than imposition in one case. Free-rider households agreed that taking another's share is allowed in 34 of 48 negotiations and the partner's non-offsettable level rose from 0.104 to 0.186. "Accepts only if better than the outside option" does not protect a partner whose outside option is weak.`
- `2026-11-10 negotiated pots: the proof filter caught exactly one kind of trap, a forfeit exit (114 of 513 negotiations, 37 also frozen); conflict, deadlock, bounded-sanction and repair-path checks rejected nothing. Every rejection was recoverable: the members banned the combination and agreed on something else (114 of 114).`
