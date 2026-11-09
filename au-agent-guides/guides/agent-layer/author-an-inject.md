---
type: guide
goal: "Author standing context for an intended session profile."
rule: "Create an inject instance with a justified scope, inspect its expansion, and verify the selected launch output."
about: "[[mcp.inject::au-mcp-sdk]]"
---

# Author an inject

Create a markdown instance of [[mcp.inject::au-mcp-sdk]] for standing context.
Supply:

- Its name
- A picker description
- The body to deliver

The description helps someone select the inject.
The agent does not match it as a task trigger.

**Expand only as needed**

Start with the body alone.
Add reference depth when neighboring content belongs in the session's standing context.
Select relevant edge kinds.
A walk beyond one hop requires an explicit edge-kind filter.

Inspect the expanded set and its size before relying on it.

**Keep essential context in the seed body**

Depth-zero expansion emits the seed body regardless of the display option.
A failed walk falls back to that body too.
The mode including frontmatter takes effect on a successful reference walk.

Inspect the delivered output if the workflow relies on those fields.
Source content omitted from delivery cannot inform the model.

**Compose and select the context**

Find the file through the qualified inject instance query and inspect scoped diagnostics.
Select it in the intended profile and inspect materialized output, including omitted blocks.
Use [[inject-is-prepaid]] for budgeting and [[a-skill-is-launch-static]] for refresh behavior.

Compare the output with the knowledge that session needs.
Use a skill for task-specific instructions or a session-start hook for context computed at session open.
