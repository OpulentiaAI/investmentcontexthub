The `fields:` key on a [[type-def]].

# Properties

## Own declarations
An optional map of the type's own field declarations, keyed by field name.
A type with no fields is a [[type tag]].
Values come from a [[type-instance]], through [[type-instance fields]].

## Name with required or optional shape
Each field has a name and a [[type-def field shape]].
The optional marker `?` sits on the name side.
- `myField: <shape>` is required.
- `myField?: <shape>` is optional.

## No redeclaration
A subtype may not redeclare a field a parent already carries.
See [[type subtyping width-only]].

## Unique names
A field name is declared once per type-def.
A second declaration of the same name is an error.
- [[spec - diagnostic codes^duplicate-field]].
- distinct from [[#No redeclaration]], which is a subtype redeclaring an ancestor's field.
- the map keys the declarations by name, so a duplicate is a duplicate mapping key.

## Collision
Same-named fields reached through mixed parents resolve by [[type-def fields collision - auto-unify and qualified field]].

## Documentation
A field declaration may carry a `#:` docstring.
See [[type docstring]].

# Structure
A map, each entry one field declaration, `name: shape`.
An explicit empty map, `fields: {}`, marks a [[type tag]], the same as omitting `fields:`.

```yaml
fields:
  myField: <shape>
  myOptionalField?: <shape>
```
