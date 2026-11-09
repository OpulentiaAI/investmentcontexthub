---
type: wks.automation
tldr: Critical investor modeling
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: Disabled automation draft; first-open gate required
slug: critical-investor-modeling
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
  tldr: 0 14 * * 4
  kind: cron
  expression: "0 14 * * 1"
  timezone: America/Chicago
  source: opulent-native
mode: draft-then-wait
confirmWord: send
firstOpenChecked: "no"
enabled: "no"
costCeilingUsd: 2
producesArtifact: investor-model-<date>.md
roleSkill: "skills/roles/critical-modeling/SKILL.md"
learningLoop: "[[learning-and-issue-review]]"
playbook: "[[critical-analysis-playbook]]"
loopGuard: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.
---
# Overview
Critical investor modeling This draft is disabled until a first-open artifact is checked and a private receipt exists.
# Prompt
```text
Create an Opulent automation named "Critical investor modeling".

Trigger: Monday at 2:00 PM America/Chicago (cron `0 14 * * 1`).
IMPORTANT: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.

When the automation runs, start a session with the prompt below. Everything after this line is the session prompt.

1. Read investment signals, forecasts, portfolio research, and investor/relationship entities.
2. Select one seed opportunity or investor-modeling question with evidence in hand.
3. State thesis and falsifier; steelman and attack; check incentives, freshness, concentration, liquidity, and disconfirming evidence.
4. Write investor-model-<date>.md as a decision draft with explicit uncertainty and UNVERIFIED gaps.
5. Append review receipt; no external contact or live action.

CAUTION: Never send, pay, publish, trade, contact a person, write back to a live CRM, or enable another automation. If live discovery fails, say so and report nothing as agreeing.
```
# Forbidden Actions
- Do not provide investment advice as fact, trade, send, pay, publish, contact, or write to CRM.
- Do not invent investor beliefs; model only from cited public/private evidence.
- Every recommendation is a draft requiring human review.
