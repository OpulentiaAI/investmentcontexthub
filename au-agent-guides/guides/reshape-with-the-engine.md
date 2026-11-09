---
type: guide.gotcha
goal: "Change identities or locations without overlooking their references."
rule: "Use the structural mutation that matches the change, inspect its scope, and verify the affected references and consumers."
---

# Reshape through the structural mutation

Use the engine's matching structural mutation when changing identities or locations.
Supported changes include:

- File or type renames
- Block-id changes
- Promotion or inlining
- Other transformations covered by an exposed structural operation

These operations understand references that a text edit cannot reliably identify.
Read the operation's preconditions and result before applying it.

**Inspect the rewrite scope**

Read inbound references and the mounted member set.
The engine can rewrite references within its supported indexed scope.
Unmounted consumers and arbitrary strings in code may need separate work.
Commit pins retain historical coordinates and are not rewritten as live links.

**Read the reported outcome**

A structural change across repositories runs as a saga with commits in the affected repositories.
It does not produce one globally atomic git commit.
Inspect the outcome after interruption or compensation before choosing another mutation.

Use a preview when the API offers one.
After the mutation, follow representative targets.
Inspect scoped diagnostics.
Exercise consumers that use names outside the typed graph.
Engine readiness does not establish preserved behavior.

**Handle refused or unsupported changes**

Read the specific precondition behind a refusal.
An unsupported transformation may still need a reference-aware migration.
Use an authorized explicit migration with checks for references the native operation cannot cover.

Account for each kind of use:

- Live typed references
- Navigation
- Code consumers
- Historical pins

Check that reported edits match the intended scope and each remaining consumer has a valid target.
