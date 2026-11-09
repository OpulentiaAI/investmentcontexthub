---
type: au.engine.readme::au-engine
tldr: Check graph meaning through audits and findings, and capture reusable feedback about agent behavior.
---

# Repo Overview

> Work in progress and not thoroughly tested.
> Expect breaking changes.

## What this is

`au-govern` helps agents check the meaning of a graph.
The engine checks its structure.

## How to use this

Depend on `au-govern` and select its `check` and `fix` skills.

Add [[audit]] recipes for the checks your graph needs.
Use [[check]] to run them and record findings.
Use [[fix]] to repair findings and verify the result.

Select the [[capture-correction]] rule profile as a launch inject.
It captures reusable feedback about agent behavior as corrections.

## How to extend this

Add `au-competency` to review corrections and develop capability changes.
