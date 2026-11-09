---
type: wks.runbook
tldr: operate-the-hub runbook
status: active
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
trigger: Routine hub operation or automation health
audience: opulent
escalateWhen:
  - "Enabled automation found"
  - "Source manifest drift is material"
  - "Cost ceiling refusal repeats"
relatedAutomations:
  - "[[connector-health-check]]"
  - "[[source-manifest-review]]"
  - "[[forecast-review]]"
---
# Procedure
Read workspace-now, connection-inventory, source-manifest, catalogs, and recent receipts. Run validators and dry-run inspectors. Report drift, blockers, and UNVERIFIED gaps. Route accepted `wks.learning` and `wks.issue` candidates through [[learning-and-issue-review]]; a separately approved hub patch plus hashed post-change check is required — not resolution without a hashed post-change check.
# Verification
validate.py clean or errors owned; catalogs regenerated; no enabled automation without first-open receipt; no live writes.
# Failure branches
Validator errors: fix owned files before adding. Live discovery fails: say so, report nothing as agreeing. Enabled draft found: disable and escalate.
