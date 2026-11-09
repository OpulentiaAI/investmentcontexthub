The shape convention for list-bearing keys and value lists.

# Properties

## Single bare, several block
For `extends:`, `type:`, `sealed:`, and value lists such as reference lists:
- a single entry is a bare scalar.
- several entries are a block list, one per line.

An inline list for several (`type: [a, b]`) stays accepted, just non-preferred.
A linter flags it, the loader accepts it.

## fields is a map, meta is a block list
`fields:` is a mapping, keyed by field name, each value a [[type-def field shape]].
- name to shape, unique per type-def, so a map is the shape.
`meta:` is a block list of typed sub-regions, each a multi-key record.
- keyed by the record's own inner `type:`, not by a map key, so it stays a list.

## Empty forms are special
- `fields: {}` is the [[type tag]] marker, the explicit empty map.
- `meta: []` is the suppression marker, see [[type-def meta]].

These carry meaning, not a style choice.

A `fields:` written as a list is rejected.
- the sequence form is not a valid `fields:` shape, `fields:` is a map.

## Empty claim rejected
An empty list names nothing and is rejected.
- `extends: []` on a [[type-def extends]] parent claim:
  - [[spec - diagnostic codes^parent-claim-bad-shape]].
- `type: []` on a [[type-instance type]] identity claim:
  - [[spec - diagnostic codes^instance-claim-bad-shape]].

## Bare-only positions
A [[type-def meta]] sub-region's inner `type:` is bare-only.
Mixin is forbidden there:
- [[spec - diagnostic codes^meta-mixin-not-supported]].

## Closed enums stay inline
A [[type-def shape enum]] shape `[low, moderate, high]` stays inline regardless.
It is one shape token, not a stylistic list.

The one exception is a named-enum [[type-def brand]] def.
- `shape:` as a block list carries a `#:` doc per member, so the block form is meaningful there.
- the inline `shape: [low, moderate, high]` is docless sugar for the same set.

# Structure
```yaml
# single → bare
type: myType

# several → block, preferred
type:
  - myType
  - myOtherType

# several → inline, accepted but non-preferred
type: [myType, myOtherType]
```
