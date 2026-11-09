---
type: wks.playbook
tldr: ingestion playbook
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: WattsKnowledgeSystem scaffold
role: source-steward
module: ingestion
inputs: owner-authorized source, manifest row, private sources/ landing zone
nextOwner: knowledge-weaver
relatedSkill: skills/ingest-source/SKILL.md

---
# Job
Ingest one owner system into private raw storage and typed captures without exposing payloads.
# Process
1. Verify manifest row and auth scope. 2. Pull read-only in bounded pages. 3. Hash artifacts. 4. Write capture/claim candidates. 5. Record receipt.
# Output
Hashed capture artifacts, manifest delta, and UNVERIFIED gaps.
# Guardrails
No send/pay/publish/trade/contact. Raw payloads stay in sources/. Empty results are UNVERIFIED.
