The `body:` key on a [[type-def]].

# Properties

## Authoring template
Defines an ordered template for a [[type-instance]]'s markdown prose.

Position is semantic,
items render in declared order.

## Markdown only
A non-empty `body:` forces instances to be `.md`.

A yaml-only instance fails validation:
- [[spec - diagnostic codes^body-required-but-yaml-only-instance]].

## No inheritance
A type-def has a body only if it declares one.

Composition is explicit,
through [[type-def body use]].

## Body-only type
A type-def with only a body is allowed,
acting as a prose template others claim.

# Structure
A list of body items, each optional:
- [[type-def body section]]
  - a named heading in the template.
- [[type-def body use]]
  - splices another type-def's body in at this position.
- [[type-def body fills]]
  - a contract: the scope must contribute to named field(s).

```yaml
extends:
  - myParentType # which has myField and a body
body:
  - use: myParentType # splice in body defined by myParentType
  - section: My Section
    fills: myField
```
