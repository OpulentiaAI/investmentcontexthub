---
type: guide.pattern
goal: "Choose a representation for a status, variant, or lifecycle."
rule: "Use an enum for uniform values, a named value contract for reuse, and record variants when fields or references depend on the branch."
example:
---

# Modeling discrete states

Choose the representation by what must vary.
A status value needs a different contract from a record whose fields depend on its state.

**Values and variants**

- Use a local enum for a small closed set when the surrounding fields stay the same
- Use a named enum under `shape:` to share a vocabulary across fields or packages without a node per value
- Use a sealed record family for mutually exclusive branches with different required fields or references to a particular branch
- Use a named union to combine existing value or record types without a common parent, as in [[name-a-value-contract]]

[[mcp.inject::au-mcp-sdk:example]] uses local enums for configuration choices.
[[mountable::au-host-sdk:example]] uses a sealed family for records with different structural jobs.
Read both definitions to see which obligations need each representation.

**Identity and specialization**

Reference a state record when the state itself needs:

- Identity
- Metadata
- An independently editable vocabulary

The reference does not give its holder branch-dependent fields.
Subtype a listed sealed branch when a consumer needs a more specific record within that branch.

**Workflow obligations**

A sealed family checks compatible claims.
The workflow must:

- Enforce transition order
- Complete side effects
- Establish any required inverse relation

[[guard-a-reference-by-state]] covers references that accept only particular states.

To check the representation, write a valid value or record for each alternative and an invalid combination that it must catch.
Check the workflow obligations separately.
