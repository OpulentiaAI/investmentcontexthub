---
type: guide.principle
goal: "Choose whether content belongs in a whole note, an addressed part, or a separate file."
rule: "Separate content when its identity, lifecycle, ownership, or reuse warrants it; address a part in place when that is enough."
---

# Choose the boundary of a note

Keep an explanation together while its parts need the same context.
Split a part when its needs diverge:

- Independent authorship or lifecycle
- Reuse outside the containing explanation
- A reading path that the containing note obscures
- Other ownership or identity that the current boundary cannot support

Length can reveal the problem, but does not set the boundary.

**Address a part in place**

A link to a part does not require another file:

- A heading link navigates to a section
- A single-caret block link navigates within the containing file
- A double-caret link selects the addressed block or inline record itself as the referent

A typed slot checks the selected part's compatible type.
`any*` can reference an existing untyped block.
See [[three-stars-three-checks]].

**Separate ownership when needed**

Use a separate file when the part needs independent:

- Movement
- Changes
- Governance

An address inside a file gives it identity without independent file ownership.
An inline record adds structure while keeping the containing prose together.

**Weigh context against independence**

Splitting loses context.
It also adds maintenance:

- Navigation
- Names
- References

Keeping unrelated obligations together invites editing conflicts and an unclear contract.
A long coherent specification may belong together while a short record with two unrelated lifecycles needs splitting.

Use [[reshape-with-the-engine]] when extraction changes addresses or references.
Keep a link or containing explanation that shows why the pieces belong together.

Imagine editing or reusing the part independently.
Choose the address and ownership that operation needs.
If every use needs the surrounding explanation, keep that context accessible.
