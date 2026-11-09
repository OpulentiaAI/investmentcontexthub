---
type: wks.extraction
tldr: Google Workspace / Outlook / Calendar / Drive extraction runbook
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
sourceSystem: Google Workspace / Outlook / Calendar / Drive
accessPath: api
requiresAuth: yes
authOwner: derrick-watts
method: codemode + owner-authorized OAuth read-only scopes
outputs: captures, claims, entities, source-manifest receipt
idempotency: Skip if a validated full receipt exists for the same scope/date; delta runs continue from lastRun
---
# Preconditions
Owner auth, manifest row, private sources/ landing zone, read-only scopes.
# Procedure
Discover tools, inventory counts, pull bounded pages, normalize, hash, write captures and receipt.
# Proof of delivery
File counts, artifact rows, recomputed sha256, and manifest state delta.
# Do not repeat if
A validated successful run receipt exists for the same automation role, scope, inputs and cycle.
