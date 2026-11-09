How a [[type reference]]'s `[[target]]` name resolves to a file.

# Properties

## Path versus basename
- target containing `/`
  - repo-relative path, exact match first.
  - otherwise the target matches a file in that directory whose stem equals the final segment, any extension.
- otherwise
  - basename match, case-insensitive.
  - otherwise the target matches any file whose stem equals it, whatever the extension.
    - `[[s-001]]` reaches `s-001.yaml`, `[[photo]]` reaches `photo.png`.

## Stem matching
The stem strips one extension: `x.session.yaml` has stem `x.session`.
Interior dots in the target are not an extension boundary.
- `[[my.file.name]]` reaches `my.file.name.md`, whose stem is the whole dotted name.
- the target matches a file whose stem equals the WHOLE target, so a wrong-extension link like `[[note.pdf]]` still misses when nothing stems to `note.pdf`.

An extension is only required to disambiguate a shared stem.
The exact basename is tried first, so `[[note.yaml]]` picks the yaml over a same-stem `note.md`.

## Type-name reachability
A [[type-def]] is also reachable by its type-name.
- a `*.type.yaml` file's stem keeps the `.type` tail, so the type-name alone would miss the stem rule.
- `[[mcp.tool]]` resolves to `mcp.tool.type.yaml`, the same as the def's identity.
- this serves [[type-def shape def-ref]] `type<T>*`, but applies to every reference, the def becomes a navigational target by name.
- a same-named non-type file wins the stem rule first, so a single-segment name colliding with a note resolves to the note, disambiguate by the explicit `type/<name>.type.yaml` path.

## Outcomes
- no match
  - a validated slot errors, [[spec - diagnostic codes^reference-target-missing]].
  - a navigational link warns, [[spec - diagnostic codes^navigational-target-not-found]].
- several matches
  - a validated slot errors, [[spec - diagnostic codes^reference-target-ambiguous]].
  - a navigational link warns, [[spec - diagnostic codes^navigational-target-ambiguous]].
  - resolve by explicit extension, explicit path, or rename.

The outcome is one per surface, see [[type reference#Navigational versus validated]].

## File name case collision
Two basenames differing only in case collide under the case-insensitive rule.
Legal on Linux, illegal on macOS-default APFS.

Surfaced at knowledge base load, before any reference is evaluated:
- [[spec - diagnostic codes^case-collision-basename]].
