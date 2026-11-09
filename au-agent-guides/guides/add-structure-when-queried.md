---
type: guide.principle
goal: "Decide whether a field, type, or typed relation earns its cost."
rule: "Add structure for a concrete distinction a reader or consumer needs, and compare its cost with the available simpler forms."
---

# Add structure for a concrete need

Add structure when it preserves a distinction the work needs.
Concrete needs include:

- Queries or validation
- Precise references or loader discovery
- Independent lifecycle or reliable automation
- Other behavior that depends on an explicit distinction

**Start with the behavior**

“Find every approved claim” and “diagnose an answer pointing at unfinished work” need different support.
Choose the shape for the actual behavior and inspect the read or consumer that will use it.
Declaring a field does not create an arbitrary query API.

**Consider smaller forms**

- A prose link can explain a relationship without a named field
- An inline record can carry structured data without a separate file
- A named scalar can share a value constraint without a record
- Another simpler form can fit if it preserves the required meaning

Choose the form that preserves the needed meaning.
[[name-a-value-contract]] and [[not-every-noun-is-a-type]] cover these choices.
A new type can also earn its place before its first instance by defining a real extension contract.

**Count the work on both sides**

Saving a field can cost more if every consumer must infer its meaning from prose.
Speculative fields cost authorship and migration work without serving a known distinction.

Once the need is clear, use [[design-for-growth]] for evolution and [[a-kind-or-a-question]] for the investigation worth doing.

Remove the proposed structure from a representative example and try the intended task.
Name what disappears:

- Information
- A guarantee
- Consumer behavior

Leave the structure out if nothing useful changes.
