# Intelligence pipeline

The capture-and-synthesis workflow behind the published site. This is the home for the intelligence
work, decoupled from any personal vault.

## Two published artifacts, one private

- **Notes** (`../src/content/docs/notes/`) — the *stream*: dated, single-source posts. "Here's what this
  source said and why it matters." Published.
- **Topics** (`../src/content/docs/topics/`) — the *garden*: evergreen, multi-source pages that keep
  evolving as new notes add to or update them. Published.
- **Source archives** (`archives/`) — the verbatim extracted source, the ground truth for verification.
  Private, gitignored, never published.

```
intelligence/
├── archives/   {slug}.source.md — verbatim source (gitignored, private ground truth)
├── _inbox/     drop files here to process (gitignored — local only)
├── tools/
│   └── lift_proxy.py   usage signal for pruning stale topics
└── README.md
```

A note is single-source and dated; a topic is multi-source and evergreen. They are different artifacts,
not duplicates: the note is one source's take, the topic weaves many notes together over time. Topics
link to the notes that fed them.

## The boundary

Only `archives/` and `_inbox/` are gitignored — raw source and intake stay on this machine. Everything in
`../src/content/docs/` is public and goes through the publish gate before shipping.

## Workflow

Driven by the `content-synthesis`, `topic-validator`, and `claim-verifier` skills in `../.claude/skills/`:

1. Share a link or drop a file in `_inbox/` → the verbatim source is archived to `archives/{slug}.source.md`.
2. A dated **Note** is written: anchored to that source, enriched with 2–4 outside perspectives gathered
   by web search (each archived), synthesized into its own argument. Public house style throughout.
3. The material is folded into the best-fit evergreen **Topic** (concept-organized), or a new topic is
   created when nothing fits. The topic links back to the note and out to the original sources.
4. `topic-validator` checks topics for redundancy.
5. `claim-verifier` adversarially fact-checks every claim against the **archived source** — a blocking
   publish gate that catches fabricated, drifted, misattributed, or mis-numbered claims and private leaks.
6. `npm run build` verifies everything builds.
7. Guided research loop ("run a research cycle on X") turns a topic's open questions into new notes.

## Pruning signal

```bash
python3 intelligence/tools/lift_proxy.py
```

Reports which published topics actually get loaded to inform new work versus only written. Set
`LIFT_SESSIONS=/path/to/sessions` if your harness stores session transcripts somewhere non-default.
