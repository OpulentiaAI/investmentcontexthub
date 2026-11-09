---
type: rule
name: a-bare-name-is-scoped-to-its-own-repo
description: a bare name resolves in the repo of the file it sits in, so a link from another repo's skill or inject needs its ::repo qualifier to reach the node you mean
---

# a bare name is scoped to its own repo

A bare name belongs to the repo of the file it sits in.
Not the repo you launched from.
A type claim and a page link follow the same rule.

A skill or an inject can reach you from a repo you depend on.
Its bare links were scoped to its repo, not yours.
Basenames collide across repos.
So a bare name is ambiguous once you cross a boundary.

When you act on a link from another repo's content, cross the boundary on purpose.
Qualify the name with `::repo` to pin the node you mean.
Never fall back to a folder path.
That is the wrong tool for a repo boundary.

To check, ask whose repo a target lives in.
A dep's, qualify the name.
Yours, leave it bare.
