---
type: wks.runbook
tldr: hub-init runbook
status: active
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
trigger: First session on this hub, or whenever init-receipt.json is missing
audience: opulent
escalateWhen:
  - "A connector needs owner login"
  - "Materialize needs the confirm word"
  - "An extraction would write back to a live system"
  - "A person would be contacted"
relatedAutomations:
  - "[[source-manifest-review]]"
  - "[[connector-health-check]]"
  - "[[historical-ingest-heartbeat]]"
---
# Procedure
Treat init as resumable intake, not permission to refresh every source. Read workspace-now and connection-inventory. Validate, dry-run materialize, extract only authorized sources, populate graph shelves, create disabled automations, write init-receipt.json.
# Verification
Every connected source has a manifest row and dated receipt or explicit UNVERIFIED gap; contacts/suppression preserved; automations disabled; hashes recompute; no send/trade/contact.
# Failure branches
Connector count 0 after settings page says on: trust live count, record it, do not extract. Materialize without confirm: preview only. First-open tick invents a row: fail the tick.
