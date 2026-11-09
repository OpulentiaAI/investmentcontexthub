Field values a [[type-instance]] carries outside its [[type effective shape]].

# Properties

## Sources
- a top-level frontmatter key.
- an inline `` `[:field]` `` or `[[link:field]]`
  - [[type-instance body contribution]].

## Pass validation
Extras do not fail the file.
[[type open-world validation]] is the spec.

The inline-prose case stays advisory:
- [[spec - diagnostic codes^unknown-field-in-prose-contribution]].

## Advisory
Surfaced as advisory output, a squiggle or a suggestion, never an error.

## Candidate source
An extra may complete a type the file could claim.
Surfaced by the [[type candidate scan]].

# Structure
```markdown
---
type: myType        # declares myField
myField: <value>    # in the effective shape
myExtra: <value>    # a frontmatter extra
---

`[:myProseExtra] <value>`   # an inline body extra
```

