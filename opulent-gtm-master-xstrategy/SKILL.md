---
name: opulent-gtm-master-xstrategy
description: Build or run Opulent GTM engineering, sales, account research, LinkedIn enrichment, signal-led outbound, and revenue learning loops. Use for GTM strategy and execution; not generic brand copy.
---

# Opulent GTM Master XStrategy

## Overview

Turn market evidence, relationship data, account signals, and sales activity into a compounding revenue learning system. The skill covers ICP selection, data enrichment, company research, campaign design, sales execution, artifact handoffs, approvals, measurement, and sequencing.

The governing thesis is: **GTM is an engineered learning loop, not a campaign factory.** Every run must improve account memory, signal quality, playbooks, or offer clarity.

Out of scope: bulk contact harvesting without a defined ICP, unsourced personalization, autonomous external sending, generic brand copy, and activity reporting that cannot be tied to revenue learning.

## What's Needed From User

- The commercial objective or decision window when it cannot be inferred.
- Approval before any external send, publish, CRM overwrite, or destructive data mutation.
- The sender identity and channel constraints when outreach is requested.

## Before You Start

1. Use this skill's evidence, sequencing, approval, and validation rules as the self-contained operating discipline. When running inside Opulent, also pair with `$opulentia-engineering-discipline` and `$process-engineering` if available.
2. Read `references/operating-sequence.md`, `references/account-campaign-contracts.md`, and `references/evidence-and-metrics.md`.
3. Load the source-specific references only when needed: `diego-workbook-evidence.md`, `field-theory-findings.md`, `reference-repo-patterns.md`, and `opulent-use-case-catalog.md`.
4. For long-running, scheduled, automated, delegated, or multi-agent work, `document_read` the scratchpad at every start or resume. Create it once only if absent; append decisions, artifacts, blockers, approvals, joins, validation results, and closeout.
5. Establish one Brand and Revenue Context artifact. One owner writes it; every downstream operator reads it before work begins.

## Procedure

1. **Name the revenue outcome.** Pin the offer, buyer, problem, time window, owner, decision, and success metric. Refuse vanity activity as the primary objective.
2. **Choose one wedge.** Use `references/opulent-use-case-catalog.md` to shortlist a `Primary wedge` or `Partner wedge`, then score candidate segment-use-case pairs on relationship access, pain intensity, proof availability, signal observability, reachable buyers, delivery confidence, and expansion potential. Preserve the site's observed labels separately from the catalog's editorial GTM labels.
3. **Register sources.** Record source, capture time, scope, allowed use, freshness, and reliability. Keep direct identifiers in controlled source files; use aggregated evidence in reusable artifacts.
4. **Normalize before enriching.** Deduplicate by LinkedIn URL, then work email, then normalized name plus company. Resolve company identity before role or industry classification. Never infer truth from a company-name string alone when evidence is available.
5. **Build the account ladder.** Assign accounts to `warm_wedge`, `fit_plus_signal`, `fit_no_signal`, `research_needed`, or `exclude`. Preserve the reason, evidence URLs, owner, next action, and expiry.
6. **Research in bounded stages.** Run discover -> candidate gate -> evidence capture -> structured extraction -> synthesis. Promote stable browser interactions to APIs only after trace-backed proof. Use the research contract in `references/account-campaign-contracts.md`.
7. **Create a decision artifact, not a dossier.** Every account brief must answer: why this account, why now, who owns the problem, what evidence supports the hypothesis, what workflow to propose, what could disconfirm fit, and what next action is safe.
8. **Route through one lead and one specialist.** Send self-contained briefs. Specialists may research and self-review but do not recursively delegate. The strategy owner controls positioning; channel owners adapt and operate the channel.
9. **Draft from signal and proof.** Use a four-part message: observed signal, likely operational consequence, one relevant workflow or proof, and one low-pressure ask. Do not claim personalization when only a token was swapped.
10. **Gate irreversible action.** Require human approval before send or publish. Validate recipient, sender, evidence freshness, consent or channel policy, message fit, and CRM write-back fields.
11. **Run the sales loop.** Prepare the call, execute a bounded discovery, show only the relevant workflow, capture commitments, and issue the follow-up sequence. Write corrections and outcomes back into account memory.
12. **Scale only after lift.** Compare against a baseline, isolate one variable per experiment, kill weak plays, promote proven plays to reusable playbooks, and close with the scorecard in `references/evidence-and-metrics.md`.

## Specifications

### Required artifacts

- Brand and Revenue Context
- source registry and evidence ledger
- normalized account table with provenance
- account brief and campaign brief
- approved outreach or channel draft
- call brief, commitment log, and follow-up plan
- experiment card and weekly revenue learning report
- selected use-case record with source URL, observed labels, GTM labels, buyer hypothesis, and proof plan

### Postconditions

- One wedge and one offer are explicit.
- Every targeted account has fit evidence, a current signal or a documented warm relationship, an owner, a next action, and an expiry.
- Direct identifiers never leak into reusable public skill references or reports.
- External actions are approved and their effects are recorded.
- Results distinguish pipeline outcomes from activity counts.
- Corrections change account memory or a reusable playbook.
- The selected use case is tied to one named buyer and workflow; catalog labels are not represented as customer proof or first-party site claims.

### Primary validation

```bash
python3 scripts/validate_skill.py
```

For a live GTM run, also perform `validation_check` or `trigger_verifier` against the account artifacts, evidence URLs, connector effects, and CRM state when those tools are available.

## Advice and Pointers

- Start with the four-layer account ladder described in `references/diego-workbook-evidence.md`; do not treat a raw LinkedIn export as a campaign list.
- Use the 90-day rollout and weekly cadence in `references/operating-sequence.md`.
- Use `references/reference-repo-patterns.md` for specialist ownership, approval gates, browser research, and browser-to-API promotion.
- Use `references/field-theory-findings.md` for source-backed GTM hypotheses; treat reported social-post metrics as hypotheses until independently verified.
- Use `references/opulent-use-case-catalog.md` to route the current Opulent use-case portfolio by buyer, value motion, lifecycle stage, and commercial role. Lead with one wedge; use expansion modules, proof accelerators, and enablement assets only in support of it.
- When available, pair `$research-assistant` for external research and `$outlook-email` only when mailbox context is explicitly in scope. The core operating sequence does not depend on either skill.

## Forbidden Actions

- Sending, publishing, or enrolling contacts without explicit approval.
- Bulk outreach from raw exports, stale data, or missing provenance.
- Copying direct identifiers, emails, LinkedIn URLs, or personalized messages into this skill's reusable references.
- Treating enrichment as correct because a model filled every cell.
- Generic messages that hide the absence of a real signal.
- Recursive agent swarms, overlapping ownership, or briefs that depend on hidden conversation history.
- Scaling a play before a baseline, quality review, and measurable lift.
- Reporting sends, impressions, or meetings as success without downstream quality and revenue context.
- Presenting all use cases as one undifferentiated offer or presenting editorial GTM labels as if Opulent published them on the source site.

## Performance Bar Checklist

- [ ] One wedge, one offer, one owner, and one decision window
- [ ] Selected use case retains its source URL and separates observed from editorial labels
- [ ] Provenance-preserving normalization and deduplication
- [ ] Current fit or signal evidence for every target
- [ ] Decision-ready artifacts with explicit disconfirmation paths
- [ ] Approval before external action
- [ ] Same-day commitment capture and write-back
- [ ] Baseline versus treatment with one variable changed
- [ ] Weekly keep, kill, or revise decision
- [ ] Account memory and playbooks improved by the run
