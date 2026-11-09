---
type: au.engine.readme::au-engine
tldr: The Ars Umbris type-system specification, standalone and implementation-free — the ~60 one-concept atoms that define the engine's type language. Read what the type system IS without cloning the Rust. The engine behaviour specs stay in au-engine.
---

# Repo Overview

## General Context
Before defining what `au-type-system` is,
here is some general context of the environment it exists in.

- `arsumbris` is a framework for agentic knowledge work.
- `au-engine` is the engine that serves a typed, queryable graph over a cross-repo substrate of markdown, YAML type-defs, `[[wiki-links]]`, code, and media.

`au-type-system` is part of this `arsumbris` framework.
It is the engine's **type-system** specification, extracted so it stands on its own.


## What this is

`au-type-system` is the **type-system specification of the au-engine**, standalone.
- `type-system/` holds ~60 one-concept atoms linked by `[[wikilinks]]`.
- the language: type-defs, instances, shapes, closures, references, sealed / abstract / meta, cross-repo identity.
- prose only, no implementation. A reader studies what the type system IS without cloning the engine source.

It states what IS, never what changed.
- a reader arriving today cannot tell what moved.
- procedural history, decisions, and design deliberation are NOT here; they live in `au-engine`.

## How to use this

This serves as a text reference to the type system au-engine implements.
- start at [[moc - type system]] under `type-system/`, the index over the atoms.
- for the whole-system view read [[type system - why this shape]] first.
- references to the engine specs or the implementation carry a `::au-engine` qualifier.

