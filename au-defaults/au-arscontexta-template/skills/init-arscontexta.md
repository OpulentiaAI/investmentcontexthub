---
type: mcp.skill::au-mcp-sdk
name: init-arscontexta
description: Introduce Ars Umbris and ask a few questions to establish a workspace premise. Use when the person starts an Arscontexta knowledge workspace or resumes unfinished setup. Ordinary work and package development use their own routes.
---

# init-arscontexta

Help someone starting from nothing understand the possibilities and give their workspace a purpose.
Reuse saved answers when resuming setup.

## Introduce the workspace

Explain Ars Umbris as a local workspace where the person and their agents build connected knowledge together.
Use [[README]] to introduce the packages briefly:

- Collect sources, research questions and connect useful knowledge
- Create guides, skills and a writing profile for their work
- Check meaning and improve the workspace as they use it

Explain that they can extend the software with their agent's help.
They can build missing features, including projections (custom views), tools and workflows.
These extensions need implementation and checks in the workspace.

Name the relevant packages and give one example suited to their interests when known.
Explain that their answers will become a short premise to guide future work.

## Ask a few questions

Invite short, tentative answers:

- What would you like this space to help you understand or do?
- What material or working practices should guide us?
- What should we leave outside this workspace for now?

Ask only what the conversation has not already answered.
Wait for their answers before writing the premise.

## Save the premise

Check that the consumer directly depends on `au-competency` before writing.
Create `workspace-premise.md` in the consumer's repo, or update its existing premise.
Use [[workspace-premise::au-competency]] with three short sections:

- **Purpose:** what the workspace should support
- **Warrant:** the practice or evidence behind that approach
- **Out-of-scope:** what belongs elsewhere

Keep uncertainty visible.
Preserve existing organization.
Check the saved premise against their answers and inspect diagnostics.

## Begin work

Show the premise and suggest one useful first task.
Continue an already requested task using the available tools and owning package's guidance.
Let the person's goal shape what comes next.
