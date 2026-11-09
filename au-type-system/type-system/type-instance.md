A file that claims one or more [[type-def]]s,
and supplies their [[type-def fields]] values.

# Properties

## File
May be `.md` with yaml preface and a prose body,
or plain `.yaml`.

A claimed [[type-def]] with a [[type-def body]] forces `.md`.

## Identity
Claims its types through [[type-instance type]].

The claims plus all ancestors give the [[type effective shape]].

## Validation
Validated against its [[type effective shape]].

[[type open-world validation]] allows extras.

The passes and their order are [[type validation]].
A writer must respect the [[type write model]].

# Structure
An instance carries:
- [[type-instance type]]
  - the required identity claim, which types this file IS.
- fields from the [[type effective shape]]
  - the required ones, plus any optional ones it fills.
- [[type extras]]
  - fields outside the shape, kept as advisory.

For `.md` files,
fields can be filled
- in the frontmatter
- via [[type-instance body contribution]]

```yaml
---
type: myType
myField: <value>   # defined in myType or its ancestors
myExtra: <value>   # outside the shape, kept as an extra
---
<!-- Potentially contributions through body prose  -->
```
