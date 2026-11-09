The whole-system view.
What the atoms add up to, and the guarantees that fall out.

The atoms are the parts.
This is the shape they form together.

# Guarantees

**Decidable.**
Every check terminates.
The closure walk is acyclic, see [[type closure]].

**Linear-time at validation.**
Effective shape is linear in chain-depth times declared fields.
See [[type effective shape]].

**Gradual-friendly.**
Files arrive partially typed and still validate.
Extras pass as advisory, see [[type open-world validation]].

# Principles

**Width-only subtyping.**
Subtypes only add.
Avoids variance traps, keeps a leaf's contract implying its parent's.
See [[type subtyping width-only]].

**The parent declaration is the single source.**
No redeclaration, no reshape.
Removes whole categories of drift.

**Instances claim identity, type-defs carry meta.**
Two layers, each one job.
Identity is what a file IS, see [[type-instance type]].
Meta is type-level and never reaches an instance, see [[type-def meta]].

**Mixin is the universal multi-claim mechanism.**
One mechanism for single-claim and multi-claim files.
Auto-unify on identical shapes, a field qualifier on collision.
See [[type-def fields collision - auto-unify and qualified field]].

**Sealed parents are the only named sum in the graph.**
Closed-world, exhaustive, queryable.
A slot union or intersection is a constraint on a slot, not a new type.
A `<A | B>` is sum-shaped but anonymous, sealing is the only route to a named one.
See [[type-def sealed]], [[type-def shape compound]].

**Frontmatter is the contract, the body is a surface.**
The body declares nothing.
It surfaces fields the frontmatter already declared, with prose context.
See [[type-instance body contribution]].

**Every contribution is self-tagged at its site.**
No routing by section.
A `fills:` contract checks a scope, it does not attribute.
See [[type-def body fills]].

**Provenance is first-class.**
A value carries every surface that produced it, plus its context.
See [[type value container]].

**Open-world by default.**
Growth is never rejected.
Stricter gates layer on top, against the same advisory stream.

**Repo-local by default, `::repo` to cross.**
A name resolves in its own repo, a `::repo` qualifier reaches a peer's.
The typed graph spans many repos over one qualifier.
See [[cross repo typed graph]].

# What it buys

- files written with partial information validate.
- agents and humans contribute without colliding.
- consumers project against named types without leaf-branching.
- queries are first-class.
- the type graph evolves additively in the common case.
  - breaking changes are diagnosable at load, see [[type graph evolution]].
- the vocabulary composes across repos, a peer's types fold in over `::repo`.
  - see [[cross repo typed graph]].
