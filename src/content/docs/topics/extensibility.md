---
title: Extensibility
description: "Open to extension, closed to modification: why the software that survives agentic-speed change is the software you adapt by adding, never by rewriting the core, and how to decide where the seams go."
lastUpdated: 2026-06-21
---

The pace of change in agentic engineering is the whole argument. Models, prompts, tools, and techniques churn at a speed no release cycle keeps up with, so the only software that lasts is software you adapt by adding rather than rewriting. That is an old principle with a new urgency, and it is the design layer beneath two ideas in [Agent Infrastructure](/working-intel/topics/agent-infrastructure/): you can only specialize a harness you can extend, and a profile is only cheap to add if the substrate is open. This topic pulls extensibility out as its own concern, names the prior art it descends from, and lands on a usable rule for where to put the seams.

## Key concepts

### Open to extension, closed to modification

The thesis comes from IndyDevDan's "5 Pillars" talk, where he names extensible software as one of two ideas he says he personally missed and went back to re-emphasize. The reasoning is the rate of change: "the best way [to] adapt to change is to build it into your software." Add capability alongside a stable core; never modify the core to get it.

The failure mode is concrete and specifically bad for agents. Software that "operates in a very specific line of cascading if statements" becomes the thing your own agents have to navigate on every run, so "next year is going to be really really hard for you because your agents will be really slow, they'll be making a lot of mistakes, and you have to teach them in your software how to navigate all that." Brittle, branch-heavy code does not just cost you maintenance. It taxes every agent that touches it. "Plugability is the key. Extensibility is the key. Composability is the key."

The principle applies to two arenas, not one:

- **Engineering work.** Your agent harness is the prime example: swappable and dynamic, with change-on-the-fly tools, prompts, agents, system prompts, and models.
- **Product work.** Production software (agentic or traditional) that has to adapt as the environment shifts. The payoff is symmetric: a product built open and closed lets its own agents add capability without a rewrite, exactly as an extensible harness does for you.

### The plugin-architecture lineage

The practitioner thesis is a rediscovery of a decades-old, well-named body of principle. Naming the lineage turns "be extensible" from a slogan into a vocabulary for *where* and *how*:

- **Microkernel / plugin architecture** (Mark Richards, *Software Architecture Patterns*). A minimal, stable core provides essential services and defines extension points, the contracts that plugins implement; functionality arrives as independently developed plugins. This is the architectural home of the whole idea.
- **The Open/Closed Principle** (Bertrand Meyer, *Object-Oriented Software Construction*, 1988; reframed by Robert C. Martin). "Open for extension, closed for modification." Meyer's mechanism was inheritance; Martin's polymorphic reading is the modern one: depend on a stable abstraction, vary behavior behind it.
- **Information hiding and design for change** (David Parnas, 1972). Decompose around what is likely to change, and hide each such decision behind an interface. This underwrites OCP: the reason to be open and closed at a given point is that you anticipate change there.
- **Encapsulate what varies** (GoF, *Design Patterns*, 1994). The operational restatement: find what changes, wrap it behind a stable interface. It tells you *where* the seam goes, on the axis of variation.
- **Mechanism, not policy** (the Unix tradition; Raymond, *The Art of Unix Programming*). The core provides mechanism, the event bus, the registry, the contract; extensions supply policy, what to actually do. Keeping policy out of the core is what keeps the core small and stable.
- **Declarative versus programmatic contribution** (VS Code, Eclipse). VS Code makes the two styles explicit: "Contribution Points are a set of JSON declarations that you make in the `contributes` field of the `package.json` Extension Manifest" (declarative, statically discoverable, lazily activated), versus registering at runtime in code (programmatic, dynamic). A mature system often offers both.
- **Stable abstractions** (Robert C. Martin). Depend in the direction of stability. The thing many plugins depend on, the contract, must be the most stable part of the system. That is what lets a platform promise "the contract will not change."

### Pi as a worked reference

Pi, Mario Zechner's open-source coding-agent harness, is open and closed expressed as a runtime, and a clean public example. It states the stance plainly: a minimal core (the loop, tools, context, sessions) that you extend through TypeScript extensions, skills, prompt templates, and themes, leaving primitives like MCP, sub-agents, and permissions for the user or community to supply. The mechanics map straight onto the lineage:

| Open/closed mechanic | How Pi does it |
|---|---|
| Minimal core, layered extensions | Extensions auto-discovered from conventional directories (`extensions/`, `skills/`, `prompts/`, `themes/`); you never edit Pi's source |
| Register, don't patch | `registerTool` / `registerCommand` / `registerProvider` and friends; new capability is additive surface, even mid-session |
| Mechanism via hooks | Lifecycle events (session start, context rewrite, tool call, provider request) are defined seams you reshape behavior through |
| Composable, shareable units | Skills, prompts, themes, and extensions bundle into Pi packages shipped over npm or git |
| Swappable on the fly | Hot reload, dynamic registration, runtime model and provider routing |

Every customization is something added alongside the core, gated through an event or a registration API, never a modification of Pi itself. Skills are one of those registered capability types, which connects this to [Skill Design and Management](/working-intel/topics/skill-design-and-management/): a skill's description is the discovery mechanism, the skill-layer analogue of a renderer or tool registry.

### A seam-decision heuristic

The principle says be extensible; it does not say where. That is the question that actually bites, because a generic plugin system built too early is its own kind of brittle. Six rules answer it:

1. **Put the seam on the axis of variation, not everywhere.** Find the one thing that genuinely varies first and expose that. Variation you cannot yet name does not get a seam (Parnas, GoF).
2. **Ship the contract before the discovery machinery.** The high-value, hard-to-change part is the contract (the payload shape, the interface). Build and freeze that now; defer the manifest and install machinery until a real third-party consumer exists, but shape the contract so that machinery is an addition, not a rewrite.
3. **Every seam needs a graceful default.** An extension point that can crash the core on an unregistered or unknown case is not done. The unknown case must degrade, not fail.
4. **Bound the blast radius of an extension.** Give each extension the smallest surface that does its job, and route unmet needs to the layer that owns the data. A bounded extension is a safe extension, the open/closed analogue of execution isolation.
5. **Separate extension responsibilities by layer.** When you build atop an already-extensible system, inherit its extension surface rather than re-implementing it, and add a seam only for the half it cannot do. Compose extension systems; do not nest or duplicate them.
6. **Prefer add-only registration over conditional core logic.** The anti-pattern is the cascading `if` in the core. Each new case as a registered unit keeps the core's branching flat, which is also what keeps your agents able to navigate the code next year.

## Current thinking

Extensibility reads as architecture advice, but in an agentic shop it is closer to a survival trait. The compounding cost is the one rule 6 names: brittle, branch-heavy code is not just hard for humans to change, it is expensive for every agent that has to reason through it. The pace argument and the agent-navigation argument point the same way, which is why the principle deserves to sit above harness sovereignty and agents-as-profiles rather than inside them.

The most useful move when someone says "make it extensible" is to refuse the generic answer and ask the seam-decision questions instead. What actually varies here? Is the contract stable enough to freeze? What happens on the unknown case? Most "we need a plugin system" instincts resolve into one or two real seams plus a lot of deferred machinery.

### Applied in

- [Build a CI-Native Review Factory](/working-intel/build/ci-native-review-factory/) — a first-party open/closed system: adopting repos never fork the core, behavior is configured per-repo, reviewers are factory-owned units added through a `defineReviewer` registry, VCS support is an adapter interface, and runtimes and providers are registered rather than patched.

## Open questions

- Where is the line between declarative and programmatic contribution for an agent system? Manifests buy discoverability and lazy activation at scale; runtime registration buys dynamism. When is each worth it for a single-operator tool versus a platform?
- What is the minimal discovery mechanism that does not reshape the core: a convention directory scanned at boot, a manifest field, or a runtime register call from an injected module? The contract can be frozen while the loading stays open.
- Does agent-as-extension-author change seam design? If the thing writing extensions is an LLM, the seams may want to be optimized for a model to discover and use rather than for a human developer, which is a different design target than any of the prior art assumed.

## Sources

- [The 5 Pillars of Agentic Engineering](https://www.youtube.com/watch?v=2KcITKKJikA) — IndyDevDan, YouTube. The origin thesis: Pillar 3, extensible software as a survival property, the cascading-if failure mode, add-don't-modify, and the engineering-versus-product arenas.
- [Pi](https://pi.dev/) — Mario Zechner. The public worked reference: a minimal-core harness extended through auto-discovered TypeScript extensions, register-don't-patch APIs, lifecycle hooks, and Pi packages.
- [VS Code Contribution Points](https://code.visualstudio.com/api/references/contribution-points) — Microsoft. The declarative contribution style (JSON in `package.json` `contributes`), contrasted with programmatic runtime registration.
- *Software Architecture Patterns* (Mark Richards, O'Reilly) — the microkernel / plugin-architecture pattern: a stable core that defines extension points implemented by plugins.
- *Object-Oriented Software Construction* (Bertrand Meyer, 1988) and Robert C. Martin's reframing — the Open/Closed Principle and stable abstractions.
- "On the Criteria To Be Used in Decomposing Systems into Modules" (David Parnas, 1972) and *Design Patterns* (GoF, 1994) — information hiding and encapsulate-what-varies, the basis for putting seams on the axis of variation.

## Changelog

- **2026-06-21** — Topic created. Promoted the "extensibility as a survival property" material out of Agent Infrastructure into its own topic, grounded in the primary sources (the 5 Pillars talk, Pi's public docs, VS Code contribution points, and the canonical plugin-architecture literature) rather than the second-hand synthesis. Added the plugin-architecture lineage, the seam-decision heuristic, and an "Applied in" link to the CI-native review factory build.
