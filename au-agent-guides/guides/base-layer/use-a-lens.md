---
type: guide.gotcha
goal: "Represent a perspective on a subject without conflating distinct judgments."
rule: "Give a judgment its own record when perspective, evidence, or history must vary independently; use a scoped field when that context is already clear."
about: "[[lens::au-base-types]]"
---

# Give a perspective the context it needs

Represent the context behind a judgment where the task can recover it.
“this company is a competitor” depends on a perspective and often a time.
An unqualified field on a shared subject can make one assessment look universal.

**Give independent judgments a record**

Use a separate record when perspectives:

- Coexist or disagree
- Cite different evidence
- Change independently of the subject

Give it the context the domain needs:

- The subject
- The assessor or standpoint
- Relevant time and support
- Any further context needed to interpret that judgment

[[lens::au-base-types]] is an abstract fieldless marker for perspective kinds.
Extend it alongside a suitable concrete domain contract.
Declare needed fields or consumer checks.
The marker itself requires none of these fields.

**Keep local assessments local**

A field or inline assessment fits when the containing record already makes perspective and scope clear and no independent identity is needed.
A changeable property alone cannot decide between these representations:

- A type
- A role
- A judgment

Operational events can support an assessment without being the assessment.

A map can compare judgments while a lens record preserves one assessment's context.
See [[not-every-noun-is-a-type]] for the broader choice.

Model two observers who disagree about one subject.
Both views should remain interpretable with their context and evidence.
A further note may add nothing if the existing record already separates them.
