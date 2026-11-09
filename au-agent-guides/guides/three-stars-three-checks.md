---
type: guide.gotcha
goal: "Choose a reference slot and address that check the intended referent."
rule: "Choose the target category first, then its address and historical behavior; a star alone does not specify the check."
example:
---

# Choose the reference's referent

Choose the reference shape for the thing the slot must accept.
A value's wikilink syntax does not tell you which check it needs.

| Shape | Intended referent |
| --- | --- |
| `T*` | An instance whose closure is compatible with T |
| `type<T>*` | A type definition compatible with T |
| `type*` | Any type definition |
| `file*` | A whole file, with no required type |
| `any*` | An addressable node without a required type |

**Read the slot's promise**

[[mcp.skill::au-mcp-sdk:example]] uses bounded definition references to identify tools.
[[source::au-base-types:example]] references original bytes as a file.
[[supersede::au-base-types:example]] accepts a successor across kinds through a broad node reference.
Inspect those slots to see why their ranges differ.

**Select the right address**

A heading or single-caret block address navigates within a file.
A double-caret address selects the block or inline record itself.

A typed slot requires a compatible type.
`any*` also accepts an existing plain block.
A file slot rejects a fragment even when its containing file exists.

**Choose live or historical behavior**

Use a pin-admitting shape for a historical coordinate.
A plain live reference does not admit a commit pin.
Pins neither follow current renames nor participate as ordinary live edges.

Compare the slot's effective shape with the referent the consumer needs.
Let the engine check category compatibility.
Probe a boundary when the shape or consumer behavior is uncertain.
Use a case that distinguishes the competing interpretations.
