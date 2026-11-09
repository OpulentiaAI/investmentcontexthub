One value a [[type-instance]] holds for a field,
plus every contribution that produced it.

# Properties

## A field holds a list
A field's effective value is a list of value containers.

Cardinality applies to the list:
- bare `T`, exactly one.
- `T[]`, zero or more.
- `T[+]`, one or more.

A bare field with two distinct values is an error:
- [[spec - diagnostic codes^field-cardinality-exceeded]].

An authored list yields ONE container PER ELEMENT.
- `[a, b]` is two values, not one value that is a list.
- so the cardinality table above counts containers, and `T[+]` is checkable here.
- every list, whatever its element type, references and primitives and records alike.

An authored EMPTY list keeps the field with ZERO containers.
- distinct from a field that was never authored, which has no entry at all.
- `T[]` admits it, `T[+]` does not, and both are decidable from the container count.

## Contributions
Each container carries the contributions that produced its value.

A contribution is one surface occurrence:
- frontmatter.
- [[type-instance body contribution]]
  - body wikilink
  - body inline code
  - body fence

Each records its location and surrounding prose.

## Section path
Only a body contribution carries one.
The chain of [[type-def body section]]s enclosing it, root-to-leaf.

- the body preamble, before any section, has the empty path.
- each entry is `"<1-based-index-on-its-level> <full exact section name>"`.
- the index is always present, it disambiguates same-name siblings.
  - a section literally named `1 Why` appears as `1 1 Why`, the index then the name.

## Equality collapses
Contributions with equal values share one container.
- references, the same target and fragment.
- primitives and inline records, structurally equal.

The same value in frontmatter and body is one container,
two contributions.
It does not count twice against cardinality.

Collapse merges CONTRIBUTIONS to one value slot.
It never merges two distinct slots.

Two elements of one authored sequence are two slots, and never collapse.
- `[a, a]` is two containers, not one carrying two contributions.
- a list is not a set, and collapsing would lose order: `[a, b, a]` would report `a, b`.

A contribution carrying no POSITION collapses into the first container with an equal value.
- a prose mention says nothing about which slot it corroborates.
- so where several slots hold that value the choice is arbitrary, and first is chosen for determinism.
- a deterministic tie-break, not a semantic claim.

An inline record's `^:` id is excluded from equality.
- the id addresses the contribution site, it is not part of the value.
- structurally-equal records with different ids still collapse.
- see [[type block-id]].

A branded value resolves to its underlying representation, the written brand riding beside it.
- `42` and its constructor `meter(42)` are the same value, one container, see [[type brand constructor]].
- the constructor name is a surface annotation, excluded from equality, like the `^:` id, so a branded value never double-counts across the frontmatter and body surfaces.
- the container carries a `brand` side-channel, the brand name written, the discriminator at a union brand, absent for a bare value or a reserved-primitive escape.
- a tuple resolves recursively, its elements each a resolved value with their own brand plus the tuple's, a tuple being one container, see [[type brand constructor]].

## Reference-ness is decided by the slot
A container is a reference when its SLOT admits one and the value is exactly one `[[...]]`.
- [[type reference]]'s validated-reference rule, applied on every surface.
- frontmatter and body alike, so one target named on both collapses rather than counting twice.

It is never inferred from contribution syntax.
- a `[[x:field]]` in prose is not a reference because of its shape, only because of its slot.
- with no slot known, an unresolved claim, the value stays a plain scalar on both surfaces.
- the navigational edge survives regardless, see [[type reference]].

## Ordering
Containers order by their earliest contribution.

Within a container,
frontmatter first,
then body in document order.

# Structure

One container for `myRef`: value `myTarget`,
two contributions.

```yaml
# myType.type.yaml
myRef: file*  # Single T*
```

```markdown
---
type: myType            # myRef is a bare reference
myRef: "[[myTarget]]"   # a frontmatter contribution
---

Also discussed in [[myTarget:myRef]].   # a body contribution, same value
```
