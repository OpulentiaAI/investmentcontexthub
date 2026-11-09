---
type: wks.forecast
tldr: Mock forecast and scorecard receipt for the demo paper fund
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: Synthetic mock data for investor demo
subject: Watts Demo Paper Fund NAV
horizon: 90 days
method: deterministic paper tick with risk clamps
inputs:
  - research/financial-demo-data.json
  - research/demo-portfolio-mandate.md
  - signals/demo-northstar-fundamentals.md
  - signals/demo-helio-value.md
  - signals/demo-atlas-quality.md
  - signals/demo-beacon-risk.md
output: base +2.1%, stress -1.4%, no-trade if drawdown clamp breached
confidence: medium
---

# Watts Demo Paper Fund forecast

Mock forecast receipt for the demo. It is not investment advice.
