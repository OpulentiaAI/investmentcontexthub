---
type: wks.playbook
tldr: autonomous au-host investor demo playbook
status: draft
owner: Derrick Watts
updated: 2026-11-09
surface: watts
provenance: Adapted from devin-cor-skill for the Watts investor demo
role: autonomous-demo-driver
module: au-host demo
inputs:
  - au-host desktop
  - watts workspace
  - synthetic demo source
nextOwner: operator
relatedSkill: skills/autonomous-demo/SKILL.md
---
# Job
Produce a short recordable investor demo in which an agent autonomously drives the Watts Knowledge System in au-host and proves live ingestion without external side effects.
# Process
1. Launch/reuse au-host with `AU_ENTRY=/home/ubuntu/repos/investmentcontexthub/watts-knowledge-system` and verify daemon, engine lifecycle, composition, and diagnostics baseline.
2. Record the desktop and open `start here.md`, `entities/source-manifest.md`, and `entities/connection-inventory.md`.
3. Create one synthetic `wks.capture` demo artifact, verify it appears in `engine.read(files)` and `files.read`, then show the file tree/graph update.
4. Open the portfolio-research, forecast-scorecard, and automation-dictionary tabs to show the research backbone stays draft/research-only.
5. Stop recording, run validation if files changed, and report proof plus blockers.
# Output
A recording, a synthetic demo capture draft, engine verification receipt, and a concise report message.
# Guardrails
Synthetic/private demo data only; no real systems, sends, trades, contact, payments, publishing, or automation enablement; cite or UNVERIFIED; fail closed.
