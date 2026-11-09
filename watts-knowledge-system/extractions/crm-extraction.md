---
type: wks.extraction
tldr: CRM set: HubSpot, Salesforce, Attio, Close, Pipedrive extraction runbook
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
sourceSystem: CRM set: HubSpot, Salesforce, Attio, Close, Pipedrive
accessPath: api
requiresAuth: yes
authOwner: derrick-watts
method: codemode + owner-authorized read-only CRM scopes
outputs: org/person/account captures, suppression surface, CRM receipt
idempotency: Skip if a validated full receipt exists for the same CRM scope/date
---
# Preconditions
Owner auth, manifest row, suppression surface read first, no write scopes exercised.
# Procedure
Resolve identities before enrichment, pull bounded read-only records, normalize, preserve suppression/do-not-contact, hash, receipt.
# Proof of delivery
Record counts by object, artifact hashes, suppression rows preserved, manifest delta.
# Do not repeat if
A validated successful run receipt exists for the same CRM scope/date.
