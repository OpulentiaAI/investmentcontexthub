# Onboarding Derrick Watts's systems

Goal: persistently ingest Derrick's current information from historical Outlook, phone, files, CRM, meeting notes, and public research into a personalized context hub.

1. Confirm scope and privacy boundaries. Raw exports stay in `sources/` and are never committed.
2. Connect read-only sources one at a time. Record each in `entities/source-manifest.md` before extraction.
3. Run the matching extraction runbook under `watts-knowledge-system/extractions/`; write hashed artifacts and receipts.
4. Weave captures into `entities/`, `concepts/`, `claims/`, and `maps/` with stated/observed/inferred provenance.
5. Seed investment workflows from `skills/portfolio-research`, `skills/forecast-review`, and `skills/critical-modeling`.
6. Keep every automation disabled until a first-open artifact is checked and a private receipt exists.
