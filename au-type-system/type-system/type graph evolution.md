How the type graph changes over time,
against an existing instance corpus.

# Properties

## Additive changes
Leave existing [[type-instance]]s valid:
- a new optional [[type-def fields]] entry.
- a new branch on a [[type-def sealed]] parent.
- a new [[type-def meta]] sub-region.
- a new top-level [[type-def]].

## Breaking changes
Diagnosable at type-graph load,
against the existing instance corpus:
- a new required field.
- a [[type-def sealed]] branch removal.
- shape tightening, e.g. `T[]` to `T[+]`.
- marking an existing type [[type-def abstract]] while direct instances claim it.
- adding a [[type-def required meta]] `required:` obligation, against the existing concrete-subtype corpus.

Adding a [[type-def body]] to an existing type-def breaks its `.yaml` instances:
- [[spec - diagnostic codes^body-required-but-yaml-only-instance]].

## Surfacing
The engine surfaces affected instances by leaf.
It proposes a structural migration where the new shape is one edit away:
- a rename.
- a leaf promotion, via the [[type candidate scan]] path.

## Identity by name
A [[type-def]] identifies by name.
There is no per-type version annotation.

Multi-version coexistence is out of scope.
Evolution is a single-graph concern.

A consumer can still track versions out-of-band.
(E.g. a [[type-def meta]] version field plus git.)

## Cross-repo is distinct types, not versions
Across repos the same name is a distinct type, each repo owns its namespace.
- `foo::a` and `foo::b` coexist as different types, `::repo` disambiguates.
- so cross-repo same-name is not the out-of-scope multi-version case, see [[type repo qualifier]].
