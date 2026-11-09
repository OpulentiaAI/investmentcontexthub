A [[type-def]] that names an underlying SHAPE instead of declaring [[type-def fields]].
A second kind of type-def, beside the record.


# Properties

## The shape key
A brand declares `shape:` in place of `fields:`.
- `shape: <primitive>`, a branded scalar.
- a `shape:` member list, a named enum.
- `shape: <A | B>`, a named union.
- `shape: (A, B)`, a tuple, see [[type-def shape tuple]].

`shape:` is a type-def-only reserved key.
On an instance or inside a meta body it is [[spec - diagnostic codes^reserved-key-on-instance]].

## Brand XOR record
A def is a brand or a record, never both.
- `shape:` beside `fields:`, `sealed:`, or `body:` is a load error, [[spec - diagnostic codes^brand-with-record-keys]].
- a brand has no fields, so it never surfaces in the [[type candidate scan]].
- a `shape:` value that is not one of the four forms is [[spec - diagnostic codes^malformed-brand-shape]].

## One definition point
A brand names a repeated shape once.
- define the shape once, reference it from many slots.
- edit the one def, every consuming slot follows.
- attach a [[type docstring]] to the type, and for a named enum to each member.

## Used by bare name
A slot types by a brand's bare name, `length: meter`.
- no new field-shape grammar, a bare name already parses as a slot demanding the named type.
- the engine resolves the name to a brand and validates the value against its shape.
- the same bare-name slot means record, reference, or brand, decided at resolution, see [[type-def shape record]].

## Nominal versus structural, keyed on the shape
The named shape decides the kind.
The keyword never carries the distinction.

- a scalar, enum, or tuple shape is NOMINAL.
  - a fresh identity over its representation, `meter` is not `second` though both are `Number`.
  - inline only, `*` and `&` reject, [[spec - diagnostic codes^brand-not-referenceable]], a scalar is not a file.
- a union shape is STRUCTURAL, a discriminated set of members, see [[type-def shape compound]].
  - referenceable ONLY when every member is a record type.
  - a union with any primitive or nominal-brand member is inline-only, a `*` / `&` on it is [[spec - diagnostic codes^brand-not-referenceable]].

## The value forms
Each brand form has one value form.
- a nominal brand, the `Name(...)` constructor, see [[type brand constructor]].
- a union member, reached by its own form, a record by its inline `type:`, a nominal member by its constructor, a primitive bare or its escape constructor.

A bare value coerces to the slot's brand, the slot is the authority.
- `length: 42` infers `meter`, coercion is the default.
- a constructor names an ADMITTED type, the brand or a union member, else a mismatch, `length: second(42)` is [[spec - diagnostic codes^brand-constructor-mismatch]].
- an indistinguishable bare value at a union names its branch, else [[spec - diagnostic codes^brand-constructor-required]], see [[type brand constructor]].

## What a brand buys, and what it does not
Buys.
- one definition point for a repeated shape.
- a queryable, named, documented type.
- nominal safety where the value is explicit, `second(42)` in a `meter` slot is a mismatch.

Does not buy.
- rejection of a bare `42` an author "meant" as seconds, the slot coerces it.
- unit conversion, `42cm = 0.42m` is arithmetic, outside the type system.

## Identity
Every brand folds its named shape into its `(name, ClosureHash)` identity.
- over the canonical declared form, present only when `shape:` is declared, so no existing record identity rotates.
- member order is significant for a scalar, enum, or tuple shape.
- a structural or tuple shape referencing record types folds those members' closures in transitively, a member divergence changes the brand's identity.
- docstrings stay advisory and out of the hash, see [[type docstring]].
- so brands compose across repos like any type, a peer's brand folds in over `::repo`, see [[cross repo typed graph]].

## The four forms
Detail lives in the shape atoms.
- a branded scalar, a [[type-def shape primitive]], optionally refined, see [[type-def shape refinement]].
- a named enum, a documented [[type-def shape enum]] lifted to a reusable def.
- a named union, a [[type-def shape compound]] the brand names.
- a tuple, a [[type-def shape tuple]].

# Structure
```yaml
# type/meter.type.yaml — branded scalar
#: a distance in metres
shape: Number

# type/icon-role.type.yaml — named enum, per-member docs
shape:
  - save        #: persist current state
  - delete      #: remove the target

# type/evidence-kind.type.yaml — named union
shape: <paper | observation | prior-decision>

# type/rect.type.yaml — tuple
shape: (Number, Number, Number, Number)
```

A slot uses a brand by its bare name:
```yaml
fields:
  length: meter              # nominal scalar, inline only
  icon: icon-role            # nominal enum
  evidence: evidence-kind*   # structural, all-record, referenceable
```
