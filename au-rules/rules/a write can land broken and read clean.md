---
type: rule
name: a-write-can-land-broken
description: check diagnostics after an accepted write because success does not establish a valid graph
---

# a write can land broken and read clean

An accepted write can leave a broken graph.
A success message does not establish clean diagnostics.

Read any diagnostics returned with the write.
If they are absent, call `au_diagnostics` for the changed file or affected scope.
Inspect the summary.
Request relevant warning or drift entries when the summary reports them.
A complete zero summary needs no further severity query.

Fix errors caused by the change before building on it.
Check warnings for effects on the consumer.
Separate pre-existing findings from regressions.

Clean diagnostics do not establish that the prose is true or the consumer works.
Check the behavior the change affects.

To check, name the write's outcome and the checks you ran afterward.
