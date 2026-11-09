---
type: guide.pattern
goal: "Name and reuse a scalar, enum, tuple, or union without inventing a record."
rule: "Use shape: for a reusable value contract; introduce a record when the value needs fields, relations, or independent identity."
---

# Name a value contract

Use a named `shape:` to share a value contract across slots.
It can name:

- A scalar or refinement
- An enum
- A tuple
- A union

Sharing a value contract does not require a node.

**A name worth sharing**

These illustrative definitions name a constrained number and a vocabulary:

```yaml
# progress.type.yaml
shape: Number{>=0 & <=1}
```

```yaml
# review-state.type.yaml
shape: [draft, approved, rejected]
```

A field can use the name directly, such as `progress?: progress`.
Keep a refinement or enum local when it belongs only to that field.
Name it when owning and evolving the contract serves:

- Shared meaning
- A reusable constraint
- An API distinction

**Brands still hold values**

These nominal brands remain values:

- Scalar
- Enum
- Tuple

A bare compatible value in a single nominal slot acquires that slot's brand.
An explicit constructor checks the brand's name.

Two numeric brands cannot make a bare number's provenance inferable.
Use explicit constructors when the author needs to preserve that distinction.

**Unions choose existing shapes**

Nominal union members need their constructors.
Record members need a type claim.
Membership does not make the types inherit a common family.

An all-record union can support references.
Adding a star cannot make a scalar brand referenceable.

**When to use records**

Use a record when the concept needs:

- Named fields or relationships
- Metadata carried by an instance
- Independent identity

Use a sealed record family when mutually exclusive branches need their own obligations.
[[modeling-discrete-states]] develops that case.

Let the engine check values against the chosen contract.
Check that the generated or runtime consumer supports the shape and preserves the distinction the task needs.
Probe a boundary when that behavior is uncertain.
Engine support for a shape does not establish support in every consumer.
