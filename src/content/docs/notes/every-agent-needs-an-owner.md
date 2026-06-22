---
title: Every Agent Needs an Owner
date: 2026-06-21
authors: wi
excerpt: A practitioner, an analyst, a platform vendor, and the security world are converging on the same unglamorous answer to agent sprawl. Every agent needs a named human owner, and they disagree mainly on how heavy that ownership should be.
tags: [agents, ownership, governance]
---

The loudest part of the agent conversation in 2026 is still about building: spin one up, connect the tools, automate the workflow. The quieter problem is what happens on day two, when the thing you built starts doing work nobody is watching. Four very different camps have arrived at the same answer, and it is not a new model or a framework. It is a name. Someone has to own each agent.

## The practitioner view: care and feeding

[Nate B Jones](https://www.youtube.com/watch?v=rh_PcL26zls) puts it bluntly: the fastest way to make an agent dangerous is to let everyone use it and nobody own it. His test for whether something even counts as an agent skips the brand on the box. If a system reads context, produces work you act on, and touches a workflow other people depend on, it needs an owner.

His operating model is four commitments per agent: a job you can state in one sentence, a diet of the context it reads, boundaries that match its risk, and a review loop. The individual version of governance is an owner card: name, owner, job, sources, what it can do, what it cannot, and the failure mode to watch. Maintenance, he argues, is the actual 2026 skill, the way prompting was the 2023 skill and delegation was the 2025 one. Building a new agent should no longer earn credit. Owning one that delivers value should.

## The analyst view: this is now a scale problem

Ownership sounds optional until you count the agents. Gartner predicts that by 2028 an average Fortune 500 enterprise will run more than 150,000 agents, up from fewer than 15 in 2025. (That figure comes from Gartner's newsroom; their page blocks automated reading, so treat it as a reported prediction rather than something I verified line by line.) Gartner's recommended response to the resulting "agent sprawl" leads with establishing governance and building a centralized agent inventory.

The adoption curve underneath that is real now, not speculative. InformationWeek cites a Deloitte survey in which nearly three-quarters of 3,325 leaders plan to deploy agentic AI within two years. The agents are coming faster than the ownership model for them.

## The security view: an unowned agent is an orphaned identity

The security world reaches the same destination from a different road. To them, an agent is a non-human identity: a service account, an API key, an OAuth token. Those identities already outnumber human users and receive far less governance. As InformationWeek frames the risk, when permissions are overly broad or poorly governed, agents amplify those weaknesses at machine speed.

The fix they propose rhymes with the owner card. Give each agent a unique identifier and tightly scoped, purpose-driven permissions. Assign clear ownership with ongoing review so identities do not go orphaned when the person who created them moves on. Same instinct, harder edge: an unowned agent is not just sloppy, it is a standing credential nobody is accountable for.

## The platform view: you can't govern what you can't see

Microsoft's Cloud Adoption Framework turns the instinct into infrastructure. Its first rule for agents across an organization is that leaders must be able to identify what agents exist, determine who owns them, limit what they can access, observe what they do, and stop what they should not do. The blunt line at the center of it: you can't govern agents you don't know exist.

The mechanism is a registry. Record every agent in one inventory, and track its ownership, purpose, platform, and access scope. Give each agent a single identity so its actions are attributable. Assign accountability for agent governance to the leaders who already own cloud governance and security, rather than standing up a parallel model. Nate's "agent roster" and Microsoft's "agent registry" are the same idea at two different altitudes.

## Where they agree, and where they don't

Strip the vocabulary and the four camps say one thing: every agent that does real work needs a named, accountable owner and a record of what it is allowed to touch. A practitioner, an industry analyst, a security discipline, and a platform vendor do not usually converge by accident.

The disagreement is about weight. Nate's owner card lives in a Slack channel and costs nothing to start. Microsoft's control plane assumes Entra identities, a central registry, and policy enforcement across platforms. Both are right for different sizes. A handful of personal agents needs the card. A hundred thousand of them needs the control plane. The mistake is matching the wrong weight to your scale: bureaucracy over three agents, or a Slack channel over fifty thousand.

The throughline is that ownership has to arrive with the agent, not after the incident. I keep the running version of this argument in the evergreen [Agent Ownership and Maintenance](/working-intel/topics/agent-ownership-and-maintenance/) topic.

## Sources

- [Most Teams Skip This Critical AI Agent Skill in 2026](https://www.youtube.com/watch?v=rh_PcL26zls) — Nate B Jones, YouTube. The care-and-feeding model, the owner card, and maintenance as the 2026 skill.
- [Governance and security for AI agents across the organization](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/governance-security-across-organization) — Microsoft Cloud Adoption Framework. The control plane, the agent registry, single identity per agent, and "you can't govern agents you don't know exist."
- [Non-Human Identity Sprawl Is Agentic AI's Real Risk](https://www.informationweek.com/risk-management/non-human-identity-sprawl-is-agentic-ai-s-real-risk) — InformationWeek. Agents as non-human identities, orphaned credentials, the Deloitte adoption figure, and the Define/Assess/Enforce/Detect/Automate framework.
- [Gartner Identifies Six Steps to Manage AI Agent Sprawl](https://www.gartner.com/en/newsroom/press-releases/2026-04-28-gartner-identifies-six-steps-to-manage-artificial-intelligence-agent-sprawl) — Gartner newsroom. The agent-sprawl prediction (150,000+ agents per Fortune 500 by 2028) and the centralized-inventory recommendation. Reported figure; primary page not machine-readable.
