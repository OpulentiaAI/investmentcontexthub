---
type: wks.extraction
tldr: Investment research sources: Crunchbase, PitchBook, Affinity, Anysite, Crustdata, Context.dev, Parallel, Mesa extraction runbook
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
sourceSystem: Investment research sources: Crunchbase, PitchBook, Affinity, Anysite, Crustdata, Context.dev, Parallel, Mesa
accessPath: mcp
requiresAuth: yes
authOwner: derrick-watts
method: read-only MCP/native/API calls within costCeilingUsd
outputs: investment signals, forecasts, evidence receipts
idempotency: Skip if validated receipt exists for same mandate/universe/date
---
# Preconditions
Owner auth, manifest row, cost ceiling, point-in-time cutoff.
# Procedure
Free/read-only first, bounded paid calls only within ceiling, cite every fact, hash outputs.
# Proof of delivery
Signal/decision/forecast files, evidence rows, spend ledger, UNVERIFIED gaps.
# Do not repeat if
Validated receipt exists for same mandate/universe/date or budget guard refuses.
