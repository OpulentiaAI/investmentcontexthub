# Use case: Watts au-host investor demo

Purpose: show Derrick Watts that the Watts Knowledge System is a live, persistent, typed workspace — not a slide deck. The agent drives au-host autonomously and records the run.

## Run of show

1. **Launch proof** — au-host opens directly into `watts-knowledge-system`; daemon and engine are `ready`.
2. **Workspace proof** — open `start here.md`, then the source-manifest and connection-inventory tabs so the coverage model is visible.
3. **Live ingestion proof** — create `captures/demo-owner-export.md` as a synthetic `wks.capture`; the engine file index and desktop tree/graph pick it up without a restart.
4. **Research backbone proof** — open portfolio-research, forecast-scorecard, and automation-dictionary tabs; everything remains draft/research-only.
5. **Governance proof** — show automations are still disabled/dry-run and no real account is connected.

## Agent procedure

Follow `skills/autonomous-demo/SKILL.md` and `playbooks/autonomous-au-host-demo.md`. Use CDP `window.main` calls for verification; use the desktop recording for the human-visible proof.

## Proof checklist

- `window.main.app.initialEntry()` returns the Watts workspace.
- `daemon.status` → `running: true`, probe `ready: true`.
- `engine.read(lifecycle)` → `ok: true`, `ready: true`.
- `recents.listCompositions` includes `workspace-layout.yaml`.
- Demo capture appears in `engine.read(files)` as `kind: instance` and `files.read` returns a hash.
- Diagnostics scoped to the demo file are empty.
- Validation/tests remain green if repo files changed.

## Recording notes

- Record the desktop, not the terminal, for the investor-facing cut.
- Keep the synthetic capture on screen only long enough to prove the engine index update.
- If MCP is not listening, keep it in the report as a blocker; do not hide it.
