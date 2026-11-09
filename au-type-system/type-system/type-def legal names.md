The naming rule for a [[type-def]].
A name is one atomic identifier, the engine reads no structure from it.

# Properties

## A name is one atomic identifier
The engine reads no structure from a name.
- `a.b.c` is a single identifier, not a path.
- `c` is not a segment with independent meaning.

Identity is the WHOLE name.
- folded whole into the type's `(name, closure-hash)` identity, never a part of it, see [[type closure]].
- two names are the same type only when the full strings match, a shared prefix is nothing.

A `.` is a legal character but structurally inert.
- the dotted `parent.subtype` form is a human naming convention, see [[type sealed naming]], not a relation the engine reads.
- subtyping is declared with [[type-def extends]], never inferred from a shared name prefix.
- a type may carry no dotted prefix at all, `my-adapter` extending `mcp.adapter` is fine, nothing enforces or reads a prefix.

## Leading letter
The first character must be a letter.

Keeps a name YAML-string-shaped.
A bare `42` would parse as a number.

## Reserved names
Some built-in names a user type-def cannot claim:
- [[type-def shape file]]
- [[type-def shape any]]
- [[type-def shape primitive]]

Claiming one is a load error:
- [[spec - diagnostic codes^reserved-type-name]].

## Cross-repo qualifier
A name never contains `:`, so the `::repo` qualifier is unambiguously appended after it.
- `foo::repo` is the name `foo` plus the repo scope, never a `:` inside the name.
- see [[type repo qualifier]].

# Structure
Regex: `^[A-Za-z][A-Za-z0-9_-]*(\.[A-Za-z][A-Za-z0-9_-]*)*$`

Allowed:
- letters.
- digits, but not as the first character.
- `-` and `_`.
- `.`, only at internal positions, see [[type sealed naming]].

Forbidden, each a [[type-def field shape]] operator:
- `*`, `&`, `?`, `+`, `[`, `]`, `<`, `>`, `|`, `:`.
- whitespace.

A violation is a load error:
- [[spec - diagnostic codes^type-name-violates-regex]].
