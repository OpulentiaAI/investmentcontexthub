A contract that a [[type-def body]] scope must contribute to named fields.
One of the [[type-def body]] items.

# Properties

## Contract, not routing
`fills:` requires the scope to contain a contribution to each named field.

Contributions are self-tagged at their site,
`fills:` does not route them.

See [[type-instance body contribution]].

## Exclusive, `fills!:`
`fills!:` forbids any contribution to a field outside the named set.
- [[spec - diagnostic codes^fills-contract-exceeded]].

A scope cannot carry both forms:
- [[spec - diagnostic codes^fills-double-form-declaration]].

## Scope
- on a [[type-def body section]], the section's content.
- at the top of a [[type-def body]], anywhere in the body.

## Nesting
A contribution counts toward every enclosing scope's contract.

Exclusivity propagates downward.
- a nested conflict is a load error:
  - [[spec - diagnostic codes^fills-contract-conflict-nested-exclusivity]].

## Bound field
Must exist in the type closure:
- [[spec - diagnostic codes^fills-unknown-field]].

Its shape is unconstrained.
Every shape can be carried in prose, so any field is a valid target.
- a primitive or enum, by the inline marker or a fence.
- a reference or def-ref, by a wikilink.
- a record, by a fence reading as a record.
- `opaque`, by a fence read verbatim; `any`, by a fence read by value-shape.
- a compound, by whichever branch the content selects.

`fills:` is a contract about PRESENCE.
Whether a value lands on the branch its author intended is a value-layer question, see [[type value container]].

## Unmet
A scope with no matching contribution is an error:
- [[spec - diagnostic codes^fills-contract-unmet]].

# Structure
```yaml
body:
  - fills: myField          # body-level, satisfied anywhere in the body
  - section: My Section
    fills:                  # multiple fields
      - myFieldA
      - myFieldB
  - section: Focused
    fills!: myFocusField    # exclusive, only this field
```
