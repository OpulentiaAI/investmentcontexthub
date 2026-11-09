---
type: mcp.skill::au-mcp-sdk
name: research-premise
description: >-
  Help the user shape a research subject into a premise and starting questions.
  Use when opening a new research field.
---

Turn a conversation about a subject into a clear research premise.

## Shape the premise together

Understand what the user wants to investigate and why.
Ask a few useful questions about scope and boundaries, building on what they already told you.

Briefly explore the subject through relevant sources to help frame it and find its main areas.

Draft:

- `# Intent`: what to investigate and why
- `# Out-of-scope`: concrete kinds of questions that do not belong
- A handful of distinct starting questions, each ready for research

Let the subject determine the scope and questions.
A narrow premise may need only one starting question.
The field studies the subject, with concrete implementation left downstream.

Present the draft, discuss adjustments and save it once the user agrees.
If they already agreed to the draft, save it without asking again.

## Save

Check for an existing field before creating a duplicate.
Follow the workspace's note requirements and supplied writing guidance.

**Create the notes**

Save a `research-premise::au-tree-research` with a `tldr` and the two sections.
Save starting questions as `question.open::au-tree-research`, each with:

- A `tldr`
- A self-contained `prompt`
- The premise as its `parent`

**Choose paths**

Use the chosen research folder, or the destination repo's root by default:

- `premise - <name>.md`
- `questions/q - <question itself>.md`
- `articles/<article name>.md` for later research
- `map - <name>.md` when refresh-map runs

Keep question filenames readable and phrased as questions, adjusting only characters unsafe in filenames or links.
Honor explicit paths and never overwrite an existing note to create a new one.

## Check and return

Check the saved notes and their parent links.
Return their paths and any unfinished work.
Leave research and later questions to the other skills.
