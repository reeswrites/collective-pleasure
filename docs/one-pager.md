# Multi-agent rules: a one-page summary

Date: 2026-11-11. Agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled state. Every finding is about scripted agents or small models with assumed parameters, not people. Full status: [goal.md](goal.md). Every result: [results/README.md](results/README.md).

## The question

Can norms and mechanisms, rather than training, let agents with different goals live well together?

Two commitments frame it. Pleasure is the good. Freedom is equal liberty minus domination. Leaving or refusing is not domination, because those options depend on agreement ([ADR 0014](decisions/README.md)).

## The product

The product is an evolving evaluator. In the author's words, "more interested in the norms but the evaluator is the more interesting product."

- **Loop one.** Rules move toward the test. Evolution tightens rules until agents stop finding seams the test catches.
- **Loop two.** The test moves toward the author's intent. Each "that's not what I meant" fixes the test. Four such fixes are logged. They are data points, not a curve.

This is the design aim. So far the test has changed only by the author's hand edits (four, on one day). No agent exploit has yet widened the formal model.

## What held

Each result carries its label from the statistics rule ([ADR 0015](decisions/README.md)).

- **Greedy play loses.** An agent that maximizes the next step's pleasure can lose to a planner, whenever its actions leave a trace in state. At discount 0.9 over 26 weeks, greedy reaches 96.8 percent of the optimum. At discount 1 it reaches 75.5 percent. Exact solves, so pass or fail with no interval. [horizon.md](results/horizon.md). Two of eight predictions missed in a clause each. Robustness ([multiverse.md](results/multiverse.md)): greedy loses something in 127 of 128 sampled settings, but the size varies widely (8 to 96 percent at discount 1 over 52 weeks). The concert timing and the 4-to-7-day friend gap from the same study did not survive the sweep and are not claimed here.
- **Appeasing feeds pressing.** Against appeasing partners, pressers do more pressing: 56.0 acts against 32.1 for attuned partners, +23.9 [9.66, 40.16], Holm p 0.0018. Holds robustly. The other three tests are descriptive, and one went the wrong way. [regulation.md](results/regulation.md).
- **Negotiation v2.1.** Under v2, real outside options made households worse than imposed rules. In v2.1 a failed deal means living apart, and that damage went away. So the v2 conclusion was an artifact of how failure was modeled. 3 of 5 predictions held. Not covered by the statistics retrofit. [negotiation-v2.1.md](results/negotiation-v2.1.md).
- **Pleasure levers.** Rotating beats repeating in 49 of 57 pairings (0.860 [0.742, 0.937]). A ritual beats an ad hoc dose of equal size (+0.0190 [+0.0161, +0.0217]). Pleasure peaks at 3 bonds, and 8 bonds sit 0.362 lower. All hold robustly. [pleasure-levers.md](results/pleasure-levers.md).
- **Robustness across assumed parameters** ([multiverse.md](results/multiverse.md)). Of twelve headline conclusions swept over half-to-double parameter ranges: 5 robust, 4 fragile, 3 flip. Robust: living apart beats cohabiting with no pot, seed v2.2's small pleasure edge and relational share, the seed v2 binding null, VPGG voluntary beats compulsory. The sweep varies numbers only, not the agent model.
- **H09.** With the floor rule removed from the prompt, 0 of 90 model proposals fell below it (95% [0, 0.040]). Holds robustly. This supports a fairness prior in the model. It does not show understanding of the floor. [h09.md](results/h09.md).

## What failed or was corrected

- **IT1 was never tested.** Three paid framings (about $10) found no inventive seam on L1 to L4. The classifier could not have labeled one: the formal model already reaches every harm those rule sets allow. The earlier "not supported" was an instrument artifact ([negative-results.md](negative-results.md), 2026-11-11; [plan](plans/inventive-seam-next.md)).
- **The first ladder harness was flawed.** One model drove both partners, so there was no victim. The first arm (270 runs, $4.35) was uninformative.
- **The household has one real fidelity mismatch.** Six tests against known findings. Two reproduced, and one of those (P2) is a re-check by the same code. Of the four that did not: P1a (outside options shape terms) had the right sign but fell below threshold, on only the pairs that formed a pot. P3 (sticky defaults) is underpowered, with the point estimate above threshold. P6 (adaptation) fails by construction, because levers-off has no adaptation; the lever itself works. Only P4 is a real mismatch: a sanction did not crowd out compliance, because the model has no crowding-out channel. P4 used a `warn` sanction, not a money fine ([fidelity.md](results/fidelity.md)).
- **Seed v2.2 does not yet beat the baseline.** The author's condition was that it show pleasure in relationships. With all three levers on it is still below baseline on the 15 hand-persona pairings: -0.019 [-0.051, +0.009]. The earlier +0.03 win comes mostly from persona weights ([pleasure-levers.md](results/pleasure-levers.md), [pleasure-demo.md](results/pleasure-demo.md)).
- **H01 missed its mechanism.** Pressing costs the presser about 22 pleasure-weeks of 156, but it costs as much when nobody can leave. Exit is not the reason ([h01.md](results/h01.md)).

## What is running and next

- **ADR 0018 tests.** Test 1 (liking versus wanting) has results: 14 of 15 predictions hold robustly, P8a weakly ([liking-wanting.md](results/liking-wanting.md)). Test 2 (worth it versus hard to leave) has a committed [prereg](results/stay-test-prereg.md) and is running.
- **H32 and H32b (done).** H32 is not supported as stated: free exit made the egoist converge in 1 of 30 cells; amplification and giving close the gap ([h32.md](results/h32.md)). H32 tested a mechanism Claude chose, not the author's essay thesis as a whole. H32b: a graded voice ladder converged in 0 of 30 cells; withdrawal alone helps, renegotiation undoes it ([h32b.md](results/h32b.md)).
- **Multiverse sweep (done).** See the robustness line under "What held".
- **Household fixes, then the v2.3 retest.** The author approved fixing the world first (2026-11-11). Seed v2.3 is partly confirmed: the author answered four points (trust, role fines, exit last, the decency floor); rule 14 (roles), the slid-into flag, the renegotiate step and the severe-distress skip were never read back ([read-back](results/seed-v2.3-readback.md)).
- **Retest verdict rule (author, 2026-11-11):** the v2.2 and v2.3 condition is judged on pleasure alone ("show both, judge on pleasure"), with net wellbeing and non-offsettable suffering shown beside it. Everyone counts, people who choose to live apart included ("everyone counts"). See [the retest prereg draft](results/v2-retest-prereg-DRAFT.md).
- **IT1 rerun.** New rule sets where an inventive seam is reachable and pays. Free harness work is approved. The paid run awaits approval, with a hard cap of $8.00 ([plan](plans/inventive-seam-next.md)).

## The open bet

*Claude-added framing, not yet confirmed by the author.* Most alignment work trains the agent. This asks whether the structure around agents can do more of the work: rules that are checked, ways to leave, and a test that keeps adapting. The hope is that a self-interested agent can be given reasons to attend to others without being made nice. This repo has not shown that. [pitch.md](pitch.md) calls alignment "the aim, not something shown so far."
