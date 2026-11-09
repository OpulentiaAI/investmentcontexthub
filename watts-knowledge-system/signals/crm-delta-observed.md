---
type: wks.signal
tldr: crm-delta-observed signal
status: active
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: Investment knowledge signal scaffold
rank: 3
sourceSystems: [hubspot, salesforce, attio, close, pipedrive, affinity]
query: "CRM delta with suppression preserved"
citationRequirement: "CRM run receipt and entity deltas"
decayDays: 7
falsePositives: [C, R, M,  , U, I,  , s, c, r, e, e, n, s, h, o, t, ,,  , u, n, s, c, o, p, e, d,  , e, x, p, o, r, t, ,,  , m, i, s, s, i, n, g,  , s, u, p, p, r, e, s, s, i, o, n,  , r, o, w, s]
openerAngle: "Reconcile entities before any outreach or investment workflow."

---
# How to detect
Delta run names continuingFrom, counts, hashes, and suppression rows.
# How to disqualify
Write-back attempts, invented contact fields, or suppression loss.
