---
type: wks.automation
tldr: Forecast and scorecard review
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: Disabled automation draft; first-open gate required
slug: forecast-review
uses:
  - "[[crunchbase]]"
  - "[[pitchbook]]"
  - "[[affinity]]"
  - "[[anysite]]"
  - "[[crustdata]]"
  - "[[contextdev]]"
  - "[[parallel]]"
  - "[[mesa]]"
schedule:
  tldr: 0 11 * * 5
  kind: cron
  expression: "0 11 * * 1"
  timezone: America/Chicago
  source: opulent-native
mode: read-only
confirmWord: send
firstOpenChecked: "no"
enabled: "no"
costCeilingUsd: 1
producesArtifact: forecast-review-<date>.md
roleSkill: "skills/roles/forecast-review/SKILL.md"
learningLoop: "[[learning-and-issue-review]]"
playbook: "[[forecast-review-playbook]]"
loopGuard: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.
---
# Overview
Forecast and scorecard review This draft is disabled until a first-open artifact is checked and a private receipt exists.
# Prompt
```text
Create an Opulent automation named "Forecast and scorecard review".

Trigger: Monday at 11:00 AM America/Chicago (cron `0 11 * * 1`).
IMPORTANT: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.

When the automation runs, start a session with the prompt below. Everything after this line is the session prompt.

1. Read forecast receipts, investment decisions, and scorecard history.
2. Recompute hit rate, slugging, information coefficient, calibration, and benchmark delta.
3. Flag leakage, decay, small samples, and missing receipts.
4. Write forecast-review-<date>.md with recomputed metrics and promotion blockers.

CAUTION: Never send, pay, publish, trade, contact a person, write back to a live CRM, or enable another automation. If live discovery fails, say so and report nothing as agreeing.
```
# Forbidden Actions
- Do not promote strategies, trade, send, pay, publish, contact, or edit mandates.
- No forecast is valid without inputs, method, horizon, and receipt.
- completed is not proof; recompute hashes and counts.
