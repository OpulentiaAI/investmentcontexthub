A slot-level union or intersection.
One of the [[type-def field shape]].

# Properties

## Operators
- `<X | Y>` is a union, a value satisfies X or Y.
- `<X & Y>` is an intersection, a value satisfies both.

## Not a type
A compound is a slot constraint, not a new type in the graph.

For a queryable named union,
- name the union with a [[type-def brand]], `shape: <A | B>`, a discriminated set reused by name.
- or seal a parent ([[type-def sealed]]) for a discriminated family instances claim.

For a queryable named intersection,
use a [[type-def]] with multiple parents.

## Subsumption
A redundant branch is a load warning.
- union, the wider branch subsumes the narrower:
  - [[spec - diagnostic codes^subsumption-in-slot-union]].
- intersection, it collapses to the narrower branch:
  - [[spec - diagnostic codes^subsumption-in-slot-intersection]].

## Uninhabitability
An intersection that looks uninhabitable is never checked.
Not at slot-declaration, not at instance time.

The cases that look uninhabitable usually aren't:
- same-named fields with differing shapes, resolved by the field qualifier.
  - see [[type-def fields collision - auto-unify and qualified field]].
- two disjoint sealed families, inhabited by a cross-family mixin.
  - `type: [familyA.leaf, familyB.leaf]`, see [[type-instance type]].

A genuinely uninhabitable slot needs no special check.
Regular instance validation catches it at the use site.
- a missing required field, or a shape mismatch.
- see [[type validation]].

## Disambiguation
A union branch is chosen by a discriminator.
- `<String | Url>` by the `^https?://` prefix.
- `<String | myType*>` by the wikilink `[[...]]` pattern.
- `<myTypeA | myTypeB>` by the inline record's `type:`.
- `<String | myMeter>` by the `Name(...)` constructor, a nominal [[type-def brand]] member, see [[type brand constructor]].

## Per-branch suffix
Each operand may carry its own [[type-def shape suffixes]] reference suffix.
- `<String | myType*>`, `*` on the `myType` branch alone.
- `<myA& | myB>`, `&` on the `myA` branch alone.

Distinct from a suffix on the whole compound.
- whole-compound `<myA | myB>&` requires every branch reference-able.
- a per-branch suffix does not, `<myA& | myB>` inlines `myB` only.

Write the intersection operator space-delimited.
- `<myA & myB>` is the operator, an intersection.
- `<myA& | myB>` is the `&` suffix on `myA`, the suffix hugs its base.

# Structure
Operands grouped in `<>`, joined by `|` or `&`.

The `<>` let a [[type-def shape suffixes]] attach to the whole compound.

```yaml
fields:
  myUnion: <myTypeA | myTypeB>
  myIntersection: <myTypeA & myTypeB>
  myList: <myTypeA | myTypeB>[]
```

