---
type: guide.gotcha
goal: "Declare the engine access a tool needs."
rule: "Request the smallest broker capability the implementation uses, and distinguish that scope from process isolation."
about: "[[tool-access-meta::au-mcp-sdk]]"
example:
---

# Declare the broker the tool uses

Request the smallest broker capability the implementation needs:

- Use none for an operation with no engine calls
- Use read for graph queries
- Use read-write for governed mutations

The default is none.
[[mcp.tool.au_agent_guide::au-agent-guides:example]] requests read access to discover and retrieve guides.
Compare the declaration with the implementation.

**Declare potential access accurately**

Mediation uses the grant to classify a tool's potential engine access.
A read-write tool can count as write-capable even when a particular call only reads.
Consider separate operations if a multipurpose tool obscures that distinction.

**Distinguish broker scope from process capabilities**

The grant scopes the supplied broker.
It does not sandbox arbitrary module code's filesystem or network access.
A tool with no broker can still use process capabilities.
Evaluate those in the actual execution environment when they matter.

**Check the loaded grant**

Broker scope is established when the plugin loads.
A metadata edit alone does not change the capability held by a running module.
See [[a-skill-is-launch-static]].

List the implementation's engine calls and invoke it under the declared grant.
It should complete within that scope.
Remove read-write if it uses no mutation.
