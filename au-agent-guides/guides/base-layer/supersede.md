---
type: guide.gotcha
goal: "Replace a note while preserving the identity or reasoning of its previous state."
rule: "Supersede when the old state must remain independently addressable; edit in place when version history is enough."
about: "[[supersede::au-base-types]]"
---

# Choose when to supersede

Use [[supersede::au-base-types]] when an old state must remain independently addressable as a node.
Edit in place when git history supplies the historical access the task needs.

**Give the successor a meaningful identity**

A concrete domain kind can extend the abstract trait.
Its optional superseded_by field points to a successor.
The trait alone cannot be claimed directly.

Choose a distinct successor when the old state must remain independently addressable as a node for:

- An argument
- An evidence set
- A published identity
- Another old state that must remain independently addressable

It can correct an error as well as improve wording.

**Interpret the chain explicitly**

Existing inbound links still reach the old note.
The engine neither redirects them nor follows the successor chain automatically.
A reader or consumer must interpret the relation.

To find the current version, query within the intended versioned family and check the chain.
A missing successor field alone does not make every node current.

**Review each carried relation**

Keep the relations the successor still supports.
Copying every link can preserve the error it corrects.

The broad target range permits successors across kinds.
Check what the range cannot establish:

- The relationship's meaning
- Freedom from cycles
- The intended endpoint

Use the consumer or editorial process for those checks.

Retiring without a successor is a different lifecycle.
Merging duplicate identities needs a deliberate reference migration.
An alias field does not redirect links automatically.

Follow an existing inbound link and the successor chain.
The reader should be able to identify:

- The old state
- Why it was replaced
- The usable successor named by the relation
