# JEV decision layer

The decisioning, evaluating, scoring and verification process for the packages in this workspace,
with Jev analysis wired in at four named points. Derived from `REVIEW.md`; every rule below traces
to a cited source or a live run recorded in `decisions/`.

## The one-sentence contract

**Jev owns judgment. Code owns arithmetic, ordering, thresholds and consequences.** Any design in
which the model produces the final ordering, count, or number is wrong by construction
(turbo-rerank: "Jev never generates text — all ordering, rank deltas and metrics are plain code").

## The four decision points

| # | Point | Question | Jev surface | Owner of the result |
|---|---|---|---|---|
| D0 | **Gate** | Is this admissible as evidence? | `screen` + `noul` gates | Code (thresholds) |
| D1 | **Score** | How good is it, on named dimensions? | composite `score` questions | Code (weights) |
| D2 | **Route** | Who acts, and how confidently? | `confidence` from D1 | Code (per-action thresholds) |
| D3 | **Verify** | Was the judgment right? | stored probabilities vs realized outcome | Code (Brier by question id) |

Every decision record is written to `schemas/jev-decision.schema.json` shape. No decision is
"made" until it is a record, because D3 needs the statement that was made *before* the outcome.

## D0 — Gate

**Untrusted text is data, not instructions.** `jev-1.13` "does not treat [state] as hostile by
default" (jaggedness #6), so the gate runs before any third-party text becomes evidence.

Order: fetch → `interaction.screen` → only on `admit` does the text become a citable source.

| screen result | action |
|---|---|
| `injection < 0.5` and `relevance ≥ 2.5` and `substance ≥ 2.0` | **admit** — usable as evidence |
| `0.5 ≤ injection < 0.8` | **quarantine** — never cited; may be used only as a pointer to re-check at the original source |
| `injection ≥ 0.8` | **reject** — discard; log the source |
| `relevance < 2.5` or `substance < 2.0` | treat as non-evidence; do not spend a judgment on it |

`noul` gates (per package, in `questions/`): a gate noul must clear its threshold on the *safe* side
before the item enters a ranked list. Gate answers are recorded with their probabilities even when
they pass, because D3 scores them like any other claim.

## D1 — Score

**Composite scoring, weights published in code** (`patterns/composite-scoring`). Each rubric
component becomes one atomic `score` question with descriptive levels — the levels are the rubric
text, so the model is not asked to invent severity, only to place the item on our spectrum.

Rules:

1. **One dimension per question.** Never "score this prospect's overall quality".
2. **Levels are the rubric.** 5 ordered, concrete levels, each phrased as an observable condition
   from the evidence (e.g. `"Credible report of a confidential S-1 submission"` → 4).
3. **State is filtered to the fields the question needs** (jaggedness #5). A prospect question gets
   the evidence lines for that dimension, not the whole candidate record.
4. **Literal instructions** (jaggedness #1): write the exact condition, including boundary cases,
   and split any interpreted composite into two literal questions combined in code.
5. **No counting, no arithmetic, no date math** (jaggedness #2, #3). Counts and date comparisons are
   code. Dates are extracted as `choice` over enumerated components with an explicit `"not stated"`
   option, then assembled and compared in code.
6. **Expectation for thresholds only** — `Σ p·level` decides pass/fail against a threshold; it is
   never interpolated into a magnitude (jaggedness: score levels are weak in numerical calibration).
7. **One shape per decision** (jaggedness #8): the same question id always means the same thing, so
   its probabilities accumulate across runs.

## D2 — Route

**Confidence is the second axis.** Floor and per-action thresholds follow
`patterns/confidence-routing` (their example: 0.6 floor → human; 0.85 for the consequential action).
Our thresholds are set by consequence, not by convenience:

| Action | Required confidence | Why |
|---|---|---|
| Admit evidence to a pipeline row | 0.6 | cheap to correct later; the row carries its probability |
| Include a name on a save-the-date / non-binding list | 0.6 | reversible |
| Route a prospect to Tier A and trigger a partner-level ask | **0.85** | an external human acts on it; a wrong intro costs a relationship |
| Place a trade / send an offer / anything irreversible | **0.9** plus primary-source confirmation | consequence is money or compliance |
| `noul` gate | per-gate, on the safe side (e.g. "would require non-public info" must be ≤ 0.1) | a gate that leaks is not a gate |

Below the floor, the item does not proceed to a human *as a decision* — it proceeds as **an
escalation with the distribution attached**. The human sees the probabilities, not a verdict.

**Abstention is an outcome, not a failure.** `rank` returning `abstained` (measured twice in
`decisions/2026-09-18-live-runs.json`) means: fall back to the deterministic rubric, keep the
probabilities as weak signal, and route to a human. Never re-read an abstention as an ordering.
Same for a `noul` inside 0.4–0.6: that band is a human-review band (`cookbooks/consistency_noul`:
"route uncertain probabilities to human review while keeping the underlying noul values visible").

**Right tool for the shape:** `rank` for a genuine single-winner choice among comparable candidates.
Typed question sets for everything heterogeneous. Two live abstentions at 2 and 6 candidates are the
evidence for that rule.

## D3 — Verify

Every answer stores its probability *before* the outcome. Then:

1. Append `(question_id, stated_probability, realized_outcome, group)` to `dashboard/calibration.csv`.
2. Compute **Brier by question id** over a trailing window; compare against the base rate.
3. A question id whose Brier is worse than base rate over ≥30 samples is **retired or rewritten**,
   not kept because it "feels" right.
4. Refit composite weights **only at the weekly review**, only against realized outcomes, and log
   the diff. Weights are a hypothesis, and the calibration log is their test.
5. Record disagreements: when Jev's composite and the deterministic rubric differ by more than 10
   points, that is a signal worth a human look — the disagreement is the finding.

## Failure and degradation

| Failure | Handling |
|---|---|
| 408 / 429 / 5xx / 529 | bounded retry with exponential backoff (the SDK and MCP server both do this); keep credentials server-side |
| Persistent provider failure | set `jev_unavailable: true` on the affected rows, fall back to the deterministic rubric, and say so in the brief — never fabricate a judgment, never silently drop the gate |
| No API key configured | the runtime's `interaction.rank` / `interaction.screen` remain available; the typed `evaluate` path (D1) is inert until a key exists — see `adapters/runtime-jev.md` |
| Model jaggedness discovered in production | add the case to the question set's `known_failures[]` with the wrong answer, and tighten the levels |

## Where this plugs in

- **Convergence desk** — D0 on every fetched source; D1 replaces hand-typed component scores with
  Jev-scored dimensions combined by the published weights; D2 gates Tier A routing; D3 calibrates
  against reply outcomes. See `../convergence/skills/jev-scoring/SKILL.md`.
- **Bellwether desk** — D0 on the resolution-source page before its text becomes a signal; D1 scores
  statement specificity and source authority; D2 gates the trade (with the phone confirmation still
  mandatory and upstream of any model); D3 calibrates against resolution outcomes. See
  `../bellwether/skills/jev-gate/SKILL.md`.

## Budget

Our measured volumes are small: a 50-candidate batch is one request (~170 ms p50 at 50 judgments)
and today's five live calls used 546–801 tokens each. Cap it anyway: ≤1 judgment request per state,
question sets versioned, and a per-day call ceiling recorded in each package's dashboard.
