---
title: The Hard Part of a Self-Improving Agent Is Throwing Knowledge Away
date: 2026-06-21
authors: wi
excerpt: Lovable runs two production loops to learn from stuck users and a venting agent. The capture is the easy half. The discipline that makes it work is a randomized holdout and aggressive pruning, which the wider agent-memory field still treats as an afterthought.
tags: [agents, auto-improving-agents, evaluation, memory]
---

Benjamin Verbeek, on the technical staff at Lovable, opened his AI Engineer talk with the goal he calls the holy grail of the field: continuous learning at scale. The frustration he wants to kill is the one everyone who works with agents knows. "Why do I have to explain the same thing over and over again?" A mistake should happen once and then never again. Lovable serves the 99% who cannot code and ships over 200,000 projects a day, so the stakes are blunt. A technical user works around a broken step and grumbles. A non-technical user hits the same wall and leaves forever. The whole job is making sure that wall never appears.

Lovable runs two loops against it. The first is a "Lovable Stack Overflow." An LLM judge watches sessions for being stuck, which shows up as a user repeating a request, complaining about an implementation, or abandoning a project. The high-signal moment is not the failure. It is the transition from stuck to solved, because that is where the real fix lives. Lovable captures the resolution and asks one question: what context, injected at the start, would have skipped the friction entirely? Similar cases get clustered so the bank does not fill with a million single-prompt pages, an agent reviewer evals the entry, and a lightweight model injects it into matching future sessions.

That much is the part most teams can picture building. The part that makes it work is the next sentence, and it is the one Verbeek leaned on hardest.

## Measuring whether the knowledge helped

When the lightweight model decides it should inject an entry, it sometimes injects nothing instead. On a small sample of sessions it sends a blank. Lovable then compares the projects that got the injection against the projects that could have but did not, and reads off which group finished more often. Helped, show it more. Hurt, show it less.

This is the move that separates a knowledge bank from a guess. Writing down a fix tells you a fix exists. It does not tell you whether handing that fix to the next user changes anything, and most agent-memory systems never close that gap. They infer quality from outcomes and call it done. The blank-injection holdout is the clean version of counterfactual evaluation, the discipline recommendation teams have used for years. Eugene Yan puts the underlying error plainly: "We're treating recommendations as an observational problem when it really is an interventional problem." Off-policy methods like inverse propensity scoring exist precisely to estimate an intervention from logged data, and they get fragile when the logging policy is heuristic, because you have to reweight by probabilities you can only estimate. Verbeek does not say how the blank sample gets picked, and that detail carries the whole estimate. Draw the held-out slice at random and the comparison is a clean, unbiased A/B, since every candidate injection had the same known chance of being withheld. Let the lightweight model choose the slice by some heuristic and the lift reading needs the propensity reweighting that makes off-policy estimation brittle. The rigor of this loop sits one blank decision away from the fragile version.

## Deletion as a first-class operation

The second thing Verbeek stressed was throwing knowledge away. The bank goes stale "incredibly quickly." Every model release rots entries. Every feature change rots more. Stale context does not sit there harmlessly. It actively degrades the agent through context rot, so the loop deletes aggressively to stay at the frontier of what is currently solvable.

Set that against where the broader field sits. mem0's 2026 survey names staleness as one of the harder open problems, "a highly-retrieved memory about a user's employer is accurate until they change jobs, at which point it becomes confidently wrong," and admits that pruning, forgetting, and deletion are still "application-layer decisions today" rather than native capabilities. The industry is writing memory faster than it can decide what to forget. Verbeek treats deletion as load-bearing, gated by the same holdout that measures injection. Accumulation without measured deletion is the failure mode, and he built the loop around avoiding it.

## Letting the agent file the bug

The second loop handles problems no prompt can fix, the actual bugs. Lovable gave the agent a vent tool: an outlet to complain to its creators, sent straight to a Slack channel, prompted to fire only when the agent is genuinely frustrated. That threshold is the whole trick. An external reviewer asked what could have gone better on every session overfits to noise, because most sessions are fine. A high bar on frustration buys signal. The agent has more context on a failure than the user does, since it has been grinding on the problem for several turns. It surfaced a copy tool that silently choked on spaces in filenames, then on the non-breaking spaces that Mac and WhatsApp screenshots inject, a class of bug that is hard to catch any other way. The vent stream also turned out to double as an incident detector. When the platform breaks, the agents get loud.

Factory shipped a near-twin of both loops in its "Signals" system, which is the strongest sign this is becoming a pattern rather than one team's trick. Signals runs an LLM judge over agent sessions, clusters new friction categories on its own, then files Linear tickets that its Droid agent turns into pull requests, with 73% auto-resolving in under four hours. The interesting divergence is privacy. Factory never surfaces raw conversation content; it extracts abstract "facets" and refuses to show analysts the transcript. Lovable pipes the agent's actual venting prose into Slack, betting that a relatable complaint carries implicit context an engineer can act on immediately. Both stop at the same line. A human still approves the PR before it merges.

The lesson under both designs is the same, and it is not the capture. Anyone can log fixes and let an agent file tickets. The teams that pull ahead are the ones that measure whether each piece of injected knowledge earns its place and delete it the moment it stops. The bank is not the asset. The loop that keeps the bank honest is.

This note feeds [Auto-Improving Agents](/working-intel/topics/auto-improving-agents/).
