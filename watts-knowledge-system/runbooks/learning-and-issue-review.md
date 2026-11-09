---
type: wks.runbook
tldr: Review accepted learnings and issues with hashed post-change proof
status: active
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
trigger: Weekly or after any accepted wks.learning / wks.issue candidate
audience: opulent
escalateWhen:
  - "A learning would change safety, compliance, spend, or contact rules"
  - "An issue lacks a baseline, window, or post-change verification"
relatedAutomations:
  - "[[source-manifest-review]]"
  - "[[connector-health-check]]"
  - "[[historical-ingest-heartbeat]]"
  - "[[portfolio-research-pass]]"
  - "[[forecast-review]]"
  - "[[critical-investor-modeling]]"
---

# Procedure
1. Read `wks.learning` and `wks.issue` candidates plus their evidence receipts.
2. Independently review each candidate; accept only sourced, scoped, non-duplicative items.
3. For accepted items, require a separately approved hub patch and a hashed post-change check.
4. Record rejected items with reasons; resolution without a hashed post-change check is not resolution.

# Verification
Every accepted learning has source SHA-256, reviewer receipt, patch reference, and post-change verification hash. Every issue has window, baseline, and verification proof.

# Failure branches
Missing receipt: leave candidate pending. Conflicting evidence: keep both and escalate. Safety/compliance change: require operator approval before patching.
