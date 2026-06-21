---
title: AI-Assisted UI Design Research
description: A repeatable workflow for running AI-assisted UI research that ends in a locked, defensible design decision instead of a pile of mood boards.
lastUpdated: 2026-04-18
---

A significant UI or aesthetic decision cascades across dozens of surfaces, and getting it wrong is expensive to undo. This is a repeatable workflow for using an AI assistant to run that research and land on a locked, defensible decision. Treat it as a living document: append new pitfalls and refinements as they surface across projects.

## When this approach fits

Use it when you face a UI or aesthetic decision that will cascade across many surfaces: a design-system pick, a rebrand, a new product's first look. It is overkill for a single component. It is underpowered for a greenfield brand with no existing constraints.

## The workflow (5 phases)

### 1. Context grounding

Capture four things before any research starts:

- **Who uses this?** Personas with usage frequency per screen.
- **What exists?** Current stack, components, routes, constraints.
- **What's locked?** Non-negotiables: license, tech stack, accessibility.
- **What's the decision?** Phrase it as a question: *"What anchor color fits a compliance tool?"*

Skip this and the research wanders.

### 2. Layered research docs

Write five short docs, each readable in one sitting:

| Doc | Role | Source |
|---|---|---|
| Inspiration analysis | What existing refs teach + what they don't cover | Refs you already have |
| Component inventory | Every surface the decision will touch | Codebase + roadmap |
| UX flows | Which surfaces matter most, for whom | Domain knowledge |
| Competitive landscape | What the rest of the market looks like | Web research (dispatch an agent) |
| Design system options | 2–3 concrete directions specified to the token level | Synthesis of the above four |

Add a **SUMMARY** on top as the one file someone reads later.

Keep them separate because each doc answers a different question, and the options doc depends on all four inputs. Collapse them into one and the synthesis turns muddy.

### 3. Exploration (visual)

Rank your options by fidelity to the aesthetic decision:

- **AI image generation** (Midjourney, DALL·E)
  - Best for: divergent exploration, early vibes, marketing surfaces.
  - Costs: ~$0.20–0.40 per run plus setup friction.
  - Weakness: it interprets briefs loosely and drops fine details (tabular numerals, letter-spacing, exact hexes).
- **Coded HTML mockup** (Tailwind + real tokens)
  - Best for: token-level precision, anything where specific values matter.
  - Costs: ~10–30 min to author, zero API.
  - Weakness: you need to know your tokens first. It fails when you don't know what you want.
- **Figma mockup**
  - Best for: handoff to designers, production-ready artifacts.
  - Costs: a Figma subscription plus time.
  - Weakness: read-only through automation, so you can't generate new designs from prose.

Use AI generation for divergence, coded mockups for convergence. Reach for Figma only when humans need to iterate on visuals directly.

### 4. Decision

Lock decisions in tiers rather than all at once:

1. **Direction first** (e.g., "light-mode calm trust" vs. "dark developer-native").
2. **Anchor elements next** (primary hue, display font).
3. **Scope modifiers** (dark mode shipping now? marketing in scope?).
4. **Taste details last** (exact hex, illustration policy).

Each tier depends on the one above it. Decide hex codes before direction and you stall.

### 5. Decision record

Record the same truth in three places:

- **Machine-readable:** a JSON file with the chosen option, tokens, and rationale, for tooling and an audit trail.
- **Human-readable:** the SUMMARY doc with a "Decision" callout at the top.
- **Session-persistent:** agent memory or similar, so future sessions know.

## Best practices

- **Dispatch competitive research in parallel.** Don't run it yourself while you still have context loaded for the other docs. An agent with web tools surveys 20+ products in five minutes while you work the inventory.
- **Find the open lane.** Competitive research should answer one question: *"what direction is visually unoccupied in this category?"* That finding is often the most load-bearing insight you get.
- **Flag when refs don't fit.** If someone hands you Sentry and Cal.com as inspiration for a dashboard, say those are marketing-site references, not product refs. Don't silently port the wrong patterns.
- **Pair each option with a stated risk.** Options without risks read as hype. *"Option B, but the risk is it looks like every other Stripe-clone"* is honest and useful.
- **Separate semantic color from brand color.** In any tool with status (pass/fail, severity, readiness), the semantic palette is untouchable. Brand accent lives in chrome only. Confuse the two and you get rainbows.
- **Density kills marketing-site refs.** Any reference with 80–96px section spacing sells breathing room as premium. Dashboards need their own spacing scale tuned for tables and drawers.
- **Honor the stakeholder lean.** If they say "I lean toward X," don't present three options that ignore X. Tilt the options so X is one of them, and frame the others as "more restraint than X" or "more personality than X."
- **Gate expensive moves behind confirmation.** Confirm the concept list before launching four parallel agents that each cost tokens. Verify the brief before spending API credits on image generation. One extra prompt costs less than wasted parallel work.
- **Kill failures fast.** When the first agent fails with a structural error (missing API key, bad config), stop the others. Don't let the rest waste tokens hitting the same wall.

## Pitfalls

1. **Designing from prose alone.** Aesthetics don't live in prose. Make or show visuals before locking a direction.
2. **Over-interrogating the stakeholder.** Two rounds of clarifying questions, no more. Beyond that you're stalling.
3. **Letting research become the product.** Research exists to inform a decision. A 50-page research doc means you're avoiding the decision.
4. **Picking hex codes before direction.** You'll change them when direction shifts.
5. **Not writing down why.** Six months out, "we chose violet" is useless. *"We chose violet because the compliance category was all blue and we had an open lane"* survives.
6. **Skipping the competitive scan.** You'll rediscover that your brilliant idea is what Drata already looks like.
7. **Treating AI mockups as source of truth.** They're impressionistic. Ask for "Inter Display 28px with tabular numerals" and the model draws a placeholder font at some size with no number alignment. Commit off a coded mockup, never an AI one.

## Decision record template

```json
{
  "decision": "<what was picked>",
  "option_chosen": "<A/B/C from options doc>",
  "date": "<ISO timestamp>",
  "rationale": "<why this over others>",
  "open_questions": ["<not yet resolved>"],
  "artifacts": {
    "research": "<path>",
    "mockup": "<path>",
    "options_doc": "<path>"
  },
  "method": "<AI mockup / coded mockup / team vote / gut>"
}
```

## The "one file to find it later" rule

Every research effort should produce exactly one SUMMARY doc that:

- Lists what else is in the folder.
- States the decision at the top.
- Flags what's still open.
- Links to artifacts.
- Fits on one screen when collapsed.

If future-you can't reconstruct the decision from the SUMMARY alone, the research isn't done.

## Sources

This playbook comes from a single internal design-research session (April 2026), distilled into the workflow above. No public capture backs it yet.
</content>
</invoke>
