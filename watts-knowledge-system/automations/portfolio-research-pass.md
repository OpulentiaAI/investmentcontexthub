---
type: wks.automation
tldr: Portfolio research pass
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: Disabled automation draft; first-open gate required
slug: portfolio-research-pass
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
  tldr: 0 10 * * 3
  kind: cron
  expression: "0 10 * * 1"
  timezone: America/Chicago
  source: opulent-native
mode: draft-then-wait
confirmWord: send
firstOpenChecked: "no"
enabled: "no"
costCeilingUsd: 5
producesArtifact: portfolio-research-<date>.md
roleSkill: "skills/roles/portfolio-research/SKILL.md"
learningLoop: "[[learning-and-issue-review]]"
playbook: "[[portfolio-research-playbook]]"
loopGuard: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.
---
# Overview
Portfolio research pass This draft is disabled until a first-open artifact is checked and a private receipt exists.
# Prompt
```text
Create an Opulent automation named "Portfolio research pass".

Trigger: Monday at 10:00 AM America/Chicago (cron `0 10 * * 1`).
IMPORTANT: Stop only if the same automation role, scope, inputs and cycle have a validated successful artifact and run receipt; check current prerequisites and eligibility before skipping; upstream artifacts also require validated successful run receipts for the relevant cycle.

When the automation runs, start a session with the prompt below. Everything after this line is the session prompt.

1. Read portfolio mandates, investment signals, forecasts, and scorecard receipts.
2. Refresh point-in-time data for one mandate/universe batch through read-only sources.
3. Run analyst skills to emit conviction + thesis with citations; construct views and apply risk clamps.
4. Write investment-signal, investment-decision, and forecast candidates as drafts.
5. Append cost ledger and UNVERIFIED gaps; stop before any live trade or contact.

CAUTION: Never send, pay, publish, trade, contact a person, write back to a live CRM, or enable another automation. If live discovery fails, say so and report nothing as agreeing.
```
# Forbidden Actions
- Do not trade live, send, pay beyond costCeilingUsd, publish, contact, or write to a broker.
- No lookahead; point-in-time data only. LLM forms views; deterministic code sizes and records.
- Every factual claim needs a resolvable source or UNVERIFIED.
