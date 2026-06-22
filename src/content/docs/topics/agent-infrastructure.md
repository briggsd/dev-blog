---
title: Agent Infrastructure
description: The production substrate beneath agent design — session durability, execution isolation, orchestration, the shared tool layer, and the multiplayer corpus that makes a fleet compound.
lastUpdated: 2026-06-21
---

Agent infrastructure is the production-platform layer beneath agent design: the substrate that runs agents reliably at scale. Agent design covers an agent's behavior, reliability, and autonomy. This covers the system the agents run inside: session durability, execution isolation, the orchestration substrate, the shared tool layer, and the multiplayer corpus that makes a fleet compound.

One through-line runs across every section. Infrastructure built for human developers is the same infrastructure agents need. Devboxes, CI loops, rule files, and tool layers built for human productivity pay direct dividends when agents inherit them.

## Key concepts

### Session, harness, sandbox decomposition

Shopify validated this three-layer split in production across River and several other agent products in 2026. It is the architecture that makes durable, cattle-not-pets agent infrastructure possible.

| Layer | What it is | Durability |
|---|---|---|
| **Session** | Durable identity. Append-only event log. Postgres-backed. The canonical truth about what's happened so far. | Permanent |
| **Harness** | The agent loop — reads history, calls the model, emits tool intents. Cheap to recreate. | Disposable |
| **Sandbox** | Where code actually runs — filesystem, shell, the repo. Bash, edit, build, test. | Disposable |

The critical boundary: the harness lives outside the sandbox. The agent does not live where the code runs.

Three properties fall out of this boundary, and you cannot retrofit them later:

- **Safety.** The agent loop sits outside the blast radius of `rm -rf` or whatever runs in the sandbox.
- **Replaceability.** Swap models, runtimes, or harness languages without disturbing the sandbox. Swap sandboxes without disturbing the session history.
- **Observability.** The entire decision stream sits on the harness side, in one place, readable without touching the execution environment.

When a Shopify session goes live, the orchestrator materializes a session cell: an ephemeral process running the Go harness. An idle cell exits. The next interaction gets a fresh cell, possibly on a different host. The session identity holds because the conversation lives in Postgres, not in memory. That is cattle, not pets, at the session level. Which orchestrator you pick matters less than your commitment to this principle.

You cannot retrofit it. If the harness co-locates with the sandbox, the session state entangles with the process. Kill the process and you kill the conversation. Once that is baked in, the only way out is a rewrite. This is a structural commitment, not a configuration choice.

The isolation ladder has two axes, not one. Keep them separate. How strong is the boundary (what the sandbox isolates) is independent of where it runs and who manages it (local versus internally-provisioned cloud). The load-bearing realization is that code isolation differs from runtime isolation, and you climb each axis only as far as the threat model and concurrency demand.

Axis one is isolation strength, the boundary itself. Each rung isolates strictly more than the one below, at strictly more cost:

1. **Git worktrees.** Filesystem isolation only. Close to free, shares the `.git` object DB, Anthropic-recommended for parallel Claude Code sessions. Isolates files but not ports, databases, the Docker daemon, or caches. Sufficient when parallel agents don't run conflicting services. Add port and DB scripting (`BASE_PORT + WORKTREE_INDEX*10` plus per-worktree DB instances) when agents must run dev servers at the same time.
2. **Container per run.** Runtime isolation, shared host kernel. The realistic team analog of a devbox: isolates process, filesystem, ports, and dependencies with reproducibility. Containers share the host kernel, so a kernel-level escape or a hostile workload is not fully contained. Fine for your own code, weaker for untrusted output.
3. **microVM per run.** Runtime isolation, separate kernel. Firecracker and Koyeb-style hardware virtualization gives each sandbox its own virtual CPU and memory, creating air-tight boundaries between execution environments. If an agent generates malicious or buggy code, the blast radius stays inside the microVM. This is the correct tier for executing untrusted AI-generated code, and the one compliance frameworks (SOC 2 code-execution isolation) ask for: microVMs, not containers.

Axis two is the provisioning model, where it runs. This is orthogonal to strength. Any rung above can be a local per-run sandbox or an internally-managed cloud pool.

- **Local per-run.** Spun up and torn down on the engineer's (or agent's) own machine. Cheapest, no infra to run.
- **Hosted preview env or Codespaces.** Zero-local-disk, shareable-URL isolation. You pay for infra but operate no pool.
- **Internally-managed pre-warmed pool.** The Stripe pattern: devboxes are AWS EC2 instances kept warm in a pool, with 10-second spin-up, repos cloned, and Bazel and type-check caches warmed. Provisioned, run, suspended, destroyed, re-provisioned. Cattle, not pets. Built on pre-existing human-developer infra, so the agents inherit it for free.

The boundary principle stays invariant across every tier. Whatever strength-by-provisioning combination you pick, the harness stays outside the sandbox. That keeps the sandbox disposable and the blast radius bounded, and bounded blast radius is what lets you flip the safety and permissions trade-off. Stripe runs its coding agents with full permissions and no confirmation prompts because the devbox sits isolated in a QA environment with no production access, no real user data, and no arbitrary internet egress. Isolation buys agent autonomy as much as it buys defense.

Worktrees fail in known ways, so don't rediscover them: port collisions, `node_modules` and `.env` not carrying over, a shared local DB causing race conditions, disk blowup as build caches multiply per worktree, and self-inflicted merge conflicts when parallel agents touch the same files with no tool warning.

The session layer sits above the harness in the stack: the durable identity the harness reads from (history) and writes to (new events). The sandbox sits below the harness: where the harness's tool intents execute. The decomposition gives each layer an explicit durability class.

### Agents as profiles: one platform, many bundles

Once a session-harness-sandbox substrate exists, build new agent products as profiles (data bundles), not new platforms. At Shopify a profile is a system prompt plus skills, extensions, sandbox policy, and model defaults, all built with Nix and shipped as a bundle.

Three consumption modes run on the same substrate:

| Mode | Example | Character |
|---|---|---|
| **Interactive** | River (Slack agent) | Durable session, live human present, long-lived |
| **Automation** | PR review agent | Durable session, woken by external event, often no human in loop |
| **Job** | CI / batch | Ephemeral — provision, run, stream, destroy |

All three share the same session model, sandbox plane, and gateway. One test tells you whether you built a substrate: the cost of your second agent product should be a new bundle, not a new platform. A second agent that forces a second platform leaves you with two copies of harness and sandbox plumbing, and you will reinvent the same three modes for every new agent after that.

### Multiplayer by construction

A private agent hits a structural ceiling at the person at the keyboard. Every insight, fix, and pattern from a private session dies with that session. At scale, N engineers running private agents gives you N siloed learning loops that never compound.

The corpus is the compounding asset. At Shopify, River only works in public Slack channels, no DMs. Every conversation becomes a searchable transcript. The team mines that corpus, so one person's hard-won fix becomes the next person's starting point and feeds back into River's skills, prompts, and defaults. The agent improves without model retraining. The numbers: 59,918 sessions in 30 days across 7,000 people, and 3,536 PRs merged in that window.

The public-only constraint is the mechanism. Privacy is not neutral for an agent system. A private thread is a disadvantage because it destroys the learning signal. The corpus compounds only if it accumulates.

What the corpus enables, concretely:

- Future sessions start from existing resolved threads rather than blank prompts.
- A second human drawn by a public thread can add context mid-session that redirects the agent.
- Pattern-mining turns high-quality threads into skill updates and prompt improvements.
- The codebase accumulates knowledge (AGENTS.md diffs, skill files) as session artifacts.

When you build agent infrastructure, default to public and shared session transcripts unless you have a specific reason not to. The value of the corpus grows with every session. Weigh the value of privacy against that compounding loss.

### Blueprint orchestration: deterministic plus agentic state machine

Stripe validated this in production across its coding agents in 2026: more than 1,300 merged PRs per week, no human-written code. A blueprint is an orchestration primitive that combines deterministic code nodes and agentic (LLM) nodes in a single state machine. It is the most concrete published answer to how you structure a reliable unattended agent.

The motivating observation: off-the-shelf orchestration picks one of two poles. Workflows give you a fixed graph, each node narrowly scoped with predefined edges, high determinism but inflexible against unknowns. Agents give you a loop with tools where the LLM decides what to do next, high flexibility but no guarantees. Production systems carry both known steps and open-ended subtasks, so neither pole fits.

Blueprints interleave both:

| Node type | What runs | Examples |
|---|---|---|
| **Deterministic node** | Code, not an LLM | "Run configured linters", "Push changes", "Apply autofixes" |
| **Agentic node** | Free-flowing LLM agent loop | "Implement task", "Fix CI failures" |

The state machine gives each subtask the right execution model. Agentic nodes get wide latitude. Deterministic nodes guarantee certain steps always complete correctly without spending tokens to reason out an answer the system already knows.

Each deterministic node narrows the error surface. One lint node catches formatting before CI. One push node guarantees `git push` runs correctly every time. Small per-node wins compound across thousands of runs into measurable system-wide reliability. Stripe frames it as putting LLMs into contained boxes.

Because each agentic node is a contained scope, blueprints make per-node context engineering easy: constrain the tool set, modify the system prompt, simplify the conversation history. You engineer context separately for each agentic node's job rather than once for the entire run.

Individual teams can define their own blueprints for specialized workflows, for example LLM-assisted migrations across the codebase that a pure codemod could not handle. The blueprint is code, not config. It lives in the harness repo and carries the full expressivity of a programming language.

Blueprints sit above the tool layer and below the session layer in the stack, and below the work-intake layer. The queues-not-loops pattern below is the human-facing backlog that feeds dequeued items into a blueprint run.

You do not need a framework. Blueprints are a named instance of the workflow-agent composition in Anthropic's *Building Effective Agents*, the exact source Stripe cited. Anthropic's direct guidance: the most successful implementations use simple composable patterns, not complex frameworks. Start with LLM APIs directly. Many patterns run in a few lines of code. A bash script (deterministic nodes) wrapping Claude Code invocations (agentic nodes) is the blueprint pattern, with no LangGraph, Strands, or Rivet required. Reach for a framework only when the orchestration graph genuinely outgrows a script, and only if it keeps prompts and responses legible. Abstraction that obscures the underlying prompts is the main framework failure mode.

### Queues, not loops: structuring AFK work as a backlog

Matt Pocock offers a framing correction to the viral agentic-loop discourse, the "Ralph" loop (Geoffrey Huntley's `while` loop re-invoking Claude Code, July 2025, amplified by Peter Steinberger). Pocock's claim: the loop is the wrong primitive, and half the hype is labs selling infinite token spend. People want AFK (away-from-keyboard) agents working a queue, not a loop.

The reframe: development has always been a queue of tasks. Multiple worker nodes pick items off, an item leaves the queue when its PR merges, and project managers add more. An infinite single loop does not match how real teams work and only makes sense if it continuously produces value. Otherwise you are paying OpenAI or Anthropic infinitely for nothing. Pocock's metaphor: a minister deployed with no commands runs on a loop and drifts, while a king runs a queue. Problems are brought to him, he prioritizes (50 bug reports, 3 critical), and he stays in charge.

The triage shape moves items through stages by label: `explore` (scope it, often AFK), then `agent implement`, then review, then merge. Any teammate can add a label to trigger work. This is the human-readable, observable version of the deterministic-plus-agentic blueprint state machine above, with GitHub Issues and labels as the queue substrate.

Pocock's concrete AFK stack runs agents inside sandboxes through his own tool, Sand Castle. Plug in Docker or Podman locally, or Vercel sandboxes remotely, so a rogue agent cannot `rm -rf` your home dir or exfiltrate env vars, and you can parallelize many agents and pull commits back. This is a practitioner instantiation of the isolation ladder above: container-per-run strength, local-or-cloud provisioning, built to make AFK parallelism safe. He pairs it with GitHub Actions as the dispatch and event layer: label-triggered runs, for example an "agent review" action on every PR that checks out the branch, runs a review prompt, type-checks, and comments back.

AFK is the unlock, not the loop. The value comes from removing yourself from the permission and confirmation loop so N agents run in parallel while you do other work. As Pocock puts it, "suddenly there are two of me, three of me." The loop-versus-queue debate is downstream of that.

Push human-in-the-loop checkpoints toward production. Move review checkpoints as far toward production as is safe, surfacing richer artifacts to the human at each step (bug report, then codebase exploration, then proposed fix, then "review this?") so a decision is one button-click away instead of a debugging session away. Review buys two things, and only one of them is safely removable: gating dangerous changes (security, leaks), and observability into your own harness. Watching the agent work is how you learn whether the system producing the code is any good. You can have an agent auto-classify "safe to skip" PRs, but someone still reviews the AI doing that classification. You spot-check its calls to improve the judgment over time. This is the same shift-interventions-right principle reached independently from the Codex side.

This is a single-practitioner thesis presented in a promotional context, so treat it as plausible rather than verified.

### CI-native review factory

Cloudflare validated this in production across 48,095 merge requests and 5,169 repositories in one month. It is the clearest published example of a review-specific agent factory: not a generic chat reviewer, and not a dark factory that writes code end to end, but a CI-native harness that turns merge requests into structured, risk-tiered, observable review runs.

The core architecture: MR event, then plugin-assembled config, then risk classification, then diff filtering, then shared context files, then a coordinator agent, then a specialist reviewer fan-out, then coordinator fusion, then GitLab comments and an approval policy. The model is one component. The value sits in the harness that scopes context, selects reviewers, normalizes output, handles retries, and posts decisions back into the existing review workflow.

The plugin lifecycle is the scale mechanism. Cloudflare's entry point assembles review configuration through plugins rather than a monolithic config path. Plugins contribute VCS setup, AI Gateway routing, tracing, compliance checks, AGENTS.md freshness review, remote model overrides, and telemetry through a controlled lifecycle: bootstrap (concurrent, non-fatal), configure (sequential, fatal), post-configure (async enrichment). This applies the same open-closed principle covered below to a CI review factory: new policies and integrations attach at the edge without rewriting the core orchestration.

Cloudflare chose OpenCode as a programmable substrate because it is open source, server-first, SDK-accessible, and capable of programmatic sessions. The coordinator runs as a child process with prompts via stdin (which avoids `ARG_MAX` failures), streams JSONL events, and exposes a runtime plugin with a `spawn_reviewers` tool that launches specialist reviewer sessions. The infrastructure lesson is not "use OpenCode." It is to pick a substrate you can automate as a server, not one whose only stable interface is a terminal UI.

Context economics shape the design. Diffs become patch files and MR metadata becomes shared context files. Reviewers receive paths and scoped instructions instead of every specialist ingesting the full MR payload. Large and noisy files get filtered before the model sees them, while migrations stay exempt because generated does not always mean semantically unimportant. This keeps multi-agent fan-out from becoming 7x context duplication.

Compute scales with risk. Trivial reviews average about $0.20, lite reviews $0.67, and full reviews $1.68. The full specialist team only runs for large or security-sensitive diffs. This is tokenomics as infrastructure policy: scale review breadth with expected review value, not with a fixed always-run-all-agents default.

Operational resilience is first-class: model-family circuit breakers, failback chains, retry budgets, per-task and whole-run timeouts, token-truncation detection, provider switches through a Worker and KV control plane, and non-blocking telemetry. Agent review in CI is a distributed-systems workload. Retries without failure classification become waste, and telemetry that can fail the job becomes an outage vector.

The measured production envelope: median duration 3m39s, median cost $0.98, P99 cost $4.45, 85.7% cache hit rate, 120B tokens processed, and 159,103 findings (about 1.2 per review). The low findings-per-review number is a feature. The harness optimizes for high-signal findings, not a firehose of plausible comments.

### Harness sovereignty: own, don't rent

This is the practitioner-level counterpart to the decomposition above. That section covers how to structure a harness. This covers why you own one rather than renting an off-the-shelf CLI. The thesis (IndyDevDan, 2026): whoever controls the agent harness controls your results. The agent supplies agentic speed, the agent lives inside the harness, so harness control is results control. Stock CLIs (Claude Code, Codex, OpenCode) are the floor, not the ceiling: a great start and a terrible place to finish, because a rented harness limits you to what the vendor permits.

Ownership unlocks a customization surface: composable, stackable units (skills, agents, commands pulled from any location) plus sandbox-by-default execution, sub-agent delegation, damage control, model fallbacks, and model routing.

Specialization is the durable edge, one tool in many versions. Build two classes of harness: engineering-pattern harnesses (agent chains, verifier harnesses where one agent checks another's work) and domain-specific harnesses that do one thing extraordinarily well, a DevOps harness, a testing harness, a billing harness. You cannot specialize the experience on a harness you don't own. Specialization is the moat an off-the-shelf agent cannot cross.

Expose your CLIs and APIs everywhere or pay a token tax. API access is a prerequisite of agentic speed: agents only command what they can programmatically reach. When an agent could do something but isn't, the cause is usually a missing integration. Expose CLIs, REST, webhooks, and RPC clients across codebases, products, and devices so agents operate at their native 10-1000x speed. The token tax is any work an agent does inefficiently purely because it lacks direct API access: tokens burned navigating around a gap that a one-time integration would close. The same isolation principle that runs through this topic guards it. Agentic access does not mean production access. Lock down the bash tool and keep destructive reach out of the blast radius, the same full-permissions-because-isolated trade-off applied at the access layer.

This is a single-practitioner thesis in a promotional context, so treat it as plausible rather than verified.

### Extensibility as a survival property

Open to extension, closed to modification is the design-principle floor under harness sovereignty (you can only specialize a harness you can extend), agents-as-profiles (the second agent is a bundle, not a platform, only because the substrate is extensible), and the Toolshed pattern (the same instinct at the tool layer). Those three depend on it, not the other way around.

This principle now has its own page. See **[Extensibility](/working-intel/topics/extensibility/)** for the plugin-architecture lineage it descends from (microkernel, open/closed, information hiding, mechanism-not-policy), Pi as a worked open/closed reference, and a seam-decision heuristic for where to put the extension points.

### Peer-to-peer (flat) agent communication

This is a contrasting orchestration substrate to everything else in this topic. Instead of an orchestrator delegating down to workers, N agents join a shared pool as equals and prompt each other bidirectionally: prompt and response in both directions, on the same device or across devices. IndyDevDan demonstrated it as a harness extension in 2026. The implementation stays deliberately minimal, four tools (list agents, send command which returns a message ID, await response which blocks, and poll which pulls non-blocking) plus a lightweight Bun server for the networked variant.

This completes the orchestration spectrum. The patterns already in this topic all move information one direction, top-down, even when results flow back: sub-agent delegation, message-queue brokering (one agent owns a queue and brokers between peers), and blueprint state machines (deterministic plus agentic nodes, but still a one-way graph). Peer-to-peer adds the missing pole: a flat substrate with no broker and no fixed graph, where any agent can reach any other and information returns are genuine two-way exchanges rather than one-way returns up a hierarchy.

The argument for flatness is informational, not just architectural. In a hierarchy the best system awareness usually sits at the worker level and gets stuck there for lack of authority, so ideas die in hierarchies. Flat structures let the best information win regardless of title. The agentic instance: a flat agent pool lets a peer's correction propagate immediately instead of being lost on the way up. The most transferable evidence is a builder-plus-validator exchange, where an Opus agent cross-checking a GPT-5.5 agent's claims surfaced 10 corrections before they hit a generated skill. Bidirectional comms is the channel that makes cross-checking possible at all.

The real payoff is context specialization, not parallel speed. Splitting work across peers keeps each agent's context window focused on one problem (one tool, one service, one slice), which drives the error rate down: a focused agent is a performant agent. This is the multi-agent answer to context-window bloat that does not wait for larger windows. Heterogeneous models in the pool (different training and RL loops) are claimed to compound into a system stronger than either alone, demonstrated rather than benchmarked.

The source names the failure modes. Loops are possible with sloppy prompts, so peer-to-peer needs an explicit end-state contract or it burns tokens indefinitely. Cost scales linearly with agent count plus communication bounce, so there is a ceiling past which adding agents stops helping (no measured heuristic, trim when not useful). The networked variant ships unauthenticated by default, secure it yourself. And there is a standing temptation to slide back into orchestration. If you actually need a top-down orchestrator, build that. Peer-to-peer's only real edge is flatness.

This is a primitive-over-composition approach, just an agent plus an extension, composable up to and including re-forming an orchestrator. It contrasts with blueprint orchestration (deterministic structure, top-down) on the determinism-versus-flatness axis: blueprints buy reliability through fixed structure, peer-to-peer buys information fidelity through flatness. Both are valid, and the choice is a trade-off, not a winner. Unlike the production patterns above, this is not validated at scale. It is a single-practitioner demonstration, so treat the compounding-models and error-rate claims as plausible rather than verified.

### Shared tool infrastructure (Toolshed pattern)

Stripe validated this in production in 2026. When an organization runs multiple agents (custom harnesses, off-the-shelf tools, Slack bots, CLI agents), each agent's tool investment defaults to being siloed. The Toolshed pattern breaks that default.

The pattern: build a centralized, organization-wide MCP server. Every agent in the fleet connects to it. Adding a tool to the server immediately grants that capability to all agents at once.

Stripe's implementation runs about 500 MCP tools spanning internal systems and SaaS platforms. The fleet scope covers a no-code agent builder, custom service agents, third-party tools (Cursor, Claude Code), CLI agents, and Slack bots, all using Toolshed as a shared capability layer. Agents perform best with smaller, focused tool sets, so each agent requests only a relevant subset, and per-user customizability lets engineers add thematically grouped bundles to their own agents. For agent runs, Toolshed tools run deterministically over likely-looking links in the input before the agent loop starts, so the context arrives hydrated rather than gathered ad hoc during the run. An internal security control framework governs tool calls to prevent destructive actions, and the devbox's QA isolation is the first line of defense.

Tool investment compounds across the fleet. One engineer authors a tool that surfaces internal ticket details, and the coding agents, Cursor, Claude Code, and internal Slack bots all get it immediately. At Stripe's scale (hundreds of distinct agents) this amortization is the decisive argument for centralization over per-agent tool configuration.

The curated-subset constraint matters. Toolshed has about 500 tools, and giving every agent all 500 would be counterproductive because context and cognitive overhead scale with tool count. The pattern is a large shared library with a small agent-specific slice. This is the same principle as directory-scoped rule files: design for the large available set but constrain the per-invocation context.

The description-field-as-discovery-mechanism principle still applies inside Toolshed. Each tool's description determines whether an agent picks it. The Toolshed pattern governs where tools live and how they propagate to agents. Description quality determines whether agents use them correctly once they do.

## Current thinking

This topic exists because two independent production systems (Shopify River and Aquifer, and Stripe's coding agents) converged on the same infrastructure shape in 2026, and a team-scale research cycle confirmed the patterns scale down. The load-bearing synthesis for a team building its own system:

- **Isolation is a ladder, not a binary.** Start at git worktrees (free, real filesystem isolation), climb to container-per-run only when you need runtime isolation. The full pre-warmed devbox pool is overkill until you run dozens of concurrent agents daily.
- **Orchestration is a script, not a framework.** Blueprints (deterministic plus agentic nodes) are Anthropic's own composable-patterns guidance. A bash wrapper around Claude Code is the minimum viable blueprint. Don't buy LangGraph first.
- **Tools should compound, not silo.** Even at 5 to 20 tools (against Stripe's 500), a shared MCP config across the team is the right default. Tool investment amortizes across every agent on the team.
- **Session durability is the one thing you cannot retrofit.** For a first team build, the PR itself carries session identity (comments, commits, the CLAUDE.md used), which is enough until you run long-lived multi-day agents. At that point the Postgres-session pattern earns its cost.
- **Extensibility is a survival property, not a feature.** Build the harness (and the product) open to extension, closed to modification: add behavior in layered units, never by editing the core. This is the floor under both agents-as-profiles and own-don't-rent, and ownership without extensibility just relocates the brittleness. See [Extensibility](/working-intel/topics/extensibility/) for the worked reference and the seam-decision rules.
- **Orchestration is a spectrum, not a default.** Top-down patterns (blueprints, brokers) buy reliability through structure. Flat peer-to-peer comms buys information fidelity and context specialization through flatness, at the cost of loop risk and a fuzzy scaling ceiling. The peer-to-peer pattern is still single-practitioner, not production-validated: promising for builder-plus-validator cross-checking and PII-safe cross-device hand-offs, but unproven at fleet scale. Pick the axis (determinism versus flatness) the problem actually needs.
- **Review factories are the practical first production harness.** Cloudflare's AI review system shows the team-scale version of these principles in a narrow workflow: plugin-configured CI entrypoint, server-first programmable harness, risk-tiered specialist agents, shared context files, JSONL traces, runtime model routing, and non-blocking telemetry. To build a local version, start thinner (coordinator plus code quality plus security plus docs) but keep the same infrastructure shape.

The right team analogy is not "build Aquifer." It is "build the things that help your human developers (devboxes, CI loops, rule files, a shared tool layer), and let the agents inherit the dividend."

## Open questions

- What is the minimal Dockerfile and entrypoint for a devbox-lite (the container-per-run tier), and the minimal Firecracker or Koyeb setup for the microVM tier above it?
- For the internally-managed cloud pool: what is the minimal pre-warmed-pool mechanic (provisioner plus warm-cache plus checkout-to-master) on AWS EC2 (or Fargate) that gets near Stripe's 10-second spin-up without Stripe's scale?
- Is the role-pool model (Frontend, Backend, DevOps, QA agents in isolated worktrees) a usable concrete orchestration pattern, or just a demo?
- At what team size and concurrency does the PR-as-session-identity approach break, forcing a move to a durable session store?
- Does Stripe publish its Toolshed or blueprint machinery as open source, or is there a credible open-source equivalent of the blueprint state machine?
- Where is the peer-to-peer scaling ceiling, and what is the minimal mechanism to prevent agent loops (turn limits, end-state contract, referee node)? The demo names the risk but not the fix.
- What is the minimal safe auth and transport for cross-device agent comms (the networked variant ships unauthenticated)?
- How does the pattern-mining pipeline actually work (public Slack thread to skill update)?
- Discovery without a manifest: what is the minimal discovery mechanism that does not reshape the core, a scanned convention directory, a manifest field on a paired package, or a runtime register from an injected module? The contract is settled, only the loading is open.
- Paired-extension packaging: if a harness extension ships a paired web renderer, how does the renderer travel with the installed package and reach the UI's registry?
- For the product-work arena of extensibility (not the harness): does shipped agentic software whose own agents author the extensions follow the same seam-decision heuristic, or does agent-as-author change the seam design (seams optimized for an LLM to discover and use, not a human developer)?

## Applied in

- [Build a CI-Native Review Factory](/working-intel/build/ci-native-review-factory/) — a first-party version of the CI-native review factory: deterministic shell (diff fetch, risk tiering, the CI gate) around an agent layer that fans out specialist reviewers and fuses them, with a single declarative tier table driving cost.

## Sources

- [Under the River](https://shopify.engineering/under-the-river) — Shopify Engineering. Source for the session/harness/sandbox decomposition, session cells (cattle-not-pets), agents-as-profiles, the three session modes, and multiplayer-by-construction with the public corpus as compounding asset.
- [Minions: Stripe's one-shot, end-to-end coding agents (Parts 1 & 2)](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents) — Alistair Gray, Stripe. Source for blueprint orchestration (deterministic plus agentic state machine), the Toolshed shared MCP server pattern, the pre-warmed EC2 devbox pool, and devbox isolation enabling full permissions.
- [The Isolation Spectrum for Parallel Coding Agents: Worktrees → Containers → Preview Envs](https://developer.upsun.com/posts/ai/git-worktrees-for-parallel-ai-coding-agents/) — Upsun. Source for the isolation spectrum, code-isolation versus runtime-isolation, and the worktree failure modes.
- [CI/CD Pipelines for AI-Generated Code: Redesigning Validation for a New Code Mix](https://dasroot.net/posts/2026/04/ci-cd-pipelines-ai-generated-code/) — dasRoot. Source for the microVM-versus-container kernel-isolation distinction and the Koyeb microVM approach for executing untrusted AI-generated code.
- [AI-Generated Code in Regulated Industries: SOC 2, PCI DSS, and the Compliance Gap](https://blaxel.ai/blog/soc-2-compliance-ai-guide) — Blaxel. Source for "microVMs, not containers" as the SOC 2 code-execution-isolation control and least-privilege role-based agent restrictions.
- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — Anthropic. Source for blueprints as a named instance of workflow/agent composition and the don't-buy-a-framework-first guidance (simple composable patterns over complex frameworks).
- [Orchestrating AI Code Review at scale](https://blog.cloudflare.com/ai-code-review/) — Ryan Skidmore, Cloudflare. Source for the CI-native review factory: plugin lifecycle, OpenCode as programmable substrate, shared context files, risk-tiered compute, circuit breakers and failback, the Worker/KV model-routing control plane, and the measured cost and latency envelope.
- [I Ranked Cloudflare's Software Factory and Wow… S TIER TOKENOMICS](https://www.youtube.com/watch?v=YG4t7aMY81c) — IndyDevDan, YouTube. Commentary source on the Cloudflare review factory emphasizing tokenomics, context sharing, risk-tiered agent teams, observability, and resilience.
- [Matt Pocock's Agentic Engineering Workflow](https://www.youtube.com/watch?v=nQwJVHCtDDY) — Matt Pocock, YouTube. Source for the queues-not-loops reframe, AFK agents as the real unlock, Sand Castle as a practitioner isolation-ladder instantiation, GitHub Actions label-dispatch as queue substrate, and pushing human-in-the-loop checkpoints toward production.
- [The 5 Pillars of Agentic Engineering](https://www.youtube.com/watch?v=2KcITKKJikA) — IndyDevDan, YouTube. Source for harness sovereignty ("own, don't rent"), domain-specific harnesses as the specialization moat, extensibility as a survival property (open/closed across two arenas), and agentic access plus the "token tax."
- [Pi2Pi: Two-Way Agent Communication](https://www.youtube.com/watch?v=PIdETjcXNIk) — IndyDevDan, YouTube. Source for peer-to-peer flat bidirectional communication, the flat-beats-hierarchical information argument, context specialization as the real payoff, the builder-plus-validator cross-check (10 corrections), and the four-tool primitive plus failure modes.
- Extensibility Principles and the Plugin-Architecture Lineage (research-cycle synthesis, no single source URL) — synthesis of documented harness philosophy and the plugin-architecture lineage (microkernel, OCP, Parnas information-hiding, GoF encapsulate-what-varies, Unix mechanism/policy, VS Code declarative-versus-programmatic contribution, stable-dependencies), and the six-point seam-decision heuristic.

## Changelog

- **2026-06-21** — Promoted the "Extensibility as a survival property" section into its own [Extensibility](/working-intel/topics/extensibility/) topic; slimmed the section here to a pointer.
- **2026-06-21** — Added an "Applied in" link to the CI-native review factory build log.
- **2026-06-21** — Migrated to the public site; sanitized and run through the publish pipeline.
- **2026-06-09** — Added the CI-native review factory (Cloudflare pattern).
- **2026-06-08** — Added harness sovereignty, extensibility as a survival property, and peer-to-peer agent communication.
- **2026-06-01** — Topic created by splitting Agent Design: the Aquifer session/harness/sandbox decomposition, agents-as-profiles, multiplayer by construction, blueprint orchestration, and the Toolshed shared-tool layer.
