Constraints the type system places on a writer of a [[type-instance]].

# Properties

## Write-direction Liskov is operational
Read-direction Liskov holds by construction,
see [[type subtyping width-only]].
A leaf's contract always implies its parent's.

The write direction does not hold structurally.
A value valid for a parent may be invalid for a leaf.
A leaf can declare new required fields the parent omits,
so a parent-typed writer does not know to supply them.

## Read before write
Required, not incidental:
- a modify recovers the precise leaf from the file's [[type-instance type]] claim, before editing.
- a create knows the leaf at design time.

A parent-typed write API without a preceding read reintroduces the gap.

## Validator backstop
Any on-disk value violating its leaf's contract is diagnosable.
A cut-corner write is recoverable, not silent.

## Migration as resolution
When a new value is invalid for the current leaf but valid for a sibling leaf,
tooling proposes switching the [[type-instance type]] claim,
and prompts for the newly-required fields.

This is the leaf-promotion path of [[type graph evolution]].

## Bulk writes
The type system prescribes no bulk-write strategy.

Validator diagnosability makes optimistic-write-then-validate viable.
Failures are recoverable rather than silent.

Concurrent edits with stale leaf inference are a concurrency concern, outside the type system.
The post-write validation is a recovery point regardless.
