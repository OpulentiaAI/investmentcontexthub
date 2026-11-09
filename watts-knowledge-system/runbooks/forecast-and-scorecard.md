---
type: wks.runbook
tldr: forecast-and-scorecard runbook
status: active
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
trigger: Forecast review or strategy scoring
audience: opulent
escalateWhen:
  - "Receipt chain is broken"
  - "Sample size is too small"
  - "Leakage or lookahead is suspected"
relatedAutomations:
  - "[[forecast-review]]"
---
# Procedure
Read forecast/decision/ledger receipts, recompute metrics, compare benchmark, flag leakage/decay, append review artifact.
# Verification
Metrics recomputed from receipts; every forecast has inputs/method/horizon; promotion remains blocked without validation receipt.
# Failure branches
Missing receipts: mark UNKNOWN. Broken hash chain: halt scoring and escalate. Small sample: report uncertainty, do not promote.
