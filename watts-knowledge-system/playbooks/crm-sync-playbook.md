---
type: wks.playbook
tldr: CRM sync playbook
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
role: crm-steward
module: crm sync
inputs: connected CRM read-only snapshot, manifest row, suppression surface
nextOwner: knowledge-weaver
relatedSkill: skills/weave-knowledge/SKILL.md
---
# Job
Reconcile CRM state into entities/claims without write-back.
# Process
1. Verify owner scope. 2. Pull bounded read-only records. 3. Normalize to org/person/account concepts. 4. Preserve suppression and do-not-contact.
# Output
CRM capture, entity deltas, and coverage receipt.
# Guardrails
No CRM write-back, no outreach, no invented contact fields.
