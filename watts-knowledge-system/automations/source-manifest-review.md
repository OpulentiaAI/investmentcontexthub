---
type: wks.automation
tldr: Review source manifest drift
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: Disabled automation draft; first-open gate required
slug: watts-source-manifest-review
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
  - "[[granola]]"
  - "[[fireflies]]"
  - "[[anysite]]"
  - "[[crustdata]]"
  - "[[contextdev]]"
  - "[[parallel]]"
  - "[[mesa]]"
schedule:
  tldr: 0 8 * * 1
  kind: cron
  expression: "0 8 * * 1"
  timezone: America/Chicago
  source: opulent-native
mode: read-only
confirmWord: send
firstOpenChecked: "no"
enabled: "no"
costCeilingUsd: 1
producesArtifact: source-manifest-review-<date>.md
roleSkill: "skills/roles/source-review/SKILL.md"
learningLoop: "[[learning-and-issue-review]]"
playbook: "[[ingestion-playbook]]"
loopGuard: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.
---
# Overview
Review source manifest drift This draft is disabled until a first-open artifact is checked and a private receipt exists.
# Prompt
```text
Create an Opulent automation named "Review source manifest drift".

Trigger: Monday at 8:00 AM America/Chicago (cron `0 8 * * 1`).
IMPORTANT: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.

When the automation runs, start a session with the prompt below. Everything after this line is the session prompt.

1. Read entities/source-manifest.md and entities/connection-inventory.md.
2. Read the owner-bound native installed integration catalog read-only.
3. Report observed identities absent from the manifest and manifest rows lacking proof.
4. Write source-manifest-review-<date>.md with sourceId, manifest state, observed state UNVERIFIED unless proved, drift or UNVERIFIED, and blocker notes.
5. Log rows compared, drifts found, rows still unproved.

CAUTION: Never send, pay, publish, trade, contact a person, write back to a live CRM, or enable another automation. If live discovery fails, say so and report nothing as agreeing.
```
# Forbidden Actions
- Do not extract, re-extract, re-auth, materialize, send, pay, publish, trade, or contact.
- Do not edit the manifest; report drift and stop.
- Do not treat one source's presence as coverage of another.
