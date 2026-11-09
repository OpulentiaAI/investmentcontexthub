---
type: guide
goal: "Author and verify a saved composition using the current host model."
rule: "Build the flat record pool and window references from current definitions, then verify topology, mounting, and persistence."
about: "[[composition::au-host-sdk]]"
---

# Author a composition

Build the composition from the current windows-and-pool contract.
Read the definitions you need:

- [[composition::au-host-sdk]]
- [[window::au-host-sdk]]
- The projections or containers you will use

Find saved entries with `au_instances_of {ofType: "composition::au-host-sdk", origins: ["file"]}`.
A container query does not list openable compositions.

**Give each owned record a stable address**

Give every record a unique stable block id.
Reference window records from the windows list and mark the intended primary window.
Reference each window's content and each container's children through its declared slots.
Use double-caret addresses for records within the document.

**Read each slot's shape**

The pool accepts mountable records, including windows and projection instances.
Put references in reference-only slots.
A container's slot wrapper can also carry structural data.
Read its definition before flattening a nested mapping.

**Preserve the authoritative pool**

Keep each view's required configuration and the composition's routing or other aspects.
For a live composition, prefer supported host operations that update the pool coherently.
For direct authored changes, use the engine mutation contract and current concurrency state.

**Check topology and persistence**

Inspect engine diagnostics for compatible values and references.
Open the composition and inspect its host diagnostics:

- Cycles
- Duplicate use
- Dangling references
- Unreachable records

The host's topology checks go beyond reference shapes.

Exercise persistence and movement in sequence:

1. Save and close the composition
2. Reopen it
3. Reparent a representative view

Check that the view keeps its identity and configuration.
Check the intended windows and routing too.
A type-clean document alone does not establish a usable composition.
