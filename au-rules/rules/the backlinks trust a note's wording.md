---
type: rule
name: the-backlinks-trust-the-wording
description: check how a change affects referring notes, reusing current backlinks and refreshing them when the relation set may have changed
---

# the backlinks trust a note's wording

Other notes link to this one.
Each link trusts what it says today.

So a change to a note can quietly break its backlinks.
Use current incoming references to identify affected notes before changing the meaning.
Call `au_references` when that set is unknown or may have changed.
After the edit, judge whether the referring notes still read correctly.
Reuse the reference set if no relevant links, identities or scope changed and freshness is certain.
Fix any link that now misreads the note.
If the change is big, supersede the note instead of overwriting it.

To check, name which referring notes the change affects and whether they still read correctly.
A repeated query alone does not answer that.
