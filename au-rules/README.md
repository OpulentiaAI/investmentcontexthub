---
type: au.engine.readme::au-engine
tldr: Centralized agent rules, selected through profiles and loaded at session start.
---

# Repo Overview

> Work in progress and not thoroughly tested.
> Expect breaking changes.

## What this is

`au-rules` centralizes agent rules in reusable profiles.
Each profile selects which rules to load.

A rule profile mixes in `mcp.inject::au-mcp-sdk`.
When you select it for an agent launch, its rules load at session start.
They provide standing instructions like `AGENTS.md`.

## How to use this

Depend on `au-rules`.
Select `core-profile::au-rules` in your agent launch to use the default rules.

## How to extend this

Write `rule::au-rules` notes in your repo.
Keep each rule to one habit.

Create `rule-profile::au-rules` profiles that list the rules to load.
Reuse existing rules or combine them with your own.
Create different profiles for different repos or kinds of work.

Use `core-profile` as an example of bundling rules through `mcp.inject`.
Select your profile in your agent launch.
