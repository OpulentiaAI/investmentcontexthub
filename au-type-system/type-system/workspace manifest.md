The `.arsumbris/workspace.yaml` file,
an optional composition beside a repo's `repo.yaml` that turns its folder into a workspace entry.

See [[cross repo typed graph]] for the general idea of a workspace of repos.
See [[cross-repo file set]] for the whole file set.

# Properties

## A typed node
A typed instance of the hardwired `au.engine.workspace` def.
- committed with the repo, so its composition travels.
- see [[engine schema files]].

## Optional, an entry concern
Sits beside `repo.yaml`, read only when its folder is the entry.
- ignored when the repo is mounted as a member of another workspace.
- with no `workspace.yaml`, the workspace is the entry repo plus its own `deps`.
- it composes members, it never edits a member's own `repo.yaml`, so every content repo stays framework-free.

## Two member lists
Both optional lists of repo names.
- `edit:`, editable members you author, resolved live at HEAD.
- `discover:`, pinned members mounted so type-discovery composes their parts, not type-dependencies.
  - crossing one via `::repo` in a type position needs a declared `dep`, see [[type repo qualifier]].
- a name in both is [[spec - diagnostic codes^workspace-member-role-conflict]], a member has one role per workspace.

## Self-complete
When present, it MUST list its own containing repo in `edit:`.
- an omission is [[spec - diagnostic codes^workspace-omits-containing-repo]], so the file reads as self-complete.
- the containing repo is a live working tree, so it belongs in `edit`, never `discover`.

## repo.yaml deps stay separate
`repo.yaml deps` is a repo's intrinsic type-dependencies, folded into its closure-hash.
- the runtime framework is a workspace composition concern, it lives in `discover`, never in `deps`.
- so a content repo's closure-hash is unaffected by the host or harness it runs under, see [[repo yaml]].

## The members
The entry repo plus its `deps`, plus the `edit` and `discover` members and their transitive `deps`.
- the editable flag is role-derived, `edit` and the entry are authoring surfaces, a `dep` or `discover` member is consumed.
- mount and watch follow the resolution, a live tree is watched, a cache snapshot is not, a consumed member served from a local tree carries the `dependency-path-overridden` hint.
- each is located by the resolution order, a co-present sibling, then registry, then cache, see [[repos yaml]].
- reachability is declaration-driven, the content walk is bounded at nested markers, a co-present member resolves by its declared name, a repo nested inside an UNDECLARED repo is unreachable.

## Member outcomes
- an `edit` member unmounted is [[spec - diagnostic codes^edit-member-unmounted]], the workspace opens degraded, the missing root surfaced.
- an `edit` member resolving only to the read-only cache is [[spec - diagnostic codes^edit-member-read-only]].
- a `discover` member unmounted is [[spec - diagnostic codes^discover-member-unmounted]].

## The lock
The `discover` closure is pinned in `.arsumbris/workspace.lock`, see [[cross-repo file set]].
- a hardwired `au.engine.workspace-lock`, parallel to `repo.lock`, engine-written by `resolve`.
- so discover members mount reproducibly and offline, an `edit` member is live and never locked here.

# Structure
```yaml
# <entry-repo>/.arsumbris/workspace.yaml
edit:                     # editable, live
  - my-content            # the containing repo, required
  - some-other-content
discover:                 # pinned, mounted for discovery
  - host-bundle
  - mcp-bundle
```
