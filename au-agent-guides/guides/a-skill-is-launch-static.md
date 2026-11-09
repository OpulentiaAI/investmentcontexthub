---
type: guide.gotcha
goal: "Determine which runtime must refresh after changing guidance or a tool."
rule: "Trace discovery, materialization, import, and session caches separately; a live daemon does not imply live code reload."
example:
---

# Refresh the layer that holds the change

Find the representation the running session uses.
These representations can hold different versions:

- Source files
- Generated harness files
- Imported modules
- Advertised schemas
- Delivered context

**Rebuild launch context**

[[mcp.skill::au-mcp-sdk:example]] and [[mcp.inject::au-mcp-sdk:example]] are assembled and materialized for a launch.
A source edit cannot rewrite context already delivered to a model.

Use the launcher's supported refresh or a new launch, then inspect what the harness loaded.
A harness-specific clear command is not a universal rematerialization operation.

**Refresh executable discovery and schemas**

[[mcp.tool::au-mcp-sdk:example]] runs through the daemon.
Discovery happens at startup or in a lazy pass.
Module imports are cached.
Executable or metadata edits can need fresh daemon discovery.
The adapter or harness may also cache the advertised tool list and input schema.

**Separate fresh reads from fresh code**

This guide server reads content through the broker on each request.
Its guide text can be current while its imported executable remains unchanged.

A session-start hook computes context at session open.
That is a different path from changing a static inject or re-emitting previously generated text.

Inspect the actual change through the delivery path the session uses.
Refresh the first layer retaining the old value.
Use a controlled new session when the existing session cannot refresh it.

If the stale layer is unclear, a harmless recognizable change can help locate it.
Compare only the representations needed to resolve that uncertainty.
