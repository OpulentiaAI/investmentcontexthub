How same-named fields from mixed parents resolve on a [[type-instance]].

# Properties

## Auto-unify
Same-named fields with token-equal shapes merge into one.
A bare value satisfies every origin at once, no qualifier needed at the use site.

Token-equal is the same shape expression:
- same primitive.
- same enum, in the same order.
- same type-def name.
- same compound, in the same order.

A subtype relation does not count as identical.

## Divergent collision
Same-named fields whose origins declare NON-token-equal shapes are a divergent field.

The field stays in the [[type effective shape]] as a per-origin set.
- each origin keeps its OWN shape, there is no unified shape to bind a bare value to.
- so a bare use is ambiguous, the engine cannot pick which origin's shape it satisfies.

Every use of a divergent field must be QUALIFIED.
- a bare use is an error, [[spec - diagnostic codes^mixin-collision]].
- there is no bare shortcut, this is the difference from an auto-unified field.

Renaming one field also removes the collision.
- distinct names never collide, so the divergence is gone.
- the qualifier resolves the collision in place, the rename removes it.

Required is still required, per origin.
- a divergent field REQUIRED at an origin fires [[spec - diagnostic codes^required-field-absent]] for that origin until a `field{origin}` qualifier fills it, whether or not the field is otherwise touched.
- so an untouched divergent field is clean ONLY when it is OPTIONAL at every origin.
- an origin's SHAPE is only checked when that origin is filled, but its PRESENCE obligation holds like any required field.
- a bare use adds the collision ON TOP of the required diagnostics (a bare value fills no origin), it does not suppress them.

The collision surfaces at an instance's bare use, never at a type-def.
- a type-def may carry a divergent inherited field, `extends: [myA, myB]` where both declare `myField` with differing shapes.
- it is legal, no diagnostic at type-graph load, the type is not broken.
- instances of it qualify each use, the resolution is per-instance, and a type-def-level warning could never be resolved there anyway.

## Qualified field
Write `field-name{type-name}` at the instance.
The brace encloses the qualifying type, it is a key-position qualifier, not a value refinement.

The qualifier is any type in the [[type closure]] whose own closure declares the field.
Originator, intermediate, or leaf all resolve to the one declaration.
- for a divergent field this holds only when the qualifier reaches ONE origin.
- a descendant below the divergence reaches BOTH divergent origins, so it names no single shape.
- such a descendant qualifier is rejected as ambiguous, name a declaring origin directly instead, `field{a}` or `field{b}`.

The value validates against the NAMED origin's own shape.
- a divergent field's origins differ, so the qualifier selects which shape checks the value.

Errors:
- the qualifier is not in the closure:
  - [[spec - diagnostic codes^qualifier-not-in-closure]].
- the qualifier does not declare the field:
  - [[spec - diagnostic codes^qualifier-does-not-declare-field]].
- the qualifier reaches a divergent field at more than one origin:
  - [[spec - diagnostic codes^qualifier-ambiguous]].
- the qualified key is malformed:
  - [[spec - diagnostic codes^malformed-qualifier-key]].

## Cross-repo qualifier
A collision can cross a repo boundary.
An own field collides with a same-named peer field.

The qualifier carries the peer's `::repo`, inside the braces.
- `field-name{type-name::repo}`.
- the brace holds a type-name position, so `::repo` reads there like every other, see [[type repo qualifier]].
- a bare qualifier names an own type, a `::repo` qualifier names a peer's.

The peer qualifier resolves over the folded closure.
- the same fold a `foo::repo` claim uses, see [[cross repo typed graph]].
- a bare qualifier stays on the own graph.

This is the case the qualifier exists for.
- two types from repos you don't control cannot be renamed, so the qualifier is the only resolution.

## Per-origin requirement
Each origin declares its own required-or-optional, and is satisfied independently.
- an auto-unified field, a bare value satisfies every origin, or a per-origin qualifier satisfies that one.
- a divergent field, only a qualifier for that origin satisfies it.

A required origin left unsatisfied is [[spec - diagnostic codes^required-field-absent]], one per unfilled origin.
- so a divergent field with two required origins needs both qualifiers.

## One form per field
The permitted forms depend on whether the field auto-unified.

An auto-unified field, all uses agree, either all bare or all qualified.
- mixing bare and qualified is [[spec - diagnostic codes^mixed-bare-and-qualified-field]].
- a bare value already fills every origin, so adding a qualifier beside it is contradictory.

A divergent field, every use is qualified.
- a bare use is [[spec - diagnostic codes^mixin-collision]], not the mixed-form error.

## Opt-in distinction
An author may qualify even when shapes are identical.
It signals "same name, conceptually different."

Then each colliding required field must be given explicitly.

## Body surface
A body contribution qualifies the same way, the [[type-instance body contribution]] carrier carries the qualifier.
- an inline marker
  - `` `[:field-name{type-name}]` ``
  - `` `[:field-name{type-name::repo-name}]` ``
- a wikilink attribution
  - `[[target:field-name{type-name}]]`
  - `[[target:field-name{type-name::repo-name}]]`
- the qualified `:field` fragment lives in [[wikilink fragments]].
- the qualifier's `}` collides with none of the `[` `]` `]]` carrier delimiters, so each carrier closes cleanly; the one delimiter collision is the `{type::repo}` `::` against the wikilink `::repo` scope, resolved by scanning the repo scope at brace depth zero, see [[wikilink fragments]].

# Structure
```yaml
# myNote and myMaturity both declare  description: String  (token-equal)

# auto-unify, a bare value fills both
type:
  - myNote
  - myMaturity
description: <value>

# opt-in qualified, kept distinct
type:
  - myNote
  - myMaturity
description{myNote}: <value>
description{myMaturity}: <value>
```

Divergent, own `title: String` collides with peer `title: Number`, every use qualified:
```yaml
type:
  - note                       # title: String
  - note::base                 # title: Number
title{note}: "a string"        # validates against note's String
title{note::base}: 42          # validates against note::base's Number
# a bare `title:` here would be a mixin-collision
```
