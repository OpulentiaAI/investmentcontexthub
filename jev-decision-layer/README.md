---
type: au.engine.readme::au-engine
tldr: The JEV decision layer — bounded typed judgments (gate, score, route, verify) wired so Jev owns judgment and code owns arithmetic, thresholds, ordering, and consequences.
---

# Repo Overview

## What this is

The decision layer this workspace routes consequential choices through: D0 gate, D1 score,
D2 route, D3 verify, with question files, schemas, and calibration records under
`decisions/` and `dashboard/`.

## How to use this

Run a bounded `evaluate` (noul/choice/score) with a filtered state, record the answer as a
decision record before acting, and let code — not the model — apply thresholds and
consequences.

## How to extend this

Add question files for new decision points, keep every record in `decisions/`, and feed
realized outcomes into `dashboard/calibration.csv` for Brier scoring.


# jev/ — the JEV decision layer

Probabilistic judgment, wired into the decisioning, evaluating, scoring and verification steps of the
packages in this workspace. Built from a live review of
[`Git-Godssoldier/jev-experiments/turbo-rerank`](https://github.com/Git-Godssoldier/jev-experiments/tree/main/turbo-rerank)
and [`OpulentiaAI/typesafe-mcp`](https://github.com/OpulentiaAI/typesafe-mcp), plus the TypeSafe docs,
and verified against the runtime's own JEV tools before anything was written into a package.

**The rule:** Jev judges. Code owns weights, ordering, thresholds and consequences.

## Start here

| File | What it gives you |
|---|---|
| `REVIEW.md` | The two repos and the docs, with citations: what Jev is, measured accuracy and latency, and an adopt / do-not-adopt table |
| `DECISION-LAYER.md` | The four decision points (gate → score → route → verify), threshold tables per package, abstention policy, failure handling |
| `adapters/runtime-jev.md` | Exact call shapes for `interaction.rank` / `interaction.screen` today, and the TypeSafe `evaluate` contract for when a key exists |
| `runbooks/using-jev.md` | The repeatable procedure, with validation |
| `skills/jev-analysis/SKILL.md` | Agent-facing skill: checklist, jaggedness constraints, failure handling |

## Tree

```
jev/
├── REVIEW.md                        repo + docs review, cited
├── DECISION-LAYER.md                the four decision points and thresholds
├── questions/
│   ├── screening.json               D0 gate for untrusted text, with a negative control
│   ├── convergence.prospect.json    D1 composite scoring of a prospect (weights = the rubric)
│   ├── bellwether.signal.json       D0 gates + advisory signal quality before a trade
│   └── bellwether.callqa.json       probabilistic QA flags over a call transcript
├── schemas/jev-decision.schema.json one record per decision, probabilities before outcomes
├── adapters/runtime-jev.md          call shapes and translation between the two surfaces
├── runbooks/using-jev.md            procedure + validation
├── skills/jev-analysis/SKILL.md     how an agent should use all of this
├── decisions/                       decision records (live-runs record from 2026-09-18)
└── dashboard/calibration.csv        stated probability vs realized outcome, Brier by question id
```

## Live evidence (2026-09-18)

Seven calls recorded in `decisions/2026-09-18-live-runs.json`:

- the screening gate **admitted** two real pages (injection 0.07 and 0.06; relevance 3.88 and 4.00)
  and **rejected** a labeled injection control (injection 0.98, relevance 0.09);
- `interaction.rank` **abstained twice** — on two heterogeneous repos and on six open decisions —
  which is why abstention is a first-class routing outcome with a deterministic fallback;
- one `rank` call was rejected for hyphenated candidate ids (`^[a-z][a-z0-9_]{0,47}$`);
- one call committed but its output was lost to a program error and is reported as lost, not re-run
  as if clean.

## Wired into

- **convergence/** — `skills/jev-scoring/SKILL.md`; the composite rubric in
  `pipeline/scoring-rubric.md` now names Jev as the estimator of its inputs while the rubric stays
  the canonical formula.
- **bellwether/** — `skills/jev-gate/SKILL.md`; the seventh market gate became an eighth (JEV
  admissibility) and the trade desk and call-QA gain the D0/D1/D2 steps. Primary-source confirmation
  and the compliance layer remain upstream and authoritative — the model never decides either.

## What this layer refuses to do

Replace the phone call; replace a citation; replace the compliance checks; produce a count, a date
comparison, or a final ordering; act on any text that failed the gate.
