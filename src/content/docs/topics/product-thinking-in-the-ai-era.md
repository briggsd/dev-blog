---
title: Product Thinking in the AI Era
description: The scarce skill is no longer execution but knowing what to build and for whom — how product thinking changes once AI makes code cheap to produce.
lastUpdated: 2026-05-29
---

"Product thinking" connects work to users, outcomes, and the "why" behind what gets built. The discipline is changing as AI makes code cheaper to produce than ever. The central claim this topic tracks: the scarce skill is no longer execution. It's knowing what to build and for whom. AI didn't create the gap between engineering and outcomes; it made that gap more economically visible.

This topic covers how product thinking shows up (or fails to) in engineering teams, the cultural and leadership conditions that make it possible, and whether those conditions scale as tools, teams, and AI agents all get more capable.

## Key concepts

### The disconnection diagnosis

Matt Watson's *Product Driven* (echoed by Marty Cagan, Teresa Torres, and others) frames the root failure mode as *disconnection* rather than process. Three disconnects compound:

- Between engineers and the users they build for
- Between output (shipped code) and outcomes (real change for users)
- Between what gets built and what matters

Symptoms: teams that ship on time into silence, roadmaps that fill with features no one uses, retrospectives that focus on process blockers instead of customer impact, and a quiet slide where "busy" gets confused with "making progress."

Watson's sharpest line on this: *"AI didn't break the system. It exposed how fragile it already was."* Before AI, a team could be disconnected from outcomes and still feel productive, because shipping itself was slow and visible. When execution gets cheap, the lack of direction becomes loud.

### The "why" question as cultural litmus test

One question diagnoses team health: *"Why are we building this?"* Teams that can ask it openly, without political cost, stay connected to outcomes. Teams where asking it reads as threatening timelines, questioning leadership, or "not being a team player" have lost product thinking.

The question does two things at once. It reconnects the work to purpose, and it signals psychological safety. Watson calls it *"the dividing line where execution shifts toward ownership, and task completion turns into real product thinking."*

The political cost of this question rises once plans are locked. That cost is the temporal axis of the same barrier whose cultural axis sits above, described next.

### The roadmap momentum trap

Once someone has scoped, resourced, and promised a plan, the cost of asking "why" changes. It stops being a question and becomes a political act that threatens timelines and challenges decisions that are already "sold."

The trap: the best time to ask "why" is before the plan is locked, but that's when teams feel least qualified to do so. By the time they're close enough to see the problem, the machine is already in motion and it's "too late" to question.

Leaders have to *make* time and space for the question *before* momentum builds. Waiting for the team to raise it under pressure asks them to pay a cost that most will decline to pay.

### Product thinking as a distributed property

A recurring claim across the product-thinking canon: product ownership cannot live in a single role (founder, PM, tech lead) without the system becoming fragile. Watson's version: *"You can't put product thinking on one person. When that happens, the rest of the team stops thinking like owners."*

This matters in the AI era because AI collapses the cost of execution, which leaves the "product thinker" bottleneck as the hardest part of the system to distribute. Organizations that over-index on a single Chief-Product-Mind will find that bottleneck harder to relieve as everything else speeds up.

The same argument applies to distributed knowledge systems: context and judgment can't live in one place if the system is going to scale.

### Workflow-first investment thinking

Nate B Jones's frame for why AI projects fail at the investment layer: teams skip the foundational question (*what is the shape of the work itself?*) and go straight to model selection, vendor evaluation, or dashboard design. All three sit downstream. At the root is whether the team can describe the work with enough precision to make a tractable investment decision.

The "workflow" is the entire operating loop: what information comes in, what the system is allowed to do, what good output looks like, who checks what, what gets escalated, who is accountable. The AI model is one component of that loop, critical but not the loop itself.

Once the team describes the workflow with precision, the investment choice becomes a checklist across five levers: automate (delete the workflow), build (own a complex/specific loop), buy (primitives or full pipeline solutions), hire (fill the specific capability gap), or wait (lower-priority workflows in a maturing category). The right answer is often a combination.

The central maxim: **do not automate what you cannot describe.** It belongs in every AI investment review. If the team can't state the inputs, outputs, exceptions, standards, and ownership in plain English, they are not ready to automate.

This is the investment-layer version of the disconnection diagnosis. The roadmap momentum trap (Watson) and the "cannot describe" failure (Jones) describe the same dynamic at different stages: teams committing resources to work they don't understand.

The "what good looks like" problem follows from shared ownership. The executive who says "go build it and make it good" without being able to evaluate the output hasn't given a mission. They've built an incentive structure where the team will deliver *something* and call it done, because no honest third-party check sits in the loop.

### Capability phase to economics phase

A frame that complements Watson's "AI exposed fragility": 2024–2025 was the *capability phase* of AI, where the dominant question was *can we build it?* What's possible? Who can push the frontier? 2026 is the *economics phase*, where the question shifts to *can we build it AND make margin on it? What's sustainable?* Selection pressure on AI products and teams now runs through unit economics, not capability demos.

This phase shift connects otherwise-disparate 2026 stories: the SaaS apocalypse (per-seat pricing collapses when 10 agents do the work of 100 reps); Sora's shutdown (~$15M/day inference vs. $2.1M lifetime revenue is unsurvivable regardless of capability); Anthropic's defense-contract refusal (safety posture as market position with revenue consequences); the rise of outcome-based pricing as a survival requirement.

For product leaders: the reflexive "ship the capability and figure out the business model later" stance that worked in the capability phase is now dangerous. Product thinking in 2026 means asking *what can we build that has positive unit economics at the inference layer*, not just *what can we build*. The most important number in AI is shifting from training FLOP count to **inference cost per delivered unit of revenue**.

### The four-or-five future roles

A second frame to hold alongside the disconnection diagnosis. As agents take over execution-layer work, Nate B Jones argues the durable human roles cluster into four (possibly five):

1. **Tool-using generalist**: the spark; can name the right AI tool, get something started, drive it toward completion. Includes vibe coders, and goes further by directing long-running agentic processes.
2. **Pipeline engineer**: infrastructure, security, data movement, measurement. Where conventional engineering is evolving.
3. **Relationship-driven operator**: salespeople, deal closers, trust-builders. One prediction worth tracking: agent-run businesses will start hiring human salespeople as the human face of the company because close-rates require it.
4. **"Adult in the room" / judgment role**: maturity to put the brake on the system. When *not* to speed up. Often takes the CEO hat, but the role is the function, not the title.
5. *(Likely fifth)* **Creative**: the envision-the-experience role. Rare but high-leverage; few people have this today.

These roles sit **above** the agents, not alongside them. The product-thinker function maps across several of them, particularly (4) and (5). Watson's "shared ownership" still applies, but the *what* being owned shifts from execution toward direction-setting and judgment-calling.

For team design: when staffing a small AI-native team, ask whether each of these roles is present. Most teams default-staff for (1) and (2) and underweight (3) and (4), the pattern that produces fast-moving teams that ship the wrong thing.

### Agent work units and the work-unit metric shift

In February 2026, Salesforce introduced **Agent Work Units (AWUs)** in its fiscal Q4 earnings, a measure of tasks accomplished by AI agents. 2.44 billion AWUs delivered to date across Agentforce and Slack, growing 57% QoQ. Note what this signals: the biggest SaaS company on the planet is not talking about seats, sessions, or tokens. It is trying to name the **work unit**.

This is the industry-level signal of a broader metrics shift, from activity proxies (clicks, sessions, messages) toward work-unit primitives. A work-unit count helps only if the team knows *what kind of work happened*, whether the tool calls succeeded, whether the user trusted the output, and whether the business outcome improved. Without run-level context, AWUs become the new "active user": a better name on the same problem of measuring activity instead of outcomes.

The pattern connects to Watson's disconnection diagnosis. *Teams that ship on time into silence* is the human-execution version; *agents that complete tasks users quietly redo* is the agentic-execution version. Same structural failure, different surface.

**The operationalization:** Completion rate ≠ acceptance rate. High completion plus low acceptance means the agent is finishing work users don't trust. High completion plus high acceptance signals a workflow ready for more autonomy. Most current dashboards, and most early work-unit metrics, cannot see the gap between the two.

### Working intelligence as a fifth category of professional capital

For decades, professional capital has had four components: **what you know** (skills), **what you can do** (abilities), **who you know** (network), and **what you can prove you've done** (track record). All four live in the human, in heads, relationships, and reputation, and travel with you.

A fifth category is emerging: **working intelligence**, the accumulated context and calibration that makes you effective with AI tools. This category has a property the others don't: *it lives outside your head, on third-party servers controlled by parties with a direct financial interest in keeping it there.*

Implications for product thinkers and leaders:

- Hiring evaluation has to evolve. Resumes don't capture working intelligence. (Meta and others are already flying candidates in and locking them in a room with company laptops to evaluate AI capability, a clumsy proxy.)
- Teams that develop *portable* working intelligence, captured in markdown, MCP-exposed databases, or other portable formats, compound effectiveness across role changes, tool changes, and IT-policy changes. Teams that pour their working intelligence into walled-garden platform memory reset on every transition.
- The career advantage isn't in today's tooling, which is rough. It's the **habit of ownership** itself, a recurring compounding skill.
- This connects to the disconnection diagnosis: a team whose working intelligence is locked inside one platform adapts to outcome shifts worse than one that owns its context.

### Empathy as a two-way requirement

Product thinking depends on empathy for users, but empathy runs both directions. *If engineers don't feel empathy from leadership, they won't extend it to users.* When engineers feel boxed in, dismissed, or treated as ticket-runners, they stop caring about the user experience. The modeling from above told them it wasn't part of the job.

The operational version: leaders who want their teams to "care about users" have to first show that they care about the team. That includes listening for honest tension instead of rewarding fast agreement, making "no" an acceptable answer, and protecting people from chaos rather than translating it downward.

### Five foundations as a scaling pattern

Watson's framework (Vision → Focus → Clarity → Shared Ownership → Courage) maps onto Google's Project Aristotle findings (psychological safety, dependability, structure/clarity, meaning, impact). Both arrive at the same claim: *performance comes from environment, not talent alone.*

The ordering matters. Vision sets direction, Focus protects it from noise, Clarity translates it into confident decisions, Shared Ownership lets it scale beyond a single person, and Courage makes it safe to question the plan when reality changes. Skip or shortcut any one and the later ones can't stand on their own.

## Current thinking

This topic is seeded largely from Watson's *Product Driven* preview. The preview popularizes ideas that already exist in the Cagan / Torres / Basecamp tradition, but Watson's AI-era framing (*AI exposes latent disconnection rather than creating it*) is the fresh contribution worth carrying forward.

The topic runs broader than "what this book says." The cross-cutting questions sit at the intersection of product thinking and AI:

- How does product thinking change when execution is nearly free?
- If "knowing what to build" is now the bottleneck, what does that imply for tool design, team design, and how AI agents should behave inside a product-thinking culture?
- Is the five-foundation model specific to human teams, or does it generalize to human-agent teams? (Courage, for example, reads weirdly well as advice for how agents should be encouraged to challenge bad instructions.)

## Open questions

- **Where do Cagan and Torres line up with Watson?** Watson's model runs downstream of *Inspired*, *Empowered*, and *Continuous Discovery Habits*. Anchoring this topic in the primary literature, Cagan's "product team vs. feature team" distinction and Torres's "opportunity solution tree," would strengthen it.
- **Google's Project Aristotle primary source.** The Watson book references it but doesn't cite. Worth finding the re:Work article and pulling the five factors with their actual definitions, so the mapping to the five foundations rests on the source rather than rhetoric.
- **What does "product thinking" look like for human-agent teams?** If the team includes agents that can execute at zero marginal cost, does "shared ownership" still mean what it meant? Does "courage" still apply to the non-human participants (should agents be designed to push back)? Most product-thinking writing hasn't caught up to this edge yet.
- **Counterexamples to the model.** Are there product-successful teams that *don't* operate this way, such as dictatorial visionary-led teams that ship great products through a single mind? Apple under Jobs is the obvious case. If the model is so clean, why do those teams exist and succeed?
- **The Stack Overflow developer satisfaction number.** Watson cites 32% very satisfied (2023). What's the 2024/2025 figure, and does AI adoption correlate with satisfaction increases or decreases? Worth grounding the "engineers feel lost" claim in fresher data.
- **Empty-chair practices at Amazon.** Watson cites this in passing. Is it still a real practice, or a myth that's been repeated long enough to feel true? Worth verifying.

## Sources

- [Product Driven (Free Preview)](https://productdriven.com/book) — Matt Watson, Full Scale. The disconnection diagnosis, the "why" question as litmus test, the roadmap momentum trap, distributed product thinking, two-way empathy, and the five foundations.
- [Nate B Jones — AI News & Strategy Daily](https://www.youtube.com/@NateBJones) — YouTube. The capability-to-economics phase shift, the four-or-five future roles, and working intelligence as a fifth category of professional capital.
- [Agent Analytics: Why Product Metrics Need to Change for AI Agents](https://www.youtube.com/watch?v=n0nC1kmztSk) — YouTube. The Salesforce AWU shift from seat and session metrics to work-unit primitives, the completion-versus-acceptance gap, and agent corrections as labeled product data.
- [When to Automate, Build, Buy, Hire, or Wait on AI](https://www.youtube.com/watch?v=LIkYVsxMpS8) — Nate Jones, YouTube. Workflow-first investment thinking, the five investment levers, the "do not automate what you cannot describe" maxim, and the "what good looks like" problem in build decisions.
