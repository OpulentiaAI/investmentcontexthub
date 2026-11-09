The per-repo `.arsumbris/repo.yaml` file,
a repo's committed identity and its declared deps.

See [[cross repo typed graph]] for the general idea of a workspace of repos.
The whole cross-repo file set is mapped in [[cross-repo file set]].

# Properties

## Committed and machine-independent
It carries no paths.
- identity and deps travel with the repo, the same on every clone.
- where a dep sits on THIS machine is resolved separately, see [[#Identity, not location]].

## A typed node
The file is a typed instance of the hardwired `au.engine.repo` def.
- it validates against that def like any instance, a malformed `deps` entry is diagnosed.
- see [[engine schema files]].

## The identity, at the root
The root keys name the repo.
- `name`
  - the durable identity.
  - what `::repo` addresses and how others reference it.
- `remote`
  - optional.
  - the git remote.
  - the cross-machine anchor that recovers an absent dep.
- `description`
  - optional.
  - free text.

### The name is the repo's to declare
The `name` is authoritative.
- others reference the repo by that name, there is no per-consumer alias.
- the on-disk folder is a soft convention, not the identity.
  - a folder disagreeing with the declared name is [[spec - diagnostic codes^repo-folder-name-mismatch]], `drift`, the declared name wins.

## Deps, the dependencies
The `deps` block lists every repo this one depends on.
- one entry per dep.
- a `name`, plus optional `remote` / `ref` / `description`.
- a repo's deps ARE its type-dependencies.
  - a clone with no deps present still knows what it depends on and where to fetch it.
- `deps` is TYPE-dependencies only, folded into the repo's closure-hash, drift-tracked.
  - the workspace's runtime composition, the `edit` and `discover` members, lives in a separate `.arsumbris/workspace.yaml`, never here, see [[workspace manifest]].
  - so a content repo's `deps` never names the host or harness framework it merely runs under.
- presence is declared here.
  - the vocabulary is discovered from `::repo` use.
  - there is no type import list.
- a dep declared by name only resolves via [[package registry]].
  - distinct from this per-repo file.

## The peer gate
A declared dep is a peer, crossable via `::repo` in a type position.
Only a declared peer may be crossed.
- a mounted member that is NOT a declared dep, a `discover` member, cannot be crossed, promote it to a dep first, see [[workspace manifest]].
Error cases:
- a `::repo` type name to an undeclared repo
  - [[spec - diagnostic codes^type-repo-unknown]].
- a `::repo` type name to a mounted-but-not-declared member
  - [[spec - diagnostic codes^type-repo-not-a-dependency]].
- a `[[x::repo]]` link to an undeclared repo
  - [[spec - diagnostic codes^reference-repo-unknown]].

## Identity, not location
The file carries identity, never a machine path.
- `name` and `remote` travel with the repo, the same on every machine.
- where each dep sits on THIS machine is resolved by an order.
  - a co-present sibling, a repo under the entry or a declared member, discovered by its `repo.yaml` marker and matched by its DECLARED name, so folder-name drift never hides it.
  - registry-located, the per-user `~/.arsumbris/au-engine/config/repos.yaml` gives it a local path.
  - cache-resolved, the package manager fetched it into the device cache, see [[package cache]].
- reachability is declaration-driven, a repo nested inside an UNDECLARED repo is unreachable, the enclosing walk stops there, declare it as a `dep` or register its path to reach it.
- present as none is unmounted.
  - [[spec - diagnostic codes^peer-unmounted]], a legitimate absent state.

Location is per-user, in the device-global [[repos yaml]].

## Every repo is explicit
A repo declares `.arsumbris/repo.yaml`, there is no implicit repo.
- the entry must be a folder-repo, a directory without `repo.yaml` is refused, see [[workspace manifest]].
- a member resolves by declared name, and resolution binds only against a target `repo.yaml` that declares it, so a member always has one.
- content without a `repo.yaml` is simply content inside some explicit repo, never its own repo.
- a name collision between two declared repos is [[spec - diagnostic codes^duplicate-repo-name]].

## Load errors
- an unparseable file
  - [[spec - diagnostic codes^repo-registry-parse-error]].
- no top-level `name`, or an invalid one
  - [[spec - diagnostic codes^repo-name-missing]].
- two repos claiming one name
  - [[spec - diagnostic codes^duplicate-repo-name]].

# Structure
```yaml
# notes/.arsumbris/repo.yaml
name: notes
remote: git@github.com:me/notes.git
deps:
  - name: library         # a dependency, by registry name
  - name: ontology        # a dependency, by explicit remote
    remote: git@github.com:org/ontology.git
    ref: main
```
