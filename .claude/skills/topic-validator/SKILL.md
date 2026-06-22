---
name: topic-validator
description: >
  Scan a published topic doc in src/content/docs/topics/ for concept-level redundancy — sections that
  make the same point under different headings, or insights that got appended rather than woven in.
  Runs after every topic distillation (Step 4 in content-synthesis) and on demand. Use when asked to
  "validate this topic", "check for redundancy in [topic]", "audit the topic doc", or automatically
  after distilling a capture into a topic.
---

# Topic Validator (working_intel)

Detect concept-level drift in published topic docs before it compounds.

## The problem

Topic docs synthesize across sources — they should not accumulate them. As captures distill in over
time, the same concept can quietly appear under multiple headings: once from an early capture, again
from a later one with slightly different framing. Each addition looks correct alone. The doc grows
incoherent by accretion. The validator reads the whole doc and finds `###` sections covering the same
territory a reader would otherwise have to visit twice.

## Two modes

- **Inline (Step 4 in content-synthesis):** runs automatically after a topic is updated during
  distillation. Validates only the doc(s) just modified, before the build check.
- **Standalone:** triggered manually — "validate agent-design" or "validate all topics".

## Process

### 1. Read the topic doc in full
Load the complete file (`src/content/docs/topics/{slug}.md`). Concept-level redundancy often spans
sections far apart in the doc.

### 2. Extract all `###` concept sections
Build a map: section heading → key claims (one line per claim). You're building a comparison surface.

### 3. Compare sections for concept-level overlap
For each pair, ask: **if a reader needed concept X, would they get it from section A, section B, or
both?** "Both" is a redundancy candidate. Distinguish:
- **True redundancy** — same principle stated twice; one can be folded into the other.
- **Complementary coverage** — one motivates (the why), one implements (the how). Lower confidence.
- **Same concept, different domain** — shared upstream principle, different application. Not redundant;
  worth a cross-reference note.

### 4. Report findings
Only report genuine candidates.

```
## Concept Redundancy Report — {topic-name}.md

### High confidence (consolidate)
- **"{Section A}"** and **"{Section B}"** — both establish [shared claim].
  A covers [angle]; B covers [angle]. The [specific claim] appears in both, ~lines X and Y.
  → Recommend: fold [B's unique content] into A, remove B.

### Medium confidence (review)
- **"{Section A}"** and **"{Section B}"** — share [concept] but [distinction].
  → Recommend: cross-reference, or merge the overlapping passage.

### No action needed
Everything else is distinct. [Note if the doc nears the ~200-line threshold.]
```

If nothing is found: "No concept-level redundancy detected." Stop.

### 5. Fix if approved
1. Read both sections in full.
2. Merge: keep the stronger framing, fold in unique claims from the weaker section, remove the duplicate.
3. Update any cross-links (including Starlight `[label](/dev-blog/topics/<slug>/)` links) that referenced
   the removed heading.
4. Keep the publish house style while editing: human-prose, public-attribution, verbatim quotes/tables.
5. Re-run the validator to confirm no new drift, then re-run `npm run build`.

## Decision rubric

| Finding | Action |
|---|---|
| Same claim, same domain, nothing unique in either | Consolidate — fold unique bits, remove one |
| Same principle, one motivates / one implements | Keep both, add cross-reference sentence |
| Same concept, different domain or application | Keep both, note shared upstream principle |
| Similar names but genuinely different territory | No action, note the distinction |

## Thresholds
- Flag any doc over **200 lines** as nearing the split-into-subtopics threshold, even with no redundancy.
- Only report pairs where the overlap is **specific and quotable**. If you can't name the exact shared
  claim, it's not a finding.

## What not to flag
- Sources duplication (expected).
- Open Questions repeated across topics (questions are not claims).
- Related concepts that share vocabulary but make different points.
- A concept stated briefly in one section and elaborated in another (cross-referencing, not redundancy).
