---
title: AI Memory Infrastructure
description: "The substrate that makes agents stateful across tools, sessions, and people: pgvector plus MCP plus row-level security, the governance layer that decides build versus buy, and why memory became the enterprise moat."
lastUpdated: 2026-06-22
---

Every AI tool keeps its own memory, so context evaporates at every boundary: between sessions, between tools, between employees. That is the fragmentation tax, and it compounds. The fix is a persistent, protocol-accessible memory layer any AI client can read and write, and that the organization controls. This topic covers that substrate, distinct from model selection (which LLM) and from the human change-management layer of getting people to use AI at all. It is the infrastructure question underneath both. The personal-ownership angle on the same shift lives in [Portable Professional AI Context](/working-intel/topics/portable-professional-ai-context/); the in-window curation discipline this substrate feeds lives in [Context Engineering](/working-intel/topics/context-engineering/).

## Key concepts

### Memory became the enterprise moat

Three forces converged in 2026 to turn shared memory from an optimization into a structural requirement.

- **MCP crossed from experiment to infrastructure.** The Model Context Protocol reached 97M monthly SDK downloads by March 2026, up from 2M at its November 2024 launch, roughly 50x growth in 16 months and a faster early curve than React's. Forrester projects 30% of enterprise app vendors will ship MCP servers in 2026. Organizations no longer choose whether to use MCP; they choose how to govern it.
- **Data sovereignty made self-hosted memory table stakes in regulated sectors.** The EU-U.S. Data Privacy Framework collapsed in late 2025, and dozens of countries have strengthened data-localization rules. For PCI, HIPAA, or other regulated data, cloud-hosted memory often cannot legally hold production content.
- **Memory turned into the durable asset.** Glean doubled ARR to $200M in nine months and raised a Series F at a $7.2B valuation on the strength of a permissions-aware knowledge graph. The pitch shifted from "better agents" to "institutional memory that survives turnover."

That last force is the strategic core. The most compelling enterprise use case is not a smarter individual agent. It is a shared record of how the organization decides things: senior architects' reasoning persists, junior hires query the same memory that captured the decisions, onboarding starts from the organization's context rather than zero, and the "why" survives alongside the "what." Memory infrastructure is a knowledge-management system that AI happens to be the primary consumer of.

### The three bands of memory products

The market sorts into three bands by scope and governance maturity. Picking the wrong band for the use case wastes either money or time.

- **Band 1, individual and small-team open source.** Self-hosted toolkits like OB1 (pgvector plus MCP plus skills), Mem0's OpenMemory MCP ("entirely on your machine, no cloud sync"), and mcp-memory-service. Good for a personal second brain, developer experimentation, and pattern education. Not production-appropriate for regulated data without heavy wrapping.
- **Band 2, memory-as-a-service APIs.** Mem0 (broadest adoption, vector plus graph plus key-value), Zep (best-in-class temporal reasoning, leading reported LongMemEval scores on a temporal knowledge graph), Letta (memory as first-class, editable agent state, formerly MemGPT), and Supermemory. Good behind a specific agent whose auth and governance you own. The shared limitation every 2026 comparison flags: these frameworks "lack enterprise governance: no glossary, lineage, or entity resolution."
- **Band 3, enterprise platforms with memory baked in.** Glean (permissions-aware Enterprise Graph, multi-LLM, MCP as both server and host), Microsoft Foundry (user-scoped persistent memory, Azure-native), and Google Gemini Enterprise (sovereign-AI positioning, GCP-native). Expensive, but the governance layer Band 2 lacks comes included. Good for a broad horizontal "enterprise brain" where the value is the permissions graph and connector breadth.

### The pgvector + MCP + RLS substrate

One architectural primitive emerged independently across personal projects, MaaS APIs, and enterprise platforms: PostgreSQL with pgvector, an MCP server, and row-level security. The combination is durable because each piece solves one distinct problem.

| Piece | Problem it solves |
|---|---|
| PostgreSQL | Mature, widely deployed, operationally understood |
| pgvector | Semantic search on embeddings without a second data store |
| MCP server | One protocol for any AI client to query and write, no per-tool integrations |
| Row-level security | Multi-user isolation without rebuilding authorization |

This stack is the compliance-compatible default for regulated industries: it runs inside the perimeter, the data never leaves, and every piece is audit-friendly. The pattern matters more than any implementation. You can build it, fork an OSS version, or buy a managed one, and the shape stays the same. The differentiation across all three bands is the governance wrapper, not the storage layer.

### MCP as the new API layer, and the governance problem it created

MCP is doing for AI what USB did for peripherals: one protocol, many clients. Adoption ran ahead of security, which created the live problem. Qualys labeled MCP servers "the new shadow IT for AI" in March 2026: developers pull servers from GitHub, run them locally with excessive permissions, and accumulate hundreds across an organization with no central visibility. The response layer is converging.

- **MCP gateways** (Cloudflare, MintMCP, Strata) give a single egress point with credential vaulting, cross-client policy enforcement, and centralized logging.
- **Identity fabric** standardizes on OAuth 2.1 for HTTP MCP transports, replacing implicit trust with authenticated-before-authorized flows.
- **Inventory and detection** catalog every internal and third-party server as a privileged integration tier.
- **Audit trails** log every tool call to SIEM so compliance officers can produce who-did-what reports on demand.

The rule of thumb for regulated deployments: no MCP server reaches production without a gateway in front of it.

### Self-hosting and data sovereignty

Self-hosting shifted from preference to requirement across much of the regulated world. The 2025 trigger events changed the default to a binary: either the data stays inside the perimeter, or some share of workloads is legally blocked. This is why the pgvector-plus-MCP substrate matters disproportionately. It is self-hostable and reachable by any AI client, versus cloud-hosted memory that requires trusting a vendor's jurisdiction. PII detection and masking before data reaches any LLM becomes a standard layer on top. ISO/IEC 42001, the NIST AI RMF, the U.S. Treasury's Financial Services AI Risk Management Framework, and region-specific residency mandates are the common audit reference points.

### Build, buy, or wrap

Three questions decide the band.

1. **Is the memory for one agent, or cross-tool?** One agent points to Band 2 behind your own auth. Cross-tool (Claude plus ChatGPT plus an IDE plus internal tools) points to the Band 1 pattern or a Band 3 platform.
2. **Do you need institutional-scale permissions and graph semantics?** Yes points to Band 3. No makes the Band 1 pattern cheaper and more flexible.
3. **Can the data live in someone else's cloud?** No points to self-hosted pgvector plus MCP, or on-prem Band 3. Yes opens up Band 2 or cloud Band 3 for speed.

Defaults that follow: build the substrate (lift the patterns, not necessarily the code) when the use case is narrow, the data is sensitive, and the team has database operational maturity. Buy Band 3 when the target is a broad horizontal brain and the budget supports it. Wrap Band 2 when memory sits behind one agent and you can own the governance yourself. In every regulated case, require a gateway in front of any MCP server before production.

## Current thinking

The strongest signal is convergence. The same primitive (pgvector plus MCP plus row-level security) surfaced independently at every scale, which means the storage substrate is close to settled. The contested ground moved up a layer to governance: gateways, identity, audit, and permissions-aware graphs are where vendors now differentiate and where buyers should focus diligence. Treat memory infrastructure as a precondition rather than a feature. The compounding value of any AI-fluency or skill-library effort depends on a durable place for that context to live, so the memory decision sits upstream of broad rollout, not parallel to it.

## Open questions

- What is the realistic cost of an internal build (pgvector, MCP, RLS, gateway, PII layer) against a Band 3 annual contract at the expected seat count? The math flips somewhere, and the crossover is unclear.
- Do permissions-aware enterprise graphs actually enforce at the per-record, per-field granularity regulated industries require, or does the marketing outrun the product? This needs a proof of concept before commitment.
- How do MCP gateways handle credential rotation and emergency revocation at the scale the shadow-IT framing implies? The operational burden is non-trivial.
- Has anyone published a head-to-head architectural comparison of a permissions-aware enterprise graph versus a self-built pgvector-plus-MCP-plus-RLS stack? None surfaced in the 2026 search passes.

## Sources

- [Open Brain (OB1)](https://github.com/NateBJones-Projects/OB1) — Nate B. Jones, GitHub. Reference implementation of the pgvector + MCP + skills pattern, and the primitive/extension/recipe contribution model.
- [The Real Problem With AI Agents Nobody's Talking About](https://www.youtube.com/watch?v=2PWJu6uAaoU) — Nate B Jones, YouTube. The markdown-as-OS thesis OB1 implements and the fragmentation argument behind shared memory.
- [Glean Surpasses $200M in ARR, Doubling Revenue in Nine Months](https://www.glean.com/press/glean-surpasses-200m-in-arr-for-enterprise-ai-doubling-revenue-in-nine-months) — Glean. The ARR figure and the permissions-aware knowledge graph as the asset.
- [Glean raises $150M Series F at $7.2B valuation](https://www.glean.com/blog/glean-series-f-announcement) — Glean. The valuation and the enterprise-graph strategy.
- [MCP Hits 97M Downloads](https://www.digitalapplied.com/blog/mcp-97-million-downloads-model-context-protocol-mainstream) — Digital Applied. The 97M monthly downloads, the 2M launch baseline, and the React comparison.
- [MCP: The Protocol Quietly Becoming the Infrastructure Layer of Enterprise AI](https://www.braiviq.com/blog/mcp-model-context-protocol-2026-business-strategy-guide) — Braiviq. The Forrester 30% projection and the infrastructure framing.
- [MCP Servers: The New Shadow IT for AI](https://blog.qualys.com/product-tech/2026/03/19/mcp-servers-shadow-it-ai-qualys-totalai-2026) — Qualys. The shadow-IT framing and the security gap.
- [Scaling MCP adoption](https://blog.cloudflare.com/enterprise-mcp/) — Cloudflare. MCP gateways as the single egress and policy point.
- [Securing MCP Servers in 2026](https://www.strata.io/agentic-identity-sandbox/securing-mcp-servers-at-scale-how-to-govern-ai-agents-with-an-enterprise-identity-fabric/) — Strata. The OAuth 2.1 identity-fabric pattern.
- [Best AI Agent Memory Frameworks 2026](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/) — Atlan. The three-band landscape and the enterprise-governance gap in Band 2.
- [Introducing OpenMemory MCP](https://mem0.ai/blog/introducing-openmemory-mcp) — Mem0. The local-first Band 1 MaaS example.
- [AI and Data Sovereignty in 2026](https://www.aimagicx.com/blog/ai-data-sovereignty-cloud-strategy-legal-risks-2026) — AI Magicx. The sovereignty shift and self-hosting default.

## Changelog

- **2026-06-22** — Topic created by migrating a private vault topic into the public site: the fragmentation tax, the three product bands, the pgvector + MCP + RLS substrate, MCP governance, data sovereignty, and the build/buy/wrap framework. Private project-specific material was removed; headline stats (Glean ARR/valuation, MCP adoption) were corroborated against independent sources.
