---
name: claim-verifier
description: >
  Adversarial accuracy gate for a topic before it publishes. Reads a topic doc in
  src/content/docs/topics/ together with the captures behind its Sources, then checks every factual
  claim — stats, dates, quotes, attributions, causal/empirical claims — against the source material.
  Catches fabricated, drifted, misattributed, or mis-numbered claims, invented Source URLs, and leaked
  private content. Runs after topic-validator and before the build in content-synthesis, and on demand:
  "verify [topic]", "fact-check [topic]", "run a verification pass", "is this topic accurate".
---

# Claim Verifier (Working Intelligence)

The last gate before a topic goes public. Assume each claim is wrong until the sources prove it right.
The goal is to publish nothing the sources don't actually support.

## When it runs

- **Inline (content-synthesis, after distillation + topic-validator, before the build check).** Verify
  the topic(s) just written. Block publish on high-severity findings.
- **Standalone.** "Verify ai-labor-market-2026" or "fact-check all topics."

## Inputs

1. The topic doc: `src/content/docs/topics/{slug}.md`.
2. Its evidence, in priority order:
   - **The archived raw source is ground truth** — `intelligence/captures/{slug}.source.md` (or
     `{slug}.sources/`), the verbatim text behind each capture. Check claims against this first.
   - The capture summary (`intelligence/captures/{slug}.md`) is a convenience index, not proof. A claim
     that matches the summary but not the raw source is still a finding (the summary drifted).
   - If a capture has `source_archive: none`, there is no ground truth locally — fall back to web
     corroboration and treat the claim as UNVERIFIABLE until corroborated.
   - For topics migrated from the vault, archives/captures may live in `~/vault/Intelligence/captures/`;
     ask the user or read there if needed.
3. For surprising or load-bearing claims with no local archive, the web (search + fetch) for
   corroboration.

## Process

### 1. Load everything
Read the full topic doc. For each cited capture, read its **archived raw source** in full (the
`.source.md`), not just the capture summary. The raw source is what you verify against; the summary only
tells you which archive to open. Build a claim ledger.

### 2. Extract every factual claim
Pull out anything checkable, with its line number:
- **Numbers/stats** — percentages, counts, dollar figures, dates, ranges.
- **Quotes** — anything in quotation marks or a blockquote.
- **Attributions** — "X said", "Y's framework", "according to Z", company actions.
- **Empirical/causal claims** — "junior postings fell 67%", "AI usage correlates with...".
Skip pure opinion and clearly-labeled speculation (but check it IS labeled — see step 5).

### 3. Judge each claim against the sources (be adversarial)
For each claim, find the supporting passage in a capture and assign a verdict:

| Verdict | Meaning | Severity |
|---|---|---|
| **SUPPORTED** | A source states this; the topic represents it accurately | — |
| **DRIFT** | A source is related but the topic overstates, generalizes, or distorts it | Medium |
| **NUMBER-MISMATCH** | The stat/date/figure differs from the source | High |
| **QUOTE-MISMATCH** | Quoted text differs from the source, or isn't a real quote | High |
| **MISATTRIBUTED** | Wrong person/company, or a non-public source named (violates the attribution rule) | High |
| **UNSUPPORTED** | No source backs it, and it isn't labeled speculation | High |
| **UNVERIFIABLE** | Can't confirm from captures; needs web corroboration or a confidence tag | Medium |

Default to the worse verdict when uncertain. "Sounds plausible" is not SUPPORTED.

### 4. Corroborate the load-bearing unknowns
For UNVERIFIABLE claims that are surprising or that a reader would lean on, web-search 1–2 credible
sources. If corroborated, keep it and tag confidence; if not, downgrade to UNSUPPORTED. Respect the
source hierarchy (peer-reviewed/official > established practitioners/reputable outlets > general blogs >
anonymous/promotional).

### 5. Sources, attribution, and leak checks
- **Sources integrity:** every URL in `## Sources` must come from a capture's `source:` field. Flag any
  invented or guessed URL (High). Confirm linked titles match the capture.
- **Attribution rule:** public-source names may stay; anything sourced non-publicly (private
  conversation, boardroom/insider) must be anonymized to a role. Flag violations (MISATTRIBUTED).
- **Speculation labeling:** forward-looking or single-source claims should read as such or carry a
  confidence tag (Verified / Plausible / Unverified). Flag confident-sounding speculation.
- **Private-content leak:** no personal names tied to private context, project names, local paths, or
  vault references. Any hit is High severity and blocks publish.

### 6. Report

```
## Verification Report — {topic}.md
Claims checked: N   |   SUPPORTED: a   DRIFT: b   MISMATCH: c   UNSUPPORTED: d   UNVERIFIABLE: e

### 🔴 Blocking (fix before publish)
- [line ~X] "{claim}" — NUMBER-MISMATCH. Topic says 67%, capture says 66% ({capture}, line Y).
  → Fix: correct to 66%, or cite a source that says 67%.

### 🟡 Review (fix or qualify)
- [line ~X] "{claim}" — DRIFT. Source supports {narrower point}; topic generalizes to {broader claim}.
  → Fix: narrow the claim, or add a confidence tag.

### 🟢 Verified
Spot-summary: the {N} numeric claims and {M} quotes trace cleanly to sources.
```

If everything passes: "Verification passed — all N checked claims trace to sources." Stop.

### 7. Gate
- **Block publish** while any 🔴 finding stands (UNSUPPORTED, NUMBER/QUOTE-MISMATCH, MISATTRIBUTED,
  private leak, invented URL).
- 🟡 findings: fix, qualify with a confidence tag, or get explicit user sign-off to ship as-is.
- After fixes, **re-verify the changed claims**, then proceed to the build check.

## Thoroughness scaling
- Routine single-capture distillation: one verification pass by the running agent is enough.
- Large or high-stakes topics (many sources, surprising claims, anything the user calls out): spawn
  parallel verifier subagents, each owning a slice of the claim ledger and prompted to refute, then
  consolidate. A claim survives only if no verifier can refute it from the sources.

## Keep edits faithful
When fixing a finding, change only what the source requires. Preserve voice and the human-prose style;
never alter verbatim quotes or table values except to correct a confirmed mismatch against the source.
