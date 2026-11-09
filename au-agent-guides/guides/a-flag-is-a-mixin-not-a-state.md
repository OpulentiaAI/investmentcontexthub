---
type: guide.gotcha
goal: "Represent a property that varies independently of a lifecycle."
rule: "Keep independent dimensions separate; use a value field for local data or a mixin for shared type membership."
example:
---

# Keep independent dimensions separate

Model an independent property separately from the lifecycle.
Urgency, for example, can vary whether work is open or complete.
A lifecycle branch for every combination makes the family harder to understand and evolve.

**Choose data or membership**

Use a Boolean or enum field for ordinary data on the record.
Use a mixin when shared type membership matters or the capability carries a coherent group of fields.
A fieldless tag is the smallest such contract.
A flag alone does not justify a new type.

**Choose who claims it**

A tag on a subtype makes every instance a member.
A concrete tag claimed by an instance makes membership local to that instance.
An abstract trait needs a concrete identity through which it can be reached.

[[supersede::au-base-types:example]] carries a field as an independent capability alongside a domain kind.
The combinations do not each need a lifecycle state.

**Check dependencies between dimensions**

Keep dimensions separate while they are independent.
Model or check any combination that needs different obligations.
Adding a mixin does not express “this flag is legal only in the open state.”

Vary the property while holding the lifecycle state fixed.
If both records make sense, choose a field or shared membership according to the consumer.
Then test combinations that must be disallowed.
