The optional `extends:` key on a [[type-def]].

# Properties

## Parent claim
Names the parent type-def(s) this type extends.
A type-def with no `extends:` has no parent.

## Inheritance
Parent fields flow down through the [[type effective shape]].
Subtyping is [[type subtyping width-only]].

## Cross-repo parent
A parent may name a peer's type, `extends: base::repo`.
- the peer's type folds in as an ancestor.
- see [[type repo qualifier]].

## Distinction from the identity claim
The parent claim and the identity claim are separate keys.
- `extends:` on a type-def names the parent(s) it extends.
- `type:` on a [[type-instance]] names what a file IS, see [[type-instance type]].
- an inline record and a meta block also claim identity with `type:`, so `type:` is the identity claim at every position.

# Structure
One parent, or several.
- single: `extends: myParentType`
- multiple:

```yaml
extends:
  - myParentType
  - myOtherParentType
```

Form follows [[type list form]].
