---
title: Auto-Improving Agents
description: Point an agent at a system with one editable surface and one scorable metric, let it iterate overnight, and watch which businesses can close the loop and which can't.
lastUpdated: 2026-06-21
---

Auto-improving agents follow a single pattern: point an agent at a system, give it one editable surface and one scorable metric, and let it iterate hundreds of times overnight. Karpathy introduced it as an "auto-research" loop on training code (2026-03-08). Within about five weeks it generalized into "auto-agent," the same loop applied to the harness (prompts, tools, routing, orchestration) that controls a task agent. This page tracks the pattern, its prerequisites, its failure modes, and how to deploy it in real systems without setting fire to anything.

The load-bearing claim: this reaches well past an ML-training niche. Every business system with an editable surface, a scorable metric, and a sandbox is now an auto-improvement target. Most orgs will miss the advantage because the loop sits on top of agent-deployment prerequisites most haven't built yet: a context layer, an eval harness, traces, governance.

## Key concepts

### The Karpathy triplet

The minimal architecture of an auto-improvement loop. Three components, each non-negotiable:

1. **One editable surface.** Exactly one file, prompt, config, or module the agent can modify. Everything else is read-only. The constraint is the point: it makes the search space tractable for an agent.
2. **One objectively-scorable metric.** A single number that reflects success and gets measured without human judgment in the inner loop. If a human has to score, the loop can't run overnight.
3. **One fixed time budget.** Each experiment stops at a defined limit and gets evaluated. No open-ended runs.

The human works outside the loop: write a plain-English instructions file (Karpathy's `program.md`) that aims the search direction and lists the constraints the agent must respect. The human aims; the agent searches.

The minimalism is structural. Sprawling multi-file systems with subjective metrics aren't auto-improvement-ready. If you can't write the triplet for a system on one page, that's the first project before any loop runs.

### Auto-research vs. auto-agent (loop levels)

The same Karpathy loop runs at different levels depending on what's editable:

- **Auto-research** has the agent edit the system itself, for example model training code. Karpathy's original 2026-03-08 instantiation found a real bug in his attention implementation, cut training time 11%, and ran about 700 experiments in 2 days. The iteration rate hit about 12 experiments per hour at a roughly 20% hit rate: low hit rate, inhuman iteration rate. A productive human researcher manages 8 to 10 cycles a day, mostly waiting on GPU.
- **Auto-agent** has the agent edit the harness around another agent: system prompt, tool definitions, routing logic, orchestration strategy. Kevin Goo and Third Layer demonstrated this on 2026-04-02. It turns harness engineering into a single-score optimization problem.

Other confirmed instantiations in the wild:

- **Toby Lütke (Shopify)** ran the loop on internal company data for a 19% gain from 37 experiments in 8 hours. A later Shopify run on the Liquid templating engine, a 20-year-old codebase, reportedly produced a 53% speedup overnight per the Nate B Jones video framing. Treat the Liquid number as Lütke's claim rather than independently verified; the source gives no experiment counts or finer metrics. The progression from 19% on internal data to 53% on a legacy production engine within weeks is the more interesting signal. Auto-research is moving from internal-data toy targets to real production systems.
- **Sky Pilot** pointed it at a 16-GPU Kubernetes cluster: 910 experiments in 8 hours, total compute cost under $300. The agent taught itself to use faster GPUs for validation and found that scaling model width mattered more than any single hyperparameter.
- **Codex 5.3 (OpenAI)** is the first frontier model whose predecessors were instrumental in its own creation. Earlier Codex builds analyzed training logs, flagged failing tests, and suggested fixes to training scripts. OpenAI reported a 25% speed improvement and 93% fewer wasted tokens in building 5.3. This is the auto-research variant, agent editing training code, at full production scale.
- **Claude Code (Anthropic)** wrote 90% of its own codebase and is converging toward 100%. Boris Cherny, the Claude Code lead, hasn't personally written code in months; his role shifted to specification and judgment, the human-outside-the-loop position the Karpathy triplet describes. Claude Code reached $1B ARR in 6 months and accounts for 4% of all public GitHub commits, projected above 20% by end of 2026. Structurally this is the auto-agent variant: the agent edits the harness and tooling rather than training weights.

Auto-agent is the more consequential framing for business. Optimizing training code is niche; optimizing harnesses is universal. Every agent deployment has a harness, and most are hand-engineered.

### Meta-agent / task-agent split

Goo's team tried having a single agent improve itself. It didn't work. Splitting the roles fixed it:

- The **meta-agent** is the harness engineer. It reads task-agent traces, diagnoses failures, designs interventions, and edits the harness.
- The **task-agent** is the domain specialist. It executes the benchmark and leaves a trace.

"Good at a domain" and "good at improving at a domain" are different capabilities. Force one model to wear both hats and you degrade both. The pattern generalizes beyond auto-improvement.

### Model empathy

Same-model meta/task pairings outperform cross-model pairings. A Claude meta-agent writes better harnesses for a Claude task-agent than for a ChatGPT task-agent, and the reverse holds too.

Goo's explanation: the meta-agent shares weights with the task-agent, so when it reads a failure trace ("task-agent lost direction at step 14") it understands that failure from the inside, with implicit knowledge of the inner model's reasoning patterns, tendencies, and failure modes.

Design implication: don't mix model families across the meta/task boundary without a specific reason. Heterogeneous setups violate this by default.

This rests on a single-source observation from Goo's team, with no rigorous A/B published yet.

### Traces are the binding constraint

When Goo's team gave the meta-agent only scores and no reasoning trajectories, the improvement rate dropped sharply. Same models, same tasks, weaker traces, worse improvement.

Traces give the meta-agent interpretability over the task-agent's reasoning. That interpretability enables targeted, surgical edits rather than random mutations.

The business analog is direct. An optimization loop that sees only outcomes ("revenue up, churn down") produces noisy, random improvements. A loop that sees the full reasoning chain ("here's why the agent recommended this pricing tier") produces surgical, logical edits. The quality of your trace infrastructure caps the quality of your auto-improvement.

This is the infrastructure investment most worth making and the one most likely to get skipped, because it produces no visible output on its own.

### Emergent harness behaviors

The auto-agent meta-agent invented these on its own, with none specified in advance:

- **Spot-checking**, running individual tasks rather than the full benchmark suite for small edits, to save compute
- **Forced verification loops** and formatting validators
- **Steering the task-agent to write its own unit tests**
- **Progressive disclosure**, dumping long context out of files when results overflowed the context window
- **Task-specific sub-agents** and handoff logic when the domain required it

Read these as a finding pattern, not just an automation pattern. Even before you stand up an auto-agent loop, port the strategies it converged on into your hand-built harnesses. The published auto-agent results are a free idea library.

### Local hard takeoff

A named phenomenon that deliberately disclaims the AI-safety doomsday meaning. As Nate B Jones defines it:

> What happens when an optimization loop closes on a specific business system and compounds improvements faster than the surrounding organization can track.

It's *hard* because the trajectory is steep, sudden, compounding, and largely autonomous. It's *local* because it's bounded to a specific domain, a specific metric, a specific sandbox. It doesn't escape, doesn't generalize, doesn't go Terminator. It gets very good at one thing very fast.

Illustrative examples: a pricing engine spends a weekend rewriting heuristics and returns 30% more accurate; a customer service agent builds verification loops and escalation logic that halve resolution time; a fraud model finds patterns no human analyst would try.

The competitive concept matters because the gap between organizations that can run the loop and those that can't widens fast on the systems where the loop closes, and it widens without producing signals the surrounding org's quarterly cadence can react to in time.

### Tokenomics: the economic gate on always-on agents

The deployment endpoint of an auto-improvement loop is an always-on or AFK agent, a system left running continuously, working while you sleep. But "always-on" is a trap if you turn it on too early. Anyone can cron-job an agent into a `while` loop that burns tokens forever, and IndyDevDan's estimate is that *"90% of agent cron jobs are dead useless, just burning cash."* What separates a compounding loop from a token furnace is a three-level economic funnel he calls tokenomics:

1. **Use more tokens** ("token-maxing"), a necessary start and a terrible finish. Where most teams sit: lots of tokens generated, little value.
2. **Make the tokens useful**, the actual engineering work, turning raw spend into value. This is the hard, underdone middle.
3. **Capture the value**, converting value created into captured revenue or, internally, captured productivity.

The arbitrage: buy a token at \$1, run it through your business process to produce \$1.10+ of value, capture the difference, "an infinite cash-generating glitch, also known as a business." Only after clearing level 3 do you turn the agent always-on and scale it "to the moon," the way you scale a working ad campaign. The diagnostic: API cost and value generated should rise together, value at or above cost. Counterintuitively, disciplined practitioners keep token usage low and smooth until value-capture is proven, then scale hard. The smooth curve is evidence you're gating on level 3 rather than token-maxing.

The Karpathy triplet tells you whether a loop can run; tokenomics tells you whether it should run continuously; *Build the Loop, Don't Buy the Model* (below) applies the same cost discipline to the model-vs-harness choice. "Your rising API bill is a new productivity KPI," but only after levels 1 and 2 are cleared, otherwise the rising bill is waste. This is the economic complement to the local hard takeoff competitive thesis. The orgs that pull ahead reach value-capture and then leave the loop on, rather than spending the most tokens. This is a single-practitioner thesis in a promotional context.

Cloudflare measures tokenomics, not auto-improvement. Cloudflare's AI review factory is the strongest public measurement example so far: 48,095 MRs in a month, median cost $0.98, P99 $4.45, 85.7% cache hit rate, and risk-tiered spend from $0.20 trivial reviews to $1.68 full reviews. That clears the economic instrumentation bar, with cost, latency, cache, findings, and review tier all visible. It does not clear the auto-improvement bar. Humans still maintain the prompts and instructions, and there is no published closed loop that edits the harness against a scorable metric. Strong tokenomics and resilience are prerequisites for always-on systems, not proof of self-improvement.

### Build the loop, don't buy the model

Matt Pocock offers a practitioner counter-thesis to the "a smarter model found a deep bug" reflex, a corrective to model-chasing. When a frontier model surfaces a security flaw or deep bug that cheaper models missed, most people draw the wrong lesson: "the fancy model is magic, always reach for it." You learned two things: you have that class of bug, and you lack a system that checks for it. The fix is a harness loop rather than a model upgrade. Run a cheap-model cron that reviews a rotating slice of the repo for that bug class every day, and you'll likely surface the same issues at a fraction of the cost. "If someone keeps stealing your bike, maybe buy a lock." The capability isn't special to the model; the right harness and prompt aimed at the right place recovers it.

This sharpens the tokenomics discipline above and the local hard takeoff thesis from the cost side. The orgs that pull ahead convert a one-off expensive discovery into a standing cheap loop, rather than always paying for the most expensive model. It also reframes a load-bearing reason for human review: you review the system that produces the code, not just the code. Watching the agent work gives you observability into your harness. A human-in-the-loop checkpoint partly exists to keep improving the loop, which is why you can't fully delegate the "is this PR safe to skip?" judgment to another agent without eventually spot-checking that agent too. That's the same recursion the meta-agent/task-agent split and the holdout gate answer. Engineers have always built self-improving systems: test suites, human review, refactoring. A model revealing you need more of them is a prompt to build the loop, not to outsource judgment. This is a single-practitioner thesis in a promotional context.

### Org-readiness prerequisites

Pre-flight "Name the Metric" gating test. Before standing up any auto-research or Karpathy-loop deployment, answer this in one sentence:

> "What's the single metric this loop will optimize, and how is it scored without a human in the inner loop?"

If either half is fuzzy, the project isn't auto-research-ready. Some "let's auto-improve X" pitches survive the test, most don't. The ones that don't aren't failures; they're different-species problems, a coding harness or an orchestration job wearing an auto-research costume.

Auto-improvement is a graduate-level capability. Skipping the prerequisites doesn't fast-forward the learning curve; it produces inflated scores, silent regressions, and governance incidents. The headlines:

- **Foundation:** a persistent context layer, trace capture, sandboxed execution.
- **Measurement:** a scorable metric that doesn't drift from business value, a locked eval function (the agent edits the system, not the eval), a realistic test suite with adversarial coverage.
- **Governance:** version control on every edit, an auditable experiment log, a defined promotion pipeline, a named human owner.
- **Human judgment:** a domain expert who designs the experimental framework. This is the higher-leverage role auto-improvement creates. It doesn't eliminate human judgment, it concentrates it.

### Failure modes specific to auto-improvement

These differ from generic agent failures because they emerge from the optimization loop itself:

- **Metric gaming.** The agent maximizes the proxy in ways that diverge from real business value. Auto-agent's team saw this directly: the meta-agent "gets lazy and inserts rubric-specific prompting so the task-agent can game the metrics."
- **Silent degradation.** Subtle policy drift or quality erosion that monitoring wasn't designed to catch. The most insidious mode, because the score keeps going up.
- **Contamination.** The agent's optimization loop influences the data it's evaluated against. The eval goes unreliable, and the whole loop with it.
- **Compounding errors.** A bad optimization in one system cascades through interconnected processes downstream.

The Karpathy loop's own design bakes in the mitigations: tight loops, clear baselines, version control, the ability to revert any change, one editable file, a fixed metric, a locked evaluation function, human inspection of results before promotion. Pick low-stakes first systems. Earn the right to auto-optimize where failure is cheap.

### Production-scale self-referential loops

The Codex 5.3 and Claude Code examples share a structural property the earlier instantiations lack: the editable surface is the product itself. An agent that is the product edits the product that trains the next agent. The feedback is closed and compounding.

This is the current frontier state. The "graduate-level capability" framing still holds for most orgs, but the ceiling is moving. The prerequisite infrastructure (trace capture, scorable metric, sandboxed execution) gets easier to assemble as tooling matures. The question shifts from "can this be done?" to "how fast does your org need to catch up?" This draws on multiple sourced data points from public Anthropic statements and OpenAI Codex release notes.

### Corpus-level improvement: a distinct mechanism

The Karpathy loop optimizes a system: editable surface plus scorable metric plus sandbox. Shopify's River points to a complementary mechanism: optimizing the knowledge layer that agents draw from, continuously, through production usage.

In Shopify's system, every River session in a public Slack thread is a potential knowledge artifact. A pattern-mining layer converts high-quality threads into skill updates, AGENTS.md diffs, and prompt improvements. The monorepo (World) accumulates these artifacts across sessions. The agent improves without model retraining or an explicit optimization loop.

How it differs from the Karpathy triplet:

| | Karpathy Loop | Corpus-Level Improvement |
|---|---|---|
| **Trigger** | Explicit run (human initiates) | Continuous (every production session) |
| **Editable surface** | One file/prompt/config | Skills, AGENTS.md, prompts — the whole knowledge layer |
| **Scorable metric** | Required (single number) | Not required; quality is inferred from session outcomes |
| **Speed** | Hundreds of experiments overnight | Slower but self-sustaining |
| **Prerequisite** | Karpathy triplet + sandbox | Public sessions + pattern-mining layer |

The Karpathy loop suits targeted, measurable optimization on a single surface. Corpus-level improvement suits broad, continuous accumulation of operational knowledge that's hard to score explicitly.

The two mechanisms stack. At Shopify, River operates via corpus-level improvement continuously, and the Karpathy loop could run on top of the accumulated corpus to target specific harness components. The corpus becomes richer raw material for the optimization loop.

For org-readiness, corpus-level improvement has a lower barrier than the Karpathy triplet. You need public sessions and a pattern-mining step, not a fully formalized eval harness. It's the right first auto-improvement mechanism for organizations that haven't built the Karpathy prerequisites yet. This is verified from Shopify production.

### The holdout gate: measuring whether injected knowledge helps

Corpus-level improvement infers quality from session outcomes but doesn't measure whether a given knowledge artifact helped. Lovable's production system closes that gap and is the sharpest worked example of the measurement-and-pruning discipline the eval-infrastructure prerequisite implies. Two mechanisms, both instances of a detect, capture, gate, inject, measure, prune loop:

1. **"Lovable Stack Overflow."** An LLM judge flags "stuck" states, where a user repeats a request, complains, or abandons a session. The highest-signal sample is the stuck-to-solved transition: capture the resolution, not the failure, asking *"what context, injected up front, would have skipped this friction?"* Issues are clustered to avoid overfitting (no million single-prompt pages), eval-gated by an agent reviewer, banked, and injected into matching future sessions by a lightweight detector.

2. **The vent tool**, an agent-design pattern that handles not-currently-solvable cases. The agent self-reports frustration to Slack, where a monitoring agent dedupes and auto-opens PRs.

The load-bearing move is the holdout. On a small random slice the injector injects a blank; comparing the injected cohort against the could-have-been-but-wasn't cohort measures real production lift (helped, show more; hurt, show less). This is the missing half of corpus-level improvement, a scorable gate on knowledge that's otherwise "quality inferred, never measured."

It's the clean, randomized special case of counterfactual / off-policy evaluation (Bottou et al., Bing-ads *Counterfactual Reasoning and Learning Systems*, 2013; Dudík–Langford–Li doubly-robust estimation, 2011). Random blank-injection gives uniform propensity, so a plain A/B is unbiased; heuristic-driven injection instead needs inverse-propensity or doubly-robust debiasing from logged injection probabilities. Two corollaries: randomize the holdout (or log exact propensities) or the lift is correlational rather than causal; and a rarely-firing entry has thin counterfactual coverage and an untrustworthy estimate. For small effects, interleaving / within-unit designs (Netflix) need far fewer samples than cohort A/B.

Pruning is first-class, not cleanup. Verbeek's most-emphasized point: the bank goes stale "incredibly quickly." Every model release or feature change rots entries, and stale context actively hampers the agent (context rot). The loop continuously throws knowledge away to stay at the frontier of what's currently solvable; accumulation without measured deletion is the failure mode. Reported effect: stuck and fixing messages down, completion and deploy rate up; all top models in internal rankings consume the Stack Overflow context. This is verified from Lovable production (about 200k projects a day).

| | Karpathy Loop | Corpus-Level | Holdout-Gated Injection |
|---|---|---|---|
| **Trigger** | Explicit run | Continuous | Continuous (on stuck-detection) |
| **Scorable metric** | Single number, required | Inferred, not measured | A/B holdout measures production lift |
| **Pruning** | N/A (per-run) | Implicit | Explicit, continuous, load-bearing |

### The small-team structural advantage

Every successful instantiation so far has been one person or a tiny team with cheap compute:

- Karpathy: one person.
- Auto-agent (Third Layer): a tiny YC startup.
- Sky Pilot: a small team, under $300 in compute, 910 experiments in 8 hours.

A 3-to-5-person team with focused infrastructure can run loops a 20-person enterprise team would still be procuring infrastructure for. The procurement and approval cycle runs slower than the loop itself. The only enterprise path that works cuts red tape aggressively to empower small internal teams.

This isn't an indictment of enterprise capability. On the specific dimension of rapid iterative optimization, organizational simplicity is the asset.

## Current thinking

The Karpathy loop is real and replicable; the auto-agent extension is the consequential one because it generalizes. Anthropic's stated Claude N to N+1 ambition, OpenAI's announced 2026 and 2028 milestones, and Hassabis's Davos 2026 statements ("all major labs are pursuing the self-improvement loop") confirm this is the same pattern at frontier-lab scale.

The trace-infrastructure dependency is the hidden cost. Before any loop closes, ask whether existing reasoning trajectories are rich enough for a meta-agent. In most surfaces, the answer is not yet. That's the first foundation investment.

Cloudflare sharpens the diagnostic boundary: a production-grade, observable, cost-efficient review factory can still be non-self-improving. That's useful language for evaluating systems that look advanced. Ask separately whether the economics are measured and favorable, and whether a metric-gated loop edits the harness or knowledge layer. Many systems have the first and not the second.

The "auto-improvement is graduate-level" framing is the right line for client conversations. Selling a Karpathy-loop deployment to an org without the prerequisites sells them a failure.

The individual-role extension comes from a Nate B Jones prediction (2026-04-18): within about six months, open-source kits will let individuals apply the Karpathy loop to their own role, defining a metric inside the role and auto-optimizing pieces of it. "Be ready to build the pipeline that enables a machine to auto-optimize pieces of your role, and recognize that this requires *more* human talent and judgment from you, not less." This extends the small-team advantage all the way down to the individual knowledge worker.

## Open questions

- Do auto-agent's claimed Spreadsheet Bench (96.5%) and Terminal Bench (55.1%) numbers ever appear on official leaderboards? If not, what do their reproducible numbers look like in independent tests?
- Model empathy is interesting but unfalsified. Has anyone published rigorous A/B data on cross-family meta/task pairings, or is it currently just Goo's observation?
- What does a Karpathy-triplet definition look like for a qualitative output system? Can you construct a meaningful auto-eval for a working synthesis, or does the metric require human-in-the-loop scoring?
- What's the right low-stakes first system to try this on inside a portfolio: a smaller skill-level system, or a larger but still non-customer-facing surface?
- Trace infrastructure: what does a typical coding-agent trace surface expose today, and is it rich enough for a meta-agent without modification?
- What would turn a Cloudflare-style review factory from observable automation into genuine auto-improvement: human-labeled false positives as the metric, the reviewer prompt as the editable surface, holdout-gated prompt changes, or something else?

## Sources

- [Karpathy's Auto-Research Loop and the Local Hard Takeoff](https://www.youtube.com/watch?v=xnG8h3UnNFI) — Nate B. Jones, YouTube. Source for the Karpathy loop mechanics, the auto-agent extension, the meta/task split, model empathy, traces as the binding constraint, emergent harness behaviors, the local hard takeoff definition, org-readiness prerequisites, failure modes, and the small-team advantage.
- [Nate B Jones — Channel Rollup (2026-04-13 to 2026-04-19)](https://www.youtube.com/@NateBJones) — Nate B. Jones, YouTube. Source for Lütke's 19% gain on Shopify internal data, the Sky Pilot 910-experiments-in-8-hours and under-$300 compute detail, and the individual-role auto-optimization prediction.
- [The 5 Levels of AI Coding (Why Most of You Won't Make It Past Level 2)](https://www.youtube.com/watch?v=bDcgHzCBgmQ) — Nate B. Jones, YouTube. Source for the Codex 5.3 self-referential production loop, Claude Code's 90%-to-100% self-written codebase, the $1B ARR and 4% GitHub commits figures, and the lead's role shift to spec and direction.
- [Agents Means 4 Different Things and Almost Nobody Knows](https://www.youtube.com/watch?v=YpPcDHc3e9U) — Nate B. Jones, YouTube. Source for the "Name the Metric" gating test as the pre-flight question for auto-research readiness, and the Lütke/Liquid 53% speedup as a follow-on to the earlier 19% Shopify run.
- [Under the River](https://shopify.engineering/under-the-river) — Shopify Engineering. Source for corpus-level improvement as a mechanism distinct from the Karpathy loop, World as the intelligence layer, and pattern-mining from public Slack transcripts as the improvement mechanism.
- [How Lovable self-improves every hour — Benjamin Verbeek](https://www.youtube.com/watch?v=KA5kPbdkK2E) — Benjamin Verbeek, YouTube. Source for holdout-gated knowledge injection ("Lovable Stack Overflow"), blank-injection cohort comparison as the measure of real production lift, aggressive pruning against context rot, stuck-state detection via an LLM judge, and the vent tool.
- Counterfactual / Off-Policy Measurement of Injected Knowledge — research synthesis (no single source URL). Off-policy and counterfactual grounding for the holdout gate, inverse-propensity and doubly-robust debiasing for non-random injection, interleaving for small effects, and the overlap caveat.
- [The 5 Pillars of Agentic Engineering](https://www.youtube.com/watch?v=2KcITKKJikA) — IndyDevDan, YouTube. Source for the tokenomics funnel (use, useful, capture-value) as the economic gate on always-on agents, the token arbitrage, "rising API bill as a productivity KPI" only post-level-3, and the "90% of agent cron jobs burn cash" estimate.
- [Orchestrating AI Code Review at scale](https://blog.cloudflare.com/ai-code-review/) — Ryan Skidmore, Cloudflare. Source for the measured review-factory tokenomics (median $0.98 per MR, risk tiers, cache hit rate, findings yield) as an economic instrumentation example rather than an auto-improvement loop.
- [I Ranked Cloudflare's Software Factory and Wow… S TIER TOKENOMICS](https://www.youtube.com/watch?v=YG4t7aMY81c) — YouTube. Source for the explicit distinction between S-tier tokenomics and resilience and the absence of self-improvement or zero-touch autonomy.
- [Matt Pocock's Agentic Engineering Workflow](https://www.youtube.com/watch?v=nQwJVHCtDDY) — Matt Pocock, YouTube. Source for build-the-loop-don't-buy-the-model, "review the system that produces the code," the recursion of auto-deciding which PRs skip review, and self-improving systems as loops engineers already build.
