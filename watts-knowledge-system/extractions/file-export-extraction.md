---
type: wks.extraction
tldr: Owner file/phone/AI-chat exports extraction runbook
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
sourceSystem: Owner file/phone/AI-chat exports
accessPath: export
requiresAuth: no
authOwner: derrick-watts
method: owner-delivered export to private sources/ then local ingest
outputs: captures, claims, entities, source-manifest receipt
idempotency: Skip if artifact sha256 already ingested for same export
---
# Preconditions
Export delivered to sources/, manifest row, no credentials committed.
# Procedure
Inventory files, compute hashes, parse bounded text, write captures/claims, receipt.
# Proof of delivery
File counts, sha256 manifest, capture rows, coverage gaps.
# Do not repeat if
Artifact sha256 already has a validated ingestion receipt.
