---
title: Context Engineering
description: "The discipline above prompt engineering: treat the context window as a finite attention budget, and curate every token that lands in it. The levers are settled; the long-horizon question (share context or isolate it) is the live edge."
lastUpdated: 2026-06-22
---

Prompt engineering is about writing the instruction. Context engineering is about everything else in the window: the tools, the retrieved data, the message history, the notes, the prior turns. Once an agent runs over many turns, the prompt is a small fraction of what the model attends to, and the larger job is curating the whole context state. Anthropic's applied team draws the line directly, calling context engineering "the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference." Three teams shipping very different products (a model lab, an autonomous coding agent, a general agent product) have independently named it the core job of building agents.

This topic owns the discipline. The domain-specific applications live in their own topics and are cross-linked here rather than restated: the storage/injection/recall memory decomposition and the dynamic-workflow patterns in [Agent Design](/working-intel/topics/agent-design/), session management in [Claude Code Lessons](/working-intel/topics/claude-code-lessons-learned/), and context rot and pruning in [The Knowledge Flywheel](/working-intel/topics/knowledge-flywheel/). The note [Context Engineering Grew Up](/working-intel/notes/context-engineering-grew-up/) is the dated synthesis behind this page.

## Key concepts

### Context is a finite resource

The organizing idea is scarcity. "Context must be treated as a finite resource with diminishing marginal returns," because an LLM has an "attention budget" it draws on when parsing a large window, the way human working memory is bounded. Past a point, more tokens buy less. The empirical name for the decay is **context rot**: as the number of tokens grows, "the model's ability to accurately recall information from that context decreases" (Chroma's study across 18 models is the standard reference). It is "a performance gradient rather than a hard cliff," but padding the window has a real cost, which is why [pruning is a first-class discipline](/working-intel/topics/knowledge-flywheel/), not cleanup.

### Volume is not signal

The finite-budget principle has a fashionable counter-current worth naming. As models get stronger, one camp reads the extra capability as license to spend more: longer specs, richer plan documents, HTML-wrapped context, generated images embedded throughout, on the logic that more tokens give the model more to work with. IndyDevDan's planning-skill rebuild makes the argument explicit, citing "HTML gives your agent more tokens" as a feature. The attention-budget view cuts the other way. Every token spent on format or decoration depletes the same budget, and context rot means recall degrades as the window fills no matter how capable the model is. Anthropic's own guidance, the source that camp tends to cite, lands on "the smallest possible set of high-signal tokens." The spec-driven-development discourse splits the same way: Birgitta Böckeler, surveying the tools on Martin Fowler's site, is "very skeptical that lots of up-front spec design is a good idea, especially when it's overly verbose."

The reconciliation is that volume and signal are different axes. A planning document earns its tokens through structure (a stated problem, files enumerated, phases with validation gates), which is high-signal by construction, and wastes them on padding (decorative wrappers, images that restate the prose). "Minimal does not necessarily mean short" already names the distinction: spend tokens where they carry information and nowhere else. The test for any artifact you load (spec, plan, memory) is signal per token, not token count. The skill-authoring side of this, meta-skills that template your engineering into reusable plan formats, lives in [Skill Design and Management](/working-intel/topics/skill-design-and-management/).

### The levers

How to spend the budget is broadly settled into a few moves.

- **System prompts at the right altitude.** The Goldilocks zone between brittle hardcoded logic and vague hand-waving: "specific enough to guide behavior effectively, yet flexible enough to provide the model with strong heuristics." Aim for "the minimal set of information that fully outlines your expected behavior," remembering that "minimal does not necessarily mean short."
- **Tools are context.** Tool definitions occupy the window and steer behavior, so they should be self-contained, non-overlapping, and token-efficient. The common failure is bloat: "If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better."
- **Just-in-time retrieval.** The highest-leverage shift is loading information when it is needed instead of pre-stuffing the window. Keep "lightweight identifiers (file paths, stored queries, web links)" and "dynamically load data into context at runtime using tools." This enables progressive disclosure: the agent discovers context through exploration rather than receiving a data dump. It is the runtime-loading framing behind the site's existing "freshness beats fullness" and capped-injection lessons.

### Cache economics: the production floor

Curation has an unglamorous economic floor that most discussions skip. Manus reports that "the KV-cache hit rate is the single most important metric for a production-stage AI agent," because cached input tokens cost a fraction of uncached ones (a 10x gap on Claude Sonnet) against an input-to-output ratio around 100 to 1. That converts abstract advice into hard rules: keep the prompt prefix stable, since "even a single-token difference can invalidate the cache"; make the context append-only and avoid rewriting prior turns; and serialize deterministically. A dynamic timestamp in your system prompt is not a style choice, it is a cache miss on every turn. Context engineering is partly an attention problem and partly a bill.

### Long-horizon context management

When one window cannot hold the task, the techniques converge:

- **Compaction.** Summarize a near-full window and reinitialize with the summary. (Do it deliberately; the site's lesson against lossy auto-compaction lives in [Agent Design](/working-intel/topics/agent-design/).)
- **Structured note-taking / externalized context.** The agent writes durable notes outside the window. Manus pushes this to treating the file system as "the ultimate context... unlimited in size, persistent by nature, and directly operable by the agent," with compression "always designed to be restorable" so nothing is lost permanently.
- **Recitation.** Manus rewrites a running `todo.md` and recites the objectives into the end of the window, pushing "the global plan into the model's recent attention span" to fight lost-in-the-middle and goal drift.
- **Keep the failures in.** When wrong turns and stack traces stay in the context, the model "implicitly updates its internal beliefs," rather than repeating the mistake on a clean slate.

The dynamic-workflow vocabulary for distributing long tasks across fresh-context subagents (and its failure modes: laziness, self-preference, goal drift) is treated in [Agent Design](/working-intel/topics/agent-design/); this page is the discipline those patterns serve.

### Share context, or isolate it

The one genuinely unresolved question sits at the long-horizon handoff. Anthropic recommends sub-agents that "handle focused tasks with clean context windows" and return condensed summaries to a coordinator. Cognition, in a piece titled "Don't Build Multi-Agents," argues the opposite reflex: parallel sub-agents fragment context, since "Subagent 1 and subagent 2 cannot see what the other was doing," so their principles are "share context, and share full agent traces, not just individual messages" and "actions carry implicit decisions, and conflicting decisions carry bad results." Their reliable shape is a single-threaded agent with a compression model for length.

Read closely, the gap is narrow. Anthropic's sub-agents are not a collaborating swarm; they take an isolated task and pass back a summary, which is close to Cognition's own pattern of a single root agent delegating isolated sub-tasks. What both reject is parallel agents making conflicting assumptions with no shared trace. The real axis is not one agent versus many. It is whether, at a handoff, you **share the full context** (and fight bloat and cost) or **isolate the task and return a summary** (and fight fragmentation). That tradeoff is the frontier of the discipline. The orchestration shapes this plays out across live in [Agent Infrastructure](/working-intel/topics/agent-infrastructure/) and [Agent Design](/working-intel/topics/agent-design/).

## Current thinking

The strongest signal is convergence under disagreement. A model lab, a production agent team, and the Devin team all elevated context curation to the central skill, using nearly the same words, while splitting on architecture. That is what a maturing discipline looks like: the fundamentals (finite budget, right-altitude prompts, lean tools, just-in-time loading, a cacheable prefix) stop being contested, and the argument moves to the hard edge.

The most useful reframe for practice is to stop treating the context window as storage and start treating it as a budget that is spent every turn. Most "the agent got confused" problems are budget problems: a bloated tool set, an uncapped memory dump, a window padded past the point of reliable recall. The fix is rarely a bigger window. It is curation.

## Open questions

- At a long-horizon handoff, when does sharing full traces beat isolating a task and returning a summary, and can the choice be made per-handoff rather than per-architecture?
- Just-in-time retrieval trades upfront tokens for runtime tool calls and latency. Where is the crossover, and how much should be pre-loaded versus discovered?
- Cache-stable prefixes and append-only context conflict with techniques that rewrite the window (compaction, recitation). What is the right interplay so you keep the cache and still steer attention?
- How much of curation can a meta-agent or harness do automatically (the auto-improving direction) versus staying a human design decision?

## Sources

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic Applied AI team. Source for context engineering vs prompt engineering, the finite-resource / attention-budget framing and context rot, right-altitude prompts, tools, just-in-time retrieval, and the long-horizon techniques. Synthesized in the note [Context Engineering Grew Up](/working-intel/notes/context-engineering-grew-up/).
- [Context Engineering for AI Agents: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) — Yichao "Peak" Ji, Manus. Source for KV-cache economics, stable prefixes and append-only context, the file system as externalized context, recitation, and keeping failures in context.
- [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) — Walden Yan, Cognition. Source for the context-fragmentation argument, the share-context principles, and the single-threaded-agent recommendation.
- [PLANS For Fable 5: Rebuilding My /Plan Skill for Mythos Class Models](https://www.youtube.com/watch?v=DzbqeO_diOQ) — IndyDevDan, YouTube. Source for the "more tokens, HTML-first" planning posture that the finite-budget view answers. Synthesized in the note [Great Planning, Not Bigger Plans](/working-intel/notes/great-planning-not-bigger-plans/).
- [Understanding Spec-Driven Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) — Birgitta Böckeler, martinfowler.com. Source for the skepticism of overly verbose up-front specs in the volume-is-not-signal concept.

## Changelog

- **2026-06-22** — Added the "Volume is not signal" concept (the more-tokens planning posture vs. high-signal-per-token, with the SDD verbosity debate). Feeds the note [Great Planning, Not Bigger Plans](/working-intel/notes/great-planning-not-bigger-plans/).
- **2026-06-22** — Topic created from Anthropic's "Effective context engineering" article plus the Manus and Cognition perspectives. Consolidates the context-engineering concept the site treated across several topics; owns the discipline (finite budget, the levers, cache economics, long-horizon management, the share-vs-isolate debate) and cross-links the domain applications. Feeds the note [Context Engineering Grew Up](/working-intel/notes/context-engineering-grew-up/).
