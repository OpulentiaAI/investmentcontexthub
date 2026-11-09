The built-in top type, an unconstrained but interpreted slot.
One of the [[type-def field shape]].

It imposes no shape constraint.
The engine still interprets the value.

# Properties

## The top type
`any` is the top ⊤, every value conforms.
- it imposes no shape constraint, so shape conformance is trivially satisfied.
- but the engine INTERPRETS the value, unlike [[type-def shape opaque]].
- so it is the honest top, "a value of any shape", not "an uninterpreted blob".

The uninterpreted case is a separate shape.
- reach for [[type-def shape opaque]] where the slot holds data the type system must NOT read.
- reach for `any` where the value's shape is genuinely unconstrained but real.

## Inline `any` is interpreted
A value in a bare `any` slot conforms trivially, and the engine reads it like any other value:
- shape conformance is trivially satisfied, any object or array or scalar passes.
  - no [[spec - diagnostic codes^field-shape-mismatch]].
- a nested `type:` IS parsed as an inline claim, record-parsed.
  - see [[type-def shape record]].
- a `[[wikilink]]` inside IS scanned, a real navigational or validated edge.
  - see [[type reference]].
- candidate types ARE scanned.
  - see [[type candidate scan]].

So the four interpretations that a typed slot performs all stay ON.
`any` only drops the shape CONSTRAINT, never the interpretation.

## Forms
Follows [[type-def shape suffixes]], every inline and reference form valid:
- `any`
  - an interpreted inline value of any shape.
- `any*`
  - a reference to any node, with no closure check.
- `any&`
  - inline-or-reference, an interpreted inline value or a top-type reference.
- `any[]` / `any*[]` / `any[+]`
  - lists of the above.

[[type-def shape opaque]] has NO reference form.
- a reference is a pointer the engine follows, so it is interpreted by definition.
- the uninterpreted idea is inline-only, and lives in `opaque`.
- so `any` keeps the full suffix grammar, `opaque` is bare-or-list only.

## `any*` is a top-type reference
- it resolves a `[[...]]` like any [[type reference]], a real navigational and validated edge.
- existence is still checked, a missing target fires [[spec - diagnostic codes^reference-target-missing]].
- it applies no closure constraint, any existing node satisfies it.
- it addresses a node, a whole file, or a typed block or an addressable inline record via the block-referent `^^block-id`.
- so `any*` is a superset of [[type-def shape file]] `file*`, which is whole-file-only.

## `any&` is inline-or-reference
Reuses the [[type-def shape suffixes]] `&` disambiguation.
- a whole-value `[[...]]` selects the reference branch, resolved as `any*`.
- any other value is the inline branch, the interpreted top.

Both branches interpret.
- the inline branch is the interpreted top, its own `[[...]]`s are real edges.
- the reference branch is a real edge.
- the `&` chooses which, it does not toggle interpretation.

## A body fence at an `any` slot reads by value-shape
The rule holds on the body surface too, and the interpreted top has no single content-form.
- so a marked fence reads by the value's SHAPE, see [[type-instance body contribution]].
- a mapping reads as a record, interpreted, a nested `type:` is a claim.
- anything else keeps its text.
- the same value-shape read an unresolved slot performs, which is what keeps the surfaces agreeing.

Contrast [[type-def shape opaque]], whose fence reads VERBATIM, never parsed.

## Reserved name
`any` is reserved.
- it joins `file`, `opaque`, and the primitives, a user [[type-def]] cannot claim it.
- [[spec - diagnostic codes^reserved-type-name]].

## Completes the file shape
[[type-def shape file]] exists only as `file*`, with no inline form, a file has no inline value.
`any` is the same no-constraint idea with the inline form present.
- so the suffix grammar applies uniformly to a no-constraint shape.
- `file*` is the whole-file narrowing of `any*`, see [[type-def shape file]].

The overlap is documented.
- a `<file* | any*>` slot-union fires [[spec - diagnostic codes^subsumption-in-slot-union]], `any*` is wider.

# Structure
```yaml
fields:
  captured: any        # an interpreted value of any shape
  log: any[]           # a list of interpreted values
  target: any*         # a reference to any node, no closure check
  slot: any&           # interpreted inline, or a [[reference]]
```

A body fence filling an `any` slot, read by value-shape:
````markdown
```[:captured]
type: myRecordType   # a mapping reads as a record, interpreted
key: value
```
````
For an uninterpreted blob, use [[type-def shape opaque]] instead.
