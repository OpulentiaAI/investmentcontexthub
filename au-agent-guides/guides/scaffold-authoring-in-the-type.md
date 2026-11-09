---
type: guide.pattern
goal: "Choose body templates and field contributions for authored records."
rule: "Use a template for recurring meaningful structure, and place a field's value where it is best authored without duplicating it."
example:
---

# Let the type support its author

Use a body template when recurring sections make instances easier to author or inspect.
Use free prose when the explanation needs to vary between instances.

[[guide.pattern::au-agent-guides:example]] offers an optional skeleton.
[[guide::au-agent-guides:example]] allows a free body.
Choose the one that fits the content.

**Author a value where it belongs**

Author a typed field through a contribution its slot permits:

- Frontmatter
- An inline contribution
- A contributing link
- A fence

Contribute a reference from the sentence explaining it when that makes authorship clearer.
Keep the required frontmatter anchor and inspect resolved values instead of maintaining a duplicate.

**Let the slot interpret the fence**

- A String or any slot keeps fence content as text
- A record-only slot parses structured content
- A slot admitting both uses a mapping with explicit `type:` as a record and other content as text

A `fills` obligation checks whether a field received a contribution in the relevant section.
It does not route an ordinary value into that field.

**Compose the body explicitly**

A subtype does not automatically inherit its parent's body template.
Use the supported `use` mechanism for composition and inspect the effective template.
Match the template's requirements:

- Section names
- Order
- Heading depth

Guidance kept with a type is easier to find, but can still become wrong.
Use a skill when the work requires decisions or operations beyond filling the body.

Author a representative instance and inspect its resolved values and section diagnostics.
Each obligation should call for meaningful content.
Each value should have a clear authorship path.
