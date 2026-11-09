The values a [[type-instance]] supplies for its [[type effective shape]].

# Properties

## Required and optional
Every required field of the [[type effective shape]] must be present.

A missing one is a validation error:
- [[spec - diagnostic codes^required-field-absent]].

Optional fields may be omitted.

## Shape conformance
Each value must match its [[type-def field shape]]:
- [[spec - diagnostic codes^field-shape-mismatch]].

## Forms
- bare, `myField: <value>`.
- prefixed, to resolve a collision, see [[type-def fields collision - auto-unify and qualified field]].
- body-contributed, for `.md` instances, see [[type-instance body contribution]].

## Extras
Fields outside the shape pass as [[type extras]].

# Structure
```yaml
type: myType          # requires myField, optional myOpt
myField: <value>      # required
myOpt: <value>        # optional, may be omitted
myExtra: <value>      # outside the shape
```
