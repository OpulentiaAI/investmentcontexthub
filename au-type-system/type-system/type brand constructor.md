The `Name(...)` value form, filling a slot typed by a [[type-def brand]].

The value axis of a brand.
A scalar, tuple, or enum brand carries no bare place for its identity, the constructor supplies it.

# Properties

## One syntax for scalar, tuple, and enum
`Name(args)` names the brand and carries its representation.
- a branded scalar, `meter(42)`.
- a tuple, args positional, `point(20, 30)`.
- a named enum member, `quality(reviewed)`.

It is to a scalar, tuple, or enum what an inline `type:` claim is to a record, see [[type-def shape record]].

## Optional when the slot pins one brand
Coercion is the default, a bare value infers the slot's brand.
- a slot pinning one brand infers it, `length: 42` coerces to `meter`.
- the name is REQUIRED only to disambiguate an ambiguous union slot, else [[spec - diagnostic codes^brand-constructor-required]].

## The name must be admitted
Admission is a VALIDATOR concern, checked against the slot's declared type.
- the admitted names are the slot's own brand, or a member of its union, records / nominal brands / primitives alike.
- the decision is LOCAL to the slot's declared type, never a graph scan.
- an unadmitted name is a mismatch, `second(42)` or `Number(42)` at a `meter` slot, [[spec - diagnostic codes^brand-constructor-mismatch]].
- a value at a plain [[type-def shape primitive]] slot never runs the recognizer, `foo(bar)` there is already the literal string.

## The value is a faithful parse, admission is separate
The value layer PARSES any well-formed `Name(x)` at a brand slot, it never judges admission.
- so `second(42)` at a `meter` slot resolves to value `42`, brand `second`, and the validator separately fires the mismatch.
- no content is lost, `Name(x)` is reconstructable from `brand(value)`, and the value layer needs no graph.
- for a value that only LOOKS like a call at a String slot, the escape opts out, `label("print(x)")`.

## The reserved-primitive escape
A [[type-def shape primitive]] constructor, `String(...)` / `Number(...)` / `Date(...)`, is admitted ONLY as a union member.
- as a member it forces that primitive branch, the literal escape for a constructor-shaped string.
  - `String("looks(foo)")` at `<String | myLabel>` is the plain string `looks(foo)`, not a brand.
- it is NOT admitted at a single brand slot, `Number(5)` at a `meter` slot is a mismatch, "not-meter Number" is meaningless there.
- the escape at a single brand slot is the brand's own constructor with a quoted arg, `myLabel("looks(foo)")`.

## A bare value at a union must be unambiguous
A bare value is ambiguous when TWO OR MORE admitting members accept it and share one base primitive with NO distinguishing predicate.
- the indistinguishable kinds, a plain `String` / `Number` / `Boolean`, and a nominal brand over one.
  - `<String | myLabel>` and `<myMeter | mySecond>` are ambiguous, the author names the branch.
- a distinguishing predicate discriminates, a `Url` prefix, a `Date` / `DateTime` format, a refined `{...}`, an enum membership.
  - `<String | Url>`, `<String | myMeter>`, `<Number | Date>` stay unambiguous, the value's shape picks the branch.
- an ambiguous bare value is [[spec - diagnostic codes^brand-constructor-required]], never a silent first-match.

## Identity on the value
`Name(v)` equals the bare `v` for an admitted type at an unambiguous slot.
- `Number(42) == 42`, `Date(2020-01-01) == 2020-01-01`, `meter(42)` coerces like `42`.
- the constructor names the branch, it never changes the value.

## An uninterpreted scalar
The constructor is a scalar value, not a new instance representation.
- it stays a plain string in the parse-layer, uninterpreted, the seam a date, a URL, or a wikilink uses.
- a recognizer parses the `Name(...)` token shape, validation interprets it against the slot's resolved brand.
- a value starting a `Name(` shape that does not close well-formed is [[spec - diagnostic codes^malformed-constructor]].

## Collapse on the underlying value, brand to the side
A branded value resolves to its underlying representation, and the written brand rides beside it.
- the value always resolves, `length: 42` and a body contribution `meter(42)` are the SAME value `42`, one [[type value container]], two contributions.
- the constructor name is a surface annotation, not part of the value, like an inline record's `^:` id, so a branded value never double-counts across surfaces.
- the container carries a `brand` side-channel, the brand name the author wrote, `meter` for `meter(5)` (a peer brand keeps its qualifier).
  - it is the discriminator at a union, `meter(42)` at `<meter | second>` is value `42`, brand `meter`.
  - it is absent for a bare value or a reserved-primitive escape, where the member is either given by the slot or inferable from the value.
- a TUPLE resolves recursively, its elements each a resolved value with their own brand, plus the tuple's brand.
  - `point(20, 30)` is elements `[20, 30]` brand `point`, each element a resolved value with its own optional brand.
  - a tuple is one value, one container, unlike a list `T[]` which is one per element.

# Structure
```yaml
length: meter(42)          # branded scalar, explicit
length: 42                 # the same, coerced at a pinned slot
offset: point(20, 30)      # tuple, args positional
state:  quality(reviewed)  # named enum member
```

A union names its branch, with the primitive-member escape:
```yaml
# slot:  myKind: <meter | second>
myKind: meter(42)          # required, a bare 42 is brand-constructor-required

# slot:  myLabel: <String | myBrandedString>   (both represented as String)
myLabel: String("foo(bar)")        # the plain string "foo(bar)", the escape
myLabel: myBrandedString("foo")    # branded
# a bare  myLabel: "hi"  is brand-constructor-required, name the branch
```
