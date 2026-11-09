---
type: guide
goal: "Write guidance that helps a builder choose and check a representation or way of working."
rule: "Teach the recommendation with its reason, the condition that changes it and evidence the reader can inspect."
tldr: Teach a useful decision with its reason, boundary and evidence. Check meaning separately from structure.
---

# Write a useful guide

State the advice.
Name the condition that changes it.
Keep the reason beside the advice so readers can apply it beyond the example.
[[a-guide-earns-its-slot]] helps decide whether the advice needs a guide.

## Explain the choice

Prefer the least structure that preserves the distinctions the task needs.
Count what it costs to:

- Author it
- Operate it
- Evolve it

A query is one reason for structure.
Validation can justify it too.
So can a consumer's need for a precise reference.

**Explain the mechanics**

Include mechanics needed to understand the choice.
Link the owning definition for the complete contract.
Use “must” for a requirement whose owner you can name.
Give a reason for a design recommendation.

**Separate the claims:**

- The engine establishes structure and diagnostics
- The consumer establishes runtime behavior
- The guide recommends a choice

Keep these results distinct:

- A successful write
- Clean diagnostics
- A useful outcome

## Use examples as evidence

Prefer a real example that demonstrates the decision.
Say what it shows.
Explain why it supports the advice.

**Check current support**

A live link avoids copying an implementation.
The link does not keep your interpretation current.
Reuse inspected evidence until relevant state changes or you are unsure it is current.

**Label illustrations**

A short snippet can clarify a distinction.
Label it as an illustration.

Support claims that a recipe runs with the current contract and an observed build or invocation.
A resolving link or compatible type alone does not show that it runs.

**Choose the link**

The optional example field accepts type definitions.
To fill it from the body, keep an example: anchor in frontmatter.
Use ordinary links for other artifacts.

## Shape the prose

Apply the active house writing voice.
Preserve supported claims and meaningful exceptions.
Unless the task authorizes changes, preserve:

- Code
- Structured values
- Quotations

**Choose a template**

Kind templates are optional starting points.
When a template is a checked contract, match its:

- Section names
- Order
- Heading depth

An H2 below a title does not satisfy a top-level H1 section with the same name.

**End with a useful check**

Add a final check when it distinguishes a fitting choice from a plausible mistake.
A counterexample may be enough.
Do not add a ritual for a low-impact decision.

## Make the guide findable

Name the file for its task or decision.
Give each guide in this package a goal.
State a rule the reader can act on.
Use about when a type helps identify the subject.

These are editorial expectations.
The shared [[guide]] contract keeps its fields optional.

Use the concrete base unless a kind clarifies the form or adds a useful shared distinction.
Follow [[write-a-guide]] to author and check a guide.
