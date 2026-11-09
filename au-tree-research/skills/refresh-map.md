---
type: mcp.skill::au-mcp-sdk
name: refresh-map
description: Recreate a premise's map of articles and open questions after research or tree changes.
---

Refresh the map after other writers finish changing the field.

## Refresh

Call `refresh_research_map` with the premise's absolute path.
Use `dry_run: true` for a requested preview.

The tool rebuilds Index as a tree of premise, article and open-question links, preserving the rest of the map.
Researched and dropped question entries stay hidden.
New maps use `map - <name>.md` beside `premise - <name>.md`.

## Check and return

If the write is uncertain, inspect the map before retrying.
If the tool is unavailable, report that it needs to be loaded.

Report the returned result:

- Map path
- Status
- Warnings
