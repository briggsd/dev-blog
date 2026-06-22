---
title: Claude Code Lessons Learned
description: Hard-won patterns and pitfalls from working with Claude Code — validation loops, context discipline, CLAUDE.md design, external review, and parallel orchestration.
lastUpdated: 2026-06-21
---

Patterns, lessons, and pitfalls from working with Claude Code, the CLI tool. This compounds practical knowledge so future sessions and future setups don't relearn the same things. The entries group by theme and grow as new ones come up.

## Validation loops

### The validation loop is the single biggest lever on output quality

Giving Claude a way to verify and self-correct its own output determines whether an agentic coding session produces good results or confidently ships broken code. It matters more than model choice or prompt quality.

- **The pattern:** Build, validate, fix, repeat. Claude runs the validation, reads the result, and self-corrects without human intervention. The loop is the automation.
- **Why it dominates other factors:** most "the AI doesn't do what I want" complaints resolve once you add a real validation loop. Without one, the model has no signal on whether its output is correct.
- **Concrete instantiations by platform:**
  - *Mobile (Xcode):* Xcode MCP builds the app, Claude reads compile errors, then fixes and re-builds.
  - *Web:* Playwright or Puppeteer navigates the running app, performs actions, checks assertions. `/chrome` is a fallback when no programmatic driver is available.
  - *Debugging:* Ask Claude to add debug logs, run the app via MCP or emulator, tail the log output, diagnose from the trace.
  - *Performance:* Hook into a profiling tool such as Perfetto. Claude reads timing traces and identifies jank without a human doing the analysis.
  - *General:* Any integration or end-to-end test suite that Claude can run and read.
- **Design principle:** when starting a new project or feature, define the validation loop before writing code. The loop design matters more than the first prompt.

## Automation and browser control

### Use Playwright and the Playwright MCP to automate

When a task requires Claude Code to drive a browser (testing UIs, scraping behind auth, validating flows end-to-end), reach for Playwright together with the Playwright MCP server rather than rolling your own automation.

- **Why it works:** Playwright is the de facto standard for reliable cross-browser automation, and the Playwright MCP exposes it to Claude as a first-class tool surface. Claude clicks, types, asserts, and screenshots through a coherent interface instead of stitching together shell commands.
- **When to use:** UI smoke tests, verifying a deploy, filling in forms during research, capturing screenshots as evidence for a session log, auth-gated scraping.
- **Watch-outs:** Still filling in as experience accumulates (headless versus headed, session and cookie reuse, flakiness patterns).

## Context engineering and session management

### Freshness beats fullness

A lean, focused context window produces better output than a rich but bloated one. This sounds obvious but has counter-intuitive implications for how you work.

- **The failure mode:** iterating on a broken approach inside the same session ("try this, try that, try this again") fills context with failed attempts. The model has no reliable way to know which attempts were good. Quality degrades.
- **The fix:** start in plan mode, get the direction right before generating code, then execute. One clean pass beats five corrective passes.
- **Signal to reset:** if Claude seems confused by its own history in a session, it probably is. Run `/clear` and restart with a fresh, focused prompt instead of continuing.
- **`/context` for auditing:** run `/context` to see a visual breakdown of what's consuming tokens. MCPs are a common surprise, since a single MCP can consume a large fraction of the available window on every turn. If costs spike or output quality regresses, diagnose here first.

### The second-brain, lazy-load pattern for cross-session continuity

Maintain a project-level local file (a CLAUDE.md in the project directory, or a similar notes file) that stores accumulated knowledge: current todos, past decisions, architecture notes, open questions. Load it on demand rather than automatically.

- **How it works:** at the end of a session, say "save what we did to my local projects file." At the start of the next session on the same project, say "load my context from my local projects file." The context is there when needed and absent when not.
- **Why it beats always-loaded context:** carrying the full project mental model into every session costs tokens and dilutes focus. Lazy loading keeps each session's starting context minimal.
- **At repo scale:** exec plans checked into `docs/exec-plans/` extend this same principle. The plan persists as a first-class repo artifact without any explicit load step. See "Exec plans as first-class checked-in artifacts" under CLAUDE.md design.

### The blank-slate reset

Matt Pocock's highest-leverage action for anyone tuning their setup: delete everything and start from zero. Remove every skill, plugin, and MCP server. Delete `CLAUDE.md` and `AGENTS.md`. Go back to absolutely nothing. Then watch what the bare agent does before adding anything back.

- **Why it works:** the universal failure mode is bloating the context window with too many instructions, skills, and MCPs. Most never fire, but all of them cost tokens and dilute the weight of everything else (the same crowding that the CLAUDE.md-size and `/context` disciplines fight). You can't tell what's load-bearing until you've seen the agent run without it.
- **The rebuild rule:** layer back only what you miss, and make the additions procedures you consciously invoke rather than abilities the model auto-loads. Each ability re-leaks its description into context. Install things in a customizable form so you can experiment, and when you hit a real problem, build a targeted fix and delegate its implementation to an AFK agent.
- **Relation to existing discipline:** this is the periodic, aggressive version of freshness beats fullness. You reset not just a confused session with `/clear` but the config layer that silently accretes between sessions. Run it when you suspect your setup has drifted into bloat.

### Model adoption: wait out the launch noise, keep the harness model-agnostic

A risk-management heuristic from Pocock that complements the harness-over-model thesis: don't adopt a new model the week it ships. Wait about a month for the noise to settle. Launch hype ("one-shotted this!") rarely justifies the immediate cost, latency, and availability trade-offs. He waited on Opus 4.5, found it worked fine, and was still on Opus 4.8 at medium effort rather than Fable at recording time. The deeper principle: keep your workspace and harness as agent-agnostic as possible. Over-optimizing around one model's quirks (shorter prompts for this one, patches for that one's weak spot) means redoing the work each generation. Betting on durable software fundamentals keeps the setup working as models change. The standing tension is the bitter lesson, that maybe you should just ride model improvement, but the pragmatic answer is to improve the harness daily and use a good model, not pick one.

### Session setup: a data room is the upstream fix for hallucinations

The strongest intervention against AI hallucinations in serious knowledge work happens before the writing prompt, not inside it. A structured data room, a local folder the agent builds as its first task, prevents the structural hallucination pattern that took down a top law firm's court filing despite premium tooling.

The principle for Claude Code sessions: when a serious coding or knowledge-work session involves multiple source files, prior decisions, stale docs, and competing versions, don't open with "write the X." Open with "build me an inventory of the relevant materials, flag what's conflicting, flag what's missing, don't write the deliverable yet."

The writing prompt shrinks as the data room grows. A long, complex prompt often signals an unstructured source set: you're using prompt engineering to compensate for not having organized the inputs. After a proper inventory, conflict, and missing-context pass, the drafting prompt becomes a few sentences: which sources are authoritative, which are background, cite claims, flag anything unsupported.

Concrete artifacts to request before drafting:

- *Source inventory:* path, type, date, authority, current versus superseded, what claims each file supports
- *Conflict log:* explicit disagreements between sources, before the agent silently smooths them
- *Missing context list:* what's absent that the agent would otherwise invent around
- *Duplicates report:* the agent names version families and confidence, the human decides what's authoritative

The source inventory is the knowledge-work equivalent of an exec plan as a checked-in artifact: external memory that makes the agent's understanding of the project visible and correctable before it matters downstream.

### Claude Code's native memory: storage, injection, recall, and how to patch each

Claude Code's built-in memory does three jobs, worth evaluating separately rather than as one "memory" feature. Simon Scrapes decomposes them into storage (saving a fact), injection (loading context at session start), and recall (retrieving something old on demand). Native Claude Code is uneven across the three, and each weakness has a known patch:

- **Storage, decent but leaky.** The native choice is agent-decided and summarized: the agent quietly notices what's worth keeping and writes a condensed version. The summarizing keeps the store lean. The agent-decided trigger is the leak, since anything the agent doesn't flag is never saved. Patch: an automatic post-turn capture hook (summarize each turn with a cheap model, append to a daily log) removes dependence on the agent noticing. The cost is noise and volume, so pair it with pruning.
- **Injection, always-on but uncapped.** The native choice is hook-loaded (CLAUDE.md plus a memory index load every session, so it always happens) but with no character or token cap, which grows unbounded and crowds the window. This is the same bloat failure as a monolithic CLAUDE.md and the direct cause of context rot. Patch: a capped, cached frozen snapshot of the highest-value memories (identity, profile, most-important recent facts). Pay the tokens once per session and keep it lean.
- **Recall, the weakest of the three.** Native Claude Code has effectively no search. If a fact wasn't written to a memory file referenced by the index, the only fallback is resuming the exact prior session, whose context may already be compressed away. Patch: a local hybrid (semantic plus keyword) vector index over the stored memories, with zero API cost, finding by meaning rather than exact slug, with a multi-tier short-circuit (check the cheap injected snapshot first, fall through to deep search only if needed). The highest-value addition is cited-answer recall: return a written answer with source citations and an explicit "it isn't there" when the fact is absent. A confident answer with no source is worse than useless on real work. Caveat (verified): citations are not a faithfulness guarantee, since up to 57% of RAG citations can be post-rationalized ([arXiv:2412.18004](https://arxiv.org/abs/2412.18004)), so a cited-answer layer still needs a faithfulness check, not just a citation.

The portable asset is the evaluation lens: score storage, injection, and recall independently, then patch the weakest job with one targeted add-on rather than swapping the whole system. The patterns underneath are established practice (hybrid BM25, vector, and rerank; MemGPT and Letta tiered memory; cited RAG) and the source's named frameworks check out as real open source (Hermes = `NousResearch/hermes-agent`; "Memarch" = `zilliztech/memsearch`; GBrain = `garrytan/gbrain`, by Garry Tan and YC), verified 2026-06-11.

## CLAUDE.md design

### Structure, size, and what belongs in a project CLAUDE.md

Claude reads the CLAUDE.md file top-to-bottom on every session start and treats earlier content as higher priority. Size affects both token cost and instruction adherence: bloated files cost more and produce worse compliance.

- **Target size:** about 300 lines. Longer works, but each added line costs tokens at startup and dilutes the weight of every other instruction.
- **Priority order:** most critical rules at the top. Absolute directives ("never do X") and identity context ("this is a Swift UI app") before stylistic preferences.
- **Content that belongs:**
  - High-level technical architecture and project purpose
  - Domain context: framework, platform, non-standard DSLs or homegrown patterns
  - High-level file structure and module map
  - Design patterns in use
  - Build and validation flow (most important, see the Validation loops section)
  - Rule-style directives for recurrent mistakes: "never do X," "always do Y," with short code snippets for non-obvious patterns
  - Keyword triggers that invoke specific skills or build commands (for example, "use my Xcode MCP to build" maps to a specific invocation)
- **Never edit CLAUDE.md by hand for rule updates.** Tell Claude "update the rule so we never do X again" and it edits the file. This keeps the rules file Claude-owned and prevents human drift.
- **Compound engineering:** once a project's CLAUDE.md is stable and useful, commit it to the repo. Strip anything path-specific or overly personal. The bar is high: it should improve every team member's Claude experience. Evaluation is vibes-based for now (test a few weeks, ask for feedback), with no settled quantitative framework yet.
- **Failure modes of a monolithic CLAUDE.md** (from OpenAI's production work): *context crowding*, where a large file crowds out the task, the code, and the relevant docs; *non-guidance*, where everything is "important" so nothing is and agents pattern-match locally instead of navigating intentionally; *instant rot*, where a monolithic file becomes a graveyard of stale rules the agent can't evaluate for freshness; *not mechanically verifiable*, where no CI can check a blob for coverage, freshness, or cross-link correctness. Fix: use CLAUDE.md as a table of contents backed by a `docs/` directory that is the system of record, and enforce freshness mechanically (CI jobs, recurring doc-gardening agents). The 100-line CLAUDE.md with 50-line per-service nested files is consistent, both a context-budget rule and a structural clarity rule.

### Prefer linters over documentation for enforcing agent behavior

Before adding a new instruction to any CLAUDE.md, ask whether you can encode it as a linter. If yes, that's strictly better, since it's enforceable rather than advisory. Lint failures are deterministic, cheap, and survive context-window limits. Instructions in a CLAUDE.md don't.

OpenAI's pattern: custom linters (written by Codex itself) enforce architecture, naming conventions, structured logging, file-size limits, and platform-specific reliability requirements. The team writes error messages on lint failures to inject remediation instructions directly into agent context, so the lint failure becomes its own prompt rather than a raw error the agent has to interpret.

This reframes how to grow instruction files: drain CLAUDE.md into linters over time rather than adding more advisory text.

### Exec plans as first-class checked-in artifacts

Treat plans as explicit, versioned, repo-resident artifacts rather than working notes or mental models. OpenAI's structure: `docs/exec-plans/active/`, `docs/exec-plans/completed/`, and `docs/tech-debt-tracker.md`, all checked into the repository alongside code.

This means:

- The agent can always see what plan is active and its current state
- Completed plans serve as decision history the agent can reference
- Known technical debt is visible to the agent and can be addressed systematically

This extends the second-brain, lazy-load pattern. Instead of a session-level notes file, the plan is a first-class repo artifact that persists across sessions without any explicit load step. Same principle, external memory for agents, executed at the repo level rather than the session level.

### Boring tech is better for agents

A design heuristic from OpenAI's production experience: technologies commonly described as "boring," with stable APIs, composability, and good representation in training data, are easier for coding agents to model and work with correctly. Sometimes it's cheaper to have the agent reimplement niche functionality than to work around opaque behavior from a specialized library the agent can't fully reason about.

Worked example: instead of pulling in a `p-limit`-style concurrency package, OpenAI's team had Codex implement its own `map-with-concurrency` helper, tightly integrated with their OpenTelemetry setup, with 100% test coverage and exact semantics for their runtime.

When a coding agent will be the primary author and maintainer of code, "how well can the agent reason about this dependency?" becomes a first-class evaluation criterion alongside the usual ergonomics, popularity, and maintenance considerations.

Open question: is this a training-data-coverage argument that weakens as models improve, or a structural composability argument that holds regardless?

## Review and external AI reviewers

### Use a second AI as an external reviewer at phase boundaries

Have a different model review work before it's declared done. It catches mistakes the implementing model papered over, because the implementer and the reviewer share fewer blind spots than a single model reviewing its own output.

- **Concrete instantiation, GSD `/gsd-review --phase 8 --all`:** in the GSD workflow, this command builds a consolidated review prompt covering everything in the current phase and invokes Codex as the external AI reviewer. Phase 8 is the review phase, and `--all` pulls the full phase scope into the prompt.
- **Why it works:** Codex is a different model family from Claude, so it tends to flag things Claude missed and vice versa. The consolidated prompt matters, since reviewing in one pass with full context beats fragmented file-by-file review.
- **When to use:** end of a phase, before merging, before declaring a milestone done. Anywhere you'd want a second pair of eyes but don't want to block on a human reviewer.
- **Pattern (tool-agnostic):** whenever a phase or milestone wraps, build a consolidated prompt with the diff, context, and intent, hand it to a different model, and treat its output as a code-review comment thread rather than gospel.

## Orchestration architecture

### Orchestration and quality-of-execution are different layers

When evaluating an agentic framework, first ask what layer it operates at before comparing it to alternatives. This avoids apples-to-oranges choices and clarifies where each tool belongs in a stack.

- **Three layers worth naming:** (1) portfolio or PM, for cross-project, cross-domain coordination; (2) per-project orchestrator, which decomposes and drives a single project to done; (3) quality-of-execution, for how each task inside a session gets done well (TDD, debug, verify).
- **Concrete placements (as of April 2026):**
  - GSD: per-project orchestrator, milestone-driven.
  - ccpm (automazeio/ccpm): per-project orchestrator, spec and task-driven with GitHub Issues as source of truth. A genuine alternative to GSD, pick per project shape.
  - superpowers (obra/superpowers): quality-of-execution skills (TDD, systematic-debugging, verification-before-completion, writing-plans). Runs inside a GSD or ccpm session, not instead of one.
- **Why this matters:** "GSD versus superpowers?" is not a real question, since they're different layers. "GSD versus ccpm?" is the real orchestrator choice. Mixing the levels collapses the architecture and forces false trade-offs.
- **Pattern:** before adopting a new framework, write one sentence placing it in the layer stack. If it doesn't fit cleanly, suspect the framing.

### Sub-agents: bring work to context, not context to work

Sub-agents are for atomic, isolated tasks, not for distributing complex reasoning. The mistake is treating sub-agents as a way to parallelize work that requires the session's full context to do correctly.

- **Good use cases:** atomic work with well-defined inputs and outputs that doesn't need to know how the session got here: writing a file, running a lookup, sending a notification, generating a report from structured inputs.
- **Bad use cases:** testing agents that need to understand the code they're testing, review agents that need the full diff and reasoning history, debug agents that need the execution trace. For these, keep the work in the main session, since the model that wrote the code is best positioned to test it.
- **Why:** sub-agents return only their output, not their reasoning path. Anything downstream that needs the reasoning to be correct, not just the result, will be missing critical context.
- **Common anti-pattern:** CEO to PM to design to engineering agent chains. These spread context across agents that all need each other's state. The chain degrades because each hop loses signal.
- **Create sub-agents the same way as skills:** do the work once in the main session, then say "use what we just did to create a sub-agent for X."

### Simple scales with agents

Cursor's empirical finding, relayed by Nate B Jones: they tried three levels of agent management and performance degraded. Two levels (planner plus short-running executor sub-agents) held across millions of lines of code. The constraint appears structural, since agents lose coherence at deeper supervision chains in a way that differs from human management.

- **Why it works at two levels:** the planner agent holds the project-scoped goal, and the executors are short-running, bounded, and directly supervised by the planner. Each supervision hop introduces error. Two hops the system can absorb, three it can't.
- **Why this matters for any per-project orchestrator:** don't add a "manager of the manager" inside one project. If you need cross-project coordination, put it on a different axis (portfolio, not project), see the next entry.
- **When to use:** every time the impulse hits to add a supervisor over an existing planner-executor setup within one project. Resist unless the axis changes.
- **Pattern:** if you're about to add a management layer, write one sentence naming the axis it operates on. If that axis matches a layer already in the system, you're stacking rather than decomposing, and stacking is what Cursor reports fails.

### Human-as-manager to agent-as-manager is the project-scale unlock

The counterintuitive reframe for project-scale agentic work: ask "how do I make it easy for the agent to do the work?" rather than "how do I speed up my human engineers with agents?" Keeping the human at the center leaves all the bottlenecks in place (reviewer cadence, context-handoff rituals, merge discipline designed for humans reading each other's diffs). They slow down the agent instead of the human.

- **Why it's load-bearing:** most individual-scale speedups feel great (one developer plus agent ships faster) but stall at project scale because the system around the agents is still human-shaped. Moving the agent into the manager seat unlocks project scale.
- **How to apply:** when designing an agentic workflow that will run at project scale, audit the bottlenecks and ask which exist because a human reviewer or coordinator sits in the loop. The ones that exist because of the human are candidates for agent-owned coordination. Keep the human in the loop only where judgment is required.
- **When to use:** whenever a "how do I speed up X?" conversation starts, swap the question to "how do I make it easy for the agent to do X end-to-end?" and see what falls out.

### Per-project orchestrators don't solve portfolio coordination

GSD, ccpm, and similar frameworks handle within-project parallelism well (workstreams, `parallel: true` metadata, dependency graphs). None coordinate across projects or across domains (code plus research plus content). Multi-project, multi-domain work needs a portfolio-level layer above the orchestrators, and it doesn't exist off-the-shelf.

- **Signal you're hitting this gap:** the operator overhead of keeping multiple concurrent threads aligned becomes the bottleneck, not the execution of any individual thread.
- **Borrowed primitive worth calling out:** ccpm's deterministic bash scripts for status (`status.sh`, `standup.sh`) avoid LLM token cost on reads. Portfolio state-read should follow the same pattern, with inference only where judgment is needed.

## Parallel development

### Multiple concurrent Claude instances as a workflow primitive

Running several Claude Code sessions at once, each on a separate workstream, is a first-class workflow pattern rather than an edge case. The mental model is managing multiple async workers: give each a command, switch to the next while it runs, come back when it finishes.

- **Terminal setup (iTerm2):** `Cmd+D` creates a new split pane, and `Cmd+[` and `Cmd+]` switch between panes. Rename tabs to track what each session works on. Voice input (Whisper) makes it practical to prompt multiple sessions without retyping.
- **Bottleneck at scale:** the limiting factor becomes your own context-switching capacity, not Claude's throughput. Keep each session's scope narrow enough to hand off cleanly.
- **Notifications:** configure Claude to emit a sound or system alert on completion so you know when to return to a session without polling.

### Git worktrees for same-project parallel execution

Running multiple Claude instances on the same project at once requires git worktrees, otherwise the instances conflict on file edits.

- **What it is:** git worktrees create independent checked-out copies of the repo on different branches, all sharing the same git history. Each Claude instance gets its own worktree, so edits don't collide.
- **When to use:** any time you want to parallelize work across features or approaches within one project. Without this, you serialize.
- **Watch-out:** worktrees multiply disk usage and can complicate merge workflows if branches diverge far before review.

## Open questions

- Patterns for hand-off between Claude Code sessions: what context survives, what doesn't
- When to prefer an MCP server over a CLI command for a given integration
- The right evaluation framework for a CLAUDE.md committed to a shared repo (vibes-based for now, no settled quantitative approach)

## Sources

- [50 Claude Code Tips](https://www.youtube.com/watch?v=mZzhfPle9QU) — YouTube. Source for validation loops, the freshness-beats-fullness context discipline, the second-brain lazy-load pattern, CLAUDE.md structure and size, sub-agent usage philosophy, and the parallel-development patterns.
- [Harness Engineering: Leveraging Codex in an Agent-First World](https://openai.com/index/harness-engineering/) — OpenAI (Ryan Lopopolo). Source for CLAUDE.md-as-table-of-contents versus the monolith, linters over documentation, exec plans as checked-in artifacts, and the boring-tech-is-better-for-agents heuristic.
- [Agents Means 4 Different Things and Almost Nobody Knows](https://www.youtube.com/watch?v=YpPcDHc3e9U) — Nate B. Jones, YouTube. Source for Cursor's simple-scales-with-agents lesson and the human-as-manager to agent-as-manager project-scale reframe.
- [The One AI Writing Hack Nobody Talks About](https://www.youtube.com/watch?v=ltbzgzZZmgI) — Nate B. Jones, YouTube. Source for the data-room pattern, the writing prompt shrinking as the data room grows, and the source-inventory, conflict-log, missing-context, and duplicates artifacts.
- [I Built The Best Claude Memory System (Beats Hermes)](https://www.youtube.com/watch?v=H9BUkgDf5Y4) — Simon Scrapes, YouTube. Source for the storage, injection, and recall decomposition of Claude Code's native memory and the per-job patch for each.
- [Matt Pocock's Agentic Engineering Workflow](https://www.youtube.com/watch?v=nQwJVHCtDDY) — Matt Pocock, YouTube. Source for the blank-slate reset and the model-adoption heuristic (wait about a month, keep the harness agent-agnostic).

## Changelog

- **2026-06-21** — Migrated to the public site; sanitized and run through the publish pipeline.
- **2026-06-11** — Added Claude Code's native memory (storage / injection / recall) and how to patch each.
- **2026-06-01** — Added the data-room session setup as the upstream fix for hallucinations.
- **2026-05-20** — Topic created: validation loops, context engineering, CLAUDE.md design, external review, and parallel orchestration with worktrees.
