The files a repo and a workspace use to compose across repos.
A map of what each holds, what is committed, and what is per-user.

See [[cross repo typed graph]] for the model these files serve.

# Two axes

Every file answers along two axes.
- COMMITTED versus PER-USER.
  - committed travels with the repo, machine-independent, the same on every clone.
  - per-user is this machine's view, never committed as identity.
- IDENTITY versus LOCATION versus SOLVE.
  - identity, who a repo is and what it depends on.
  - location, where a name's bytes sit on this machine.
  - solve, which commit each dependency resolved to.

# Committed, in-repo

Per repo, in its `.arsumbris/`, committed, so identity and solve travel with the repo.

**`repo.yaml`**, identity plus declared deps.
- `au.engine.repo`, see [[repo yaml]].
- `name`, the durable identity `::repo` addresses.
- optional `remote`, the cross-machine anchor.
- `deps:`, the repos this one depends on, each a name plus an optional `remote` / `ref` assertion.
```yaml
# notes/.arsumbris/repo.yaml
name: notes
remote: git@github.com:me/notes.git
deps:
  - name: library
  - name: ontology
    remote: git@github.com:org/ontology.git
    ref: main
```

**`repo.lock`**, the dependency solve.
- `au.engine.repo-lock`, see [[package cache]].
- pins this repo's OWN transitive closure, each dependency to a concrete sha.
- per-repo, because deps are declared per-repo, so the solve belongs to the repo.
- a standalone repo is reproducible from its own lock, the Cargo-per-crate model.
- `resolve` is entry-global, one solve across all repos' deps and the workspace's `discover` set, then it writes each repo's own lock and the `workspace.lock`.
- a dependency shared by two repos pins to one sha in every lock, a disagreement is `dependency-version-conflict`.
```yaml
# notes/.arsumbris/repo.lock            — engine-written
packages:
  - name: library
    remote: git@github.com:org/library.git
    sha: 9f3a1c2e7b4d…
  - name: ontology                      # transitive, via library
    remote: git@github.com:org/ontology.git
    sha: 1a2b3c4d5e6f…
```

# Committed, per entry repo

**`.arsumbris/workspace.yaml`**, the optional workspace composition.
- `au.engine.workspace`, see [[workspace manifest]].
- beside the entry repo's `repo.yaml`, read only when its folder is the entry.
- `edit: [names]`, editable members, and `discover: [names]`, pinned members mounted for discovery.
- the members are the entry repo plus its `deps` plus the `edit` and `discover` members and their transitive deps.
```yaml
# my-workspace/.arsumbris/workspace.yaml
edit:
  - my-workspace       # the containing repo, required
  - notes
discover:
  - host-bundle
```

**`.arsumbris/workspace.lock`**, the discover solve.
- `au.engine.workspace-lock`, engine-written by `resolve`, parallel to `repo.lock`.
- pins the `discover` closure, the discover members and their transitive deps, each to a concrete sha.
- so an `edit` member stays live, a `discover` member mounts reproducibly and offline.
```yaml
# my-workspace/.arsumbris/workspace.lock   — engine-written
packages:
  - name: host-bundle
    remote: git@github.com:org/host-bundle.git
    sha: 7c1d…
```

# Per-user, device-global

This machine only, never committed as identity.

**`~/.arsumbris/au-engine/config/repos.yaml`**, the location registry.
- `au.engine.repos`, engine-written, name to `{ remote, path }`, where each repo sits here.
```yaml
repos:
  - name: library
    remote: git@github.com:org/library.git
    path: /Users/username/kb/library
```

**`~/.arsumbris/au-engine/config/workspaces.yaml`**, the workspace index.
- `au.engine.workspaces`, user-authored, pointers to workspace-repo FOLDERS by name, never inline selections.
```yaml
workspaces:
  - path: /Users/username/kb/my-workspace          # name defaults to the folder basename
  - name: scratch
    path: /Users/username/experiments/scratch
```

**`~/.arsumbris/au-engine/cache/packages/<sha>/`**, the device cache.
- immutable dependency snapshots, one per resolved commit, what the `repo.lock` and `workspace.lock` shas point into, see [[package cache]].

**`~/.arsumbris/au-engine/run/<hash>.sock`**, the daemon socket.
- runtime, ephemeral, `<hash>` is the FNV-1a of the absolute entry-FOLDER path, injective by folder, outside the knowledge base so a deep path never overruns the socket-path limit.

# The split

Identity and solve travel with the repo.
- `repo.yaml`, `repo.lock`, committed, the same on every clone.

Location and preference are per-user.
- `repos.yaml`, `workspaces.yaml`, the cache, never committed as identity.

A name resolves by identity, the per-user files only answer where the bytes sit here.

# The lock

Two lock kinds, both engine-written by `resolve`.
- `repo.lock`, per-repo, the repo's own dependency solve.
- `workspace.lock`, per entry repo, the workspace's `discover` solve.
- which VERSION of each, advanced by `resolve`, a version pin merges by text.
