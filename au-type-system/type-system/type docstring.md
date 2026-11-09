A `#:` comment the engine captures and surfaces, attached to the declaration it sits on.

# Properties

## Intended documentation
Distinct from a plain `#` comment, which is incidental and dropped.
The `:` sigil marks documentation meant to surface.
The `///` to a plain comment's `//`.

## Advisory only
A docstring never affects validation.
Metadata for consumers.
- hover
- completion
- codegen

## Navigational links
A `[[...]]` in a docstring is a navigational edge, see [[type reference#Navigational versus validated]].
- a clickable, followable edge, tagged with a docstring origin and its binding declaration.
- navigational only, it fills no slot, contributes no value, and never validates.
- a dangling or ambiguous target is a warning, never an error, the same open-world stance as body prose.
- only navigational fragments apply, the value-bearing `:field` and `^^block-id` carry no docstring meaning.
- the edge is derived from the text, so a docstring stays advisory and out of the closure hash.

## Attachment
Binds to the nearest declaration.
- a trailing `#:` binds to its own line's declaration.
- leading `#:` lines accumulate, then bind to the next declaration.
- both forms may appear on one declaration.

Surfaces on a [[type-def]]:
- a [[type-def fields]] declaration.
- the [[type-def]] itself, via a `#:` block before the first top-level key.
  - it sits above `extends:` and `fields:`, so it documents the def, not a field.
  - leading-block only, a trailing `#:` on the `extends:` / `fields:` line dangles.
- a [[type-def meta]] block, its head doc and each field doc.
  - a meta block is a structured record, so it documents like a nested inline record.

Surfaces on a [[type-instance]] too, the same sigil on the value surface.
- a frontmatter field, trailing or leading its key.
- the instance itself, a `#:` block before the first frontmatter key, above `type:`.
- a nested inline record, its own leading-block head doc plus each of its field docs.
  - see [[type-def shape record]], the head doc binds before the record's first key.
- a record-bearing body fence, over its yaml content, see [[type-instance body contribution]].
  - a fence reading verbatim, a `String` or `any` slot, carries no docs, its content is literal.

A record or container field's doc is leading-block only, like the type-def head.
- a `#:` block BEFORE a container field documents that field.
- a `#:` block INSIDE, before the record's first key, is the record's head doc.
- a trailing `#:` on the container's own key line is ambiguous between the two, so it dangles, never silently guessed.
- a scalar field still binds a trailing `#:`, that names the field unambiguously.

An instance doc is the same advisory metadata, surfaced as read data for consumers.
- a projection reads a step's intent-comment beside its value, shows it, and round-trips it.
- the write half already preserves it, a byte-splice edit never re-renders the comment.

## Capture
The YAML parser drops comments.
The engine recovers a `#:` doc by a span-aligned pass over the source.
- it reuses each declaration's byte span.
- it respects YAML string lexing, a `#` inside a quoted value is not a comment.

The head-and-fields pass covers the [[type-def]] head and its [[type-def fields]].
- it skips the [[type-def meta]] and [[type-def body]] value ranges.
- the [[type-def body]] range is a free-form prose template, so a `#:`-looking line there is prose, never a doc.

A separate pass captures the docs inside each [[type-def meta]] block.
- a meta block is a structured record, not free-form text, so it documents like a nested inline record.
- its head doc, each field doc, and each nested-record doc.

The same head-and-fields pass runs over a [[type-instance]]'s yaml surfaces.
- its frontmatter, and each body fence a record-bearing slot reads as a record.
- it aligns to instance fields and nested-record heads by their byte spans, the value-surface twin of a def's head and fields.
- it skips free-form value ranges the same way, a block scalar or a verbatim `String` / `any` fence holds content, not docs.

## Dangling doc
A `#:` that binds to no declaration is a warning.
- [[spec - diagnostic codes^dangling-doc-comment]].
- the same on an instance surface, a `#:` attaching to no field or record.

# Structure

A type-def, head doc plus field docs:
```yaml
#: an atomic text region in a PDF
fields:
  page-doc: Number   #: page in the file
  quote: String      #: verbatim text of this region
  #: short context string before the quote
  prefix?: String
```

An instance, the same sigil on the value surface:
```yaml
#: the release checklist, human-gated
type: workflow
owner: alice           #: who signs off
steps:                 # a list of step records
  - ^: build
    gate: manual       #: reviewer confirms the signature
    run: make image
```
The instance head doc, the `owner` field doc, and the nested `gate` field doc all surface as data.
