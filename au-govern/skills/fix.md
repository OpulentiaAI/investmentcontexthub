---
type: mcp.skill::au-mcp-sdk
name: fix
description: Repairs open findings on a knowledge graph, checks the repair against their doctrine, and records resolution. Use when the findings worklist needs draining or the human asks to resolve recorded findings. Check owns discovering semantic defects. General code fixes and unrecorded bug reports stay with their own workflows. Acceptance and dismissal require the human's ruling.
---

# fix

Repair each scoped [[finding.open]] by correcting its subject.
Demonstrate that the violated doctrine now holds.
Keep the repair evidence and disposition on each finding.
[[check]] owns independent semantic sweeps.

## Choose the repair

Use the finding's subject and breaks to judge the defect against its evidence.
Reuse current reads until relevant state changes or freshness is uncertain.
When the worklist is unknown or stale, query au_instances_of with ofType: finding.open::au-govern.
Follow every page before claiming the worklist is complete.

Prioritize repairs by their effect on the affected work.
Inspect incoming references when a repair may change what referring notes mean.

**Human-authored text**

Use the human's existing authorization when their words need changing.
Without that authorization, return the proposed change for a ruling.
Do not alter their words merely to make the check pass.

**Identity and location**

Use [[reshape-with-the-engine::au-agent-guides]] for changes to identities or locations.
Choose the operation for its supported effects on references.

For a successor, follow [[supersede::au-agent-guides]].
Existing links still reach the old note.
The engine neither redirects them nor follows the successor chain automatically.
Carry only relations the successor still supports.
Check that readers can reach the required history and usable successor.
Explain any deliberate reference migration.

## Demonstrate the repair

Repeat the check that exposed the defect.
Use the audit named by caught_by, or the documented direct check when no audit produced the finding.
Do not invent an audit to close the record.

Keep the repair and observed result on the finding.
If the defect remains or the check cannot be completed, leave it open with the remaining work.
Repeat only checks affected by a further change.

## Record the disposition

Use [[finding.resolved]] after the repair has passed its check.
Describe the repair in resolution.
Keep the supporting evidence in the body.

Apply a human ruling for either other terminal state:

- [[finding.accepted]] records a real deviation the human chooses to retain
- [[finding.dismissed]] records a false alarm and any needed correction to the audit or its application

Use a ruling already given.
Keep the finding open while a required ruling is outstanding.

Write through the native engine.
When changing the lifecycle claim, preserve other claims, fields and evidence.
Read back the changed claims and required fields when the write result does not show them.
Inspect write diagnostics, requesting scoped error and warning diagnostics when absent or stale.
Repair introduced errors and assess relevant warnings before relying on the disposition.
A successful write alone does not establish a valid transition.
Never delete a finding.
