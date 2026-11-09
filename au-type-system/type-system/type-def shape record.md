A bare [[type-def]] name, filled by an inline record value.
One of the [[type-def field shape]].

# Properties

## Inline record value
The slot takes a YAML map mirroring a file's frontmatter.
A [[type-instance type]] claim plus the type's fields.

Two surfaces carry it, both reading as a record because THIS slot demands one.
- a frontmatter value.
- a marked body fence, see [[type-instance body contribution]].

## Resolution
The bare name must resolve to a [[type-def]] in the graph.
A slot naming an absent type is a load error:
- [[spec - diagnostic codes^slot-references-absent-type]].

The bare-name slot is shape-agnostic, its meaning is decided at resolution.
- a name resolving to a record demands an inline record value.
- a name resolving to a [[type-def brand]] demands the brand's shape, a scalar, enum, union, or tuple.
- the inline `type:` claim is to a record what the `Name(...)` constructor is to a nominal brand, see [[type brand constructor]].

## Nesting
An inline value may contain further inline values.

Mirroring the file structure it would have if extracted.

## Type claim
The inline `type:` is optional when the slot pins a single type-def.

Required at a NON-claimable ceiling, a [[type-def sealed]] parent or a [[type-def abstract]] type, and at a union or an intersection slot.
- without it the record would synthesize the ceiling's own identity, an implicit claim of a non-claimable type.

Errors:
- [[spec - diagnostic codes^inline-value-missing-type]].
- [[spec - diagnostic codes^inline-value-type-not-compatible]].

### It also disambiguates a body fence
A marked fence reads by the slot, and a union slot has no single answer.
The same `type:` settles it, see [[type-instance body contribution]].
- content parsing to a mapping that carries `type:` reads as the RECORD branch.
- anything else reads as the TEXT branch.

One rule, two positions.
- pinned slot infers, union demands explicit.
- it governs the frontmatter value and the body fence alike.

## Addressability
An inline record may carry a `^:` key, a block-id.
A reserved key beside `type:`, never a field.

Makes the record a [[type reference]] target,
`[[file^id]]` cross-file, `[[^id]]` within the file.

Rules and grammar live in [[type block-id]].

## Reference form
A `*` or `&` suffix turns the slot into a [[type reference]] instead.
See [[type-def shape suffixes]].

The target declares its own `type:`:
- a file, in its frontmatter.
- a typed block, via [[type-instance body contribution]].
- an addressable inline record, explicit `type:` or slot-pinned, see [[type block-id]].

# Structure
A bare type-def name.

The value is an inline record:
```yaml
# slot:  myField: myRecordType
myField:
  type: myRecordType
  myInnerField: <value>
```

With a `&` or `*` suffix the value is a reference instead.
See [[type-def shape suffixes]].
```yaml
# slot:  myField: myRecordType&
myField: "[[myFile]]"             # a file
# or
myField: "[[myFile^myBlockId]]"   # a typed block, or an inline record carrying ^: myBlockId
```
