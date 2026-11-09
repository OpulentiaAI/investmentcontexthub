A fixed-arity positional product, each position its own shape.
One of the [[type-def field shape]].

# Properties

## Fixed arity
`(A, B, ...)` declares an ordered product of a fixed number of elements.
Every element is required, that is the point over a list.

A value whose element count differs from the declared arity is a validation error:
- [[spec - diagnostic codes^tuple-arity-mismatch]].

## Element shapes
Each position is its own [[type-def field shape]],
independent of the others — the positions need not share a type.
- a primitive, `(Number, String)`.
- a brand, `(myPoint, myColor)`, see [[type-def brand]].
- a record type, or a nested tuple, `(myPoint, (Number, Number))`.

Each element validates against its own position's shape, and order is significant, `(String, Number)` and `(Number, String)` are different shapes.

## Parens are a tuple, brackets never are
`(...)` is a tuple, and `[...]` is never a tuple, in BOTH grammars.
- in the SHAPE grammar of a `.type.yaml`, `(A, B)` is a tuple, distinct from every `[...]` form, the `[]` / `[+]` list suffix and the `[low, high]` enum.
- in the VALUE grammar of an instance, `(20, 30)` is a tuple and `[20, 30]` is a list, see [[#Value form]].
- so the parens never collide with a list, at either level, and reading a value never needs the slot to tell a tuple from a list.

## Not a type
A bare inline tuple slot is a slot constraint, not a new type in the graph.
To name a tuple, brand it, `shape: (Number, Number)`, see [[type-def brand]].

## Value form
A tuple value is a paren form, never a bracket sequence.
- an inline slot `(A, B)` reads the paren form `(20, 30)`, a nameless positional product of exactly the arity.
- a tuple BRAND reads the `Name(...)` constructor, args positional, see [[type brand constructor]].
- a `[20, 30]` bracket sequence is always a LIST value, so at a tuple slot it is a shape mismatch, write the paren or constructor form.

The paren form is a plain YAML scalar the engine reparses.
- `(...)` is not a YAML flow indicator, so `myPair: (20, 30)` reads as one scalar string, no quoting.
- the engine interprets that string as a tuple, the same way it interprets `Name(...)` and a date, the engine owns its value grammar.

## Multi-line values
A tuple value is one scalar, so a long or nested one may wrap with a YAML block scalar, `>-`.
- `>-` folds the wrapped lines into the one scalar string the engine reparses, so the paren form need not sit on one crowded line.
- a plain unquoted multi-line paren value is fragile, YAML folding rules bite on an interior `: `, so `>-` is the escape hatch to reach for.

A tuple that WANTS to wrap is usually a record instead.
- a tuple suits a short fixed product, see [[#Prose elements want a record]].
- for a long or nested structure, a record nests natively in YAML and names its parts, the better shape.

## Cycles and inhabitability
A tuple is a containment shape, its elements ARE the value, not references.
- so a tuple whose shape cycles, `myFirst: (mySecond, mySecond)` and `mySecond: (myFirst, myFirst)`, is UNINHABITABLE, no finite value satisfies it.
- this is not a load error, the parallel of an inline [[type-def shape record]] containment cycle, and of [[type-def shape compound]]'s stance, a genuinely uninhabitable shape needs no special check.
- type identity stays cycle-safe regardless, the referenced-closure hash condenses cycles, so the graph loads and terminates.
- instance validation catches it at the use site, any value mismatches, so no dedicated diagnostic fires.
- a reference cycle (a `*` slot) is a different case, legal and inhabitable, a pointer does not contain its target.

## Prose elements want a record
A tuple suits a short fixed product, a `point` or a `rect`.
For long or prose-heavy elements, a record with named fields is the better shape.

# Structure
```yaml
fields:
  myPair: (Number, Number)        # inline tuple slot, same-type positions
  myLabelled: (String, Number)    # positions may differ, each its own shape
  myCorners: (myPoint, myPoint)   # elements may be records or brands
```

An inline tuple value is the paren form, never a bracket sequence:
```yaml
myPair: (20, 30)     # a tuple;  myPair: [20, 30] would be a list, a mismatch here
```

A tuple brand value is its constructor:
```yaml
# slot:  myOffset: myPoint       (myPoint is shape: (Number, Number))
myOffset: myPoint(20, 30)
```

A long or nested value may wrap with a `>-` block scalar:
```yaml
myGrid: >-
  ((1, "a"),
   ("b", 2))
```
