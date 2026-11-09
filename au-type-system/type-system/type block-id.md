A `^block-id` addressing one block or inline record inside a file.

# Properties

## General-purpose addressability
Two attachment surfaces:
- a `^block-id` marker on any body block:
  - a heading
  - a paragraph
  - a marked fence
- a `^:` key on an inline record,
  see [[type-def shape record]].

Attaching one is always legal.
No type declares it.

## Marker placement
A body marker attaches two ways:
- trailing, the line's last whitespace-separated token.
  - `A paragraph. ^id`
  - a heading's text excludes its marker, section matching is unaffected.
- own-line, directly below the block.
  - the form a fence requires, after the closing fence.

`word^id` glued to prose is not a marker.

## Id grammar
An id is `[A-Za-z0-9_-]+`.
Same rule on both surfaces.

The body parser skips a malformed marker silently, it reads as prose.
A malformed `^:` value is surfaced, an explicit key cannot be prose.

## Engine-assigned ids
Ids are hand-authored or engine-assigned.
The mutation channel's `assign_block_id` implements lazy id-on-reference:
"reference this thing" → the engine assigns the id and returns the ref.
- engine-assigned ids carry a `b-` prefix, collision-checked within the file.
- a record already carrying an id returns it unchanged, assignment is idempotent.

## `^:` is identity-layer
A reserved key beside the inline `type:` claim.
- never a field, field names cannot be `^`, see [[type-def legal names]].
- validation skips it, it never lands in [[type extras]].
- the candidate scan ignores it.
- the value is the bare id, the key carries the sigil.

At instance frontmatter root it is a warning.
The file is addressable by name.

## File-local, globally unique
A block-id is unique within its file,
across both surfaces.
The full `[[file^block-id]]` is globally unique.

A duplicate within one file is an error:
- [[spec - diagnostic codes^block-id-duplicate]].
- body marker vs record id collide like marker vs marker.
- references resolve to the first occurrence only.

## Typed block
A typed block is a marked fence (` ```[:field] `) carrying a `^block-id`.
See [[type-instance body contribution]] for the fence form.

Its own `type:` claim is what a [[type reference]] to it satisfies, not the host file's.

## Addressable inline record
An inline record carrying `^:` is a reference target.

Its effective claim is what the reference satisfies:
- the explicit inline `type:` when present.
- else the type the slot pins, see [[type-def shape record]].

A record under a union or sealed slot without an explicit claim is already an error,
so every resolvable record has a claim.

## Resolution as a reference
A block-id fragment carries a MODE, decided by the link, not by the target's state.
- bare `[[file^block-id]]` is NAVIGATIONAL.
  - the FILE is the referent, its claim checks the slot, `^block-id` is a jump anchor.
  - parallels a `#head` anchor, see [[type reference]].
  - a bare marker with no fence is valid, navigation needs no type.
  - a missing id is a dangling anchor, [[spec - diagnostic codes^navigational-block-id-not-found]] (warning), the file the referent, no type check.
- `[[file^^block-id]]` is a BLOCK-REFERENT value. (double caret)
  - the block (not the file) is the referent, its claim checks the slot.
    - in a typed slot, a reference edge: the value is the wikilink, resolving to the block, no copy.
    - in a body contribution, the block's typed value is contributed into the host field, see [[type-instance body contribution]].
  - a typed block or an addressable inline record resolves.
  - a plain (untyped) block is [[spec - diagnostic codes^block-id-not-typed]], `^^` demanded a typed value.
  - an absent id is [[spec - diagnostic codes^block-id-not-found]].

Both modes apply on both surfaces, a frontmatter typed slot and a body contribution.
- bare block-id in a typed slot is navigational, double-caret marks a block-referent value.

## Local form
`[[^block-id]]` resolves within the host file.
Empty name means the current file,
see [[type reference]].

# Structure
````markdown
---
type: myType
myRecords:           # slot: myRecordType[]
  - ^: myRecordId
    myInner: <value>
---

A paragraph, navigationally addressable. ^myParagraph

```yaml [:myField]
type: myRecordType
myInner: <value>
```
^myTypedBlock
````

`[[thisFile^myTypedBlock]]` resolves to the typed block.
`[[thisFile^myRecordId]]` resolves to the inline record.
`[[^myRecordId]]` resolves the same, from inside the file.
`[[thisFile^myParagraph]]` is navigational only.
