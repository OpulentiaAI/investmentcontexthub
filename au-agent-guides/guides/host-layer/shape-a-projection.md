---
type: guide.gotcha
goal: "Implement a projection's mount, configuration, and cleanup responsibilities."
rule: "Render within the supplied container, use the host's ownership boundaries, and make configuration and cleanup correct across mounts."
about: "[[projection::au-host-sdk]]"
example:
---

# Respect the mounted view's boundaries

Render in the container supplied by the host.
For a pane, let the host or container own:

- Placement
- Framing
- Pane-level controls

Keep meaningful controls within the pane's content.

Status and container projections have other surface roles.
A blanket “never draw chrome” rule does not fit the whole family.

**Clean up each mount**

Return an unmount function from the mount.
Release the resources it owns:

- Listeners and subscriptions
- Timers
- Rendering roots
- Other resources acquired by that mount

Guard asynchronous completions against updating a disposed view.
[[hello::hello:example]] demonstrates that guard.

**Reflect the current configuration**

Read configuration from the supplied host and persist through its supported capability.
Where onOwnConfigChange is available, opting in means reflecting every relevant content change in place, including a changed resource.
Make the handler idempotent because a write can echo back.

Ignoring a changed field after opting in can leave stale content on screen.
Without that capability, use the host's remount behavior.

**Stay within the public contract**

Check optional capabilities before using them.
Use the public boundary instead of reaching into an assumed host implementation to recover a missing capability.
The loaded module must match the entry and mount contract version.

Exercise the lifecycle in sequence:

1. Mount
2. Update configuration
3. Unmount during an asynchronous read
4. Mount again

Visible content should follow the current configuration.
No prior mount should keep receiving or applying updates.
