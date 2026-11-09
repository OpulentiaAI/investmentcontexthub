The `location:` key on a [[type-def]].
An advisory declaration of where the type's instances live.

# Properties

## Advisory placement
Placement becomes a checkable typed constraint, not a convention carried in prose.
- checked, never blocks, per [[type open-world validation]].
- a broken block surfaces a diagnostic but never aborts the repo's instance validation.
- a type-def-only key, on an instance it is [[spec - diagnostic codes^reserved-key-on-instance]].

## The block
A mapping with four optional sub-keys, `name`, `path`, `fileType`, `strict`.
A malformed block, name template, path glob, or fileType is a load error:
- [[spec - diagnostic codes^location-bad-shape]].

## `name`, a pure template
Renders the file's basename STEM, the extension excluded.
- `${.type}` renders the OWNING type's name.
- `${.field}` renders a required scalar field's value, literal text otherwise.
- pure, no clock, no I/O, so rendering is deterministic.

A referenced field must be REQUIRED and a SAFE SCALAR.
- legal
  - `String` / `Number` / `Boolean` / `Date` / `DateTime` / an enum
  - or a refinement over these
- illegal
  - `Url`, a list, a reference, a record, a compound, a tuple
  - an optional or divergent field
  - or one absent from the effective shape
  - each a [[spec - diagnostic codes^location-bad-shape]].
- the `DateTime` is the colon-free `YYYY-MM-DDThhmmssZ` form, so it renders one safe component.

## `path`, a static glob
Matches the file's repo-relative directory, rooted at the repo root.
- `*` one segment, `**` zero or more, a trailing `/` the directory the file sits inside.
- static only, a `${.field}` segment, a `..`, an absolute, or a partial-glob segment is [[spec - diagnostic codes^location-bad-shape]].

## `fileType`, the extension pin
Engine type supported file types (currently `md` or `yaml`), matched against the file extension.
- closes a reference ambiguity, `[[governance]]` across `governance.md` and `governance.yaml`.
- `yaml` beside a non-empty effective [[type-def body]] is unsatisfiable:
  - [[spec - diagnostic codes^location-filetype-body-conflict]].

## Severity, strict is placement-only
`strict` raises a placement mismatch from a warning to an error, on ANY path.
- soft, matches no claimed location, [[spec - diagnostic codes^location-mismatch]] (warning).
- soft, a raw mixin matched one claimed location but not another, [[spec - diagnostic codes^location-partial-unmet]] (hint).
- `strict: true` unmet, [[spec - diagnostic codes^location-strict-violation]] (error), and it opts out of the mixin satisfy-any.
- `strict` governs adherence only, never uniqueness or identity.

## Singleton emerges from an exact slot
The "at most one" property is not a flag.
- an exact `path` plus `name` pins one physical slot, so a second instance is necessarily misplaced.
- the placement check catches it, no dedicated rule.
- a wildcard path has no singleton, `strict` still mandates the pattern.

## Inheritance, whole-block
Inherits WHOLE-BLOCK like [[type-def meta]], not per-key like [[type-def fields]].
- the closest declared block in the [[type closure]] wins, in full.
- a subtype's own block replaces the ancestor's ENTIRELY, `strict` included.
- `location: {}` drops the constraint, the `meta: []` analog.
- `strict` is owned per-declaration, so a subtype can relax an ancestor's strictness.

## Mixin, satisfy-any
A file is one physical fact, so a raw mixin of divergent locations satisfies at most one.
- clean when the placement matches at least one claimed location.
- token-equal blocks auto-unify to one constraint.
- a `strict` location opts out, unmet even inside a mixin.

## No uniqueness diagnostic
`location` adds NO proactive name-collision check.
- a duplicate name is caught where it bites, [[spec - diagnostic codes^reference-target-ambiguous]] on a `[[name]]` link, and [[spec - diagnostic codes^case-collision-basename]] for the case trap.
- a not-yet-linked duplicate is a normal forge state, never a nag.
- proactive or queryable uniqueness, if a puller appears, is a read, a graph-shape concern.

## Cross-repo
Placement composes across repos over the `::repo` qualifier.
- an instance claiming `type: foo::repo`, or a subtype `extends: foo::repo` with its own `name` over an inherited field, resolves over the folded resolution graph, see [[cross repo typed graph]].
- the `path` and `name` are matched relative to the CLAIMING repo's root, the location travels with the type.

## Identity
`location` does NOT fold into the type's `(name, ClosureHash)` identity.
- advisory, so folding it would let a filing convention fork a type's cross-repo identity.
- two same-named peer types stay in-sync when only their `location` differs.

# Structure
```yaml
# type/plan.type.yaml
fields:
  slug: String
location:
  name: "${.type} - ${.slug}"   # → the stem "plan - my-thing"
  path: "**/plan/"              # under any `plan/` directory
  fileType: md

# type/governance.type.yaml — an exact strict singleton
location:
  path: "config/"
  name: "governance"
  fileType: yaml
  strict: true
```
