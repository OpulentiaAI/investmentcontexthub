A set of types plus all their transitive ancestors.
Walked over [[type-def extends]] parent links.

# Properties

## The walk
From a set of starting types,
follow every [[type-def extends]] parent.
Collect them and every ancestor reached.

A type may declare several parents,
so one starting type already fans into a tree.

## Starting types
- a [[type-def]] starts from itself
  - may have multiple parents
- a [[type-instance]] starts from its [[type-instance type]] claims.
  - a mixin claims several types at once.

The closure is the deduped union across all of them.
A forest, not one chain.

## Termination
The parent graph is acyclic.

A cycle is a load error:
- [[spec - diagnostic codes^cycle-in-type-chain]].

A depth bound guards the walk regardless.
Exceeding it is a load error:
- [[spec - diagnostic codes^type-chain-depth-exceeded]].
- a pathologically deep chain, or a cycle that slipped past cycle detection.

A diamond dedupes,
each ancestor is visited once.

## Uses
- the [[type effective shape]]
  - the fields declared across the closure.
- sealed-family reachability
  - see [[type-def sealed]].
- prefix resolution
  - see [[type-def fields collision - auto-unify and qualified field]].

## Cross-repo
A `foo::repo` parent folds the peer's closure into the walk, see [[cross repo typed graph]].
- a cross-repo `extends:` cycle is diagnosed like the single-repo case, [[spec - diagnostic codes^cycle-in-type-chain]].

# Structure
A type-def, with several parents that share an ancestor:
```yaml
# type/myBase.type.yaml
fields:
  myBaseField: String

# type/myParentA.type.yaml
extends: myBase
fields:
  myFieldA: String

# type/myParentB.type.yaml
extends: myBase
fields:
  myFieldB: String

# type/myType.type.yaml
extends:                 # two parents
  - myParentA
  - myParentB
fields:
  myOwnField: String
```
Closure of `myType`: `myType, myParentA, myParentB, myBase`.
`myBase` is reached twice but visited once.

An instance, unioning unrelated claims:
```yaml
# type/myUnrelated.type.yaml
fields:
  myUnrelatedField: String

# instance
type:
  - myType
  - myUnrelated
```
Closure: `myType, myParentA, myParentB, myBase, myUnrelated`.
