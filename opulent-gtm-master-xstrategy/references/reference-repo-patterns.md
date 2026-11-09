# Reference Repository Patterns

## Vercel Labs marketing-team-eve-template

Inspected commit: `7ccaa5f406edf179cbef4d81bcb200fd3ee9da67`

Repository: https://github.com/vercel-labs/marketing-team-eve-template

Patterns to keep:

- One lead routes to one specialist and hands back the specialist's artifact.
- One product marketer owns Brand Context; every other specialist reads it.
- Every brief is self-contained because specialists start with fresh context.
- Delegation is one level deep; specialists research and review their own work.
- Positioning, long-form content, SEO, social, and email have distinct ownership.
- Newsletters and other cross-channel work move by artifact ID, not shared hidden chat history.
- Drafting is reversible; sends, publishes, deletes, and account mutations require approval.
- Channel agents have narrowed tool surfaces; operational credentials and administrative tools are separated.
- Every prose specialist runs a surface-specific style and quality pass.

Applied to Opulent GTM:

- Strategy owns claims and offer design.
- Research owns evidence and account briefs.
- Campaign lead owns the commercial brief.
- Channel specialists adapt and execute after approval.
- Sales owns discovery, commitments, and opportunity state.
- Account memory is the shared state; only defined owners may mutate its fields.

## Browserbase skills

Inspected commit: `6afe8663693372e59e167dfa5be37932af09ae3d`

Repository: https://github.com/browserbase/skills/tree/main/skills

Patterns to keep:

- Company research and competitor analysis use explicit discover, candidate, capture, extraction, and compile stages.
- Profiles make repeat research reproducible while keeping target-specific inputs outside the core skill.
- Evidence artifacts retain URLs, screenshots or snapshots, structured fields, and failure state.
- Browser traces are used to understand dynamic interactions and promote stable calls to APIs.
- Browser-to-API tooling filters, redacts, normalizes, infers schemas, and emits a reusable interface.
- Safe-browser guidance separates browsing from secret access and narrows execution boundaries.
- Agent-experience evaluation checks real completion, tool output, silent workarounds, and narrative contradictions rather than trusting self-reports.

Applied to Opulent GTM:

- Browser research is exploratory infrastructure, not an excuse for unbounded scraping.
- Every candidate account must pass a gate before deep capture.
- Stable repeat tasks should graduate to typed, testable APIs.
- Dynamic UI claims require screenshots or traces; static facts require attributable URLs.
- Verification must compare claimed outcomes with actual connector, browser, CRM, or file effects.

## GTM engineering template deck

Source artifact: 43-slide `gtm-engineering-at-opulent-deck.pptx`, SHA-256 `b46be927998ea833f749f34d51b7d287192cb17bc0e5217d52d5308a7816304b`.

Patterns to keep:

- GTM is an engineering discipline with strategy, systems, outbound, research, data, and infrastructure.
- Delegate outcomes, not prompts.
- Use reusable company research and signal monitoring.
- Reference the signal rather than pretending to personalize.
- Keep the outbound stack minimal and modular.
- Discovery, demo, follow-up, pricing, and proof are part of the same system.
- Sell one workflow that is slow, costly, or hard to review, then prove it end-to-end.
