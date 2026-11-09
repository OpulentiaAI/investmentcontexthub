The device-global store of fetched dependency snapshots, keyed by commit sha.
It makes a declared dependency's types usable in place, pinned, never copied into your repo.

See [[cross repo typed graph]] for how a peer's types are then used.
See [[cross-repo file set]] for the whole file set.

# Properties

## What it holds
- device-global, `~/.arsumbris/au-engine/cache/packages/<sha>/`, one immutable snapshot per resolved commit.
- shared across every workspace on the machine, so one commit is fetched once and reused.
- a monorepo's subpackages share one snapshot, the subpath is applied at mount.

## From declaration to use
Four steps make a peer's types available.
- DECLARE, a dependency in a repo's [[repo yaml]] `deps`.
- RESOLVE, the `resolve` verb fetches the declared closure into the cache and writes the lock.
- MOUNT, each cached snapshot mounts read-only as a member, located by its sha.
- USE, the peer's types resolve via `::repo`, folded from the snapshot, no copy.

## Resolve is the fetch
`resolve` is a daemon verb over the whole workspace, not a per-package call.
- it fetches each declared dependency, and its transitive `deps`, cycle-safe by sha.
- it fetches a `(remote, ref)`, a by-name dependency's remote comes from the [[package registry]].
- the fetched commit's sha is the snapshot's identity, git's own integrity is the check.
- a dependency it cannot deliver is loud, [[spec - diagnostic codes^dependency-resolution-failed]], the rest still resolve.

## The lock pins the solve
`resolve` writes each editable repo's `.arsumbris/repo.lock`, and commits it, see [[cross-repo file set]].
- each repo's lock pins its OWN full transitive fetched closure, one sha per dependency.
- a re-open with the lock present and the cache populated is reproducible and offline.
- the lock is the engine's output, never hand-edited, like `package-lock.json`.

## No copy
The cache is why a peer's vocabulary needs no vendored copy.
- import folds a peer type from the cached snapshot at the locked sha, nothing lands in your tree.
- so a dependency's types are used in place, pinned, never duplicated into your repo.
- the version moves only when you bump the declared `ref:` and re-resolve.

## Read-only and overridable
- a snapshot is read-only and immutable, the sha names it, so it is never edited or watched.
- a co-present sibling or a [[repos yaml]] `path:` serves an editable local tree instead, [[spec - diagnostic codes^dependency-path-overridden]].

## Version conflicts
The engine never picks a winner.
- one package required at two shas, [[spec - diagnostic codes^dependency-version-conflict]], align the pins.
- one name resolving to two different packages, [[spec - diagnostic codes^dependency-identity-conflict]].

# Structure
`notes` declares two dependencies.

```yaml
# notes/.arsumbris/repo.yaml   —  you declare the dependencies
name: notes
deps:
  - name: library                          # by name, via the registry
  - name: ontology                         # by explicit remote
    remote: git@github.com:org/ontology.git
    ref: main
```

```yaml
# notes/.arsumbris/repo.lock   —  resolve writes and commits this
packages:
  - name: library
    remote: git@github.com:org/library.git
    sha: 9f3a1c2e7b4d...
  - name: ontology
    remote: git@github.com:org/ontology.git
    sha: 1a2b3c4d5e6f...
```

After resolve, `book::library` folds from the cached snapshot, usable as a type, no copy in `notes`.
