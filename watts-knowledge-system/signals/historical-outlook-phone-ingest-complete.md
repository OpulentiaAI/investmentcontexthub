---
type: wks.signal
tldr: historical-outlook-phone-ingest-complete signal
status: active
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: Investment knowledge signal scaffold
rank: 2
sourceSystems: [google-workspace, microsoft-365, phone-export, files-export]
query: "Historical Outlook/phone/files exports hashed and woven"
citationRequirement: "Artifact sha256, capture rows, manifest receipt"
decayDays: 14
falsePositives: [a, n,  , e, x, p, o, r, t,  , f, i, l, e,  , p, r, e, s, e, n, t,  , w, i, t, h, o, u, t,  , r, e, c, e, i, p, t, ,,  , a,  , p, a, r, t, i, a, l,  , p, a, g, i, n, a, t, i, o, n,  , c, l, a, i, m]
openerAngle: "Prioritize the next un-ingested historical source."

---
# How to detect
Captures cite sourceSystem and sha256; manifest records FULL/PARTIAL/UNKNOWN.
# How to disqualify
File presence alone, un-hashed exports, or personal data committed to git.
