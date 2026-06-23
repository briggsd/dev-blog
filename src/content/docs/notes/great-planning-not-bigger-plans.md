---
title: Great Planning, Not Bigger Plans
date: 2026-06-22
authors: wi
excerpt: "IndyDevDan rebuilt his /plan skill around one bet: spend more tokens up front and the model rewards you. The planning-leverage half is right and the field agrees. The more-tokens half collides with what Anthropic and others have learned about finite attention."
tags: [planning, skills, context-engineering, spec-driven-development, agentic-engineering]
---

IndyDevDan spends a half-hour dev-vlog rebuilding his `/plan` skill from an empty directory, and the whole thing rests on one line he repeats until he warns you you'll be sick of it: great planning is great engineering. His target is the habit of handing a bare `/plan` to Claude Code or Codex and trusting the agent to guess what you wanted. He calls that the start of skill atrophy, "the mass deprecation of raw engineering talent," and his fix is to stop outsourcing the thinking. He sits down and types a `raw.md` by hand before any agent touches the work, then encodes his judgment into a fixed plan template the agent reproduces every time. He calls this templating your engineering, and it is the durable idea in the video.

The leverage claim holds up well outside his channel. The spec-driven development movement spent the last year arriving at the same place from the tooling side: write the spec first, iterate on it while it is cheap to change, then let the agent derive the code. Birgitta Böckeler, surveying Kiro, GitHub's Spec Kit, and Tessl on Martin Fowler's site, frames the spec as "a structured, behavior-oriented artifact" and sorts the approaches by how long the spec lives: spec-first specs get discarded after generation, spec-anchored specs are maintained alongside the code, and spec-as-source specs become the file humans edit while the code is generated. IndyDevDan's design lands squarely in the spec-anchored tier. His plans carry append-only metadata headers, back and forward references to other plans, and an amendment log, because he wants the plan to stay a living artifact over the codebase's life rather than a throwaway prompt. The skill keeps it living by routing one prompt to one of five dedicated workflows, so the same document gets created, revised, referenced, and built without ever leaving its format:

| Workflow | When it fires |
|---|---|
| **Create Plan** | plan, spec, or design new work |
| **Update Plan** | revise an existing plan (a surgical edit, logged as an amendment) |
| **Update References** | refresh metadata, or wire back and forward references to other plans |
| **Build Plan** | implement the plan, flipping status markers as it goes |
| **Image Generation** | subworkflow that fills the embedded diagrams |

The other half of his thesis, the part about not outsourcing your thinking, has its own growing literature. Addy Osmani's work on skill atrophy makes the same argument with more caution: cognitive offloading erodes the debugging and architectural muscles you stop using, and "the more people leaned on AI tools, the less critical thinking they engaged." His counsel is to treat AI as a collaborator and keep doing the hard reasoning yourself. That is IndyDevDan's whole posture, expressed as a workflow. On this point the two agree, and the broader field agrees with both.

Where the video gets contestable is the prescription that follows. IndyDevDan reads the rise of stronger models as license to spend without limit. His stated priority order is performance over speed over cost, and he means it literally: HTML-first plans because they burn more tokens, generated images embedded in every phase, maximum thinking effort on work a smaller model could do. His justification is that "HTML gives your agent more tokens" and more tokens buy a slight edge, which he attributes to an Anthropic piece. The Anthropic piece argues close to the opposite. Its core claim is that context is a finite attention budget: "every new token introduced depletes this budget by some amount," and "as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases." The phenomenon has a name, context rot, and the recommended practice is "finding the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome." Böckeler, from the spec side, voices the matching doubt in plain terms: "I'm very skeptical that lots of up-front spec design is a good idea, especially when it's overly verbose."

So the question is whether a bigger plan is a better plan, and the honest answer is that volume and quality are different axes. What makes IndyDevDan's template strong is not its token count. It is the structure: a problem and solution stated in a fixed shape, relevant files split into existing and new, work broken into phases with a per-phase checklist, and validation commands that keep the agent looping until every box is checked. That structure is high-signal by construction. Here is the phase block it stamps onto every plan, with status markers (`[]` idle, `[wip]` in progress, `[x]` complete, `[f]` failed) sitting right in the checklist so the building agent tracks itself against the same document it fills:

```html
<!-- condensed from the planf3 plan template; one block per phase, mirrored every run -->
<div class="phase">
  <h3><code class="status">[]</code> Phase {{PHASE_NUMBER}}: {{PHASE_NAME}}</h3>
  <p>{{PHASE_DESCRIPTION}}</p>

  <h4>{{TASK_NUMBER}}. {{TASK_NAME}}</h4>
  <ul class="checklist">
    <li><code class="status">[]</code> {{SPECIFIC_ACTION}}</li>
  </ul>

  <h4>{{LAST_TASK_NUMBER}}. Testing Strategy</h4>
  <p>{{TESTING_APPROACH: technology used to test/validate, including edge cases}}</p>
  <ul class="checklist">
    <li><code class="status">[]</code> <code>{{VALIDATION_COMMAND}}</code> — {{WHAT_IT_PROVES}}</li>
  </ul>
  <div class="loop">
    🔁 <strong>Do not exit this phase until every box above is checked.</strong>
    If any command fails, fix the cause and re-run — loop until all pass.
  </div>
</div>
```

None of that is the expensive part. The HTML wrapper and the per-phase imagery are the parts most exposed to the context-rot critique, because they spend the attention budget on tokens that may not earn their keep. His own demo hints at the tension: the strongest moment is when the agent fills the freeform notes section with a feature-parity matrix he never asked for, and the weakest is when it inflates a single request into half-built sections he didn't want. The model rewards the structure and punishes the open-ended sprawl.

The cleanest part of his design is the hedge he builds against his own rigidity. A common objection to templating is that a fixed format boxes in a model that might plan better if left free. His answer is a notes section where the agent runs without constraints, alongside the rigid scaffold everywhere else. That is the right shape for the whole problem. The scaffold carries your judgment in dense, reusable form, and the open section lets the model add what your template could not anticipate. Read that way, the disagreement with Anthropic mostly dissolves. Both want high-signal context. They differ on whether HTML and images clear that bar, which is an empirical question you can settle per codebase rather than a principle.

What survives from the video is the strong claim: the plan is the highest-leverage artifact you own, it should be a living thing in the repo, and you should encode your own engineering judgment into it instead of delegating that judgment to the agent. What I would not carry over is the reflex that spending more always wins. Treat tokens the way the rest of the engineering world is learning to: as a budget you spend on signal. Great planning is great engineering. Bigger plans are just bigger.

This note feeds [Skill Design and Management](/working-intel/topics/skill-design-and-management/) and [Context Engineering](/working-intel/topics/context-engineering/).

## Sources

- [PLANS For Fable 5: Rebuilding My /Plan Skill for Mythos Class Models](https://www.youtube.com/watch?v=DzbqeO_diOQ) — IndyDevDan, YouTube. The anchor: rebuilding a planning meta-skill, templating your engineering, plans as living artifacts, and the spend-tokens-for-performance bet.
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic. The finite attention budget, context rot, and the case for the smallest set of high-signal tokens.
- [Understanding Spec-Driven Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) — Birgitta Böckeler, martinfowler.com. The spec-as-artifact taxonomy (spec-first, spec-anchored, spec-as-source) and skepticism of verbose up-front specs.
- [Avoiding Skill Atrophy in the Age of AI](https://addyo.substack.com/p/avoiding-skill-atrophy-in-the-age) — Addy Osmani. Cognitive offloading, the dependency trap, and keeping the hard thinking yours.
- [planf3 — the companion repo](https://github.com/disler/planf3) — IndyDevDan, GitHub (MIT). Source for the workflow table and the phase-block template shown above, plus a real, unedited generated plan.
