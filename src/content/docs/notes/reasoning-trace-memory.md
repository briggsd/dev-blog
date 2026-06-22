---
title: The Reasoning Trace Is the Memory You Throw Away
date: 2026-06-22
authors: wi
excerpt: "Agent memory keeps what was retrieved and discards why a decision was made. A Neo4j talk argues for a third memory tier that stores the reasoning trace as a graph, and the research direction suggests the idea outlasts the vendor pitch."
tags: [agents, memory, knowledge-graphs, evaluation]
---

Stephen Chin, who runs developer relations at Neo4j, opened his AI Engineer talk with a gap in how agents remember. Retrieval gets you semantically similar content. It does not get you the reasoning behind past decisions. His fix is a three-tier memory model, all of it persisted in a graph: short-term memory (the current pipeline state and conversation), long-term memory (the domain model of customers, products, and prior decisions), and a third tier most systems skip, the reasoning trace.

That third tier is the interesting one. "Typically what we get from LLMs is we get the result," Chin says, but "to get to that result there is thinking, there's reasoning which happens behind the scenes," and that thinking normally gets thrown out the moment the answer ships. A reasoning trace keeps it: what tools were called, what policies were consulted, what the model weighed, and what it decided, stored as queryable nodes and edges. The payoff he names is decision provenance, learning from precedent, and "a great hook in for compliance and debugging."

Set that against how agent memory usually works. The common model is three verbs, storage, injection, and recall, running over vector retrieval. That machinery is good at keeping the *what*: the documents, the facts, the prior turns. It discards the *why*. The reasoning trace is a different axis from all three verbs. It is provenance, and it is the half of memory most teams never persist, because the model produces it for free and then drops it on the floor.

## Why a graph, and when not to bother

Chin's case for graph structure is the standard one, made cleanly. Relationships are first-class, so a walk from patient to diagnosis to treatment to prior operations is a traversal, not a pile of joins. Multi-hop queries stay fast. And the traversal path itself is the explanation: you can show a reviewer exactly which nodes and edges produced an answer. For a regulated decision, that auditability is the product.

The honest framing of graph versus vector has settled, though, and it is not "graphs win." It is hybrid. Vector retrieval finds the entry point, graph traversal pulls the relational context from there. One practitioner guide puts the adoption order plainly: "Start with vector databases for foundational agent memory, then selectively introduce knowledge graphs as reasoning complexity demands multi-hop relationship resolution." Vector handles single-hop and similarity; a graph earns its place when your retriever cannot follow a relationship chain, A to B to C, and that specific failure is why the answers are wrong. Reach for the graph for that reason, not because it is fashionable.

## The direction is real, and it has a clock

The provenance-as-graph idea is bigger than one vendor's slide. Zep's temporal knowledge graph for agent memory reports beating MemGPT on the benchmark MemGPT's own team established, "94.8% vs 93.4%" on Deep Memory Retrieval, and its open-source engine Graphiti is, in the paper's words, "a temporally-aware knowledge graph engine that dynamically synthesizes both unstructured conversational data and structured business data while maintaining historical relationships."

The load-bearing word there is temporally-aware. Chin's model captures the why; Zep adds the when. Facts change, and a memory that never invalidates a stale one hands the agent a contradiction to reason from. A decision trace without time is half a trace: it can tell you what was decided, but not whether the world it was decided in still exists. If you build the provenance tier, build it with validity in mind from the start.

## The caveat that comes with the territory

Both Neo4j and Zep sell graph databases, so the strongest claims arrive motivated. Chin notes that Gartner added context graphs to its AI hype cycle, which cuts both ways: real enough to track, hyped enough to discount the live demos. The auditable loan-decision demo, where the agent surfaces a prior rejection from the graph and explains its denial, is exactly the kind of staged, happy-path artifact that looks better on stage than under production load. Take the architecture, hold the adoption pressure.

The durable lesson does not require a graph database tomorrow. Agent memory has an axis most teams ignore. Past storing what was retrieved and recalling it later, persist *why* each decision was made: the tools, the policies, the alternatives, the outcome, and when it was true. That trace is what makes an agent auditable, what lets it learn from its own precedent instead of re-deriving the same call next week, and what turns "the model said so" into a path someone can walk. A graph is a natural home for it because the path through the graph is the explanation. The point is to stop throwing the why away.

This note feeds [Agent Design](/working-intel/topics/agent-design/).

## Sources

- [Connecting the Dots with Context Graphs](https://www.youtube.com/watch?v=eW_vxrjvERk) — Stephen Chin, Neo4j (AI Engineer), YouTube. The anchor talk: the three-tier memory model and the reasoning-trace tier, the graph-for-memory case, and the healthcare and loan-decision demos.
- [Vector Databases vs. Graph RAG for Agent Memory](https://machinelearningmastery.com/vector-databases-vs-graph-rag-for-agent-memory-when-to-use-which/) — MachineLearningMastery. When each wins, the multi-hop limitation of similarity search, and the hybrid (vector entry, graph traversal) recommendation.
- [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/abs/2501.13956) — Rasmussen et al. The DMR benchmark result versus MemGPT and the temporally-aware Graphiti engine (open-source, built on Neo4j).
