The `::repo` qualifier on a type name,
naming which repo owns the type.

The type-name axis of `::repo`.
The value axis, a wikilink pointing into a peer, is [[type reference]].

See [[cross repo typed graph]] for the general idea of types crossing repo boundaries.

# Properties

## Owner of the type, not location of a value
`foo::repo` names the repo that owns the type `foo`.

### Inside a type definition
Given the type-def for "myType" inside repo "repoA",
`repoA/type/myType.type.yaml`

Inside the type-defs parent/mixin type ([[type-def extends]]):
- `extends: foo` - the bare name
  - "foo" is a type inside the same "repoA" as "myType"
- `extends: foo::otherRepo` - repo qualifier
  - "foo" sits in another repo "otherRepo"
  - we must specify the name of the repo so the type can be found
  - "otherRepo" must be a declared peer, see [[repo yaml]]
  
Inside a type-def's slot definitions ([[type-def fields]]):
- `myField: foo*` - the bare name
  - an instance of "myType" that fills "myField" must reference a file that has "foo" in its closure
  - "foo" is defined inside the same repo (repoA)
  - the actual referenced instance can sit wherever
- `myField: foo::otherRepo*` - repo qualifier
  - an instance of "myType" that fills "myField" must reference a file that has "foo" in its closure
  - "foo" is defined inside another "otherRepo"
  - the actual referenced instance can sit wherever

In both cases `foo::repoA` within "repoA" is legal but redundant,
the bare form is canonical.

- so `foo::repo*` demands the type `foo` from `repo`
  - the referenced node can still live anywhere.

## Every type-name position
The qualifier reads the same wherever a type name appears.

Inside a type-definition file:
- `extends: foo::repo`
  - a parent / mixin
  - a type-def's extension
  - see [[type-def extends]].
- `myField: foo::repo*`
  - a field shape
  - before the suffixes
  - see [[type-def field shape]].
- same for meta sub-regions
  - see [[type-def meta]].
- `use: foo::repo`
  - body splice
  - see [[type-def body use]].

Inside a type instance file:
- `type: foo::repo`
  - an instance's identity
  - see [[type-instance type]].

## The peer gate
`::repo` may name only a declared dep, a peer.
the repo's `deps`, see [[repo yaml]].

Failure cases:
- a mounted member that is not a declared dep, the gate itself
  - [[spec - diagnostic codes^type-repo-not-a-dependency]], fix by adding it to `deps`.
- an undeclared repo, not a member at all, likely a typo
  - [[spec - diagnostic codes^type-repo-unknown]].
- a declared dep not present in this workspace
  - [[spec - diagnostic codes^type-repo-unavailable]], a warning, resolves once mounted.
- a present peer with no such type-def
  - [[spec - diagnostic codes^peer-type-not-found]].

## Suffix order
For suffix ordering, please see:
- [[type-def shape suffixes]]
- [[type-def legal names]], which forbids ":" inside file names

## Names are unique per repo
Within one repo a type name is unique,
a second is [[spec - diagnostic codes^duplicate-type-def]].

Across repos the same name is allowed,
each repo owns its namespace,
`::repo` disambiguates.

# Structure
In repo `notes`, deps `library` and `ontology`.

```yaml
# notes/type/book-review.type.yaml
extends: commentary::ontology         # parent, a type owned by ontology
fields:
  book: book::library*             # slot, a type owned by library
  replyTo?: book-review*           # bare, a type owned by notes, this repo
```

```yaml
# notes/content/my-review-1.md  -  instance file
type: book-review                    # canonical, bare
```

```yaml
# notes/content/my-review-2.md  -  instance file
type: book-review::notes             # redundant, a type-repo-self hint
```

