---
type: wks.runbook
tldr: portfolio-research runbook
status: active
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
trigger: Mandate or investment research request
audience: opulent
escalateWhen:
  - "Cost ceiling would be exceeded"
  - "Point-in-time data is unavailable"
  - "A trade or contact is requested"
relatedAutomations:
  - "[[portfolio-research-pass]]"
  - "[[forecast-review]]"
  - "[[critical-investor-modeling]]"
---
# Procedure
Fix mandate/universe/cutoff, gather evidence, run analyst skills, construct conviction-weighted views, apply risk clamps, emit signal/decision/forecast drafts and receipts.
# Verification
Every signal has analyst, asset, conviction, thesis, horizon, evidence; decisions have rationale and cost ceiling; no lookahead; hashes recompute.
# Failure branches
Missing data: UNVERIFIED, not zero. Budget refusal: log and skip. Live trade request: refuse and escalate to operator.
