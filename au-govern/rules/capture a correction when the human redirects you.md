---
type: rule::au-rules
name: capture-a-correction-when-redirected
description: preserve reusable feedback about agent behavior as a correction, linked to its original occurrence when it recurs
---

# capture a correction when the human redirects you

Capture feedback that changes how the agent should work as a `correction.open`.
Keep ordinary task choices and changes of scope in the current work.

Record the behavior that drew the correction under `What I did`.
Record the desired behavior under `What they wanted`, using the person's words where useful.

When the friction repeats a known correction, set `recurs` to its original occurrence.
Follow an existing recurrence chain to its root.
The relation preserves which friction returned.

A useful correction lets a future agent recognize the situation and choose the better behavior.
