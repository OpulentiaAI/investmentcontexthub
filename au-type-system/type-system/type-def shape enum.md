A closed list of literal values.
One of the [[type-def field shape]].

# Properties

## Membership
A value must be one of the listed literals.

A non-member is a validation error:
- [[spec - diagnostic codes^field-shape-mismatch]].

## Element names
Each element follows the [[type-def legal names]] regex.

Keeps e.g. `[+]` unambiguously the non-empty-list suffix,
not a one-element enum.

A bad element is a load error:
- [[spec - diagnostic codes^shape-syntax-error]].

## Ordering significant
`[low, high]` and `[high, low]` are distinct.

Ordering matters for auto-unify across mixed parents.

## Named, reusable form
An inline enum has nowhere to hang a per-member doc, or a name to reuse across slots.
A [[type-def brand]] `shape:` member list lifts it to a named, documented, reusable def.
- the block-list form carries a `#:` docstring per member, and a head doc, see [[type docstring]].
- the same closed literal set, one definition point instead of a retype per slot.

## No reference
An enum is not a file.

The `*` and `&` reference suffixes are a load error:
- [[spec - diagnostic codes^shape-syntax-error]].

# Lists
A list suffix `[]` or `[+]` is fine.

A suffixed enum must be quoted.
- `myField: "[low, high][]"`, not bare `myField: [low, high][]`.
- the bare form is not valid YAML.
  - `[low, high]` reads as a YAML flow sequence.
  - the trailing `[]` then has no valid parse, the file fails YAML load.
- the quotes make the whole shape one scalar string, `[low, high][]`, which the grammar parses as a list of the enum.
- a bare enum with no suffix stays unquoted, `[low, high]` is a plain flow sequence the engine recovers from the source.

This is a YAML-layer constraint, not a grammar one.
The shape grammar accepts `[low, high][]` directly, the quoting only gets the string past the YAML parser.

# Structure
A bracketed list of literals.

```yaml
fields:
  myLevel: [low, moderate, high]
  myLevels: "[low, moderate, high][]"   # a suffixed enum, quoted
```
