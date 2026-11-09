# Watts financial-analysis demo

## Purpose

Show the Watts Knowledge System powering a COR-style financial analysis presentation from synthetic mock data inside the real arsumbris workspace.

## Run of show

1. Launch or reuse au-host with `AU_ENTRY=/home/ubuntu/repos/investmentcontexthub/watts-knowledge-system`.
2. Verify daemon/engine readiness and open `workspace-layout.yaml`.
3. Open `start here.md`, `entities/workspace-now.md`, `entities/connection-inventory.md`, and `entities/source-manifest.md`.
4. Show the typed mock investment layer: `research/demo-portfolio-mandate.md`, the four `signals/demo-*.md` files, the four `research/demo-decision-*.md` files, and `research/demo-forecast.md`.
5. Run `python3 scripts/render_financial_deck.py` from `watts-knowledge-system`.
6. Open `research/financial-analysis-demo.html` in Chrome or the desktop viewer and walk the four slides.
7. Show `research/financial-analysis-demo-message.txt` as the report receipt.

## Proof checklist

- Engine lifecycle ready and composition mounted.
- Mock data labeled MOCK in JSON, deck, and message.
- Position weights plus cash equal ~100%; sector weights equal ~100%.
- Four slides render: efficiency, exposure, signals/forecasts, decisions.
- No live trading, sends, contact, payments, publishing, or automation enablement.

## Recording notes

Record the desktop while driving au-host and the rendered deck. Keep the mock disclaimer visible. If engine diagnostics or MCP status are imperfect, state them as caveats rather than hiding them.
