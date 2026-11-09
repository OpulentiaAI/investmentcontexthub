---
type: guide.pattern
goal: "Choose how to deliver knowledge or behavior to an agent."
rule: "Match delivery to the moment knowledge is needed and use executable mechanisms for deterministic work or enforcement."
example:
---

# Choose how the guidance or behavior applies

Start with the event or task that creates the need.
Choose a mechanism that can reach it with the required reliability.

| Need | Suitable starting point |
| --- | --- |
| Meaning or a caveat tied to a type or field | A docstring read with the contract |
| Structure and authoring advice for an instance body | A body template with guidance |
| A decision the builder seeks during work | A guide |
| A recognizable task needing a judgment-driven procedure | A skill |
| An explicitly invoked operation | A tool |
| Standing context for a selected session | An inject |
| A runtime phase or invariant | A hook |

**Read the execution contract**

[[mcp.skill::au-mcp-sdk:example]] supplies task guidance that the agent must select and use.
[[mcp.tool::au-mcp-sdk:example]] supplies a callable operation.
[[mcp.hook::au-mcp-sdk:example]] supplies these phases:

- observer
- mediator
- stamper
- session-start

A session-start hook can compute fresh orientation where a static inject would carry stale facts.

A read-precondition can ask the configured floor to require an observed read before a tool call.
Its behavior depends on:

- The configured floor
- Resolution
- The serving contract

It does not prove comprehension.
See [[make-a-read-mandatory]].

**Combine mechanisms for distinct jobs**

A skill can guide a complex task while a tool performs an exact transformation and a hook checks an invariant.
Explain the decisions around the operation in the skill.
Keep the algorithm in code.

Metadata takes attention.
Standing context takes space.
Runtime checks take implementation and execution.

Name what happens if the agent forgets the advice.
If correctness requires stopping an action or transforming data exactly, put that obligation at an executable boundary too.
