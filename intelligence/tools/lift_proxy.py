#!/usr/bin/env python3
"""
lift_proxy.py — a usage-based pruning signal for published topic docs.

WHAT THIS IS
  A cheap stand-in ("proxy") for the causal "lift" of a knowledge artifact.
  Lovable measures whether injected knowledge helps via a randomized holdout.
  We can't run a holdout on our own topic docs, so we mine an OBSERVABLE signal
  that correlates with usefulness: how often each doc is actually loaded into a
  session to inform work.

THE KEY DISTINCTION
  - "load"      = any Read of the file.
  - "reference load" = the file was Read in a session where it was NOT edited.
    This is the high-signal event: the doc was pulled in to inform OTHER work,
    not just opened to be rewritten. Reference loads are the real lift proxy.

BIAS GUARDS (the OPE "coverage/overlap" caveat, made operational)
  A doc that never had a fair chance to fire carries no usable signal. So:
  - Docs younger than MIN_AGE_DAYS are reported but never flagged for pruning.
  - "Never loaded" != "useless" — it may just mean no relevant session occurred.
    These are surfaced as RESURFACE candidates (maybe the agent doesn't know to
    retrieve them), distinct from PRUNE candidates.

USAGE
  python3 intelligence/tools/lift_proxy.py            # full report
  python3 intelligence/tools/lift_proxy.py --json     # machine-readable

  Override the session-transcript location if your harness stores them
  elsewhere:  LIFT_SESSIONS=/path/to/sessions python3 .../lift_proxy.py
"""
import json, glob, os, sys, re, datetime, collections

# Where the harness writes per-session JSONL transcripts. Override with
# LIFT_SESSIONS if your harness stores them somewhere else.
SESSIONS = os.path.expanduser(os.environ.get("LIFT_SESSIONS", "~/.pi/agent/sessions"))
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TOPICS_DIR = os.path.join(REPO, "src/content/docs/topics")
TOPICS_GLOB = os.path.join(TOPICS_DIR, "*.md")
PATH_MARKER = "/src/content/docs/topics/"
TODAY = datetime.date.today()

MIN_AGE_DAYS = 21      # below this, a doc hasn't had fair exposure — don't flag
STALE_DAYS = 30        # no reference load in this long => review candidate
READ_TOOLS = {"Read", "read"}
EDIT_TOOLS = {"Edit", "edit", "Write", "write"}


def mine_sessions():
    """Return per-path: {read_sessions, edit_sessions, last_read} restricted to topic docs."""
    read_s = collections.defaultdict(set)
    edit_s = collections.defaultdict(set)
    last_read = collections.defaultdict(str)
    if not os.path.isdir(SESSIONS):
        return read_s, edit_s, last_read
    for f in glob.glob(os.path.join(SESSIONS, "**/*.jsonl"), recursive=True):
        sid = os.path.basename(f)
        for line in open(f, errors="ignore"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("type") != "message":
                continue
            ts = d.get("timestamp", "")
            for c in (d.get("message", {}).get("content") or []):
                if not isinstance(c, dict) or c.get("type") != "toolCall":
                    continue
                a = c.get("arguments") or {}
                p = a.get("path") or a.get("file_path") or ""
                if PATH_MARKER not in p:
                    continue
                p = os.path.abspath(os.path.expanduser(p))
                name = c.get("name")
                if name in READ_TOOLS:
                    read_s[p].add(sid)
                    if ts > last_read[p]:
                        last_read[p] = ts
                elif name in EDIT_TOOLS:
                    edit_s[p].add(sid)
    return read_s, edit_s, last_read


def created_date(path):
    """Prefer an explicit `created:`; fall back to `lastUpdated:` for Starlight docs."""
    try:
        head = open(path, errors="ignore").read(800)
        for field in ("created", "lastUpdated"):
            m = re.search(rf"{field}:\s*(\d{{4}}-\d{{2}}-\d{{2}})", head)
            if m:
                return datetime.date.fromisoformat(m.group(1))
    except Exception:
        pass
    return None


def days_since(iso_or_date):
    if not iso_or_date:
        return None
    if isinstance(iso_or_date, str):
        try:
            d = datetime.date.fromisoformat(iso_or_date[:10])
        except Exception:
            return None
    else:
        d = iso_or_date
    return (TODAY - d).days


def build():
    read_s, edit_s, last_read = mine_sessions()
    rows = []
    for path in sorted(glob.glob(TOPICS_GLOB)):
        ap = os.path.abspath(path)
        loads = len(read_s.get(ap, set()))
        edits = len(edit_s.get(ap, set()))
        ref = len(read_s.get(ap, set()) - edit_s.get(ap, set()))
        last = last_read.get(ap, "")
        ref_stale = days_since(last) if ref else None
        age = days_since(created_date(ap))
        young = age is not None and age < MIN_AGE_DAYS
        # classification
        if young:
            cls = "TOO_NEW"            # not enough exposure to judge
        elif loads == 0:
            cls = "RESURFACE?"         # never retrieved — discovery gap, not proven dead
        elif ref == 0:
            cls = "WRITE_ONLY"         # only ever read while being edited — terminal doc
        elif ref_stale is not None and ref_stale > STALE_DAYS:
            cls = "REVIEW"             # was useful, but gone cold
        else:
            cls = "ACTIVE"
        rows.append(dict(doc=os.path.basename(path), loads=loads, ref=ref,
                         edits=edits, last_read=last[:10], age=age, cls=cls))
    return rows


def main():
    rows = build()
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=2))
        return
    order = {"WRITE_ONLY": 0, "RESURFACE?": 1, "REVIEW": 2, "ACTIVE": 3, "TOO_NEW": 4}
    rows.sort(key=lambda r: (order.get(r["cls"], 9), -r["ref"], -r["loads"]))
    print(f"Lift-proxy report  ({TODAY})   loads=reads | ref=reference loads (read≠edit session)\n")
    if not os.path.isdir(SESSIONS):
        print(f"  (no session transcripts found at {SESSIONS} — set LIFT_SESSIONS to enable usage mining)\n")
    print(f"{'class':<11}{'loads':>6}{'ref':>5}{'edits':>6}{'lastRead':>12}{'age':>6}  doc")
    print("-" * 78)
    for r in rows:
        age = f"{r['age']}d" if r["age"] is not None else "?"
        print(f"{r['cls']:<11}{r['loads']:>6}{r['ref']:>5}{r['edits']:>6}"
              f"{(r['last_read'] or '—'):>12}{age:>6}  {r['doc']}")
    print("\nLegend:")
    print("  WRITE_ONLY  read only while being edited — knowledge isn't flowing back out (retrieval gap)")
    print("  RESURFACE?  never loaded in any session — discovery gap, not proven useless")
    print("  REVIEW      had reference traffic but gone cold > %dd — pruning/refresh candidate" % STALE_DAYS)
    print("  ACTIVE      currently earning its tokens via reference loads")
    print("  TOO_NEW     < %dd old — insufficient exposure to judge (coverage guard)" % MIN_AGE_DAYS)


if __name__ == "__main__":
    main()
