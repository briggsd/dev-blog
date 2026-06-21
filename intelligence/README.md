# Intelligence pipeline

The capture-and-synthesis workflow that feeds the published topics. This is the new home for the
intelligence work, decoupled from any personal vault.

## Layout

```
intelligence/
├── captures/   raw intake (gitignored — local only, private)
│   ├── {slug}.source.md   verbatim archived source (ground truth)
│   └── {slug}.md          the capture (summary derived from the archive)
├── _inbox/     drop files here to process (gitignored — local only)
├── tools/
│   └── lift_proxy.py   usage signal for pruning stale published topics
└── README.md
```

**Archive first, summarize second.** The verbatim source is saved as `{slug}.source.md` at ingestion;
the capture summary and the published topic are derived from it. The verifier checks claims against the
archive, not the summary, so summarization errors can't slip through.

Published topics live in `../src/content/docs/topics/` and are built into the site.

## The boundary

`captures/` and `_inbox/` are **gitignored**: raw intake stays on this machine and never gets pushed.
Only distilled topics are committed and published. The capture → topic step is where rough, private
notes become public-ready prose (sanitized, human-prose, real-URL Sources).

To back up captures, copy them somewhere private. They are intentionally kept out of this public repo.

## Workflow

Driven by the `content-synthesis` and `topic-validator` skills in `../.claude/skills/`:

1. Share a link or drop a file in `_inbox/` → the verbatim source is archived to `{slug}.source.md`,
   then a capture summary (`{slug}.md`) is written from that archive.
2. Strong captures distill into a published topic (concept-organized, public house style).
3. `topic-validator` checks the topic for redundancy.
4. `claim-verifier` adversarially fact-checks every claim against its sources — a blocking publish
   gate that catches fabricated, drifted, misattributed, or mis-numbered claims and private leaks.
5. `npm run build` verifies the topic builds.
6. Guided research loop ("run a research cycle on X") turns a topic's open questions into new captures.

## Pruning signal

```bash
python3 intelligence/tools/lift_proxy.py
```

Reports which published topics actually get loaded to inform new work versus only written. Set
`LIFT_SESSIONS=/path/to/sessions` if your harness stores session transcripts somewhere non-default.
