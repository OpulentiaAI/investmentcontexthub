---
type: guide.gotcha
goal: "Decide whether a concept needs a type, a value, or an instance."
rule: "Give a concept a type when it supplies a useful contract or identity; instance count alone does not decide."
example:
---

# Choose a type for its contract

Use an existing kind for a named thing unless it needs a new contract.
A type earns its place through a useful contract or identity, such as:

- Fields or a value constraint
- Reference precision or discovery
- A consumer capability
- Another distinction the task needs

**Count does not decide**

A single configuration can need a type because a loader discovers and validates it.
A hundred similar notes can share an existing contract.
A type with no instances can define an extension point or a reusable value.

[[guide::au-agent-guides:example]] gives records carrying different advice a shared contract.
[[mcp.tool.au_agent_guide::au-agent-guides:example]] defines a discoverable capability with one implementation.
Each has a reason for its type identity.

**A judgment may need its own record**

Keep a viewpoint in a field when the containing record makes its subject and perspective clear.
Its meaning must be unambiguous there.
Give the judgment a record when perspectives need independence:

- They can disagree
- They need evidence
- They have their own history

[[use-a-lens]] describes one vocabulary for that choice.

**Find what the type contributes**

Read related definitions and inspect how the intended consumer finds or checks them.
Inherit for the contract, not just a shared topic.

Remove the proposed type from the design and name the loss:

- What can no longer be expressed
- What can no longer be discovered
- What can no longer be checked

If only its title would be lost, an instance or ordinary value may do the job.
