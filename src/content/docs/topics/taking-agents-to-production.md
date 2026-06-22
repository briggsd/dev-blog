---
title: Taking Agents to Production
description: "The demo-to-production gap for agents: treat evaluation as the spec, trace every decision, and pick the model last, because production agents fail behaviorally and reliability lives in the measurement system."
lastUpdated: 2026-06-21
---

Most agent projects die the same way. Leadership feels pressure to ship something with AI, the first question is which model to use, a team demos features on clean data, and a few weeks into production nobody can explain what the agent is actually doing or why it stopped working. The demo never scaled, and the spend returned nothing.

This topic tracks the operational discipline that gets an agent from demo to production and keeps it there. It sits above the runtime substrate ([Agent Infrastructure](/working-intel/topics/agent-infrastructure/)) and the agent's own behavior ([Agent Design](/working-intel/topics/agent-design/)): the measurement, observability, and governance system that proves an agent is reliable and holds it reliable under real traffic. The load-bearing claim, which the field has converged on, is that production agents rarely fail at the model. They fail across the trajectory, so reliability is a property of the system around the model rather than the model itself.

## Key concepts

### The three production gaps

Three gaps sink production AI, and each maps to a discipline this topic covers:

1. **Observability gap.** You cannot see what the agent did, so you cannot debug it, improve it, or defend it to a regulator.
2. **Evaluation gap.** You never defined the one number that means success for the business, so you cannot tell whether the system is improving.
3. **Governance gap.** Nobody owns the failure at 3 a.m., nobody owns the data the agent reads, and nothing catches an injection or a leak.

Naming the gaps first, before any code or model talk, is what separates a project that ships from a demo that stalls.

### Evaluation is the specification

Evaluation is the spec for an AI system, and it comes before code, features, or models. Defining success means business numbers, not "accuracy" in the abstract: for a support chatbot, deflect some target percentage of simple queries at some target accuracy and latency. The test set comes from domain experts, not intuition. Sit with the humans doing the job today, collect their real answers to real questions, and capture what they do in the confusing edge cases. That golden dataset becomes an automated pipeline: live responses score against it continuously, low-scoring responses route to a human, and every fix becomes a new case.

The dataset is a living, owned asset. It starts small (one banking build seeded it with 200 real cases) and compounds as production surfaces new failures. The bigger and better-curated it grows, the stronger the system, which makes it the closest thing an agent program has to a moat. This is the same accumulate-and-measure dynamic the [Knowledge Flywheel](/working-intel/topics/knowledge-flywheel/) describes, applied to test cases.

A caveat to the golden-dataset orthodoxy: you do not always need a pre-labeled set to begin. You can synthesize cases with "dueling LLMs" that role-play users, or curate anonymized production sessions into permanent test cases, then label as you go.

### The three evaluation layers

Evaluation is an architectural decision with three layers, and teams skip the third:

1. **Deterministic.** The cheap, decades-old checks: regex for email and phone formats, classic ML for intent classification and PII detection. Get these out of the way.
2. **Semantic.** Non-deterministic quality, scored by an LLM judge that grades the primary model's output for groundedness, safety, and relevance against the golden answers. Mature platforms run custom LLM judges automatically over traces.
3. **Behavioral.** The agent's process itself: did it call the right tool, pass the right arguments, avoid loops, and answer without burning ten API calls. Teams under-invest here, and the next section explains why it carries production reliability.

Behavioral evaluation has standard sub-metrics: tool correctness (did it pick the right tool, a deterministic check), argument correctness (right tool, wrong arguments is its own failure), and step efficiency. Others frame it as evaluating the trajectory rather than the final output. Testing agent pipelines at the behavioral level connects to the patterns in [Agent Design](/working-intel/topics/agent-design/).

### Failures are behavioral, not model-based

The reason the behavioral layer matters is that production agents fail across steps, not at the model. The canonical example: a user asks for an account balance, the agent returns the right number, and every output check passes. Walk the trace and the agent made three duplicate database calls to get there, retrying through silent failures. Harmless in a demo, expensive across thousands of daily queries.

The field describes the same pattern from several angles. One framing: "An agent can look busy, reason intelligently, call the right-looking tools, and still fail to complete the task." Google Cloud calls it a "silent failure," where an agent "might give the correct number but reference last year's report by mistake. The result looks right, but the execution failed." A deployment-loop catalog lists where agents break: bad retrieval on step 2, wrong tool arguments on step 4, silent state corruption on step 5, a plausible-looking final answer on step 8. None is a model-quality problem, and none is visible without a trace.

The consequence is the organizing idea of this topic: reliability is built with a measurement system, not bought with a better model.

### Observability and tracing

Observability means capturing every decision an agent makes as a causal trace, not just logging the final response. For a banking fee-waiver request, the trace shows intent classification with its confidence and latency, the account-database call, the policy-document retrieval from a vector store, the reasoning step, and the final guardrail checks. The field calls this the shift from "response logging" toward "causal tracing": session IDs, trace IDs, step-level spans, tool inputs and outputs, and explicit success or failure markers.

Tracing pays off three ways. It is a regulatory precondition, since regulators in Europe and elsewhere refuse to onboard agents without it, and a customer dispute is indefensible if you cannot show what the agent did. It powers online monitoring that can cap retries or route to a human mid-incident. And it is how failure attribution works: "when a metric fails, you walk the trace from the final output to the exact span that broke." Observability and evaluation are a pair, not substitutes: "observability without evals produces dashboards / evals without observability produce blind benchmarks."

### The data foundation

Often the largest share of the work (one practitioner reports spending 60% of project time here). Data was built for humans, who forgive a wrong figure in a report and ask someone to fix it. Agents do not forgive. They read the wrong value and answer confidently wrong, and you may never notice. Two kinds of data need a strategy:

- **Question data:** what the agent reads to answer, including retrieval sources and the APIs it calls. Stale or low-quality question data is a leading cause of confident wrong answers.
- **Tracking data:** the trace and observability data itself, which needs a deliberate schema so you can serve it to auditors, run LLM judges over it, and drive monitoring.

At enterprise scale, agents run across multiple frameworks and clouds, so the tracking data wants a centralized collection layer that feeds operational dashboards, first-line support, and the eval pipeline from one place. Governing the question data through a single catalog (descriptions, column metadata, PII tags) also gives the agent better context when it queries those tables.

### Orchestration patterns

One agent needs no orchestration. Five agents make coordination the hard problem. Three patterns recur, and related orchestration material lives in [Agent Infrastructure](/working-intel/topics/agent-infrastructure/):

- **Orchestrator-worker:** a central orchestrator routes work to specialized agents and every request flows through it, which concentrates control and makes failures easy to find in one log.
- **Choreography:** autonomous agents publish and subscribe to a message bus, running in parallel and reacting to events they care about, which cuts latency by removing the central round-trips.
- **Human-in-the-loop:** when an agent crosses or falls below a confidence threshold, a human enters the workflow to review and act.

The production concerns that decide between them are state management and fault tolerance.

### Governance for AI, beyond data governance

Data governance is assumed. The AI-specific governance layer covers:

- **Audit trails** for every action, connection, and request, the record regulators expect.
- **PII pre-validation** using named-entity recognition and rejection rules before data reaches the model. One build caught 47 PII breaches during the testing phase with this layer alone.
- **Prompt versioning as change management.** A prompt change is a production change, not a one-word git commit. Record what failed, why the prompt changed, and what the new version corrects, so you can trace a regression to the edit that caused it.
- **Model change management.** Provider benchmarks do not predict performance on your data, so run every candidate or upgraded model against your own dataset before trusting it. This keeps you free to switch providers and avoids betting the system on one model.

The accountability side of this (who owns which agent and which failures) is the subject of [Agent Ownership and Maintenance](/working-intel/topics/agent-ownership-and-maintenance/).

### The production incident playbook

The artifact most teams skip. A defined sequence for when an agent fails in production:

1. **Detect** on the eval dashboard (a metric or satisfaction score drops).
2. **Diagnose** in the trace (find the span that broke).
3. **Contain** by reverting the offending prompt version, applying a fallback, or routing to a human. Fault-tolerance patterns here include saga, compensation, and circuit breaker.
4. **Fix**, then add the failing case back to the test library so the bug stays fixed.
5. **Alert** through the existing ITSM system so the right person is paged and downstream systems are protected.

A worked example: six weeks after launch a chatbot's satisfaction scores fell. The trace showed the agent reading a superseded policy document, because new embeddings never reached the vector database. Without the system, that reads as "AI is acting up." With it, it reads as a stale-index bug with a known fix.

### Pick the model last

The pillars compose into one counterintuitive ordering. In an eight-week banking-chatbot build, the team chose the model in week seven. Weeks one and two built evaluation, the next weeks built the data foundation and tracing, and only then did model choice come up, at which point it was a fast measurement against the dataset rather than a month of debate. An earlier vendor POC had spent about 85,000 dollars over six months with none of this and failed, because no one could measure why it was failing or say who owned the failure.

The model question feels urgent because the model is the new and exciting part. The work that decides whether an agent survives production is the measurement and governance system around it, most of which is engineering teams already know how to do. Build that first and the model becomes a swappable, last decision. This connects to the broader [auto-improving](/working-intel/topics/auto-improving-agents/) thesis: a metric-gated loop is only as good as the eval harness under it.

## Current thinking

The strongest signal here is convergence. A vendor practitioner, an independent eval guide, a hyperscaler methodology, and the production-loop literature all arrive at the same shape: define success as a business metric, trace the trajectory, evaluate behavior and not just output, and feed failures back as test cases. When sources with different incentives describe the same discipline, it is closer to settled practice than to one vendor's pitch.

The reframe with the most leverage is "reliability is a system property, not a model property." It reorders a project (eval and observability first, model last), reassigns the budget (data foundation and test curation over model trials), and reassigns the risk (model portability over single-model lock-in).

The behavioral evaluation layer is the current frontier of neglect. Deterministic and semantic checks are well understood. Trajectory-level evaluation (tool correctness, argument correctness, step efficiency, loop detection) is where teams under-invest and where the expensive silent failures hide.

## Open questions

- Behavioral evals are expensive to run against a growing dataset. Beyond running a subset in CI and the full suite on merge, what other cost-control patterns hold up at hundreds or thousands of cases?
- Where is the line between "you don't need a golden dataset to start" (synthesize and curate as you go) and the discipline of a curated golden set? When does each approach win?
- What does the tracking-data schema look like in practice across heterogeneous frameworks (different orchestrators, clouds) so that one eval and monitoring layer can consume it?
- How much of this playbook can a holdout-gated [auto-improving](/working-intel/topics/auto-improving-agents/) loop automate, and which pillars (governance, incident ownership) must stay human-owned?
- Prompt-versioning-as-change-management is sound in principle. What does a lightweight version that teams actually follow look like, short of full enterprise change control?

## Sources

- [The Production AI Playbook: Deploying Agents at Enterprise Scale](https://www.youtube.com/watch?v=ObTPqBGsEbA) — Sandipan Bhaumik, Databricks (AI Engineer), YouTube. Source for the five pillars, the three production gaps, the three evaluation layers, evaluation-as-spec and the living test set, causal tracing and online monitoring, the data foundation, orchestration patterns, AI governance, the incident playbook, and the week-seven "pick the model last" case study. Synthesized in the note [Pick the Model Last](/working-intel/notes/pick-the-model-last/).
- [LLM Agent Evaluation](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide) — Confident AI. Source for agent failures being behavioral rather than model-based, evaluation as the reliability determinant, tool correctness and argument correctness as distinct metrics, and trace-based failure attribution.
- [A methodical approach to agent evaluation](https://cloud.google.com/blog/topics/developers-practitioners/a-methodical-approach-to-agent-evaluation) — Google Cloud. Source for "silent failures," trajectory versus final-output evaluation, the "you don't always need a pre-labeled golden dataset" caveat, and eval as a CI/CD quality gate with a feedback loop.
- [Production AI Agents in 2026: Observability, Evals, and the Deployment Loop](https://dev.to/chunxiaoxx/production-ai-agents-in-2026-observability-evals-and-the-deployment-loop-4aab) — DEV Community. Source for multi-step trajectory failure categories, the shift from response logging to causal tracing, and the "observability without evals / evals without observability" framing.

## Changelog

- **2026-06-21** — Topic created from the Databricks "Production AI Playbook" talk and three converging outside sources (Confident AI, Google Cloud, the 2026 deployment-loop write-up). Seeded with the three production gaps, evaluation-as-spec and the three eval layers, behavioral-failure thesis, observability and tracing, the data foundation, orchestration patterns, AI governance, the incident playbook, and "pick the model last." Feeds the note [Pick the Model Last](/working-intel/notes/pick-the-model-last/).
