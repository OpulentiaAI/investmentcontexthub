Declaration of a type.

# Properties

## File
A type-def file is classified by its name.
The `.type.yaml` / `.type.yml` suffix is the sole marker.
- location plays no part in classification.
- a nested `type/meta/x.type.yaml` classifies by its suffix, like any file.

Discovery is recursive across the whole knowledge base.
Not limited to a single top-level `type/`.
Nested sub-projects authoring their own types are picked up.

The `type/` directory is an authoring convention, not a classification rule.
- a type-def outside a `type/` directory is an advisory warning, never a reclassification.
- [[spec - diagnostic codes^type-def-outside-type-dir]].
- so a prose `README.md` under `type/` is a plain note, not a forced type-def.

## Name
Its name is unique across the knowledge base.
It conforms to [[type-def legal names]].

A name is one atomic identifier, the engine reads no structure from it.
- `a.b.c` is a single name, not a path, and `c` has no meaning on its own, see [[type-def legal names]].

Two files deriving the same name are a load error:
- [[spec - diagnostic codes^duplicate-type-def]].

## Brand or record
A def is a record or a brand, never both.
- a record declares `fields:`, the default kind these atoms describe.
- a [[type-def brand]] declares `shape:` in place of `fields:`, naming a scalar, enum, union, or tuple.
- `shape:` beside a record key is [[spec - diagnostic codes^brand-with-record-keys]].

## Instantiation
Claimed by a [[type-instance]] through [[type-instance type]].

## Inheritance
Inheritance works through [[type subtyping width-only]].

## Evolution
Changes across versions are governed by [[type graph evolution]].

## Documentation
A `#:` block before the first key documents the type-def.
See [[type docstring]].

# Structure
Reserved keys, all optional.
`fields:`, `sealed:`, `abstract:`, `meta:`, `body:`, `shape:`, and `location:` are type-def-only.
On a [[type-instance]] they are a load error:
- [[spec - diagnostic codes^reserved-key-on-instance]].

- [[type-def extends]]
  - parent claim(s).
- [[type-def fields]]
  - the type's own field declarations.
- `shape:`
  - names a scalar, enum, union, or tuple instead of fields, see [[type-def brand]].
- [[type-def sealed]]
  - closed set of permitted branches.
- [[type-def abstract]]
  - non-claimable-but-open marker, `sealed` is abstract plus closed.
- [[type-def meta]]
  - type-level metadata
  - never flows to a [[type-instance]].
- [[type-def body]]
  - authoring template for [[type-instance]] prose.
- `location:`
  - where this type's instances live, advisory, out of identity.

```yaml
# file: myType.type.yaml
# optional parent
extends: <type name>
# optional fields
fields:
  <field items>
# optional sealed leaves
sealed:
  - <sealed items>
# optional non-claimable marker
abstract: true
# optional body
body:
  - <body items>
# optional meta
meta:
  - <meta item>
```