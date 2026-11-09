---
type: guide.gotcha
goal: "Require a read before a tool action through the existing mediation floor."
rule: "Declare the read prerequisite, then test the loaded floor's actual resolution and denial behavior; an observed read does not prove comprehension."
about: "[[read-precondition-meta::au-mcp-sdk]]"
example:
---

# Check a read prerequisite

Declare an executable read prerequisite with [[read-precondition-meta::au-mcp-sdk:example]] on the guarded tool's definition.
The loaded tool-precondition floor compares its resolved requirements with the session's read or served view.

It checks invocations routed through the configured gate prefix.
With no prefix, or for an unprefixed invocation, the current floor allows the call without this check.
A request in the tool description remains guidance.

**Identify the file actually read**

Read the exact target through `read_file_pinned` or a native file reader whose read the adapter records.
A serving tool can participate through [[serves-files-meta::au-mcp-sdk]] when its declaration maps to the file actually served.
The current templates describe paths beneath the serving tool's package.
They cannot express arbitrary cross-package selection.

**Know what the observation establishes**

The observation records a call and its declared path mapping.
It does not attest to:

- Successful delivery
- Full comprehension
- Following the advice

A served entry also lacks the exact-content read and concurrency token required by read-before-write.

**Inspect failure behavior**

The current floor:

- Skips unresolved targets
- Allows calls when derivation cannot run
- Strips repository qualifiers during target derivation

Check cross-package requirements with a negative case.
Implement and test a stricter invariant in the mediator or operation boundary when the operation needs it.

In a fresh session, attempt the guarded action in sequence:

1. Before reading
2. After reading a different file
3. After reading the required file

Also check an unresolved target and the relevant unavailable-engine case.
Document only the guarantee those observations support.
