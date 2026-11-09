The types a [[type-instance]] could claim but does not.
Surfaced on demand.

# Properties

## Qualification
A [[type-def]] is a candidate when:
- its required fields are all satisfied by the instance's top-level fields.
  - whether those land in the [[type closure]] or as [[type extras]].
- each value conforms to the declared shape.
- it is not already in the closure.

## Fully satisfied only
Partial matches do not surface.

A [[type tag]] never surfaces.
Zero required fields would match every file.

A [[type-def abstract]] type never surfaces.
A claim on it is impossible, so the suggestion would be unactionable.

## Advisory
Never validates or invalidates a file.

Promotion is a one-line edit,
adding it to the [[type-instance type]] mixin.

## Nested
The same scan runs inside inline values,
against each value's own scope.

It recurses, and a candidate attaches to its source scope.

A claim-less slot-pinned record is skipped.
- its identity is the slot's, see [[type-def shape record]].
- promotion would write an explicit claim, which replaces the pin and breaks the slot.
- the scan resumes once the record carries an explicit `type:`.
- nested values inside it still scan, against the pinned type's shape.

## Ranking
By specificity, a larger required-field set ranks higher.
Ties broken by also-satisfied optional fields.

Discovery and ranking are the engine's contract.
Presentation is the consumer's.

# Structure
```yaml
# type/myType.type.yaml
fields:
  myField: <shape>

# type/myOtherType.type.yaml
fields:
  myOtherField: <shape>

# an instance not claiming myType
type: myOtherType
myOtherField: <value>
myField: <value>      # satisfies myType, here an extra

# the scan surfaces: myType
# promote by adding it to type:
```
