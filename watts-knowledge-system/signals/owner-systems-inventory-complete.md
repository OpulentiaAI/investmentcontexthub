---
type: wks.signal
tldr: owner-systems-inventory-complete signal
status: active
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: Investment knowledge signal scaffold
rank: 1
sourceSystems: [google-workspace, microsoft-365, linkedin, hubspot, salesforce, attio, close, pipedrive, notion, slack, granola, fireflies, phone-export, files-export]
query: "Owner-confirmed systems inventory with read-only observations"
citationRequirement: "Owner confirmation or read-only capability receipt"
decayDays: 30
falsePositives: [a,  , c, o, n, n, e, c, t, o, r,  , s, e, t, t, i, n, g, s,  , p, a, g, e, ,,  , a,  , s, t, a, l, e,  , m, a, n, i, f, e, s, t,  , r, o, w]
openerAngle: "Convert the verified inventory gap into the next owner ask."

---
# How to detect
A manifest row moves from pending to extracted only with a validated run receipt.
# How to disqualify
Settings pages, stale rows, or one source's extraction standing in for coverage.
