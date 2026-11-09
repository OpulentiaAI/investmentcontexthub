A [[type-def]] with no fields, contributing identity only.

# Properties

## Identity only
No fields to supply.
The type contributes only its name to a [[type-instance]]'s closure.

## Not a separate kind
Just an empty record.
`fields: []`, or no `fields:` at all.

"Tag" is more a conceptual framing.

## Body template
A tag may still carry a [[type-def body]].
Then it acts as a prose template others claim.

## Not a candidate
A tag has zero required fields.
It never surfaces in the candidate scan,
it would match every file.

# Structure
```yaml
# type/myTag.type.yaml
fields: {}
```
