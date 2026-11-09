---
tldr: "Canonical enumeration of every diagnostic code the engine emits. Code name, severity, message shape, trigger, spec cross-reference. Lives outside the main type-system spec so the catalogue can grow without polluting it."
---

# Diagnostic codes

Stable kebab-case identifiers.
Downstream consumers
- UI
- future LSP
- agents
- ...
match on the code, not the message, over the daemon wire.

Messages are user-facing prose that may evolve.
Codes are the contract.

Severity
- `error`
- `drift`
- `warning`
- `hint`
is part of the contract too.

An `error` prevents some downstream stage from running
- graph load errors block per-file validation
- per-file errors stay per-file.

A `drift` is advisory, high attention.
A same-named type across repos has diverged from the identity this repo resolves against.
It never blocks, resolution still succeeds and the local definition validates standalone.
Its own tier so consumers can rank it above ordinary warnings.

A `warning` is advisory.
The engine completes the stage and surfaces the issue.

A `hint` is advisory, a suggestion.

Codes are grouped by emission **stage**,
so the catalogue mirrors the pass order in [[type validation]].

Within a stage, codes are listed by topic.

Each entry is an H3 sub-section:
- with stable block-id for referencing, identical to the code
- user facing message
- triggers
- abstract example

```
### `code-name` - severity
^code-name

**Message:**
template with `{placeholders}` for dynamic values.

**Triggers:**
short trigger sentence.
Optional bulleted cases.
Optional trailing prose for rationale or consequences.

**Example:**
abstract placeholder shape (optional; only when clearer shown than described).

**Spec:** [[atom]] wikilinks (when relevant).
```

The `^code-name` block-id makes each entry addressable.
Reference an entry as `[[spec - diagnostic codes^code-name]]`.

Quoted message templates preserve the engine's literal text.
That includes any em-dashes inside backticks.
Surrounding prose follows the house writing style.

## Span encoding

Every byte offset the engine emits is a **UTF-8 byte offset** into the source file.
That covers:
- `span.range.{start, end}` on every Diagnostic.
- Every Span inside `related[]`.
- `location.byte_range` on `Contribution` (introspect `effective_values`).
- All `span` fields on `body_events` introspect entries.
- `section_presence[*].span`, `meta_blocks[*].source.span`, `graph.types[*].source.span`, etc.

Ranges are half-open: `start` is inclusive, `end` is exclusive.

UTF-8 is Rust's native string indexing.
The wire stays encoding-stable across consumers.

Byte offsets are canonical.
Every span additionally carries `line_col`, the derived rendering:
- `{ start { line, col }, end { line, col } }`, 1-based.
- `col` counts UTF-8 bytes from the line start, plus one.
- omitted only for spans into files the build never read (assets).

Consumers targeting UTF-16 surfaces (VSCode `Range`, browser `String.length`) convert within the one line:
take `line_col.line`, then count UTF-16 code units from the line start to the byte offset.
No whole-file newline scan is needed.

Non-ASCII content (em-dashes, accented characters, emoji) is where UTF-8 ≠ UTF-16; ASCII-only content happens to be 1:1 between the two.

---

## 0. Workspace and repo discovery (au-core, au-engine::repo)

Discovers the repos in a workspace from their `.arsumbris/repo.yaml` markers, before any knowledge base load.
Membership is load-bearing: every file resolves type claims against its repo's graph.
These discovery diagnostics stay advisory: a malformed registry degrades to an implicit repo, it never blocks the load.

### `repo-registry-parse-error` - error
^repo-registry-parse-error

**Message:**
`repo registry is not valid YAML: {detail}`.

**Triggers:**
a `.arsumbris/repo.yaml` is not valid UTF-8 or YAML. The directory is not treated as a repo root.

`error`, not advisory.
- the repo produces no type graph, and every `::repo` fold into it is blocked, a downstream stage.
- the build never aborts, `error` is a severity tier, not a fatal exit.

Carries a `fix` for the recurring case, an unquoted `:` inside a scalar value.
- e.g. `description: text: colon`, the embedded colon-space reads as a nested mapping and breaks the parse.
- the hint suggests quoting the value, `key: "value"`.

### `repo-name-missing` - error
^repo-name-missing

**Message:**
`repo.yaml must declare a valid top-level 'name'`.

**Triggers:**
a `repo.yaml` parses but has no non-empty top-level `name`, or its `name` is not a valid repo name (the type/field-name grammar: a leading letter, then letters / digits / `_` / `-`, dot-separated). The directory is not treated as a repo root. Rejecting an invalid name is also a security gate: a valid name has no `/`, `..`, whitespace, or newline, so a resolved name is always one benign path component (the `sibling_scan` probe joins it onto a parent directory).

`error`, the same vanish-the-repo cascade as `repo-registry-parse-error`.

### `duplicate-repo-name` - warning
^duplicate-repo-name

**Message:**
- `repo name '{name}' is declared by more than one repo; this registry is ignored and its directory is mounted as an implicit repo so it stays isolated`, for two declared registries.
- `repo name '{name}' is already used by another repo; this member is mounted as '{disambiguated}' so the two stay isolated`, for an implicit member whose name collides.
- `dep '{name}' matches more than one co-present sibling ({roots}); resolution refuses to pick, it stays unmounted`, for a dep resolving to two co-present siblings.

**Triggers:**
two repos in the workspace claim the same name, or a dep resolves to two co-present siblings of one name.
- two declared repos with the same `name`: the first wins, the later `repo.yaml` is ignored and its directory degrades to an implicit repo, isolated, never merged into its parent.
- an undeclared member whose name collides with an already-claimed name.
  - the name is its manifest member name, else its path basename.
  - it is disambiguated so the per-repo graphs stay isolated, never silently merged.
- a dep resolves to two or more co-present siblings declaring one name: resolution REFUSES to pick, the dep stays unmounted, never a nondeterministic tiebreak..

### `repo-folder-name-mismatch` - drift
^repo-folder-name-mismatch

**Message:**
`repo '{name}' lives in a folder named '{folder}'; the declared name wins`.

**Triggers:**
a declared repo's on-disk folder basename differs from its declared `name`, compared CASE-INSENSITIVELY (repo names are ASCII, so a case-only difference on a case-insensitive filesystem like macOS APFS or Windows is not a mismatch, and does not drift). A soft convention, not an error: identity is declared, never positional, so resolution still succeeds by the declared name. `drift` severity, a high-attention advisory. Exempt: a cache-mounted dependency (its folder is a commit sha, a managed dep the package manager places, not the user), and an implicit repo (no `repo.yaml`, its name IS its folder). The cache-root exemption is a first cut, to be refined against an editable / provenance signal.

### `peer-unmounted` - warning
^peer-unmounted

**Message:**
`peer '{name}' is declared but not mounted on this machine`.

**Triggers:**
a declared dep (a plain `dep`) resolves via none of the tiers (no co-present sibling, no registry `path:`, no cache snapshot, and it is not a discovered repo). A legitimate state, not an error. The role-keyed unmounted code for a `dep`: an `edit` member (or the entry) escalates to `edit-member-unmounted`, a `discover` member to `discover-member-unmounted`. Carries a fix: register a path, or place it as a co-present sibling. The `register` config mutation is the typical bootstrap, via a consumer's folder picker.

### `workspace-member-unwalkable` - warning
^workspace-member-unwalkable

**Message:**
`workspace member '{name}' has a path that cannot be walked: {cause}`.

**Triggers:**
a workspace member resolves to a local root that exists, but its root cannot be walked: it is a file not a directory, or it is unreadable. Distinct from the role-keyed unmounted codes (`edit-member-unmounted` / `discover-member-unmounted` / `peer-unmounted`), where the member resolves to nothing. A path resolved, so the fix is to correct it, not add one. Carries the OS-level cause and a fix: point it at a readable directory, or place it as a co-present sibling.

### `edit-member-unmounted` - warning
^edit-member-unmounted

**Message:**
`workspace edit member '{name}' resolves to nothing; the workspace opens degraded over its present members`.

**Triggers:**
an `edit` member (or the entry), an editable authoring ROOT, resolves via none of the tiers: no co-present sibling, no per-user registry path, no cache snapshot. The role-keyed unmounted code for an editable member. The workspace opens DEGRADED over its present members, the missing root surfaced, never silently dropped, since a typo in an `edit` member silently omitting a root is the silent-drop the engine forbids. A legitimate absent state, so a `warning`, never blocking: the fix is environmental, register a local path or place it as a co-present sibling, not a source edit. An edit member that resolves only to the read-only cache is `edit-member-read-only` instead. A consumed member is `discover-member-unmounted` (a `discover`) or `peer-unmounted` (a `dep`). Renamed from the retired `primary-unmounted`.

### `edit-member-read-only` - warning
^edit-member-read-only

**Message:**
`workspace edit member '{name}' resolves only to the read-only cache; an edit member is meant to be editable`.

**Triggers:**
an `edit` member (or the entry) resolves ONLY to the read-only cache snapshot, its root sitting under the device package cache, present but not a live working tree. An edit member is meant to be editable, so this is surfaced, a `warning`, and the workspace still opens. The fix is to register a local path for it or place it as a co-present sibling. Distinct from `edit-member-unmounted`, where the member resolves to nothing, and from a cache-mounted consumed member (a `dep` / `discover`), where read-only is the expected state and no diagnostic fires. Derived from the member's resolved location, `root.starts_with(cache_root)`, the same path-under-cache signal the members read serves as `local: false`. Renamed from the retired `primary-read-only`.

### `discover-member-unmounted` - warning
^discover-member-unmounted

**Message:**
`workspace discover member '{name}' is declared but not mounted on this machine`.

**Triggers:**
a `discover` member resolves via none of the tiers: no co-present sibling, no per-user registry path, no cache snapshot. A `discover` member is a pinned discovery mount, so unmounted it contributes no vocabulary; a `warning`, never blocking, the workspace still assembles from the rest. The role-keyed unmounted code for a `discover` member, distinct from `edit-member-unmounted` (an editable authoring root) and `peer-unmounted` (a plain `dep`). A cache-mounted `discover` is the expected pinned state and fires nothing. Carries a fix: register a path, place it as a co-present sibling, or run `resolve` to fetch it.

### `disabled-member-not-declared` - warning
^disabled-member-not-declared

**Message:**
`workspace 'disabled' names '{name}', which is not a declared member; a disabled name must appear in 'edit' or 'discover'`.

**Triggers:**
a `workspace.yaml`'s `disabled:` overlay names a repo absent from both `edit:` and `discover:`. The `disabled:` overlay silences a DECLARED member (excluding it from the mount set with no diagnostic), so a name it lists must itself be declared. An undeclared name is inert and does nothing, the silent-drop the engine surfaces instead of dropping. A `warning`, never blocking. A `disabled:` entry that DOES match a declared member is intentional and fires nothing (no unmounted code, no hint). Fix: add the name to `edit` or `discover`, or remove it from `disabled`. Emitted at the workspace file.

### `member-at-reserved-root` - warning
^member-at-reserved-root

**Message:**
`workspace member '{name}' resolves to the reserved device root ~/.arsumbris; it is excluded, the workspace opens over the rest`.

**Triggers:**
a declared workspace member resolves to the reserved device root `~/.arsumbris`, whose `.arsumbris/` IS the device config/data area. The member is EXCLUDED from the mount set, never walked (walking a home directory as content would be catastrophic), and the workspace opens over the rest. A `warning`, never blocking, the parity of the unmounted member-outcome family. The check is EQUALITY (the member's canonical root equals the canonical `$HOME`), not a subtree test, so a cache-mounted member under `~/.arsumbris` is unaffected. It is specific and takes precedence over the generic unmounted signal, so a reserved member fires this rather than `edit-member-unmounted` / `discover-member-unmounted` / `peer-unmounted`. The entry sibling of this outcome is `EntryReserved` (a hard refusal, the daemon does not serve). Fix: point the member at a directory other than the home directory. Emitted at the workspace file.

### `workspace-member-role-conflict` - error
^workspace-member-role-conflict

**Message:**
`workspace member '{name}' appears in both 'edit' and 'discover'; a member has one role per workspace`.

**Triggers:**
a name listed in both a `.arsumbris/workspace.yaml`'s `edit:` and its `discover:` list. A member has ONE role per workspace: `edit` is an editable authoring surface, `discover` is a consumed discovery mount, so the two are contradictory. An `error`, but the editable role (`edit`) wins meanwhile so assembly stays deterministic and the workspace still opens. Carries a fix: keep the name in `edit` or `discover`, not both. Emitted at the workspace file. Distinct from `discover-member-is-a-dependency` (a redundant, not contradictory, listing).

**Example:**
```yaml
# .arsumbris/workspace.yaml
edit:
  - my-content        # also in discover: a role conflict
discover:
  - my-content
```

### `discover-member-is-a-dependency` - hint
^discover-member-is-a-dependency

**Message:**
`workspace member '{name}' is listed in 'discover' but is also a declared dependency; the 'discover' listing is redundant`.

**Triggers:**
a name in a `.arsumbris/workspace.yaml`'s `discover:` list that is ALSO a declared `dep` (reached through some member's `deps`). During assembly the member resolves to the higher role (`dep` subsumes `discover`), so the `discover` listing adds nothing: the dep already mounts and pins it, and — unlike a bare `discover` — lets its types be crossed via `::repo`. A `hint`, never blocking. Distinct from `workspace-member-role-conflict` (a contradictory `edit` + `discover`); this is a redundant, compatible listing. Emitted at the workspace file. Fix: drop the name from `discover`.

**Example:**
```yaml
# my-content/.arsumbris/repo.yaml declares dep 'shared'
# my-content/.arsumbris/workspace.yaml
edit:
  - my-content
discover:
  - shared            # already a dep: the discover listing is redundant
```

### `workspace-omits-containing-repo` - error
^workspace-omits-containing-repo

**Message:**
`workspace.yaml does not list its containing repo '{name}' in 'edit'; the entry repo is a live working tree and belongs in 'edit'`.

**Triggers:**
a folder-repo `.arsumbris/workspace.yaml` does not list its own containing repo in `edit:`. The containing repo is the entry, a live working tree at HEAD, so it belongs in `edit`; an omission would read as if the file excludes its own repo. An `error`, so the file reads as self-complete. The engine still mounts the containing repo regardless (it is always a member with role `entry`), so the omission never drops the home; the error just requires the listing. Fires only for a folder-repo entry (`<repo>/.arsumbris/workspace.yaml`), where the containing repo's identity is known from the sibling `repo.yaml`. Carries a fix: add the containing repo to `edit`.

**Example:**
```yaml
# my-content/.arsumbris/workspace.yaml   (containing repo is 'my-content')
edit:
  - some-other-content       # omits 'my-content'
discover:
  - host-bundle
```

### `undeclared-nested-repo` - warning
^undeclared-nested-repo

**Message:**
`nested repo '{name}' is not a declared member; its subtree is skipped and contributes nothing`.

**Triggers:**
a nested `.arsumbris/repo.yaml` under a walked repo (the entry or a declared member) that is not itself a declared member. The content walk is BOUNDED at the nested marker, so it records the marker and never descends the subtree, the nested repo contributes NOTHING, never silently absorbed into its parent and never a `duplicate-repo-name` fight. A `warning`; the fix names how to include it: declare it as an `edit` / `discover` member in `workspace.yaml`, or as a `dep` in `repo.yaml`. A DECLARED nested repo is a member root walked by its own bounded walk, so it mounts as its own member and never fires this. Only the OUTERMOST undeclared nested repo warns: the enclosing walk stops at it, so a repo buried inside another undeclared repo is never walked, never surfaces, and its inclusion is the outer repo's concern. Emitted at the nested repo's `.arsumbris/repo.yaml`.

**Example:**
```yaml
# my-content/.arsumbris/workspace.yaml   (declares only 'my-content')
edit:
  - my-content
# my-content/vendored/.arsumbris/repo.yaml   (a nested repo, undeclared → skipped)
```

### `dependency-version-conflict` - error
^dependency-version-conflict

**Message:**
`package '{package}' is required at {n} conflicting versions ({shas}); align the members [{names}] to one version`.

`{package}` is the source `{remote}` plus the subpath for a monorepo package.

**Triggers:**
two or more dependency edges across the resolved closure require the same package, the same `(remote, path)`, at different commit shas. The package-manager-aware companion to `duplicate-repo-name`. The engine never picks a winner, so the conflicted package is left unresolved, excluded from the mounts and the lock, never a degenerate half-mounted state. The human or agent aligns the edges to one version, or applies a workspace-level override. Carries a fix: align the conflicting members to one version. Supersedes the former `version-skew` advisory, which only warned.

### `dependency-identity-conflict` - error
^dependency-identity-conflict

**Message:**
- `dependency name '{name}' resolves to {n} different packages ({packages}); a name must identify one repo, rename or align the sources`, for the transitive-closure case.
- `dep '{name}' resolves via the registry to a repo that declares '{declared}'; a registry path must match its key`, for a registry `path:` whose target declares a different name.
- `dep '{name}' asserts remote '{asserted}', but '{name}' declares '{owner}'` and `registry remote for '{name}' is '{reg}', but the repo declares '{owner}'`, for a remote disagreeing with the owner.

`{packages}` lists each distinct `{remote}` (plus subpath for a monorepo package).

**Triggers:**
a dependency name resolves ambiguously to two identities, or its remote disagrees with the owner.
- one name resolves to two or more DIFFERENT packages across the closure, distinct `(remote, path)`, two unrelated repos wearing one name. The identity sibling of `dependency-version-conflict` (which is one package at two shas); a name at two remotes is an orthogonal collision the version grouping misses. Without this the last-walked edge would silently overwrite the earlier one in the mounts map. The engine never picks a winner, so the name is left unresolved, excluded from the mounts and lock.
- a registry `path:` whose target `repo.yaml` declares a name different from the registry key: the entry is mis-registered, so the dep stays unmounted, never silently resolved past. The `register` config mutation runs the same check before writing.
- a REMOTE disagreeing with the owner: the canonical remote is the depended repo's own `repo.yaml remote`. A depender's `deps[].remote` assertion, or a per-user registry entry's remote, that differs from it is a conflict, a real disagreement about the owner rather than an artifact of which depender resolved first. Advisory..

Carries a fix: give the name one source, rename a colliding repo, fix the registry path, or align the remote with the owner.

This is a SAFETY FLOOR, not the ergonomic end-state: it rejects rather than resolving, over-rejecting the legitimate transitive case where two independent deps happen to share a name and should coexist. The end-state is `(name, source)` member identity (Cargo's model), so same-name-different-source coexist and only a genuine direct ambiguity rejects. Matches Cargo's "error until disambiguated" default meanwhile.

### `dependency-resolution-failed` - error
^dependency-resolution-failed

**Message:**
the resolver's reason, e.g. `dependency '{name}' is not in the registry` or the git fetch error.

**Triggers:**
a declared dependency the resolver cannot deliver, direct or transitive: no registry entry, no remote, or an unreachable remote. A hard error, a failed open at release, distinct from an expected-unmounted member (which stays advisory). Surfaces on the `resolve` verb's `resolved` frame, one entry per failed member in `failed`, each carrying this `code` and a `reason`. The resolver is per-repo independent, so the rest of the closure still resolves and locks.

### `dependency-path-overridden` - hint
^dependency-path-overridden

**Message:**
`dependency '{name}' is served from a local working tree at {path}, not its locked snapshot at {sha}; edits to the local tree take effect, remove the local resolution (unregister its path or move the co-present sibling) to return to the pinned dependency`.

**Triggers:**
a locked dependency that also resolved to a LOCAL working tree (a co-present sibling or a per-user registry path), so the editable local tree mounts instead of the pinned cache snapshot. This is the sibling → registry → cache order: the local resolution shadows the cache. Informational, never blocks. Exists so a forgotten override does not read as a stale or missing dependency. The dependency-side sibling of a Cargo path / `[patch]` override. Emitted at the local root, one per overridden dependency.

### `dependency-cache-miss` - warning
^dependency-cache-miss

**Message:**
`transitive dependency '{name}' is locked at {sha} but its snapshot is not in the device cache; run resolve to fetch it`.

**Triggers:**
a transitive locked dependency (in the lock, not a manifest member) whose pinned snapshot is absent from the device cache, so it cannot be mounted offline. Advisory, never blocks, the workspace still assembles from the rest, but the dependency's types stay unavailable until a resolve fetches its pinned commit. Without it the transitive dep was silently unmounted, surfacing only later as an unresolved `::repo`. A manifest member gets a role-keyed unmounted code instead (`edit-member-unmounted` / `discover-member-unmounted` / `peer-unmounted`), so this fires only for a transitive dependency. Emitted at the workspace manifest. Carries a fix, run resolve to fetch it. Related to the fresh-clone reproducibility gap, `todo - 2606300141`.

### `dependency-path-escapes-snapshot` - error
^dependency-path-escapes-snapshot

**Message:**
`dependency '{name}' declares a subpath '{path}' that escapes its cache snapshot; an absolute or parent-escaping path is refused, the dependency is not mounted`.

**Triggers:**
a dependency's declared subpath is absolute, or climbs above its cache-snapshot root under lexical normalization (a `../..`). The subpath is untrusted, a transitive peer's subpath is read verbatim from a FETCHED repo's `.arsumbris/repo.yaml`, so an unchecked `snapshot.join(path)` would mount an arbitrary local directory and persist the escaping path into the lock. The engine refuses the subpath, the dependency is excluded from the mounts and the lock, exactly like a conflicted package. A containment guard against a hostile or buggy dependency, not an ergonomic knob. Checked at the single mount choke point, so it holds for the resolve path and the offline locate (a hand-edited or hostile lock) alike. Emitted at the workspace manifest.

### `repo-missing-readme` - warning
^repo-missing-readme

**Message:**
`repo '{name}' has no README.md at its root; a repo self-describes through a root README.md`.

**Triggers:**
an editable repo (the entry or a workspace `edit` member) has no `README.md` at its root. A repo self-describes through a root README, the way it declares its identity through `.arsumbris/repo.yaml`. Scoped to AUTHORING surfaces: a consumed `dep` / `discover` member and a cache snapshot are exempt, their README is their own repo's concern, and an unmounted member is absent from the check by construction. Anchored at the repo's `.arsumbris/repo.yaml`, since the missing file has no span of its own. Carries a fix: add a `README.md` at the root declaring `type: au.engine.readme::au-engine` with a `# Repo Overview` section holding the three sub-sections. Advisory `warning`, never blocks. Computed post-assembly in `au-engine::readme`, listed here with the repo obligations.

### `readme-type-undeclared` - warning
^readme-type-undeclared

**Message:**
`` README.md does not declare `type: au.engine.readme::au-engine`; the canonical README self-declares its type ``.

**Triggers:**
a `README.md` at an editable repo's root that does not self-declare `type: au.engine.readme::au-engine` in its frontmatter. The canonical README self-declares its type (the type-declares-its-place direction), so an undeclared one reads as a plain note and the engine cannot validate it against the section template. Distinct from `repo-missing-readme` (the file is absent) and `readme-misplaced` (a claim off the root). Carries a fix: add the frontmatter claim. Advisory `warning`.

### `readme-misplaced` - warning
^readme-misplaced

**Message:**
`` file claims `au.engine.readme` but is not the repo's root README.md; the readme type is a singleton at `<root>/README.md` ``.

**Triggers:**
a file that claims `au.engine.readme` but is not its repo's root `README.md`. The readme type is a singleton at `<root>/README.md`, so a claim anywhere else is a misplacement. Anchored at the offending claim. Distinct from `repo-missing-readme` and `readme-type-undeclared`. Carries a fix: move the file to the repo root as `README.md`, or drop the claim. Advisory `warning`.

---

## 1. Repo load (au-parser, au-references)

Filesystem walk, file I/O, YAML parse, basename indexing.

Runs before any type-graph work.
Errors here mean a file is skipped.
The rest of the knowledge base still loads.

### `repo-walk-error` - error
^repo-walk-error

**Message:**
`cannot walk repo entry: {os-error}`.

**Triggers:**
per-entry failure during the directory walk.

Failure modes:
- unreadable subdir
- broken symlink
- metadata error
- canonicalize error

Walk skips the entry and continues.
One bad path doesn't void the whole validation.

### `auignore-load-error` - warning
^auignore-load-error

**Message:**
`cannot apply `.auignore`, scoping falls back to the default excludes: {reason}`.

**Triggers:**
a member's `<root>/.arsumbris/.auignore` exists but could not be applied.

Failure modes:
- the read failed (permission, I/O).
- a pattern is malformed.

The member falls back to the default excludes, as if the file were absent.
Scoping degrades loudly, never silently dropping or over-including files.
Advisory, it never aborts the build.

### `auignore-empty-scope` - warning
^auignore-empty-scope

**Message:**
``.auignore` excluded every file under {root}; the member contributes nothing`.

**Triggers:**
a member's `.arsumbris/.auignore` applied cleanly but scoped out every file under the member.

Almost always an over-broad pattern:
- `*`
- `**`
- a stray `/`

Surfaced so an accidental empty scope is loud, not a silently missing subtree.
Advisory, it never aborts the build.

### `repo-file-read-error` - error
^repo-file-read-error

**Message:**
`cannot read repo file: {os-error}`.

**Triggers:**
repo walker listed the file but `read_file` failed.

Failure modes:
- permission denied
- mid-walk deletion
- I/O error

File is skipped.

### `repo-file-not-utf8` - error
^repo-file-not-utf8

**Message:**
`file is not valid UTF-8 (first invalid byte at offset {offset})`.

**Triggers:**
file bytes aren't valid UTF-8.

Fires only for files the parser tries to read:
- type-defs
  - `*.type.yaml` / `*.type.yml` under `type/`
- type-instance candidates
  - `*.md` / `*.yaml` / `*.yml` outside `type/`

Other extensions are assets.
Walker keeps them in `RepoIndex` for `file*` reference resolution,
parser never decodes their bytes,
so a PDF or PNG never triggers this code.

Skipped rather than lossily decoded.
Silent replacement would skew byte offsets in every subsequent diagnostic.

### `file-too-large` - error
^file-too-large

**Message:**
`file is {size} bytes, over the {cap}-byte read cap; it is skipped and not analysed`.
Carries a `fix`: split the file, or exclude it via `.arsumbris/.auignore`.

**Triggers:**
a file the parser would read is larger than the engine's fixed read cap, so it is skipped rather than pulled whole into memory.

The skip-at-read sibling of `repo-file-read-error` and `repo-file-not-utf8`: same `error` tier, same "file is skipped" outcome.
- fires for the same read set: type-defs and instance candidates.
- an asset is never read, so its size is never capped, a multi-gigabyte PDF is fine.
- catalogued by path and kind (an unread entry), so existence-based `file*` and navigational references still resolve, but it carries no parse, no `type:` claim, and no validation.
- an over-cap type-def is a vocabulary error for its repo, so the repo aborts its own instance validation, like an unreadable type-def.

Surfaces a self-inflicted footgun, an oversized note or export dropped into the vault, loudly and actionably rather than as an OOM.
The cap is a generous FIXED ceiling (32 MiB), not yet a config knob.
- a fixed cap is crossed only by a byte-size change, which already dirties the file, so incremental recompute stays byte-identical with no cap-changed re-evaluation.
- making it per-repo adjustable via the scoped config channel is a tracked refinement.

**Spec:** [[type reference]].

### `frontmatter-unterminated` - error
^frontmatter-unterminated

**Message:**
`frontmatter opens with '---' but never closes before EOF`.

**Triggers:**
markdown frontmatter opens with `---` but no closing `---` line is found.

Frontmatter would be silently dropped without this signal.

### `yaml-parse-error` - error
^yaml-parse-error

**Message:**
YAML library's error verbatim.

**Triggers:**
frontmatter (or pure-YAML type-def) fails to parse as YAML.

**Fix:**
a type-def failure carries a targeted `fix` when the source shows an unquoted suffixed inline enum, `myField: [a, b][]`.
- the bare form is not valid YAML, `[a, b]` closes as a flow sequence and the trailing `[]` / `[+]` has no valid parse.
- the fix names the quoting rule and shows the quoted shape, `myField: "[a, b][]"`.
- the shape grammar accepts the string form, quoting is the whole fix, see [[type-def shape enum]].

### `duplicate-key-in-mapping` - warning
^duplicate-key-in-mapping

**Message:**
`duplicate key '{name}' in YAML mapping; saphyr keeps only the last occurrence and silently drops earlier values`.

**Triggers:**
the same key appeared twice (or more) in one YAML mapping.

saphyr silently keeps the LAST occurrence and drops the earlier values.
Fires per second-and-later occurrence, so the dropped earlier value does not vanish silently.
`related` carries the span of the first occurrence.

Advisory, the mapping still parses (last-wins), so it surfaces the drop without blocking.
- a duplicate FIELD in a `fields:` map is the more specific `duplicate-field` instead, see [[spec - diagnostic codes^duplicate-field]].

**Example:**
```yaml
myField: <value>
myField: <value>   # duplicate key; the last value wins, the first is dropped
```

### `mapping-key-not-a-string` - warning
^mapping-key-not-a-string

**Message:**
`mapping key at {span} is not a string; entry dropped`.

**Triggers:**
top-level YAML mapping key on an instance or type-def is not a string.

E.g. `1: foo`, `[a, b]: foo`.

Entry dropped, not error.
Surfaces the likely authoring mistake without aborting.

### `case-collision-basename` - warning
^case-collision-basename

**Message:**
`basename '{a}' collides under case-insensitive comparison with '{b}' — references to either are ambiguous on case-insensitive filesystems (macOS APFS default)`.

**Triggers:**
two basenames in the knowledge base collide under case-insensitive comparison.

Legal on Linux, illegal on macOS-default APFS.

Severity is `warning` because the local knowledge base still validates.
The issue is portability.

**Example:**
```
myNote.md
MyNote.md   # collides under case-insensitive comparison
```

**Spec:** [[type reference]].

---

## 2. Type-def structural parse (au-core::typedef)

Runs while building each `TypeDef` from its YAML doc.

Catches malformed top-level shapes before any structural checks fire.
E.g. `fields:` not a list, `meta:` block missing `type:`.

### `type-def-not-a-mapping` - error
^type-def-not-a-mapping

**Message:**
`type-def root value is not a YAML mapping`.

**Triggers:**
top-level YAML node of a type-def file is not a mapping.

### `parent-claim-bad-shape` - error
^parent-claim-bad-shape

**Message:**
`'extends:' must be a string or list of strings`.

**Triggers:**
`extends:` on a type-def is neither a scalar nor a list of scalars.

**Spec:** [[type list form]], [[type-def extends]].

### `fields-not-a-map` - error
^fields-not-a-map

**Message:**
- `` `fields:` must be a map keyed by field name ``, for a scalar.
- `` `fields:` must be a map keyed by field name, not a list ``, for a YAML sequence.

**Triggers:**
`fields:` is not a YAML map.
- a scalar, malformed.
- a sequence, the retired list-of-single-key-maps form.
  - carries a `fix`, write each field as `name: shape` under `fields:`, not `- name: shape`.

**Spec:** [[type-def fields]].

### `field-decl-bad-shape` - error
^field-decl-bad-shape

**Message:**
- `field name must be a string`, for a non-scalar key.
- `` field name '{name}' is not a valid identifier (must match [A-Za-z][A-Za-z0-9_-]*) ``, for a bad name.

**Triggers:**
a `fields:` map entry has a bad key.
- a non-scalar key.
- a name that violates the field-name grammar.

**Spec:** [[type-def fields]].

### `duplicate-field` - warning
^duplicate-field

**Message:**
`field '{name}' is declared more than once in this type-def`.

**Triggers:**
the same field name appears twice in one type-def's `fields:` map.
A duplicate mapping key, so saphyr keeps only the last and the earlier declaration is silently dropped without this signal.
- `related` points at the first declaration.
- Advisory, the def still loads (last-wins), so the duplicate surfaces without aborting the def or its repo graph.
- keyed on the DIRECT field-key spans, a duplicate key nested inside a field's inline-record shape is a record key, not a field, and does not fire.
- the map form makes this a checkable mapping-key duplicate, the retired list form hid it as two sequence items.
- distinct from `field-redeclaration`, a subtype redeclaring an ANCESTOR's field.
- the engine's generic `duplicate-key-in-mapping` is suppressed for the fields map, so this carries the single signal.

**Example:**
```yaml
fields:
  weight: String
  weight: Number   # duplicate field name; String is silently dropped
```

**Spec:** [[type-def fields]].

### `sealed-bad-shape` - error
^sealed-bad-shape

**Message:**
`'sealed:' must be a list of strings`.

**Triggers:**
`sealed:` is not a list of strings.

**Spec:** [[type-def sealed]].

### `abstract-marker-bad-shape` - error
^abstract-marker-bad-shape

**Message:**
`` `abstract:` must be a boolean (`true` or `false`) ``.

**Triggers:**
the `abstract:` marker's value is not a boolean.
`abstract: true` marks a type-def non-claimable, `false` or absent is concrete.
The type-def still parses, defaulting to concrete, so the rest of the file loads.

**Example:**
```yaml
abstract: maybe   # not a boolean
fields: []
```

### `malformed-brand-shape` - error
^malformed-brand-shape

**Message:**
- `` `shape:` names an empty enum; a named enum must list at least one member ``.
- `` `shape:` enum member must be a string literal ``.
- `` `shape:` enum member '{m}' is not a legal name; a member is a letter then letters, digits, '_' or '-' ``.
- `` `shape:` must be a scalar shape, a `<A | B>` union, a `(A, B)` tuple, or a list of enum members ``.
- `` `shape:` is '{shape}', not a brand form; a brand names a scalar, a named enum, a `<A | B>` union, or a `(A, B)` tuple ``.

**Triggers:**
a `shape:` brand value that is not one of the four brand forms.
- an empty enum list (`shape: []`).
- a non-string enum member.
- a block-list enum member that is not a legal name (`shape: ["a, b", c]`), which would otherwise canonicalize ambiguously.
- a value that is neither a scalar shape-expression nor an enum member list (a mapping, say).
- a parseable shape that is NOT a brand form, a bare record name (`shape: note`), a `*` / `&` reference (`shape: note*`), a `<...>*` compound reference, a `type*` def-ref, `any`, a list (`shape: Number[]`), a pin, or an intersection (`shape: <a & b>`). A brand names a scalar, enum, union, or tuple, nothing else.

A bad shape EXPRESSION, a malformed `<A | B>` or `(A, B)` STRING, is `shape-syntax-error` from the slot grammar instead, since a scalar `shape:` reuses `parse_shape`.

**Example:**
```yaml
# meter.type.yaml
shape:
  a: 1     # a mapping, not a scalar shape or an enum member list
```

### `meta-not-a-list` - error
^meta-not-a-list

**Message:**
`'meta:' must be a list of mappings`.

**Triggers:**
`meta:` is neither a list nor an empty-list suppression marker (`meta: []`).

**Spec:** [[type-def meta]].

### `meta-block-bad-shape` - error
^meta-block-bad-shape

**Message:**
`meta block must have a string 'type:' key`.

**Triggers:**
a `meta:` sub-region is missing its `type:` discriminator, or the value is not a string.

**Spec:** [[type-def meta]].

### `meta-mixin-not-supported` - error
^meta-mixin-not-supported

**Message:**
`meta block 'type:' must be a single name; mixin form is not allowed inside meta`.

**Triggers:**
a `meta:` sub-region's `type:` is a list rather than a bare scalar.

Distinct from `meta-block-bad-shape` so consumers can match on the specific authoring error.

**Example:**
```yaml
meta:
  - type: [myMetaA, myMetaB]   # mixin form not allowed inside meta
```

**Spec:** [[type-def meta]].

### `required-meta-bad-shape` - error
^required-meta-bad-shape

**Message:**
`` `required:` must be a meta type name or a non-empty list of names ``, or `` `required:` list entry must be a meta type name `` for a bad list element.

**Triggers:**
a `required:` item inside `meta:` carries a value that is neither a name nor a non-empty list of names.
The `required:` obligation names the meta types every concrete subtype must carry, per [[type list form]].

**Example:**
```yaml
meta:
  - required: 42   # not a name or list of names
```

### `instance-not-a-mapping` - error
^instance-not-a-mapping

**Message:**
`instance frontmatter root is not a YAML mapping`.

**Triggers:**
top-level frontmatter of an instance file is not a mapping.

### `instance-claim-bad-shape` - error
^instance-claim-bad-shape

**Message:**
specific per failure mode. Examples:
- `` `type:` must be a type-name string or a list of type-name strings ``
- `` `type:` list cannot be empty — a list-form claim must name at least one type ``
- `` `type:` list elements must be type-name strings ``

**Triggers:**
instance `type:` is malformed.

Cases:
- neither a scalar nor a list of scalars.
- an empty list (`type: []`), which must name at least one type.
- a list element that isn't a string.

**Example:**
```yaml
type: []   # a list-form claim must name at least one type
```

**Spec:** [[type list form]], [[type-instance type]].

### `reserved-key-on-instance` - error
^reserved-key-on-instance

**Message:**
`'{key}' is a type-def-only key and not allowed on instances`.

**Triggers:**
a type-def-only key appears on an instance, `fields:` / `sealed:` / `abstract:` / `meta:` / `body:` / `location:` at instance top level, or `fields:` / `sealed:` / `abstract:` / `meta:` / `location:` on an inline value.

**Example:**
```yaml
# an instance file
type: myType
fields:            # type-def-only key, illegal on an instance
  - myField: <shape>
```

**Spec:** [[type-def]].

### `block-id-malformed` - error
^block-id-malformed

**Message:**
- `` `^:` value '{value}' is not a valid block-id — ids are [A-Za-z0-9_-]+ ``
- `` `^:` value must be a scalar block-id ([A-Za-z0-9_-]+) `` for the non-scalar case.

**Triggers:**
the `^:` key on an inline record carries a value that fails the block-id grammar,
or is not a scalar.

String and integer scalars are accepted.
A digit-only id (`^: 123`) YAML-types as an integer, quoting is not required.

The body parser skips a malformed `^marker` silently, it reads as prose.
An explicit `^:` key cannot be prose, so it surfaces.

**Example:**
```yaml
type: myType
myField:
  - ^: "bad id"   # whitespace violates the block-id grammar
    myInner: <value>
```

**Spec:** [[type block-id]].

### `block-id-on-instance-root` - warning
^block-id-on-instance-root

**Message:**
`` `^:` on the instance root has no effect — the file is addressable by name; block-ids belong on inline records ``.

**Triggers:**
a `^:` key at the top level of instance frontmatter.

The key is dropped.
Never silently meaningful, never a field or an extra.

**Example:**
```yaml
type: myType
^: myId        # the file is addressable by name
```

**Spec:** [[type block-id]].

### `missing-type-claim` - error
^missing-type-claim

**Message:**
`instance has no top-level 'type:' key`.

**Triggers:**
instance file has frontmatter but no `type:`.

Direct `parse_instance` callers see this diagnostic.
The engine's build classifies first, so a no-`type:` markdown file becomes a plain note, not a failed instance.

**Spec:** [[type-instance type]].

### `unknown-top-level-key` - warning
^unknown-top-level-key

**Message:**
`unknown top-level key '{name}' on type-def; expected one of: extends / fields / sealed / abstract / meta / body / shape / location`.

**Triggers:**
type-def top-level key isn't one of the engine-recognized keys.

Likely a typo.
Engine drops the entry.
The warning surfaces what was typed.

A stray `type:` at a type-def root does NOT fall here.
- it fires the specific `type-key-on-type-def` error instead, so a mistaken parent claim is never silently dropped.
- see [[spec - diagnostic codes^type-key-on-type-def]].

### `type-key-on-type-def` - error
^type-key-on-type-def

**Message:**
`` `type:` on a type-def is not a parent claim; did you mean `extends:`? ``.

**Triggers:**
a top-level `type:` key on a type-def file.

On a type-def the inheritance claim is `extends:`, and `type:` is the identity claim, which a type-def never makes of itself.
- so a `type:` at a def root is almost always an `extends:` claim written with the wrong key.
- a targeted `error`, never the generic `unknown-top-level-key`, which would DROP the key and silently strip the parent, vanishing the parent's fields from every instance with no signal.
- a permanent guard, not a migration aid, a def-root `type:` is always a likely mistake.
- distinct from `reserved-key-on-instance`, the type-def-only key on an INSTANCE; this is the identity key on a type-DEF.

**Example:**
```yaml
# type/myChild.type.yaml
type: myParent     # wrong key on a type-def; write `extends: myParent`
```

**Spec:** [[type-def extends]], [[type-instance type]].

### `dangling-doc-comment` - warning
^dangling-doc-comment

**Message:**
`` `#:` doc comment is attached to no declaration; it is dropped ``.

**Triggers:**
a `#:` doc comment binds to no declaration.
- trailing a line that carries no declaration.
- a leading block with no declaration following it.

Fires on a type-def surface and an instance surface alike.
- a type-def, over its fields and head.
- a meta block on a type-def, over its head and body fields.
- an instance, over its frontmatter fields, its head, and its nested records.

The doc is dropped.
Surfaced because `#:` signals intended documentation, not an incidental `#` comment.

**Example:**
```yaml
fields:
  - myField: <shape>
#: documents nothing, no declaration follows
```

**Spec:** [[type docstring]].

### `location-bad-shape` - error
^location-bad-shape

**Message:**
specific per failure mode. Examples:
- `` `location:` must be a mapping of name / path / fileType / strict ``
- `` `location.name`: unterminated `${` in name template ``
- `` `location.path`: `..` is not allowed in a location path ``
- `` `location.fileType` must be `md` or `yaml` ``
- `` `location.strict` must be a boolean ``
- `` unknown `location` sub-key '{name}'; expected name, path, fileType, strict ``

**Triggers:**
a `location:` block on a type-def is structurally malformed.
- the block is not a mapping.
- a non-string `name` / `path`, a `fileType` that is not `md` / `yaml`, a non-bool `strict`.
- an unknown sub-key.
- a malformed `name` template, an unterminated `${`, an empty or nested field reference, an illegal field name.
- a malformed `path` glob, absolute, a `..` or `.` segment, an empty (`//`) or partial-glob (`foo*`) segment.

A second pass, over the type's own fields, fires `location-bad-shape` too:
- a `name` `${.field}` references a field ABSENT from the type's effective shape.
- it references an OPTIONAL field, a name template references required fields only.
- it references a DIVERGENT field, a name template needs one unambiguous shape.
- it references a field whose SHAPE is not a safe scalar, `Url`, a list, a reference, a record, a compound, or a tuple, so it does not render one filesystem-safe component.

**Example:**
```yaml
# plan.type.yaml
location:
  fileType: txt        # not md or yaml
```

### `location-filetype-body-conflict` - error
^location-filetype-body-conflict

**Message:**
`` `location.fileType: yaml` conflicts with a non-empty `body:` on '{name}'; a body forces markdown, so no instance can be yaml ``.

**Triggers:**
a type-def declares `location.fileType: yaml` beside a non-empty `body:` (its own, with `use:` splices resolved).
A non-empty body forces markdown ([[spec - diagnostic codes^body-required-but-yaml-only-instance]]), the pin forces yaml, so the type is unsatisfiable, every instance would draw a diagnostic.
An `error`, computed over the type's own fields, so it sits with the location load pass beside the field-safety `location-bad-shape` cases.

**Example:**
```yaml
# x.type.yaml
body:
  - section: S          # forces markdown
location:
  fileType: yaml        # forces yaml — unsatisfiable
```

### `location-mismatch` - warning
^location-mismatch

**Message:**
`file does not match its type's location ({names})`.

**Triggers:**
an instance matches NONE of the soft (non-strict) locations it is subject to.
- a single-claim mismatch, or a mixin matching none of its claimed locations, one case.
- the name stem, the path glob, or the fileType extension does not match.
A `warning`, advisory, the same tier as [[spec - diagnostic codes^readme-misplaced]], never blocks. Anchored at the instance file. A rendered name that is unsafe or empty simply fails to match, so it surfaces here.

### `location-partial-unmet` - hint
^location-partial-unmet

**Message:**
`file matches another claimed location but not '{name}'s (expected {parts})`.

**Triggers:**
in a raw mixin, the instance matched at least one claimed location but not this SOFT one.
A `hint`, the lowest tier: a file cannot be in two places, so an unmet sibling is not a violation. One per unmet soft location. A subtype override, or the file's own placement, resolves which location the file adheres to.

### `location-strict-violation` - error
^location-strict-violation

**Message:**
`file does not satisfy the strict location of '{name}' (expected {parts})`.

**Triggers:**
an instance does not satisfy a `strict: true` location it is subject to.
A strict location is MANDATORY, so it opts out of the mixin satisfy-any and is checked even when another claimed location matches. An `error`. Two mutually-unsatisfiable strict locations in one mixin are uninhabitable, every instance fires this, resolved by softening one or a subtype override.

---

## 3. Slot-expression parse (au-grammar)

Runs while parsing each field shape into a `Shape` AST.

`shape-syntax-error` results are stored on the `FieldDecl` as `parsed_shape: Err(...)`.
They lazy-surface when an instance uses the slot.
(Per the lazy-surfacing mechanism in `validate.rs`.)

### `shape-syntax-error` - error
^shape-syntax-error

**Message:**
specific per failure mode. Examples:
- `shape starts with invalid character '{c}'`
- `'*' suffix on primitive shape '{name}' is not allowed`
- `'&' suffix on inline enum is not allowed`
- `'file&' is not meaningful; use 'file*'`
- `'[+]' suffix has no inner shape`
- `'{name}' is not a valid type-def name`
- `enum literal '{token}' violates the type-name regex`
- `shape has unbalanced brackets: {reason}`
- `union has empty branch`
- `mixed '|' and '&' in one compound`
- `'{token}' has an empty repo scope after '::'; write 'name::repo' or drop the '::'`
- `'{repo}' is not a valid repo name in a '::repo' qualifier`
- `built-in shape '{name}' cannot carry a '::repo' qualifier; '::repo' names a peer type-def`

**Triggers:**
the field's right-hand shape expression fails to parse per the [[type-def field shape]] grammar.

Covers all parse failures from au-grammar.
Surfaces at the use site, not at type-graph load.

**Example:**
```yaml
fields:
  - myField: String*   # '*' is not allowed on a primitive shape
```

{@gian should we consider splitting this up into individual codes?}
The value-refinement and cardinality failures ARE split out, see the two codes below.

### `refinement-bad-shape` - error
^refinement-bad-shape

**Message:**
specific per failure mode. Examples:
- `a comparison predicate applies to an ordered primitive (Number, Date, DateTime), not '{p}'`
- `the 'integer' predicate applies to a 'Number' base, not '{p}'`
- `a regex predicate applies to a 'String' base, not '{p}'`
- `refinement has more than one lower bound`
- `'{s}' is not a valid number literal`
- `refinement '{}' has no predicate`
- `regex predicate /{p}/ is not a valid regular expression` (at load, incl. backreference / lookahead)
- `'{s}' is not a valid Date literal` (at load)

**Triggers:**
a value refinement ([[type-def field shape]], `Base{predicate}`) is malformed.
- at PARSE, a predicate invalid for its base, a duplicate-kind predicate, a bad number literal, an empty or non-primitive refinement, an unterminated regex.
- at LOAD, a regex that does not compile (the finite-automaton engine also rejects the non-regular backreference / lookahead forms), or an invalid `Date` / `DateTime` bound literal.

**Example:**
```yaml
# myType.type.yaml
fields:
  bad: String{>=0}   # a comparison does not apply to String
```

### `cardinality-bad-shape` - error
^cardinality-bad-shape

**Message:**
- `list cardinality '[{x}..{y}]' is inverted; the lower bound must not exceed the upper`
- `list cardinality bound '{s}' is not a non-negative integer`
- `'[..]' is redundant with '[]'; use '[]'`

**Triggers:**
a list cardinality suffix ([[type-def shape suffixes]], `T[x..y]`) is malformed.
- an inverted range `[5..1]`, a non-integer or negative bound, or the redundant `[..]`.

**Example:**
```yaml
# myType.type.yaml
fields:
  bad: point[5..1]   # inverted range
```

### `not-yet-implemented-shape-feature` - error
^not-yet-implemented-shape-feature

**Message:**
placeholder for future deferred features.

**Triggers:**
forward-compat hook.
Test helpers synthesize this to exercise the lazy-surfacing dispatch.

---

## 4. Type-graph build + structural load checks (au-core::load_checks, au-engine::engine_schema)

Runs after every type-def has been parsed.
Failures here usually block per-instance validation for the affected types.
The engine-namespace reservation codes and `type-def-outside-type-dir` are the exception, advisory notes the engine layers on over the parsed defs.

### `duplicate-type-def` - error
^duplicate-type-def

**Message:**
`type-def name '{name}' is declared by multiple files: {paths}`.

**Triggers:**
two or more files derive the same type-name.

The name derives from the basename, path-independent, so two same-basename `.type.yaml` files in different directories collide.

**Example:**
```
type/myType.type.yaml
type/nested/myType.type.yaml   # same type name from two files
```

### `type-def-outside-type-dir` - warning
^type-def-outside-type-dir

**Message:**
`` type-def does not live under a `type/` directory; by convention every type-def sits under the repo's `type/` ``.

**Triggers:**
a type-def file, classified by its `.type.yaml` / `.type.yml` suffix, whose path has no `type/` component relative to its member root.

The suffix is the SOLE classification marker, so the file is a valid type-def regardless.
The `type/` directory is an authoring convention, so a type-def outside it is surfaced, never reclassified.
- advisory `warning`, never blocks, [[type open-world validation]].
- fires on LOCATION, independent of parse outcome, so a malformed misplaced type-def warns too.
- relative-to-member-root, so a `type` component in the root's own path prefix does not falsely satisfy the convention.
- a prose `README.md` under `type/` is NOT a type-def, so it never fires this, it is a plain note.

Carries a `fix`: move the file under the repo's `type/` directory.
Emitted in au-engine::build, over each classified type-def file.

**Example:**
```
notes/widget.type.yaml   # a valid type-def by suffix, but not under `type/`
```

**Spec:** [[type-def]].

### `engine-name-forward-reserved` - hint
^engine-name-forward-reserved

**Message:**
`type-def '{name}' is in the engine-reserved 'au.engine.*' namespace, which the engine may hardwire in a future version`.

**Triggers:**
a repo-authored type-def whose name sits in the reserved `au.engine.*` namespace, but is not one of the engine's hardwired defs.
The namespace is reserved by CONVENTION, forward: the engine may hardwire this name later, at which point the repo def would live-shadow it (`engine-name-live-shadow`).
Advisory, never blocks. The repo def keeps its own `(name, hash)` identity and resolves normally, so this is a heads-up, not a rejection.
The engine's own hardwired defs never fire this, they are seeded into the `au-engine` repo, never walked as repo files.

**Example:**
```
type/au.engine.widget.type.yaml   # in the reserved namespace, not a hardwired def
```

### `engine-name-live-shadow` - warning
^engine-name-live-shadow

**Message:**
`type-def '{name}' shares a name with a hardwired engine type; both coexist as distinct identities, '{name}::au-engine' names the engine's`.

**Triggers:**
a repo-authored type-def named EXACTLY like one of the engine's hardwired `au.engine.*` types.
COEXISTENCE, not annihilation: the two are distinct `(name, hash)` identities in distinct repos, so it is not a `duplicate-type-def`.
The bare name resolves to the knowledge base's def in its own repo, `::au-engine` scopes the engine's, they compose like any cross-repo same-name pair.
The code only NOTES that the engine owns the name, it never ignores or overrides the knowledge base's def.
Advisory, never blocks. Fires for EVERY hardwired-name shadow, in-sync or diverged. A diverged shadow additionally fires `engine-name-shadow-drift` (`drift`), the in-sync-versus-diverged enrichment against the engine's `(name, hash)`.

**Example:**
```
type/au.engine.repo.type.yaml # same name as the hardwired au.engine.repo::au-engine
```

### `engine-name-shadow-drift` - drift
^engine-name-shadow-drift

**Message:**
`type-def '{name}' shadows a hardwired engine type and has DIVERGED from it; the engine's copy is '{name}::au-engine'`.

**Triggers:**
a repo-authored type-def named like a hardwired `au.engine.*` type whose `(name, closure-hash)` identity DIFFERS from the engine's copy.
Emitted alongside `engine-name-live-shadow` (which notes the coexistence for every shadow); this escalates a DIVERGED shadow to the `drift` tier, the advisory-high-attention tier for a cross-version divergence, so a consumer can rank it above an in-sync shadow.
Computed post-graph-build by comparing the repo def's closure-hash to the engine's hardwired copy of the same name; an IN-SYNC shadow (equal hashes) fires only `engine-name-live-shadow`, never this.
Advisory, never blocks; the repo def resolves standalone in its own repo. The engine-SDK mirror consistency guard builds on this same `(name, hash)` comparison.

**Example:**
```
type/au.engine.repo.type.yaml   # named au.engine.repo but with different fields than the engine's
```

### `engine-schema-type-unwritten` - drift
^engine-schema-type-unwritten

**Message:**
`` engine-schema file carries no written `type:`; the kind assigns the floor `{floor}` regardless, but the file does not self-describe on disk ``.

**Triggers:**
an engine-schema file (`repo.yaml`, `workspace.yaml`, the locks, the device-config files) carries no written top-level `type:` key.
The file KIND still assigns the floor type, so the file stays fully correct and the engine reads its data from the claim-independent resolution path.
`drift`, a high-attention advisory, never blocks.
The engine's own writers emit the qualified `type: au.engine.X::au-engine`, so an absent one reads as a hand-authored or legacy file.
The suggested written form follows the file's validation scope.
- an in-repo file crosses to the builtin peer, so `{floor}` is `::au-engine`-qualified.
- a device-global file validates in the builtin's own scope, so `{floor}` is BARE, a `::au-engine` self-qualifier there is a redundant `type-repo-self`.

**Example:**
```yaml
# .arsumbris/repo.yaml
name: myrepo # no written `type:` — the floor au.engine.repo::au-engine still applies
```

### `engine-schema-type-floor-omitted` - error
^engine-schema-type-floor-omitted

**Message:**
`` engine-schema file writes a `type:` whose closure omits the kind's floor `{floor}::au-engine`; the written claim names the wrong kind ``.

**Triggers:**
an engine-schema file writes a `type:` whose RESOLVED closure does not include the kind's floor type.
The written claim names the wrong kind, so the file does not self-describe as what it structurally is.
- e.g. a `repo.yaml` written `type: au.engine.workspace::au-engine` names the wrong floor.
An `error`, but recoverable, never lost data.
The engine still reads its data from the kind-assigned floor, the resolution path is claim-independent.
A written claim that INCLUDES the floor and mixes in more is fine.
An UNRESOLVABLE claim is the `unknown-type-claim` gate's, so it is skipped here, no double-signal.
Computed over the resolution graph, so a subtype whose closure folds the floor in satisfies it.

**Example:**
```yaml
# .arsumbris/repo.yaml
type: au.engine.workspace::au-engine # wrong floor: a repo.yaml is au.engine.repo
name: myrepo
```

### `config-type-unresolved` - warning
^config-type-unresolved

**Message:**
`` type `{type}` does not resolve in `{scope-repo}`, so the config is stored as-is and not field-shape checked ``.

**Triggers:**
a scoped-config `config` read or `set_config` write names a `type` that does not resolve to a def in the scope's graph.
- repo scope resolves in the owning member's graph, machine scope in the served entry's graph, a `foo::repo` type in the named peer's graph.
The value is STORED as-is, the field-shape check is skipped, so the file still reads and writes.
`warning`, advisory, never a refusal.
- machine-scope config stays writable regardless of the served workspace, and a consumer's type vocabulary may simply not be mounted.
- so the honest guarantee is field-shape checked WHEN the type is available, stored as-is otherwise.
Replaces the hard `unknown-type-claim` a walked instance would get, this channel is store-and-advisory by design.

### `config-type-unwritten` - drift
^config-type-unwritten

**Message:**
`` config file carries no written `type:`; the declared type `{type}` is applied regardless, but the file does not self-describe on disk ``.

**Triggers:**
a scoped-config file carries no written top-level `type:` key.
The declared wire `type` is stamped as the floor, so the file stays fully correct and field-shape validated, this is only the nudge to self-describe.
`drift`, high-attention advisory, never blocks.
- a governed `set_config` write INJECTS `type:`, so an absent one reads as a hand-authored or seeded file.
- a written `type:` WINS over the stamp and may subtype the declared floor, mixing in more.
The config-channel sibling of `engine-schema-type-unwritten`, which is for the engine's OWN device files (a kind-assigned `au.engine.*` floor), so the two never overlap.

### `type-name-violates-regex` - error
^type-name-violates-regex

**Message:**
`type name '{name}' violates the type-name regex`.

Variants:
- `parent type name '{name}' violates the type-name regex`
- `sealed branch name '{name}' violates the type-name regex`

**Triggers:**
the type-def name, any parent claim name, or any sealed branch name doesn't match `^[A-Za-z][A-Za-z0-9_-]*(\.[A-Za-z][A-Za-z0-9_-]*)*$`.

The same regex applies to enum elements ([[type-def shape enum]]).
Those fire as `shape-syntax-error` from the shape parser, not as this code.

**Example:**
```yaml
extends: 1myParent   # type names must start with a letter
```

**Spec:** [[type-def legal names]].

### `reserved-type-name` - error
^reserved-type-name

**Message:**
`type-def name '{name}' is reserved by the engine ({rationale})`.

**Triggers:**
a user type-def claims a reserved name.

Reserved names:
- `file` (built-in any-repo-file reference target)
- `any` (the no-type slot shape)
- `opaque` (the uninterpreted slot shape)
- primitive shapes
  - `String`
  - `Number`
  - `Boolean`
  - `Date`
  - `DateTime`
  - `Url`

**Example:**
```yaml
# file: String.type.yaml   # 'String' is a reserved primitive name
fields:
  - myField: <shape>
```

**Spec:** [[type-def legal names]], [[type-def shape primitive]], [[type-def shape file]], [[type-def shape any]].

### `cycle-in-type-chain` - error
^cycle-in-type-chain

**Message:**
`type-def '{name}' has a cycle in its 'extends:' chain: {a → b → ... → a}`.

**Triggers:**
`extends:` chain contains a cycle.

Blocks closure walks.
Downstream checks short-circuit on cyclic types.

Also fires across a repo boundary.
- a cross-repo `extends:` cycle, `H` in one repo `extends: B::repo`, `B` in another `extends: H::repo`, spans two graphs.
- the own-graph cycle check sees one graph, so the fold's resolved parent edges surface it.
- reported from each importing repo's resolution graph, anchored at a member that repo owns, so a purely-imported cycle is left to the repos that own it.
- the message renders each member's authored form, `H -> B::repo -> H`, the peer member qualified.
- aborts each owning repo's instance validation, at parity with the single-repo case, so instances never validate against the degenerate cyclic-union closure. Every repo owning a cyclic member imports (it has a `::repo` parent), so each emits and aborts its own.

**Example:**
```yaml
# type/myA.type.yaml
extends: myB

# type/myB.type.yaml
extends: myA          # cycle: myA -> myB -> myA
```

**Spec:** [[type closure]].

### `type-chain-depth-exceeded` - error
^type-chain-depth-exceeded

**Message:**
`type-chain walk exceeded MAX_TYPE_CHAIN_DEPTH starting from '{name}'`.

**Triggers:**
defensive guard.
Chain walker exceeds the depth limit without terminating.

Either:
- a pathologically deep chain
- a cycle that slipped past `cycle-in-type-chain`

Fires cross-repo too, on the FOLDED chain, like `cycle-in-type-chain`.
- the fold's walk hits the bound over a chain spanning repos.
- gated to a cross-boundary chain anchored at an owned member, so it never double-fires with the per-repo own-graph check.

### `duplicate-meta-block` - error
^duplicate-meta-block

**Message:**
`type-def '{host}' has two 'meta:' sub-regions for the same type '{meta-type}'`.

**Triggers:**
two `meta:` sub-regions on one host use the same `type:` discriminator.

Keyed on `(type_name, repo)`, so an own meta and a same-named PEER meta coexist.
- `display-meta` and `display-meta::other` are distinct types, not a duplicate.
- only a same-`(name, repo)` pair fires.

**Example:**
```yaml
meta:
  - type: myMeta
    myField: <value>
  - type: myMeta     # second sub-region for the same meta-type
    myField: <value>
```

**Spec:** [[type-def meta]] singleton rule.

### `slot-references-absent-type` - error
^slot-references-absent-type

**Message:**
`field '{field}' on type-def '{td}': slot references absent type '{name}'`.

**Triggers:**
a `Shape::Reference` slot (`name*`) names a type-def that isn't in the type graph, and the name isn't the built-in `file`.

Walks `Shape::List` wrappers transparently.

**Example:**
```yaml
fields:
  - myField: myMissingType*   # myMissingType is not in the type graph
```

**Spec:** [[type-def shape record]].

### `parent-references-absent-type` - error
^parent-references-absent-type

**Message:**
`type-def '{td}' claims parent '{name}', which is not in the type graph`.

**Triggers:**
an `extends:` claim names a type-def that isn't in the type graph, and the name isn't the built-in `file`. The closure truncates silently otherwise, the parent's fields vanish from every instance with no signal. The parent sibling of `slot-references-absent-type`; fires for every type-def.

**Spec:** [[type-def extends]].

### `required-meta-absent-type` - error
^required-meta-absent-type

**Message:**
`type-def '{td}' requires meta '{name}', which is not in the type graph`.

**Triggers:**
a bare `required:` obligation names a type-def absent from the graph. An absent obligation could never be satisfied. The meta sibling of `slot-references-absent-type` / `parent-references-absent-type`. A `::repo`-qualified `required:` target is the cross-repo gate's (`type-repo-*` / `peer-type-not-found`), not this code's. A present-but-non-meta target is `required-meta-not-a-meta-type`.

**Example:**
```yaml
meta:
  - required: ghost-meta   # ghost-meta is not in the type graph
```

### `subsumption-in-slot-union` - warning
^subsumption-in-slot-union

**Message:**
`field '{f}' on type-def '{td}': slot-union branch '{X}' adds nothing — '{Y}' is wider and accepts every '{X}' value`.

**Triggers:**
a slot-union has two branches in a strict subset relationship.

Two cases:
- subtype-by-closure: `<decision | decision.decided>`
- cardinality-refinement: `<T[] | T[+]>`

The narrower branch is redundant because the wider already accepts every value it would.

**Example:**
```yaml
# myParent is sealed, myParent.myLeaf is one of its leaves
fields:
  - myField: <myParent | myParent.myLeaf>   # leaf adds nothing; parent is wider
```

**Spec:** [[type-def shape compound]].

### `subsumption-in-slot-intersection` - warning
^subsumption-in-slot-intersection

**Message:**
`field '{f}' on type-def '{td}': slot-intersection branch '{X}' adds nothing — '{Y}' is stricter and the intersection collapses to '{Y}'`.

**Triggers:**
mirror of slot-union.
A slot-intersection has two branches in a strict subset relationship.

The wider branch is redundant.
The intersection collapses to the stricter.

**Example:**
```yaml
fields:
  - myField: <myParent & myParent.myLeaf>   # collapses to myParent.myLeaf
```

**Spec:** [[type-def shape compound]].

### `redundant-abstract-on-sealed` - hint
^redundant-abstract-on-sealed

**Message:**
`` type-def '{name}' is sealed, which already implies abstract; the explicit `abstract: true` is redundant ``.

**Triggers:**
a sealed type-def also declares `abstract: true`.
Sealed is abstract plus a closed branch set, so it already carries non-claimability.
Advisory hint, never blocks. The sealed form is the stricter one, so the marker adds nothing.

**Example:**
```yaml
# decision.type.yaml
abstract: true    # redundant: sealed already implies it
sealed:
  - decision.pending
```

### `brand-with-record-keys` - error
^brand-with-record-keys

**Message:**
`` type-def '{name}' declares both `shape:` (a brand) and record key(s) ({keys}); a def is a brand XOR a record ``.

`{keys}` lists the conflicting record keys present, each backticked, e.g. `` `fields:`, `body:` ``.

**Triggers:**
a type-def declares `shape:` (a brand) beside a record key, `fields:`, `sealed:`, or a non-empty `body:`.
A def is a brand XOR a record: a brand names an underlying shape and has no fields.
An `error`, anchored at the def. Carries a fix: keep `shape:` for a brand, or the record keys for a record, not both.
A `meta:` or `abstract:` beside `shape:` is NOT part of this conflict; only the record-shape keys are.

**Example:**
```yaml
# bad.type.yaml
shape: Number
fields:            # a brand has no fields
  a: String
```

### `brand-not-referenceable` - error
^brand-not-referenceable

**Message:**
one of, `{suffix}` is `*` or `&`:
- nominal, `` field '{field}' on type-def '{td}': slot references nominal brand '{name}' with '{suffix}'; a nominal brand (scalar / enum / tuple) is inline-only, use it by bare name '{name}' ``.
- union with a non-record member, `` field '{field}' on type-def '{td}': slot references union brand '{name}' with '{suffix}', but it has a non-record member; a union brand is referenceable only when every member is a record type, so use it by bare name '{name}' ``.

**Triggers:**
a field slot demands a brand with a `*` or `&` reference suffix the brand does not admit.
- a NOMINAL brand (a `shape:` def whose shape is a scalar, enum, or tuple), inline-only like the primitive it wraps, so it is used by BARE NAME, not referenced.
- a STRUCTURAL (union) brand with any non-record member (`<evidence | String>`, `<meter | second>`); a union is referenceable ONLY when every member is a record type.
A load-time slot-declaration check, walking each field shape (through list, pin, union, and compound-reference wrappers), so it fires once at the def, independent of any instance.
Fires cross-repo too: a `::repo` brand reference (`evidence-kind::sdk*` over a nominal or mixed-member peer brand) is gated at the cross-repo type pass against the peer's graph, so the diagnostic reaches a peer brand exactly as an own one.
Carries a fix: drop the suffix, write the slot by bare name.

**Example:**
```yaml
# icon-role.type.yaml is a nominal enum brand
# command-meta.type.yaml
fields:
  icon: icon-role*    # nominal brand, inline-only; write `icon: icon-role`
```

---

## 5. Inheritance load checks (au-core::load_checks)

Runs after structural checks.
Requires the closure walk to function.
Cyclic types short-circuit.

### `field-redeclaration` - error
^field-redeclaration

**Message:**
`field '{name}' on type-def '{td}' is already declared by ancestor '{ancestor}'`.

**Triggers:**
a subtype declares a field name an ancestor already carries.

Width-only subtyping forbids redeclaration even with identical shape.

**Example:**
```yaml
# type/myParent.type.yaml
fields:
  - myField: <shape>

# type/myChild.type.yaml
extends: myParent
fields:
  - myField: <shape>   # already declared by myParent
```

**Spec:** [[type subtyping width-only]].

### `sealed-no-surprise-children` - error
^sealed-no-surprise-children

**Message:**
`type-def '{td}' transitively claims sealed parent '{sealed}' without going through any of its listed branches: {branches}`.

**Triggers:**
a type-def's `extends:` chain crosses a sealed parent.
The chain isn't transitively reachable through any listed sealed branch.

**Example:**
```yaml
# type/myParent.type.yaml
sealed:
  - myParent.myLeaf

# type/myStray.type.yaml
extends: myParent     # crosses sealed myParent without being a listed branch
```

**Spec:** [[type-def sealed]].

### `mixin-collision` - error
^mixin-collision

**Message:**
`field '{name}' is declared with non-token-equal shapes across mixin origins: {origin-summary} — a bare use is ambiguous; qualify each use as `{name}{type}``.

`{origin-summary}` lists each origin in authored form with its raw shape, `'note' (String), 'note::base' (Number)`.

**Triggers:**
a BARE use of a divergent field, a same field name reached by mixin origins with non-token-equal `parsed_shape`.

Fires at validate time, against the instance's claim list, on a bare use of the divergent field.
- every use must be qualified (`field{type}`); a bare value cannot disambiguate the origins.
- a divergent inherited field is LEGAL at a type-def, so the type-graph load fires nothing.
- the collision can only be resolved per-instance (a `field{type}` qualifier), so it surfaces there, see [[type-def fields collision - auto-unify and qualified field]].
- ADDITIVE with `required-field-absent`: a bare value fills no origin, so on a required divergent field the collision and the per-origin required diagnostics both fire; it does NOT suppress required.

**Example:**
```yaml
# myA declares  myField: String
# myB declares  myField: Number
# (myC extends [myA, myB] — a divergent inherited myField, LEGAL at the type-def)

# an instance
type:
  - myA
  - myB
myField: hello     # BARE use of the divergent field → mixin-collision
# fix: qualify each use, myField{myA} and myField{myB}
```

**Cross-repo same-name diamond:**
`mixin-collision` also covers a folded cross-repo mixin that reaches two DISTINCT identities of one type name.
- own plus peer (`type: [note, note::base]`), or two peers (`type: [foo::a, foo::b]`).
- when they disagree on a field, that is a collision like any two ancestors.
- the origin's authored form (`note::base`) distinguishes the identities, so the message does not read as `note` vs `note`.
- resolvable by the qualified field key, `field{note}` for own and `field{note::base}` for the peer.

**Spec:** [[type-def fields collision - auto-unify and qualified field]].

### `duplicate-claim` - warning
^duplicate-claim

**Message:**
`claim '{name}' appears more than once in '{td}' / instance type list`.

**Triggers:**
repeated name in an `extends:` or `type:` list.

The closure dedupes silently.
The warning surfaces the likely authoring mistake.

Fires at:
- load time (type-def parents)
- validate time (instance claims)

**Example:**
```yaml
type:
  - myType
  - myType         # repeated claim
```

**Spec:** [[type-instance type]].

### `subsumption-in-mixin` - warning
^subsumption-in-mixin

**Message:**
`claim '{X}' is implied by '{Y}' and is redundant`.

**Triggers:**
one claim's closure includes another in the same `extends:` or `type:` list.
The wider claim is implied by the narrower.

Fires at both load and validate time.
Symmetric to the [[type-def shape compound]] slot-union subsumption.

**Example:**
```yaml
# myChild.type.yaml
extends:
  - myParent

# myOtherType.type.yaml
extends:
  - myParent # myParent is implied by myChild
  - myChild # myChild implies myParent
```

**Spec:** [[type-instance type]].

---

## 6. Per-instance validation (au-core::validate)

Runs per instance file after type-graph load succeeds.
Per-file errors don't block other files.

### `unknown-type-claim` - error
^unknown-type-claim

**Message:**
`instance claims unknown type '{name}'`.

**Triggers:**
instance `type:` claim names a type-def absent from the type graph.

**Example:**
```yaml
type: myMissingType   # not defined in the type graph
```

**Spec:** [[type-instance type]].

### `required-field-absent` - error
^required-field-absent

**Message:**
`instance is missing required field '{name}' (declared on '{origin}')`.
- a near-miss suffix is appended when an undeclared present key looks like a typo of the missing name.
  - `… — did you mean '{key}'?`, with a related span pointing at the suspected key.
  - the near-miss is an undeclared bare key within a small edit distance of the missing field name.

**Triggers:**
a required field declared by the instance's effective shape is missing.

Missing covers two forms.
- the frontmatter key is absent, no body contribution.
- the frontmatter key is a null "filled by body" anchor, but no body contribution arrives, see [[type-instance body contribution]].
  - the null anchor promises a body fill, an unkept promise leaves the field as absent as an omitted key.

The near-miss hint is advisory sugar on the same diagnostic, it never changes the severity or whether the code fires.
- it surfaces at every claim site, instance frontmatter, inline records, and meta sub-region bodies.

Per [[type-def fields collision - auto-unify and qualified field]], fires per originator if the same field has mixed required / optional declarations across mixin branches.

**Example:**
```yaml
# myType.type.yaml
fields:
  - myField: <shape> # required field

# myInstance.yaml
type: myType
# myField omitted
```

**Spec:** [[type-instance fields]], [[type-def fields collision - auto-unify and qualified field]].

### `field-shape-mismatch` - error
^field-shape-mismatch

**Message:**
specific per failure mode. Examples:
- `field '{f}' value does not match declared shape '{shape}'`
- `field '{f}' value is an empty list — declared shape {inner}[+] requires one or more elements`
- `field '{f}' value is not a list — declared shape is {inner}{[] or [+]}`
- `field '{f}' value '{s}' is a wikilink but its target satisfies none of the reference branches in declared shape {shape} (attempted: {branches})`
- `` field '{f}' references '{s}' with a sub-file fragment — `file*` references a whole file; use `any*` to address a `^block-id` or `#head` ``

**Triggers:**
a field's value doesn't match its declared shape.

Failure modes covered:
- primitive type mismatch
- enum non-member
- empty list on `T[+]`
- list-element shape mismatch
- union no-branch-matches
- a `file*` value carrying a `^block-id` or `#head` fragment, see [[type-def shape file]]
- ...

The catch-all shape-conformance code.

**Example:**
```yaml
# myType.type.yaml
fields:
  - myNumber: Number

# myInstance.yaml
type: myType
myNumber: "not a number" # value does not match declared shape
```

**Spec:** [[type-instance fields]].

### `non-finite-number` - error
^non-finite-number

**Message:**
`field '{f}' is a non-finite number ({value})`.

**Triggers:**
a `Number` field holds a non-finite float.
- `.nan`, `.inf`, `-.inf`.
- these parse as floats but are not valid numbers.

Distinct from `field-shape-mismatch`.
- the value is a float, so "does not match Number" would mislead.
- the real problem is non-finiteness.

**Example:**
```yaml
# myType.type.yaml
fields:
  - myNumber: Number

# myInstance.yaml
type: myType
myNumber: .nan # a non-finite number
```

**Spec:** [[type-instance fields]].

### `value-out-of-refinement` - error
^value-out-of-refinement

**Message:**
`field '{f}' value {v} is not {op} {bound}`, or `... value {v} is not an integer`.

**Triggers:**
a value is the right base type but falls outside its slot's value refinement.
- `-1` in a `Number{>=0}` slot.
- `1.5` in a `Number{integer}` slot.
- `2019-12-31` in a `Date{>=2020-01-01}` slot.

Distinct from `field-shape-mismatch`.
- the value IS the base type, so "does not match" would mislead.
- the message names the failed predicate.

Suppressed when the refinement is provably empty.
- `refinement-unsatisfiable` fires on the type-def instead.

**Example:**
```yaml
# myType.type.yaml
fields:
  depth: Number{>=0}

# myInstance.yaml
type: myType
depth: -1 # outside the refinement
```

### `refinement-unsatisfiable` - warning
^refinement-unsatisfiable

**Message:**
`field '{f}' declares a value refinement '{shape}' that admits no value`.

**Triggers:**
a type-def field's value refinement has a numeric meet that admits no value.
- `Number{>=5 & <=1}`, an empty interval.
- `Number{>=2 & <2}`, a single exclusive point.
- `Number{>2 & <3 & integer}`, no integer in the range.

A `warning` on the type-def, advisory, never blocks.
- the slot can never be satisfied, so every value would fail.
- the validator suppresses the per-value `value-out-of-refinement` and surfaces this once.

**Example:**
```yaml
# myType.type.yaml
fields:
  impossible: Number{>=5 & <=1}
```

### `brand-constructor-mismatch` - error
^brand-constructor-mismatch

**Message:**
one of:
- single brand, `` field '{f}' constructor names brand '{ctor}', but the slot demands '{brand}' ``.
- union, `` field '{f}' constructor names brand '{ctor}', not a member of union '{brand}' ``.
- union record member, `` field '{f}' constructor names record member '{ctor}' of union '{brand}'; a record member is claimed with an inline `type:`, not a constructor ``.

**Triggers:**
an explicit `Name(...)` constructor names a type the slot does not admit.
- the admitted names are the slot's own brand, or a member of its union, records / nominal brands / primitives alike.
- `length: second(42)` where the slot is `length: meter`, a foreign brand.
- `length: Number(42)` where the slot is `length: meter`, a reserved primitive that is not a union member, admitted only as a member.
- a `::repo`-qualified peer brand at an own-repo brand slot.

A bare value COERCES to the slot's brand silently, the slot is the authority, so nominal safety lands only where the author was explicit.
- `length: 42` and `length: meter(42)` are both accepted.

A reserved-primitive constructor IS admitted where the primitive is a union member, the literal escape, not a mismatch.
- `String("looks(foo)")` at `<String | label>` forces the plain-String branch.

**Example:**
```yaml
# meter.type.yaml -> shape: Number ; second.type.yaml -> shape: Number
# myType.type.yaml
fields:
  length: meter

# myInstance.yaml
type: myType
length: second(42) # names a foreign brand
```

### `brand-constructor-required` - error
^brand-constructor-required

**Message:**
one of:
- ambiguous, `` field '{f}' bare value is ambiguous at union brand '{brand}'; name the branch with a `Name(...)` constructor ``.
- inline, `` field '{f}' inline value at union brand '{brand}' needs a `type:` to pick a member ``.

**Triggers:**
a bare value at a union brand slot cannot be discriminated to one member.
- a bare value TWO OR MORE admitting members accept, sharing one base primitive with no distinguishing predicate.
  - `"hi"` at `<String | label>`, both represented as `String`; name the branch, `String("hi")` or `label("hi")`.
  - `42` at `<meter | second>`, both nominal over `Number`; write `meter(42)` / `second(42)`.
- an inline record with no `type:` to pick a record member.

A bare value with a single unambiguous branch coerces, no error.
- a distinguishing predicate discriminates, a `Url` prefix, a `Date` / `DateTime` format, a refined `{...}`, an enum membership.
- so `<String | Url>`, `<String | meter>`, `<Number | Date>` pick by the value's shape, never ambiguous.

**Example:**
```yaml
# meter.type.yaml -> shape: Number ; second.type.yaml -> shape: Number
# quantity.type.yaml -> shape: <meter | second>
# myType.type.yaml -> fields: { v: quantity }
type: myType
v: 42 # cannot tell meter from second → write meter(42)
```

### `tuple-arity-mismatch` - error
^tuple-arity-mismatch

**Message:**
`` field '{f}' tuple has {got} element(s), but the declared shape has {expected} ``.

**Triggers:**
a tuple value's element count differs from the declared arity.
- a `point(20, 30, 40)` constructor at a `(Number, Number)` slot.
- a wrong-arity paren form `(20)` at an inline `(Number, Number)` slot.

A tuple is a fixed-arity positional product, every element required, so a wrong count cannot be checked positionally.
A `[...]` bracket is always a list value, so a `[20, 30]` at a tuple slot is a `field-shape-mismatch` (a list where a tuple is wanted), not this code.

**Example:**
```yaml
# point.type.yaml -> shape: (Number, Number)
# myType.type.yaml -> fields: { pt: point }
type: myType
pt: point(20, 30, 40) # three args, arity is two
```

### `malformed-constructor` - warning
^malformed-constructor

**Message:**
`` field '{f}' value looks like a `Name(...)` constructor but is malformed ``.

**Triggers:**
a value at a nominal brand slot starts a `Name(` constructor shape but does not close as a well-formed one.
- an unbalanced paren, `meter(42`.
- content after the closing `)`, `meter(42)x`.

A `warning`, advisory, the file still loads.
- surfaces the one actionable problem, the mis-typed constructor, not a secondary shape mismatch on the broken string.
- "starts a constructor" is a tight token, a legal name followed IMMEDIATELY by `(`, so prose like `save (the file)` is a plain value, never this.

**Example:**
```yaml
# meter.type.yaml -> shape: Number
# myType.type.yaml -> fields: { length: meter }
type: myType
length: meter(42 # unbalanced
```

### `sealed-parent-claimed` - error
^sealed-parent-claimed

**Message:**
`claim '{name}' is a sealed type-def and cannot be claimed directly`.

**Triggers:**
any element of a `type:` claim list names a sealed type-def.

Claim sites:
- file-level
- inline-value
- meta-region

Per-claim: a non-sealed sibling in a mixin does not excuse a sealed claim.

**Example:**
```yaml
# myParent.type.yaml
sealed:
  - myParent.child1
  - myParent.child2

# myInstance.yaml
type: myParent  # myParent is sealed; a non-sealed leaf must be claimed
```

**Spec:** [[type-def sealed]].

### `abstract-type-claimed` - error
^abstract-type-claimed

**Message:**
`type-def '{name}' is abstract and cannot be claimed directly; claim a concrete subtype`.

**Triggers:**
a claim names a declared-abstract, non-sealed type.
Abstract types are non-claimable but open to subtyping, so a claim must drill to a concrete subtype.

Claim sites:
- file-level
- inline-value
- meta-region

Per-claim: a concrete sibling in a mixin does not excuse the abstract claim, parallel to `sealed-parent-claimed`.

A sealed claim fires the more specific `sealed-parent-claimed` instead, never both.
Sealed is abstract plus a closed branch set, so its non-claimability is the same property, surfaced with the sharper message.

**Example:**
```yaml
# pane.type.yaml
abstract: true
fields:
  - title: String

# myInstance.md
type: pane   # pane is abstract; claim a concrete subtype
```

### `multi-leaf-in-sealed-family` - error
^multi-leaf-in-sealed-family

**Message:**
`claim list contains multiple non-sealed leaves of sealed family '{sealed}': {leaves}`.

**Triggers:**
one `type:` claim list (file-level or inline-value) contains two or more distinct non-sealed leaves descending from the same sealed type-def.

Fires once per violated sealed family.
Innermost-only suppression on nested sums when inner and outer bucket identical leaf sets.

**Example:**
```yaml
type:
  - myParent.myLeafA
  - myParent.myLeafB    # two leaves of the same sealed family
```

**Spec:** [[type-instance type]].

### `inline-value-missing-type` - error
^inline-value-missing-type

**Message:**
varies per [[type-def shape record]] case.

Shape: `inline value at {kind} slot '{slot}' must declare 'type:' naming a concrete (claimable) descendant`, `{kind}` being `sealed-parent` or `abstract`; union / intersection slots carry their own variant.

**Triggers:**
inline value at a slot that requires an explicit `type:` claim omits it.
The slot requires one when its demand is
- a NON-CLAIMABLE single-demand ceiling, sealed or abstract.
  - defaulting to the ceiling's own identity would implicitly claim a non-claimable type.
- a union or intersection ([[type-def shape record]]), needing the branch identified.

A qualified peer demand (`foo::repo` where `foo` is sealed or abstract in `repo`) is the cross-repo case, an omitted `type:` there must name a concrete descendant.

Single code, message variant per case.

**Example:**
```yaml
# myA.type.yaml
fields:
  myInnerField: <shape>

# myB.type.yaml
fields:
  myInnerField: <shape>

# myType.type.yaml
fields:
  myField: <myA | myB>

# myInstance.yaml
myField:
  # no 'type:' to select the union branch
  myInnerField: <value>   
```

**Spec:** [[type-def shape record]].

### `inline-value-type-not-compatible` - error
^inline-value-type-not-compatible

**Message:**
`inline value 'type: {claimed}' does not satisfy slot {slot-shape}`.

Case 1 / case 3 / case 4 variants name the specific mismatch:
- closure-missing-demanded
- no-matching-union-branch
- missing-intersection-branch

**Triggers:**
inline value's declared `type:` exists in the graph but doesn't satisfy the slot's demand.

A qualified `foo::repo` demand is the cross-repo case, the inline claim's FOLDED closure must include the demanded peer type's identity, else this fires.

**Example:**
```yaml
# myType.type.yaml
fields:
  myField: <myTypeA | myTypeB>

# myInstance.yaml
myField:
  type: myUnrelatedType
```

**Spec:** [[type-def shape record]].

### `malformed-qualifier-key` - error
^malformed-qualifier-key

**Message:**
`field key '{key}' uses qualifier syntax (`field{type}`) but is malformed: {reason}`.

**Triggers:**
qualified key `field{type}` is syntactically broken.

Failure modes:
- empty field name
- empty qualifier
- unclosed or stray braces
- qualifier type violating the type-name regex

**Example:**
```yaml
{myType}: <value>               # empty field
myField{myType: <value>         # unclosed brace
```

**Spec:** [[type-def fields collision - auto-unify and qualified field]].

### `qualifier-not-in-closure` - error
^qualifier-not-in-closure

**Message:**
`qualifier '{T}' is not in the instance's closure — a valid qualifier must be a claimed type or one of its ancestors`.

**Triggers:**
qualified key `field{type}` names a `type` that isn't in the instance's claimed types plus all transitive ancestors.

**Example:**
```yaml
# myType.type.yaml
fields:
  myField: <shape>

# myInstance.yaml
type: myType
myField{myOther}: <value>   # myOther is not in myType's closure
```

**Spec:** [[type-def fields collision - auto-unify and qualified field]].

### `qualifier-does-not-declare-field` - error
^qualifier-does-not-declare-field

**Message:**
`qualifier '{T}' (and its closure) does not declare field '{F}' — no type-def in the qualifier's chain has it in `fields:``.

**Triggers:**
qualified key `field{type}` names a `type` in closure, but no type-def in `closure_of(type)` declares the field in its `fields:`.

**Example:**
```yaml
# myType.type.yaml
fields:
  myField: <shape>

# myInstance.yaml
type: myType
myAbsentField{myType}: <value>   # no type-def in myType's closure declares it
```

**Spec:** [[type-def fields collision - auto-unify and qualified field]].

### `qualifier-ambiguous` - error
^qualifier-ambiguous

**Message:**
`qualifier '{T}' reaches divergent field '{F}' at more than one origin — name a declaring origin directly ({F}{A}, {F}{B})`.

**Triggers:**
qualified key `field{type}` names a `type` whose closure declares `field` at two or more NON-token-equal origins, a divergent field reached through a non-declaring descendant. Which origin's shape the value would check against is arbitrary, so the qualifier is rejected. A qualifier naming a declaring origin directly (`field{a}` / `field{b}`) resolves unambiguously.

**Example:**
```yaml
# a.type.yaml declares  title: String ; b.type.yaml declares  title: Number
# c extends [a, b]  → title is divergent in c's closure

# myInstance.yaml
type: c
title{c}: "x"   # c reaches title at both a and b → qualifier-ambiguous
```

**Spec:** [[type-def fields collision - auto-unify and qualified field]].

### `mixed-bare-and-qualified-field` - error
^mixed-bare-and-qualified-field

**Message:**
`field '{name}' has both bare and qualified entries on this instance — must be either all bare (auto-unify) or all qualified (explicit per-origin distinction)`.

**Triggers:**
same field name on one instance has both bare and qualified entries.

Mixing the two is a contradictory claim about whether the field auto-unified.

**Example:**
```yaml
type:
  - myA
  - myB
myField: <value>         # bare
myField{myA}: <value>    # and qualified: pick one form
```

**Spec:** [[type-def fields collision - auto-unify and qualified field]].

### `reference-target-type-mismatch` - error
^reference-target-type-mismatch

**Message:**
`reference '{wikilink}' resolves to '{target-path}', whose 'type:' closure does not include the slot's required type '{required}'`.

**Triggers:**
a typed-reference slot's wikilink resolved to a target whose claim closure doesn't satisfy the slot's constraint.

The checked claim depends on the target kind:
- a plain `[[file]]`, the file's `type:` claim.
- with a `^block-id`, the addressed entity's own claim, see [[type block-id]]:
  - a typed block's fence claim.
  - an inline record's effective claim, explicit or slot-pinned.
- the local forms `[[^id]]` / `[[#head]]` resolve against the host file, same rules.

A `[[name::repo]]` target is checked across the repo boundary.
- the target's closure must include the required type, and that type must be the SAME type as the slot's repo's copy.
- sameness is the full closure compared member by member, each `(name, canonical-hash)`, not the required type's hash alone.
- two repos can write the same `myType (type: foo)` while their local `foo` diverges, so `myType` hashes equal yet validates instances differently.
- a name match, or even a top-level hash match, is not enough.
- the existence side (`reference-repo-unknown` / `-unavailable` / cross-repo `reference-target-missing`) is the engine's, this code is the type side.

A qualified DEMANDED type, a slot shaped `foo::repo*`, checks the peer type `foo` as `repo` defines it.
- membership is `TypeId` equality, the demanded `(foo, repo.closure_id(foo))` must be in the target's FOLDED closure.
- the target's folded closure resolves its own claims over its repo's resolution graph, so a target claiming `foo::repo` and a target in `repo` claiming bare `foo` both satisfy it.
- the message names the authored `foo::repo`, not the bare base.
- an unresolvable demand repo is the `type-repo-*` gate's, this code is the value-satisfaction side.
- a `^block-id` target folds its own BLOCK claim, an inline record's or a body typed-fence's, checked the same way.

Produced by the validator.
Resolution-side codes live in au-references.

**Example:**
```yaml
# myType.yaml.md
fields:
  - myField?: myTarget*

# myOtherInstance.yaml
type: myType # does not include "myTarget" as ancestor

# myInstance.yaml
type: myType
myField: "[[myFile]]"   # myFile's type closure does not include myTarget
```

**Spec:** [[type reference]].

### `def-ref-target-not-a-type-def` - error
^def-ref-target-not-a-type-def

**Message:**
`reference '{wikilink}' in a 'type<...>*' slot resolves to '{target-path}', which is not a type-def`.

**Triggers:**
a [[type-def shape def-ref]] slot (`type<T>*` or `type*`) resolved to a target that is not a type-def.
- the target exists, so it is not [[spec - diagnostic codes^reference-target-missing]].
- but it is a plain instance or asset, not a `.type.yaml` file.

The def-ref axis demands a def.
- `T*` would check this same target's instance identity, a different axis.
- `type<T>*` demands the target BE a def, before any closure check.

**Example:**
```yaml
# myMode.type.yaml
fields:
  - proposeTool: type<mcp.tool>*

# myMode.md
type: myMode
proposeTool: "[[some-note]]"   # resolves to a plain note, not a type-def
```

**Spec:** [[type-def shape def-ref]].

### `def-ref-closure-mismatch` - error
^def-ref-closure-mismatch

**Message:**
`reference '{wikilink}' resolves to type-def '{target-name}', whose parent closure does not include the required type '{required}'`.

**Triggers:**
a constrained [[type-def shape def-ref]] slot (`type<T>*`) resolved to a type-def whose [[type-def extends]] parent closure misses `T`.
- the def axis sibling of [[spec - diagnostic codes^reference-target-type-mismatch]].
- that code checks the target instance's identity closure, this one checks the target def's parent closure.
- a compound bound (`type<a | b>*`) is satisfied any-of for a union, all-of for an intersection.
- a `::repo` ceiling (`type<baz::repo>*`) checks the ceiling's peer identity against the target def's FOLDED parent closure, the def-axis qualified demand.
- the unconstrained `type*` never fires this, it imposes no closure.

**Example:**
```yaml
# myMode.type.yaml
fields:
  - proposeTool: type<mcp.tool>*

# someDef.type.yaml — not under mcp.tool
fields:
  - x: String

# myMode.md
type: myMode
proposeTool: "[[someDef]]"   # someDef's parent closure does not include mcp.tool
```

**Spec:** [[type-def shape def-ref]].

---

## 7. Reference resolution (au-references)

Fired by the wikilink resolver during instance validation and the meta-body pass.
Produces well-known codes the validator surfaces as field-shape errors when they fire in a reference-typed slot.

### `reference-target-missing` - warning
^reference-target-missing

**Message:**
`wikilink target '{target}' did not resolve to any repo file`.

Cross-repo variant, for a `[[target::repo]]` link whose `repo` is present but lacks the target:
- `reference '{target}::{repo}' does not exist in repo '{repo}'`.

**Triggers:**
wikilink's target doesn't match any knowledge base basename, stem, or repo-relative path.
For a `::repo` link, the named repo is present but the target is absent from it.

Severity is `warning`, not `error`, because a dangling typed reference is open-world growth.
The target may be authored next, so a dangling link doubles as a forge signal, the note the graph wants next.
This mirrors the prose sibling `navigational-target-not-found` (already a warning) and the open-world stance, growth is never rejected.
A consumer wanting strictness gates on this code.
Distinct from `reference-target-type-mismatch`, where the target EXISTS but is the wrong type, a real mistake that stays an error.
See the decision that dangling typed reference is advisory warning not an error.

**Example:**
```yaml
# myType.yaml
fields:
  myField: file*

# myInstance.yaml
type: myType
myField: "[[myMissingFile]]"   # resolves to no repo file
```

**Spec:** [[type reference]].

### `reference-target-ambiguous` - error
^reference-target-ambiguous

**Message:**
`wikilink target '{target}' resolves ambiguously to multiple files: {paths}`.

Cross-repo variant, for a `[[target::repo]]` link ambiguous within a present `repo`:
- `reference '{target}::{repo}' is ambiguous in repo '{repo}'`.

**Triggers:**
wikilink target matches two or more repo files.
An extensionless target matches by stem, so same-stem files (`note.md` + `note.yaml`) collide too.
For a `::repo` link, the named repo is present but the target matches two or more files there.

Resolution requires explicit extension, explicit path, or rename.

**Example:**
```yaml
# myType.yaml
fields:
  myField: file*

# myInstance.yaml
myField: "[[myNote]]"   # two files named myNote resolve ambiguously
```

**Spec:** [[type reference]].

### `reference-path-escapes-repo` - warning
^reference-path-escapes-repo

**Message:**
- slot: `{field} references '{target}', a path that leaves this repo; a wikilink is repo-scoped, so it can never resolve`.
- prose: `` wikilink `[[{raw}]]` names a path that leaves this repo; a wikilink is repo-scoped, so it can never resolve ``.
- cross-repo: `reference '{target}::{repo}' names a path that leaves repo '{repo}'; a wikilink is repo-scoped, so it can never resolve`.

**Triggers:**
a wikilink target names a path that leaves its own repo, checked LEXICALLY.
- absolute, `[[/etc/passwd]]`.
- climbing above the root, `[[../peer-repo/notes/x.md]]`.

A wikilink is repo-scoped by construction, and `::repo` is how an edge crosses a boundary, see [[type repo qualifier]].
So the address contradicts its own scope, and no file authored later makes it resolve.

Distinct from [[spec - diagnostic codes^reference-target-missing]], and the distinction is the point.
- a missing target is open-world growth, it may be authored next.
- an escaping target is IMPOSSIBLE, so reporting both as missing puts a nonsense address in the same bucket as a renamed or not-yet-written one.
- that bucket is where a malformed pin becomes indistinguishable from a legitimately drifted one.

Fires on all THREE resolution surfaces with one code, a typed slot, a prose link, and a `::repo`-qualified target.
- the qualifier says which repo to resolve in, so a target climbing out of THAT repo contradicts its own scope the same way.
- a code that appeared and disappeared with the spelling would make the distinction "usually" rather than "always", and a consumer matches on the code.
- the severity is `warning` on all three, so the never-error stance on a navigational site is untouched.
- the engine stays advisory here, the value is DISTINGUISHABILITY plus a fix, not blocking.

Not a traversal guard.
Resolution is a lookup over indexed repo-relative paths and never joins a target onto a root, so nothing escapes the filesystem today.
Only a path-mode target can fire it, a bare name has no components to climb with, and an interior `..` staying inside the repo (`a/../b.md`) is an ordinary path.

**Fix:**
name the target in its own repo with the `::repo` qualifier, `[[name::repo]]`, rather than reaching across with a relative path.

**Example:**
```yaml
# myType.type.yaml
fields:
  - mySibling: file*

# myInstance.md
type: myType
mySibling: "[[../peer-repo/notes/x.md]]"   # leaves this repo; use [[x::peer-repo]]
```

**Spec:** [[type reference]], [[type repo qualifier]].

### `reference-repo-unknown` - error
^reference-repo-unknown

**Message:**
`reference repo '{repo}' is not a declared peer or workspace member`.

**Triggers:**
a `[[name::repo]]` link names a `{repo}` that is neither a declared peer of the source's repo nor a workspace member.

The qualifier resolves to no known repo, the likely cause is a typo.
Distinct from `reference-repo-unavailable`, where the repo is known but not present.

### `reference-repo-unavailable` - warning
^reference-repo-unavailable

**Message:**
`reference repo '{repo}' is declared but not present in this workspace`.

**Triggers:**
a `[[name::repo]]` link names a `{repo}` that is a declared peer or a workspace member, but is not present in the loaded workspace on this machine.

A legitimate state, the repo is known but unmounted, so the reference cannot resolve here.
Warning, not error, mirroring `peer-unmounted`.
The reference resolves once the repo is mounted, no source change needed.

### `type-repo-empty` - error
^type-repo-empty

**Message:**
`type '{base}::' has an empty repo qualifier; bare '{base}' is the own-repo form`.

**Triggers:**
a `::repo`-qualified type name has an empty repo, `foo::`, at a claim or parent position.

The type-name sibling of `wikilink-empty-repo`.
Bare `foo` is the canonical own-repo form, so an empty `::` adds nothing and is rejected.
At the field-shape position au-grammar rejects `foo::` as `shape-syntax-error` instead, so this code is a claim / parent concern, reachable only via the quoted form `type: "foo::"`.

### `type-repo-unknown` - error
^type-repo-unknown

**Message:**
`type '{base}::{repo}' names repo '{repo}', which is not a declared dependency or a known workspace member`.

**Triggers:**
a `::repo`-qualified type name, an instance claim, a type-def parent, a field shape, a meta sub-region `type:`, a body `use:`, or a nested inline `type:` claim inside a body typed-block, names a `{repo}` that is neither a declared dependency of the source's repo nor a known workspace member.

The qualifier resolves to no known repo, the likely cause is a typo.
The type-side sibling of `reference-repo-unknown`.
Distinct from `type-repo-unavailable` (the repo is a declared dep but not present) and `type-repo-not-a-dependency` (the repo is a mounted member but not a declared dep).

**Spec:** [[repo yaml]].

### `type-repo-unavailable` - warning
^type-repo-unavailable

**Message:**
`type '{base}::{repo}' names repo '{repo}', which is declared but not present in this workspace`.

**Triggers:**
a `::repo`-qualified type name names a `{repo}` that IS a declared dependency of the source's repo, but is not present in the loaded workspace on this machine.

A legitimate state, the dependency is known but unmounted, so its type cannot be folded here.
Warning, not error, mirroring `reference-repo-unavailable` and `peer-unmounted`.
Resolving / vendoring the closure is the fix that survives an absent peer; otherwise the type resolves once the dep is mounted, no source change needed.
The type-side sibling of `reference-repo-unavailable`.

**Spec:** [[repo yaml]].

### `type-repo-not-a-dependency` - error
^type-repo-not-a-dependency

**Message:**
`type '{base}::{repo}' names repo '{repo}', a workspace member but not a declared dependency of this repo; add '{repo}' to this repo's deps to cross its types`.

**Triggers:**
a `::repo`-qualified type name names a `{repo}` that is a mounted workspace member (an `edit` or `discover` member) but is NOT a declared dependency of the source's repo. The peer gate: a type position crosses a peer's VOCABULARY, which requires the peer declared as a `dep` (deps fold into the closure-hash), independent of whether it is mounted for discovery / editing. A `discover` member is mounted so its parts compose, not as a type-dependency; crossing its types needs it promoted to a `dep`. An `error`.

A plain VALUE link into a member (`[[node::repo]]`) stays permissive, only a TYPE crossing gates. The self-qualifier (`note::app` inside `app`) is not gated (it resolves to the own type, `type-repo-self`). Distinct from `type-repo-unknown` (the repo is not a member at all) and `type-repo-unavailable` (a declared dep not present). Fix: add `{repo}` to this repo's `deps`.

**Spec:** [[repo yaml]].

### `peer-type-not-found` - error
^peer-type-not-found

**Message:**
`repo '{repo}' has no type-def '{base}'`.

**Triggers:**
a `::repo`-qualified type name names a present `{repo}` that has no type-def `{base}`.

The repo resolved, but the name is wrong, the common typo case `mcp.tool::au-mcp-sdk` where the peer exports `mcp.Tool`.
The type-side sibling of `slot-references-absent-type`.
Distinct from `type-repo-unavailable` (the peer is absent) and `type-repo-unknown` (the peer is undeclared); here the peer is present but the name does not resolve in its graph.

### `type-repo-self` - hint

^type-repo-self

**Message:**
`type '{base}::{repo}' qualifies the own repo; bare '{base}' is the own form`.

**Triggers:**
a `::repo`-qualified type name whose `{repo}` is the source file's OWN repo, `note::app` written inside `app`.

It resolves to the own type and validates like bare `{base}`, so it is not an error, just redundant.
The only `type-repo-*` code that names yourself; every other names a peer.
Advisory, never blocks.

### `pinned-commit-unavailable` - warning
^pinned-commit-unavailable

**Message:**
`pinned commit '{commit}' is not present in the local object store`.

**Triggers:**
a `[[file::@commit]]` pin names a commit the local object store does not hold.

A legitimate state, the commit is known but unavailable here, so the pin cannot resolve.
Warning, not error, mirroring `reference-repo-unavailable` and `peer-unmounted`.
The pin resolves once the commit is fetched, no source change needed.

Spec-ahead. The resolver returns this as an internal outcome; the `Diagnostic` mapping lands when the on-demand read surface is wired.

**Spec:** [[type reference]].

### `pinned-path-absent` - error
^pinned-path-absent

**Message:**
`pinned reference '{raw}': target '{target}' is not present in commit '{commit}'`.

**Triggers:**
a pin resolves its commit, but the target, a path or a bare name, is absent from that commit's tree.

The pin names bytes that never existed at that commit, a bogus reference.
- distinct from a deletion-stable pin, which resolves because the target did exist there.
- distinct from `pinned-commit-unavailable`, where the commit itself is missing locally.
- cannot arise for an engine-written pin, construction validated it; surfaces when an out-of-band pin's record is derived.

Spec-ahead. The resolver returns this as an internal outcome; the `Diagnostic` mapping lands when the on-demand read surface is wired.

**Spec:** [[type reference]].

### `value-not-pinned` - error
^value-not-pinned

**Message:**
`{field} value is not commit-pinned — declared shape {shape} requires a '[[…::@commit]]' pin`.

**Triggers:**
a value in a `*@` enforced-pinned slot ([[type-def shape suffixes]]) does not carry a `@commit` pin.
- an unpinned wikilink (`[[note]]` in a `file*@` slot).
- a non-reference value in a reference-only `*@` slot.

The shape-level requirement, checked before resolution.
- its mirror is `unexpected-commit-pin`, a pinned value in a slot that admits no pin.

**Spec:** [[type-def shape suffixes]].

### `unexpected-commit-pin` - error
^unexpected-commit-pin

**Message:**
`{field} value is commit-pinned — declared shape {shape} admits no pin; use a '*@' slot or a '< T* | T*@ >' union`.

**Triggers:**
a pinned value (`[[note::@sha]]`) in a slot whose shape admits no pin.
- a plain `T*` / `T&` slot, which forbids a pin.
- fires only when NO branch of the slot admits a pin, a `< T* | T*@ >` union accepts the pin on its `*@` branch.

The mirror of `value-not-pinned`.
- `value-not-pinned`, a `*@` slot got an unpinned value.
- `unexpected-commit-pin`, a non-pin slot got a pinned value.

**Spec:** [[type-def shape suffixes]].

### `wikilink-empty-target` - error
^wikilink-empty-target

**Message:**
`{prefix} value '{raw}': wikilink has no target before its field delimiter`.

**Triggers:**
wikilink has the `[[ … ]]` frame but the target portion is empty,
and no locating fragment (`#head`, `^block-id`) is present.

E.g. `[[:field]]`.

A locating fragment grants the empty name.
`[[^id]]` and `[[#head]]` are the legal local forms, current file, see [[type reference]].

### `wikilink-empty-anchor` - error
^wikilink-empty-anchor

**Message:**
`wikilink '{raw}' ends with '#' but no anchor value`.

**Triggers:**
wikilink ends with `#` and no anchor follows.

E.g. `[[note#]]`.

Likely an in-progress edit.

### `wikilink-empty-block-id` - error
^wikilink-empty-block-id

**Message:**
`wikilink '{raw}' ends with '^' but no block-id value`.

**Triggers:**
wikilink ends with `^` and no block-id follows.

E.g. `[[note^]]`, or a block-referent `[[note^^]]` with no id after the double caret.

Likely an in-progress edit.

### `wikilink-reversed-delimiters` - error
^wikilink-reversed-delimiters

**Message:**
`wikilink '{raw}' has '^' before '#' — canonical order is target[#anchor][^block-id]`.

**Triggers:**
wikilink has block-id-delimiter `^` before anchor-delimiter `#`.

Canonical order is fixed because either suffix's value would otherwise be ambiguous.

**Spec:** [[type reference]].

---

## 8. Meta-body validation (au-core::validate)

Meta sub-region bodies validate against their named meta-type-def using the same per-instance machinery.

They emit the same codes as the per-instance validation stage.
E.g.:
- `required-field-absent`
- `field-shape-mismatch`
- `unknown-type-claim`
- `sealed-parent-claimed`
- `multi-leaf-in-sealed-family`

Meta-body validation is otherwise a parallel invocation of the same checks.
The meta-specific codes are the nominal-legality gate and the required-subtype-meta codes below.

Parse-time meta issues fire in the type-def parse stage.
E.g.:
- `meta-not-a-list`
- `meta-block-bad-shape`
- `meta-mixin-not-supported`
- `duplicate-meta-block`

### `non-meta-type-in-meta-position` - error
^non-meta-type-in-meta-position

**Message:**
`` type-def '{name}' is not a meta type; a meta sub-region's type must mix in '{marker}::{repo}' ``.

`{marker}::{repo}` is the engine meta marker, `au.engine.meta::au-engine`.

**Triggers:**
a `meta:` sub-region names a CLAIMABLE type whose RESOLVED closure does not include the engine meta marker `au.engine.meta`.
Meta-ness is nominal: a meta type declares it by mixing in the marker, `type: [X, au.engine.meta::au-engine]`, or via a dedicated wrapper subtype.

Checked over the resolution graph, the parity of the sealed cross-repo check, comparing by `(name, closure-hash)` identity.
- only for a CLAIMABLE meta type; a sealed or abstract one already fired the sharper `sealed-parent-claimed` / `abstract-type-claimed`, so no double-signal.
- an unresolvable named type is the `type-repo-*` / `unknown-type-claim` gate's, not this code's.
- the marker itself named directly fires `abstract-type-claimed`, it is abstract.

**Example:**
```yaml
# plain-meta.type.yaml — a plain record, no marker
fields:
  - x?: String

# host.type.yaml
fields: []
meta:
  - type: plain-meta   # not a meta type: does not mix in au.engine.meta
```

### `required-meta-not-a-meta-type` - error
^required-meta-not-a-meta-type

**Message:**
`type-def '{td}' requires meta '{name}', which is not a meta type; it must mix in '{marker}::{repo}'`.

**Triggers:**
a present, resolvable `required:` target whose RESOLVED closure does not include the engine meta marker `au.engine.meta`. The base-side sibling of `non-meta-type-in-meta-position`, checked over the resolution graph. Skips the cases other gates own, a bare absent target (`required-meta-absent-type`) and an unresolvable qualified target (`type-repo-*`).

**Example:**
```yaml
# plain.type.yaml — a plain record, no marker
fields:
  - x?: String

# base.type.yaml
meta:
  - required: plain   # plain is not a meta type
```

### `subtype-missing-required-meta` - warning
^subtype-missing-required-meta

**Message:**
`type-def '{td}' is concrete but does not declare the required meta '{name}'; a base in its closure obligates it`.

**Triggers:**
a NON-ABSTRACT type-def whose closure includes a base declaring a `required:` obligation, that does not itself declare a satisfying meta block.
- satisfaction is LITERAL, only the type's OWN `meta:` blocks count, an ancestor's surfaced block does not.
- satisfaction is BY CLOSURE, a block whose type's closure includes the required meta satisfies it (a subtype of the required meta counts).
- `meta: []` exempts nothing, an emptied meta declares no block.
- the closure is reflexive, so a CONCRETE declaring base is on its own hook; abstract / sealed types are exempt.
- advisory `warning`, per the open-world stance, growth is never blocked.

Computed over the resolution graph, so a cross-repo base's obligation and a cross-repo required meta type both resolve. One diagnostic per unmet obligation, anchored at the offending type-def, `related` at the obligating base. The same computation is exposed as the `unmet_required_meta` read.

**Example:**
```yaml
# base.type.yaml — obligates every concrete subtype
abstract: true
meta:
  - required: pm

# tool.type.yaml — concrete, declares no pm block
extends: base
fields: []
```

---

## 9. Body typing (au-core::body, au-core::body_validate, au-references)

The body-typing extension layers `body:` templates, `use:` splicing,
wikilink `:field` fragments, inline `` `[:field]` `` codes, marked
fences, and `fills:` contracts onto type-defs and instances.
Codes are grouped here by sub-stage (parse → graph load → per-instance
validation) rather than scattered across the earlier stage sections.

### 9.1 Type-def body parse (au-core::body)

### `body-not-a-list` - error
^body-not-a-list

**Message:**
`'body:' must be a YAML list`.

**Triggers:**
type-def `body:` value is not a YAML sequence.

**Spec:** [[type-def body]].

### `body-item-not-a-mapping` - error
^body-item-not-a-mapping

**Message:**
`each 'body:' item must be a YAML mapping with a discriminator key ('use:', 'section:', 'section?:', 'fills:', or 'fills!:')`.

**Triggers:**
a top-level `body:` list element is not a mapping.

**Spec:** [[type-def body]].

### `body-item-missing-discriminator` - error
^body-item-missing-discriminator

**Message:**
`'body:' item is missing a discriminator ('use:', 'section:', 'section?:', 'fills:', or 'fills!:')`.

**Triggers:**
mapping has none of the recognized discriminator keys.

**Spec:** [[type-def body]].

### `fills-value-bad-shape` - error
^fills-value-bad-shape

**Message:**
`'fills:' value must be a field name or a list of field names`.

**Triggers:**
the value under `fills:` / `fills!:` is neither a string nor a sequence of strings.

**Spec:** [[type-def body fills]].

### `fills-double-form-declaration` - error
^fills-double-form-declaration

**Message:**
`scope carries both 'fills:' and 'fills!:' — pick one`.

**Triggers:**
one scope (section or body-level) declares both forms.

**Example:**
```yaml
body:
  - section: mySection
    fills: myField
    fills!: myField     # both forms on one scope
```

**Spec:** [[type-def body fills]].

### `body-use-nested` - error
^body-use-nested

**Message:**
`'use:' is valid only at the top of the outermost 'body:'`.

**Triggers:**
`use:` appears inside a section's nested `body:`.

The top-level-only constraint is structural; nested splicing belongs in a separate operator (deferred;).

**Example:**
```yaml
body:
  - section: mySection
    body:
      - use: myParent    # use: only valid at the outermost body
```

**Spec:** [[type-def body use]]. Not enumerated in the source spec; introduced by implementation.

### 9.2 Type-graph body-typing load checks (au-core::load_checks)

### `body-use-out-of-closure` - error
^body-use-out-of-closure

**Message:**
`'use: {target}' references a type-def not in '{host}'s closure`.

**Triggers:**
splice target is not in the host type-def's transitive ancestor set.

Bodies cannot travel without their declaring types — referenced bodies must come from a claimed lineage.

Also fires across a repo boundary.
- a `use: parent::repo` demands the host EXTEND the peer, so the peer type must be in the host's FOLDED closure.
- checked in the engine's cross-repo gate over the host's resolution graph, the parity of the own-graph closure check.
- the message renders the authored `parent::repo`.

**Example:**
```yaml
# myType.type.yaml
body:
  - use: myOtherType  # myOther is not in myType's closure
```

**Spec:** [[type-def body use]].

### `body-use-cycle` - error
^body-use-cycle

**Message:**
`type-def '{name}' participates in a 'use:' splice cycle`.

**Triggers:**
the `use:` splice graph contains a cycle reachable from this type.

Self-cycles (`use: self`) and multi-step cycles both fire; every type on the cycle gets its own diagnostic.

**Example:**
```yaml
# type/myA.type.yaml
body:
  - use: myB

# type/myB.type.yaml
body:
  - use: myA         # splice cycle
```

**Spec:** [[type-def body use]].

### `body-use-target-has-no-body` - warning
^body-use-target-has-no-body

**Message:**
`'use: {target}' splices nothing — '{target}' declares no 'body:' template`.

**Triggers:**
`use: T` resolves to a type-def `T` in closure that declares no `body:` (or declares `body: []`).
The splice contributes nothing; the line is dead syntax.

Severity is warning, not error.
The instance still validates against its claims.
The `use:` is surfaced because it almost always indicates author error:
- typo on the target name, or
- a dangling `use:` left after the target's body was removed.

Also fires across a repo boundary: an in-closure `use: parent::repo` whose peer type declares no body, checked in the engine's cross-repo gate.

Does not fire when the target is out of closure (`body-use-out-of-closure` covers that), or when the splice forms a cycle (`body-use-cycle`).

**Example:**
```yaml
# myOther.type.yaml
fields:
  myField: <shape>

# myType.type.yaml
body:
  - use: myOther  # myOther does not define a body
```

**Spec:** [[type-def body use]].

### `fills-unknown-field` - error
^fills-unknown-field

**Message:**
`'fills:' references field '{name}' which is absent from '{type}'s effective closure`.

**Triggers:**
a `fills:` field name doesn't resolve under the host type-def's closure (own fields + transitive ancestors).

**Example:**
```yaml
fields:
  - myPresentField: <shape>
body:
  - section: mySection
    fills: myMissingField   # absent from the closure
```

**Spec:** [[type-def body fills]].

### `fills-contract-conflict-nested-exclusivity` - error
^fills-contract-conflict-nested-exclusivity

**Message:**
`nested 'fills:' requires '{field}', but an ancestor 'fills!:' forbids any field other than '{exclusive}'`.

**Triggers:**
a nested scope's `fills:` (or `fills!:`) requires a field not in an ancestor `fills!:`'s allowed set.

The conflict is structural: the type-def can never produce an instance that satisfies both contracts.

**Example:**
```yaml
body:
  - section: myOuter
    fills!: myFieldA        # exclusive: only myFieldA
    body:
      - section: myInner
        fills: myFieldB     # requires myFieldB: conflict
```

**Spec:** [[type-def body fills]].

### 9.3 Wikilink `:field` fragment parse (au-references)

### `wikilink-empty-field` - error
^wikilink-empty-field

**Message:**
`wikilink '{raw}' ends with ':' but no field value`.

**Triggers:**
wikilink ends with `:` and no field-name follows.

E.g. `[[note:]]`.

Parallel to `wikilink-empty-anchor` / `wikilink-empty-block-id`.

**Spec:** [[type reference]].

### `wikilink-empty-repo` - error
^wikilink-empty-repo

**Message:**
`wikilink '{raw}' ends with '::' but no repo value`.

**Triggers:**
the `::repo` qualifier is present with no repo name following.

E.g. `[[note::]]`.

Parallel to `wikilink-empty-field` / `wikilink-empty-anchor`.

**Spec:** the decision that repo qualifier is a postfix double-colon wikilink fragment.

### `wikilink-empty-commit` - error
^wikilink-empty-commit

**Message:**
`wikilink '{raw}' has '@' but no commit value`.

**Triggers:**
the `@commit` pin qualifier is present with no commit-ish following.

E.g. `[[note::@]]`.

Parallel to `wikilink-empty-repo` / `wikilink-empty-anchor`.

**Spec:** [[type reference]].

### `pinned-commit-not-oid` - error
^pinned-commit-not-oid

**Message:**
`wikilink '{raw}' pins a non-oid commit; a pin's commit must be an immutable oid, not a branch, tag, or relative rev`.

**Triggers:**
a `@commit` pin whose value is not a hex oid.
- a mutable rev, a branch or a tag (`[[note::@main]]`, `[[note::@v1.0]]`).
- a relative or symbolic rev (`[[note::@HEAD]]`, `[[note::@HEAD~2]]`).

A pin is a coordinate into an immutable past.
- a branch or tag can be repointed, a relative rev moves with HEAD, both defeat that.
- an oid, full or an abbreviated prefix, is the only form that never moves.

Checked at PARSE, no length floor.
- an over-short prefix is accepted here and fails at resolution as ambiguous.
- distinct from `wikilink-empty-commit` (an `@` with no value at all).

**Spec:** [[type reference]].

### `wikilink-invalid-repo-name` - error
^wikilink-invalid-repo-name

**Message:**
`wikilink '{raw}' has an invalid '::repo' name (must match the repo-name regex)`.

**Triggers:**
the `::repo` value violates the identifier regex ([[type-def legal names]]).

E.g. `[[note::b/c]]`, `[[note::1bad]]`, `[[note::ba d]]`.

Repo names share the type/field-name grammar. Rejecting a malformed name at parse gives a clear authoring error, instead of degrading to a misleading `reference-repo-unknown` at lookup. Parallel to `wikilink-invalid-field-name`; distinct from `wikilink-empty-repo` and the order codes.

**Spec:** [[type reference]].

### `wikilink-fragment-order` - error
^wikilink-fragment-order

**Message:**
`wikilink '{raw}' violates the strict 'name / #head / ^block-id / :field' order`.

Variant for the repo qualifier:
- `wikilink '{raw}' has its '::repo' qualifier out of order; canonical order is 'name ::repo@commit #anchor ^block-id :field', at most one '::repo'`.

Variant for the commit qualifier:
- `wikilink '{raw}' has its '@commit' qualifier out of order or unanchored; '@commit' binds to '::repo', written '::repo@commit'`.

**Triggers:**
- `:field` fragment placed before `#anchor` or `^block-id` (e.g. `[[note:f#a]]`).
- the `::repo` qualifier placed after a `#`/`^`/`:` fragment, or more than one `::repo` (e.g. `[[note#a::base]]`, `[[note::a::b]]`).
- the `@commit` qualifier placed after a `#`/`^`/`:` fragment, or more than one `@commit`.

Covers ONLY positional ordering — name-validity errors fire `wikilink-invalid-field-name` separately so consumers can route them distinctly.
A bare `@` with no preceding `::` is a literal filename character, not an out-of-order pin, see [[type reference]].

**Spec:** [[type reference]], the decision that repo qualifier is a postfix double-colon wikilink fragment.

### `wikilink-invalid-field-name` - error
^wikilink-invalid-field-name

**Message:**
`wikilink '{raw}' has an invalid ':field' name (must match the field-name regex)`.

**Triggers:**
the wikilink's `:field` fragment is positioned correctly but the value doesn't match the field-name grammar (e.g. `[[note:1bad]]`, `[[note:has spaces]]`).

Split off from `wikilink-fragment-order` so a downstream consumer (LSP completion, lint UI) can distinguish "fix the position" from "rename the field" without parsing the message text.

**Spec:** [[type reference]].

### 9.4 Per-instance body validation (au-core::body_validate)

### `body-required-but-yaml-only-instance` - error
^body-required-but-yaml-only-instance

**Message:**
`instance's type declares a 'body:' template, but the instance is yaml-only (must be markdown)`.

**Triggers:**
the instance's claimed type-chain declares a non-empty `body:`, but the instance file is `*.yaml` / `*.yml` (no markdown body possible).

**Example:**
```yaml
# myType.type.yaml
body:
  - section: My Section

# file: myInstance.yaml   # yaml-only, so no markdown body
type: myType
```

**Spec:** [[type-def body]].

### `body-section-missing` - error
^body-section-missing

**Message:**
`required body section '{marks} {name}' is missing from the instance`.

`{marks}` matches nesting depth: `#` for top-level, `##` for sub-section under a top-level, etc.

**Triggers:**
a declared (non-optional) section isn't present anywhere in the body.
Applies at every nesting depth — sub-sections declared via a parent section's `body:` are checked too.
Optional sections (`section?:`) may be absent.

Out-of-position presence fires `body-section-out-of-order` instead — `body-section-missing` covers only true absence.

**Example:**
```yaml
# myType.type.yaml
body:
  - section: My Required Section

# myInstance.md
---
type: myType     # body declares section: My Required Section
# required "# My Required Section" is absent from body
---
```

**Span:**
primary span is the instance's whole-file source span (the section has no body location to anchor at — it's missing).
`related[]` points at the `section:` declaration in the type-def (file + byte-range of the section name), so IDEs can offer "jump to template".

**Spec:** [[type-def body section]].

### `body-section-out-of-order` - error
^body-section-out-of-order

**Message:**
`body section '# {name}' appears before '# {prev}', but '{prev}' is declared earlier in the template`.

**Triggers:**
a declared section IS present in the body but precedes another declared section that came before it in the template.
Order check uses each declared section's earliest unconsumed body occurrence; same-name siblings consume distinct headings in declaration order.

**Example:**
```markdown
---
type: myType     # body declares myFirst then mySecond
---
# mySecond
# myFirst        # appears before mySecond, against template order
```

**Span:**
primary span anchors at the offending section's heading in the body.
`related[]` carries the heading span of the section it appeared before (so authors see both endpoints of the swap).

**Spec:** [[type-def body section]].

### `body-unterminated-fence` - warning
^body-unterminated-fence

**Message:**
`fenced code block opens (`{info}`) but has no matching closing fence later in the body`.

`{info}` echoes the fence-info string from the open line (e.g. `yaml`, `yaml [:field]`); empty info renders as `<unspecified>`.

**Triggers:**
a fence opens with a run of three or more backticks, and no closing fence of at least that run length appears later in the source.
fences are variable-length per CommonMark, so a longer fence legitimately wraps a shorter one.
a quad-backtick fence around a triple-backtick example does NOT trigger this, the inner triple-close is content, not a close.
The parser recovers by treating the fence-open as ordinary content and continuing to scan subsequent lines — headings, wikilinks, inline-code, and block-id markers all still emit.

Advisory severity per CommonMark, which permits unterminated fences but reads them ambiguously.

**Example:**
````markdown
```yaml [:myField]
type: myType
# no closing fence before end of body
````

**Span:**
primary span covers the fence-open line only.
No `related[]` — the cause is purely on that line.

**Spec:** [[type-instance body contribution]].

### `block-id-duplicate` - error
^block-id-duplicate

**Message:**
`block-id '^{id}' appears {N} times in this file; references resolve to the first only — disambiguate`.

**Triggers:**
two or more occurrences in a single file carry the same block-id.
One namespace per file, across all attachment surfaces:
- trailing-fence markers (` ```yaml [:f] ` then `^id` on next line).
- bare `^id` markers.
- inline-record `^:` ids in the frontmatter.

`resolve_block_id` returns the first match and silently ignores the rest, so without this diagnostic later references would resolve to phantom-stable targets while the duplicate sits invisibly nearby.

**Example:**
```markdown
A first block. ^myId
A second block. ^myId   # same block-id twice in one file
```

**Span:**
primary span anchors at the first block-id occurrence.
`related[]` carries every subsequent occurrence in source order.

**Spec:** [[type block-id]].

### `fills-contract-unmet` - error
^fills-contract-unmet

**Message:**
`` fills contract for '{field}' not satisfied — no body contribution found in scope {scope-path}; contributions are self-tagged (`[[target:{field}]]`, `[:{field}] value`, or a ```[:{field}] fence`) — a bare `[[target]]` is navigational and does not count ``.

**Triggers:**
a scope's `fills: f` or `fills!: f` declares the field, but no body contribution to `f` appears within the scope.

Body-level `fills:` requires a contribution somewhere in the body (frontmatter alone doesn't satisfy).
Section-level `fills:` requires a contribution under that section's heading chain (including nested sub-sections).

The message names the self-tagging rule.
A bare `[[target]]` inside the scope is the common confusion, navigational, never a contribution, see [[type-instance body contribution]].

**Example:**
```markdown
<!-- section declares  fills: myField -->
# mySection
Prose with no contribution to myField.
```

**Span:**
primary span anchors at the scope's heading line in the instance.
For body-level scopes (no enclosing section), or when the scope's heading isn't present in the body, falls back to the instance's whole-file source-span.
The contract's declaration in the type-def travels via `related[]` (file + byte-range of the field claim within the `fills:` list).

**Spec:** [[type-def body fills]].

### `fills-contract-exceeded` - error
^fills-contract-exceeded

**Message:**
`fills!: forbids field '{field}' inside scope {scope-path} — only {declared} permitted`.

**Triggers:**
a scope declared `fills!:` (exclusive) contains a body contribution to a field not in the declared set.

Exclusivity propagates: a parent `fills!: f` forbids contributions to other fields anywhere within (including nested sub-sections).

**Example:**
```markdown
<!-- section declares  fills!: myFieldA -->
# mySection
[[myTarget:myFieldB]]   # contributes to a field other than myFieldA
```

**Span:**
primary span anchors at the violating body contribution.
The exclusive contract's declaration in the type-def travels via `related[]` (file + byte-range of the `fills!:` list).

**Spec:** [[type-def body fills]].

### `body-fills-without-frontmatter-key` - error
^body-fills-without-frontmatter-key

**Message:**
`body contributes to '{field}' but frontmatter is missing the '{field}:' key`.

**Triggers:**
an optional field has ≥1 body contribution but no frontmatter key (null or otherwise).

The [[type-instance body contribution]] rule: frontmatter is the index. Body-filled optional fields still appear as keys with null values; bare-key-absent is the diagnostic.

**Example:**
```markdown
---
type: myType
# optional myField has a body contribution but no key here
---
# mySection
[[myTarget:myField]]
```

**Span:**
primary span is the first body contribution to the field.
`related[]` points at the canonical declaring type-def's field-name span, so IDEs can offer "jump to declaration" from the violation.

**Spec:** [[type-instance body contribution]].

### `field-cardinality-exceeded` - error
^field-cardinality-exceeded

**Message:**
`field '{name}' has {n} distinct ValueContainers but its shape is bare (cardinality 1)`.

**Triggers:**
a bare-shape field receives distinct values from multiple surfaces (frontmatter + body, or multiple body contributions).

Equal values across surfaces collapse into one ValueContainer per [[type value container]] and don't fire this; only distinct values do.

**Example:**
```markdown
---
type: myType         # myField is bare (cardinality 1)
myField: "[[myA]]"
---
[[myB:myField]]       # a second, distinct value
```

**Spec:** [[type value container]].

### `unbound-field-binding` - error
^unbound-field-binding

**Message:**
`wikilink :field references '{name}' which is not in the instance's effective closure`.

**Triggers:**
a body wikilink `[[target:field]]` names a field absent from the host instance's closure.

**Example:**
```markdown
[[myTarget:myMissingField]]   # myMissingField is not in the closure
```

**Spec:** [[type-instance body contribution]].

### `body-slot-shape-mismatch` - error
^body-slot-shape-mismatch

**Message:**
- `wikilink target '{target}' does not satisfy slot '{shape}' for field '{field}'`, for a wikilink contribution.
- `marked fence cannot fill slot '{shape}' for field '{field}' — the slot admits only a reference, which has no inline form`, for a fence at a reference-only slot.
- `marked fence for '{field}' does not fill record slot '{shape}' — the content is not a record (needs a `type:` and fields)`, for a fence at a record slot whose content is not a mapping.

**Triggers:**
a body contribution whose value cannot fill its slot. The code is carrier-agnostic, and the two carriers fail for different reasons, so each carries its own message shape.

**A wikilink**, when it resolves to a target whose inferred type closure doesn't include any of the slot's required type-def names.

For `[[file]]` or `[[file:field]]` wikilinks the inferred type is the target file's own `type:` claim (closure walked).
For `[[file^block-id]]` or `[[file^block-id:field]]` wikilinks the inferred type is the **block's** `type:` claim — the host file's claims are irrelevant when a block-id is present.
For a cross-repo `[[file::repo:field]]` wikilink the target is resolved in the named repo and checked by `(name, canonical-hash)` identity, the same as a frontmatter cross-repo typed reference.

`file*` is the any-repo-file built-in per [[type-def shape file]]: satisfied by mere knowledge base-index resolution; no closure check.

**A marked fence**, when the slot is REFERENCE-ONLY (`T*`, `file*`, `any*`, `type<T>*`, `<A | B>*`). A fence is inline content and those slots carry no inline form, so nothing can fill one. Fires only when the slot is KNOWN: an unresolved [[type-instance type]] claim yields no effective shape, so the fence is captured without a verdict. The value layer still captures the content, so the contribution exists and the diagnostic anchors to it, rather than the fence being silently accepted as text the slot cannot hold. See [[type-instance body contribution]]. A fence at a RECORD-bearing slot whose content is not a mapping (plain prose, or invalid YAML) also fires: the slot demands a record and the content is not one, so the value layer's captured `inline_record` holds a scalar the slot never admitted.

**Example:**
```markdown
<!-- myField: myTarget* -->
[[myFile:myField]]   # myFile's closure does not include myTarget
```

**Span:**
primary span is the violating wikilink in the body.
`related[]` points at the canonical declaring type-def's slot shape span, so IDEs can offer "jump to slot declaration" from the violation.

**Spec:** [[type-instance body contribution]].

### `unknown-field-in-prose-contribution` - warning
^unknown-field-in-prose-contribution

**Message:**
`inline '[:{name}]' references a field absent from the instance's effective closure (advisory)`.

**Triggers:**
an inline `` `[:field]` `` marker names a field not in the closure.

Advisory because prose contributions are open-world per [[type open-world validation]].
Authors may be exploring a future field or simply typo'd.

**Example:**
```markdown
`[:myMissingField] <value>`   # field absent from the closure (advisory)
```

**Spec:** [[type-instance body contribution]].

### `malformed-attribution-marker` - warning
^malformed-attribution-marker

**Message:**
`inline code '{content}' starts with '[:' but does not match the '[:fieldName] value' form`.

**Triggers:**
an inline code span starts with `` `[:` `` but doesn't match the well-formed shape.

Examples that fire:
- `` `[:]` `` — empty field
- `` `[: ]` `` — whitespace inside brackets
- `` `[: field]` `` — stray whitespace before field
- `` `[:field]` `` with no value following

Severity is warning, not error.
`` `[:` `` is reserved attribution syntax in prose, so near-misses are worth surfacing.
But the author's intent is ambiguous:
- `` `[:field]` `` may be a botched attribution (forgot the value), or
- a documentation idiom referencing the field by name in prose.
Both are common.
Validation does not fail on these.

**Spec:** [[type-instance body contribution]].

### `navigational-target-not-found` - warning
^navigational-target-not-found

**Message:**
`wikilink '[[{raw}]]' resolves to no repo file`.

**Triggers:**
a navigational wikilink whose target matches no repo file.
- a bare body wikilink (no `:field` fragment).
- a wikilink embedded in a frontmatter value, see [[type reference#Navigational versus validated]].
- a `[[...]]` in a `#:` docstring, on a type-def or an instance, see [[type docstring]].

Warning, never error.
Navigational sites are open-world growth, the target may be authored next.
The slot-side validated sibling [[spec - diagnostic codes^reference-target-missing]] is also a warning, the same open-world growth on a typed edge; the two differ only by code, navigational versus validated.

Ambiguous targets fire the sibling `navigational-target-ambiguous` below.

**Spec:** [[type reference]].

### `navigational-target-ambiguous` - warning
^navigational-target-ambiguous

**Message:**
`wikilink '[[{raw}]]' resolves ambiguously to {count} repo files`.
The candidate files ride in `related`.

**Triggers:**
a navigational wikilink whose target matches two or more repo files, so it resolves to too much rather than nothing.
- a bare body wikilink (no `:field` fragment).
- a wikilink embedded in a frontmatter value, see [[type reference#Navigational versus validated]].
- a `[[...]]` in a `#:` docstring, on a type-def or an instance, see [[type docstring]].
- an extensionless target matching by stem, so same-stem files (`note.md` + `note.yaml`) collide.

Warning, never error.
Navigational sites are open-world growth, the same advisory stance as the missing sibling [[spec - diagnostic codes^navigational-target-not-found]].
The slot-side validated twin [[spec - diagnostic codes^reference-target-ambiguous]] is an `error`, the two differ by severity and code, navigational versus validated.

Resolution requires explicit extension, explicit path, or rename.

**Spec:** [[type reference]].

### `navigational-block-id-not-found` - warning
^navigational-block-id-not-found

**Message:**
- prose: `wikilink '[[{raw}]]' — block-id '{id}' not found in {target}`.
- slot: `{prefix} wikilink '[[{target}^{id}]]' — block-id '{id}' not found in {target}`.
The local form labels the target `this file`.

**Triggers:**
a navigational `^block-id` (a bare single-caret link) whose id exists on neither addressable surface of the target, see [[type block-id]].
Fires for body prose, frontmatter-embedded links, and `#:` docstrings alike.
Local forms included, growth is the same story in the current file and across files.

A bare `^id` is navigational, so a missing id is advisory, not an error.
- the block-referent `^^id` demands a value, so its missing id is `block-id-not-found` (error) instead, see the decision that bare block-id in a typed slot is navigational, double-caret marks a block-referent value.

Navigation accepts any occurrence:
- record `^:` ids.
- bare markers and fence ids, typed or not.

Silent for targets whose body the engine does not hold (plain notes, assets).
A false warning is worse than a missed one there.

**Spec:** [[type block-id]], [[type reference]].

### `anchor-not-found` - warning
^anchor-not-found

**Message:**
- prose: `wikilink '[[{raw}]]' — heading '{anchor}' not found in {target}`.
- slot: `{prefix} wikilink — heading '{anchor}' not found in {target}`.
The local form labels the target `this file`.

**Triggers:**
a wikilink's `#head` fragment matches no heading in the resolved target,
per the [[type reference]] anchor-matching contract.

Fires for prose, slot values, and `#:` docstrings alike.
Anchors are navigational everywhere, so the severity is warning everywhere.
Independent of the typed check, a slot mismatch and a dangling anchor can both fire.

Silent when the engine does not hold the target's body (plain notes, assets).
A yaml-only instance has no headings, its anchors are verifiably absent.

**Spec:** [[type reference]].

### `block-id-not-typed` - error
^block-id-not-typed

**Message:**
`{prefix} wikilink '[[{target}^^{id}]]' — block '{id}' exists but isn't typed (no '[:field]' fence)`.

**Triggers:**
a block-referent `[[file^^id]]` (double caret) resolves to a `^id` marker in the target file, but the marker isn't attached to a `yaml [:field]` fence.

Only a fence-less body marker fires this.
An inline record always has a claim, so it resolves, see [[type block-id]].

Resolution is gated to reference-admitting slots.
A wikilink-shaped string in a primitive slot is just that string, never block-id-resolved.

The block-referent sigil `^^` is what demands a typed block, see the decision that bare block-id in a typed slot is navigational, double-caret marks a block-referent value.
- fires on both surfaces, a frontmatter typed slot (`myField: "[[file^^id]]"`) and a body contribution (`[[file^^id:field]]`).
- a bare `[[file^id]]` (single caret) is navigational, the FILE is the referent and `^id` an anchor, so it never fires this.

**Example:**
```markdown
myField: "[[myFile^^myId]]"    # ^^ demands a typed block, myId is plain prose (no [:field] fence)
```

**Spec:** [[type block-id]].

### `block-id-not-found` - error
^block-id-not-found

**Message:**
`{prefix} wikilink '[[{target}^^{id}]]' — block-id '{id}' not found in {target}`.
A target with no body and no record appends `(no body, no record id)`.
The local form labels the target `this file`.

**Triggers:**
a block-referent `[[file^^id]]` or `[[^^id]]` (double caret) whose block-id isn't present on either addressable surface of the target, see [[type block-id]]:
- no inline record carries `^: id`.
- no `^id` marker on any fence or paragraph.

Resolution is gated to reference-admitting slots, like `block-id-not-typed`.

The block-referent sigil `^^` demands the block as a value, so an absent id is an error, see the decision that bare block-id in a typed slot is navigational, double-caret marks a block-referent value.
- fires on both surfaces, a frontmatter typed slot and a body contribution.
- a bare `[[file^id]]` (single caret) with an absent id is navigational instead, softening to `navigational-block-id-not-found` (warning), the FILE the referent and `^id` a dangling anchor (consistent with the decision that dangling typed reference is advisory warning not an error).

**Example:**
```markdown
myField: "[[myFile^^myMissingId]]"   # ^^ demands a value from a block absent in myFile
```

**Spec:** [[type block-id]].

### `embedded-record-validation-failure` - error
^embedded-record-validation-failure

**Message:**
`embedded record ('type: {type}') fails its type's contract — required field(s) absent: {names}`.

**Triggers:**
a marked fence (` ```[:field] `) reads as a record and carries a `type:` claim, but its body doesn't satisfy that type's required-field contract.

This code is the TOP-LEVEL required-field-presence check for the block's own claim.
A marked fence reading as a record otherwise validates like a frontmatter inline record.
- resolution-aware, a `::repo` block claim validates against the folded peer shape.
- recursive, nested inline records inside the block validate their own contracts (firing `required-field-absent` and the other inline codes), and a nested `::repo` typo fires `type-repo-unknown`.

**Example:**
````markdown
```yaml [:myField]
type: myType
# a required field of myType is omitted
```
````

**Spec:** [[type-instance body contribution]].

### `body-fence-read-as-record` - hint
^body-fence-read-as-record

**Message:**
`marked fence for '{field}' read as the record branch of its union slot, because the content parses as a mapping declaring 'type: {type}'; if it was meant as text, reword it so the content does not parse as a yaml mapping`.

**Triggers:**
a marked fence fills a compound slot carrying BOTH a record-bearing branch and a text branch (`String` or `any`), its content parsed as a mapping declaring `type:`, so it read as the record branch, AND that record then failed.

A union has no single content-form, so the inline `type:` disambiguates it, see [[type-instance body contribution]]. Text that happens to be a well-formed typed mapping therefore selects the record branch, which is the one shape a text-intending author can trip on. The trigger is narrow: the WHOLE fence must parse as yaml, so structured key-value text can reach it but ordinary prose cannot. A `type:` line followed by prose is not valid yaml, fails to parse, and stays text.

Names the cause the accompanying failure cannot. `embedded-record-validation-failure` and `inline-value-type-not-compatible` both report a bad record, which is misleading when the author wrote prose and never wanted a record at all.

Rides ALONGSIDE that failure, never replacing it.
- the failure keeps its own severity, the record really is invalid.
- so this is a `hint`, a suggestion attached to an already-surfaced error, never an independent problem.
- a fence whose record READS and VALIDATES fires nothing, the author got what the `type:` asked for.

Carries a fix naming both readings: `reword the content so it does not parse as a yaml mapping, or correct the record`.

**Example:**
````markdown
```[:summary]
type: production
replicas: 3
```
````
The slot is `<String | myRecordType>`, and the author meant the content as literal text.
It parses as a well-formed mapping carrying `type:`, so it takes the record branch and fails there.

A `type:` line followed by prose does NOT trip this: it is not valid yaml, so it never parses as a mapping.

**Spec:** [[type-instance body contribution]], [[type-def shape record]], [[type-def shape compound]].
