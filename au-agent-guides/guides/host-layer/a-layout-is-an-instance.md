---
type: guide.gotcha
goal: "Choose where a saved host arrangement and temporary view state belong."
rule: "Persist the arrangement as a composition of windows and referenced records; keep machine-specific and transient state at their own layer."
about: "[[composition::au-host-sdk]]"
example:
---

# Persist the composition as typed data

Save a host arrangement as a [[composition::au-host-sdk:example]] instance.
Composition is its own branch of the mountable family.
Even one visible view uses a composition and a window.

**Arrange references over stable records**

The composition names windows and owns a flat pool of mountable records.
Windows reference content.
Containers reference children through declared slots.

Reparenting changes those references while the child keeps its identity.
Copying a child's old configuration into a parent can overwrite independent changes or disconnect the real record.
Use the host's structural and configuration operations for a live arrangement.

**Separate saved configuration from view state**

Persist configuration that should travel with the composition.
Machine-local view state can hold:

- Window geometry
- Cursor position or scroll
- Temporary selection
- Other state specific to the machine or current view

A layout API and a typed saved document serve complementary parts of the system.

Use [[author-a-composition]] for authoring and [[shape-a-projection]] for a mounted view's responsibilities.

Reopen the saved composition and check that its windows and intended content return.
Move a pane and check that its identity and configuration survive without a duplicate pool record.
