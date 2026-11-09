---
type: guide.gotcha
goal: "Define a tool's public input without maintaining a duplicate schema."
rule: "Author public arguments as type fields, inspect the generated schema, and check runtime rules at the operation boundary."
about: "[[mcp.tool::au-mcp-sdk]]"
example:
---

# Define the arguments in the tool type

Author public arguments in the tool type's fields and descriptions.
The daemon generates the advertised JSON Schema from those effective fields.
Maintain that source instead of a parallel argument catalogue.

[[mcp.tool.au_agent_guide::au-agent-guides:example]] declares selectors in fields and implements their meaning in its serving module.
The schema describes the arguments.
The implementation checks relationships such as mutually exclusive selectors.

**Share only common input**

Inherited fields count as arguments.
Put an argument on a parent only when every child accepts it with the same meaning.
A fieldless base fits unrelated operations, but is not required for every tool family.
Keep runtime configuration and presentation at their own contract levels.

**Inspect each validation surface**

Generated object schemas reject additional properties.
The engine validates records with an open-world model.
The daemon's input check uses the engine verdict and handles failures through its own logic.

These surfaces can impose different restrictions.
Advertised validation does not remove the need for runtime checks.

Inspect the generated schema before depending on a new shape.
An engine-valid type may still exceed a generator's or harness's support.

Try:

- A valid call
- An invalid field value
- A cross-field combination the schema cannot express

Compare each result with the documented operation.
