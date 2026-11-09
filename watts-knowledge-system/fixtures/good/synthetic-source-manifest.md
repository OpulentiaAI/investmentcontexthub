---
type: wks.source-manifest
tldr: Synthetic example of a source manifest row set. Illustrative only.
status: active
owner: Derrick Watts
updated: 2026-09-18
surface: watts
provenance: "Synthetic example. No real account data. The authoritative populated manifest stays private."
sources:
  - sourceId: example-a
    kind: mcp
    reach: readable
    authorization: live
    state: extracted
    lastObservedAt: 2026-09-18
    staleAfterDays: 30
    entitiesAvailable: 12
    entitiesCaptured: 12
    completeness: FULL
    datasetOwner: example-owner
    suppressionSurface: no
    covers: "the prospect and campaign corpus for this synthetic example"
    doesNotCover:
      - "the mailbox"
      - "the writing voice"
      - "conversation history"
    privacy: private
  - sourceId: example-b
    kind: oauth
    reach: refreshable
    authorization: past-use
    state: pending
    lastObservedAt: 2026-09-18
    staleAfterDays: 14
    entitiesAvailable: 28
    entitiesCaptured: 6
    completeness: PARTIAL
    datasetOwner: example-owner
    suppressionSurface: yes
    covers: "a partial slice of one source, captured on one date"
    doesNotCover:
      - "22 of 28 entities"
      - "messages and sequences"
      - "the denial-reason suppression rows"
    blockerNote: "access token expired; a refresh token exists and one authorized run restores access"
    privacy: private
  - sourceId: example-c
    kind: api
    reach: none
    authorization: none
    state: unavailable
    lastObservedAt: 2026-09-18
    entitiesAvailable: 0
    entitiesCaptured: 0
    completeness: UNKNOWN
    datasetOwner: example-owner
    suppressionSurface: no
    covers: "nothing yet"
    doesNotCover:
      - "everything this source holds"
    blockerNote: "no tokens stored; extraction is impossible until someone authorizes it"
    privacy: private
---

# Synthetic source manifest example

This file shows the **shape** of a source manifest. Every value is synthetic.

The authoritative, populated manifest is private and never enters this
repository. This example exists so the schema is readable and testable without
shipping real account data.

Three rows, deliberately covering the three states that matter:

- **`example-a`** — fully read, and honest about what it still does not cover.
  One source being complete says nothing about the others.
- **`example-b`** — partial: 28 entities available, 6 captured, token expired.
  Note `authorization: past-use`, not `live`: having used a source before is
  history, not current permission. It carries a `suppressionSurface: yes`, so
  its unread suppression rows are named as a gap rather than assumed empty.
- **`example-c`** — registered but unreachable. `unavailable` with a verbatim
  blocker, not an empty result.

# How completeness is read

`completeness` is derived from page contiguity, never from a file being present.
A `ready` artifact is not evidence of completeness, and one extracted source is
never evidence that the account is covered. See
`docs/completeness-and-source-coverage.md`.
