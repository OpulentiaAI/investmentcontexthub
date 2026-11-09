A `required:` item inside a [[type-def meta]] list.
Obligates every concrete type extending this base to carry a meta of a named type.

# Properties

## Declaration
A `required:` item names the meta types every concrete subtype must carry.
- the value is one name, or a list, per [[type list form]].
- it sits beside ordinary `type:` value blocks in the same `meta:` list, discriminated by the `required:` key.
- opt-in, a plain `- type: X` value block carries NO obligation.
- a base MAY also carry its own `type: X` value block for a required type, allowed, not required.

## The named type must be a meta type
A `required:` names a META type, its closure includes the marker.
- a present type that is not meta-legal is [[spec - diagnostic codes^required-meta-not-a-meta-type]].
- the base-side sibling of [[spec - diagnostic codes^non-meta-type-in-meta-position]], see [[type-def meta marker]].
- an absent type is [[spec - diagnostic codes^required-meta-absent-type]].
- a bad shape (not a name or list of names) is [[spec - diagnostic codes^required-meta-bad-shape]].

## Who is on the hook
Every NON-ABSTRACT type whose [[type closure]] includes the declaring base.
- the closure is reflexive, so a CONCRETE declaring base is itself on the hook.
- a subtree walk, every concrete descendant, not just direct children.
- abstract and sealed types are exempt, they are not instance-claimable, see [[type-def abstract]].
  - exempt from SATISFYING, an abstract type still carries `required:` and its own value blocks freely.

## Satisfaction is literal, and by closure
A concrete type satisfies by declaring, in its OWN `meta:`, a value block of the required type.
- by CLOSURE, a block whose type's closure includes the required type satisfies it.
  - the same width-only rule as a `tool-presentation*` reference, see [[type subtyping width-only]].
- LITERAL, the subtype must declare its own block, [[type-def meta]] ancestor surfacing does NOT satisfy.
  - surfacing still serves reads, the obligation demands the subtype's OWN declaration.
- `meta: []` does NOT exempt, an emptied meta declares no block, so the obligation is unmet.

## The violation
A concrete type on the hook with no satisfying block fires [[spec - diagnostic codes^subtype-missing-required-meta]].
- a `warning`, advisory, per [[type open-world validation]], growth is never blocked.
- one per unmet obligation, anchored at the offending def, `related` at the base's `required:`.

## The read
The same computation is exposed as a read, so a consumer gates without parsing diagnostics.
- per non-abstract type, its set of UNMET required-meta obligations, empty when satisfied.
- a base's declared `required:` set is exposed too.

## Identity
The obligation folds into the declaring type's `(name, ClosureHash)` identity.
- contract-shaped, it changes the valid-subtype contract, like a required field.
- the referenced meta type's closure folds in too.
- descriptive value blocks stay EXCLUDED from the hash, the obligation is contract, the value is not.
- folded ONLY WHEN PRESENT, a type with no `required:` has an unchanged canonical form.

## Cross-repo
The obligation composes across a repo boundary.
- a subtype extending a peer's base inherits the base's obligation.
- the required meta type may itself be a peer, `required: tool-presentation::sdk`.
- checked in the importing repo's resolution graph, compared by `(name, canonical-hash)`, see [[cross repo typed graph]].

# Structure
```yaml
# base, abstract
abstract: true
meta:
  - required: myMeta                # every concrete subtype must carry it

# a concrete subtype
extends: myBase
meta:
  - type: myMeta
    myField: <value>               # satisfies the obligation
```
