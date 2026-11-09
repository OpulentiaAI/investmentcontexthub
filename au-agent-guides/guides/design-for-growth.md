---
type: guide.principle
goal: "Evolve a type without overlooking existing data and consumers."
rule: "Separate inheritance rules from schema evolution, and check a change against both existing instances and the consumers that interpret them."
example:
---

# Evolve the contract with its consumers

Check a type change against existing data and the consumers that interpret it.
Width-only inheritance prevents a subtype from redeclaring an inherited field, even with the same shape.
It does not make every addition to a definition compatible.

**Examples of additions that change behavior**

- An optional field preserves records that omit it, but constrains any existing open-record extra with the same name
- A new sealed branch can break a consumer's exhaustive switch while leaving old records valid
- Metadata can change loading or execution without changing instance fields
- Other additions need checking against the existing data and consumers they affect

**Require what valid instances need**

Make a field required when every valid instance must supply the information.
Make it optional when absence has a meaningful interpretation.
Deferring every obligation leaves consumers guessing about records that validate.

[[tool-presentation-meta::au-mcp-sdk:example]] combines required presentation with optional proactive guidance.
A missing required meta block is an engine warning, yet a consumer may need it to load.

**Review the change with its migration**

Before changing a shared definition, inspect:

- Existing instances
- Subtypes and references
- Actual consumers

Include body templates and required metadata.

Use a mutation preview where available to inspect the diagnostic impact it reports.
After an authorized change, inspect diagnostics and exercise the affected consumer.
A narrower shape can be right when the data and code migrate with it.

Pins preserve historical coordinates.
They do not track live-target drift or make a changing consumer compatible.
See [[what-rots-silently]].

Choose cases affected by the change.
For a field addition, check existing values under that name and records that omit it.
For a branch addition, check consumers that dispatch on the type.
Reuse current instance and consumer evidence when it already answers the compatibility question.
