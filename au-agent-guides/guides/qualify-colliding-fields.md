---
type: guide.pattern
goal: "Combine types that declare different fields under the same name."
rule: "Preserve distinct origins with qualified field keys when the combination is intentional, and check consumers can interpret it."
---

# Qualify fields from different origins

Qualify an instance's field keys when it intentionally combines contracts with different shapes under the same name.
The engine can unify fields whose shape tokens agree.
Divergent shapes can coexist when the instance identifies which origin each value fills.

**Select the origin**

Suppose local-task and remote-issue declare different status enums.
An instance carrying both can state:

```yaml
type: [local-task, remote-issue]
status{local-task}: open
status{remote-issue}: queued
```

The qualifier selects a field origin in the instance's closure.
Add a repository qualifier inside the braces when needed to disambiguate it.
A qualifier that reaches both divergent origins is still ambiguous.

Supply a value for each required origin.
A bare status does not choose one.

**Keep both meanings clear**

Qualification fits when preserving both existing contracts expresses the domain accurately.
For a new combined API, distinct field names may be clearer.
Equal shapes do not prove equal meaning either: two String fields can describe different facts.

A subtype still cannot redeclare an inherited field.
Qualification does not override that rule.
See [[design-for-growth]].

**Check the reader as well**

Inspect the resolved values and the generated schema or reader that consumes them.
A consumer expecting one unqualified value per name may not support this valid engine representation.

Let the engine check required origins and ambiguous keys.
Judge whether the consumer preserves both meanings.
Use a focused probe when its treatment of qualified fields is uncertain.
