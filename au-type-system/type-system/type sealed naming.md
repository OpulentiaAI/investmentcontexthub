The dot-separated naming convention for [[type-def sealed]] leaves.

# Properties

## Convention
A leaf of a sealed parent `myParent`
is named `myParent.mySubtype`.

## File path
The path mirrors the name.
- `type/decision.decided.type.yaml`

A sealed family is N files, one per leaf, each at its mirrored path.

## Lint, not load
A convention only.
The loader accepts any dotted name conforming to [[type-def legal names]].

A non-`parent.`-prefixed leaf emits a lint warning.

## The dotted form carries no engine meaning
The `.` is inert to the engine, a name is one atomic identifier, see [[type-def legal names]].
- the whole name is the identity, the `.leaf` has no independent meaning.
- family membership is the parent's `sealed:` branch list plus [[type-def extends]], never the shared prefix.
- a leaf named without the prefix (`myLeaf` extending `myParent`, listed as `myLeaf` in `sealed:`) is a valid family member, only the lint nudges the dotted name.

So this convention is a reading aid for humans, never a structural relation.

# Structure
```yaml
# type/myParent.type.yaml
sealed:
  - myParent.myFirstLeaf
  - myParent.mySecondLeaf

# type/myParent.myFirstLeaf.type.yaml
extends: myParent
fields:
  myField1: <shape>

# type/myParent.mySecondLeaf.type.yaml
extends: myParent
fields:
  myField2: <shape>
```
