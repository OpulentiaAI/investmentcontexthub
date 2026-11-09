---
type: mcp.skill::au-mcp-sdk
name: check
description: Checks the meaning of a changed graph cluster against applicable audits and doctrine, using an independent reader. Records verified findings and the checks actually run. Use when graph work converges or the human asks to verify its meaning. Writing-style audits use check-writing-style, skill and guide reviews use review-a-skill, and structural validation uses au_diagnostics. Repairs stay with fix.
---

# check

Establish whether the affected graph still satisfies its doctrine.
Leave a scoped result and verified [[finding.open]] records for [[fix]].

**Independent reading**

Use a fresh reader who has not seen the material being made.
Give them the actual notes and sources.
An author's summary can conceal the defect under review.

Keep dispatch within the caller's authorization and privacy constraints.
If independent reading is unavailable, report that limit.
An author check does not establish an independent pass.

## Choose the checks

Start with the changed notes and the doctrine they must satisfy.
Include referring notes whose meaning may be affected.
Use au_references when the affected set is unknown or stale.
Reuse current evidence and tool results until relevant state changes or freshness is uncertain.

Select audits whose scope reaches those subjects.
An absent scope gives an audit graph-wide applicability.
Discover the roster with au_instances_of using ofType: audit::au-govern when needed.
Follow every page before claiming complete audit coverage.

Run the applicable audit recipes against their doctrine.
When no audit applies, check the subjects directly against their doctrine.
An empty audit roster does not establish that the graph is sound.
Use engine diagnostics for structural validation.

## Record verified defects

Check each reader catch against the subject and doctrine before recording it.
A reader can lack context.
An unsupported finding can prompt a harmful repair.

Reuse an open finding for the same subject, doctrine and defect.
For a new catch, follow the [[finding.open]] contract.
Supply the required tldr with a short statement of the defect.
Explain the violation and its evidence in the finding.
Set caught_by only when an audit produced that catch.

This pass does not repair subjects or delete findings.

## Leave a scoped result

Keep the result in the existing work.
Use a separate check note when it needs its own reader or has no suitable home.

Record:

- The subjects checked and the audits or direct checks that actually ran
- What those checks established, linking findings or stating that none were found
- Incomplete coverage and limits on independent reading
- The checked revision when later changes could make the result misleading

Save records through the native engine.
Inspect write diagnostics, requesting scoped error and warning diagnostics when absent or stale.
Repair introduced errors and assess relevant warnings before relying on the result.
Check a saved reference when its intended target remains uncertain.
