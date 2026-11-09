The per-user `~/.arsumbris/au-engine/config/workspaces.yaml` file,
a user-authored index pointing at workspace-repo folders by name.

See [[cross-repo file set]] for the whole file set.
See [[workspace manifest]] for the workspace composition each folder carries.

# Properties

## Per-user, user-authored
One file per user, `~/.arsumbris/au-engine/config/workspaces.yaml`.
- a human or a consumer writes it, the engine only reads it.
- device-scoped, this machine's named selections, never committed as identity.

## A typed node
A typed instance of the hardwired `au.engine.workspaces` def.
- device-global, so validated on the `device_config` read.
- not a knowledge base node, it sits outside every knowledge base.
- see [[engine schema files]].

## Points at folders, never inlines a selection
Each entry points at a workspace-repo FOLDER, a directory carrying `.arsumbris/repo.yaml`, see [[workspace manifest]].
- `path`, the folder's path.
- `name`, optional, the lookup name, defaults to the folder basename.
- the composition itself lives in the committed `.arsumbris/workspace.yaml`, this only names the folder.
- so a workspace folder is addressed by path, a named workspace by lookup here, no unified name-space and no collision.

## Named opening
`au open <name>` resolves a name here to its workspace-repo folder, then enters on it.
- one entry per name, first wins on a clash.
- an entry with no `path`, or an unnameable one, is skipped.
- an unknown name is a loud error naming the known workspaces, never a silent empty open.

## Split from the registry
Distinct from the engine-written [[repos yaml]], the split is deliberate.
- `repos.yaml` is engine-maintained location, written by `register` and `resolve`.
- `workspaces.yaml` is user preference, so a `resolve` never rewrites a working set.

## Read-injected
The read path is the injected config port, the same as [[repos yaml]].
- default, the device root `$HOME/.arsumbris`, then `au-engine/config/workspaces.yaml`.
- a parse error degrades to an empty index.

# Structure
```yaml
# ~/.arsumbris/au-engine/config/workspaces.yaml
workspaces:
  - path: /Users/username/kb/my-workspace          # name defaults to the folder basename
  - name: scratch
    path: /Users/username/experiments/scratch
```
