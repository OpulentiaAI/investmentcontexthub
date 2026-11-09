---
type: wks.runbook
tldr: multi-source-delta-ingest runbook
status: active
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
trigger: New owner export or connector delta arrives
audience: opulent
escalateWhen:
  - "Raw export contains credentials or personal data"
  - "Source auth is ambiguous"
  - "Pagination cannot be proven complete"
relatedAutomations:
  - "[[historical-ingest-heartbeat]]"
  - "[[source-manifest-review]]"
---
# Procedure
Add manifest row first, land raw bytes in private sources/, compute sha256, run bounded read-only extraction, write captures/claims, append receipt, update manifest only with proof.
# Verification
Artifact hashes recompute; capture rows link to sourceSystem; manifest distinguishes FULL/PARTIAL/UNKNOWN; no raw payload committed.
# Failure branches
Ambiguous auth: mark unavailable with blocker note. Partial pagination: mark PARTIAL, never FULL. Duplicate sha256: skip as no-op success.
