---
type: wks.automation
tldr: Historical ingest heartbeat
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: Disabled automation draft; first-open gate required
slug: historical-ingest-heartbeat
uses:
  - "[[google-workspace]]"
  - "[[microsoft-365]]"
  - "[[linkedin]]"
  - "[[hubspot]]"
  - "[[salesforce]]"
  - "[[attio]]"
  - "[[close]]"
  - "[[pipedrive]]"
  - "[[granola]]"
  - "[[fireflies]]"
  - "[[parallel]]"
  - "[[mesa]]"
schedule:
  tldr: */20 * * * *
  kind: cron
  expression: "0 7 * * 1-5"
  timezone: America/Chicago
  source: opulent-native
mode: autonomous
confirmWord: send
firstOpenChecked: "no"
enabled: "no"
costCeilingUsd: 0
producesArtifact: ingest-heartbeat-<date>.md
roleSkill: "skills/roles/ingest-heartbeat/SKILL.md"
learningLoop: "[[learning-and-issue-review]]"
playbook: "[[ingestion-playbook]]"
loopGuard: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.
---
# Overview
Historical ingest heartbeat This draft is disabled until a first-open artifact is checked and a private receipt exists.
# Prompt
```text
Create an Opulent automation named "Historical ingest heartbeat".

Trigger: weekdays at 7:00 AM America/Chicago (cron `0 7 * * 1-5`).
IMPORTANT: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.

When the automation runs, start a session with the prompt below. Everything after this line is the session prompt.

1. Read entities/source-manifest.md, entities/connection-inventory.md, and captures/source-intake-template.md.
2. Pick one pending source batch no larger than 10 items from Outlook, phone, files, CRM, meetings, or exports.
3. For each item, verify auth scope and manifest row; pull read-only bounded pages only.
4. Write hashed artifacts under private sources/, typed captures under captures/, and claim candidates under claims/.
5. Append coverage receipt and rewrite the scratchpad; commit only repository-safe files.

CAUTION: Never send, pay, publish, trade, contact a person, write back to a live CRM, or enable another automation. If live discovery fails, say so and report nothing as agreeing.
```
# Forbidden Actions
- Do not send, pay, publish, trade, contact, write back to live systems, or enable automations.
- Do not commit raw exports, credentials, phone numbers, or personal data.
- Empty results are UNVERIFIED, never zero. One extraction is not coverage.
