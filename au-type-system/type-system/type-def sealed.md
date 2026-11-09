The `sealed:` key on a [[type-def]].

# Properties

## Discriminated union
A closed list of the type's permitted branches.
A branch is a direct crossing of this parent, a type-def claiming it through [[type-def extends]].
Makes the type a sealed parent.
List form follows [[type list form]].

The list closes the branch set, not the leaf set.
- no type-def outside the list may cross the parent, see [[#No surprise children]].
- a non-sealed branch is still a normal type, open to subtyping, see [[#Open below a branch]].

## sealed = abstract + closed
A sealed parent is non-claimable plus a closed branch set.
- the non-claimable half is [[type-def abstract]], `sealed` is the special case, abstract plus the branch list.
- a sealed type IMPLIES abstract, one non-claimable predicate covers both.
- claiming a sealed parent stays its own [[spec - diagnostic codes^sealed-parent-claimed]], the more specific message.
- an explicit `abstract: true` on a sealed type is redundant, [[spec - diagnostic codes^redundant-abstract-on-sealed]] (hint).

## Why
A sealed family is a tagged union,
each leaf a variant with its own [[type-def fields]].

You cannot express this on one type.
Fields are unconditional,
none appears for only some values.

So a discriminant that selects different field sets becomes a sealed parent,
one leaf per variant.

This allows expressing, e.g.:
```yaml
myStates: [state1, state2]
myField1: <shape> # only if myStates is state1
myField2: <shape> # only if myStates is state2
```
which does not work in a single type.

## Branch naming
Branch names follow [[type sealed naming]].

## Exhaustiveness
A [[type-instance]] claims a non-sealed leaf,
never the sealed parent directly.

Claiming the parent is a validation error:
- [[spec - diagnostic codes^sealed-parent-claimed]].

## No surprise children
A type-def crossing this parent without going through a listed branch is a load error:
- [[spec - diagnostic codes^sealed-no-surprise-children]].

The check is transitive.
- a type-def is permitted when its [[type closure]] contains a listed branch.
- a listed branch at any depth above it satisfies the rule.

## Nested sums
A listed branch may itself be sealed.
The drill-through repeats until a non-sealed leaf.

## Open below a branch
A non-sealed branch is a leaf, and stays open to subtyping.
A subtype of a branch is a new leaf of the family.

It reaches the parent only through that branch,
so [[#No surprise children]] still holds.

The closed set is the branches, not the leaves.
- no new branch can cross the parent.
- new leaves can still appear below an existing non-sealed branch.

There is no per-leaf freeze marker.
Sealing a branch closes it further, but changes its nature,
it becomes a sum parent instances cannot claim, see [[#Nested sums]].

## Reads against the parent
A read through the sealed parent sees only the parent's [[type-def fields]].
Leaf-specific fields are not lifted.

A consumer wanting a leaf field branches on the [[type-instance type]] claim.
The branch set is closed and enumerable at load, so the branching is exhaustive.

Dispatch is by branch membership, not by exact leaf identity.
- a consumer asks which listed branch the instance's [[type closure]] contains.
- this stays exhaustive when a branch is subtyped, the subtype carries its branch in its closure.
- [[type subtyping width-only]] makes the subtype's contract imply its branch's, so the read is sound.

# Structure
A closed list of branch names.

```yaml
# type/myParent.type.yaml
sealed:
  - myParent.myFirstLeaf
  - myParent.mySecondLeaf

# type/myParent.myFirstLeaf.type.yaml
extends: myParent
fields:
  myField1: <shape>

# type/myParent.mySecondLeaf.type.yaml
extends: myParent
fields:
  myField2: <shape>
```