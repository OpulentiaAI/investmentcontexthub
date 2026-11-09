---
type: guide.gotcha
goal: "Require a referenced target to have a particular state or capability."
rule: "Use a target type for an engine-checked reference guard, and place the field where its range is shared by all descendants."
---

# Guard a reference by the target's type

Use a target type when the graph contract must check a referenced state or capability.
A typed reference checks the target's type closure.
It cannot express a predicate such as “the target's status field equals approved.”

**Choose where the check belongs**

A state branch or mixed-in capability can supply the type identity.
[[modeling-discrete-states]] covers that choice.
Keep state as an ordinary value when a consumer predicate is the appropriate check.

**Put the field where its range holds**

Declare the field on the base when every descendant accepts the same target range.
Declare it on the relevant branches when their ranges differ.
Width-only inheritance prevents a child from narrowing or otherwise redeclaring the inherited field.
Qualifying a collision does not relax that rule.

**A diagnostic leaves the action to its consumer**

A target outside the required closure produces a type-mismatch diagnostic.
The engine can still save the file and resolve the link.
The diagnostic does not reject a workflow transition or undo its side effects.

A consumer promising a hard guard must check at the action boundary and handle concurrent target changes.
It must also check any inverse obligation.
An “answered” state alone cannot establish that an answer record exists.

Change a representative target out of the accepted state and inspect the referrer's diagnostics.
Then exercise the action that relies on the guard.
Check its refusal or recovery separately from the graph diagnostic.
