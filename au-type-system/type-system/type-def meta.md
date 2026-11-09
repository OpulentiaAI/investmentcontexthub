The `meta:` key on a [[type-def]].

# Properties

## Type-level metadata
Attached to the type itself.
Never flows into a [[type-instance]]'s frontmatter.

## Typed sub-regions
A list of sub-regions,
one per named meta type.

A sub-region's `type:` names that type-def,
the rest are its fields.

The named type must be a META type, its closure mixes in `au.engine.meta::au-engine`.
- meta-ness is nominal, not positional, see [[type-def meta marker]].
- a non-meta type is [[spec - diagnostic codes^non-meta-type-in-meta-position]].
- the `-meta` suffix convention (`display-meta`, `runtime-meta`) is now a checked type relation, not just a name.

Each validates against its named type-def,
the same as instance validation.

## Required sub-region on subtypes
A `required:` item obligates every concrete subtype to carry a named meta.
- opt-in, beside the ordinary `type:` value blocks, discriminated by the `required:` key.
- see [[type-def required meta]].

## Singleton
At most one sub-region per named type-def per host.
A duplicate is a load error:
- [[spec - diagnostic codes^duplicate-meta-block]].

## No mixin
A sub-region's `type:` is single-name only.
- [[spec - diagnostic codes^meta-mixin-not-supported]].

## Inheritance and suppression
Not inherited as data.

The consumer walks the ancestor chain at read time, and the closest ancestor's meta for a name is surfaced.
The walk crosses `::repo` parents, a peer ancestor's meta surfaces through the fold, the same as `location:`.

`meta: []` marks an explicit break,
and suppresses that lookup.

There is no per-name suppression.
An empty sub-region body (`- type: myMeta` with no other keys) is just an empty declaration.
- valid only if that type-def's fields are all optional.
- no suppression effect.

# Structure
A list of typed sub-regions, plus optional `required:` obligations.

```yaml
meta:
  - required: myMeta        # every concrete subtype must carry it, see [[type-def required meta]]
  - type: myMeta
    myField: <value>
  - type: myOtherMeta
    myField: <value>
```
