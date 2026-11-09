The ordered passes that validate a knowledge base, and how errors gate them.

# Properties

## Pass order
1. knowledge base load
  - scan the filesystem, catalog basenames.
  - emit knowledge-base-load diagnostics, e.g. [[spec - diagnostic codes^case-collision-basename]].
2. type-graph load
  - parse every [[type-def]], build the inheritance and [[type-def sealed]] graphs.
  - run the type-graph load checks.
3. per-file instance validation
  - walk the [[type closure]], check
    - required fields
    - shapes
    - and the sealed-leaf rule.
  - resolve each [[type reference]].
4. [[type candidate scan]]
  - advisory, on demand.

## Error gating
An `error` blocks a downstream stage.
A `warning` is advisory, the stage completes.

- knowledge-base-load diagnostics are advisory.
  - they do not block the type-graph load.
  - except where they stop reference resolution in stage 3.
- a type-graph load error blocks per-file validation.
- a per-file error stays per-file, other files still validate.
- the candidate scan runs on demand, regardless of per-file results.

## Open-world
Per-file validation is [[type open-world validation]].
Extras pass as advisory, see [[type extras]].
