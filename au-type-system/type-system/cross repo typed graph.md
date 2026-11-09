A typed graph can span many repos.
The `::` qualifier marks an edge that crosses a repo boundary.

A bare name resolves in the source's own repo, the repo of the file the edge sits in.

- `[[some-file::some-repo]]`
  - a wikilink to "some-file" in "some-repo".
- `[[some-file]]`
  - the same, resolved in the source's own repo.
- `[[some-file::this-repo]]`, `this-repo` being the source's own
  - legal but redundant, the bare form is canonical.

# The substrate

What a repo can reach.
- a **workspace** composes a set of repos into one graph
  - see [[workspace manifest]].
- a **peer** is another repo the current one declares as a dependency
  - see [[repo yaml]].
- a single repo is the simple case, no peers, every name bare.

Only a declared, present peer is reachable.
An absent peer is advisory, it never blocks the graph.

# The crossings

Three kinds of edge cross a repo boundary, each marked `::repo`.
- `[[note::repo]]`
  - a **cross-repo wikilink**
  - points at a node in a peer, see [[type reference]].
- `type: foo::repo` / `extends: foo::repo`
  - a **cross-repo type claim**
    - see [[type repo qualifier]]
  - `type: foo::repo`, an instance claims a peer's type as its identity
    - see [[type-instance type]].
  - `extends: foo::repo`, a type-def extends one as a parent
    - see [[type-def extends]].
- `someField: foo::repo*`
  - a **cross-repo field slot**
  - demands a peer's type as a value's type
    - see [[type repo qualifier]].

The same `::` reads the same at every type-name position
- a parent
- a meta block
- a body splice

See [[type repo qualifier]].

# Structure
An example knowledge base over three repos:
- `ontology`, a foundational vocabulary, owns `person` and `commentary`.
- `library`, a shared book catalog, depends on `ontology`.
- `notes`, your personal reviews, depends on `library` and `ontology`.

```yaml
# library/type/book.type.yaml
fields:
  name: String
  # cross-repo slot, type owned by ontology, instance can live wherever
  author: person::ontology*  
  released: Date
  # bare, type owned by library, instance can live wherever
  sequelOf?: book*
```

```yaml
# notes/type/book-review.type.yaml
# cross-repo parent, extend type from ontology
extends: commentary::ontology
fields:
  rating: Number
  # cross-repo slot, a reference to a book (type from library repo)
  book: book::library*
  # an optional list of books (type from library repo)
  similarTo?: book::library*[+]
```

```yaml
# notes/dune-messiah.md
---
type: book-review
# the actual book instance happens to also live in library repo
# it could also be [[dune]] if the instance was in "notes" repo instead
book: "[[dune::library]]"
rating: 10
# filled by a body contribution instead of in the frontmatter
# the engine will still surface it for this slot
similarTo:
---
...
this book really reminded my of [[otherBook:similarTo]]
```