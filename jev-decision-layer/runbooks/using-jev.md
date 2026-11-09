<!-- Runbook: Overview / What's Needed From User / Procedure (<12 steps + validation) / Specifications -->

# Runbook: run a JEV judgment

**Overview.** Get a probabilistic judgment into a decision without letting a model own the
arithmetic or the consequences. Four decision points (D0 gate, D1 score, D2 route, D3 verify) and
one rule: Jev judges, code decides.

**What's Needed From User**
- The decision being made, stated as one bounded question with a name (a `question_id`).
- The candidate state: the exact fields to be judged, already filtered.
- Any thresholds the decision must respect (gates, confidence floors) — or authority to set them.
- For D1 via TypeSafe: a bound `TYPESAFE_API_KEY` or `OPENROUTER_API_KEY`. Without one, plan for the
  degraded path and say so up front.

**Procedure**
1. Name the decision point (D0/D1/D2/D3) and pick the surface from `adapters/runtime-jev.md`.
2. Choose the question type: `noul` for yes/no with a probability, `score` for a position on
   ordered levels you can describe, `choice` for a closed set (always include a `not_determined`
   option so absence is reported rather than guessed).
3. Write the levels or criteria verbatim from the source rubric — never paraphrase in the model's
   favor, and never ask it to invent severity.
4. Filter the state to the fields this question needs; do not send the whole record.
5. Screen any third-party text first (`questions/screening.json`); a non-admitted source cannot be
   state.
6. Send all questions for one state in **one** request; record `requests: 1`.
7. Read the answer shape: `score`→`score`+`probabilities`+`confidence`; `choice`→`choice`+
   `probabilities`+`confidence`; `noul`→probability only.
8. Compose in code with published weights; keep the rubric and the weights in the same file.
9. Route by the threshold table in `DECISION-LAYER.md` D2 — abstention, the 0.4–0.6 band, and any
   failed gate all route to a human with the distribution attached.
10. Write the decision record (`schemas/jev-decision.schema.json`) **before** acting on it.
11. Append the stated probabilities to `dashboard/calibration.csv`.
12. When the outcome arrives, fill `outcome` on the record and score Brier by `question_id`.

**Validation**
- Re-run the negative control in `questions/screening.json`: it must still return `reject` with
  `injection ≥ 0.8`. If it does not, the gate changed and the thresholds must be re-tested.
- Confirm `requests == 1` per state and that no answer was acted on before its record existed.
- Confirm every gate answer has a `gate_result` and every routed decision has a `threshold_applied`.
- After ≥30 samples on a question id, compare its Brier against base rate; retire it if worse.

**Specifications**
- Surfaces: `interaction.rank` / `interaction.screen` (runtime, available now); TypeSafe
  `evaluate` → `POST /v1/systemone` or the OpenRouter Decisions endpoint (needs a key).
- Candidate ids for `rank`: `^[a-z][a-z0-9_]{0,47}$`.
- Model: `jev-latest` by default; `jev-1.13` behavior is documented in
  `https://docs.typesafe.ai/model-jaggedness/jev-1.13` — read it before writing questions.
- Retries: 408/429/5xx/529 with exponential backoff, bounded; credentials server-side only.
- Known limits: no counting, no date arithmetic, no numeric interpolation, literal reading,
  degraded accuracy on large states and adversarial text.
