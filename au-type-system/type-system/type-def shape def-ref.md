The built-in typed reference to a [[type-def]].
One of the [[type-def field shape]].

A slot value points at a type-def as a validated value.
Not an instance of that type, the def itself.

# Properties

## The def axis of `T*`
A mirror of [[type-def shape suffixes]] `T*`, on the other axis.
- `T*` walks the target instance's [[type-instance type]] identity closure.
- `type<T>*` walks the target def's [[type-def extends]] parent closure.
- same [[type closure]] machinery, the def axis instead of the instance axis.

Type-defs are already files in the graph, reachable by [[type-def shape file]] `file*`.
This makes that edge typed, instead of existence-only.

## Constrained and unconstrained
- `type<T>*`
  - the target's parent closure must include `T`.
- `type*`
  - any type-def, no closure check.
  - the degenerate form, parallel to `file*` and [[type-def shape any]] `any*`.

The constrained form carries the guarantee.
The unconstrained form is the def-axis `any*`.

## Reference only
A def has no inline value form here.
- only `type<T>*` and `type*` are meaningful, the `*` is baked in.
- no bare `type<T>`, no `type<T>&`.
- parallel to `file*`.

The value form and resolution live in [[type reference]].

## The boundary
A typed pointer to a def.
- it does not make defs mutable as data.
- it adds no reflection over the def's fields.
- defs stay non-data, referenced not unpacked.

## Failure modes
- the target is not a type-def:
  - [[spec - diagnostic codes^def-ref-target-not-a-type-def]].
- the target def's parent closure misses `T`:
  - [[spec - diagnostic codes^def-ref-closure-mismatch]].

Existence is checked like any validated reference.
- a dangling target is [[spec - diagnostic codes^reference-target-missing]].

## Composition
The bound `T` accepts the same compound-of-type-def-names that `*` and `&` accept.
A union or intersection of ceilings goes inside the angle brackets.
- `type<a | b>*`, a def in either subtree.
- `type<a & b>*`, a def whose parent closure includes both.

The union goes inside, not outside, because the `*` is baked into `type<...>*`.
- def-refs are `*`-only, there is no bare `type<T>` shape.
- so the `*` cannot factor out the way `<A | B>*` does for a normal reference.
- `<type<T1> | type<T2>>*` is ill-formed, `type<T1>` is not a shape without its `*`.
- `<type<T1>* | type<T2>*>` is allowed but redundant, `type<T1 | T2>*` is canonical.

The outer compound stays meaningful for a heterogeneous union.
- branches of different kinds, no common suffix to factor.
- `<type<mcp.tool>* | file*>`, a tool def or any plain file.
- `<type<mcp.tool>* | String>`, a tool def or a freeform string.
- each branch carries its own form, like `<String | T*>` and `<file* | any*>`.

So union of ceilings inside, union of different kinds outside.

# Structure
```yaml
fields:
  dryRunTool: type<mcp.tool>*       # a def in mcp.tool's subtree
  anyDef: type*                     # any type-def
  eitherKind: type<mcp.tool | mcp.resource>*
```

The value is a wikilink to the def file.
```yaml
dryRunTool: "[[mcp.tool.dry_run_type]]"
```
