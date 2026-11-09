---
type: rule
name: ask-the-graph-before-you-guess
description: ask the graph with a typed read instead of guessing, since it answers exactly where a filename or your memory can mislead
---

# ask the graph before you guess

The engine answers questions about the vault.
Use its current answers instead of guessing from a filename.
Reuse a result already read when the relevant graph state has not changed.
Refresh it when affected files, contracts or relations change, or freshness is uncertain.
Each call should answer a missing question needed for the next decision.

Ask it for what you need:
- what a note links to and from, with `au_references`
- every instance of a type across every mounted repo, with `au_instances_of`
- what is mounted and what you may edit, with `au_members`
- and the rest of the reads for anything else

Its answer is exact where a guess is not.
A count of zero is a real zero.
So the engine can prove a thing absent where a `grep` only fails to find it.

To check, ask how you learned the last fact you acted on.
If you guessed it, ask the graph instead.
