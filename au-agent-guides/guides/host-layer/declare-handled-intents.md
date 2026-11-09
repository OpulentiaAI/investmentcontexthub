---
type: guide.gotcha
goal: "Declare and route the commands a projection can receive."
rule: "Keep static intent capabilities, mounted handlers, and composition routing consistent; choose ambient and aimed delivery deliberately."
about: "[[handles-intent-meta::au-host-sdk]]"
example:
---

# Declare the intents the projection handles

Keep these parts consistent:

- Static intent capabilities
- Mounted handlers
- Composition routing

[[handles-intent-meta::au-host-sdk:example]] declares which intent definitions a projection can handle.
The host reads it during discovery.
The mounted instance separately binds runtime handlers through its supplied intent capability.

**Choose ambient or aimed handling**

A viewer can accept an open command aimed at it without joining the ambient open search.
[[editor-pane::editor:example]] demonstrates this through handles and handlesTargeted.
Read the intent definitions with the handler implementation.

**Trace the route**

The host interprets the intent mechanism and the composition's [[intent-routing::au-host-sdk:example]] configuration.
The recipient can depend on:

- Explicit wires and reachability
- Focus
- Mounted topology

A static capability establishes eligibility, not delivery.

**Keep the relationships distinct**

Handler metadata relates the projection and intent definitions.
The projection does not need to inherit the intent's data type.
Declaring a fired intent and binding a handled intent are separate responsibilities.

Keep handler registration and disposal with the mounted instance.
Read the actual capability checks.
Missing declarations do not all have the same failure policy.

Inspect capabilities before mounting, then mount two plausible recipients.
Try an ambient command and an explicitly aimed command.
Check:

- The recipient
- The payload
- Handler disposal after unmount
