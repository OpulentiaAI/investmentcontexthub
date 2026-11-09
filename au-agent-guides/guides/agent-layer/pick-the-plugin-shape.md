---
type: guide.gotcha
goal: "Choose an agent tool or the hook phase a runtime capability needs."
rule: "Use a tool for an agent-invoked operation; use hook shapes for runtime phases, choosing ordering and failure behavior deliberately."
about: "[[plugin-runtime-meta::au-mcp-sdk]]"
example:
---

# Choose the plugin kind and hook phases

Use a tool for an agent-invoked operation and a hook for internal runtime phases.
A subtype of [[mcp.tool::au-mcp-sdk:example]] supplies invoke and has no shapes list.
A subtype of [[mcp.hook::au-mcp-sdk:example]] supplies one or more hook phases.

Name it `mcp.tool.<name>` or `mcp.hook.<name>` as required by the loader.
Inheritance alone does not satisfy that discovery filter.

| Hook shape | Job |
| --- | --- |
| observer | Consume session or lifecycle events |
| mediator | Decide or review a pending action |
| stamper | Add records folded into a governed write |
| session-start | Compute context at session open |

**Place the behavior on the timeline**

Use a mediator to check a pending action before execution.
An observer cannot undo the action afterward.

Use a stamper when generated data belongs in the governed mutation's own commit.
Use session-start for fresh computed context.
A static inject supplies authored standing text.

**Combine phases for one capability**

A hook can implement several shapes when they form a coherent capability.
Its fields describe typed configuration supplied by an agent profile.
They are not agent-call arguments.

**Choose ordering and failure behavior**

Choose the tier by responsibility.
They run in this order:

1. gate
2. floor
3. policy

Critical marks load and selection requirements.
It does not guarantee that every callback succeeds or every hook failure blocks.
Read the callback's actual error handling.

Place the behavior on the runtime timeline and state what must happen if it fails.
Check each part of the declaration against that result:

- Kind and shape
- Ordering tier
- Failure policy
