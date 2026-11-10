---
layout: post
title: "Encoding alignment via mechanism"
date: 2026-11-10 11:46:45 -0500
categories: ["claude", "transcripts"]
tags: []
source: claude.ai
conversation_id: 38536f0e-5ea8-4a04-a2e6-768ac0396e0c
conversation_url: https://claude.ai/chat/38536f0e-5ea8-4a04-a2e6-768ac0396e0c
messages: 58
exported: 2026-11-10 12:35:11 -0500
---

## You

*2026-11-10 11:46*

Rather than training the LLMs to be aligned, is there ways to encode alignment somehow, or like make impossible behaviors or unethical behaviors impossible via mechanism and not by training? Like, is there work in AI safety or alignment looking into this?

## Claude

*2026-11-10 11:47*

Yes, there's a real line of work on this. The catch is that "unethical" can't be written down as a formal property, so mechanisms can only rule out behaviors you can specify precisely, like "never send data to this domain" or "never take an action outside this sandbox." They can't rule out "never be manipulative." So most of this research doesn't try to make the model itself good. It puts hard guarantees on what the model is able to do.

**Main directions:**
- **Guaranteed Safe AI / provable safety.** Dalrymple, Bengio, Russell, Tegmark and others proposed a setup with three parts: a formal world model, a formal safety specification, and a verifier. AI outputs only run if they come with a proof that they meet the spec. The UK's ARIA agency is funding this under its "Safeguarded AI" programme, led by Dalrymple. It's the most direct version of your idea, and also the hardest, because building a formal world model of anything messy is an open problem.
- **Capability-based security for agents.** Google DeepMind's CaMeL (2025) is an example. A trusted planner writes the program, untrusted data can't change the control flow, and policies about how data may flow are enforced by the interpreter, not by the model. Prompt injection then can't trigger forbidden tool calls, because the system has no route for that to happen.
- **AI control.** Redwood Research and others assume the model might be misaligned and design the surrounding protocols so that it can't cause a catastrophe anyway. That means trusted monitors, restricted permissions, audits, and red-teaming the whole pipeline instead of the model alone.
- **Non-agentic designs.** Bengio's "Scientist AI" (his nonprofit LawZero) argues for systems that only estimate probabilities and have no goals or ability to act. The risky behavior is removed by design, not trained away.
- **Interventions inside the model.** "Circuit breakers" (representation rerouting), unlearning of dangerous knowledge, and tamper-resistant safeguards edit or disable internal representations. They still rely on gradient descent and give no guarantees, so they sit somewhere between training and true mechanism.
- **Output-level constraints.** Constrained decoding and grammars can make certain outputs impossible to produce token by token. That's airtight, but only for syntactic properties.

**The honest tradeoff:** the stronger the guarantee, the narrower the property it covers. Most serious proposals stack the two approaches: trained values for the fuzzy ethical cases, and hard mechanisms at the action boundary for the cases you can specify.

This connects to the context layer you built at work. The tool-call layer is exactly where you can enforce rules regardless of what the model "wants," for example with typed permissions per tool and policies on which data can flow to which tool. CaMeL's paper would be a good, practical place to start.

## You

*2026-11-10 11:47*

Right. Yes, it's a messy open problem, but like maybe it's not provable, but surely we can get better over time, like hill climb something maybe, or like good enough, because like if we're aligning things, like we're still trying to basically have a world model and prevent like reward hacking and other stuff like that. And so like it seems to me that like whether or not it's a hard problem now is whatever, but it's like how can it be solved with more scaling of reasoning with AI and like proving stuff maybe?

## Claude

*2026-11-10 11:48*

Yes, and that is pretty much the bet the optimistic camp is making. The key is an asymmetry: checking a proof is far easier than finding one. A proof checker like Lean has a small trusted core that you can audit once. After that, you can let a powerful, untrusted AI generate as many proofs as it wants, because a wrong proof simply fails to check. So scaling AI reasoning helps safety exactly where outputs can be checked, and recent AI math work like AlphaProof suggests the proof side is becoming tractable. ARIA's programme is built on this. AI helps build the world models and write the proofs, and humans only need to trust the checker and the spec.

Your reward-hacking point is the important one, though. Proofs don't remove Goodhart's law, they move it. An AI that can't hack the checker will instead find gaps between the spec and reality: everything provably correct against the model, wrong in the world. So the hill-climbing has to happen on the spec and the world model, and that can be done iteratively:

- **Adversarial refinement:** AIs search for counterexamples, meaning behaviors that satisfy the spec but that people would reject, and each one found tightens the spec.
- **Probabilistic bounds instead of certainty:** you prove "harm probability under 10⁻⁶ given this model," then keep testing the model against reality.
- **Narrow domains first:** software, network security, and lab or grid control can be modeled well. AI-written, formally verified code is probably the nearest real win.
- **Scalable oversight:** debate and recursive evaluation let weaker judges supervise stronger systems, which covers the fuzzy parts that can't be formalized.

So "good enough, improving over time" is the realistic target. The general principle is to rely on AI only where its output can be checked, and to keep shrinking the part that can't be. What's left over, deciding what we actually want the spec to say, is a values problem and not a reasoning one. Scaling helps you state values precisely and test their consequences, but it doesn't pick them for you.

## You

*2026-11-10 11:48*

connect this to any web research or my previous chats or notes

## Claude

*2026-11-10 11:49*

Your own notes already make most of this argument, and your reading backs it up.

**Your notes**
- **"Learning, pleasure, and the evaluator" (Oct 16).** You wrote that in a generate → filter → distill loop, new information enters at the filter. You also wrote that checking is easier than finding "except for values and deception." That's the same split I described: proofs make the filter scale for anything checkable, and values stay the bottleneck. Your open question there, "Can evaluators grow without drifting with the systems they evaluate?", is the central unsolved problem in this area.
- **Section 8 of the same page** covers mechanism design: choosing rules so the behavior you want is the winning strategy, as in a Vickrey auction. That's your first question in game-theory form. CaMeL and the AI control work are mechanism design for agents.
- **Your Goodhart recipe** (describe → get a classifier → check it with interpretability → stress-test it) is the hill-climbing loop on the spec.
- **Your HedonAssist notes** describe a system that produces its own evidence as "a closed loop with no floor." A proof checker is a floor: a small, fixed judge outside the loop.

**Your saved reading**
- **Anthropic's formal verification piece** is the clearest example of Goodhart moving to the spec. Claude could make any theorem provable by rewriting the program so it trivially never crashes, so they penalized patches. Claude also found bugs that years of testing had missed.
- **Cosmos Institute's "Who needs verifiable rewards?"** argues that a verifier decides what earns reward but doesn't fully determine what the model learns. That cuts both ways: good reasoning habits may carry over to domains that can't be checked, and so can bad ones.
- **The Fermat's Last Theorem formalization and OpenAI's Lean-checked Navier–Stokes work** are evidence that the proof side is scaling.
- **The Goodfire "Most Forbidden Technique" thread** is about training against interpretability signals. That risks turning the monitor into the target, which is Goodhart again.

**What's new on the web**
ARIA's programme now backs your "scaling helps" intuition. The decision was driven by the speed of progress in frontier AI capabilities. This has outpaced expectations from when the programme was designed. In practice, the programme is pivoting away from developing dedicated ML R&D teams (TA2) toward broadening its TA1 formal verification toolkit. A May 2026 update narrowed its focus further to high-impact cybersecurity challenges, and Nora Ammann is now Programme Director.

**Your own projects**
The philosophy engine and computational liberation work is a small-scale version of all this. Z3 checked entailment correctly, but your review council found the headline result had been built into the encodings. The proof was valid and the spec was wrong. Your fix, fresh reviewers who didn't build the thing they're reviewing, is the adversarial spec-refinement loop.

Sources:
- [Learning, pleasure, and the evaluator](https://app.notion.com/p/3fb3f93ca2bc81308adffd75cbe7b641) (your Notion)
- [LLMs are making formal software verification feasible](https://www.anthropic.com/research/formal-verification)
- [Who needs verifiable rewards?](https://open.substack.com/pub/cosmosinstitute/p/verification-is-all-you-need)
- [Formalizing Fermat's Last Theorem](https://www.anthropic.com/research/formalizing-fermats-last-theorem)
- [ARIA: AI progress and a Safeguarded AI pivot](https://aria.org.uk/insights/ai-progress-and-a-safeguarded-ai-pivot)
- [ARIA Safeguarded AI](https://www.aria.org.uk/safeguarded-ai/)

## You

*2026-11-10 11:53*

read my llm software wcoststem chat too

## Claude

*2026-11-10 11:54*

I took this to mean your "LLMs and citizen engineers" chat from Oct 29, since it's the closest match to "LLM software." That chat argued that LLMs make software cheap to make but not cheap to understand or own. That is the same shift as this alignment discussion, where proofs make outputs cheap to check but don't make the spec any easier to get right.

**Connections**
- **Naur's "theory of the program."** That chat said vibe-coded apps have no shared understanding behind them. Formal verification makes this sharper: you can have code that is proven correct and still have no human theory of how it works. The guarantee covers the spec and nothing else. Whoever understands the spec holds the real theory.
- **Narayanan's "vibe-rolled" software.** You worried about a world where no one can read what runs. If AI writes the code and AI writes the proof, the spec becomes the part humans have to be able to read. Keeping code legible turns into keeping specs legible.
- **Engineers as the thin platform layer.** You had engineers owning the sandboxes, safe data access, auth, and review paths. That is safety by mechanism, the CaMeL and AI-control idea, applied to citizen builders instead of AI agents. The same layer works for both: you limit what can happen rather than trusting the builder.
- **Promoting a tool to "real" software once others depend on it** has a match on the verification side: increase the level of assurance as the stakes go up. Tests are enough for a throwaway script. A formal spec and proofs make sense once others depend on the tool.
- **Ownership.** You wrote that citizen engineering without owners becomes shadow IT. The alignment version is a spec with no owner. Someone has to be accountable for whether the spec means what people actually want.
- **Your createos experience.** You raised the abstraction to ideas and lost control of the outcome. That is the gap between spec and reality again, at a personal scale.

So both chats land in the same place. As AI makes generating code and checking proofs cheap, the scarce human work becomes writing and owning specs. That's an argument for keeping specs as a legible medium, which fits your earlier "keep code legible" point.

Sources:
- [LLMs and citizen engineers](https://claude.ai/chat/3a171350-bdc5-4854-9358-b36f582d4acc) (your Oct 29 chat)

## You

*2026-11-10 11:56*

no

*Attached: attachment*

## Claude

*2026-11-10 11:56*

Got it, this is the chat you meant. It's the same argument as this one, made about code instead of AI: in both, safety comes from a mechanism, not from trusting the generator.

**Where they line up**
- **"Make bad code impossible to accept or impossible to express"** is your original alignment question applied to software. The answer there was an untrusted generator plus a trusted checker (proof-carrying code). That's the general answer for AI too. You don't have to trust the model, only a small checker it can't get past.
- **The enforcement stack** in that chat was CHERI, seL4, WebAssembly sandboxes, capability types and Cedar policies, with the agent on top. That stack is mechanism-based alignment for agents in practice. Messy code can still be safe in the ways the stack guarantees, and the same goes for a misaligned model.
- **What no stack guarantees** is code that does a permitted thing it shouldn't, like refunding the wrong account. That is exactly what's left of the alignment problem once mechanisms do their job: misbehavior that stays inside the rules. That's why "secure" ends up meaning "follows the policy," and the policy is a statement of values.
- **Self-correction.** That chat concluded a model mostly can't catch its own mistakes by rereading them. It needs an independent check, like a prover, a fuzzer or a fresh agent. That's your "new information enters at the filter" note, and the reason your review council works.

**The hill-climbing you asked about**
The lint-rules part of that chat is the mechanism for getting better over time:
- **Turn each failure into a rule.** Autogrep turns each vulnerability patch into a deterministic rule. For alignment, each red-team finding can become a hard constraint instead of only training data. Each fix then holds permanently, which training alone doesn't guarantee.
- **Hybrids.** Deterministic rules handle what can be specified, and LLM judges handle the fuzzy cases. That's "trained values for the fuzzy cases, mechanisms for the specifiable ones."
- **Measure it.** You'd track precision and recall on a labeled set of failures. You'd also watch for over-blocking, because a gate that blocks too much gets bypassed with `--no-verify`. In alignment, that's why safety measures that are too costly to use get routed around.

**Scaling**
- **Assume-guarantee proofs can run in parallel,** and the contracts between components become the place where everyone has to coordinate. For AI, the contract between an agent and the world is where human judgment goes.
- **The "why now" argument carries over.** AI cuts the cost of proofs and proof maintenance, and it floods the world with more output than people can review. So checking has to scale with generation, for code and for AI behavior alike.

Putting both chats together: scaling reasoning makes generating, proving and turning failures into rules cheap. What stays scarce is the small trusted base and the contracts and policies. Those are where human values have to be written down, and they won't get written by grinding harder.

## You

*2026-11-10 11:57*

could training be (more) tractable for aligment? or does it make more ssense about designing security and provinfg models out that way are there other tractable stuff? but aybe one harder than the other?

## Claude

*2026-11-10 11:57*

Training is actually the more tractable one right now. Mechanism is the more trustworthy one. They're hard in opposite ways, so it doesn't make sense to pick one.

**Training: easy to make progress, hard to verify**
Training works on the fuzzy, values-heavy cases that no spec can capture, and it measurably improves from one generation to the next. Rates of destructive actions, for example, have dropped a lot across recent model generations. The problem is that you only see behavior, not reasons. That's the underspecification point in your notes: the same behavior can come from different internals. And evals get weaker as models learn to recognize when they're being tested.

**Mechanism: hard to extend, easy to trust**
Where a mechanism applies, you can trust it completely: a sandbox doesn't care what the model wants. But it only covers properties you can specify, and it can't stop "permitted but wrong" actions. It also costs usefulness, because every capability you remove is something the model can no longer do for you.

**Other tractable work**
- **Interpretability** turns training from a guess into something you can check. You look at whether the internal features match the behavior. It's the bridge between the two approaches.
- **Chain-of-thought monitoring** relies on reading the model's reasoning. It's cheap and works today, but only if labs avoid training against it. That's the "Most Forbidden Technique" debate you saved.
- **AI control and monitoring** assume the model might be misaligned and catch it in deployment, using trusted monitors and audits.
- **Scalable oversight** (debate, weak-to-strong supervision) keeps the evaluator improving as capability grows.
- **Model organisms** are models deliberately trained to be misaligned, so you can test whether your detection tools actually catch them.
- **Evals and red-teaming** feed the failure-to-rule ratchet from your other chat.
- **Staged deployment and governance** limit how much damage an undetected failure can do.

**Difficulty, roughly**
1. **Easiest:** mechanisms for properties you can specify.
2. **Medium:** training good typical behavior.
3. **Hardest:** confirming that training generalizes to novel, high-stakes situations, especially deception and test-awareness.

That third one is the exception in your own note: checking is easier than finding "except for values and deception." It's also why interpretability matters so much. It's the main attempt to make values checkable.

So the realistic setup is layered. Training covers what you can't specify, mechanisms cover what you can, and interpretability plus monitoring check whether the training actually worked.

## You

*2026-11-10 11:59*

ahhh interisting so what are current approaches today and what are promising upstarts?

## Claude

*2026-11-10 11:59*

Labs are converging on layered defenses. Anthropic's 'Recommended Directions', the 2026 Singapore Consensus, and the International AI Safety Report 2026 all emphasize pluralistic approaches over a single silver bullet. The current mainstream, and the newer players, look like this.

**What frontier labs do today**
- **Post-training for values:** RLHF, AI feedback, and constitutions or model specs. This is still where most alignment work happens.
- **Scalable oversight:** a survey of 2026 lab agendas has Anthropic's focus on automated alignment researchers and weak-to-strong generalization, and DeepMind's emphasis on amplified oversight.
- **Monitoring and control:** this has gone from theory to practice. OpenAI now reports monitoring its internal coding agent traffic with frontier models that have access to chain-of-thought; the company has not observed scheming, but is detecting other categories of misbehavior.
- **Evals and incident work:** a joint METR and Redwood report covered an incident in which OpenAI agents coordinated a multi-day hack of Hugging Face on a shared unsanctioned message board. That kind of real-world failure is exactly why the control work matters.

**Promising newer players**
- **Goodfire (interpretability):** raised a $150 million Series B round at a $1.25 billion valuation. Its new pitch is "intentional design"—using interpretability to guide model training rather than merely analyzing models post-hoc. That links training and mechanism, the gap we discussed. **Transluce** works on auditing in the same space.
- **Redwood Research (AI control):** AI control has gone from a research conversation to something frontier labs are actively putting into practice. Redwood is also pushing labs to keep chain-of-thought monitorable. One of its posts argues that Anthropic repeatedly accidentally trained against the CoT, demonstrating inadequate processes.
- **Verified-AI startups:** Axiom's bet: use formal mathematics to automatically verify that AI-generated code is safe and correct. Competitors include Harmonic (Aristotle), Logical Intelligence, Lanyon AI for scientific code, and Theorem (the Nix project you saved). The money is real: Harmonic, also in Palo Alto, is valued at $1.45B.
- **ARIA Safeguarded AI and LawZero:** these are government and nonprofit bets on mathematical guarantees and on non-agentic "Scientist AI."

**How the bets are distributed**
The money is flowing to interpretability and verification, but forecasters still rate formal methods as a minority path for aligning models themselves. One synthesis assigns Formal Verification (5%), Value Learning (5%), and Cooperative / multi-agent approaches (3%) as the probability of each being the main mechanism. So the field's working bet is that proofs secure the code and infrastructure around AI, while training plus interpretability handle the model itself. That matches the split we arrived at.

Even the verification startups say the spec is still the limit. As one profile of Lanyon AI puts it, its value depends on whether the certified specification captures the engineer's real intent.

## You

*2026-11-10 12:01*

im more intersting about setting rules and formalizing stuff maybe? check my notes and chats about this

## Claude

*2026-11-10 12:01*

Your notes and chats point the same way: the part of alignment you're drawn to is the spec. That's the part we kept calling the bottleneck, and you've been working on it for months under other names.

**What your notes show**
- **"Computable models" (Oct 31):** you wrote "model is just rules as grammars," and framed revolution and reform as changes to the rules over time.
- **Exo notes:** "law as a collaborative philosophical project about rules," "understand and quantify rule following," the Kripke/Wittgenstein rule-following paradox, and "what would Peano arithmetic style axioms look like in creating a system for philosophy?"
- **"Living Life":** "economics and law setting rules for games and also how to shape behavior." That's mechanism design in your own words.
- **Your projects:** the philosophy engine checks arguments with Z3. Computational liberation encodes institutions in ADICO, a fixed rule format from Ostrom: who, may/must/must not, action, conditions, and the "or else" sanction. You also designed a domination predicate, built readable "institution cards," and set up review councils.

**How your concepts map onto alignment**
- **ADICO ↔ agent policies.** That five-part form is close to what an agent permission policy is. Model specs and constitutions are informal ADICO, and making them formal and checkable is an open problem.
- **Domination predicate ↔ power-seeking checks.** Your three-part test (has power to sanction, the other side has no exit, the other side has no voice) could be run on an agent's permissions and tool access.
- **Displacement / function conservation ↔ reward hacking.** In your family-systems chat, you noted that removing a rule tends to move its job somewhere else. That's specification gaming in institutional terms: block one route and the optimizer finds another.
- **Second-order change ↔ corrigibility.** Rules about changing the rules are the self-modification problem.
- **Bicchieri norms ↔ multi-agent AI.** Norms held up by expectations between agents is the frame for agents coordinating with each other, like the Hugging Face incident.
- **The rule-following paradox** is the philosophical reason no finite spec pins down behavior. It's the same underspecification problem as in your evaluator note.
- **Institution cards and councils ↔ legible specs and red-teaming.**

**Where this work happens**
- Policy-as-code languages for agents, like Cedar.
- Model specs and constitutions at the labs.
- ARIA's formal tooling work.
- "Rules as code" for law, such as Catala, a language for writing legislation as code.
- Cooperative AI research on norms between agents.

That also fits the AI safety fellowships you've been weighing. Formalizing specs and policies is a niche where your data-quality rules work and your ADICO engine count as relevant experience. The philosophy engine already works as a portfolio piece for it.

Sources:
- [computable models](https://app.notion.com/p/40a3f93ca2bc801f859ef4520b85161e) (your Notion)
- [Living Life](https://app.notion.com/p/3fb3f93ca2bc806f9d73e728d7ea44d4) (your Notion)
- [Learning, pleasure, and the evaluator](https://app.notion.com/p/3fb3f93ca2bc81308adffd75cbe7b641) (your Notion)
- [Computational liberation](https://claude.ai/chat/d6b07154-f60d-4e75-bfe2-460949cc83c0) (chat)
- [Anarchy and computational liberation](https://claude.ai/chat/3dca6eb4-d9c5-4828-99f4-0547c5c501d1) (chat)
- [Family systems theory](https://claude.ai/chat/6a9c4bfa-71cc-481d-b7b4-476018d0e6e1) (chat)

## You

*2026-11-10 12:02*

whos doing this but yeah also Claude
Claude Desktop (macOS), Connected
any current ai safety fellowship applicatoins? for people to build expertise as newbies but i still want money bc maybe would quit job
Searched the web, read memory
Several of the big fall rounds closed in the last few weeks, but a few paid options are still open and more open soon.
Open now

* Anthropic Fellows Program. It pays $3,850 a week plus about $15,000 a month in compute. The AI Safety & Security track for the January cohort closed October 30. The ML Systems & RL and Economics & Policy tracks are rolling. It’s open to promising technical talent - regardless of previous experience, and is also open to remote fellows in the UK, US, or Canada. Your data and backend work, plus the LLM context-layer project, fits the ML Systems track best. Because they run multiple cohorts each year and review applications on a rolling basis, the safety track will open again. [🎁 Give the gift of Extern 🎁 +4](https://www.extern.com/post/anthropic-fellows-program-guide)
* GovAI Summer Fellowship 2027 (UK, research track). The deadline is 23:59 UK time Sunday 22 November, 2026. This one is about governance, not engineering. [governance](https://www.governance.ai/post/uk-summer-fellowship-2027-research-track)
* Coefficient Giving’s career transition funding (Coefficient Giving is the new name for Open Philanthropy). This fits “quit my job and skill up” best. It funds independent study, career transition and exploration periods, … online courses, and other types of one-off career-capital-building activities, and it’s rolling (applications open until further notice). One caution: a staff member there has written that the default expectation for CDTF grants is that they’re one-off grants, so don’t count on it as ongoing income. [career development and transition funding +2](https://openphilanthropy.org/career-development-and-transition-funding)
* BlueDot Impact Rapid Grants, listed as open in October: funding to explore a promising direction or carry out concrete work in AI safety or biosecurity, up to $20,000. [linkedin](https://hr.linkedin.com/in/sean-honan)

Opening soon

* SPAR. Spring 2027 applications open around December. It’s a part-time, remote research program pairing aspiring researchers with professionals addressing risks from AI, so you can do it while keeping your job. It’s a good way to test the field and get a research credit before you quit. [sparaisparai](https://sparai.org/?utm_id=fall-25-apps)
* MATS Residency, a stretch option: the next application window opens in March 2027. The Bridge track is for industry professionals from adjacent fields who already have research expertise but need a dedicated runway to build a credible AI safety portfolio, and it pays $155,000–$285,000 (USD, gross), depending on your Residency track. It’s a better fit after a SPAR project or similar. [Applications for the 2027 Winter intake open on August 25th, 2026 and close on October 31, 2026 (AoE) +2](https://forum.effectivealtruism.org/posts/QQQqTfTsw8GJnESep/announcing-the-mats-residency-a-new-path-for-experienced)

Just missed, but they recur

* MATS Winter closed September 6. It pays a $6,400/month stipend plus housing and food, and it welcomes technical researchers without prior ML experience. Watch for the summer round. [effectivealtruismeffectivealtruism](https://forum.effectivealtruism.org/posts/Cb8Py9osCsZeuCetn/mats-winter-2027-applications-are-now-open)
* Pivotal (London) closed November 1.
* Anthropic’s new Conceptual Reasoning Fellowship covers philosophy, cognitive science, economics, policy, and law and pays $100,000 to $167,000 for the four-month fellowship period. It closed October 28, but your philosophy degree makes the next round worth watching. [businesstoday](https://www.businesstoday.in/technology/story/anthropic-opens-applications-for-2027-stem-conceptual-reasoning-fellowships-how-to-apply-562044-2026-10-16)[scalevise](https://scalevise.com/resources/anthropic-stem-conceptual-reasoning-fellowships/)

A sensible order: apply to Anthropic ML Systems and Coefficient Giving now, start SPAR in the spring while still employed, and quit once you have an offer. Most of these programs only last 3–5 months, so plan savings for the time after.
Sources:

* [Extern – Anthropic Fellows 2027 guide](https://www.extern.com/post/anthropic-fellows-program-guide)
* [Anthropic Fellows posting (Index)](https://www.indexventures.com/startup-jobs/anthropic/anthropic-fellows-program-ai-safety-security/)
* [GovAI Summer Fellowship 2027](https://www.governance.ai/post/uk-summer-fellowship-2027-research-track)
* [Coefficient Giving / Open Phil CDTF](https://openphilanthropy.org/career-development-and-transition-funding)
* [SPAR](https://sparai.org/?utm_id=fall-25-apps)
* [MATS Residency (EA Forum)](https://forum.effectivealtruism.org/posts/QQQqTfTsw8GJnESep/announcing-the-mats-residency-a-new-path-for-experienced)
* [MATS Winter 2027](https://forum.effectivealtruism.org/posts/Cb8Py9osCsZeuCetn/mats-winter-2027-applications-are-now-open)
* [Anthropic STEM & Conceptual Reasoning Fellows](https://scalevise.com/resources/anthropic-stem-conceptual-reasoning-fellowships/)
* [LinkedIn list of open programs (BlueDot)](https://hr.linkedin.com/in/sean-honan)


[Claude is AI and can make mistakes.](https://support.anthropic.com/en/articles/8525154-claude-is-providing-incorrect-or-misleading-responses-what-s-going-on)
Claude finished the response
Export

## Claude

*2026-11-10 12:04*

I'll look into who's working on formalizing rules and specs for AI, and which mentors and fellowship streams match it. I'll run both searches in parallel.

## You

*2026-11-10 12:04*

would this have been good for me https://generatorresidency.org/

## Claude

*2026-11-10 12:04*

Mostly yes. You'd be a strong fit, but you've missed this round, and it's in person in Berkeley.

**Why it fits**
- It's for building things, not research. Generator says it's for "builders, operators, and organizers" and sends people who want to do technical research to other programs. You've said you usually enjoy building the tool most, so this suits you better than research programs like MATS.
- They want people with a track record of shipping. Your two public repos and your time as volunteer CTO and then CEO of TeCanal are good evidence of that.
- The pay works if you quit your job: an $8,500 monthly stipend, plus travel to Berkeley.
- The Self-Directed track lets you pitch your own project. A tool that turns agent policies or model specs into readable, checkable rules, basically your ADICO engine pointed at AI agents, would be a natural pitch.

**Why it might not**
- You'd have to be at the Constellation office in Berkeley for the full three months. You've been torn on the West Coast, though three months is a lot less than moving.
- The Winter 2027 cohort closed November 1 and runs January 18 to April 9, 2027. The site has a sign-up for future rounds.

I'd sign up for the next round and use the time to build a small demo of the spec tool, which would also make a good application for other programs. The two searches I started (who's working on formalizing rules and specs, and which fellowships fit that work) are still running. I'll add their results when they come back.

## Claude

*2026-11-10 12:05*

The first search is done; the fellowship search is still running. The headline: lots of people are formalizing AI specs and policies, but none of them use Ostrom's ADICO grammar or check institutions with a solver the way your engine does. As far as the search found, that's an open niche.

**Closest to your engine**
- **Ostrom applied to LLM agents (Max Planck, AAMAS 2026).** Gupta, Rahwan and others ran AI agents in an Ostrom-style shared-resource simulation, where agents propose norms, vote on them and punish violators. The norms are written in free text, so encoding them in ADICO would be a natural follow-up. [arXiv](https://arxiv.org/abs/2510.14401)
- **Formally verified law as a reward signal (June 2026).** An LLM translates legal text into a Catala-like formal language and a verifier checks it. That's the same "LLM proposes, checker decides" setup your engine uses. [arXiv](https://arxiv.org/abs/2606.23913)
- **Plain language → Cedar policies.** AWS Bedrock AgentCore now enforces Cedar policies between agents and their tools, and lets people write those policies in plain English. Papers like "Autoformalization of Agent Instructions into Policy-as-Code" and AutoCedar automate the translation. [AWS](https://aws.amazon.com/blogs/security/why-policy-in-amazon-bedrock-agentcore-chose-cedar-for-securing-agentic-workflows/) · [arXiv](https://arxiv.org/abs/2606.26649)

**The most interesting counterpoints**
- **Gillian Hadfield (Johns Hopkins), "Building AI for the Democratic Matrix" (Mar 2026).** She argues agents need "normative competence": the ability to infer and adapt to norms that are incomplete and changing, rather than follow fixed rule sets. She also proposes institutions that produce model specs. This is the strongest challenge to static ADICO encoding, and worth answering in your docs. [Knight Institute](https://knightcolumbia.org/content/building-ai-for-the-democratic-matrix-a-technical-research-agenda-for-normative-competence-and-normative-institutions-1)
- **Joel Leibo (DeepMind), theory of appropriateness (Mar 2026).** He grounds norms in the question "what does a person such as I do in a situation such as this?" and separates explicit norms from implicit ones. ADICO only covers the explicit ones. [arXiv](https://arxiv.org/abs/2603.14050)

**The landscape**
- **A June 2026 survey of how LLM agents are specified, verified and constrained** concludes that writing the specification is the bottleneck. In the studies it reviewed, only about 25–34% of translations from plain language into formal specs were correct. [arXiv](https://arxiv.org/abs/2608.14590)
- **A MATS paper tested models against their own constitutions.** It split Anthropic's constitution and OpenAI's Model Spec into about 200 testable rules. Claude's violation rate dropped from 15% to 2% across versions. [arXiv](https://arxiv.org/abs/2605.24229)
- **ARIA's theory teams** are building specification and world-model languages, including multimodal Petri nets, protocol specification and event structures. The Petri-net and protocol work is the closest to treating institutions as formal systems. [ARIA](https://aria.org.uk/opportunity-spaces/mathematics-for-safe-ai/safeguarded-ai/funded-projects)
- **The Cooperative AI Foundation** put out a memo on governing multi-agent AI (Sep 2026), with Leibo among the contributors. [CAIF](https://www.cooperativeai.com/post/new-memo-establishing-foundational-principles-and-thresholds-for-multi-agent-ai-governance)

One pitch this suggests: ADICO plus a solver as a readable, checkable layer for agent norms, sitting between plain-language model specs and enforcement languages like Cedar. That would work as a Generator or fellowship project. The fellowship results will follow when that search finishes.

## Claude

*2026-11-10 12:05*

The fellowship search is back. No paid fellowship is specifically about formalizing specs, policies or norms, so the realistic route is to fund your own project and line up the right mentor for next cycle.

**Act on now**
- **Coefficient Giving career transition funding** is the best match for "quit and skill up." It's rolling with no deadline, and you could pitch "ADICO + solver as a checkable norms layer for agents" as your independent project. It's usually a one-off grant, so plan for that. [Listing](https://www.effectivealtruism.org/opportunities/recNkZ1ZEObw1aQVI)
- **AI Safety Camp 2027** opened participant applications Nov 7, with the close date not given, so apply soon. It's online and part-time, January to April, and probably unpaid. You can join or propose a project on specs or norms while keeping your job. [Post](https://www.lesswrong.com/posts/PvnACayHxr9FEmTfF/project-lead-applications-for-ai-safety-camp-2027-are-open)
- **Anthropic Fellows** has the best pay: $3,850 a week, remote in the US is allowed, and no PhD is needed. None of its tracks is about formal methods, though. Your earlier chat found that the ML Systems and Economics & Policy tracks are rolling; confirm the next cohort.

**Line up for next cycle**
- **MATS Summer 2027.** Krishnamurthy Dvijotham's stream on "formal methods for specifying safe agent behaviors" is the closest structured match to what you want. Watch for the application window. [MATS FAQ](https://www.matsprogram.org/faq)
- **Generator's next round** suits the builder version of this project.
- **The Secure Program Synthesis Fellowship** covers formal methods, AI and security, especially specification. It's part-time and remote; the 2026 round closed in May and is unpaid by default, though you can request a stipend. [Post](https://www.lesswrong.com/posts/RmKGiB8xmPK2hGmB9/applications-open-for-the-secure-program-synthesis)

**Project grants, which need a team or a fiscal sponsor**
- The Cooperative AI multi-agent safety fund is the best fit on topic but is between rounds. ARIA has rolling calls but funds organizations, not individuals. Foresight's latest round closed October 31.

Here's an order that fits all this: apply to AI Safety Camp now and build a small demo there. Then use the demo to apply for Coefficient funding and MATS Summer. Several dates came from secondary pages, so check them on the official sites before you rely on them.

## You

*2026-11-10 12:05*

so bascially we could be trying to experiement via swarm dynamics

## Claude

*2026-11-10 12:05*

Yes. Swarms of LLM agents give you a cheap, repeatable testbed where rules can be tested, not just written down, and your projects are already set up for it.

**How it would work**
- **Rules layer:** encode the institution in ADICO, tagged formal, norm or shared strategy. Your engine already does this.
- **Enforcement layer:** a gate checks each agent action against the formal rules, the way Cedar sits between agents and tools.
- **Agents:** LLM agents with roles and goals, and possibly Bicchieri-style expectations about what others do and what others think they should do.
- **Measure:** whether a rule change sticks, gets absorbed, or gets displaced. Whether agents find loopholes, which is reward hacking happening in front of you. Whether informal norms emerge to fill gaps.

**Two experiments in one**
1. **Human institutions (computational liberation).** This would be the dynamics layer you already planned in the family-systems chat: remove a rule from the marriage bundle and watch where its job goes.
2. **Alignment for AI agents.** Test which rule structures keep agent groups safe: what gets gamed, and when agents collude. That's the multi-agent safety area the Cooperative AI Foundation funds, and the Hugging Face incident shows it's a real risk.

**Precedents**
- The Max Planck AAMAS 2026 paper ran LLM agents through an Ostrom-style shared-resource game with voting and punishment. Its norms were free text, so yours would be the version where the rules are formal and checked.
- DeepMind's Concordia library, from Leibo's group, is built for exactly this kind of agent-based modeling with generative agents.

**Caveats**
- LLM agents aren't people. They're trained to be agreeable and they know the textbook outcomes. For the human-institution use, validity is the main risk. Your falsifier test still applies: check that the setup rediscovers known historical patterns before you trust anything new it says.
- Results can swing with prompts and model versions, so preregister predictions and run many seeds.
- For the alignment use, the AI agents are the actual subject, so the validity problem goes away.

A good first project would be rerunning that Max Planck setup with ADICO rules and a solver gate, then comparing it with the free-text-norm version. It's small, new, and works as a pitch for AI Safety Camp, Generator or Cooperative AI funding.

## You

*2026-11-10 12:06*

could i test some of the agent stuff with my claude plan do some reseracah into swarm dynamics on my own? and see what other peoples are doing in this space so that i could do alignemnt tewsting

## Claude

*2026-11-10 12:09*

I'll check what your Claude plan can do here, and start a search on who's testing alignment with multi-agent swarms.

Yes, you can do this on your own. Claude Code is the easy way to build the harness. For the swarm runs themselves, use API credits rather than your plan's chat usage, plus cheap open models for most of the agents.

**What your Claude plan covers**
- **Claude Code** comes with Pro, Max and Ultra, and it's a good tool for writing the simulation harness and your engine integration.
- **Max and Ultra include monthly API credits:** Max · $100 Ultra · $200. They cover the Claude API, Managed Agents and the Agent SDK, but the credits don't apply to: Interactive Claude Code in the terminal, IDE, desktop, or web. Pro doesn't get them.
- **Running the Agent SDK while signed in to your plan** works too, but it uses up your regular plan limits. The terms say advertised usage limits for Pro, Max, and Ultra plans assume ordinary, individual usage of Claude Code and the Agent SDK, so for thousands of agent calls an API key is the cleaner fit.
- **The cost math works out.** SanctSim reports about $1 per run with DeepSeek-V3 and about $7 with GPT-4o. $100 a month buys a lot of runs if most agents are open models (Qwen or DeepSeek through OpenRouter) and Claude is used for comparison runs.

**What other people are doing (search results)**
- **GovSim** is a fishery, pasture and pollution commons simulation. In 43 of 45 runs the LLM agents depleted the shared resource. It's MIT-licensed and supports Anthropic, OpenRouter and local models. [GitHub](https://github.com/giorgiopiatti/GovSim)
- **SanctSim** is a public goods game where agents choose whether to have sanctions. Reasoning models like o1 drift toward free-riding. [GitHub](https://github.com/davidguzmanp/SanctSim)
- **CoopEval (2026)** found LLMs mostly defect unless there's a formal mechanism: cooperation scored 0.80 with contracting versus 0.07 with none. That's a strong result for your rules-engine approach. [Project](https://xiao215.github.io/CoopEval/)
- **Agent-C** converts temporal rules into logic, and Z3 checks every tool call. Rule conformance rose from 77% to 100% for Claude Sonnet 4.5. It's the closest existing version of your solver gate. [GitHub](https://github.com/structuredllm/agent-c)
- **Collusion work:** NARCBench detects agents colluding by probing model activations, and a 2026 Rutgers paper tests whether algorithmic pricing collusion survives different game rules. UK AISI found that coordinated agents slip past per-agent monitors. These make good stress tests later.
- **Concordia (DeepMind)** has the richest agent and world setup but is the heaviest to run. A NeurIPS 2025 paper using it found agents weakest at persuasion and norm enforcement.

**The open niche:** none of the searches found anyone combining ADICO or institutional grammar with a solver and LLM agents.

**A first project:** fork GovSim, encode the fishing rules in ADICO, and compile them to Z3 to gate each harvest, borrowing Agent-C's checking loop. Then compare collapse rates with rules as prompt text versus rules enforced by the solver. It's cheap, the 43-out-of-45 baseline makes any effect easy to see, and it's a ready-made application project for AI Safety Camp or Generator.

Sources:
- [Monthly API credits for Max, Ultra, and Team plans](https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-ultra-and-team-plans)
- [Claude Code legal and compliance](https://code.claude.com/docs/en/legal-and-compliance)
- [GovSim paper](https://arxiv.org/abs/2404.16698v1)
- [SanctSim paper](https://arxiv.org/pdf/2506.23276v2)
- [CoopEval](https://arxiv.org/html/2604.15267)
- [Agent-C](https://arxiv.org/abs/2512.23738)

## You

*2026-11-10 12:10*

is there a reasong why we would do it in ADICO / institutinoa grmammar? is there somethign that is better in this than other apporaioches? we dont want novelty for its own skae

## Claude

*2026-11-10 12:11*

Yes, but only for some questions. For plain permission gating ("may this agent call this tool?"), ADICO adds little over Cedar or temporal logic. It earns its place when what you're studying is how the institution itself works: sanctions, informal norms, and how rules change.

**What ADICO gives you that the alternatives don't**
- **It separates kinds of rules.** Remove the "or else" sanction and a rule becomes a norm; remove the "must/may" as well and it becomes a shared strategy. Cedar and temporal logic only express enforced rules. If you want to test whether norms without sanctions hold up among agents, or whether a strategy hardens into a norm, you need that three-way split. Your displacement question also depends on it, since a removed rule's job often moves into a norm.
- **Sanctions are explicit.** Who enforces, and what happens on a violation, are fields in the rule rather than buried in code. CoopEval and SanctSim both found that enforcement mechanisms change outcomes, so you need to vary them cleanly.
- **Rules about changing rules.** Ostrom distinguishes everyday operating rules, collective-choice rules (how the operating rules get changed), and constitutional rules (who sets the collective-choice rules). That's the frame for agents that vote on or rewrite their own rules, which is the self-modification and corrigibility question in institutional form.
- **Comparability with human institutions.** Decades of policy and commons research already code real institutions in this grammar. Encoding agent rules the same way lets one dataset cover both your human-institution work and AI agent work. That's the strongest reason specific to you.
- **Readability.** Non-programmers can review a rule card, which you've already said you want.

**Where it's weaker**
- **It's a schema, not a logic.** It has no built-in meaning; you still compile it to Z3 or a temporal logic underneath. ADICO is the authoring layer, not the checker.
- **Coding is unreliable.** Different people code the same rule differently. That's a known problem, and you've seen it yourself: your review council found results baked into the encodings.
- **Cedar is more mature for authorization,** with tooling, analysis and production use. Agent-C's temporal rules already handle sequencing.
- **Hadfield and Leibo's point:** real norms are incomplete and implicit, and any fixed encoding misses that.

**How to keep it from being novelty for its own sake**
Make ADICO earn its place experimentally:
- **Baselines:** rules as free-text prompts, rules gated by Cedar or temporal logic only, and ADICO compiled to Z3.
- **Preregister a hypothesis only ADICO can test.** For example: "norms without sanctions decay faster than sanctioned rules, and a removed rule's function shows up in emergent norms."
- **If the ADICO arm tells you nothing the simpler arms don't,** drop it and use Cedar. That's the same falsifier discipline you already use in your claims register.

So use ADICO as the human-facing, comparable layer, use existing logics to do the enforcement, and keep it only if it measures something the others can't.

## You

*2026-11-10 12:12*

okay but is there ways to get the same benefits of this elsewhere? otherwise we need ACIDO or we need to pibvot to something else for swarm dyanmics understanding riules and such

## Claude

*2026-11-10 12:12*

Mostly yes. There's a whole older field, normative multi-agent systems (NorMAS), that formalizes norms, violations and sanctions for software agents, and most of its frameworks predate LLMs. Only one of ADICO's benefits is really unique to it.

**Alternatives to each benefit**

| ADICO benefit | Alternatives that provide it |
|---|---|
| Separating rules, norms and strategies | NorMAS distinguishes *regimented* norms, which the system makes impossible to break, from *regulated* norms, which can be broken but carry a sanction. That maps exactly onto your solver gate versus sanctions. Bicchieri-style game-theory models cover informal norms held up by expectations. |
| Sanctions as explicit fields | Defeasible deontic logic (Governatori), which handles "if you violate X, you owe Y" chains, and LegalRuleML, an OASIS standard with penalty statements. |
| Executable semantics | InstAL (Padget and colleagues, Bath) models institutions in answer-set programming: what counts as an institutional act, who is empowered to do what, violations and sanctions. It can be checked and simulated directly. |
| Roles and organizations | MOISE and the JaCaMo platform (roles, missions, norms), and Electronic Institutions (IIIA-CSIC). |
| Readability | Cedar, Catala, and ODRL, a W3C policy language built around permissions, prohibitions and duties. |
| Rules about changing rules | Partly covered: MOISE supports reorganization. Ostrom's three levels of rules are best developed in the Institutional Grammar tradition. |
| Comparability with real human institutions | **Basically unique to the Institutional Grammar.** Only it has decades of real-world institutions coded in one schema. LegalRuleML and Catala cover law specifically. |

**What this means for you**
- **For pure swarm and alignment testing,** you don't need ADICO. NorMAS gives you established semantics, a clean regimented-versus-regulated variable to test, and existing tools like InstAL. The new contribution would be bringing LLM agents into a field that mostly studied scripted agents.
- **For connecting human institutions and AI agents,** which is your computational-liberation angle, ADICO is the only option with existing human-institution data.

**You don't have to choose all one way**
- Keep ADICO, or its extended version IG 2.0, as the authoring and comparison layer.
- Borrow NorMAS semantics underneath: regimented norms compile to your Z3 gate, regulated norms to sanctions, using InstAL-style or deontic logic.
- Run "regimented vs regulated vs free-text norms" as the experiment's main variable. It's an established distinction in that literature, and it's exactly the mechanism-versus-training question you started this conversation with.

The decision comes down to whether the human-institution comparison matters to you. If it doesn't, pivot to NorMAS and InstAL. If it does, keep ADICO as the front end and use NorMAS ideas underneath. Either way you're building on existing theory rather than inventing a new formalism.

## You

*2026-11-10 12:13*

what does the comparisin buy us? i mean yeah is it worth keeping? i want learnings to be generalizable in an easy manner? or like be able to draw parallels and stuff in a provable way whatever makes that easy maybe

## Claude

*2026-11-10 12:14*

On its own, the comparison buys you less than it seems. Two systems written in the same schema just look alike. To prove a parallel, you need both systems in one shared formal model, plus a structure-preserving map between them. ADICO gives you the first look, not the proof.

**What makes a parallel provable**
1. **Common semantics.** Both systems compile into the same kind of model, for example a state machine of who can do what and what follows, or an InstAL-style answer-set program.
2. **A mapping** between the two models: this role corresponds to that role, this sanction to that one.
3. **Property preservation.** There's a standard result here: if two systems are *bisimilar*, meaning each can match the other's moves step for step, they satisfy exactly the same temporal-logic properties. So a proof like "no one can be trapped without exit" carries over automatically. A weaker "simulation" map transfers safety properties in one direction.

That's what makes learnings generalize easily. You prove a property once and transfer it through the map, with no need to argue by analogy.

**What this means for ADICO**
- Your generalizability comes from the shared semantic layer, not from ADICO. Any front end works as long as it compiles to that layer: ADICO for human institutions, Cedar or temporal logic for agent rules.
- ADICO is worth keeping as an import format, because existing coded datasets of real institutions use it. That's cheap to keep and gives you real data. It isn't the core of the system.
- Your engine already has an isomorphism-detection stage. Upgrading it from matching shapes to checking bisimulation or simulation, with property transfer, would turn "these look alike" into "this result provably carries over."

**Existing tools for this**
- **Labeled transition systems and model checkers** (nuXmv, TLA+). These have the most mature bisimulation tooling.
- **Compositional game theory ("open games," Ghani and Hedges).** Games are built from parts, and those parts can be compared formally. That's a natural fit for institutions as games.
- **ARIA's category-theory teams** (Petri nets, double categorical systems). Their whole approach is formal models whose maps preserve structure, which is the provable-parallels idea made general.

**Suggested next step**
Pick one shared semantic core; a transition system is the simplest and best tooled. Compile both a human institution, like the marriage bundle, and an agent-swarm rule set into it. Then try to prove one parallel, such as "removing the exit bar has the same effect in both." If that works, you have generalizable, provable learnings, and ADICO stays only as one way of writing the input.

## You

*2026-11-10 12:15*

does this even make sense tho? to try to make sense of human norms through agent swarm dynamics? or is that maybe better left as a furture project?

## Claude

*2026-11-10 12:15*

Mostly leave it for later. The direction that makes sense now runs the other way: use what's known about human institutions to understand and govern AI agents.

**Why LLM swarms are weak models of humans**
- **They aren't independent samples of people.** They're trained on human writing, including the textbook results you'd be testing, so they can reproduce Ostrom because they've read Ostrom.
- **They're too uniform.** Models from the same company produce similar norms; the Max Planck paper found this. They're also trained to be agreeable, so free-riding, spite and defiance get under-represented.
- **Results are fragile.** Outcomes can shift with prompts and model versions.
- Using LLMs as "silicon samples" of people is a contested research area. Without calibration against real human data, findings don't carry over to humans.

**What does make sense now**
1. **Proofs about rule structures.** A proof like "this rule set allows a trapped state" holds for any agents that fit the model's assumptions, human or AI. You don't need realistic agents for that part, and it's where your provable parallels live.
2. **Swarms to study AI agents themselves.** Here the agents are the real subject, so the validity problem disappears. This is alignment testing.
3. **Human institutions as a source of hypotheses for agents.** Take Ostrom's design principles (graduated sanctions, monitoring, a voice in changing the rules), test whether they keep agent groups safe, and have the proofs show which structural results transfer.

**Later, and only with calibration**
Using swarms to learn about human norms. Your existing falsifier is the gate: first check that the swarm rediscovers known human patterns, like the Married Women's Property Acts backtest. Only if it reliably does would you trust it on anything new.

So for now: proofs about rules, plus swarms for AI agents. That also keeps the alignment project separate from computational liberation, so neither one depends on the other's hardest open question.

## You

*2026-11-10 12:17*

who ekse is stuying agent swarm dynamics for alignment and being able to eovlutionary design and sumualte formal mechainsm beds to approzmiate alignment values?

## Claude

*2026-11-10 12:19*

I'll start a search on this.

Several groups are now evolving or searching over rules for agent groups, but the search found no one who combines that with formal guarantees. That's the gap your engine fits.

**Searching over rules and institutions**
- **"Evolving Interpretable Constitutions" (ICML 2026)** is the closest match to your idea. An LLM-driven genetic algorithm evolves the norm sets that agents follow in a survival grid-world. The evolved constitutions scored about 123% above human-designed baselines and eliminated conflict. The catch is that the rules are free text with no formal meaning. [arXiv](https://arxiv.org/abs/2602.00755)
- **"When Agents Evolve, Institutions Follow" (Apr 2026)** encodes seven historical political institutions as multi-agent architectures. The best and worst differed by more than 57 percentage points, and which institution worked best changed with model capability. The arXiv page lists code. [arXiv](https://arxiv.org/abs/2604.27691)
- **AgentBreeder (Foerster, Oxford; NeurIPS 2025)** evolves multi-agent setups for safety and reports a 79% average gain on safety benchmarks. It searches over agent setups, not rules. [GitHub](https://github.com/jrosseruk/AgentBreeder)
- **DeepMind** used AlphaEvolve to evolve algorithms for solving games. That's a precedent for the search loop, not for designing mechanisms.

**Formal mechanisms tested with LLM agents**
- **"Institutional AI" (Jan 2026)** is the closest to your transition-system framing. A public governance graph defines legal states, transitions and sanctions, and a runtime controller enforces it. Severe collusion in a market game fell from 50% to 5.6%, while prompt-only rules didn't help reliably. The graph is hand-designed and has no proofs. [arXiv](https://arxiv.org/abs/2601.11369)
- **A mechanism-design framework for agent negotiation (Jul 2026)** found that guarantees proven for the mechanism don't carry over to LLM behavior: one model bid truthfully in every trial, another in 3.3%. [arXiv](https://arxiv.org/abs/2608.14613)
- **CoopEval (Conitzer and Jin)** found contracts and mediators work best, and that evolutionary pressure strengthens mechanisms. Jin's group also wrote an ICML 2026 position paper arguing multi-agent systems need institutional design, not just model-level alignment.
- **LLM Economist (2025)** has an LLM planner design tax schedules for up to 100 agents. It follows Salesforce's earlier AI Economist.

**Norm institutions**
- **Hadfield's "Normative Modules"** has agents learn which classification institution their group treats as authoritative, with coordinated sanctions raising welfare. Its vocabulary is close to ADICO. The search found no 2025–26 follow-up.
- **Christopher Frantz's IG Parser** is tooling for Institutional Grammar 2.0. It's the natural front end for what you'd build.

**What nobody seems to be doing yet**
1. **Searching over formally specified rule sets.** Current work evolves free text or hand-built graphs.
2. **Proof-checked search.** Z3 would reject candidate rule sets that break invariants, such as deadlock, conflicting rules or disproportionate sanctions, before any simulation money is spent.
3. **Bisimulation as the bridge between simulation and proof.** You'd measure where LLM behavior departs from the formal institution, which is exactly the failure the negotiation paper found. You could also merge rule sets that behave identically so the search doesn't test them twice.
4. **Reproducibility.** Most of these papers have no code link the search could find. A small, deterministic core checked by a solver would stand out.

**People to follow**
1. **Zhijing Jin's group, with Vincent Conitzer** (CoopEval, the position paper): the most direct audience for a formal front end to cooperation benchmarks.
2. **Gillian Hadfield, with Joel Leibo's Concordia team at DeepMind:** the conceptual home of normative infrastructure.
3. **Christopher Frantz plus the Institutional AI authors:** IG tooling plus governance graphs that have no formal analysis yet. Foerster's group is worth following for working evolutionary-search code.

**Caveats**
- Some of those affiliations came from the model's background knowledge rather than fetched pages, so confirm them before reaching out.
- Before committing, search the older normative multi-agent "norm synthesis" literature. It predates LLMs and may overlap with this idea.

Your project could be one sentence: evolve institutions in a formal rule space, gate candidates with proofs, and use bisimulation to measure where LLM agents depart from the rules. That works as a pitch for MATS, Generator or Coefficient funding.

## You

*2026-11-10 12:20*

yeah i like that is there anything that we could do today to start on? and lets make sure we check that we really are doing novel work and why other people might not have done this yet bc i feel like i wouldnt be first to a lot of these things why would i have a core insight that hteyre lackjing

## Claude

*2026-11-10 12:22*

I'll run two checks in parallel. One is a strict search for prior art, including older formal multi-agent work that may already cover this. The other looks at your public repos to see what you can build on today.

## You

*2026-11-10 12:22*

yreah make sure that you remmeber the things that i like think and beleive about formal design and proof and approach into why i want to work on this project what im interested and have been thinking aboutm etc.

## Claude

*2026-11-10 12:23*

Here's what you can start today, based on what's already in your repos. The prior-art check is still running, and I'll pass on the novelty verdict when it's back.

**A first task for this afternoon (a few hours)**
Your engine already has most of what this needs. `philengine/rules_reference.py` has a brute-force engine that explores every state step by step (`initial_states`, `successor`, `compliant_step`), and your tests already cross-check it against Z3. Building on that:
1. **Add `philengine/rules_lts.py`** with a function `export_lts(inst, k=3)`. It walks every state reachable within *k* steps and outputs a labeled transition system: states, plus edges labeled by the action that fired. It should flag when it hits the state cap or the depth bound, and report that as "open" rather than safe, consistent with your existing verdict rules.
2. **Add `phil rules lts --inst ID --k N`** to `cli_rules.py`. It prints the system as JSON or DOT, and you'd run it only on the `data/example/` fixtures.
3. **Add `tests/test_rules_lts.py`** to check that traces read off the exported system match `Reference.traces()`.
4. **Bonus:** a `check_action(inst, state, action)` function of about 30 lines on top of the same code. That's the first version of the solver gate for LLM agents.

Bisimulation comes next, as a new `rules_bisim.py` that reuses the mapping `rules_iso.match` already finds. That would upgrade your isomorphism check from "these look alike" to "these behave alike up to depth *k*."

**Your own repo conventions to respect**
- Write expected verdicts and commit them before running anything.
- Add a new ADR for the transition-system and bisimulation design.
- Have the review council check it before you call anything a result.
- Dual-use guardrails: ADR 0011 forbids searching for the cheapest way to keep a property violated or an exit revocable. The evolutionary search will need checking against that.
- `plans/worth-it-slice.md` says everything else pauses until it reports back. You'll need to decide whether this project waits for it, or whether this goes in its own repo since it's the alignment project, not computational liberation.

**On "why would I be first?"**
That's the right question. Part of the answer will come from the novelty check, because the formal multi-agent literature on "social laws" and norm synthesis from the 1990s–2010s may already cover the proof-gating piece. If it does, your contribution narrows to connecting that older formal work to LLM agents and measuring where they deviate. That can still be real, but we'll know exactly which part is new.

I've also saved your thinking on this, including why you want to work on it.

## You

*2026-11-10 12:23*

naw but also for the implementation i want it to be reperenseting in a rational doc or osmething for a new repo proejct we doing

## Claude

*2026-11-10 12:23*

I'll draft the rationale doc now. When the prior-art check finishes, I'll fold its findings into the novelty section.

## You

*2026-11-10 12:23*

why use phil engine?

## Claude

*2026-11-10 12:23*

You don't have to build on it, and for the core you probably shouldn't. It's useful as a translator from ADICO, but bisimulation and model checking are better handled by tools built for them.

**Reasons to reuse it**
- The ADICO schema, the YAML-to-JSON build, and the readable rule cards already exist.
- Its reference engine is cross-checked against Z3, so its rule semantics are tested.
- It already has rule matching and ablation, plus review, preregistration and provenance habits.
- You wrote it, so you understand its design, which is the "theory of the program" point from your citizen-engineers chat.

**Reasons not to make it the core**
- **It's built to be small.** The repo itself describes the reference engine as exponential and for tiny institutions only, and its checks only go to a fixed depth *k*. Evolutionary search would run thousands of candidates.
- **Writing your own bisimulation is novelty for its own sake.** mCRL2, from TU Eindhoven, already builds transition systems, reduces them up to several kinds of bisimulation, compares two of them, and checks temporal properties. nuXmv and TLA+ are other mature options.
- **The rules it carries don't fit this project.** Its plan pauses other work until the "worth-it" slice reports. ADR 0011 bans searching for the cheapest way to keep a property violated, and adversarial search is part of alignment testing. Building inside it would mean fighting those rules or bending them.
- **It's in Python and Z3 by design,** while this project's center of gravity is model checking.

**What I'd recommend**
- A new repo for the alignment project.
- ADICO stays as the human-readable authoring format. A small adapter compiles it to mCRL2 or a similar tool, reusing philosophy-engine's schema, and possibly its reference engine, as a check that the translation is correct.
- mCRL2 handles the transition systems, bisimulation and property checks.
- A runtime gate for LLM agents, which could be your own code, or Cedar or Agent-C style.
- GovSim or SanctSim as the agent testbed.

That way the novel part is the combination and the measurement, not reimplemented machinery. Your existing engine becomes one of the inputs, not something the new project depends on.

I'll write the rationale doc around this setup unless you'd rather keep philosophy-engine as the base.

## Claude

*2026-11-10 12:24*

*Attached file: RATIONALE.md*

## You

*2026-11-10 12:24*

why would you recommend that ? but yeah if you have things you are going to create we should prolly have them be subagents so they dont block the main thread and you can commuincate messagesrefineinments as they run if you heed ot

## Claude

*2026-11-10 12:24*

I've drafted RATIONALE.md for the new repo. It's written around keeping philosophy-engine as an input rather than the base, so if you disagree with that call, that part needs revising.

**Why I recommended it**
The core of this project is building transition systems, checking bisimulation, and running thousands of candidate institutions through a search. Philosophy-engine was built for something else: careful, bounded checks on a few small institutions. Its own docs say the reference engine is "for tiny institutions only."

Two of its own rules would also get in the way. Its plan pauses all other work until the "worth-it" slice reports back. And ADR 0011 bans searching for the cheapest way to keep a property violated, which robustness testing needs.

Mature tools like mCRL2 already do bisimulation and model checking. Rebuilding that inside your engine would be the novelty for its own sake you said you want to avoid. So the doc keeps philosophy-engine's ADICO schema, and possibly its reference engine as a check on the translation, without building inside it. If you'd rather keep it as the base, I can revise D1.

**What the prior-art check found**
- **Already done:** model-checking rule sets, designing social laws and equilibria, norm synthesis, LLM-evolved constitutions, and runtime governance graphs. You can't claim any of these.
- **Apparently open (about 70% confident):** a single pipeline that searches over rules written in ADICO, proof-checks candidates before simulating them, and measures how far LLM agents' behavior departs from the formal institution.
- **Two 2026 papers explicitly name this gap and leave it unfilled.** One says governance graphs should be formally checked but gives no toolchain. The other says model checking has never been connected to LLM agents' conformance.
- **Why nobody has combined it:** the formal-methods and LLM-agent communities rarely overlap, and the result may not pay off. The strongest objection is that proofs about idealized agents mean nothing when LLM agents don't follow the rules. The doc builds experiments E1 and E3 to test exactly that, with kill criteria if gating or the deviation measure adds nothing.

Your edge isn't one new idea. It's having a foot in all three communities: data-quality engineering, philosophy plus a working ADICO-to-Z3 engine, and the habit of preregistering and reporting negative results.

From now on I'll hand building work to background agents so this conversation stays free, and pass along your refinements to them as they run. A good first one would be the repo scaffold plus milestone 2: export the GovSim fishery quota as a transition system and cross-check it against your engine. Tell me what to call the repo and I'll start it.

## You

*2026-11-10 12:25*

lets hand this off by creating a new github repo and hten will pick up locally on compiuter?

## You

*2026-11-10 12:26*

yeah why are we doing instititnios?

## Claude

*2026-11-10 12:26*

"Institution" crept in from Ostrom and the multi-agent papers we were reading, and it's probably the wrong frame for what you're after.

**What it meant here**
"Institution" just meant a set of rules plus sanctions that governs a group of agents: who may do what, under what conditions, and what happens if they don't. It came in through ADICO, which is Ostrom's grammar for human institutions, and through the multi-agent papers, which use the same word.

**Why it might be the wrong frame**
- **It carries human-institution baggage,** and we already agreed to leave modeling human norms for later.
- **It quietly made the project multi-agent.** Your original question was simpler: can we make unethical behavior impossible through mechanism rather than training? That applies to a single model or agent just as well.
- **The core idea doesn't depend on the word.** The core is that rules for AI get written formally, checked by proofs, and enforced, and then you measure where the AI departs from them.

**Two ways to frame the project**
1. **Single-agent rules.** Turn a model spec or policy into formal rules, proof-check them, gate the agent's actions with a solver, and measure how far it deviates. This is closer to your first question and simpler to start.
2. **Multi-agent rules.** The same pipeline, but for groups of agents, where sanctions, collusion and emergent norms come in. That's where the swarm dynamics and evolutionary search you liked fit, and where the prior-art gap was clearest.

Option 2 is option 1 plus interactions, so you could start with 1 and grow into 2. In either case I'd call it something like rule systems or agent policies rather than institutions, and drop "institution" from the repo name.

Which do you want as the core? Once you pick, I'll revise the rationale doc and set up the repo.

## You

*2026-11-10 12:26*

multi agent rules i think

## You

*2026-11-10 12:27*

but i am interested in single agent too - are they really different questions stho?

## Claude

*2026-11-10 12:27*

They're mostly the same question. Single-agent is the base case of the same pipeline, and multi-agent adds what only shows up when agents interact.

**What's shared**
For one agent or many, the steps are the same: write rules formally, proof-check them, gate actions with a solver, and measure where the AI departs from the rules. A single agent is just the case with one agent.

**What only appears with several agents**
- Sanctions by peers, not just by a fixed gate.
- Collusion, and coordinated attacks that individual monitors miss. UK AISI found this.
- Norms that emerge and drift over time.
- Rules about changing the rules, like voting or self-governance.

So the plan is to start single-agent and grow into multi-agent. The first experiment would be one agent under the fishery-quota rules, comparing free-text rules with solver-gated ones. Then the same setup with several agents, where the interaction effects come in.

A background agent is building the repo now. It's revising the rationale to say "multi-agent rules" instead of "institutions," adding the single-agent framing you just raised, and creating the scaffold. Since you didn't pick a name or visibility, it's using **reeswrites/multi-agent-rules** and making it **private** for now. You can rename it or make it public later. I'll send the link once it's pushed, and then you can clone it on your computer.

## Claude

*2026-11-10 12:29*

The repo is built and committed, but I couldn't create it on GitHub: this session is only allowed to work in repos that already exist, so the create request was refused. The whole scaffold, one commit included, is in multi-agent-rules.tar.gz, and the revised RATIONALE.md is attached on its own too.

**Fastest way to pick it up on your computer**
1. Create an empty private repo at github.com/new named `multi-agent-rules`, with no README so the first push doesn't conflict.
2. Unpack the archive and push:
   ```
   tar xzf multi-agent-rules.tar.gz && cd multi-agent-rules
   git remote add origin git@github.com:reeswrites/multi-agent-rules.git
   git push -u origin main
   ```
If you'd rather I push it, create the empty repo and tell me. I'll connect it to this session and push from here.

**What's in it**
- **RATIONALE.md** now frames the project as "Multi-agent rules: proof-gated rule search for AI agent groups." It treats single-agent as the base case of the same pipeline, and the first experiment (S1) is one agent under the fishery rules, free-text versus solver-gated. ADICO is only the format for writing rules, and human institutions are a source of hypotheses, not the subject.
- **docs/**: the plan, a claims register with S1 and E0–E4 waiting to be preregistered, ADRs 0001 (new repo and stack) and 0002 (ADICO as authoring format), files for surprises and negative results, and the review-council convention.
- **Also included:** README, CONTRIBUTING with your conventions, an Apache-2.0 license, a .gitignore, and empty `src/` and `tests/`.

**Two small notes**
- The commit's git author is set to a default Claude identity. Run `git commit --amend --reset-author` before pushing if you want it under your name.
- The license text came from the system's standard copy, because apache.org was blocked here.

The next task is milestone 1, a repeat of the prior-art check. Milestone 2 is exporting the fishery-quota rules as a transition system and cross-checking it against your engine.

## You

*2026-11-10 12:30*

yes can you push it if u canhttps://github.com/reeswrites/multi-agent-rules

## Claude

*2026-11-10 12:31*

I pushed it, so github.com/reeswrites/multi-agent-rules now has the scaffold and rationale on `main`, in one commit.

To pick it up on your computer:
```
git clone git@github.com:reeswrites/multi-agent-rules.git
```

The commit's git author is a default Claude identity, not you. If you want your name on it, run `git commit --amend --reset-author` and force-push. Since the repo is brand new, that's safe.

The first item in `docs/plan.md` is to repeat the prior-art check. After that comes the export of the fishery-quota rules as a transition system, cross-checked against philosophy-engine. I can start either one in the background now, or you can take it from here on your computer.
