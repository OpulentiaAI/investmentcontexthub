A `[[target]]` value,
filling a slot whose [[type-def field shape]] admits a reference.

It resolves to a file.
A bare `^block-id` is navigational, the file is the referent and `^block-id` a jump anchor.
A `^^block-id` (double caret) is a block-referent value, the typed block or inline record is the referent.
See [[type block-id]].

How a `[[target]]` name maps to a file is [[reference name resolution]].
The optional `::repo @commit #head ^ ^^ :field` fragments are [[wikilink fragments]].

# Properties

## When a value is a reference
Both must hold:
- the slot admits a reference.
  - `T*`, `T&`, `file*`, or a reference branch of a compound.
  - see [[type-def shape suffixes]].
- the value is exactly one `[[...]]`.

A wikilink that misses either is not a reference:
- a whole-value `[[x]]` in a [[type-def shape primitive]] slot is the string `[[x]]`.
- a `[[x]]` inside a longer string is part of that string.

Not a reference is not inert.
A well-formed `[[...]]` stays navigational, see [[#Navigational versus validated]].

## Navigational versus validated
Two orthogonal properties of a `[[...]]`.

Validated reference:
- fills a typed slot, checked against its demanded type.
- needs both conditions above.
- a dangling target is an error, [[spec - diagnostic codes^reference-target-missing]].
- an ambiguous target, resolving to two or more files, is an error, [[spec - diagnostic codes^reference-target-ambiguous]].

Navigational link:
- a clickable, followable edge in the graph.
- holds for any well-formed `[[...]]`, wherever it sits.
  - a bare `[[target]]` in body prose.
  - a whole-value `[[x]]` in a primitive slot.
  - a `[[x]]` embedded in a longer string value.
  - a `[[x]]` in a `#:` docstring, tagged with a docstring origin, see [[type docstring]].
- the one exception is an [[type-def shape opaque]] field, whose content is uninterpreted and forms NO edge.
  - the intent, the edge suppression is not yet wired, so a `[[...]]` in an `opaque` field currently still surfaces, see [[type-def shape opaque]].
- fills no slot, contributes to no field.
- counts as an outgoing edge, surfaced resolved or broken.
- a dangling target is a warning, [[spec - diagnostic codes^navigational-target-not-found]], never an error.
- an ambiguous target is a warning too, [[spec - diagnostic codes^navigational-target-ambiguous]], the same open-world stance.

So missing and ambiguous are both surfaced on both surfaces, error when validated, warning when navigational.

A whole-value `[[x]]` in a `T*` slot is both.
A `[[x]]` embedded in a `String` value is navigational only.

In the body, attribution adds a case:
- a `[[target:field]]` contributes mid-prose, see [[type-instance body contribution]].
- a bare `[[target]]` contributes nothing.

## Forms
- `name*`
  - the target's `type:` closure must include `name`.
- `name&`
  - same constraint, the reference case of inline-or-reference.
- `file*`
  - the built-in [[type-def shape file]].
  - a whole file by existence, no closure check.
  - a `^block-id` or `#head` on the value is rejected, `file*` references the whole file.
  - a `file` branch of a compound admits a whole-file reference, never a `^^` block-referent, a block is not a whole file, so `^^` must satisfy a non-file branch.
- `any*` / `any&`
  - the built-in [[type-def shape any]] reference forms.
  - any node by existence, no closure check, a `^block-id` target allowed.
- `type<T>*` / `type*`
  - the built-in [[type-def shape def-ref]], a typed reference to a [[type-def]].
  - the target is a `.type.yaml` file, checked on the def axis, not the instance axis.
  - whole-def only, a `^block-id` is meaningless, the def is the unit.
- any reference form, commit-pinned by an `@commit` fragment.
  - `[[file::@commit]]` resolves against that commit's tree, not the working tree.
  - deletion-stable, the edge survives the live file's removal.
  - the `*@` shape postfix demands a pin, see [[type-def shape suffixes]].
  - see [[wikilink fragments#Commit-pinned references]].

A target whose closure misses the demanded type is an error:
- [[spec - diagnostic codes^reference-target-type-mismatch]].

A `type<T>*` reference checks the def axis instead:
- the target must be a type-def, else [[spec - diagnostic codes^def-ref-target-not-a-type-def]].
- the target's [[type-def extends]] parent closure must include `T`, else [[spec - diagnostic codes^def-ref-closure-mismatch]].
- `type*` skips the closure check, any type-def by existence.

## Target is a file or block, never a primitive
A reference resolves to an addressable entity:
- a file claiming a record
  - files identity is its [[type-instance type]] claim.
  - `file*` relaxes this to any whole file by existence, including untyped assets.
  - `any*` relaxes it to any node by existence, see [[type-def shape any]].
- a typed block claiming a record
  - a marked fence in prose
  - see [[type-instance body contribution]].
- an inline record carrying a `^:` id
  - its effective claim is the explicit inline `type:`, else the slot-pinned type.
  - see [[type block-id]].

A primitive is neither.
`String`, `Number`, and the other [[type-def shape primitive]]s name value shapes.
- Files can not claim primitives
- marked fences can not claim primitives

So `*` and `&` cannot attach to a [[type-def shape primitive]] or [[type-def shape enum]]:
- [[spec - diagnostic codes^shape-syntax-error]].
- see [[type-def shape suffixes]].

## Primitive-vs-reference union
In `<String | T*>` the whole-value `[[...]]` pattern selects the reference branch.
Non-matching strings stay plain values.

Parallel to the `Url` prefix rule,
see [[type-def shape primitive]].

# Structure
A reference fills a slot in frontmatter or an inline value.
The YAML key names the field,
so no `:field` fragment appears here:

```yaml
# slot:  myField: myType*
myField: "[[myTarget]]"            # resolves to a file

# slot:  myField: myType&
myField: "[[myTarget^myBlockId]]"  # resolves to a typed block or inline record in that file
myField: "[[^myBlockId]]"          # the same, in the current file

# path vs basename
myField: "[[notes/myTarget]]"      # repo-relative path, exact match
myField: "[[myTarget]]"            # basename, case-insensitive
```

A [[type-instance body contribution]] adds the `:field` fragment to name its target:
```markdown
The rationale is [[myTarget:myField]].
```
