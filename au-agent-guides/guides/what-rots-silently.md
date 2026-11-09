---
type: guide.principle
goal: "Identify what structural validation cannot establish."
rule: "Inspect diagnostics at all relevant severities, then verify meaning and consumer behavior beyond the engine's checks."
---

# Check beyond clean diagnostics

Use diagnostics for the structural findings they report.
Check meaning and consumer behavior at the layers that can establish them.
Clean diagnostics do not establish:

- True prose or justified relationships
- Executable code
- Completed side effects

**Separate acceptance from correctness**

The engine can accept a write that leaves diagnostics.
A consumer may reject an action because of those diagnostics or its own invariants.
Report those observations separately.

**Read relevant severities**

A missing typed target or required-meta block can be a warning with immediate consumer consequences.
Other warnings can describe legitimate unfinished work.
Classify findings by consequence.

**Follow changes beyond the count**

Examples that need further checks include:

- Follow a renamed heading or moved referent to check its destination
- Inspect effective metadata after changing inheritance or an explicit empty meta list
- Check the consumer after changing a locator, configuration or discovered family
- Re-read an example after its implementation changes, even when the link resolves
- Check other changed behavior through the consumer that interprets it

**Check historical availability separately**

A commit pin preserves a historical coordinate.
It does not drift with the live target or establish that the current consumer understands the old content.
Retrieval also depends on the referenced git objects being available.

State the result each observation establishes, such as:

- An accepted write
- A resolved target or compatible value
- Loaded code
- A correct outcome
- Another result observed at the layer responsible for it

If the task needs stronger evidence, check the layer that can supply it.
