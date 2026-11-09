The `abstract:` key on a [[type-def]].
A marker making the type non-claimable but open to any subtype.

# Properties

## The marker
- `abstract: true` marks the type-def non-claimable.
- `abstract: false`, or the key absent, is concrete, the default.
- a non-boolean value is a load error:
  - [[spec - diagnostic codes^abstract-marker-bad-shape]].
- a type-def-only key, on an instance it is [[spec - diagnostic codes^reserved-key-on-instance]], like `fields:` / `sealed:` / `meta:`.

## Non-claimable
A [[type-instance type]] claim naming an abstract type is an error:
- [[spec - diagnostic codes^abstract-type-claimed]].

Per-claim, an abstract element inside a mixin fires it, a concrete sibling does not excuse it.
- the parallel of [[spec - diagnostic codes^sealed-parent-claimed]].
An inline record ([[type-def shape record]]) claiming an abstract type directly fires it too.
A slot-pinned inline record at an abstract ceiling MUST carry an explicit concrete `type:`.
- the "requires explicit `type:`" gate is keyed on NON-CLAIMABLE, sealed or abstract.
The [[type candidate scan]] never surfaces an abstract type, a claim on it is impossible.

## Open
Any type-def may extend an abstract parent, there is no branch list.
This is the difference from [[type-def sealed]], which closes the crossing set to its listed branches.

## Not inherited
A per-def property, never inherited.
- a subtype of an abstract type is CONCRETE, unless it also declares `abstract: true`.
- an inherited abstract would make every descendant abstract, so nothing could ever be instantiated.
- mirrors [[type-def sealed]], a sealed parent's leaves are not sealed unless they declare it.

## Parent-side uses stay allowed
- an `extends:` claim ([[type-def extends]]), the point, fields / body / meta flow to concrete subtypes.
- a slot ceiling, `abstractType*`, a concrete subtype in the target's closure satisfies it ([[type reference]]).
- a def-ref ceiling, `type<abstractType>*` ([[type-def shape def-ref]]).

## sealed = abstract + closed
`sealed` means non-claimable plus a closed branch set.
- `abstract` names the non-claimable half.
- a sealed type IMPLIES abstract, one non-claimable predicate, "declared abstract OR sealed".
- an explicit `abstract: true` on a sealed type is redundant, [[spec - diagnostic codes^redundant-abstract-on-sealed]] (hint).
See [[type-def sealed]].

## No concrete descendant is legitimate
An abstract type with no non-abstract descendant is a normal, stable state, never a defect.
- a cross-repo abstract interface defined for OTHER repos to extend, or for future extension.
- the engine emits NO diagnostic, the open-world stance of [[type open-world validation]].

## Identity
Abstractness folds into the type's `(name, ClosureHash)` identity.
- it removes the type itself as a direct claim, contract-shaped like `sealed`.
- folded ONLY WHEN DECLARED, a plain concrete type's canonical form is unchanged, so existing identities do not rotate.
- two same-named defs, one abstract and one not, are DIFFERENT identities, see [[cross repo typed graph]].

## The exemption handle
"Non-abstract descendant" is exactly the concrete, instance-claimable set.
- the clean exemption for [[type-def required meta]], whose obligation is on concrete subtypes only.

# Structure
```yaml
# type/myBase.type.yaml
abstract: true
fields:
  myField: <shape>

# type/myBase.myLeaf.type.yaml   — concrete, claimable
extends: myBase
```
