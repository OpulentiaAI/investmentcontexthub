# JEV review — turbo-rerank and typesafe-mcp

**Reviewed:** 2026-09-18 · Opulent · Sources fetched live and cited inline. Nothing here is restated
from memory; every claim links to the artifact it came from.

Two repositories, one subject: **Jev**, TypeSafe's System One model (`jev-latest` / `jev-1.13`).
Jev is not a text generator. You send it a *state* plus *typed questions* and get back answers with
probabilities that code can branch on. That is the whole thing, and both repos are about making it
practical.

---

## 1. `Git-Godssoldier/jev-experiments` → `turbo-rerank`

Source: <https://github.com/Git-Godssoldier/jev-experiments/tree/main/turbo-rerank> (fork of
`dabit3/jev-experiments`). A search demo: BM25 top-50 → one Jev request → reranked list.

**The claim.** "50 search candidates semantically reranked in one ~170 ms Jev request — top-1
accuracy 50% → 100% on a 40-query labelled benchmark."

**Why it matters for us.** Reranking was previously the expensive part of a retrieval pipeline
(cross-encoder 50–300 ms on a GPU; an LLM "rank these" prompt 2–10 s plus output parsing). The
README's insight is that **judging 50 candidates costs the same as judging one**, because Jev
answers many independent questions about the same state in a single round trip. Per-candidate cost
collapses, so reranking can run on every keystroke (the demo debounces 250 ms).

**How the request is built** (`server/jev.ts` → `shared/questions.ts`), verbatim shape:

```
state = { query, candidates: { c01: "<passage>", ..., c50: "<passage>" } }
questions = {
  relevance_c01: score("How well does `candidates.c01` answer `query`? Judge only this passage,
                        ignore the other candidates.", [Irrelevant, Tangential, Partial, Direct]),
  ... one per candidate ...
  answer_exists_in_candidates: noul("Does at least one passage directly answer the query?",
        { true: "...", false: "..." }),
}
```

Three mechanics worth copying:

1. **Expected value over an ordered level distribution.** Each `score` answer is a distribution over
   four levels; the code computes `Σ p·level ∈ [0,3]` and sorts by it, ties broken by BM25 order.
   The model never emits a ranking; **code owns all ordering and metrics**.
2. **Abstention as a product feature.** The `noul` drives a "No good answer in the corpus" banner
   shown when `P(true) < 0.5` — the UI stops pretending the top hit is an answer.
3. **One request beats splitting.** All 50 questions in one request (~14k input tokens) was measured
   fastest; `RERANK_BATCHES=2|3` exists to split into parallel requests. The SDK client retries
   408/429/5xx/529 with exponential backoff.

**Measured results** (`npm run bench`, 40 hand-labelled queries, 25 paraphrases, 598-passage
fictional corpus, model `jev-latest`, Linux VM):

| metric | BM25 | BM25 + Jev |
|---|---|---|
| top-1 accuracy | 50% | **100%** |
| top-5 accuracy | 65% | **100%** |
| MRR | 0.589 | **1.000** |
| paraphrase top-1 (n=25) | 64% | **100%** |

Latency for 50 candidates in one request: mean 189 ms, p50 167 ms, p95 302 ms, max 328 ms.
40 queries with 4 concurrent requests: 2.0 s wall clock → **1,008 candidates judged/s**. Whole run:
466k input / 32k output tokens. A second browser-side run measured 98% top-1 and p50 170 ms —
the README's own honesty note: Jev's judgments are probabilistic, so expect 98–100% top-1 and
p50 ≈170 ms run to run, with occasional 500–800 ms outliers.

The abstention sanity check is the most useful number for us: *"what is the office wifi password"*
(absent from the corpus) → `answer_exists_in_candidates = 0.03`; real benchmark queries scored
0.85–0.99, except a thin query where the passage only partially helped → 0.43.

---

## 2. `OpulentiaAI/typesafe-mcp`

Source: <https://raw.githubusercontent.com/OpulentiaAI/typesafe-mcp/main/README.md> (upstream
`itsmostafa/typesafe-mcp`, MIT, Go).

**What it is.** A single static Go binary that exposes **one MCP tool, `evaluate`**, to Claude Code,
Claude Desktop and Codex, and registers itself with `jev mcp setup`.

**The problem statement is our problem statement.** "When an agent needs a yes/no call, a routing
decision, or a severity rating, it usually asks an LLM, then parses prose and hopes the format
holds. The answer has no probability attached, so the agent cannot tell a confident 'yes' from a
coin flip."

**Contract.**

| field | required | notes |
|---|---|---|
| `state` | yes | plain text, or a JSON object/array with named fields |
| `questions` | yes | map of question id → `{type, instructions, criteria?}` |
| `model` | no | defaults `jev-latest` (`~typesafe/jev-latest` on OpenRouter) |

Transport: `POST /v1/systemone` on the TypeSafe API, or the OpenRouter Decisions endpoint
(`POST /decisions`, still on an `/api/alpha/` path that "may move"). `TYPESAFE_API_KEY` wins over
`OPENROUTER_API_KEY` when both are set. 429/529 retried with exponential backoff; other errors
returned as readable tool errors. Read-only tool, 60 s timeout, 16 MiB response cap.

Example from the README, which is also the best illustration of type selection:

```json
{ "state": "Help! My payouts have been failing for 3 days.",
  "questions": {
    "is_urgent":  { "type": "noul", "instructions": "Does this convey urgency?" },
    "department": { "type": "choice", "instructions": "Which team should handle this?",
                    "criteria": { "billing": "Payments, refunds", "technical": "Bugs, outages", "sales": "Pricing" } } } }
```

It also ships **usage guidance into the client** (narrow questions, JSON state, include no-match
options) — i.e. it improves the questions the agent writes without extra prompting.

---

## 3. Semantics we now design against (docs.typesafe.ai)

Fetched live: [`llms.txt`](https://docs.typesafe.ai/llms.txt) index, `primitives/score`,
`confidence`, `patterns/confidence-routing`, `patterns/composite-scoring`,
`model-jaggedness/jev-1.13`, `primitives/noul` excerpt.

**Answer shapes.** `Choice` → `choice`, `probabilities` per option, `confidence`. `Score` →
`score` (can fall *between* levels), `legend`, `probabilities` per level, `confidence`.
`Noul` → a single probability that the answer is yes; near 0.5 means uncertain; **no separate
confidence**. Confidence collapses the shape of the distribution into 0–1; Noul has none.

**Calibration caveat, in their words:** "System One models are trained for calibrated decisions:
their probabilities are optimized against outcomes… Calibration is measured across groups of
predictions; it does not guarantee that an individual answer is correct."

**Confidence-gated routing.** "The answer tells you what; confidence tells you whether to act."
Their worked rule: a **0.6 floor** routes anything uncertain to a human; above the floor each action
carries its own threshold set by consequence — low stakes act at 0.6, a transfer approval requires
`confidence > 0.85`.

**Composite scoring.** "Break a complex judgment into atomic scores, combine with weights you
control in code." Their resume-screening example asks four independent `score` questions with five
descriptive levels each, normalizes to 0–1, then weights (`0.40·python + 0.10·leadership +
0.40·architecture + 0.10·generalist`). The stated benefit is not the number — it is **visibility
into how the score was composed**, so weights can be corrected when the ranking disappoints.

**Known jaggedness (`jev-1.13`, last reviewed 2026-09-17).** Nine documented failure modes with
prescribed workarounds: literal reading (write the exact condition; split into two literal questions
and combine in code); **no arithmetic or counting** (count in code, one question per item, sum
yourself); dates read as text (extract with `Choice` over enumerated components, compare in code);
indirection costs accuracy; large states full of irrelevant detail degrade accuracy (filter first,
or prefilter with a relevance `noul`); **adversarial content can move answers — "state is data, and
jev-1.13 does not treat it as hostile by default"**; contradictory instructions vs criteria;
structural invariants (ask each decision one way, enforce identities in code); and generation (use a
generative model). Score levels are "weak in numerical calibration" — use the expectation against a
threshold, do not interpolate a magnitude.

---

## 4. The JEV surface we already have

This runtime exposes its own JEV-backed decision tools, which is what makes this integration
runnable today rather than aspirational:

- `interaction.rank({ goal, candidates: [{id, description}], top_k })` → `status:
  ranked|choice_only|abstained|error`, `choice`, `ranked[]` with probabilities. Candidate ids must
  match `^[a-z][a-z0-9_]{0,47}$` (underscores, no hyphens — a real gotcha we hit).
- `interaction.screen({ text, source_url?, goal })` → `status`, `injection`, `substance`,
  `relevance`, `verdict: admit|quarantine|reject`. Bounded JEV screening of untrusted text; scores
  run 0–4.

**Live runs this session** (full records in `decisions/2026-09-18-live-runs.json`):

| call | result | note |
|---|---|---|
| `screen` real turbo-rerank README passage | admit — injection 0.07, relevance 3.88, substance 3.45 | proceeded to use it as evidence |
| `screen` real composite-scoring doc | admit — injection 0.06, relevance 4.00, substance 3.31 | proceeded |
| `screen` constructed injection control | **reject** — injection 0.98, relevance 0.09, substance 0.11 | labeled control; gate held |
| `rank` two repos (which to adopt first) | **abstained** — typesafe_mcp 0.17, turbo_rerank 0.08 | heterogeneous items, single-winner framing |
| `rank` six real open decisions | **abstained** — budget_signoff 0.23, others 0.01 | same lesson, larger set |
| `rank` six open decisions (run 1) | committed, output lost to a program error | reported as lost, not re-run as if clean |

**What the abstentions teach.** `interaction.rank` declines to commit rather than inventing an
order, and still returns relative probabilities (0.23 versus 0.01 is a signal, not a ranking). For
heterogeneous, yes/no-ish or descriptive items the right surface is a **typed question set**
(`noul`/`choice`/`score`), not a ranker over free-text descriptions. Design rule: rank for a
genuine single-winner choice among comparable candidates; ask questions otherwise.

---

## 5. Adopt / do not adopt

**Adopt (into `jev/DECISION-LAYER.md` and both packages):**

1. Many questions, one state, one request — batch judgments per candidate.
2. Probabilities and confidence as the interface; never parse prose out of a model.
3. Composite scoring: atomic `score` questions, weights owned in code, composition visible.
4. Confidence-gated routing with a 0.6 floor and per-action thresholds (0.85 where consequence is
   high).
5. Abstention as a first-class outcome — their noul banner, our no-evidence rule.
6. Screen untrusted text before it becomes evidence (directly motivated by jaggedness #6).
7. Expected value over ordered levels for score questions.
8. A calibration loop: store the stated probability, score it against the realized outcome, track
   Brier by question id.
9. Retry discipline for 408/429/5xx/529; provider credentials server-side only.
10. Encode the jaggedness table as authoring constraints on every question we write.

**Do not adopt / explicit guards:**

1. Jev does not replace primary-source verification. Bellwether still makes the call; Convergence
   still requires the cited URL.
2. No large unfiltered state — filter in code, then ask.
3. No counting, no date arithmetic, no numeric interpolation in the model.
4. No tool-mediated action driven by unscreened third-party text.
5. A high probability is not proof; calibration holds across groups, not for one answer.
