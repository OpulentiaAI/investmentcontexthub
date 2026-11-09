Map of the type-system atoms.
The reading order runs top to bottom, each atom one concept.

For the whole-system view, read [[type system - why this shape]] first.
For how the atoms are authored, see the README.

# Files
- [[type-def]]
  - declaration of a type.
- [[type-instance]]
  - a file claiming type-defs and supplying their values.

# Inheritance
- [[type-def extends]]
  - the optional parent claim.
- [[type subtyping width-only]]
  - additions-only inheritance.

# Fields and shapes
- [[type-def fields]]
  - own field declarations.
- [[type-def field shape]]
  - the slot-expression grammar.
- [[type-def shape primitive]]
  - String, Number, Boolean, Date, DateTime, Url.
- [[type-def shape enum]]
  - a closed list of literal values.
- [[type-def shape record]]
  - a bare type-def name, filled by an inline record.
- [[type-def shape compound]]
  - slot-level union and intersection.
- [[type-def shape tuple]]
  - a fixed-arity positional product, `(A, B)`.
- [[type-def shape file]]
  - the built-in whole-file reference target.
- [[type-def shape any]]
  - the built-in top type, unconstrained but interpreted, inline or reference.
- [[type-def shape opaque]]
  - the built-in uninterpreted inline slot, stored but never read.
- [[type-def shape def-ref]]
  - the built-in typed reference to a type-def, `type<T>*`.
- [[type-def shape suffixes]]
  - `*`, `&`, `[]`, `[+]` modifiers.
- [[type-def shape refinement]]
  - `Base{predicate}` value narrowing and `T[x..y]` range cardinality, meets on a slot.

# Brands
- [[type-def brand]]
  - a type-def naming a shape instead of fields, a scalar, enum, union, or tuple.
- [[type brand constructor]]
  - the `Name(...)` value form for a nominal brand.

# Identity and effective shape
- [[type-instance type]]
  - identity claim and mixin.
- [[type-instance fields]]
  - values supplied for the effective shape.
- [[type closure]]
  - a type set plus all transitive ancestors.
- [[type effective shape]]
  - the merged field set an instance must satisfy.
- [[type-def fields collision - auto-unify and qualified field]]
  - same-named field resolution.
- [[type tag]]
  - a no-fields, identity-only type.

# References
- [[type reference]]
  - wikilink reference values and their kinds.
- [[reference name resolution]]
  - how a `[[target]]` name maps to a file.
- [[wikilink fragments]]
  - the ordered `::repo @commit #head ^ ^^ :field` fragments.
- [[type block-id]]
  - `^block-id` addressability and typed blocks.

# Cross-repo
- [[cross repo typed graph]]
  - the orientation, one qualifier crossing repo boundaries.
- [[type repo qualifier]]
  - `::repo` on a type name, which repo owns the type.

# Sealed, abstract, meta
- [[type-def sealed]]
  - closed set of permitted branches, the only named sum in the graph.
- [[type-def abstract]]
  - non-claimable-but-open marker, sealed is abstract plus closed.
- [[type-def meta]]
  - type-level metadata, never reaches an instance.
- [[type-def meta marker]]
  - the meta position admits only types mixing in `au.engine.meta`.
- [[type-def required meta]]
  - a base obligates every concrete subtype to carry a named meta.

# Placement
- [[type-def location]]
  - where a type's instances live, an advisory name / path / fileType / strict meet.

# Names and documentation
- [[type docstring]]
  - `#:` comments the engine captures and surfaces.
- [[type-def legal names]]
  - the type-name regex, reserved built-in names, and a name's atomicity.
- [[type sealed naming]]
  - the dotted `parent.subtype` leaf convention, a naming aid with no engine meaning.
- [[type list form]]
  - single-bare / multi-block shape convention.

# Body
- [[type-def body]]
  - ordered authoring template for instance prose.
- [[type-def body section]]
  - a named heading in a body template.
- [[type-def body use]]
  - splice another type-def's body.
- [[type-def body fills]]
  - a section or body contract over named fields.
- [[type-instance body contribution]]
  - field values contributed from the markdown body.
- [[type value container]]
  - a value plus every contribution that produced it.

# Validation and lifecycle
- [[type validation]]
  - the ordered passes and how errors gate them.
- [[type open-world validation]]
  - extras pass, growth is never rejected.
- [[type extras]]
  - field values outside the effective shape.
- [[type write model]]
  - read-before-write, operational Liskov.
- [[type candidate scan]]
  - types a file could claim but doesn't.
- [[type graph evolution]]
  - additive vs breaking changes over time.

# Cross-repo infrastructure
- [[cross-repo file set]]
  - the map of every file, committed versus per-user, identity versus location versus solve versus sync.
- [[repo yaml]]
  - a repo's committed identity and its deps.
- [[repos yaml]]
  - the per-user device-global name-to-path registry.
- [[workspace manifest]]
  - the optional in-repo `workspace.yaml`, `edit` and `discover` members over the entry folder-repo.
- [[workspaces yaml]]
  - the per-user index of named workspaces.
- [[package cache]]
  - the device-global store of fetched dependencies.
- [[package registry]]
  - the hosted name-to-remote catalog.
- [[engine schema files]]
  - the hardwired `au.engine.*` defs and the engine's typed files.

# Errors
- [[spec - diagnostic codes]]
  - the full catalog, each row addressed by `^code-name`.
