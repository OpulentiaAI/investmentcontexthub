---
type: guide.gotcha
goal: "Share a build across related projection surfaces without sharing the wrong instance state."
rule: "Give each surface its own projection definition and select its function from one registered module when shared ownership justifies it."
about: "[[projection-runtime-meta::au-host-sdk]]"
example:
---

# One module can supply several surfaces

Share a package and entry when related surfaces have common ownership and dependencies.
Give each surface its own:

- Projection subtype
- Configuration contract
- Runtime locator

The locator's export names a mount function on the registered default object.

[[editor-pane::editor:example]] and [[editor-status::editor:example]] share an entry while selecting different surfaces.
The host discovers and places each through its own kind.
defineProjection composes the module.
The surfaces do not each need an independent ESM default export.

**Choose state ownership separately**

Several mounted instances can use one module.
Separate windows can use different runtime realms.
A module variable does not automatically hold the state of “this pane.”

Keep instance state in the mount or a store keyed by the appropriate stable identity.
Use host channels for composition state or communication across runtime boundaries.
Give every mount its own cleanup.

**Separate packages when ownership differs**

Separate packages can be justified by different:

- Ownership
- Release cadence
- Isolation needs

They can still share code.
A shared dependency does not require a shared entry.

Mount two instances of one surface and a related second surface.
Change one instance's state and unmount it.
Check that only the intended consumers observe the change and retain resources.
