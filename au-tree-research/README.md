---
type: au.engine.readme::au-engine
tldr: Recursive deep research produces articles for further processing. Run four skills from a scoped premise. Extend with consumer types and writing guidance.
---

# Repo Overview

> Work in progress and not thoroughly tested.
> Expect breaking changes.

## General Context

`au-tree-research` is a research package for Arsumbris.
It builds a corpus of deeply researched articles that other projects can reuse.

## What this is

The research forms a tree:

- A premise defines the subject and scope
- Questions branch into follow-up questions as review reveals gaps
- Articles answer individual questions
- A map shows articles and open questions as a tree

The caller chooses what to research and when to stop.

See [au-tr-example on GitHub](https://github.com/arsumbris/au-tr-example) for a worked research tree.

## How to use this

Consider keeping each research field in its own Arsumbris repo or a subrepo of your working project.
This keeps the tree reusable across projects and lets other work build on its articles.

Depend on `au-tree-research`.
Load its four skills and the `refresh_research_map` tool.

### Get started

1. Invoke **research-premise** with a subject to shape the premise and seed its starting questions
2. Invoke **research** for each question you want answered in a deeply synthesized article
3. Invoke **mediate** to explore the findings, propose further questions and refresh the map

Repeat research and mediation to develop the field.
Invoke **refresh-map** whenever you want to rebuild the map separately.
You choose which questions to pursue and when to stop.

The default layout inside a research folder:

```text
map - <name>.md
premise - <name>.md
questions/
  q - <question itself>.md
articles/
  <article name>.md
```

## How to extend this

Take your research graph and use `au-weave` to create a new graph from it.

Supply your own writing guidance.
Subtype `research-premise::au-tree-research` or `article::au-tree-research` to add fields or sections.
