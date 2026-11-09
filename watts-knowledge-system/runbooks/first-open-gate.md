---
type: wks.runbook
tldr: first-open-gate runbook
status: active
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
trigger: Before any automation is enabled or materialized
audience: operator
escalateWhen:
  - "Artifact cannot be opened"
  - "Cost exceeds ceiling"
  - "Receipt hash mismatch"
relatedAutomations:
  - "[[source-manifest-review]]"
  - "[[connector-health-check]]"
  - "[[historical-ingest-heartbeat]]"
  - "[[portfolio-research-pass]]"
  - "[[forecast-review]]"
  - "[[critical-investor-modeling]]"
---
# Procedure
Open the produced artifact, verify automationSlug/status/openedBy/openedAt/effects/cost/artifactSha256, then record private receipt. Only after that may an operator consider enablement.
# Verification
Receipt validates against scripts/readiness.py and validate.py; artifact hash recomputes; effects list is empty for read-only/draft runs.
# Failure branches
Missing artifact: fail closed. Cost over ceiling: fail closed. Any effect: fail closed and escalate.
