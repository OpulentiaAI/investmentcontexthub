# Deepline Play-run helper

This stdlib-only helper uses the [canonical HTTP contract](https://deepline.com/docs/api-reference) at `https://code.deepline.com`. It reads `DEEPLINE_API_KEY` only when making a request. `inspect_tool(tool_id)` reads metadata; `get_run(run_id)` and `poll_run(run_id)` read an existing Play run. `prepare_play(name, input)` builds the exact `{name,input}` body offline. There is no generic tool execution, send, CRM, or monitor API.

```python
from adapters.deepline import DeeplineClient, prepare_play

client = DeeplineClient()
plan = prepare_play("prebuilt/person-linkedin-to-email", {"linkedin_url": "https://www.linkedin.com/in/example-person/"})
```

Starting a Play can spend credits and trigger provider work. An operator must inspect the live route and schema and its side effects, verify owner scope and suppression, approve a measured budget and workspace cap, and obtain the current explicit `CONFIRM=send` before calling `client.run_play(plan, live=True)`. There is exactly one POST attempt; a transport failure or non-success response can leave the outcome unknown, so never retry blindly. The helper does not enforce a server-side spend cap. See [cost control](https://deepline.com/docs/cost-control). A prepared request is not an approval or a live call.

`poll_run` allows only 1–20 GETs and up to 120 seconds, with request timeouts clipped to the remaining deadline. It accepts `queued`, `running`, and `waiting` as nonterminal, and returns only `completed`, `failed`, or `cancelled`; callers must inspect the retained package and outputs to determine whether anything is usable. Unknown statuses and identity changes fail closed. The [generated SDK reference](https://deepline.com/docs/sdk-v2/api-reference) shows a different `{workflowId,status}` envelope, but this helper deliberately rejects it in favor of the canonical `schemaVersion: 1`, `kind: play_run`, `run: {id,status}` package. No live contract has been verified here; tests use an injected transport without credentials or network.

Keep request inputs and returned packages private. Starting an arbitrary saved Play can have side effects: this adapter enforces dispatch confirmation, not the Play's semantics, suppression eligibility, or budget. Only an independently inspected, approved read-only Play belongs in these research flows.
