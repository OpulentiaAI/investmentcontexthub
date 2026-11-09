---
type: guide.gotcha
goal: "Choose which package should own a type definition."
rule: "Place a type with the owner of its semantic contract; let consumers depend on that owner regardless of where their instances live."
example:
---

# Put the type with its contract owner

Place a definition in the package responsible for its meaning and evolution.
A local domain type often belongs with its instances.
A shared vocabulary or SDK capability belongs with the owner whose contract its consumers accept.

**Instances can live elsewhere**

[[mcp.tool::au-mcp-sdk:example]] belongs to the agent SDK.
[[mcp.tool.au_agent_guide::au-agent-guides:example]] belongs here because this package implements and maintains the capability.
External packages can claim [[guide::au-agent-guides:example]] without copying or moving its definition.

**Make the dependency explicit**

Bare claims resolve in the file's repository.
A qualified claim names a peer.
Cross-package type use needs the appropriate dependency.

Workspace discovery makes capabilities available.
It does not replace a vocabulary dependency.
Avoid making a base depend on an application to reach a type the base itself interprets.

Move a shared contract down when ownership and dependency direction justify it.
A second consumer alone does not require a new package.

**Distinguish ownership from identity**

A repository qualifier disambiguates ownership and lookup.
The engine's structural type identity includes the name and closure hash.
Matching definitions in different owners can therefore share an identity.

Name who should review a change in meaning and draw the dependency arrows.
Put the definition where that ownership and direction agree.
