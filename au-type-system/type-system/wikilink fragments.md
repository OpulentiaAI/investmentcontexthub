The optional fragments a [[type reference]] `[[target]]` carries, in strict order.

# Properties

## Fragment order
A wikilink carries optional fragments, in strict order:
- `name`
- `::repo`
  - the repo scope, which store to resolve in.
- `@commit`
  - the commit scope, which tree to resolve against, see [[#Commit-pinned references]].
  - a resolution-scope qualifier like `::repo`, both select where, applied before the in-file locators.
  - binds to `::repo`, written `::repo@commit`, never bare, see [[#Commit-pinned references]].
- `#head`
  - heading anchor, navigational only.
- `^block-id`
  - navigational, a jump anchor, the file is the referent, see [[type block-id]].
- `^^block-id`
  - a block-referent value, the block or inline record is the referent, see [[type block-id]].
- `:field`
  - body-contribution attribution, only meaningful in the body.
  - names the host field the link contributes to, see [[type-instance body contribution]].
  - the field name may carry a collision qualifier, `field{type}` / `field{type::repo}`, see [[#Qualified field attribution]].
  - the contribution value is the target, optionally narrowed to a `^^block-id`.

A `:field` never follows a `#head`.
- a `#head` is navigational, a heading is not an addressable value, see [[type reference#Target is a file or block, never a primitive]].
- so a heading can not be a contribution source.
- a `:` after a `#head`, with no `^block-id` between, is literal heading text, part of the anchor.
  - `[[note#My: Heading]]` anchors the heading "My: Heading", it carries no field.
- a `:field` follows a `^^block-id`, the block is the contributed value.
  - `[[otherFile^^block-id:localField]]` contributes the block to the host's `localField`.
  - a bare `[[otherFile^block-id:localField]]` contributes the FILE, `^block-id` a navigational anchor into it.

## Errors
Out-of-order fragments are an error:
- [[spec - diagnostic codes^wikilink-fragment-order]].
- [[spec - diagnostic codes^wikilink-reversed-delimiters]] for `^` before `#`.

At most one fragment of each kind per link.

An empty fragment value is an error:
- [[spec - diagnostic codes^wikilink-empty-target]].
  - except an empty name with a locating fragment (`#head`, `^block-id`), the local form below.
- [[spec - diagnostic codes^wikilink-empty-anchor]].
- [[spec - diagnostic codes^wikilink-empty-block-id]].
- [[spec - diagnostic codes^wikilink-empty-field]].
- [[spec - diagnostic codes^wikilink-empty-commit]], an `@` with no commit, `[[file::@]]`.

A `:field` name breaking [[type-def legal names]], or its `{type}` qualifier breaking the type-name rules, is an error:
- [[spec - diagnostic codes^wikilink-invalid-field-name]].

## Qualified field attribution
The `:field` name may carry a collision qualifier,
the same `field{type}` form a frontmatter key uses.
- `[[target:field{type}]]`, an own-type qualifier.
- `[[target:field{type::repo}]]`, a peer-type qualifier.
- it resolves a divergent same-named field, exactly as the frontmatter key does, see [[type-def fields collision - auto-unify and qualified field]].

The qualifier's `}` collides with no wikilink close.
- `}` is not `]` or `]]`, so the enclosing `[[...]]` closes cleanly after it, `[[target:field{type}]]`.
- the inline-marker carrier is the same, see [[type-instance body contribution]].

The `::` in a `{type::repo}` qualifier IS the same token as the `::repo` scope.
- so the `::repo` scan must skip a `::` inside the braces, reading only a brace-depth-zero `::` as the repo scope.
- the qualifier sits in the `:field` value, the last fragment, so a `{type::repo}` `::` is always inside braces and after the `:field` delimiter, never the repo scope.
- `:field` is the last fragment, so nothing follows the qualifier but the wikilink close.

## Local form
An empty name with a locating fragment means the current file.
- `[[^myId]]` resolves like `[[thisFile^myId]]`, navigational.
- `[[^^myId]]` resolves like `[[thisFile^^myId]]`, a block-referent value.
- `[[#head]]` resolves like `[[thisFile#head]]`, navigational.

In a typed slot the anchor stays navigational decoration.
`[[#head]]` there is a self-reference, the host file.

`[[:field]]` stays an error, a contribution needs a target:
- [[spec - diagnostic codes^wikilink-empty-target]].

An empty fragment value stays an error either way:
- `[[^]]` or `[[^^]]`, [[spec - diagnostic codes^wikilink-empty-block-id]].
- `[[#]]`, [[spec - diagnostic codes^wikilink-empty-anchor]].

Resolution skips name lookup, no missing or ambiguous outcome.
A dangling bare `^id` is [[spec - diagnostic codes^navigational-block-id-not-found]] (warning), the file being the referent, the same on both surfaces.
A dangling `^^id` is [[spec - diagnostic codes^block-id-not-found]], the block-referent demanded a value, the same on both surfaces.

## Anchor matching
A `#head` fragment resolves to a heading by text.
- case-insensitive, exact text match.
- a heading's text excludes its trailing `^id` marker, see [[type block-id]].
- several matches, the first in document order wins.

The engine owns this contract.
Consumers resolve through it, never by re-implementing the match.

Navigational only.
An anchor is never type-bearing, resolution still targets the file.

## Commit-pinned references
An `@commit` fragment pins the reference to a commit.
- `[[file::@commit]]` resolves against that commit's tree, not the working tree.
- the file still exists there, so the edge stays valid after the live file is deleted.
- deletion-stable and version-exact, anchored to history not to HEAD.

A pin value is legal only where the slot's shape admits one.
- a `*@` slot, or a `*@` branch of a union, admits a pin, see [[type-def shape suffixes]].
- a plain `T*` / `T&` slot forbids it, a pinned value there is [[spec - diagnostic codes^unexpected-commit-pin]].

The delimiter is `@`, not `##`.
- `##` would collide with a `#`-led heading anchor, a real ambiguity.
- `@` reads as "file at commit" and avoids it.

`@` binds to `::repo`, never bare.
- `@` is a legal filename character, so a bare `[[file@commit]]` is the literal filename `file@commit`.
- anchored after `::`, the position is unambiguous.
- `[[file::repo@commit]]`, that repo at that commit.
- `[[file::@commit]]`, this repo at that commit.

So `::` is conceptually always present.
- `[[file]]` equals `[[file::]]` equals `[[file::<this repo>]]`.
- requiring `::` even in the this-repo case keeps `@` a legal filename character.
- `[[my @ file::@commit]]` works, the name's `@` and the pin's `@` never collide.

The commit is an immutable oid, abbreviated or full, not a mutable rev.
- accepted, a hex string, a full oid or an abbreviated prefix of one.
- rejected, a branch, a tag, `HEAD`, or a relative rev like `HEAD~2`.
  - a branch or tag can be repointed, and a relative rev moves with HEAD.
  - both defeat the immutable past a pin records, an oid is the only form that never moves.
- the commit value runs to the first `#`, `^`, or `:`, so a `^` ends it.
  - `[[file::@HEAD^]]` reads `HEAD` as the commit and `^` as an empty block-id, an error.

The resolution semantics and the failure modes:
- a pin is an inert snapshot, its past immutable, forming no live edge.
- reconstructing where the recorded content went now is a consumer's tool, not the pin's, see the spec's build-state.
- a bare name resolves against the pinned commit's tree, the path is not required.
- a divergent live counterpart is not the pin's concern, a snapshot does not drift, so nothing fires.
- a target absent at the pinned commit errors, [[spec - diagnostic codes^pinned-path-absent]].
- a commit absent from the local store warns, [[spec - diagnostic codes^pinned-commit-unavailable]].

# Structure
The fragments a `[[target]]` may carry, each in its ordered position:

```markdown
[[note::repo]]                 # repo scope, resolve in a peer
[[note::@<commit>]]            # this repo, pinned to a commit
[[note::repo@<commit>]]        # peer repo, pinned
[[note#My Heading]]            # navigational heading anchor
[[note^para]]                  # navigational jump anchor, the file is the referent
[[note^^block]]                # block-referent value, the block is the referent
[[other^^block:localField]]    # body contribution, the block value into localField
[[^block]]                     # local form, the current file
```
