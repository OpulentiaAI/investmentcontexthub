---
type: guide.principle
goal: "Decide whether advice needs a guide of its own."
rule: "Keep a guide when it improves a distinct, plausible decision and gives the reader enough evidence to apply it."
---

# Give each guide a useful decision

Keep a guide when it helps a builder make a plausible decision.
It can prevent a mistake or explain a tradeoff between valid choices.
The advice need not be compulsory to be useful.

**Find the gap**

Look for evidence of the gap:

- A repeated failure
- A difficult implementation choice
- A grounded counterexample
- Another concrete decision the existing guidance does not help

Read existing guides and reference material first.
A missing paragraph may be better repaired in its current guide than added as a catalogue entry.

**Connect the recommendation to its reason**

Include mechanics that the reader needs to understand the choice.
Keep a field list in the type reference when it adds no decision-making guidance.
An exact operation or invariant may also need a tool or hook.
See [[pick-the-vehicle]].

Use the concrete [[guide]] base when no kind helps.
A kind should clarify the form or add a shared contract.

**Check the boundary**

Compare nearby cases that should choose differently.
[[not-every-noun-is-a-type]] distinguishes a particular note from a singleton capability whose type enables discovery.
That distinction gives the reader more help than an instance-count rule.

Name the choice the reader can make and the plausible mistake the guide prevents.
Improve an existing guide if it already owns that choice.
Leave the advice out if it still changes no useful decision.
