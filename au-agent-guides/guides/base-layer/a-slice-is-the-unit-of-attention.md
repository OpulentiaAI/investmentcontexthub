---
type: guide.principle
goal: "Choose enough context to reason about or verify a graph change."
rule: "Start with the task's evidence needs, then expand the reading scope until its dependencies and counterexamples are covered."
about: "[[map::au-base-types]]"
---

# Choose the scope of attention

Read enough of the graph to support the task's conclusion.
Choose the starting scope from the question:

- A precise lookup may need one node
- A relationship change needs its endpoints and relevant referrers
- An architectural decision may need an overview and selected deep reads
- Other tasks need the sources that can establish their material claims

A small graph can be read whole.

**Choose the reading aid**

Use a map when it gives useful orientation.
Use the engine read that answers the question directly:

- Type queries or aggregate graph reads
- Neighborhoods or references
- Search
- Other relevant graph reads

A map is not a mandatory gateway to the engine.

**Expand when the evidence demands it**

Treat the initial scope as a hypothesis.
Expand it when a dependency crosses the boundary or an example challenges the interpretation.
Read further when a summary cannot support a material claim.
A convenient map or context budget does not establish sufficient coverage.

**Make the result reviewable**

Give a reviewer enough context to assess the changed claim or behavior.
That can be a corrected value or a chain from types through references into consumer code.
The work's governance determines approval requirements.
The size of the reading scope does not.

[[use-a-map]] covers working from a useful synthesis.
[[what-rots-silently]] covers evidence a structural read cannot supply.

Name the conclusion and its supporting sources.
Find the nearest plausible counterexample or dependency outside the current scope.
Read it if it could change the conclusion.
Report any material boundary left unexamined.
