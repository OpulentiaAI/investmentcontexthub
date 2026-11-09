---
type: wks.runbook
tldr: critical-investor-modeling runbook
status: active
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
trigger: Investor or seed-decision analysis requested
audience: opulent
escalateWhen:
  - "Evidence is stale or unverifiable"
  - "Incentives or conflicts are material"
  - "A recommendation would be treated as advice"
relatedAutomations:
  - "[[critical-investor-modeling]]"
  - "[[portfolio-research-pass]]"
---
# Procedure
State thesis/falsifier, steelman and attack, check freshness/incentives/concentration/liquidity/disconfirming evidence, emit decision draft with uncertainty.
# Verification
Memo cites sources, names UNVERIFIED gaps, includes disconfirming evidence, and states it is not investment advice.
# Failure branches
No evidence: do not model. Conflicting evidence: keep both. Human asks for live action: refuse and escalate.
