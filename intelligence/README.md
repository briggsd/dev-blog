# Intelligence pipeline

The capture-and-synthesis workflow that feeds the published topics. This is the new home for the
intelligence work, decoupled from any personal vault.

## Layout

```
intelligence/
├── captures/   raw intake notes (gitignored — local only, private)
├── _inbox/     drop files here to process (gitignored — local only)
├── tools/
│   └── lift_proxy.py   usage signal for pruning stale published topics
└── README.md
```

Published topics live in `../src/content/docs/topics/` and are built into the site.

## The boundary

`captures/` and `_inbox/` are **gitignored**: raw intake stays on this machine and never gets pushed.
Only distilled topics are committed and published. The capture → topic step is where rough, private
notes become public-ready prose (sanitized, human-prose, real-URL Sources).

To back up captures, copy them somewhere private. They are intentionally kept out of this public repo.

## Workflow

Driven by the `content-synthesis` and `topic-validator` skills in `../.claude/skills/`:

1. Share a link or drop a file in `_inbox/` → a capture lands in `captures/`.
2. Strong captures distill into a published topic (concept-organized, public house style).
3. `topic-validator` checks the topic for redundancy; `npm run build` verifies it.
4. Guided research loop ("run a research cycle on X") turns a topic's open questions into new captures.

## Pruning signal

```bash
python3 intelligence/tools/lift_proxy.py
```

Reports which published topics actually get loaded to inform new work versus only written. Set
`LIFT_SESSIONS=/path/to/sessions` if your harness stores session transcripts somewhere non-default.
