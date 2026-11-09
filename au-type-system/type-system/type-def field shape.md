The value shape of a [[type-def fields]] declaration.

# Properties

## Value constraint
Declares which values the field accepts.

## Parse
Parsed by a slot-expression grammar.
A malformed shape is a load error:
- [[spec - diagnostic codes^shape-syntax-error]].

## Cross-repo demand
A slot may demand a peer's type, `foo::repo*`.
- the `::repo` qualifier binds to the name, before the suffixes.
- the referenced value may live in any repo, see [[type repo qualifier]].

# Structure
A base shape, optionally carrying suffixes.

Base shapes:
- [[type-def shape primitive]]
  - primitives
- [[type-def shape enum]]
  - a closed list of literals, `[low, high]`.
- [[type-def shape record]]
  - a bare [[type-def]] name, taking an inline record value.
- [[type-def shape compound]]
  - `<myA | myB>` union, `<myA & myB>` intersection.
- [[type-def shape tuple]]
  - `(myA, myB)` a fixed-arity positional product.
- [[type-def shape file]]
  - the built-in whole-file reference target.
- [[type-def shape any]]
  - the built-in no-type slot, opaque inline or unconstrained reference.
- [[type-def shape def-ref]]
  - the built-in typed reference to a type-def, `type<T>*`, reference-only.

Suffixes attach to a base shape:
- [[type-def shape suffixes]]
  - `*` reference
  - `&` inline-or-reference
  - `[]` list
  - `[+]` non-empty list.

```yaml
fields:
  myPrimitive: String
  myEnum: [low, high]
  myRecord: myType
  myReference: myType*
  myDefReference: type<myType>*
  myList: myType[]
  myNonEmptyList: myType[+]
  myUnion: <myA | myB>
  myTuple: (Number, Number)
```
