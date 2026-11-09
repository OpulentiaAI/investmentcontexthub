The merged field set a [[type-instance]] must satisfy.
Computed across its [[type closure]].

# Properties

## Field union
The union of fields declared by every type in the [[type closure]].
- a single claim gathers down its parent chain.
- a mixin gathers across every claimed type's chain.

## Same-named fields
Two chains may reach a field of the same name.
- token-equal shapes auto-unify into one.
- anything else must be resolved.

The rules and the field qualifier are [[type-def fields collision - auto-unify and qualified field]].

# Structure
Single claim, fields gather down the chain:
```yaml
# myNote      declares  description
# myDecision  (parent myNote)  declares  status

type: myDecision
description: <value>   # from myNote
status: <value>        # from myDecision
```

Mixin, fields gather across claims:
```yaml
# myNote        declares  description
# myDeliverable declares  audience

type:
  - myNote
  - myDeliverable
description: <value>   # from myNote
audience: <value>      # from myDeliverable
```

Same-named fields across mixed chains follow [[type-def fields collision - auto-unify and qualified field]].
