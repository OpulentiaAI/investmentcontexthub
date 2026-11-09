---
type: mcp.skill::au-mcp-sdk
name: write-a-guide
description: Authors or improves a typed Ars Umbris guide in the package that owns the advice. Use when a consumer wants to add a guide, turn a recurring design decision into guidance, or refine an existing guide's recommendation and examples. Produces the guide and checks its sources, graph contract and discovery. Use apply-writing-style for a prose-only rewrite, and write-a-skill for agent skill authoring.
related-tools:
  - "[[mcp.tool.au_agent_guide::au-agent-guides]]"
---

# Write a guide

Write a guide that helps the reader decide.
Use the owning package's source paths, not this skill's materialized directory.

## Find the decision

Improve the guide that already owns the question.
If the owner is unknown, find related guidance with au_agent_guide.
[[a-guide-earns-its-slot::au-agent-guides]] helps judge whether advice needs its own guide.

If the service is unavailable, use au_instances_of.
Set ofType to guide::au-agent-guides.
Limit origins to files.

**Check the sources**

Support changed claims with sources.
Read the current contract and its consumer when their behavior is uncertain.
Reuse inspected evidence until relevant state changes or you are unsure it is current.

Keep the decision and evidence in the guide when that is enough.
Optional ways to resolve uncertainty:

- Research notes
- Design artifacts
- Independent review
- Other ways to resolve the uncertainty

## Author the guide

Use [[guide::au-agent-guides]] or an existing kind that fits.
The owning package needs au-agent-guides as a type dependency.
Give the guide a goal.
State a rule the reader can act on.
Use about when a type helps identify the subject.

**Link the evidence**

The example field references type definitions.
To fill example from the body, keep its frontmatter anchor.
Use ordinary links for instances and executable source.
Qualify cross-package links.

**Apply the voice**

Follow [[write-a-useful-guide::au-agent-guides]] for the editorial standard.
Apply the consumer's active writing voice.

Read the old guide in full.
Preserve supported claims and examples unless the task calls for a substantive correction.
Keep code and structured values intact during a prose pass.

## Check the changed behavior

Check whether the advice helps the reader choose.
Check when it applies.
Check what the affected examples demonstrate.
State limits where sources disagree or operations are missing.

**Check structure and use**

Read the diagnostics returned with the write.
Request scoped diagnostics if none were returned.
Fix errors the change introduced.
Assess warnings before relying on the change.

Check discovery after changing:

- Identity
- Type claims
- Delivery

Exercise a consumer or run a guidance trial when needed to resolve uncertainty about the changed behavior.
Stay within the user's scope.

**Report the result:**

- The authored path
- The decision the guide helps the reader make
- The checks that support it

Distinguish:

- Source you inspected
- Tests you ran
- Trials you did not run
