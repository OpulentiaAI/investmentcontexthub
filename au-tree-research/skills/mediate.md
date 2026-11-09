---
type: mcp.skill::au-mcp-sdk
name: mediate
description: >-
  Explore the premise and research graph, develop follow-up questions and recommend what to research next.
  Use after research or when deciding where to deepen the field.
---

Develop the premise into a tree with both broad coverage and deep understanding.
Update its question queue and propose the next research.

## Explore

Read the premise's Intent and Out-of-scope.
Explore its question tree through `parent` links and its articles through `answers` links.
Use the computed map to navigate articles and open questions, checking the graph for current states and retired leads.

Use summaries to choose where to look.
Read articles in full when deriving follow-ups or judging coverage.

Explore older branches as well as new findings.
Follow gaps, unresolved questions and connections across articles.
You do not need to reread every article each round.

Compare what the premise calls for with what the articles establish.
Distinguish missing coverage from coverage you have not checked.
Read relevant existing work before claiming a gap or duplicate.

## Develop questions

Find investigations that would add meaningful understanding:

- Breadth where an important area or perspective is missing
- Depth where an important subject is introduced but underdeveloped
- Connections or disagreements across branches that deserve investigation

Let the subject determine what deeper understanding requires.
A topic already discussed in an article may deserve a focused question.
Make clear what that question would add.
Keep every question within the premise's boundaries.

## Update the question queue

**Reuse or create**

Reuse equivalent open questions and check retired leads before recreating them.
Save new questions as `question.open::au-tree-research` with:

- A `tldr`
- A self-contained `prompt`
- One `parent`

Include the context needed to investigate without the mediation conversation.
Parent a follow-up under its source question, or choose the premise or relevant question for a gap or cross-branch investigation.

**Choose paths**

Follow workspace requirements and supplied writing guidance.
Use requested paths or unused `questions/q - <question itself>.md` paths inside the folder containing the premise.
Keep the question's wording in the filename, adjusting only characters unsafe in filenames or links.

**Retire unused leads**

Retire duplicate or off-scope open leads as `question.dropped::au-tree-research`, preserving their other data.
Leave these untouched:

- Active work
- Questions with saved answers
- Questions with live descendants

Report these for recovery or tree cleanup instead.
Do not force a state change inherited through a custom type.

## Recommend the next research

**Rank by added understanding**

Rank by importance to the premise and the understanding each question would add.
A central gap outranks a marginal refinement.
A consequential deeper question outranks a peripheral topic added merely for breadth.
Do not aim for equal branches or use article count, age or tree depth as a measure of coverage.

**Find at least four follow-ups**

Recommend at least four worthwhile next questions unless the caller requests a different count.
Existing open questions can count if still relevant.

If fewer emerge, explore older branches, thin areas and connections again.
Do not pad the list with trivial, duplicate or off-scope questions.
If evidence or budget limits still leave fewer, explain the shortfall.

One article per area or an empty queue does not finish the premise.
The user decides when to stop the research.

## Refresh the map and return

1. Check saved questions and their parent links
2. Run the `refresh-map` skill once for this premise after all question updates are finished
3. Return a ranked list of question paths with a short reason for each

Include in the result:

- Changes to the question queue
- Limits to the review
- The map refresh result

Leave articles untouched and do not start research workers.
