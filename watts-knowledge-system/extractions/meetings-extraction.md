---
type: wks.extraction
tldr: Granola / Fireflies / Zoom meetings extraction runbook
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
sourceSystem: Granola / Fireflies / Zoom meetings
accessPath: api
requiresAuth: yes
authOwner: derrick-watts
method: codemode + owner-authorized read-only meeting scopes
outputs: meeting captures, claims, decision candidates, transcript receipts
idempotency: Skip if a validated full receipt exists for the same meeting scope/date
---
# Preconditions
Owner auth, manifest row, consent/privacy boundary confirmed.
# Procedure
Pull metadata and transcripts read-only, hash, extract decisions/commitments as claims, write captures.
# Proof of delivery
Meeting counts, transcript hashes, claim rows, manifest delta.
# Do not repeat if
A validated successful run receipt exists for the same meeting scope/date.
