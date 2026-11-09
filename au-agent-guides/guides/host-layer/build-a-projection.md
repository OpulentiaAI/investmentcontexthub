---
type: guide
goal: "Build and load a view through the host projection contract."
rule: "Pair the typed config and runtime locator with a registered SDK module, then verify the built entry through an actual mount."
about: "[[projection::au-host-sdk]]"
example:
---

# Build a projection

Choose the subtype for the surface's job.
Choose from:

- A pane
- A status surface
- A container
- Another supported kind

Its fields describe instance configuration.
Its own [[projection-runtime-meta::au-host-sdk]] locates the entry relative to the owning package and declares the mount contract version.

**Use an example for unfamiliar mechanics**

[[hello::hello:example]] illustrates a typed mount with an engine read, cleanup and defineProjection registration.
[[editor-pane::editor:example]] adds instance configuration and declared capabilities.
Read the entry source or build configuration that answers the missing question.
Check the implementation before adapting it as a recipe.
Reuse inspected examples while their relevant state is unchanged.

**Register the module and build its entry**

The default export is the object returned by `defineProjection`.
Type it with the appropriate SDK contract.
The runtime locator's export selects a mount function on that object and defaults to mount.
A plausible function in an unregistered module is insufficient.

Use the SDK's sharedDepExternal seam for host-shared dependencies imported by the bundle.
Duplicate runtime libraries can break shared state or identity despite a successful build.
Inspect the artifact the host loads and its contract version.

**Use the supplied mount capabilities**

The mount receives a container and MountHost.
Use the supplied capabilities:

- entry.path and configuration
- Engine and files
- Other capabilities the mount exposes

Return cleanup for resources the mount owns.
See [[shape-a-projection]] for lifecycle responsibilities.

Inspect diagnostics and subtype discovery.
Build the declared entry and mount it in the intended host.
Exercise the mounted view:

- Configuration
- A representative operation
- Unmount

A dev server helps when the host is configured to load from it.
