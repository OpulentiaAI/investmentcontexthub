# Adapter: the two JEV surfaces

Two ways to get a Jev judgment. Use whichever is bound; the question sets are written to be
transport-independent, so a set can move between them without rewriting the questions.

## Surface A — runtime JEV tools (available now)

Execute-only tools, callable only inside a `code_mode` program:

```js
// D0 gate: screen untrusted text before it becomes evidence
const gate = await tools.interaction.screen({
  intent: "Screen a fetched page before using its claims as evidence",
  text: pageText,                                   // never treated as instructions
  source_url: "https://example.com/page",
  goal: "what this screening is protecting: the bounded task goal"
});
// → { success, status: "screened"|"error", injection, substance, relevance, verdict: "admit"|"quarantine"|"reject", usage }

// D2 choice among comparable candidates only
const rank = await tools.interaction.rank({
  intent: "Pick the single best candidate",
  goal: "the bounded decision, phrased as a single-winner choice",
  candidates: [{ id: "candidate_one", description: "one comparable description per candidate" }],
  top_k: 3
});
// → { success, status: "ranked"|"choice_only"|"abstained"|"error", choice, ranked: [{id, probability}], usage }
```

Rules that come from getting these wrong in practice:

- **Candidate ids**: `^[a-z][a-z0-9_]{0,47}$` — lowercase, digits, underscores. A hyphen is rejected
  before the call runs (recorded failure #2 in `decisions/2026-09-18-live-runs.json`).
- **`status: "abstained"` is an outcome.** Fall back to the deterministic rubric, keep the
  probabilities as weak signal, route to a human. Never read it as an ordering — measured twice.
- **`rank` is for a single winner among comparable candidates.** Heterogeneous items go to typed
  question sets instead.
- **Screen verdicts**: `admit`/`quarantine`/`reject` per `questions/screening.json` thresholds;
  scores are 0–4.
- **Record every call** as a `schemas/jev-decision.schema.json` record before acting on it, because
  D3 needs the probability that was stated *before* the outcome.

## Surface B — TypeSafe `evaluate` (needs a key)

The typed question path (D1 proper): `noul`, `choice`, `score` with criteria, many questions per
state in one request. Provided by the MCP server `OpulentiaAI/typesafe-mcp` (`jev mcp setup`) or the
HTTP API directly.

```json
POST /v1/systemone            Authorization: Bearer $TYPESAFE_API_KEY
{
  "state": { "...": "filtered fields only, per the question set's state_shape" },
  "questions": {
    "path_strength": {
      "type": "score",
      "instructions": "…from jev/questions/convergence.prospect.json, verbatim…",
      "criteria": ["…five descriptive levels…"]
    },
    "answerable_from_public_record": {
      "type": "noul",
      "instructions": "…",
      "criteria": { "true": "…", "false": "…" }
    }
  }
}
```

Response per question: `score` → `{score, legend, probabilities, confidence}`; `choice` →
`{choice, probabilities, confidence}`; `noul` → `{noul}` with no confidence. Composition (weights,
normalization, thresholds) happens in code — see `DECISION-LAYER.md` D1/D2.

Transport notes:

- Key handling: `TYPESAFE_API_KEY` (TypeSafe) or `OPENROUTER_API_KEY` (OpenRouter Decisions
  endpoint); TypeSafe wins when both are set. Server-side only, never in a browser or a prompt.
- Retries: 408/429/5xx/529 with exponential backoff, bounded attempts.
- Batch many questions into **one** request per state; splitting into parallel requests is a
  deliberate choice, not a default.
- If neither key is bound, the typed path is inert: record `jev_unavailable: true`, fall back to the
  deterministic rubric, and say so rather than substituting prose judgment.

## Translating between surfaces

| question set entry | Surface A today | Surface B when keyed |
|---|---|---|
| `screen` (D0) | `interaction.screen` | not applicable — screening is the runtime's gate |
| `noul` gate (D0) | approximate with `screen`'s relevance/substance, or an LLM-free deterministic check | `{type:"noul"}` |
| `score` dimension (D1) | not available — use the deterministic rubric and mark `degraded_no_jev` | `{type:"score", criteria:[…]}` |
| `choice` (D1) | `interaction.rank` only if the options are comparable and a single winner is wanted | `{type:"choice", criteria:{…}}` |

A judgment that could only come from Surface B is **not silently replaced** by Surface A. It is
marked degraded, and the deterministic rubric answers it until a key exists.
