---
title: Skill Design and Management
description: How to build, test, version, and govern agent skills that produce reliable outcomes across the full lifecycle.
lastUpdated: 2026-06-21
---

Skills produce reliable outcomes when you treat them like software rather than
prompts. This topic covers the full lifecycle: drafting, testing, versioning, and
governing skills invoked by humans or agents. The best practices keep shifting as
agents take over more of the invocation, so the design requirements shift with them.

## Key concepts

### The description field is the skill's API

The description field in SKILL.md frontmatter decides whether an agent invokes a
skill. It is the most critical element and the most neglected one. Most builders
write descriptions that run too generic, too short, or focused on what the skill
is rather than when it should fire.

Write descriptions that push. List the contexts, keywords, user phrases, and
situations where the skill should trigger. Treat it as a targeting algorithm, not a
docstring. Include both what the skill does and the specific signals that trigger
it, including the edge cases where the skill helps but the user never names it.

A description-optimization workflow (eval queries, train/test split, iterative
refinement) systematically improves triggering accuracy.

### Agent-first design

Agents now call skills more often than humans do. That changes the design
requirements:

- **No recovery loop.** A human who triggers a skill and gets bad output corrects
  it. An agent calling a skill gets no such intervention. Bad output propagates
  silently and grows expensive at scale.
- **Contract-style interfaces.** Agent-driven invocation needs explicit inputs,
  expected outputs, and failure-mode handling. The skill behaves like a
  well-defined function, not a loose prompt.
- **Description as discovery mechanism.** A vague description means agents miss the
  skill when they need it, or call it when they shouldn't.

Assume an agent will call your skill. Make inputs and outputs explicit, handle edge
cases defensively, and write instructions that don't lean on human judgment to
cover ambiguity. Assuming an agent can call it is itself a choice. Sometimes you
keep invocation in human hands and suppress the description entirely.

### Procedures vs. abilities: who invokes the skill

A second invocation axis cuts across agent-first design. Who triggers a skill
determines how you write it and what it costs. Matt Pocock, who maintains the
most-followed public skills repo (`mp-skills`), splits skills two ways:

- **Abilities** are skills the model invokes itself, mid-task, when it decides
  they're relevant. A "React coding standards" ability the agent pulls in while
  writing a component to check house style (use X not `useEffect`) is one example.
  These are the discovery-driven skills, and they carry a hidden tax: every ability
  leaks its description into the context window whether or not it fires. 100
  abilities means 100 descriptions resident in context every turn. This is the same
  context-crowding failure as a monolithic CLAUDE.md, relocated to the skill layer.
- **Procedures** are skills the human invokes deliberately to make the model behave
  a certain way (`grill-me`, `2PRD`, a planning skill). The human stays the driver
  and chains them: `grill-me` to `2PRD` to splitting into issues to implementing.
  Pocock prefers procedures, saying "I don't want to delegate my thinking to the
  model," and contrasts that with the model-in-control stance of Obra's
  `superpowers`. Neither is wrong. It is a control-philosophy choice that maps onto
  the same human-as-driver versus agent-as-driver axis running through the
  orchestration literature.

The context-leak lever is `disable model invocation: true`. A skill flagged this
way can only be invoked by the user, and its description stays out of context. That
makes "procedure vs. ability" an enforceable setting rather than an authoring
intent. The design rule follows: if a skill is meant for human invocation, disable
model invocation so you stop paying its description tax every turn. Audit your skill
libraries for abilities that should be procedures. Each one reclaimed returns
context budget.

- **Source:** Matt Pocock's agentic engineering workflow (2026-06-21)

### Stateful vs. stateless skills

A skill is stateless when it needs no memory of prior runs. Most procedures are:
invoke, run, done. A skill is stateful when it relies on information persisted
locally between invocations. Pocock's `teach` skill is the canonical stateful
example: it writes a `mission.md`, a learning record, and lesson artifacts to the
workspace, so it behaves like a real teacher who remembers what you've done, where
you are, and what's next. Stateful skills must declare where state lives and run in
a workspace that can hold it, and they inherit all the staleness and pruning
concerns of any persistent memory layer. Default to stateless. Reach for stateful
only when continuity across sessions is the actual value: teaching, long-running
projects, accumulating context.

- **Source:** Matt Pocock's agentic engineering workflow (2026-06-21)

### Knowledge, skills, wisdom: what can and can't be bundled

Pocock decomposes "being good at something" three ways, which bounds what a skill
file can encode:

- **Knowledge** is the conceptual understanding of a thing.
- **Skills** are the muscle memory from having done it many times.
- **Wisdom** is knowing when to do it and how it fits the real world.

Knowledge and skills bundle well. They are what a well-written skill or reference
captures and ships. Wisdom does not bundle. Pocock calls it "almost impossible to
obtain without actually having done the thing in the exact context where you need to
do it." You can skill-file your way to the knowledge and skills of an Anthropic
engineer. You cannot skill-file their wisdom without working there. So a skill
should aim to transfer knowledge and procedure, and stay honest that judgment of
when remains with the human invoker. This is also why procedures, where the human
decides when, age better than abilities for anything where the timing is the hard
part.

- **Source:** Matt Pocock's agentic engineering workflow (2026-06-21)

### Three-tier architecture for teams

Organizations managing multiple skills at different levels of formality can sort
them into three tiers:

1. **Personal skills** are individual productivity shortcuts and automations. Loose,
   experimental, low governance overhead.
2. **Team skills** stay shared within a functional group. Standardized workflows,
   consistent outputs, moderate testing.
3. **Organizational skills** run enterprise-wide, admin-controlled, and
   version-managed, available across all surfaces (Claude, Excel, PowerPoint, Claude
   Code). They need test suites, change management, and rollback capability.

The tiers map to different levels of testing rigor. Personal skills can run on
vibes. Organizational skills need quantitative evaluation.

### Quantitative testing and versioning

Treat skills like software:

- **Test suites.** Build a basket of realistic test cases that exercise the skill
  across scenarios. An eval framework with `evals.json`, parallel test runs, and
  grading supports this.
- **Version control.** Increment a version, even informally with dated notes, when
  you change a skill. Run the test suite before and after.
- **Measurable comparison.** Measure pass rates, compare across versions, track
  regressions. Don't eyeball results.
- **Iterative refinement.** Wording changes trigger unpredictable parts of a
  transformer's latent space. Getting the right behavior can take three or four
  wording iterations with measured results each time.
- **Compounding payoff.** A well-tuned skill gets called thousands of times. Small
  quality improvements multiply across every invocation, which justifies the upfront
  testing.

### Skill lifecycle

The full lifecycle described across sources:

1. **Capture intent.** What should the skill do? When should it trigger? What output
   do you expect?
2. **Draft.** Write the SKILL.md with description, instructions, and structure. Keep
   it under 500 lines and use progressive disclosure (references/, scripts/) for
   depth.
3. **Test.** Run against realistic prompts, human and agent-triggered.
4. **Quantify.** Grade results, measure pass rates, compare versions.
5. **Iterate.** Refine wording based on measured results. Generalize rather than
   overfit.
6. **Deploy.** Roll out to the appropriate tier, from personal to team to org.
7. **Maintain.** Monitor performance, update when requirements change, prune stale
   skills.

### The composability framework: skills, MCPs, sub-agents, hooks, plugins

Claude Code has four composable primitives:

1. **Skills and slash commands** are recurring workflows saved as SKILL.md files in
   a designated directory. Claude discovers and invokes them by name. Skills and
   slash commands now unify (a recent Anthropic change, as of around 2026-04): a
   skill named `fetch-hackernews` is automatically available as `/fetch-hackernews`.
   The creation pattern is to do the workflow once, then tell Claude "save this as a
   skill called X," rather than writing them from scratch.
2. **MCPs (Model Context Protocol)** connect to external tools and services.
   Powerful but expensive in context tokens, since each active MCP adds to every
   turn's overhead. The default posture is no MCPs unless the project needs one. Ask
   Claude to find and install them rather than managing config files by hand.
3. **Sub-agents** are parallel workers for atomic, isolated tasks. They suit work
   with well-defined inputs and outputs that doesn't need the session's reasoning
   history.
4. **Hooks** automate pre and post tool use. A post-tool hook runs a linter or
   formatter after every edit. A pre-tool hook blocks destructive operations before
   they execute. They work like git hooks. Ask Claude to create and configure hooks
   rather than writing them by hand.

Plugins package any combination of these into a single installable unit: a skill
that triggers an MCP that invokes a sub-agent, with a hook for cleanup, all bundled
and shareable. Anthropic runs an official plugin ecosystem, and community plugins
exist too. This is how personal productivity workflows become shareable team
infrastructure.

Because these primitives compose, the interesting design question is how to chain
them rather than which one to use. A well-designed skill can call a sub-agent that
uses an MCP and posts a result through a hook. The combination enables workflows
none of the primitives manage alone.

Let Claude own the lifecycle rather than maintaining it by hand. Ask Claude to
create and update all five primitives. Treat them as Claude-owned artifacts you
describe intent into, the same as CLAUDE.md rules, not config files you maintain.
The pattern: "save what we just did as a skill called X," "extend the X skill to
also do Y," "update X so it always does Z." Manual edits cause drift between what
the skill says and what Claude does. Keeping Claude in the loop keeps them coherent.

- **Source:** 50 Claude Code tips (2026-04-22)

### Conditional rule files and cross-agent sync

Stripe validated two patterns in production in 2026 across Minions, Cursor, and
Claude Code. Both apply directly to any large codebase.

First, directory-scoped conditional rules beat global unconditional rules. In a
codebase of significant size, unconditional global rules hit a hard scalability
limit: they load into every agent context window regardless of what the agent does.
At Stripe's scale (hundreds of millions of lines of code), global rules would fill
the agent's context before the task begins. The workable model scopes rules to
specific subdirectories or file patterns, attached automatically as the agent
traverses the filesystem. Most of Stripe's agent rule files are conditional. They
load only when the agent enters the relevant directory or touches the relevant file
patterns. This formalizes the directory-nested CLAUDE.md principle as a design
policy rather than an ad-hoc practice. When you author rule files, default to the
narrowest scope that covers the relevant code. An unconditional global rule should
exist only if it applies to every file in the repo. Most rules apply to a service, a
library, a language, or a domain.

Second, cross-agent rule sync means writing once and having all agents read it.
Stripe runs three primary coding agents in the same codebase: Minions (a custom
harness), Cursor, and Claude Code. Rather than maintaining separate rule file sets
per agent, they standardized on Cursor's rule format, which supports
directory-scoped conditional attachment, and synced it to the formats each agent
reads. Engineers author context conventions once. All three agents, from fully
unattended Minions to supervised Cursor sessions to interactive Claude Code
sessions, read the same guidance and follow the same conventions. If your team runs
more than one agent against the same codebase, check whether you duplicate rule
maintenance. Settle on a canonical format your agents can all read, or a sync step
that keeps them aligned, and invest in rules once.

This reinforces the skill-lifecycle pattern. Skill and rule authoring is
high-leverage because each authored rule amortizes across every agent invocation
that traverses its scope. At Stripe's scale, that means thousands of Minion runs per
week benefiting from a single well-written rule file.

### Instruction freshness reviewers

Cloudflare adds the most concrete maintenance pattern for repo-local agent
instructions: run a dedicated reviewer whose job is instruction freshness, not code
correctness. Their AGENTS.md reviewer looks for material repo changes that should
update agent guidance: package-manager changes, test-framework changes, build-tool
changes, CI/CD changes, new environment variables, and major restructures.

Most skill and rule systems skip this lifecycle step. Instruction files rot because
the codebase changes silently underneath them. A reviewer that asks "did this diff
invalidate the instructions future agents will read?" turns rule-file maintenance
from ad-hoc cleanup into a review concern.

The anti-patterns Cloudflare flags transfer directly to skills and CLAUDE/AGENTS
files:

- generic filler that sounds helpful but changes no behavior,
- files over about 200 lines that become context dumps instead of guidance,
- tool names without runnable commands,
- broad workflow instructions in one shared file when narrower workflow-specific
  guidance would read clearer.

The positive standard is concise, command-bearing, scoped instructions. A rule file
tells the agent what to do, when it applies, and which command proves it.

### Community and sharing

Community skill repos serve as both distribution and learning mechanisms. Watch how
other practitioners structure their skills, which domain-specific templates recur,
and which testing approaches you can adopt.

## Current thinking

The composability framework (skills plus MCPs plus sub-agents plus hooks, packaged
as plugins) is now the canonical Claude Code mental model for building compound
workflows. A skill that invokes scripts, calls sub-agents for parallel extraction,
and eventually ships as a packaged plugin shows the pattern in practice.

Two gaps keep recurring across teams: most skill libraries lack formal version
tracking, and most testing stays human-invoked rather than agent-triggered. The
skills and slash-command unification also means existing slash commands may now
duplicate skill invocations, which is worth auditing.

Pocock's procedures-vs-abilities lens adds a concrete audit task. Classify every
skill as a procedure (human-invoked, `disable model invocation: true`, no
description leak) or an ability (model-invoked, paying the description tax). The
blank-slate reset he recommends, where you strip everything, observe the bare agent,
then layer back only the procedures you consciously choose, keeps a skill library
from accreting context-leaking abilities nobody invokes.

The Cloudflare AGENTS.md reviewer adds a maintenance loop. Every significant repo
change should ask whether agent instructions changed too. The analogous reviewer for
a skill library flags when a workflow changes but the SKILL.md still encodes the old
command, output shape, or trigger language.

## Open questions

- How do you measure agent-triggered versus human-triggered skill performance
  separately?
- What does skill governance look like at scale: approval workflows, rollback,
  access control?
- What's the right cadence for re-testing skills: after every edit, or on a
  schedule?
- How do community skill repos handle quality control and contribution standards?
- Should a lightweight instruction-freshness check live inside code-review or
  handoff workflows, so stale skills and rules get caught alongside code changes?

## Sources

- [Anthropic, OpenAI, and Microsoft Just Agreed on One File Format. It Changes Everything.](https://www.youtube.com/watch?v=0cVuMHaYEHE) — Nate B Jones, YouTube. Source for description-field optimization, agent-first design, the three-tier architecture, and the quantitative testing methodology.
- [50 Claude Code Tips](https://www.youtube.com/watch?v=mZzhfPle9QU) — YouTube. Source for the composability framework (skills, MCPs, sub-agents, hooks, plugins), the skills and slash-command unification, and the let-Claude-own-the-lifecycle principle.
- [Minions: Stripe's one-shot, end-to-end coding agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents) — Alistair Gray, Stripe. Source for conditional directory-scoped rule files as a scalability requirement and cross-agent rule sync across Minions, Cursor, and Claude Code from a single canonical format.
- [Orchestrating AI Code Review at scale](https://blog.cloudflare.com/ai-code-review/) — Ryan Skidmore, Cloudflare. Source for the AGENTS.md freshness reviewer, instruction-file rot signals, and the anti-patterns including generic filler, oversized instruction files, and tool names without runnable commands.
- [I Ranked Cloudflare's Software Factory and Wow… S TIER TOKENOMICS](https://www.youtube.com/watch?v=YG4t7aMY81c) — YouTube. Commentary critique that shared agents.md surfaces become overloaded and may need workflow-specific instruction scopes.
- [Matt Pocock's Agentic Engineering Workflow](https://www.youtube.com/watch?v=nQwJVHCtDDY) — YouTube. Source for procedures vs. abilities and the description-leak tax, `disable model invocation: true` as the context-leak lever, stateful vs. stateless skills with `teach` as the stateful exemplar, the knowledge/skills/wisdom decomposition, and the blank-slate reset as a library-hygiene discipline.
