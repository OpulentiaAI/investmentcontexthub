---
type: guide.pattern
goal: "Model ownership, containment, or a hierarchy."
rule: "Choose the direction, endpoint types, and lifecycle of the relation before choosing prose, a field, or a separate record."
example:
---

# Modeling composition

Decide what belongs to what and whether the part needs identity outside the whole.
Keep content inline when it is owned and replaced with its parent.
Use a reference when the part needs independent access:

- Addressing
- Reuse
- Updates

**Make containment distinguishable**

A prose link is enough to explain a relationship to a reader.
Use a typed field when a consumer must distinguish containment from a passing mention or check the endpoint's kind.

When a parent names its children, its outgoing links show them.
Each child's backlinks show its referrers.
When a child names its parent, the parent's backlinks show the children.
Filter by the intended field or relation before treating backlinks as containment.

**Choose the range**

The target need not have the source's kind:

- A section may parent another section
- A task may belong to a project
- A heterogeneous tree may accept a shared base
- Other arrangements can share a relation when their consumers agree on its meaning and range

That relation cannot automatically specialize its target to each claimant's subtype.

**Give the relationship attributes**

Use a relationship record for attributes such as:

- Role
- Validity dates
- Provenance
- Other data belonging to the relation

The record can remain inline.
Separate identity is a further choice.

**Check the topology**

[[composition::au-host-sdk:example]] owns a pool of records that reference one another.
The host checks additional topology rules.
`T*` alone does not prevent:

- Cycles
- Multiple parents
- Unreachable parts

Compare a valid arrangement with:

- A cycle
- A wrong-kind parent
- A multiply owned child

For each case, decide whether it is legal.
For an illegal case, identify whether the type or consumer must catch it.
