---
type: mcp.skill::au-mcp-sdk
name: research
description: >-
  Research one question in depth and synthesize a self-contained article.
  Use for an assigned question or to recover an interrupted answer.
---

Create a deeply researched, coherent article that develops the question into understanding.
Let the subject determine the evidence, approach and structure.
Follow supplied writing guidance and the caller's scope and budget.

## Start from the question

Read its prompt and any relevant supplied material.
Check for existing articles through their `answers` links.

**Recover existing work**

Recover an unfinished answer or review a complete one before creating anything new.
Create an additional answer only when requested.
If several existing answers make recovery ambiguous, ask which to use.

Leave dropped questions alone unless the user asks otherwise.

## Investigate in depth

**Frame the investigation**

Frame what a substantive answer must establish.
Check assumptions and ambiguous terms.
Break the question into the dimensions it needs, without imposing a fixed disciplinary template.

Use your knowledge to form a provisional outline.
Mark unchecked claims, missing evidence and competing accounts as the search queue.
Use web search and source reads to investigate them, revising the outline as you learn.

**Choose evidence** suited to the claim:

- Empirical claims need observations, methods and conditions
- Historical claims need sources in their context
- Interpretations need support in the material being interpreted
- Arguments need sound premises and reasoning
- Other claims need the standards appropriate to their subject

**Read in context**

Read sources beyond search snippets.
Use authoritative syntheses to understand the field and primary material to examine important evidence.
Read whole works when the question depends on their structure or development.
Keep source details so the reader can check the claims later.

**Test the evidence**

Seek concrete support where the answer would otherwise stay vague.
Cross-check consequential or disputed facts against independent evidence where available.
Test interpretations and arguments against plausible alternatives.

Distinguish sourced findings, your inferences and illustrative examples.
Never invent specifics or imply certainty the evidence does not support.

**Deepen the answer**

After each pass, identify what is missing or in conflict and investigate those gaps.
Explain why accounts differ and weigh their support without forcing agreement or equal weight.

Depth is the default.
Develop the central questions, important distinctions and implications before stopping.
Continue while investigation is likely to materially deepen the answer, within the caller's budget.
Repeated familiar facts do not establish coverage of an unexamined area.

## Plan the synthesis

Before drafting, establish:

- The central answer and its supporting evidence
- How the findings connect, qualify or challenge one another
- The distinctions needed to understand them
- What remains uncertain and what the reader can conclude

Build the article's outline from this understanding, not the order of searches or sources.
Return to the evidence if a missing connection prevents a coherent answer.

## Write the article

**Build a connected account**

Develop the explanation, description, interpretation or argument the question calls for.
Synthesize the material into a connected account, not a sequence of source summaries.
Show how concrete evidence supports broader conclusions and where its support ends.

Open with `# Overview`, giving the subject, central answer and scope.
Make it understandable on its own.
Let later sections develop the subject in an order the reader can follow.

**Give the reader enough explanation**

Write for a curious, capable reader who has not seen the prompt or sources.
Give difficult ideas enough context, examples and connected reasoning.
Develop one main idea per paragraph, with whitespace between ideas.
Use prose for reasoning and lists for parallel facts.

Cut repetition and filler, not the explanation the reader needs.
Length follows the substance, with no word or source quota.

**Keep the article self-contained**

Identify sources near the claims they support.
External citation links are allowed, but the article must make sense without following them.
Keep all wikilinks outside the article body, including examples.

## Save the article

Save as `article::au-tree-research` or the requested compatible type, following the workspace's note requirements.
Include a `tldr` and an `answers` link to the question.

Follow the question's parent chain to its premise.
Use the assigned path or an unused `articles/<article name>.md` inside the folder containing the premise.
Name the article for its subject or finding.

On recovery, update the existing article and preserve its metadata.

## Review and finish

**Review the saved article**

Re-read the saved article for evidence, depth and readability.
Check that its sections build a synthesis and that difficult ideas receive real development.

Find passages where a careful reader still needs explanation, evidence or context to understand the central answer.
Develop those passages before finishing.
Repair unsupported claims, shallow passages and missing connections.

An unresolved issue in the field is acceptable when the article establishes what is known and why uncertainty remains.
If the investigation remains incomplete, leave the question open and report the gaps.

**Check before completing**

Check the article's diagnostics before completing.
Its `answers` link temporarily reports a state mismatch while the question is open.
Resolve other errors first.

**Complete the question**

After review, re-read the question and change only its direct `question.open::au-tree-research` claim to `question.researched::au-tree-research`.
Preserve its prompt, parent and other data.

Handle completion exceptions:

- Already researched: leave its state unchanged
- Incompatible state change or state inherited through a custom type: report it instead of forcing a change
- Parallel answers to one question: use distinct article paths and one designated completion owner

**Check and return**

Check diagnostics on both notes.
The answers mismatch should clear after completion.
Report any unfinished work honestly.

Return the article path and question state.
Leave new questions to mediation and the map to refresh-map.
