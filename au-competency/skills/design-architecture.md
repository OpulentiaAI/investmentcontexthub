---
type: mcp.skill::au-mcp-sdk
name: design-architecture
description: >-
  Explains how workspace mechanisms cooperate when their interactions need a separate design.
  Use within a proposal, approved implementation or a direct design brief.
  Keep small designs in the proposal.
---

# design-architecture

Return an explanation of how the capability will work.
Reuse an adequate design or short proposal.
Create a separate [[architecture-design]] only when its explanation serves a distinct need.

[[propose]] develops the change for the human's ruling.
[[improve]] owns implementation.
A direct brief needs no invented competency or research artifact.

## Explain the consequential choices

Establish the caller's intended behavior and constraints.
Use current evidence and engine results.
Deepen the owning contracts and implementations where a choice depends on them.

Use [[compose-a-capability::au-agent-guides]] for cooperating mechanisms.
Consult other guides for the choices they address.
For example, [[the-capability-pattern::au-agent-guides]] explains discovery and [[design-for-growth::au-agent-guides]] covers contract evolution.

Follow the architecture-design fields and body guidance.
Connect each obligation to an owner and an operation that can fulfill it.
Explain why the mechanisms fit, including their inputs, permitted effects and activation.
Account for recovery or migration where it affects the choice.

Check uncertainties through representative cases.
Use a failure case when it distinguishes a plausible alternative.
Separate expected behavior from observed results.
Name unresolved dependencies and the obligations they prevent.
A prerequisite leaves the larger requirement intact.

## Reuse existing designs

Compare candidates by their behavior and grounds.
For a competency, inspect each design's own competencies relation.
Backlinks narrow candidates but passing mentions do not establish scope.

When discovery is needed, query architecture-design::au-competency with origins: ["file"].
Include subtypes and page completely before claiming no match.
Use effective top-level values, including body contributions.
Exclude nested look-alikes.

Use [[qualify-colliding-fields::au-agent-guides]] when field origins collide.
Resolve missing identity or fragment details through the engine.
A block referent is not its containing question.
Keep unreadable relations visible as incomplete evidence.

Read matching designs and their grounds before judging fit.
Reuse current results until relevant state changes or freshness is uncertain.

## Return a checked result

Write through the engine when a design needs saving.
Read it for meaning and inspect write diagnostics.
Repair introduced errors and assess relevant warnings before relying on it.

Return the design or existing route with its supported scope.
Identify the relevant revision and any evidence still needed.
Keep unresolved work on the design or the caller's existing artifact.
Create no duplicate summary record.

Structural validity does not prove delivery.
Check within the caller's authorization and report what remains unobserved.
