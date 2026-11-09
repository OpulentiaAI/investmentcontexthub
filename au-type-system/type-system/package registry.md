

The hosted catalog that maps a package name to its git remote and audited ref.
It is a repo, not a service.

# Properties

## A repo, not a service
- one registry repo, one `registry.yaml` at its root, version-controlled.
- the engine reads a default registry repo, fetched into the [[package cache]] like any package, at its default branch.
- no service to run, GitHub is the backend, listing a package is a pull request against the file.

## What it maps
- `packages:`, a list of `name` to `{ remote, ref, path?, description? }`.
- a by-name dependency, `- name: library`, is looked up here and resolved to its remote and audited ref, see [[package cache]].
- an explicit-remote dependency needs no registry, it carries its own `remote` and `ref`.
- the content always lives in the dependency's OWN repo, the registry only points and vouches.

## Curation is the trust layer
- a registry entry's audited pinned ref is the install-time trust artifact, curators vouch for repo X at ref Y.
- curation plus the content-hash, the fetched repo must match the resolved sha, is integrity plus provenance without signing.
- it does NOT sandbox executed dependency code, that is a separate concern.
- a name the registry does not list is [[spec - diagnostic codes^dependency-resolution-failed]].

## Distinct from the repo registry
- the [[repo yaml]] is per-repo, a repo's own `name` and `deps`.
- the package registry is the shared hosted catalog, `name` to remote.
- a by-name dependency declared in a [[repo yaml]] is resolved through this catalog.

# Structure
```yaml
# registry.yaml at the registry repo root
packages:
  - name: library
    remote: git@github.com:org/library.git
    ref: v1
    description: the shared book catalog
  - name: ontology
    remote: git@github.com:org/ontology.git
    ref: v2
    path: vocab                    # a monorepo subpath
```
