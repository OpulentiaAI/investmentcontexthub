The per-user `~/.arsumbris/au-engine/config/repos.yaml` file,
the device-global registry mapping every known repo name to its remote and local path.

See [[cross-repo file set]] for the whole file set.
See [[cross repo typed graph]] for the workspace of repos it serves.

# Properties

## Per-user, device-global
One file per user, `~/.arsumbris/au-engine/config/repos.yaml`.
- shared across every workspace on the machine.
- never committed as identity, this machine's view of where repos sit.

## A typed node
A typed instance of the hardwired `au.engine.repos` def.
- device-global, so validated on the `device_config` read.
- not a knowledge base node, it sits outside every knowledge base.
- see [[engine schema files]].

## Location, not identity
It maps a `name` to `{ remote, path }`.
- identity, WHO a repo is, lives in each repo's [[repo yaml]].
- this file answers only WHERE a repo's bytes sit on this machine.
- a name resolves by identity, this registry is one tier of that resolution, see [[#Resolution tier]].

## The entries
A `repos:` block, one entry per repo.
- `name`, the repo's declared name, the resolution key.
- `path`, the absolute local path to its checkout.
- `remote`, optional, its git remote, the cross-machine anchor.
- one entry per name, per-user unique, a `BTreeMap` on load.

## Resolution tier
Tier 2 of the order, after the co-present sibling, before the cache.
- sibling first, then this registry `path:`, then the cache, else unmounted.
- a registry `path:` never shadows a co-present sibling of the same name.
- resolving a `path:` verifies the target [[repo yaml]]'s declared `name` equals the key.
  - a mismatch is [[spec - diagnostic codes^dependency-identity-conflict]], never silently resolved.
- a local `path:` over a cached sha fires [[spec - diagnostic codes^dependency-path-overridden]].

## Engine-written
The engine owns the write, the consumer drives it.
- `register`, a config mutation, writes or updates one `{ name, remote, path }` entry.
  - the bootstrap path, a consumer surfaces the [[spec - diagnostic codes^peer-unmounted]] fix as a folder picker, then calls `register`.
  - it refuses to overwrite a name whose remote or declared identity disagrees, [[spec - diagnostic codes^dependency-identity-conflict]].
- `resolve`, the package-manager verb, writes the dependency entries it fetches.
- the sibling scan never writes, a discovered sibling resolves directly.
- device-scoped, so a write commits no git, unlike a per-repo `.auignore`.

## Read-injected
The read path is an injected port, like the `FileSystem` port.
- default, the device root `$HOME/.arsumbris`, then `au-engine/config/repos.yaml`.
- `$HOME` is required, an unset `$HOME` refuses rather than falling back.
- a test injects a tempdir standing in for the device root, so no test reads the developer's real registry.
- the injected path is the build's determinism seam.
- an explicit empty source, a headless run, resolves siblings and cache only.

## Degrades to empty
A parse error degrades to an empty registry.
- advisory, resolution falls back to siblings and cache.

## Distinct from the package registry
Two different registries, do not conflate.
- this is the per-user LOCATION registry, where names sit locally on this machine.
- [[package registry]] is the hosted name-to-remote catalog, a repo, not a per-user file.
- a by-name dependency's remote comes from the package registry, its local path from here.

# Structure
```yaml
# ~/.arsumbris/au-engine/config/repos.yaml
repos:
  - name: library
    remote: git@github.com:org/library.git
    path: /Users/username/kb/library
```
