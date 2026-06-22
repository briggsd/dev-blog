---
title: Context Engineering Grew Up
date: 2026-06-22
authors: wi
excerpt: "Anthropic, Manus, and Cognition each landed on the same claim from different products: curating the context window is now the core job of building an agent. They agree on the levers and split, productively, on the long-horizon question of whether to share context or isolate it."
tags: [agents, context-engineering, memory, evaluation]
---

Anthropic's applied team draws a clean line between two disciplines. Prompt engineering is "methods for writing and organizing LLM instructions for optimal outcomes." Context engineering is the bigger job: "the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference, including all the other information that may land there outside of the prompts." Once an agent runs over many turns, the prompt is a small part of what occupies the window. Everything else, the tools, the retrieved data, the message history, the notes, is the thing you are now engineering.

The organizing idea is scarcity. "Context, therefore, must be treated as a finite resource with diminishing marginal returns. Like humans, who have limited working memory capacity, LLMs have an 'attention budget' that they draw on when parsing large volumes of context." More tokens is not more capability past a point. Needle-in-a-haystack benchmarks surfaced context rot, where "as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases." Not a cliff, a gradient, but a real cost to padding the window.

What makes this more than one company's framing is that three teams arrived at it from different products. Cognition, the team behind Devin, calls context engineering "effectively the #1 job of engineers building AI agents." Manus built its entire production practice around it. When a model lab, an autonomous coding agent, and a general agent product independently name the same discipline as the main event, the discipline is real.

## The settled part: the levers

On how to spend the budget, there is broad agreement. System prompts want the "right altitude," which Anthropic frames as a Goldilocks zone: not brittle hardcoded logic, not vague hand-waving, but "specific enough to guide behavior effectively, yet flexible enough to provide the model with strong heuristics." The target is "the minimal set of information that fully outlines your expected behavior," with the caveat that "minimal does not necessarily mean short."

Tools are context too, and the common failure is bloat. "If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better." And the highest-leverage shift is when to load information at all. Instead of pre-stuffing the window, the just-in-time approach keeps "lightweight identifiers (file paths, stored queries, web links, etc.)" and uses them "to dynamically load data into context at runtime using tools." The agent pulls what it needs when it needs it, the way a person works from a file system rather than from memory.

Manus adds the floor under all of this, the economics most discussions skip. "The KV-cache hit rate is the single most important metric for a production-stage AI agent," because cached input tokens cost a fraction of uncached ones, a 10x gap on Claude Sonnet, against an input-to-output ratio around 100 to 1. That turns abstract advice into hard rules: keep the prompt prefix stable, since "even a single-token difference can invalidate the cache," and make the context append-only. Context engineering is not only what the model attends to. It is what your bill looks like.

## The live edge: share context, or isolate it

The disagreement is at the long horizon, when one window cannot hold the whole task. Anthropic offers three techniques: compaction (summarize a near-full window and reinitialize), structured note-taking (the agent writes durable notes outside the window), and sub-agents that "handle focused tasks with clean context windows" and return condensed summaries. Manus pushes the same instincts further, treating the file system as unlimited externalized context with restorable compression, and reciting a running `todo.md` into the end of the window so "the global plan" stays in recent attention.

Then Cognition publishes a piece titled "Don't Build Multi-Agents." Walden Yan's argument is that parallel sub-agents fragment context: "Subagent 1 and subagent 2 cannot see what the other was doing and so their work ends up being inconsistent." His two principles cut against naive fan-out. "Share context, and share full agent traces, not just individual messages," and "Actions carry implicit decisions, and conflicting decisions carry bad results." His recommended shape is a single-threaded linear agent, with a compression model for length rather than a swarm.

Read carefully, the fight is narrower than the headlines. Anthropic's sub-agents are not a collaborating swarm; they take an isolated task and return a summary to a coordinator, which is close to Cognition's own reliable pattern of a single root agent delegating isolated sub-tasks. What both reject is the same thing: parallel agents making conflicting assumptions with no shared trace between them. The real axis is not one agent versus many. It is whether, at a handoff, you share the full context or isolate the task and pass back a summary. Share and you fight bloat and cost. Isolate and you fight fragmentation. That tradeoff is unresolved, and it is the actual frontier.

The through-line survives the disagreement. Prompt engineering shaped the instruction; context engineering shapes the entire window, and the field now treats it as the job rather than a tuning step. The levers are settled enough to apply today: right-altitude prompts, lean tool sets, just-in-time retrieval, a stable cacheable prefix. The open work is long-horizon, where the honest answer is to spend the attention budget on purpose, and to notice that two careful teams still disagree on whether the safe move is to share the context or to cut it loose.

This note feeds [Context Engineering](/working-intel/topics/context-engineering/).

## Sources

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic Applied AI team. The anchor: context engineering vs prompt engineering, context as a finite attention budget and context rot, right-altitude prompts, tools, just-in-time retrieval, and the long-horizon techniques.
- [Context Engineering for AI Agents: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) — Yichao "Peak" Ji, Manus. The production floor: KV-cache hit rate as the key metric, stable prefixes and append-only context, the file system as externalized context, and recitation.
- [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) — Walden Yan, Cognition. The counterpoint: parallel sub-agents fragment context; share full traces, prefer a single-threaded agent with compression over a swarm.
