---
type: au.engine.readme::au-engine
tldr: Design and build new workspace capabilities, using research into methods and practices to guide the choices.
---

# Repo Overview

> Work in progress and not thoroughly tested.
> Expect breaking changes.

## What this is

`au-competency` helps you design new structure for your Arsumbris workspace.
That can mean types and relationships for your knowledge, skills and guides for your agents, or tools and workflows that connect them.

Self-research investigates methods and established practices through [[README::au-tree-research]].
It helps you decide what fits your work and why.
A known solution can go straight to a proposal.

## How to use this

Mount the package and select the skills your task needs.
Tell the agent what your workspace should be able to do or where you keep running into friction.
Use [[workspace-premise]] to ground improvements in its purpose and boundaries.

| Skill | Use |
| --- | --- |
| [[derive]] | Identify a missing capability |
| [[self-research]] | Research methods that could guide its design |
| [[propose]] | Develop a change you can review |
| [[design-architecture]] | Explain how the parts will work together |
| [[improve]] | Build approved changes and check the result |

Use the supporting guidance from [[README::au-agent-guides]].
For research setup, follow [[README::au-tree-research]].
Keep small designs in the proposal.

## How to extend this

Keep your requirements, proposals and evidence in your own repo.
Depend on `au-competency` when using its types.
Extend them with fields or writing guidance suited to your work.
