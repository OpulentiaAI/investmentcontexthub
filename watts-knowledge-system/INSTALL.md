# Install WattsKnowledgeSystem

This repository is self-contained: the arsumbris engine, host, MCP, type system, and Opulent knowledge materials are vendored beside `watts-knowledge-system/`.

1. Open the workspace member `watts-knowledge-system/` in au-host, or run the bundled au-engine from the repository root.
2. Read `AGENTS.md`, then `docs/onboarding.md`, then `skills/opulent-onboarding/SKILL.md`.
3. Run `python3 watts-knowledge-system/scripts/validate.py --catalog`.
4. Install into Opulent only through `scripts/materialize.py` dry-run first; `--apply` requires `CONFIRM=send` and private owner/workspace bindings.

No provider account, CRM, mailbox, phone export, or broker is connected by installation.
