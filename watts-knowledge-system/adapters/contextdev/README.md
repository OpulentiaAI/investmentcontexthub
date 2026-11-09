# Context.dev Answers

Stdlib-only helper for [`POST /v1/web/answers`](https://docs.context.dev/api-reference/web-extraction/answers.md). `build_request` validates and returns an offline payload without reading a key or making a request. `ContextAnswers.answer` makes exactly one billable attempt only when both `live=True` and the **current process** has `CONFIRM=send`; it reads `CONTEXT_DEV_API_KEY` at call time. No redirect or retry is followed, including for uncertain timeout and rate-limit outcomes.

This example is offline and does not use a key:

```python
from adapters.contextdev import build_request

payload = build_request(
    "Find the pricing page and public plan names for context.dev.",
    json_format={"pricing_url": "", "plans": [{"name": ""}]},
    mode="fast",
    timeout_opts={"milliseconds": 30000, "behavior": "return-partial"},
)

```

Only after the operator authorizes the billable call in this session, set `CONTEXT_DEV_API_KEY` and `CONFIRM=send` in the process environment. The second step sends one request:

```python
from adapters.contextdev import ContextAnswers

answer = ContextAnswers().answer(payload["task"], json_format=payload["json_format"],
                                 mode=payload["mode"], timeout_opts=payload["timeoutOpts"],
                                 live=True)
```

The helper defaults to `fast` (10 credits, 30-second research budget); `ultra` costs 100 credits and has a 50-second budget. The provider defaults to ultra if mode is omitted, so this helper always sends mode. `json_format` is an **example object**, not JSON Schema; omitting it lets the provider use `{"result": ""}`. The HTTP timeout exceeds the effective research deadline by 15 seconds. `timeout_opts` accepts 1,000–300,000 milliseconds for either `fail` or `return-partial`. A deadline cannot extend a mode's research budget. A usable partial is charged and retains `partial=True`; an absent partial marker remains `None`.

`Answer` retains `json_content` unchanged, source URLs as a whole-answer list, and separate optional `credits_consumed`, `credits_remaining`, and `credits_used_header` values. Missing cost stays `None`, not zero. Unknown fields may be `null`, which is different from `false` and `0`. Sources can be snippets and do **not** cite individual fields, prove freshness, or authorize contact or sending; verify claims and consent outside this helper. It never stores credentials or sends anything beyond the explicitly authorized research request. Tests inject a transport and do not use the network.
