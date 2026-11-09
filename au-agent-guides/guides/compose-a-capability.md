---
type: guide
goal: compose mechanisms into a capability whose behavior, ownership, and verification fit together
rule: Start from observable obligations, give each an owner and a compatible operation, and check how the complete path becomes usable and proves its result.
---

# Compose a capability

Start with the behavior the user needs, including what happens when input is invalid or incomplete.
Add a mechanism only when it has a job in that behavior.

Reuse an existing operation or concise change note when it explains the whole path.
Write a separate architecture explanation when consequential interactions need to survive review and revision.

**Give each obligation an owner**

Follow each producer's output into the next consumer's input.
Check for steps left without an owner between otherwise sound components.
Keep each fact's authoritative record and write authority clear when copies cross that boundary.

Use [[pick-the-vehicle]] and the mechanism's owning contract.
Use [[modeling-composition]] for a part's identity or ownership.
One mechanism can fulfill several obligations.

**Check what the operation can do**

Suppose an extraction operation may write only its output.
If it reads and copies existing source locators, a locator field in its profile may suffice.
If the locator requires a source edit, that field supplies neither the missing operation nor permission to perform it.

For a read-only source, find a compatible way to obtain the locator or name the missing integration and its owner.
An extensible data contract does not promise arbitrary new effects.

**Trace how the consumer reaches it**

Check how the intended caller obtains and invokes the capability.
An audit needs an invocation path.
Naming the records it checks does not schedule it.

A discoverable skill still needs delivery and invocation.
[[a-skill-is-launch-static]] explains which representations may need refreshing.
Include migration or recovery when existing content or interrupted work crosses the new boundary.

**Match evidence to the promise**

Check consequential interactions that existing component evidence does not establish.
Choose a successful or failing case that could expose the gap.
Reuse current evidence for unchanged paths.

Diagnostics establish shape.
A prevention claim needs observed refusal through the controlled path.
A semantic check needs a plausible wrong example that the shape accepts.

Check availability through the actual consumer.
For historical evidence, demonstrate retrieval.
Keep expected outcomes separate from observations, as [[what-rots-silently]] explains.

**Keep unresolved work visible**

Name the unmet obligation and what would resolve it.
State which useful work can proceed.
Keep the original requirement visible when a prerequisite supplies only part of it.

An architectural dependency can change what must be built.
An implementation test checks whether the chosen design works.
