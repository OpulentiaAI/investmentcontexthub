Modifiers that attach to a base [[type-def field shape]].

# Properties

## The suffixes
- `*` reference
  - to a file or typed block whose `type:` closure includes the named type.
  - the value form and resolution are [[type reference]].
- `&` inline-or-reference
  - the value is an inline record or a [[type reference]].
- `[]` list
  - of values matching the inner shape.
- `[+]` non-empty list
  - rejects an empty list:
  - [[spec - diagnostic codes^field-shape-mismatch]].
- `[x..y]` range cardinality list
  - enforces length bounds
  - see [[type-def shape refinement]].
- `{}` value refinement
  - narrows a scalar base to a smaller value region.
  - see [[type-def shape refinement]]

## Reference suffix targets
`*` and `&` attach only to a [[type-def]] name, or a compound of type-def names.

Not to a [[type-def shape primitive]] or [[type-def shape enum]]:
- [[spec - diagnostic codes^shape-syntax-error]].

The built-in [[type-def shape file]] takes `*` only.

The built-in [[type-def shape def-ref]] `type<T>*` bakes the `*` into its keyword form.
- it is `*`-only, no bare `type<T>`, no `type<T>&`.
- the bound `T` takes a compound of type-def names, the union goes inside the brackets.

## The `@` pin-enforcement postfix
`@` attaches only to a `*` reference suffix, and demands a commit-pinned value.
- `myType*@`, a typed reference that must be pinned, `[[file::@commit]]`.
- `file*@`, a file-ref that must be pinned, the deletion-stable touched-file case.
- `any*@`, any node, pinned.
- `myType&@` is ILLEGAL, `@` requires `*`. A `&` inline branch cannot pin, so `&@` is a contradiction. Express "inline or pinned reference" as the union `< myType& | myType*@ >`.

A pin is legal only where the slot's shape ADMITS one.
- a `*@` shape, or a `*@` branch of a union, admits a pin.
- a plain `T*` / `T&` slot does NOT, a pinned value there is [[spec - diagnostic codes^unexpected-commit-pin]].
- an unpinned value in a `*@` slot is [[spec - diagnostic codes^value-not-pinned]].
- the postfix guarantees the pin is present, not that the producer chose the right commit.

The `@` does double duty, one concept in two positions.
- value fragment `[[file::@commit]]`, pinned at this commit, see [[type reference]].
- shape postfix `T*@`, must be pinned.
- shapes live in `.type.yaml`, fragments in instance values.

The value form and resolution:
- a pinned value is an inert snapshot, its past immutable, forming no live edge.
- `file*@` / `any*@` pin a whole file, `T*@` also pins a typed reference.
- a pin does not drift and is not re-resolved, a fixed past cannot diverge.

## The pinning axis
Complete, over the reference base and the union.
- `T*`, must NOT be pinned, a live reference. A pinned value is [[spec - diagnostic codes^unexpected-commit-pin]].
- `T*@`, must be pinned, an inert snapshot.
- `< T* | T*@ >`, either, the explicit union for a slot that accepts both.

No separate must-not-pin postfix is needed.
- `T*` already IS the must-not-pin slot, so the earlier `T*~` candidate is subsumed.
- pinned-ness is a property of the SHAPE, so a default slot is unambiguous, and mixing is opt-in via the union.
- see the decision that a git pin attaches only to a star reference, mixed slots need an explicit union.

## List suffix targets
`[]` and `[+]` attach to any inner shape.
For its bounded forms `T[x..y]` / `T[n]`,
see [[type-def shape refinement]].

## Order
Value refinement `{...}` first, then reference suffix, then `@` pin-enforcement, list suffix last.

- `myType*[]` is a list of references.
- `myType*@` is a must-be-pinned reference.
- `myType*@[]` is a list of must-be-pinned references.

# Structure
A base shape,
an optional value refinement `{}`,
an optional reference suffix `*`/`&`,
an optional `@` pin-enforcement,
an optional list suffix `[]`/`[+]`/`[x..y]`.

```yaml
fields:
  myRef: myType*
  myInlineOrRef: myType&
  myList: String[]
  myNonEmpty: myType[+]
  my5ElementList: myType[5]
  myRefList: myType*[]
  myPinnedRef: myType*@
  myPinnedFile: file*@
  myPinnedRefList: myType*@[]
  myIntegerList: Number{integer}[]
  myIntegerListMax10Elements: Number{integer}[..10]
```
