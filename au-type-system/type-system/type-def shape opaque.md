The built-in uninterpreted slot, an inline value the type system stores but never reads.
One of the [[type-def field shape]].

It imposes no shape constraint, and the engine interprets nothing.
The uninterpreted sibling of [[type-def shape any]], which is the interpreted top.

# Properties

## Uninterpreted
An `opaque` value is stored faithfully and the type system reads nothing inside it.
- it is for a slot holding data the engine must NOT interpret, a captured payload, a foreign document, free text.
- the shape is unconstrained, like [[type-def shape any]], but the interpretation is OFF, unlike `any`.

The distinction is the whole point of the split.
- `any` is the top type ⊤, unconstrained but interpreted.
- `opaque` is unconstrained and uninterpreted.
- one keyword per concept, so an author picks the one they mean.

## The four interpretations, off
A typed slot performs four interpretations on a value.
An `opaque` slot suppresses each:
- shape conformance is trivially satisfied, any object or array or scalar passes.
  - no [[spec - diagnostic codes^field-shape-mismatch]].
- it is NOT parsed as a record, a nested `type:` is plain data, never an inline claim.
  - see [[type-def shape record]].
- it is NOT scanned for candidate types.
  - see [[type candidate scan]].
- it is NOT scanned for `[[wikilinks]]`, so its content forms no edge and a rename never rewrites it.
  - see [[type reference]].

### Known limitation, the wikilink suppression is not yet wired
The fourth suppression, the wikilink one, is the INTENT and not yet implemented.
- a `[[...]]` inside an `opaque` value currently STILL forms a backlink edge, and a rename STILL rewrites it.
- the first three suppressions hold, only the edge one is pending.
- the backlink index is shape-blind by design, so suppressing an opaque field's edge is a bounded engine change, tracked separately.

This is a temporary limitation, intended to be fixed.
- an author relying on opacity should not yet place a `[[...]]` in an `opaque` field expecting it to stay inert.

## Inline-only, no reference form
`opaque` has no `*` or `&` form.
- a reference is a pointer the engine follows, so it is interpreted by definition, which contradicts opacity.
- the interpreted top-type reference is [[type-def shape any]] `any*` / `any&`, use that where a reference is wanted.
- an `opaque*` or `opaque&` slot is a shape error, [[spec - diagnostic codes^shape-syntax-error]].

The list form is valid, each element opaque.
- `opaque[]`, `opaque[+]`, a list of uninterpreted values.
- a list is still inline content, so opacity is preserved per element.

## A body fence at an `opaque` slot reads verbatim
The rule holds on the body surface too.
- a marked fence reading an `opaque` slot is captured as authored, never yaml-parsed into a record.
- the value is exactly the content lines, no trimming, no folding.
- contrast [[type-def shape any]], whose fence reads by value-shape, a mapping becoming a record.
- see [[type-instance body contribution]].

## Reserved name
`opaque` is reserved.
- it joins `file`, `any`, and the primitives, a user [[type-def]] cannot claim it.
- [[spec - diagnostic codes^reserved-type-name]].

## Where the old inline `any` opacity moved
Inline `any` once meant uninterpreted.
- that opacity is now `opaque`, done right, including the wikilink suppression `any` never actually honored.
- `any` is now the interpreted top, see [[type-def shape any]].
- a slot that held opaque data as `any` is authored as `opaque`.

# Structure
```yaml
fields:
  captured: opaque      # an uninterpreted inline subtree
  payload: opaque       # a foreign document the engine never reads
  log: opaque[]         # a list of uninterpreted values
```

A body fence filling an `opaque` slot, captured as authored:
````markdown
```[:captured]
type: not read as a claim, the slot imposes no interpretation
key: not read as a mapping either
```
````
