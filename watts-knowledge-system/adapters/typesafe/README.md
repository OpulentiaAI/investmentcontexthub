# TypeSafe System One adapter

This directory is a small, stdlib-only client for `POST https://api.typesafe.ai/v1/systemone`. It sends one state with a map of independent, typed questions (`noul`, `choice`, and `score`) and returns the provider's structured answers. Question IDs are local identifiers, so each instruction states its full question.

## Boundaries

Jev supplies a narrow judgment only. `constraints.py` owns all arithmetic, threshold comparisons, human-review bands, budgets, ordering, and consequences. A threshold compares an expected probability to a fixed boundary; it is never a rank, score magnitude, or count. The adapter cannot produce a send action: every decision record has `send: false`.

No key, malformed response, a provider failure, or an abstention is surfaced rather than filled in. Callers must use their deterministic fallback for these paths. The hard call cap is one transport attempt, so a rate limit is **not retried**. A shared `Budget` defaults to one batched call and 2,000 ms of accumulated latency per run; the actual transport timeout is clamped to remaining latency before dispatch. Callers may configure a stricter bound. `scripts/jev_evaluate.py` stays offline by default and requires both `--live` and the current `CONFIRM=send` for its separate one-call paid path.

The client reads `TYPESAFE_API_KEY` only at runtime. Tests inject a transport and never call the network. State may contain fetched text, but it is passed as data; adapter instructions are constructed separately and do not accept instructions from that text.
