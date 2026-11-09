The nominal marker gating which types may fill a [[type-def meta]] position.
A type is meta-legal only if its [[type closure]] mixes in the engine-owned `au.engine.meta` base.

# Properties

## Nominal, not positional
Meta-ness is a property the TYPE declares, by mixing in the base.
- it travels with the type, queryable and self-describing, not inferred from a use site.
- the `-meta` suffix convention becomes a real, checked type relation.

## The engine base
The engine hardwires `au.engine.meta`.
- a [[type tag]] (`fields: []`), `abstract: true`, see [[type-def abstract]].
- owned by the builtin `au-engine` repo, the universal `::au-engine` peer, no `deps` declaration, see [[engine schema files]].
- so it is mixed in QUALIFIED, `au.engine.meta::au-engine`, a bare `au.engine.meta` resolves in the author's own repo and dangles, see [[type repo qualifier]].
- abstract, so never a meta block's type directly, a block names a concrete subtype.

## Legality
A type is META-LEGAL when its RESOLVED closure includes `au.engine.meta::au-engine`.
- checked over the RESOLUTION graph, not the own-graph walk, the parity of sealed's cross-repo check.
- compared by `(name, closure-hash)` identity, see [[cross repo typed graph]].
- a `meta:` block `- type: X` where X is not meta-legal is an error:
  - [[spec - diagnostic codes^non-meta-type-in-meta-position]].

## A type is one mixin away
Nothing is lost, any type reaches meta-legality.
- an OWNED type, add the base as a parent, `extends: [X, au.engine.meta::au-engine]`.
- a NON-owned peer type, a WRAPPER subtype, `extends: [foo::peer, au.engine.meta::au-engine]`, then name the wrapper in the block.
- the mixin lives on the meta TYPE's def, the block still names a SINGLE type, so [[spec - diagnostic codes^meta-mixin-not-supported]] is untouched.
- the recommended idiom is a dedicated wrapper (`foo-meta`), keeping identity and meta concerns separate.

## Layered ownership
Each SDK layer owns its DOMAIN meta bases, abstract subtypes of `au.engine.meta`.
- e.g. a `presentation-meta`.
- the engine owns only the generic marker, it knows no domain meta.

## Tightens the required obligation
A [[type-def required meta]] `required:` item names a META type.
- with meta-ness nominal, `required:` naming a non-meta type is checkable, an error.
- a `required:` naming an abstract domain meta base is satisfied by any concrete subtype-of-it, by closure.

# Structure
```yaml
# a meta type mixes the marker in
# type/my-meta.type.yaml
extends: au.engine.meta::au-engine
fields:
  myField: <shape>

# a host names it in a meta position
meta:
  - type: my-meta
    myField: <value>
```
