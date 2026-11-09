---
type: guide.principle
goal: "Extend a framework capability through the representation its consumer discovers."
rule: "Inspect the consumer's discovery contract before choosing a subtype, an instance, or a mixin."
example:
---

# Match the capability's discovery contract

Extend a capability through the representation its consumer reads.
Read that discovery contract before choosing how to extend the graph.

**Definitions contribute executable behavior**

[[mcp.tool::au-mcp-sdk:example]] and [[projection::au-host-sdk:example]] use subtype definitions with runtime metadata.
Their consumers discover the definitions and resolve code through the owning package.
An instance alone does not register an implementation.

**Instances contribute content**

[[mcp.skill::au-mcp-sdk:example]] and [[guide::au-agent-guides:example]] use concrete instances.
A new skill or guide usually needs no subtype.
Derive a type when it adds a useful shared contract.

[[mcp.hook::au-mcp-sdk:example]] uses both levels: definition discovery for executable behavior and typed configuration from a profile.

**Choose the contract deliberately**

Keep a base concrete when a direct instance is meaningful.
Make it abstract when it supplies common structure or a discovery boundary without being directly claimable.
The engine enforces that distinction.

Multiple inheritance and mixed claims can express independent capabilities.
Check that each consumer understands the combination.
Legal mixing does not prove that two loaders will interpret one record coherently.
Naming conventions alone do not establish type identity.

**Follow discovery through use**

Read the discovery requirements:

- Required metadata
- Selection rules
- Supported instance origins

Then account for the consumer's remaining obligations:

- Loading and authorization
- Configuration
- Invocation

Add the smallest representative contribution and use the consumer's qualified subtype or instance query.
Then load or use it.
Keep the observations distinct:

- A registry entry
- A resolving type
- Working behavior
