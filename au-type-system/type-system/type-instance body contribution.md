A field value contributed from a [[type-instance]]'s markdown body.

# Properties

## Self-tagged
Every contribution names its target field at the site.
No routing by section.

A [[type-def body fills]] contract checks a scope,
it does not route.

## Heading lines are prose
A heading line carries no contributions.
- inline `` `[:field]` ``, wikilink contributions, and marked fences are not recognized within a heading.
- its text is pure prose, navigational via `#head`, see [[wikilink fragments]].
- a trailing `^block-id` marker is the one exception, recognized and stripped from the heading text, see [[type block-id]].

## Forms
Two carriers, split by EXTENT, plus the wikilink.
- a wikilink, `[[target:field]]`, for `T*` / `T&`
  - see [[type reference]].
  - the target may narrow to a block value with the block-referent `^^`: `[[target^^block-id:field]]`
  - a bare `^block-id` is navigational, so `[[target^block-id:field]]` contributes the FILE, `^block-id` an anchor.
- an inline marker, `` `[:field] value` ``, ONE line
  - so it carries a scalar and nothing else.
- a marked fence, ` ```[:field] `, MANY lines
  - the multi-line carrier, see [[#The fence content-form]].

Extent is the whole distinction between the two non-wikilink carriers.
Neither names a content type, the slot does.

The `field` name may carry a collision qualifier, `field{type}`, see [[#Qualified attribution]].

A `:field` never attaches to a `#head`.
- a heading is navigational, not an addressable value, so it can not be a source.
- see [[wikilink fragments]].

## Qualified attribution
The `:field` names a host field,
and that name may carry a collision qualifier,
`field{type}` / `field{type::repo}`.

It contributes to a divergent same-named field's specific origin,
the resolution of [[type-def fields collision - auto-unify and qualified field]].

Every carrier takes it.
- a wikilink
  - `[[target:field{type}]]`
  - `[[target:field{type::repo}]]`
- an inline marker
  - `` `[:field{type}] value` ``
  - `` `[:field{type::repo}] value` ``
- a fence
  - ` ```[:field{type}] `
  - ` ```[:field{type::repo}] `

The qualifier's `}` collides with no carrier close.
- `}` is not the `]` closing a `[:` marker, nor the `]]` closing a wikilink, so each carrier reads its own close first.
- the ONE collision is the `::` in a `{type::repo}` qualifier against the wikilink `::repo` scope, so that scan skips a `::` inside the braces, see [[wikilink fragments#Qualified field attribution]].

## The fence content-form
A marked fence is a MULTI-LINE CHANNEL.
The field's declared [[type-def field shape]] decides how its content reads.

This is [[type value container]]'s "reference-ness is decided by the slot", one step further.
The slot decides content-form on the same principle, so both surfaces agree.

### The language tag carries no engine meaning
The tag is a syntax-highlighter hint, optional and ignored.
- ` ```yaml [:field] `, ` ```md [:field] `, and a bare ` ```[:field] ` are the same contribution.
- a tag disagreeing with the slot is SILENT, no diagnostic.
- the marker may sit anywhere in the info string, so a tag stays legal beside it.

### The read the slot selects
- a record-bearing slot reads a YAML record
  - [[type-def shape record]], and the inline-or-reference `&` form.
- a `String` slot reads VERBATIM
  - the multi-line text case, the reason this form exists.
- a non-`String` primitive or enum slot reads a trimmed scalar
  - the same read the inline marker performs.
  - so identical authored content collapses across the two carriers, see [[#Collapse forces the scalar read]].
- an `opaque` slot reads VERBATIM
  - the uninterpreted inline case, the reason this form exists for multi-line data.
  - [[type-def shape opaque]] stores an inline value uninterpreted, so nothing parses it, not even into a record.
- an inline-admitting `any` slot reads by VALUE-SHAPE
  - bare `any` and `any&`, the interpreted top, see [[type-def shape any]].
  - a mapping reads as a record, anything else keeps its text, the same read an unresolved slot performs.
  - `any*` is reference-only, so it takes the reference-slot line below.
- a slot the engine cannot resolve reads by VALUE-SHAPE
  - an unresolved [[type-instance type]] claim leaves no effective shape, so there is no contract to honor.
  - a mapping is unambiguously structured, so it reads as a record, anything else keeps its text.
  - the same fallback the frontmatter surface uses with no slot, which is what keeps the two agreeing.
  - so a fence read is never proof of the slot's kind, see [[#An unresolved slot must still collapse]].
- a reference-only slot admits no fence
  - `T*`, `file*`, `any*`, `type<T>*`, and a `<A | B>*` compound.
  - a fence is inline content, and these carry no inline form at all.
  - the content is still CAPTURED, so the contribution exists and the error anchors to it.
  - [[spec - diagnostic codes^body-slot-shape-mismatch]], which carries a fence message shape beside its wikilink one.
  - only when the slot is known, an unresolved claim yields no shape and no verdict.

### Collapse forces the scalar read
A non-`String` primitive must parse, it cannot capture verbatim.
- `` `[:count] 42` `` yields the number, so a fence over `42` must yield the number too.
- otherwise the two carriers produce unequal values for identical content.
- unequal values do not collapse, so one authored value would count twice.
- on a bare slot that falsely fires [[spec - diagnostic codes^field-cardinality-exceeded]].

See [[type value container]] for the collapse rule this protects.

### An unresolved slot must still collapse
Collapse is why the no-slot fallback is value-shape rather than plain text.
- a frontmatter mapping reads as a record from its VALUE, no slot consulted.
- a fence of equal structure must reach the same value, or the two never collapse.
- so one authored value would count twice on an instance that is merely unresolved.

The two surfaces share one fallback, so they cannot disagree.

### Verbatim means the lines between the delimiters
The value is exactly the content lines, joined by their terminators.
- the terminator of the last content line belongs to the closing delimiter, not the value.
- no trimming, no dedenting, no yaml scalar folding.
- blank lines are preserved, so a multi-paragraph value survives intact.

### A union slot disambiguates by the inline `type:`
A union has no single answer, so the author disambiguates.
- content parsing to a mapping that carries `type:` reads as the RECORD branch.
- anything else reads as the TEXT branch.

One rule, two positions.
[[type-def shape record]] makes an inline `type:` MANDATORY at a union or intersection slot.
The pinned-slot-infers / union-demands-explicit split governs the frontmatter value and the fence alike.

Content parsing WHOLLY as a mapping that carries `type:` therefore reads as a record, even when it was meant as text.
- the whole fence must be well-formed yaml, so the residual is narrow.
- prose carrying a `type:`-shaped line does not parse as a mapping at all, and stays text.
- so it reaches structured key-value text, not ordinary prose.
- it fails loudly, never silently, see [[#Shape]].

## Cross-file block
A `^block-id` on a marked fence makes it referenceable from another file.
See [[type block-id]].

Another file pulls the block into its own field with the block-referent `^^`:
- `[[otherFile^^block-id:localField]]` contributes the block as a value to the host's `localField`.
- `:field` names the local receiving field, the target plus `^^block-id` is the value.
- a bare `[[otherFile^block-id:localField]]` instead contributes the FILE, `^block-id` a navigational anchor.
- holds whether or not the block also contributes locally via its own `` `[:field]` `` marker.
  - with the marker, the block also fills its own file's field.
  - without it, the block is a typed [[type extras]] that only external links pull from.

## Frontmatter key
A body-filled field still appears as a frontmatter key,
so the contract stays visible,
and tooling can attach at a fixed location.
- [[spec - diagnostic codes^body-fills-without-frontmatter-key]].

The null key is a promise, not a value.
A required field left as a null anchor with no body contribution is absent.
- it fires [[spec - diagnostic codes^required-field-absent]], like an omitted key.
- an optional null anchor is fine, nothing requires it.

## Accumulation
Contributions to one field accumulate,
across frontmatter and body.

Equal values collapse into one [[type value container]],
a value plus its contributions.

## Shape
A contribution whose value misses the slot shape is an error:
- [[spec - diagnostic codes^body-slot-shape-mismatch]].

An inline `` `[:field]` `` that breaks the `` `[:fieldName] value` `` form is a warning:
- [[spec - diagnostic codes^malformed-attribution-marker]].

A marked fence reading as a record and failing its claimed type's contract is an error:
- [[spec - diagnostic codes^embedded-record-validation-failure]].

A fence at a union slot that read as a record, and failed, when the union also carries a text branch:
- [[spec - diagnostic codes^body-fence-read-as-record]].
- it names the likely cause, prose whose first line reads as `type:`.
- it rides ALONGSIDE the failure above, it never replaces it.

## Extras
An inline `` `[:field]` `` to a field outside the [[type effective shape]] fills a [[type extras]], advisory:
- [[spec - diagnostic codes^unknown-field-in-prose-contribution]].

A wikilink `:field` to an unknown field is an error instead:
- [[spec - diagnostic codes^unbound-field-binding]].

## Documenting the marker
Prose that DOCUMENTS the marker must not trip it.
A single-tick marker is the real syntax, so it contributes or warns.

To show one as an example, wrap it in double backticks.
- the inline-code content then starts with a backtick, so the parser reads it as literal text, not a marker.
- the backticks stay visible when rendered, which is the point, it shows the literal token you would type.

Illustrated:
```markdown
`[:field] value`         real marker, contributes or warns
`` `[:field] value` ``   an example, inert
```

No opt-out syntax exists, and none is needed.
The convention rides on standard markdown, the scanner matches backtick runs by length.
The same double-tick trick shows any reserved token as an example, not a use.

# Structure
````markdown
---
type: myType        # declares myRef, myNote, myRecord, myProse
myRef:              # filled by body
myNote:
myRecord:
myProse:
---

# My Section

A reference to [[myTarget:myRef]].

`[:myNote] a primitive value`

```[:myRecord]
type: myRecordType
myInner: <value>
```

```[:myProse]
A multi-line value, because the slot is a String.

Blank lines and every other character survive verbatim.
```
````

Both fences carry the same marker and no tag.
The slot alone decides that one reads as a record and the other as text.
