---
type: rule
name: write-through-the-gate
description: route graph changes through the engine and resolve refusals before retrying
---

# write through the gate, never behind it

Every change to the graph goes through the engine's gate.
Use its write or structural mutation tool.
Use focused replacements for edits and full-content writes for rewrites.

The gate can reject an operation when a precondition fails.
Read the refusal and resolve its cause before retrying.

To check, ask whether the engine handled the change.
