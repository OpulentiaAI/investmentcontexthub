---
type: guide
goal: "Create a native package with resolvable vocabulary and usable capabilities."
rule: "Declare package identity and dependencies, then verify mounting, typed content, and the consumer that loads the capability."
---

# Scaffold a native package

Declare the package's identity and vocabulary dependencies in `.arsumbris/repo.yaml`.
Give it a README with a useful tldr.
A JavaScript package may also need package.json for its dependencies and scripts.

**Read the current manifest contract**

Use the engine's current schema and write its engine type claim.
Take supported fields from that schema.
Copied comments or installation scripts may describe an older format.

**Declare vocabulary dependencies**

Declare peer packages used by the vocabulary:

- Claims and inheritance
- Field shapes
- Typed metadata

The engine's builtin vocabulary is universally available.
Value links can reach mounted members without making every linked package a type dependency.
See [[where-a-type-lives]].

**Check how the workspace reaches it**

A declaration still needs a resolvable location and a workspace mount.
Inspect the live member list and the intended role.

Discovery composes the runtime.
It does not substitute for a vocabulary dependency.
The declared package name need not equal the folder's basename.

**Author and use the capability**

Record definitions declare fields as a mapping and inherit through `extends`.
Named value contracts use `shape:`.
Instances claim `type`.

Follow the capability's loading contract.
[[the-capability-pattern]] explains the distinct paths for tools and skills as well as projections.

Check the package boundary the change affects.
For a new package or a mounting change, check its live member role and vocabulary resolution.
For a new capability or a loading change, use it through its consumer.
Inspect diagnostics for the changed scope and assess reported warnings.
Reuse current evidence for unchanged paths.
A running daemon or a manifest on disk establishes only part of the result.
