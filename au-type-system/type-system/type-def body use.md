A splice point that inlines another [[type-def]]'s body.
One of the [[type-def body]] items.

# Properties

## Splice
`use: T` inlines T's body at this position.

Resolved recursively at type-graph load.

Repetition is literal,
`use: T` twice inlines twice,
no dedup.

## In-closure only
T must be in the file's effective closure,
claimed directly or through inheritance.
- [[spec - diagnostic codes^body-use-out-of-closure]].

## Acyclic
The splice graph must be acyclic.
- [[spec - diagnostic codes^body-use-cycle]].

## Template axis only
`use:` pulls in T's body sections, not T's fields.

Field inheritance flows through [[type-def extends]] independently.

## Top-level only
Valid only at the top of the outermost body,
not inside a nested section body.
- [[spec - diagnostic codes^body-use-nested]].

## Empty target
`use: T` where T declares no body splices nothing, a warning:
- [[spec - diagnostic codes^body-use-target-has-no-body]].

# Structure
```yaml
extends: myParentType        # which declares a body
body:
  - section: My Intro Section   # added before the splice
  - use: myParentType           # inlines myParentType's body
  - section: My Outro Section   # added after the splice
```
