---
type: wks.automation
tldr: Connector health check
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: Disabled automation draft; first-open gate required
slug: connector-health-check
uses:
  - "[[google-workspace]]"
  - "[[microsoft-365]]"
  - "[[linkedin]]"
  - "[[hubspot]]"
  - "[[salesforce]]"
  - "[[attio]]"
  - "[[close]]"
  - "[[pipedrive]]"
  - "[[notion]]"
  - "[[slack]]"
  - "[[teams]]"
  - "[[granola]]"
  - "[[fireflies]]"
  - "[[crunchbase]]"
  - "[[pitchbook]]"
  - "[[affinity]]"
  - "[[apollo]]"
  - "[[clay]]"
  - "[[instantly]]"
  - "[[lemlist]]"
  - "[[smartlead]]"
  - "[[anysite]]"
  - "[[crustdata]]"
  - "[[contextdev]]"
  - "[[deepline]]"
  - "[[parallel]]"
  - "[[mesa]]"
schedule:
  tldr: 0 9 * * 1-5
  kind: cron
  expression: "0 9 * * 1-5"
  timezone: America/Chicago
  source: opulent-native
mode: read-only
confirmWord: send
firstOpenChecked: "no"
enabled: "no"
costCeilingUsd: 0
producesArtifact: connector-health-<date>.md
roleSkill: "skills/roles/source-review/SKILL.md"
learningLoop: "[[learning-and-issue-review]]"
playbook: "[[ingestion-playbook]]"
loopGuard: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.
---
# Overview
Connector health check This draft is disabled until a first-open artifact is checked and a private receipt exists.
# Prompt
```text
Create an Opulent automation named "Connector health check".

Trigger: weekdays at 9:00 AM America/Chicago (cron `0 9 * * 1-5`).
IMPORTANT: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.

When the automation runs, start a session with the prompt below. Everything after this line is the session prompt.

1. Read entities/connection-inventory.md and entities/source-manifest.md.
2. Check read-only capability surfaces for connected/pending/error state.
3. Write connector-health-<date>.md with connector, state, blocker note, and UNVERIFIED where live reach is not proved.
4. Log connectors checked and blockers named.

CAUTION: Never send, pay, publish, trade, contact a person, write back to a live CRM, or enable another automation. If live discovery fails, say so and report nothing as agreeing.
```
# Forbidden Actions
- Do not extract payloads, send, pay, publish, trade, contact, or enable automations.
- Do not mark a connector connected without read-only proof.
- Do not store credentials or personal data in the repository.
