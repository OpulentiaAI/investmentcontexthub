The required `type:` key on a [[type-instance]].

# Properties

## Identity claim
Names which [[type-def]]s the file IS.

Determines the [[type effective shape]].

## Mixin
Several claims merge into one identity.

## Cross-repo claim
A claim may name a peer's type, `type: foo::repo`.
- the peer's type folds in, its fields join this file's [[type effective shape]].
- see [[type repo qualifier]] and [[cross repo typed graph]].

## One leaf per sealed family
A sealed family is a discriminated union.
One file cannot be two sibling leaves at once.

The deduped claim may name at most one leaf per sealed family:
- [[spec - diagnostic codes^multi-leaf-in-sealed-family]].

Leaves of different families combine freely.
The rule is per-family, not global.
A cross-family mixin is the way to inhabit an intersection of two sealed families.
See [[type-def shape compound]].

Applies the same to an inline-value identity claim.
See [[type-def shape record]].

Diagnostic emission:
- one diagnostic per violated family.
- a claim buckets under every sealed ancestor in its closure.
- nested sums with an identical offending leaf set fire innermost-only, the outer is suppressed.
- a strict-superset outer set fires independently, a distinct violation level.

```yaml
# myParent sealed; leaf myParent.myMid is itself sealed into .leafA / .leafB

type: [myParent.myMid.leafA, myParent.myMid.leafB]
# one diagnostic, at myParent.myMid; myParent's bucket matches, suppressed

type: [myParent.myOther, myParent.myMid.leafA, myParent.myMid.leafB]
# two diagnostics, at myParent (three leaves) and myParent.myMid (two); sets differ
```

## Traits
There is currently no special way to distinguish between
- `is-a` type
- `has-a` type

Users can consider using a custom [[type-def meta]] to mark traits.

## Constraints
The key is required.
An instance with frontmatter but no `type:` is an error:
- [[spec - diagnostic codes^missing-type-claim]].
- a direct `parse_instance` caller sees it.
- the engine's build treats a no-`type:` markdown file as a plain note.

A list-form claim must name at least one type.
`type: []` is rejected:
- [[spec - diagnostic codes^instance-claim-bad-shape]].

A claim naming a type absent from the graph is a validation error:
- [[spec - diagnostic codes^unknown-type-claim]].

A [[type-def sealed]] parent claimed directly is a validation error:
- [[spec - diagnostic codes^sealed-parent-claimed]].

A [[type-def abstract]] type claimed directly is a validation error:
- [[spec - diagnostic codes^abstract-type-claimed]].
- per-claim, an abstract element in a mixin fires it, a concrete sibling does not excuse it.

## Redundant claims
A repeated or implied claim is a warning, not an error.
The [[type closure]] dedupes either way.
- a literal duplicate, `type: [a, a]`:
  - [[spec - diagnostic codes^duplicate-claim]].
- a subsumed claim, where one claim's closure includes another:
  - [[spec - diagnostic codes^subsumption-in-mixin]].

## Distinction from the parent claim
`type:` is the identity claim, at every position.
- an instance root, an inline record, a meta sub-region, a body typed fence.
- it names what a file or value IS.

The parent claim is a separate key, `extends:`, on a [[type-def]] only.
- it names what a type-def extends, see [[type-def extends]].
- so the two are told apart by keyword, never by which file they sit in.

# Structure
One type, or several.
- single: `type: myType`
- mixin:

```yaml
type:
  - myType
  - myOtherType
```

Form follows [[type list form]].
