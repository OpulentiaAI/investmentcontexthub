---
type: guide.gotcha
goal: "Write a tool description and decide whether proactive guidance is useful."
rule: "Make the description sufficient to select and call the tool; add guidance only for a distinct proactive use cue."
example:
---

# Describe the tool where it is selected

Write the description so an agent can choose and call the tool.
State what the caller needs:

- Purpose
- Useful input distinctions
- Result
- Material limitations

Include a brief “use this when” if it distinguishes nearby tools.

**Add a separate cue when useful**

[[tool-presentation-meta::au-mcp-sdk:example]] also offers guidance for session orientation.
Use it to prompt a specific occasion to seek the tool before inspecting its entry.
Keep it optional and give it a cue beyond the description.

These surfaces reach the reader at different moments.
The description must support selection on its own.
Long instructions consume attention whenever either surface appears.

**Put procedures and checks in their own mechanisms**

Use a skill for a task requiring several steps and judgment.
Use the appropriate runtime check when an invariant must affect execution.
The description and guidance can explain those mechanisms, but cannot enforce them.

Read the description alone among neighboring entries and check whether it supports the right selection and call.
Then read the guidance in session orientation.
Retain it when it adds a useful cue.
