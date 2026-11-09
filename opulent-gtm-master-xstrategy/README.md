---
type: "au.engine.readme::au-engine"
tldr: "Published GTM master strategy package — SKILL.md, operating sequence, use-case catalog, contracts, PII-safe workbook profile, and strategy PDF."
---

# Repo Overview

## What this is

The published Opulent GTM master strategy package (private repo `OpulentiaAI/opulent-gtm-master-xstrategy`): a self-contained skill — SKILL.md, operating sequence, account/campaign contracts, 44-use-case catalog, PII-safe Diego workbook profile, Field Theory corpus evidence, and the strategy PDF.

## How to use this

Start at `SKILL.md`, then `references/operating-sequence.md`. Evidence lives in `research/evidence/`; the final artifact is `artifacts/opulent-gtm-master-xstrategy.pdf`. Validate with `python3 scripts/validate_skill.py`.

## How to extend this

Workbook originals stay local-only under `source-pack/diego/` (gitignored); only PII-safe aggregates belong in `research/evidence/`. Re-run `scripts/profile_workbooks.py` after refreshing workbook sources.

# Opulent GTM Master XStrategy

An isolated, self-contained GTM strategy package. It is intentionally not installed under `frontend/`, `templates/convex-nextjs/`, `.agent/skills/`, or `.agents/skills/`.

## Package layout

- `SKILL.md` - reusable operating skill
- `references/` - PII-safe strategy, sequencing, source synthesis, use-case catalog, contracts, and scorecards
- `scripts/` - corpus collection, use-case extraction, workbook profiling, PDF build, and package validation
- `source-pack/` - GTM engineering source deck plus a local-only, gitignored `diego/` directory for sensitive workbook originals
- `research/evidence/` - generated PII-safe profiles and Field Theory corpus snapshots
- `research/repositories/` - pinned clones of the Vercel eve template and Browserbase skills
- `artifacts/` - final strategy PDF

## Validate

```bash
python3 scripts/validate_skill.py
```

## Build the PDF

```bash
python3 scripts/build_strategy_pdf.py
```

## Refresh the live use-case catalog

```bash
python3 scripts/extract_opulent_use_cases.py
python3 scripts/build_strategy_pdf.py
python3 scripts/validate_skill.py
```

The extractor preserves the site-published category, featured status, capability tags, title, summary, and URL. It adds deterministic editorial GTM labels for buyer group, value motion, lifecycle stage, and portfolio role. Those two label layers remain separate in both JSON and Markdown.

Run commands from this directory. The package uses only package-relative paths and does not require the Convex or Next.js runtime.

## Data boundary

The raw Excel files contain direct identifiers, LinkedIn URLs, email addresses, and personalized messages. They remain local under the gitignored `source-pack/diego/` directory and must never be committed. The versioned skill references, PII-safe profiles, and PDF contain only aggregates and source descriptions.

## Installation policy

Do not copy this package into the Convex/Next.js template. If an agent needs it, point the agent to this isolated `SKILL.md` or install a copy into that agent's own user-level skill directory after an explicit decision.
