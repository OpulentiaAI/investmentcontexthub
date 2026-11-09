---
type: au.engine.readme::au-engine
tldr: Shared types for Arsumbris knowledge. Use them in your notes or extend them for your domain.
---

# Repo Overview

> Work in progress and not thoroughly tested.
> Expect breaking changes.

## General Context

`au-base-types` is the shared vocabulary for Arsumbris knowledge repos.
Other packages build their own types and workflows on it.

## What this is

Five kinds describe the knowledge a graph holds:

| Type | Use |
| --- | --- |
| `thing` | A persistent subject, such as a person or tool |
| `idea` | Content, such as a claim or concept |
| `event` | A happening with a date |
| `source` | Captured material that other knowledge can draw on |
| `map` | An authored or computed view over a selection of the graph |

All five inherit a required `tldr` summary from the abstract `node`.
`map` extends `idea` and keeps its fields.

Two abstract traits let concrete types carry additional meaning:

- `lens` marks a perspective on a subject
- `supersede` adds an optional `superseded_by` reference to a successor

## How to use this

Depend on `au-base-types` in your repo's `.arsumbris/repo.yaml`.
Use a concrete type in a note's frontmatter, such as `type: idea::au-base-types`.
Supply its required fields and keep the note in your own repo.

**See it in use**

- `au-tree-research` builds a research corpus with `article` notes and a `map.computed-index`
- `au-weave` builds connected `concept`, `claim` and `entity` notes, organized through `map.overview` and `map.synthesis`

## How to extend this

Define your own types in your package.
Name a parent with `extends`, for example `extends: idea::au-base-types`.
Add fields for the distinctions your work needs.
Inherited fields remain part of the type and cannot be redeclared.

Include `lens` or `supersede` in a concrete type's `extends` list when it needs those traits.
Use qualified parent names, such as `lens::au-base-types`.
Instances claim the concrete type.
Each perspective kind defines its own typed subject field.

Supply your own authoring guidance and workflows.
