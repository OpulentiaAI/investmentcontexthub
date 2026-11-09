# Account and Campaign Contracts

## Normalized account record

Required fields:

- `account_id`
- `company_name`
- `company_domain`
- `person_id`
- `person_name`
- `role_title`
- `linkedin_url`
- `work_email`
- `relationship_owner`
- `relationship_strength`
- `segment`
- `use_case`
- `use_case_source_url`
- `use_case_site_category`
- `use_case_capability_tags`
- `use_case_buyer_group`
- `use_case_value_motion`
- `use_case_lifecycle_stage`
- `use_case_portfolio_role`
- `fit_reason`
- `fit_confidence`
- `signal_type`
- `signal_summary`
- `signal_observed_at`
- `signal_expires_at`
- `evidence_urls`
- `source_workbook`
- `source_row_id`
- `dedupe_key`
- `consent_or_channel_basis`
- `next_action`
- `next_action_owner`
- `status`
- `exclusion_reason`

Direct identifiers belong in access-controlled records. Reusable reports use counts, distributions, and anonymous examples.

## Deduplication order

1. Exact normalized LinkedIn URL.
2. Exact normalized work email.
3. Normalized full name plus resolved company domain.
4. Human review for ambiguous matches.

Never collapse two people using name alone. Preserve every original row in a source-link table.

## Research contract

### Discover

Collect only candidate URLs and source types. Prefer official company pages, filings, job pages, product docs, partner pages, and attributable interviews.

### Gate

Require relevance to the wedge, capture recency, accessible evidence, and a clear reason to continue. Reject directory spam, circular citations, and unverifiable social claims.

### Capture

Save URL, title, publisher, capture time, excerpt or structured field, and screenshot or trace when layout matters.

### Extract

Resolve company identity, current role, operational signal, likely owner, and potential disconfirming evidence. Keep facts separate from inference.

### Synthesize

Produce a one-page decision brief. Do not produce a generic company biography.

## Account brief

- Account and owner
- Why this account
- Why now
- Evidence and freshness
- Likely operational consequence
- Proposed workflow and proof
- Buyer or champion hypothesis
- Disconfirming evidence and open questions
- Safe next action
- Approval state

## Campaign brief

- Revenue objective and time window
- Segment-use-case wedge
- Offer and proof
- Inclusion and exclusion logic
- Signal source and freshness rule
- Target count and quality sample
- Channel and sender
- Message architecture
- Approval owner
- Baseline and treatment
- Stop conditions
- CRM write-back contract

## Message contract

Use four sentences when practical:

1. A current, attributable signal or a real relationship context.
2. The operational implication as a hypothesis, not a fabricated fact.
3. One relevant workflow, proof, or useful idea.
4. A low-pressure next step with permission to decline.

Do not insert generic praise, false familiarity, or unsupported pain claims.

## Sales execution contract

- Pre-call: account brief, attendees, hypothesis, questions, relevant proof, desired decision.
- Discovery: rapport and agenda; diagnose current workflow, consequence, ownership, urgency, constraints, and decision process.
- Demo: show only the workflow that answers the diagnosed problem.
- Close: record decision, owner, next step, deadline, risks, and promised artifacts.
- Follow-up: recap on day 0; add ROI or evidence, proof, implementation path, executive summary, and proposal only when relevant.
