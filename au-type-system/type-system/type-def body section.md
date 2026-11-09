A named heading in a [[type-def body]] template.
One of the [[type-def body]] items.

# Properties

## Heading
`section:` names the exact heading text.

## Optional, `section?:`
The heading may be absent from the instance.

When present, it keeps its templated position.

## Presence and order
A required section must appear at its templated position.
- absent is an error:
  - [[spec - diagnostic codes^body-section-missing]].
- out of order is an error:
  - [[spec - diagnostic codes^body-section-out-of-order]].

## Nesting
A section may carry its own `body:` for sub-sections.

Heading depth matches nesting depth, `#` then `##`.

## Optional keys
- `fills:` binds the section to a field,
  - see [[type-def body fills]].
- `guidance:` is a free-text hint for authors and agents
  - not validated.

# Structure
```yaml
body:
  - section: My Section
    fills: myField
    guidance: "What belongs here."
    body:
      - section?: My Optional Subsection
```
