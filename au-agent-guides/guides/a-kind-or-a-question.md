---
type: guide.principle
goal: "Choose how much investigation a modeling decision needs."
rule: "Research uncertainty that could change the model; prototype a clear, reversible contract with representative data."
---

# Match the investigation to the decision

Investigate uncertainty that could change the design.
Match the evidence to the question:

- For a domain distinction, choose evidence that can answer it
  - Examples
  - Domain sources
  - A domain expert
- For an engine mechanism, choose evidence of its behavior
  - Its definition
  - Its implementation
  - A focused probe

**Prototype a clear local contract**

Inspect the existing vocabulary.
Draft representative instances.
Try the intended read or consumer.
Include an awkward case.
A small prototype can reveal more than a speculative taxonomy.

**Investigate costly or contested choices**

Spend more effort before consequential choices such as:

- Establishing a widely consumed base
- Committing to a costly migration
- Choosing a distinction whose meaning is contested
- Other choices whose uncertainty or cost warrants investigation

A first cut can validate cleanly while its categories misrepresent the domain.
A small change can still warrant a cheap check of an uncertain detail.

**Keep the evidence reviewable**

Use engine validation or mutation preview for the mechanics it covers.
A vocabulary or diagnostics preview cannot establish that the domain model is right.
Keep the evidence and reason for the shape with the affected work.
Use a separate design record when the decision needs its own reader or lifecycle.

Type changes remain editable, but their costs grow through instances and consumers.
Follow the user's authorization and the repository's governance.
Adding a type does not create a universal human approval gate.

Name the unresolved question and a plausible answer that would change the design.
Investigate it before committing to the choice that depends on it.
