---
title: Agent Design
description: Principles and patterns for building AI agent systems that produce reliable, predictable outcomes across harnesses, task suitability, autonomy, error recovery, multi-agent workflows, and the analytics that steer them.
lastUpdated: 2026-06-09
---

This collects principles and patterns for designing AI agents and agent pipelines that produce reliable, predictable outcomes. It covers how agents invoke tools and skills, how to handle failures, how to calibrate autonomy, how to test, and how to coordinate multiple agents. The design layer sits on top of a production-platform layer (session durability, execution isolation, orchestration substrate, shared tools) that has its own concerns; this page stays with design.

## Key concepts

### Harness: a working definition

Pin this term first, because everything else depends on it. An agent is a model plus a harness. The model is the reasoning substrate: weights and inference. The harness is everything else, all the software wrapped around the model that turns a raw LLM into a goal-directed, tool-using, self-correcting agent. The canonical analogy: the LLM is the CPU, the harness is the operating system. Swap the harness and the same model behaves differently. Swap the model and the harness still works, better or worse. That separability is why harness engineering stands on its own as a discipline.

The 2026 consensus component list (across Fowler, Parallel, Daily Dose of DS, and Firecrawl) puts these inside the harness:

- Orchestration loop: the thought, action, observation cycle that drives each turn.
- Tool layer: schemas, sandboxed execution, result parsing, observation formatting.
- Memory and state: short-term working memory, long-term persistence across sessions.
- Context construction: what gets assembled into each prompt, when, and how it gets compacted when it overflows.
- Output parsing: turning raw generation into structured actions.
- Error handling and retries: detection, classification, recovery, fallback chains.
- Verification loops and guardrails: sensors that check the agent's output before it propagates.
- Subagent dispatch and inter-agent routing, once the system spans more than one model call.

What sits outside the harness: model weights, training, fine-tuning, the model's internal reasoning, anything that requires changing the model itself.

Fowler's two-axis taxonomy helps when you design one. Guides are feedforward: docs, rules, and scripts that steer the agent before it acts, raising the odds of a good first attempt. Sensors are feedback: linters, tests, and reviewer-agents that catch errors after it acts, enabling iterative self-correction. Both can be computational (deterministic, fast, cheap) or inferential (LLM-based, nuanced, slower, more expensive). Every harness design picks points on both axes.

Three related words get used loosely across the industry. Scaffolding is the temporary setup work to get the agent to its first run, a one-time configuration. Prompt engineering crafts one input at a time to get the best response from the model. Harness engineering is the ongoing practice of designing the whole system that decides what the model sees and what happens to its output, across every turn. Prompt engineering is one duty inside harness engineering, not a substitute for it.

The word "harness" itself carries a few distinct meanings worth disambiguating. The generic sense is Fowler's, the whole system above. A "coding harness" names a specific deployment of harness plus model aimed at software work with a human in the loop as manager; it is an instance of the generic sense, not a redefinition. An "eval harness" is the scoring infrastructure that evaluates an agent's outputs, different machinery from the agent's own harness, sharing only the word. Read that one as "eval-harness" when ambiguity bites.

The reason this matters for design: two systems running the same underlying model can be radically different agents because their harnesses differ. When an agent system underperforms, the model is usually the wrong first suspect. The harness is where the leverage lives and where most design decisions actually happen.

Web references: [Fowler — Harness Engineering for Coding Agent Users](https://martinfowler.com/articles/harness-engineering.html); [Parallel — What is an Agent Harness](https://parallel.ai/articles/what-is-an-agent-harness); [Daily Dose of DS — Anatomy of an Agent Harness](https://blog.dailydoseofds.com/p/the-anatomy-of-an-agent-harness); [Firecrawl — What Is an Agent Harness](https://www.firecrawl.dev/blog/what-is-an-agent-harness).

### Memory as a harness component: storage, injection, recall

Memory and state is one of the harness components above, and like the others it is a design surface with explicit choices rather than a single feature. A useful decomposition splits any agent memory system into three jobs, each evaluated on its own:

- Storage: saving a fact. Two orthogonal dials. Trigger (automatic hook versus agent-decided) and form (verbatim versus summarized). Verbatim keeps everything but stays bulky; summarized runs lean but the agent decides what survives. Agent-decided triggers leak, since unflagged facts never persist; a hook guarantees capture at the cost of noise.
- Injection: what loads into context at session start. Dials: source (hook-loaded and always-in versus agent-pulled judgment call) and cap (bounded versus unbounded). Uncapped injection guarantees completeness but bloats every turn, the storage-side cause of context rot.
- Recall: retrieving something old on demand. Dials: search type (keyword, semantic, hybrid) and return shape (raw chunks, reranked, or a cited answer). A cited answer that can say "not present" beats a chunk dump the agent has to re-derive from, the same provenance-over-confidence principle as deterministic evidence-grounding in code review.

The design move is best-of-breed assembly: score the three jobs on their own, patch the weakest with one targeted add-on, and prefer owning the seams (legibility, portability across harnesses) over adopting a monolith. A multi-tier short-circuit, checking the cheap injected snapshot first and falling through to deep search only if needed, is the standard token-cost optimization.

The underlying patterns here are established practice: hybrid BM25 plus vector plus reciprocal rank fusion plus cross-encoder rerank; MemGPT and Letta tiered memory ([arXiv:2310.08560](https://arxiv.org/abs/2310.08560)); cited RAG with abstention. One caveat: cited RAG is not the same as faithful RAG. Up to 57% of citations can be post-rationalized ([arXiv:2412.18004](https://arxiv.org/abs/2412.18004)), so the "tells you exactly where it came from" property needs faithfulness checks, not just citations.

### Four species of agent systems

Before designing any specific agent system, classify what kind of system it is. By 2026 the word "agent" had splintered into four structurally distinct species, and most production misfires are category errors, using the wrong species for the problem shape, rather than wrong-model or wrong-framework problems.

The four species:

1. Coding harness. A single agent (or small cluster) acts as an engineer; the human is the manager. Two scales: individual (one developer plus one or N parallel single-threaded agents) and project (planner agent plus short-running executor sub-agents). Defining property: a human is in the loop on each meaningful decision.
2. Dark factory. A spec-in, software-out pipeline. Humans own intent at the top and acceptance at the bottom; the middle runs fully autonomous. Defining property: no human inspects the middle. Most enterprise deployments are not ready for this. Amazon's recent post-incident huddle with senior engineers is a canary.
3. Auto-research. Metric optimization in a loop: one editable surface, one scorable metric, one fixed time budget. Defining property: the metric is the goal. Tobi Lütke's Liquid speedup is the canonical 2026 enterprise-CEO instance.
4. Orchestration. Specialized-role agents handing work off (writer to editor to publisher; LangGraph, CrewAI). Defining property: the agents have different jobs, not the same job at different stages. Cost lives in the handoffs, not the agents, so it only pays off at high handoff volume (tens of thousands of handoffs, not hundreds).

Run a problem-shape diagnostic before picking tools or frameworks. First: is the problem software-shaped, metric-shaped, or workflow-shaped? That narrows you to coding harness or dark factory, auto-research, or orchestration. If software-shaped: human in the middle, or only at the boundary? That decides coding harness versus dark factory. If metric-shaped: can you name the single metric in one sentence and score it without a human in the inner loop? That separates genuine auto-research from a force-fit.

Cursor's empirical lesson on scale: three management levels degraded performance; planner plus executor (two levels) held. So at project scale, don't add a third layer inside the project. Systems that span multiple projects need a supervision layer above the per-project orchestrators that operates on a different axis (portfolio, not project).

The most common production misfires:

- Using auto-research to build software (no metric means no loop).
- Using a long-running coding harness to write a novel (wrong goal shape).
- Using orchestration when the problem is actually a dark factory (handoff overhead with no volume to amortize it).
- Pretending to run a dark factory when the org won't actually let the middle be unsupervised, which produces an under-supervised coding harness, the worst configuration.

One naming collision to watch: planner-plus-executor "orchestrators" are coding harnesses in this taxonomy, not orchestration. The word "orchestrator" is overloaded across the industry; resolve to species before reasoning about a system.

### Task suitability: what to hand an agent

The single biggest determinant of whether an unattended agent system produces value or slop is task selection, and the major production write-ups tend to skip it. GitHub's official cloud-agent guidance gives the clearest published taxonomy. The governing reframe: treat the issue you assign as a prompt. If the issue description wouldn't work as an AI prompt, it won't work as an agent task.

A well-scoped agent task has three parts:

1. A clear description of the problem or work required.
2. Complete acceptance criteria, what "done and good" looks like (for example, "includes unit tests").
3. Directions about which files change. Semantic code search can often find them, but naming them helps.

Agent-suitable tasks are well-bounded with a clear success signal: bug fixes, UI feature alterations, improving test coverage, updating docs, improving accessibility, addressing technical debt.

Four categories of work stay with humans, and they double as a risk filter:

| Category | Why it fails as an agent task |
|---|---|
| Complex / broadly scoped | Cross-repo refactoring, dependency and legacy understanding, deep domain knowledge, substantial business logic, large changes needing design consistency — exceeds what fits a bounded run |
| Sensitive / critical | Production-critical, security/PII/auth, incident response — the blast radius is too large for unattended action |
| Ambiguous | Unclear requirements, open-ended, requires working through uncertainty — the agent fills gaps by inventing |
| Learning tasks | The human wants the understanding — the value is the human learning, so don't outsource it |

Two connections sharpen this. Task suitability decides whether to hand a task over at all; the ask-versus-act heuristic below calibrates how much autonomy once you do. And "issue as prompt" relocates the bottleneck upstream: the limiting factor isn't agent capability, it's ticket quality. A team that writes vague tickets gets vague code regardless of how good the harness is.

### The no-recovery-loop problem

When you use a tool and get bad output, you see it immediately and correct course. Agents lack this built-in feedback. An agent calling a skill or tool that produces subtly wrong output will propagate that error downstream, possibly through an entire pipeline before anyone notices.

This is the fundamental design constraint for agent systems. Every component an agent touches needs to be robust enough to produce correct results without human intervention, or the system needs explicit checkpoints that validate output before proceeding. Tools and skills built for agent consumption need tighter error handling, clearer failure signals, and more defensive instruction sets than tools built for direct human use.

### Handoffs and contracts

Treat agent-to-tool interactions as contracts. Inputs must be explicitly defined: what the agent sends, in what format, with what constraints. Outputs must be predictable: what the tool returns, how it signals success versus failure. Failure modes need handling: what happens when input is malformed, when a dependency is unavailable, when the output misses quality thresholds.

Loose, conversational interfaces work fine for people, since we adapt. Agents need explicit structure. This applies to skills (via the SKILL.md format), MCP tools, and any API an agent calls. The no-recovery-loop problem above explains why this strictness is load-bearing: without explicit contracts, bad output propagates silently through the entire downstream pipeline.

### Agent-driven tool discovery

Agents discover and select tools and skills through description fields, metadata, and context. The quality of those descriptions decides whether an agent picks the right tool for a job. So every tool in an agent's ecosystem needs a description optimized for programmatic discovery, not just human readability.

### Error recovery patterns

Agent pipelines need self-healing, or you lose half the value of using agents. The field has converged on several named patterns.

Tiered retry. Escalate progressively: original prompt with standard timeout, then add error feedback with reduced temperature, then simplify the prompt with a smaller model, then route to human review. The key is not retrying blindly. By one estimate, more than 90% of retries in ReAct agents waste budget on errors that can never succeed, such as calling tools that don't exist.

Failure classification. Lightweight classifiers predict whether a failure is transient (worth retrying) or permanent (stop immediately) before spending the retry budget. One report puts the reduction in wasted API calls at around 40% in production. A `sameErrorThreshold` pattern stops retrying when identical errors occur 3 times consecutively.

Circuit breaker. If a dependency fails repeatedly within a time window, stop calling it and fail fast. This prevents cascade failures where one broken component drags down the whole pipeline. The pattern is well-established in distributed systems and widely adopted in agent architectures.

Fallback hierarchies. Every critical capability should have layered fallbacks: model fallback (swap to a different model), tool fallback (use cached data when APIs are down), capability fallback (return partial results), and human fallback (escalate when confidence drops below threshold).

Checkpointing. Save state at successful intermediate steps so retries resume from the last checkpoint rather than restarting the whole workflow. Essential for long-running tasks.

Graceful degradation. When components fail and retries are exhausted, keep processing without the failed enrichment, mark records for later retry, and deliver partial results rather than nothing.

Three failure modes need distinct handling: hallucination loops (the agent misreads results and repeats futile actions), tool chain failures (an intermediate step fails and cascades downstream), and context overflow (long-running agents exceed token limits and forget instructions).

### Agent-initiated feedback: the vent tool

Error recovery is the agent healing a failure. The complementary pattern is the agent reporting a failure it can't heal (degraded tooling, docs, or platform behavior) upstream to the people who can fix it. Lovable productionized this as a "vent tool": a send-feedback tool the agent calls when tooling, docs, or platform quality is so low it degrades the work (missing or unsuitable tools, unclear tool names, schemas that don't match expectations, conflicting docs, broken platform behavior, repeated environment-caused failures). Vents route straight to Slack.

Three design points make it work. First, the agent is a better reporter than the user. End users rarely know the cause of a failure; the agent has worked the problem for several turns and holds far more context. Its reports are specific and human-relatable ("I just want to send four numbers, I don't need all this casting gymnastics"), so engineers immediately have the implicit context to act. It surfaced bugs monitoring couldn't see, like a copy tool silently failing on non-breaking spaces from screenshot filenames. Second, frustration-gating buys signal-to-noise. A naive "external reviewer critiques every iteration" produces low signal because most iterations work fine, so you overfit to noise. The vent tool fires only when the agent is really frustrated; tune that threshold until the stream is high-signal. Third, in-line signal economics: the cheapest high-quality reviewer is the working agent itself, because it already holds the context. You generally don't want a top-frontier model re-reading full transcripts as an external reviewer when an in-line self-report is comparatively free.

In operation, the vents feed a monitoring agent that dedupes, investigates, and auto-opens PRs, with humans still in the merge loop. Vent volume doubles as an incident detector, since complaint spikes track platform outages.

### Autonomy levels: when to ask versus act

Multiple frameworks classify agent autonomy. The most practical for AI agents uses five interaction-focused levels:

1. Operator: the human drives, the agent assists.
2. Collaborator: shared control, back-and-forth.
3. Consultant: the agent advises, the human decides.
4. Approver: the agent acts, the human confirms or rejects.
5. Observer: the agent acts autonomously, the human monitors.

The ask-versus-act heuristic: agents should ask for approval when operating in high-uncertainty environments or performing irreversible actions. They can act autonomously in bounded, well-defined domains with clear success metrics and limited consequences.

Design autonomy independently of capability. A highly capable agent can still be required to consult before acting. The level should match the stakes, not the intelligence.

Trust calibration is empirical. Anthropic's research (February 2026) shows Claude Code users naturally grant more autonomy over time: auto-approve rises from about 20% for new users to 40% or more by 750 sessions. Users earn trust through experience rather than declaring it upfront.

One limitation for digital agents: unlike autonomous vehicles with defined operational design domains (specific road conditions), digital agents operate in the internet's infinite, chaotic environment. Clear ODD-equivalents for AI agents remain an open problem. Aviation's veto-window concept (Parasuraman Level 6) offers one balance point: the agent acts, but the human gets a restricted time window to override, trading some speed for safety on time-sensitive tasks.

### Testing agent pipelines

Agent testing has converged on a three-layer architecture:

1. Unit tests: individual functions, tool calls, parsing logic. Deterministic, fast, cheap.
2. Reasoning-trace evaluation: assess the decision-making path, not just the output. Tools like LangSmith evaluate whether the agent chose the right tools and reasoning steps.
3. End-to-end sandbox testing: give the agent a complete task in an isolated environment and measure task completion. The gold standard, but slower and more expensive.

Identical inputs produce varied agent outputs, which makes traditional binary pass/fail assertions insufficient. Agent testing needs statistical evaluation: run the same test multiple times, measure pass rates, compare distributions across versions.

A practical cadence: run a sanity simulation set with strict gates on every prompt or model change, execute the full suite nightly with expanded personas and randomized tool failures, and add safety and compliance sweeps for release candidates. Component tests catch regressions cheaply but miss integration issues; E2E tests catch real-world failures but stay expensive and flaky. Best practice runs both, with heavy component coverage for fast feedback and targeted E2E for critical paths. RAG-specific tools (Ragas, DeepEval) score retrieval precision and generation faithfulness separately, which enables more targeted debugging than a holistic pass/fail.

By one estimate, teams with cross-functional evaluation access deploy features 40 to 60% faster.

### Multi-agent disagreement

When multiple agents work together, disagreement is inevitable. The field has shifted from treating all disagreement as noise toward recognizing some of it as diagnostically valuable.

Disagreement as signal. When similarly capable agents persistently disagree, it often signals the content occupies a contested semantic region where humans would also disagree. AI disagreement can serve as a proxy for human cognitive disagreement, a signal to defer to human judgment rather than force automated resolution.

The majority-pressure problem. Multi-agent debate can suppress independent correction. Extended debate rounds sometimes entrench errors rather than fix them, and a correct minority position can get overridden by confident-but-wrong majority agents. So don't assume more debate rounds produce better answers.

Practical guardrails: "Agent Tennis" detection (flag when two agents disagree on the same point for three or more turns), iteration limits and timeout thresholds, hierarchy-based resolution (a manager agent overrides subordinate disputes), and escalation to human review when disagreement crosses defined thresholds. A lightweight small language model can monitor the primary swarm's logic flow in real time, detecting circular disagreement loops without the overhead of another full agent.

### Meta-agent and task-agent split

When a system has both domain work and improvement-of-the-domain-work as goals, separating those roles outperforms putting both on a single agent. One auto-improvement team demonstrated this directly: a single self-improving agent stalled, but splitting into a meta-agent (a harness engineer that reads traces, designs interventions, and edits the harness) and a task-agent (a domain specialist that executes the work and leaves a trace) made the loop work.

The general principle: "good at a domain" and "good at improving at a domain" are different capabilities. Force one model to wear both hats and you degrade both.

There is also a model-empathy constraint. Same-model meta/task pairings outperform cross-family pairings. The plausible mechanism: the meta-agent shares weights with the task-agent and reads failure traces from the inside, with implicit understanding of the inner model's reasoning patterns and failure modes. Don't mix model families across the meta/task boundary without a specific reason, which is easy to violate by default when you pick the cheapest model per role independently. This rests on a single team's observation, with no rigorous A/B published yet.

### Dynamic workflow design patterns (Claude Code)

Anthropic's June 2026 guide to Claude Code dynamic workflows gives a named vocabulary for multi-agent orchestration shapes. The core premise: a single long-running context window degrades in three specific ways. Agent laziness (it gives up on later tasks), self-preference bias (it over-rates its own output), and goal drift (the original intent erodes through compaction and summarization). Dynamic workflows fix all three by distributing work across many fresh-context subagents instead of accumulating it in one session.

Think of workflows as on-the-fly harness construction: Claude Code builds a task-specific machine on demand, then runs it. Six named patterns describe the shapes that machine can take.

Pattern 1, Classify and Act (Router). A lightweight classifier agent sits at the front of the pipeline, reads each input, and routes it to the correct specialist. It works as a quarantine step: raw input hits a cheap classifier first, and specialist agents only ever see pre-classified, routed work. Use it for inbox triage, issue routing, and multi-domain pipelines with heterogeneous inputs.

Pattern 2, Fan Out and Synthesize (Parallel plus Barrier). Decompose the task into N mutually exclusive slices, assign one subagent per slice in its own clean context (files never cross-contaminate), run in parallel, then merge at a barrier step. The isolation is the point; shared context between agents defeats the purpose. Use it for deep research, due diligence across document sets, and codebase audits. Each agent returns structured output with source citations, and the synthesizer merges into one cited document.

Pattern 3, Adversarial Verification (structural anti-self-preference). Deploy multiple skeptic agents to evaluate an output against a rubric, each working in isolation. This is the structural fix for self-preference bias: it separates the generator from the evaluators so no agent rates its own work. Build the rubric before the workflow runs; the rubric is the quality contract the skeptics push against. Use it for fact-checking AI-generated content, code review, and compliance checks.

Pattern 4, Generate and Filter (overgenerate plus judge). Spin up generator agents to produce a large option space (names, titles, ideas), then apply separate judge agents to filter down. The generator and judge must always be different agents. The value is in the ratio: going from 1,000 to 3 produces better outcomes than 10 to 3. Use it wherever taste matters: naming, copy selection, design direction.

Pattern 5, Tournament (pairwise bracket, recommended for high-stakes selection). A bracket-style elimination where pairs of candidates compete head-to-head, each match handled by a fresh-context agent with no memory of prior matches. Each round can use a different rubric (coarse filters early, precision criteria in finals). It produces an auditable decision trail; you can trace exactly why each candidate advanced or was eliminated. Use it for resume screening at scale, vendor selection, proposal ranking, any high-stakes N-to-1 selection where anchoring and context bloat are risks.

Pattern 6, Loop Until Done (outcome-bounded iteration). No fixed iteration count. Define a specific exit condition rather than a number of retries, then keep spawning new agents with fresh theories until the condition is met. Tell the orchestrator what success looks like, not how many times to try. Use it for flaky test reproduction, exhaustive pattern mining, and bug reproduction where the failure probability per run is low.

Patterns compose. A realistic stack: Fan Out (surface candidates), then Adversarial Verification (filter findings), then Loop Until Done (iterate until a clean pass). You don't have to design stacks by hand; using the vocabulary keywords in the prompt ("fan out", "adversarially verify", "loop until") is enough for Claude Code to compose the right shape.

Workflows multiply token cost, so skip them for basic tasks, single-concern prompts, or anything a strong single-context session can handle. As models improve, the threshold for when a workflow is worth the cost rises. Each workflow is a JS file. A portable package is a SKILL.md plus a workflow.js plus any supporting markdown (rubrics, templates), loaded and shared exactly like skills.

### Production review agents: specialize, scope, fuse

Cloudflare's code-review system is the most concrete production instance of the Fan Out and Synthesize plus Adversarial Verification patterns applied to software review. The design lesson: the reviewer agents are not interchangeable clones. They are specialists with bounded domains, explicit non-goals, structured output, and a coordinator that owns final judgment.

Specialize by failure mode, not by org chart. Cloudflare's reviewers map to review-relevant risk domains: security, performance, code quality, documentation, release, compliance, and AGENTS.md freshness. The split works because each reviewer answers a different question and suppresses a different class of false positives. Seven agents reviewing the same diff generally would multiply noise; seven scoped agents multiply coverage.

Prompt non-goals are load-bearing. Review prompts define what to flag and what not to flag: no speculative risks requiring unlikely preconditions, no unchanged-code issues, no generic library suggestions, no style-only nitpicks unless tied to concrete risk. A role prompt without non-goals invites plausible-but-low-value output. Non-goals are the guardrail that protects downstream human trust.

Structured findings beat prose. Reviewers return severity-classified structured findings, and the coordinator can deduplicate, recategorize, filter, verify uncertain claims with source reads, and apply approval or block policy. If a downstream agent must judge or fuse another agent's work, the handoff format should be parseable and semantically constrained.

Coordinator as judge, not micromanager. The coordinator does not inspect every token of every specialist's reasoning. Its job is fusion: combine findings, remove false positives, resolve severity, decide the outcome. Specialists own narrow analysis; the coordinator owns policy and final synthesis.

Bias toward approval unless risk is concrete. Cloudflare's rubric approves clean MRs and suggestion-only MRs, approves with comments for non-production-risk warnings, and blocks only on concrete production or security risks. A reviewer that blocks on every plausible issue becomes organizational friction and gets ignored.

Stateful re-review is part of the design. Incremental reviews carry prior findings and user replies forward: fixed issues get resolved, user-acknowledged issues stay resolved, disagreements get evaluated, and unfixed findings persist. Review agents become more useful when they remember review state, not just diff state.

### Run-level product analytics: the layer above traces

Engineering traces (Langfuse, Langsmith, and the like) capture execution telemetry: model calls, tool calls, latency, cost, errors. They answer what happened mechanically. They don't answer product questions: did this run matter to the user, and should the product change?

The missing layer is run-level product analytics, one record per agent run that captures:

- Run start: timestamp, user, workflow type.
- Task completion: did the run reach a finish state.
- Acceptance: did the user trust the result, which is distinct from completion, since a user can silently redo the agent's work.
- Mid-run corrections: interruptions, edits, denied approvals, clarifications, task reopens.

Tie all four to the same agent run ID, which is what enables completion rate and correction rate by workflow.

Completion is not acceptance, and the gap between them is the central diagnostic:

| Completion | Acceptance | Signal |
|---|---|---|
| High | Low | Agent finishes work users don't trust — not building trust |
| Low | Low | Users abandoning before reaching a reviewable state |
| Low | High | Too conservative — valuable when it works, but rarely reaches reviewable state |
| High | High | Workflow likely ready for more autonomy |

The completion/acceptance gap reads directly on whether your current autonomy calibration is correct. It connects autonomy levels to empirical measurement: you don't have to guess whether an agent should have more autonomy, the gap tells you.

Corrections are labels. When a user interrupts mid-run, edits an output, denies an approval, or reopens a task, they label that run: what the agent misunderstood, what context was missing, which action felt unsafe. This is why agent analytics and eval belong close together. A denied approval is effectively a test. A failed tool call can become a schema test. An abandoned workflow is a research cue.

The minimum viable schema is three events tied to a run ID: run start, task completion, mid-run user corrections. With these you can compute completion rate and correction rate per workflow and trend them over time.

The rudder principle. Agents can accelerate work 10x to 1000x. The value of that acceleration depends entirely on whether you can shape the direction. Product analytics is the rudder. Engineering traces alone leave you with a fast speedboat and no steering.

### Trace quality caps improvement quality

Give a meta-agent (or any reviewing or improving system) only outcome scores instead of full reasoning trajectories, and the improvement rate drops sharply. One team observed this directly with their auto-improvement loop: same models, same tasks, weaker traces produced worse improvement.

The mechanism: traces enable interpretability over reasoning, and interpretability is what enables targeted, surgical edits rather than random mutations. The quality of your trace infrastructure caps the quality of any downstream optimization, review, or self-correction system, whether the consumer is a meta-agent in an auto-improvement loop, an external AI reviewer, or a human debugger.

For agent system design, trace capture is not optional plumbing. It is the design surface that determines what kinds of review, correction, and improvement become possible at all.

### Org coordination as friction at high automation

Every coordination structure in modern software organizations was built to address a specific human limitation. When the agent does the implementation, those limitations are gone, and the structures that addressed them become pure overhead.

The mapping, from StrongDM's production dark-factory analysis:

- Standups exist because developers on the same codebase need daily sync. Agents don't need sync.
- Sprint planning exists because humans can only hold a bounded number of tasks in working memory. Agents don't have that constraint.
- Code review exists because humans make mistakes other humans can catch. When no human wrote the code, human review often becomes theater, since the diff is too large, too fast, too frequent.
- QA teams exist because builders can't objectively evaluate their own output. Scenario-based external evaluation replaces this structurally.

StrongDM's three-person team runs with no sprints, no standups, no Jira board. They write specs and evaluate outcomes. The entire coordination layer most engineering managers spend 60% of their time maintaining disappears, not as a cost-cutting measure, but because it no longer serves a purpose.

The role shift moves the valued skills from coordination to articulation. An engineering manager moves from "coordinate the team building the feature" to "define the specification precisely enough that agents build the feature." A program manager moves from "track dependencies between human teams" to "architect the pipeline of specs that flow through the factory." The bottleneck is no longer implementation speed; it is spec quality, which is a function of how deeply you understand the system, the customer, and the problem.

Writing a specification detailed enough for an agent to implement correctly without human intervention demands rigorous systems thinking most organizations have never needed from most people. Humans could fill spec ambiguity with judgment, context, and a Slack message. Machines build what you described, so ambiguity produces software guesses, not customer-centric guesses. This skill gap is the primary reason more than 90% of developers stay at Level 2 to 3 in the five-level framework rather than Level 4 to 5.

### Data room pattern: structure the environment before drafting

The structural cause of most 2026 AI hallucinations in serious knowledge work is the working environment around the model, not model capability. Hand an agent a general mess of source material (some current, some stale, some contradicting each other) and ask it to produce a final artifact, and it has to do two jobs at once: figure out what the material is, and produce something from it. That dual-job condition is where hallucinations emerge. The agent fills gaps by inventing, and the prose reads confidently. A sharper prompt won't patch it.

The pattern: build a bounded "data room" (a structured local folder for one job) before issuing any drafting prompt. The agent's first job is to build the room, not to write the deliverable. Once the room exists, the writing prompt becomes short, because the agent already knows what the project consists of and which sources are authoritative.

The first instruction is not "do the thing":

> "Find the relevant materials. Preserve the originals. Build me a data inventory. Tell me which files seem authoritative, which are duplicates, which are old, which are missing. Summarize every source before you synthesize anything. Do not write the deliverable yet."

The agent produces four artifacts inside the room. A source inventory, a table recording path, type, date, apparent authority, current or superseded status, what claims each file supports, its limitations, and how to use it. This is the gate: review it, correct it, and if you can't tell why one file outranks another, fix that before drafting starts. A conflict log surfaces every disagreement between sources (old PDF versus current plan, different names for a stakeholder across docs, numbers with no visible assumptions); a weak workflow lets the agent smooth conflicts silently, a strong one makes them legible before you draft. A missing-context list names what the agent doesn't have to do the job well: the absent data file referenced in only one doc, the current version that's nowhere to be found. Ask for it before drafting or those gaps become hallucination traps. A duplicates report names the version families and confidence levels; the human decides what's authoritative, and the agent never silently resolves duplicates on high-value work.

The writing prompt shrinks because, after the room exists, the only work left is resolving conflicts, telling the agent which source wins. That's judgment a human can provide in a sentence. Before the room, the prompt has to do all the source-disambiguation work that should have happened upstream.

This is for serious, long-running knowledge work: complex deliverables, board docs, legal filings. It's overkill for casual AI interactions. The canonical 2026 case is the Sullivan and Cromwell court filing with dozens of fabricated citations despite premium AI tooling; the structural cause was the unstructured working environment, not the model.

### Brownfield coding agent patterns

These come from six months of production use on a difficult legacy modernization project. Two layers: the workflow structure and the session mechanics that make it durable.

#### Research, Plan, Implement (RPI)

This is the most practically validated pattern for brownfield agentic coding. The core insight: research outputs must become explicit artifacts, not stay in the developer's head. When research stays informal (a ChatGPT chat, mental notes), the agent has no access to it. When research goes into markdown files, the agent can use it as structured context for implementation.

The three steps. Research: ideate with the agent, get feedback, look for alternatives, iterate. The agent's codebase knowledge makes this different in kind from external search, and the research outputs should become explicit folder artifacts (source inventory, conflict log) per the data room pattern above. Plan: run the planning phase, review the plan, write it into a file as external memory, then clear the context. The plan file is the bridge between sessions. Implement: implement against the plan file, updating its todo list along the way. On context overflow, capture the current session to a file, start a new session, and feed it the plan plus the session file.

Frequent intentional compaction is the upgraded version: design the context lifecycle around RPI rather than compacting ad hoc. The guardrails cone is a useful mental model: picture a triangular area for the agent's room for error. Each guardrail (a CLAUDE.md instruction, a plan file, an example, a constraint) narrows the cone. Context engineering is the discipline of narrowing this cone for every significant task. For prompting quality: be as detailed as needed, explain the purpose, and provide examples.

#### Session mechanics

(Here, "session" means a Claude Code context window, the conversational context of a single coding run, distinct from a durable session identity at the infrastructure level.)

CLAUDE.md nesting. The root file runs about 100 lines (hard cap around 300) and covers tech stack, project structure, and conventions. Per-service nested files run about 50 lines (hard cap around 100) and cover service-specific nuances. This is the minimum viable guardrails setup that turns a general-purpose coding agent into a project-aware one.

Disable auto-compact. Default auto-compact pre-allocates buffer space and can produce lossy summaries that pollute later sessions. Use explicit compaction at deliberate breakpoints instead.

Master-clone subagents. When the main context needs to stay clean but a subtask requires noisy tool calls, spawn a clone agent with its own context window. The clone's full trace gets discarded; only the final result returns. Prompt trigger: "use subagents to..."

Two parallel agents is the sweet spot. Two is the practical ceiling for individual practitioners: one for main work, one for background tasks checked between cycles. Three demanded too much coordination overhead.

Human-in-the-loop as governance. Non-negotiable for brownfield. Review every plan file, the agent's steps during complex tasks, every output, and the final code diff before PR creation; have a second agent do a quality review; get colleague approval. This is the comprehension gate at the individual workflow level, and it produces the evidence trail for change management in compliance-sensitive environments.

### Emergent harness behaviors as a finding pattern

An auto-improvement meta-agent independently invented strategies its designers never specified: spot-checking (running individual tasks rather than full benchmarks for small edits), forced verification loops, formatting validators, steering the task-agent to write its own unit tests, progressive disclosure (dumping long context out to files when results overflowed the window), and task-specific sub-agents with handoff logic.

These work as a finding pattern, not just an automation pattern. Even before you stand up an auto-improvement loop, the strategies an autonomous optimizer converges on make good design defaults to port into hand-built harnesses. The published results function as a free idea library for harness design.

## Open questions

- How do you define operational design domains for your own agent workflows, the bounded conditions where full autonomy is safe?
- What's the practical cost of checkpointing in token-limited contexts? Is the state-saving overhead worth it for shorter pipelines?
- How should you handle the majority-pressure problem when running parallel agent evaluations, such as skill testing across multiple runs?
- Does pattern stacking have known failure modes, like an overly aggressive adversarial step eliminating valid fan-out findings, or a tournament converging on a locally optimal winner because of rubric design?
- The loop-until-done pattern has no inherent exit condition for failure. How do you prevent runaway loops when the success condition is never achievable?
- What token-budgeting heuristics stay stable per pattern type? Fan-out scales linearly with N slices; tournament scales as N log N. Are there practical guidelines for when the cost is worth it?
- For review factories, what is the optimal small-team reviewer set? Coordinator plus security plus code quality, or does documentation and release review pay for itself below Cloudflare scale?
- What does "Agent Tennis" detection look like in practice?
- Has anyone other than the originating team replicated the model-empathy finding (better same-family meta/task pairings), or is it still a single observation?

## Sources

- [Anthropic, OpenAI, and Microsoft Just Agreed on One File Format. It Changes Everything.](https://www.youtube.com/watch?v=0cVuMHaYEHE) — Nate B. Jones, YouTube. Source for agent-first design principles, the no-recovery-loop problem, and contract-style interfaces.
- Agent Error Recovery Patterns — auto-researched from multiple web sources (no single canonical URL). Source for tiered retry, circuit breakers, failure classification, checkpointing, and graceful degradation.
- Testing AI Agent Pipelines — auto-researched from multiple web sources (no single canonical URL). Source for the three-layer testing architecture, the non-determinism problem, and the component-versus-E2E tradeoff.
- Levels of AI Agent Autonomy — auto-researched from multiple web sources (no single canonical URL). Source for the five-level autonomy framework, the ask-versus-act heuristic, and trust-calibration data.
- Multi-Agent Disagreement Resolution — auto-researched from multiple web sources (no single canonical URL). Source for disagreement-as-signal, the majority-pressure problem, and Agent Tennis detection.
- [Karpathy's Auto-Research Loop and the Local Hard Takeoff](https://www.youtube.com/watch?v=xnG8h3UnNFI) — Nate B. Jones, YouTube. Source for the meta-agent and task-agent split, model empathy across the meta/task boundary, trace quality caps improvement, and emergent harness behaviors as design findings.
- [Agents Means 4 Different Things and Almost Nobody Knows](https://www.youtube.com/watch?v=YpPcDHc3e9U) — Nate B. Jones, YouTube. Source for the four-species taxonomy, the problem-shape diagnostic, the "simple scales with agents" Cursor lesson, and the category-error watchlist.
- [The 5 Levels of AI Coding (Why Most of You Won't Make It Past Level 2)](https://www.youtube.com/watch?v=bDcgHzCBgmQ) — Nate B. Jones, YouTube. Source for org-coordination-as-friction, the spec-writing skill gap, and the StrongDM dark-factory operating model.
- [Six Months of Agentic Coding in the Trenches: Lessons from a Brownfield Project](https://www.yduman.dev/posts/six-months-of-agentic-coding/) — Yadullah Duman. Source for the RPI workflow, the guardrails-cone model, CLAUDE.md nesting, frequent intentional compaction, the two-parallel-agents sweet spot, and master-clone subagents.
- [The One AI Writing Hack Nobody Talks About](https://www.youtube.com/watch?v=ltbzgzZZmgI) — Nate B. Jones, YouTube. Source for the data room pattern, the structural hallucination argument, the four pre-drafting artifacts, and the Sullivan and Cromwell case.
- [Agent Analytics: Why Product Metrics Need to Change for AI Agents](https://www.youtube.com/watch?v=n0nC1kmztSk) — YouTube. Source for run-level product analytics, the completion-versus-acceptance gap, corrections as labels, the minimum viable run schema, and the rudder principle.
- [What Makes a Task Agent-Suitable (GitHub Copilot Cloud Agent Guidance)](https://docs.github.com/en/copilot/tutorials/cloud-agent/get-the-best-results) — GitHub. Source for the well-scoped-task definition, the agent-suitable versus keep-for-humans taxonomy, and the "issue as prompt" reframe.
- [How Lovable self-improves every hour — Benjamin Verbeek](https://www.youtube.com/watch?v=KA5kPbdkK2E) — Benjamin Verbeek, YouTube. Source for the vent tool, frustration-gating for signal-to-noise, in-line versus external reviewer economics, and stuck-state detection.
- [Every Claude Code Dynamic Workflow (& When to Use Each)](https://www.youtube.com/watch?v=g9b9G8dcS8Y) — Mark Kashef, YouTube. Source for the six named dynamic-workflow patterns, the three context-window failure modes, pattern stacking, and when not to use workflows.
- [Orchestrating AI Code Review at scale](https://blog.cloudflare.com/ai-code-review/) — Ryan Skidmore, Cloudflare. Source for production review-agent design: specialist reviewer domains, explicit prompt non-goals, structured severity output, coordinator fusion, approval bias, and incremental re-review state.
- [I Ranked Cloudflare's Software Factory and Wow… S TIER TOKENOMICS](https://www.youtube.com/watch?v=YG4t7aMY81c) — YouTube. Source for framing the Cloudflare review system as an A-tier agentic-engineering pattern with strong tokenomics and resilience, reinforcing risk-tiered specialist teams and observability as design constraints.
- [I Built The Best Claude Memory System (Beats Hermes)](https://www.youtube.com/watch?v=H9BUkgDf5Y4) — Simon Scrapes, YouTube. Source for memory decomposed into storage, injection, and recall, each with orthogonal design dials; best-of-breed assembly; multi-tier short-circuit recall; and cited-answer-over-chunks as the provenance principle.
