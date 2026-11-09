A slot refinement narrows its base to a smaller region of allowed values,
without naming a new type.
A modifier on a [[type-def field shape]],
not a shape of its own.

Two axes, each a meet on the one value lattice.
- the VALUE axis, `Base{predicate}`, which values a scalar admits.
- the COUNT axis, `T[x..y]`, how many elements a list admits.

# Properties

## Opt-in precision
An absent refinement keeps the base's full value-space.

A refinement is always the author's choice, declared at the shape.
Never inferred from a value.

## Anonymous and structural
The narrowed region is anonymous,
nothing named,
nothing joins the [[type closure]].

## Value refinement `Base{predicate}`
A brace-delimited predicate narrows a scalar [[type-def shape primitive]].

The refinable bases are the primitives that admit a predicate:
- `Number`, comparisons and `integer`.
- `String`, a regex.
- `Date` and `DateTime`, comparisons, the ordered temporal primitives.

`Boolean` and `Url` admit no predicate, any refinement on them is a load error:
- [[spec - diagnostic codes^refinement-bad-shape]].

An enum, record, compound, and reference are not refinable.
- an enum is already a set-refinement of a scalar, narrowing it further is field narrowing, a separate concern.

The predicate vocabulary is small and closed
- **comparison**
  - `>`, `>=`, `<`, `<=`
  - on `Number`, `Date` or `DateTime`
- **`integer`**
  - on `Number`
- **regex**
  - `/.../`
  - on `String`
  - an unanchored regular language
  - no backreferences, no lookahead.
  - reference implementation is rust `regex`, similar to RE2
- **`&`**
  - conjunction of predicates

At most
- one lower comparison
- one upper comparison
- one `integer`
- one regex
A duplicate-kind predicate is [[spec - diagnostic codes^refinement-bad-shape]].

## Range cardinality `T[x..y]`
A bracket suffix bounds a list's element count.
- `[x..y]`, inclusive discrete bounds.
- `[x..]`, unbounded above.
- `[..m]`, floor `0`, equal to `[0..m]`.
- `[n]`, an exact count, equal to `[n..n]`.

- `[]` equals `[0..]`, any count.
- `[+]` equals `[1..]`, non-empty.

A negative or non-integer bound, and an inverted range `[5..1]`, are a load error:
- [[spec - diagnostic codes^cardinality-bad-shape]].

## Validation
A value is checked against its base,
then against each predicate, the meet.

On a list slot the two axes act on different targets.
- the predicate constrains each ELEMENT.
- the range constrains the list LENGTH.
- `Number{>=0}[3..]` is at-least-three non-negative numbers.

A value outside its slot's refinement is an `Error`,
the file still loads:
- [[spec - diagnostic codes^value-out-of-refinement]], per [[type open-world validation]].

A slot whose numeric meet admits no value is diagnosed once on the type-def:
- [[spec - diagnostic codes^refinement-unsatisfiable]], a `Warning`.
- while empty, the validator suppresses the per-value error, the type is broken not the data.

## Identity and compatibility
A refinement is part of the field shape, so it joins the canonical form and the closure hash.
- the predicate tokens render in a fixed canonical order, the meet is commutative.
- identity is structural, not semantically minimized, `Number{>0 & integer}` and `Number{>=1 & integer}` stay distinct.

Adding or tightening a refinement narrows the valid-instance set, so it is a breaking change.
- loosening or removing one widens, so it is compatible.
- see [[type graph evolution]].

# Structure
A base shape,
an optional value refinement `{...}`,
an optional reference suffix,
an optional count suffix `[...]`.

The value refinement precedes the reference suffix,
the count suffix comes last.
A refined scalar takes no `*` / `&` / `@`,
a primitive is not referenceable.

```yaml
fields:
  myDepth:  Number{>=0 & integer}     # a non-negative whole count
  myRatio:  Number{>=0 & <=1}         # a bounded fraction
  mySlug:   String{/^[a-z0-9-]+$/}    # a pattern
  myAfter:  Date{>=2020-01-01}        # a lower date bound
  myTriple: Number[3]                 # exactly three
  myVertices: myPoint[3..]            # at least three records
  myScores: Number{>=0 & <=100}[+]    # a non-empty list, each bounded
```
