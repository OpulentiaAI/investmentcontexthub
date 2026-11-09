---
type: guide.gotcha
goal: "Attach metadata consumed through a type definition."
rule: "Put type-level presentation, loading, or routing data in typed meta; keep per-instance configuration in fields."
example:
---

# Put metadata at the level its consumer reads

Put a type's runtime entry or presentation in its typed `meta:` blocks.
A type-level consumer will not obtain them from similarly named instance fields, even if the engine preserves those extra values.

[[mcp.tool.au_agent_guide::au-agent-guides:example]] declares call input in fields.
Its metadata describes:

- The module
- Presentation
- Broker access

A call supplies input without redeclaring the runtime.

**Use a metadata type**

A metadata type must belong to the engine's meta family.
The engine checks the block's fields as values of that type.
The containing type's fields continue to describe its instances.

**Supply required metadata locally**

A concrete type with a required-meta obligation must supply its own satisfying block.
An ancestor's surfaced block does not satisfy it.
`meta: []` does not exempt the type and also affects ancestor lookup.
Inspect the resolved result before using an empty list.

**Check what the consumer reads**

An unmet obligation produces an engine diagnostic.
Its severity does not establish whether the consumer can load the capability or proceed with an action.

Inspect the type through the engine and locate the exact block the consumer reads.
Compare two instances with different configuration.
Values that vary per instance belong in their contract.
The shared locator stays on the definition.
